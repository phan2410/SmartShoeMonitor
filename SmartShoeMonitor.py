from __future__ import print_function
import os
from multiprocessing import Process, Pipe
from subprocess import Popen
from threading import Thread, Lock
from pyqtgraph import PlotWidget
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from tkinter import Tk, messagebox
import numpy as np
import socket
import sys
import time
import matlab
import matlab.engine

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1024, 700)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon/starLogo24x24.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.WeightDistributionMap = RightFootWeightDistributionMap(self.centralWidget)
        self.WeightDistributionMap.setGeometry(QtCore.QRect(10, 10, 200, 470))
        self.WeightDistributionMap.setObjectName("WeightDistributionMap")
        self.WeightDistributionGraph = PlotWidget(self.centralWidget)
        self.WeightDistributionGraph.setGeometry(QtCore.QRect(220, 10, 794, 310))
        self.WeightDistributionGraph.setObjectName("WeightDistributionGraph")
        self.currentGaitPhase = RightLegGaitPhase(self.centralWidget)
        self.currentGaitPhase.setGeometry(QtCore.QRect(10, 490, 200, 150))
        self.currentGaitPhase.setObjectName("currentGaitPhase")
        self.rawDistributionGraph = PlotWidget(self.centralWidget)
        self.rawDistributionGraph.setGeometry(QtCore.QRect(220, 330, 794, 310))
        self.rawDistributionGraph.setObjectName("rawDistributionGraph")
        self.frame = QtWidgets.QFrame(self.centralWidget)
        self.frame.setGeometry(QtCore.QRect(9, 660, 1004, 32))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.matlabSwitch = QtWidgets.QPushButton(self.frame)
        self.matlabSwitch.setGeometry(QtCore.QRect(900, 0, 100, 32))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.matlabSwitch.setFont(font)
        self.icon1 = QtGui.QIcon()
        self.icon1.addPixmap(QtGui.QPixmap("icon/playButton32x32.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icon2 = QtGui.QIcon()
        self.icon2.addPixmap(QtGui.QPixmap("icon/stopButton32x32.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.matlabSwitch.setIcon(self.icon1)
        self.matlabSwitch.setIconSize(QtCore.QSize(70, 40))
        self.matlabSwitch.setCheckable(False)
        self.matlabSwitch.setChecked(False)
        self.matlabSwitch.setObjectName("matlabSwitch")
        self.processingSpeedBar = QtWidgets.QProgressBar(self.frame)
        self.processingSpeedBar.setGeometry(QtCore.QRect(133, 3, 747, 24))
        self.processingSpeedBar.setProperty("value", 0)
        self.processingSpeedBar.setTextVisible(False)
        self.processingSpeedBar.setObjectName("processingSpeedBar")
        self.SampleLimitation = QtWidgets.QSpinBox(self.frame)
        self.SampleLimitation.setGeometry(QtCore.QRect(60, 3, 42, 24))
        self.SampleLimitation.setMinimum(1)
        self.SampleLimitation.setProperty("value", 5)
        self.SampleLimitation.setObjectName("SampleLimitation")
        self.labelSecond = QtWidgets.QLabel(self.frame)
        self.labelSecond.setGeometry(QtCore.QRect(105, 3, 16, 24))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelSecond.setFont(font)
        self.labelSecond.setObjectName("labelSecond")
        self.labelSecond_2 = QtWidgets.QLabel(self.frame)
        self.labelSecond_2.setGeometry(QtCore.QRect(3, 3, 53, 24))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelSecond_2.setFont(font)
        self.labelSecond_2.setObjectName("labelSecond_2")
        self.line = QtWidgets.QFrame(self.centralWidget)
        self.line.setGeometry(QtCore.QRect(0, 644, 1021, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_4 = QtWidgets.QFrame(self.centralWidget)
        self.line_4.setGeometry(QtCore.QRect(130, 650, 3, 61))
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.line_5 = QtWidgets.QFrame(self.centralWidget)
        self.line_5.setGeometry(QtCore.QRect(900, 650, 3, 61))
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Smart Shoe Monitor"))
        self.matlabSwitch.setText(_translate("MainWindow", "MATLAB"))
        self.labelSecond.setText(_translate("MainWindow", "s"))
        self.labelSecond_2.setText(_translate("MainWindow", "Interval"))

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    print(*args, **kwargs)

class RightFootWeightDistributionMap(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self,parent)
        self.backgroundPixMap = QtGui.QPixmap('icon/WeightDistributionMapBackground.png','PNG').scaled(200, 470)
        self.painter = QtGui.QPainter(self.backgroundPixMap)
        self.brush0 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush1 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush2 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush3 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush4 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush5 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush6 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush7 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        global maxSensibleWeight
        self.ColorTemperatureToWeightRatio = float(1023/maxSensibleWeight)        
    def paintEvent(self, event):
        self.painter.setBrush(self.brush0)
        self.painter.drawEllipse(24,47,30,30)
        self.painter.setBrush(self.brush1)
        self.painter.drawEllipse(33,120,30,30)
        self.painter.setBrush(self.brush2)
        self.painter.drawEllipse(78,141,30,30)
        self.painter.setBrush(self.brush3)
        self.painter.drawEllipse(34,158,30,30)
        self.painter.setBrush(self.brush4)
        self.painter.drawEllipse(141,169,30,30)
        self.painter.setBrush(self.brush5)
        self.painter.drawEllipse(128,264,30,30)
        self.painter.setBrush(self.brush6)
        self.painter.drawEllipse(84,359,30,30)
        self.painter.setBrush(self.brush7)
        self.painter.drawEllipse(85,400,30,30)
        QtGui.QPainter(self).drawPixmap(0,0,self.backgroundPixMap)        
    def GenBrushFromWeightData(self,WeightData):
        colorTemp = int(WeightData*self.ColorTemperatureToWeightRatio)
        Red = 0
        Green = 0
        Blue = 0
        if colorTemp < 256:
            Blue = 255
            Green = colorTemp
            Red = 0
        elif colorTemp < 512:
            Blue = 511 - colorTemp
            Green = 255
            Red = 0
        elif colorTemp < 768:
            Blue = 0
            Green = 255
            Red = colorTemp - 512
        else:
            Blue = 0
            Green = 1023 - colorTemp
            Red = 255
        return QtGui.QBrush(QtGui.QColor(Red,Green,Blue,255))
    def updateColor(self,WeightDataIntArr):
        self.brush0 = self.GenBrushFromWeightData(WeightDataIntArr[0])
        self.brush1 = self.GenBrushFromWeightData(WeightDataIntArr[1])
        self.brush2 = self.GenBrushFromWeightData(WeightDataIntArr[2])
        self.brush3 = self.GenBrushFromWeightData(WeightDataIntArr[3])
        self.brush4 = self.GenBrushFromWeightData(WeightDataIntArr[4])
        self.brush5 = self.GenBrushFromWeightData(WeightDataIntArr[5])
        self.brush6 = self.GenBrushFromWeightData(WeightDataIntArr[6])
        self.brush7 = self.GenBrushFromWeightData(WeightDataIntArr[7])
        self.update()

class RightLegGaitPhase(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self,parent)
        self.UnknownPixMap = QtGui.QPixmap('icon/Unknown.png','PNG').scaled(200, 150)
        self.InitialContactPixMap = QtGui.QPixmap('icon/InitialContact.png','PNG').scaled(200, 150)
        self.LoadingResponsePixMap = QtGui.QPixmap('icon/LoadingResponse.png','PNG').scaled(200, 150)
        self.MidStancePixMap = QtGui.QPixmap('icon/MidStance.png','PNG').scaled(200, 150)
        self.TerminalStancePixMap = QtGui.QPixmap('icon/TerminalStance.png','PNG').scaled(200, 150)
        self.PreSwingPixMap = QtGui.QPixmap('icon/PreSwing.png','PNG').scaled(200, 150)
        self.currentPixMap = self.UnknownPixMap
    def paintEvent(self, event):
        QtGui.QPainter(self).drawPixmap(0,0,self.currentPixMap)
    def updateGait(self,isOfStancePhases,WeightDataIntArr):
        if isOfStancePhases:
            sumHindFoot = sum(WeightDataIntArr[6:8])
            midFoot = WeightDataIntArr[5]
            sumForeFoot = sum(WeightDataIntArr[1:5])
            greatToe = WeightDataIntArr[0]
            isHindFoot = sumHindFoot
            if sumHindFoot > 3:                
                if midFoot > 3:
                    if sumForeFoot >= 1:
                        if sumHindFoot > sumForeFoot:
                            self.currentPixMap = self.LoadingResponsePixMap
                        else:
                            self.currentPixMap = self.MidStancePixMap
                    else:
                        self.currentPixMap = self.InitialContactPixMap
                else:
                    self.currentPixMap = self.InitialContactPixMap
            else:
                if midFoot > 3:
                    if sumForeFoot >= 1:
                        self.currentPixMap = self.TerminalStancePixMap
                    else:
                        self.currentPixMap = self.UnknownPixMap
                else:
                    if greatToe > (sumForeFoot/4):
                        self.currentPixMap = self.PreSwingPixMap
                    else:                        
                        self.currentPixMap = self.TerminalStancePixMap
        else:
            self.currentPixMap = self.UnknownPixMap
        self.update()
     
class SmartShoeMonitor(Ui_MainWindow):
    lock = Lock()
    def __init__(self, ctrlPipe, datPipe):
        super().__init__()
        self.app = QtWidgets.QApplication(sys.argv)        
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)

        self.WeightDistributionGraph.setMenuEnabled(False)
        self.WeightDistributionGraph.showGrid(x=True,y=True)
        self.WeightDistributionGraph.setLabel('left','Weight','N')
        self.WeightDistributionGraph.setLabel('bottom','Time','s')
        self.weightA0 = self.WeightDistributionGraph.plot(pen=(153,51,102))
        self.weightA1 = self.WeightDistributionGraph.plot(pen=(255,0,0))
        self.weightA2 = self.WeightDistributionGraph.plot(pen=(255,102,0))
        self.weightA3 = self.WeightDistributionGraph.plot(pen=(255,255,0))
        self.weightA4 = self.WeightDistributionGraph.plot(pen=(0,255,0))
        self.weightA5 = self.WeightDistributionGraph.plot(pen=(0,255,255))
        self.weightA6 = self.WeightDistributionGraph.plot(pen=(255,0,255))
        self.weightA7 = self.WeightDistributionGraph.plot(pen=(255,255,255))
        self.weightAxYData = None 
        
        self.rawDistributionGraph.setMenuEnabled(False)
        self.rawDistributionGraph.showGrid(x=True,y=True)
        self.rawDistributionGraph.setLabel('left','Raw Data','point')
        self.rawDistributionGraph.setLabel('bottom','Time','s')
        self.rawA0 = self.rawDistributionGraph.plot(pen=(153,51,102))
        self.rawA1 = self.rawDistributionGraph.plot(pen=(255,0,0))
        self.rawA2 = self.rawDistributionGraph.plot(pen=(255,102,0))
        self.rawA3 = self.rawDistributionGraph.plot(pen=(255,255,0))
        self.rawA4 = self.rawDistributionGraph.plot(pen=(0,255,0))
        self.rawA5 = self.rawDistributionGraph.plot(pen=(0,255,255))
        self.rawA6 = self.rawDistributionGraph.plot(pen=(255,0,255))
        self.rawA7 = self.rawDistributionGraph.plot(pen=(255,255,255))
        self.rawAxYData = None        
        
        self.x = None
        self.bufferSize = None
        self.renderDelayCounterUpperLimit = None
        self.renderBoostDelayCounter = 0

        self.processedSampleCount = int(0)
        self.msecSpeedCheckDelay = 250
        self.processingSpeedBar.setMaximum(int(self.msecSpeedCheckDelay/10))
        self.speedCheckTimer = QtCore.QTimer()
        self.speedCheckTimer.setSingleShot(False)
        self.speedCheckTimer.setInterval(self.msecSpeedCheckDelay)
        
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
    
        self.hostAddress = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.listenSocket.bind((self.hostAddress, 11247))
        except socket.error as msg:
            eprint('Socket binding is failed!!! Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        self.listenSocket.listen(10)
        print('Smart Shoe Server ' + self.hostAddress + ' is listening on port 11247 ...')
        self.clientConnection = None
        self.clientAddress = None

        self.controlPipe = ctrlPipe
        self.dataPipe = datPipe

        self.isMatLabConnectionStateConfirmed = True
        self.isMatLabConnected = False

        self.app.lastWindowClosed.connect(self.quit)
        self.timer.timeout.connect(self.updateGraphics)
        self.speedCheckTimer.timeout.connect(self.updateProcessingSpeedBar)
        self.SampleLimitation.valueChanged.connect(self.updateInterval)
        self.matlabSwitch.clicked.connect(self.signalMatLabConnection)        
    def run(self):
        print('Waiting for client ...')
        self.clientConnection, self.clientAddress = self.listenSocket.accept()
        self.clientConnection.settimeout(3)
        print('Connected with ' + self.clientAddress[0] + ':' + str(self.clientAddress[1]))  
        self.MainWindow.show()
        self.updateInterval(self.SampleLimitation.value())        
        self.timer.start(1000)
        self.app.exec_()         
    def updateInterval(self,interval):
        self.bufferSize = int(interval*100)
        self.renderDelayCounterUpperLimit = int(interval)
        self.x = np.linspace(-interval,0.0,self.bufferSize)
        self.rawAxYData = np.zeros([8,self.bufferSize], dtype = int)
        self.weightAxYData = np.zeros([8,self.bufferSize], dtype = float)
    def updateGraphics(self):
        global rawDataToWeightDicts
        print("Smart Shoe Monitor is about to run !")        
        self.timer.timeout.disconnect(self.updateGraphics)        
        self.speedCheckTimer.start()
        rawDataPacket = None
        rawDataIntArr = np.zeros([8,1], dtype = int)
        WeightDataIntArr = np.zeros([8,1], dtype = float)
        renderDelayCounter = 0
        while True:
            try:
                rawDataPacket = self.clientConnection.recv(17)
            except OSError:
                eprint('Timed out for data reception from ' + self.clientAddress[0])
                self.app.closeAllWindows()
                return
            except EOFError:
                eprint('Unexpectedly disconnected from ' + self.clientAddress[0])
                self.app.closeAllWindows()
                return
            except:
                eprint('Unknown Error occurs in the connection with ' + self.clientAddress[0])
                self.app.closeAllWindows()
                return
            if len(rawDataPacket) == 17 and rawDataPacket[0] == 82:
                self.processedSampleCount += 1
                renderDelayCounter += 1
                rawDataPacket = rawDataPacket[1:]                    
                self.rawAxYData[:,:-1] = self.rawAxYData[:,1:]
                self.weightAxYData[:,:-1] = self.weightAxYData[:,1:]
                for i in range(0,8,1):
                    tmpInt = rawDataPacket[i*2]*43 + rawDataPacket[i*2+1] - 2112
                    if tmpInt < 0 or tmpInt > 1023:
                        tmpInt = 0
                    rawDataIntArr[i,0] = tmpInt
                    WeightDataIntArr[i,0] = rawDataToWeightDicts[i][tmpInt]
                self.rawAxYData[:,-1] = rawDataIntArr[:,0]
                self.weightAxYData[:,-1] = WeightDataIntArr[:,0]
                if self.isMatLabConnected:
                    self.dataPipe.send(rawDataIntArr.tolist()+WeightDataIntArr.tolist())
                if renderDelayCounter >= self.renderDelayCounterUpperLimit:
                    renderDelayCounter = 0
                    self.rawA0.setData(self.x,self.rawAxYData[0])
                    self.rawA1.setData(self.x,self.rawAxYData[1])
                    self.rawA2.setData(self.x,self.rawAxYData[2])
                    self.rawA3.setData(self.x,self.rawAxYData[3])
                    self.rawA4.setData(self.x,self.rawAxYData[4])
                    self.rawA5.setData(self.x,self.rawAxYData[5])
                    self.rawA6.setData(self.x,self.rawAxYData[6])
                    self.rawA7.setData(self.x,self.rawAxYData[7])
                    self.weightA0.setData(self.x,self.weightAxYData[0])
                    self.weightA1.setData(self.x,self.weightAxYData[1])
                    self.weightA2.setData(self.x,self.weightAxYData[2])
                    self.weightA3.setData(self.x,self.weightAxYData[3])
                    self.weightA4.setData(self.x,self.weightAxYData[4])
                    self.weightA5.setData(self.x,self.weightAxYData[5])
                    self.weightA6.setData(self.x,self.weightAxYData[6])
                    self.weightA7.setData(self.x,self.weightAxYData[7])
                    self.WeightDistributionMap.updateColor(WeightDataIntArr)
                    self.currentGaitPhase.updateGait(sum(rawDataIntArr)>80,WeightDataIntArr)
            self.app.processEvents()
    def updateProcessingSpeedBar(self):
        speedQuality = float(self.processedSampleCount/self.processingSpeedBar.maximum())
        self.processingSpeedBar.setValue(self.processedSampleCount)
        if self.renderDelayCounterUpperLimit > 0 and speedQuality >= 1:
            self.renderBoostDelayCounter += 1
            if self.renderBoostDelayCounter > 3:
                self.renderBoostDelayCounter = 0
                self.renderDelayCounterUpperLimit -= 1                
        elif speedQuality < 0.8:
            self.renderBoostDelayCounter = 0
            self.renderDelayCounterUpperLimit += 1
        self.processedSampleCount = 0
    def quit(self):
        print("Smart Shoe Monitor is about to close !")
        try:
            self.listenSocket.close()
            self.dataPipe.close()
            if self.isMatLabConnected:
                self.controlPipe.send(7)
                time.sleep(0.1)
            self.controlPipe.send(2)
            time.sleep(0.1)
            self.controlPipe.close()            
            self.app.quit()
        except: pass
        finally:
            sys.exit()
    def signalMatLabConnection(self):
        if self.isMatLabConnectionStateConfirmed:
            self.isMatLabConnectionStateConfirmed = False
            try:                  
                self.controlPipe.send(7 if self.isMatLabConnected else 9)
            except: pass
            self.matlabSwitch.setText("WAIT ...")            
            Thread(target=self.updateMatLabConnection).start() 
    def updateMatLabConnection(self):
        with SmartShoeMonitor.lock:
            isMatLabConnected = False
            try:
                isMatLabConnected = self.controlPipe.recv()
            except: pass
            if isMatLabConnected:
                self.matlabSwitch.setIcon(self.icon2)
                tmpDataList = [[-511]]*8 + [[-15]]*8
                self.dataPipe.send(tmpDataList)
                self.dataPipe.send(tmpDataList)
                self.dataPipe.send([1])
                self.dataPipe.send(tmpDataList)
                self.dataPipe.send(tmpDataList)
            else:
                self.matlabSwitch.setIcon(self.icon1)
                tmpDataList = [[-1023]]*8 + [[-30]]*8
                self.dataPipe.send(tmpDataList)
                self.dataPipe.send(tmpDataList)
            self.isMatLabConnected = isMatLabConnected
            self.app.processEvents()
            time.sleep(0.1)
            self.matlabSwitch.setText("MATLAB")            
            self.isMatLabConnectionStateConfirmed = True
        
                
class MatLabCommunication(Process):
    lock = Lock()
    def __init__(self, ctrlPipe, datPipe):
        super().__init__()
        self.controlPipe = ctrlPipe
        self.dataPipe = datPipe
        self.isMatLabConnectionStateRequestNotChecked = True
        self.isMatLabConnected = False
        self.isStreamingStartMarked = False
        self.currentMatEng = None
        self.selfTerminationNotRequested = True
    def run(self):
        while self.selfTerminationNotRequested:
            if self.isMatLabConnectionStateRequestNotChecked:
                self.isMatLabConnectionStateRequestNotChecked = False
                Thread(target=self.updateMatLabConnection).start()                
            if self.isMatLabConnected:
                try:
                    if self.isStreamingStartMarked:
                        self.isStreamingStartMarked = False
                        markedStartList = []
                        while len(markedStartList) != 1:
                            markedStartList = self.dataPipe.recv()
                    dataList = self.dataPipe.recv()
                    self.currentMatEng.insertToBag(matlab.double(dataList))
                except: pass
        print("Disconnected from MatLab Communication Process !")
    def updateMatLabConnection(self):
        with MatLabCommunication.lock:
            def replyMatLabConnectionState(booleanValue):
                self.isMatLabConnected = booleanValue
                time.sleep(0.1)
                try:
                    self.controlPipe.send(booleanValue)
                    if booleanValue:
                        self.isStreamingStartMarked = True
                    else:
                        self.currentMatEng.quit()
                except: pass
                self.isMatLabConnectionStateRequestNotChecked = True
            requestedMatLabState = False
            try:
                requestedMatLabState = self.controlPipe.recv()
            except EOFError:
                requestedMatLabState == 2
            except:
                self.isMatLabConnectionStateRequestNotChecked = True
                return
            if requestedMatLabState == 9 and not self.isMatLabConnected:
                sharedMatLabSessions = matlab.engine.find_matlab()
                isAvailableSharedMatLabSessionAccepted = False
                if 'SmartShoeMonitor' in sharedMatLabSessions:
                    isAvailableSharedMatLabSessionAccepted = True
                    self.currentMatEng = matlab.engine.connect_matlab('SmartShoeMonitor')
                elif sharedMatLabSessions:
                        tmpTopLevelWin = Tk()
                        tmpTopLevelWin.attributes("-topmost",True)
                        tmpTopLevelWin.withdraw()
                        isAvailableSharedMatLabSessionAccepted = messagebox.askyesno(title="Shared MatLab Session Detected", message="There is a currently opening shared MatLab Session named " + sharedMatLabSessions[-1] + ". Do you want to stream data into this one?")
                        tmpTopLevelWin.destroy()
                        if isAvailableSharedMatLabSessionAccepted:
                            self.currentMatEng = matlab.engine.connect_matlab(sharedMatLabSessions[-1])
                if not isAvailableSharedMatLabSessionAccepted:
                    try:
                        Popen("matlab -r \"matlab.engine.shareEngine(\'SmartShoeMonitor\')\"")
                    except:
                        eprint("Failed to open MatLab !")
                        replyMatLabConnectionState(False)
                        return
                    while 'SmartShoeMonitor' not in sharedMatLabSessions:
                        time.sleep(2)
                        sharedMatLabSessions = matlab.engine.find_matlab()                    
                    self.currentMatEng = matlab.engine.connect_matlab('SmartShoeMonitor')
                time.sleep(0.1)
                try:
                    self.currentMatEng.cd(os.path.dirname(os.path.abspath(__file__)))
                except:
                    eprint("Failed to establish MatLab communication !")
                    replyMatLabConnectionState(False)
                    return
                replyMatLabConnectionState(True)            
            elif requestedMatLabState == 7 and self.isMatLabConnected:
                replyMatLabConnectionState(False)
            elif requestedMatLabState == 2:
                self.dataPipe.close()
                self.controlPipe.close()
                self.selfTerminationNotRequested = False

rawDataToWeightDicts = []
maxSensibleWeight = 0
                
if __name__ == "__main__":
    print("\n\n\n==================SMART SHOE MONITOR=========================\n")

    print("Importing Data Files ...")
    for i in range(1,9,1):
        f = None
        try:
            f = open('data/pyDictSensor' + str(i) + '.txt','r')
        except:
            eprint('Data File Not Found data/pyDictSensor' + str(i) + '.txt !')
            sys.exit()
        aDict = []
        try:
            for line in f:
                lineParts = line.strip().split('\t')
                if len(lineParts) > 1:
                    tmpFloat = float(lineParts[1])*10
                    if tmpFloat > maxSensibleWeight:
                        maxSensibleWeight = tmpFloat
                    aDict.append(tmpFloat)
            if len(aDict) != 1024:
                print('Missing Data In File data/pyDictSensor' + str(i) + '.txt !')
                sys.exit()
        except:
            eprint('Invalid Data File data/pyDictSensor' + str(i) + '.txt !')
            sys.exit()
        f.close()
        rawDataToWeightDicts.append(aDict)
        print('\tRead data/pyDictSensor' + str(i) + '.txt !')           

    print('\n')      
    childControlPipe, parentControlPipe = Pipe(True)
    childDataPipe, parentDataPipe = Pipe(False)    
    MatLabCommunication(childControlPipe,childDataPipe).start()
    SmartShoeMonitor(parentControlPipe,parentDataPipe).run()

