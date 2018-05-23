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
        self.PressureDistributionMap = RightFootPressureDistributionMap(self.centralWidget)
        self.PressureDistributionMap.setGeometry(QtCore.QRect(10, 10, 200, 470))
        self.PressureDistributionMap.setObjectName("PressureDistributionMap")
        self.PressureDistributionGraph = PlotWidget(self.centralWidget)
        self.PressureDistributionGraph.setGeometry(QtCore.QRect(220, 10, 794, 310))
        self.PressureDistributionGraph.setObjectName("PressureDistributionGraph")
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

class RightFootPressureDistributionMap(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self,parent)
        self.backgroundPixMap = QtGui.QPixmap('icon/PressureDistributionMapBackground.png','PNG').scaled(200, 470)
        self.painter = QtGui.QPainter(self.backgroundPixMap)
        self.brush0 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush1 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush2 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush3 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush4 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush5 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush6 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        self.brush7 = QtGui.QBrush(QtGui.QColor(255,255,255,255))
        global maxSensiblePressure
        self.ColorTemperatureToPressureRatio = float(1023/maxSensiblePressure)        
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
    def GenBrushFromPressureData(self,PressureData):
        colorTemp = int(PressureData*self.ColorTemperatureToPressureRatio)
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
    def updateColor(self,PressureDataIntArr):
        self.brush0 = self.GenBrushFromPressureData(PressureDataIntArr[0])
        self.brush1 = self.GenBrushFromPressureData(PressureDataIntArr[1])
        self.brush2 = self.GenBrushFromPressureData(PressureDataIntArr[2])
        self.brush3 = self.GenBrushFromPressureData(PressureDataIntArr[3])
        self.brush4 = self.GenBrushFromPressureData(PressureDataIntArr[4])
        self.brush5 = self.GenBrushFromPressureData(PressureDataIntArr[5])
        self.brush6 = self.GenBrushFromPressureData(PressureDataIntArr[6])
        self.brush7 = self.GenBrushFromPressureData(PressureDataIntArr[7])
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
    def updateGait(self,PressureDataIntArr):
        SumPressureData = np.sum(PressureDataIntArr)
        if SumPressureData > 99:
            sumHindFoot = np.sum(PressureDataIntArr[6:8])
            midFoot = PressureDataIntArr[5]
            sumForeFoot = np.sum(PressureDataIntArr[1:5])
            greatToe = PressureDataIntArr[0]
            if sumHindFoot > 20:                
                if midFoot > 18:
                    if sumForeFoot >= 27:
                        if sumHindFoot > sumForeFoot:
                            self.currentPixMap = self.LoadingResponsePixMap
                        else:
                            self.currentPixMap = self.MidStancePixMap
                    else:
                        self.currentPixMap = self.InitialContactPixMap
                else:
                    self.currentPixMap = self.InitialContactPixMap
            else:
                if midFoot > 18:
                    if sumForeFoot >= 27:
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

        self.PressureDistributionGraph.setMenuEnabled(False)
        self.PressureDistributionGraph.showGrid(x=True,y=True)
        self.PressureDistributionGraph.setLabel('left','Pressure','kPa')
        self.PressureDistributionGraph.setLabel('bottom','Time','s')
        self.PressureA0 = self.PressureDistributionGraph.plot(pen=(153,51,102))
        self.PressureA1 = self.PressureDistributionGraph.plot(pen=(255,0,0))
        self.PressureA2 = self.PressureDistributionGraph.plot(pen=(255,102,0))
        self.PressureA3 = self.PressureDistributionGraph.plot(pen=(255,255,0))
        self.PressureA4 = self.PressureDistributionGraph.plot(pen=(0,255,0))
        self.PressureA5 = self.PressureDistributionGraph.plot(pen=(0,255,255))
        self.PressureA6 = self.PressureDistributionGraph.plot(pen=(255,0,255))
        self.PressureA7 = self.PressureDistributionGraph.plot(pen=(255,255,255))
        self.PressureAxYData = None 
        
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
        self.PressureAxYData = np.zeros([8,self.bufferSize], dtype = float)
    def updateGraphics(self):
        global rawDataToPressureDicts
        print("Smart Shoe Monitor is about to run !")        
        self.timer.timeout.disconnect(self.updateGraphics)        
        self.speedCheckTimer.start()
        rawDataPacket = None
        rawDataIntArr = np.zeros(8, dtype = int)
        PressureDataIntArr = np.zeros(8, dtype = float)
        renderDelayCounter = 0
        isPressureOnMeanCurve = np.ones(8, dtype = bool)
        PressureCurveChangeCounters = np.zeros(8, dtype = int)
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
                self.PressureAxYData[:,:-1] = self.PressureAxYData[:,1:]
                for i in range(0,8,1):
                    tmpInt = rawDataPacket[i*2]*43 + rawDataPacket[i*2+1] - 2112
                    tmpInt1 = rawDataIntArr[i]
                    if tmpInt < 0 or tmpInt > 1023:
                        tmpInt = 0
                    tmpInt2 = tmpInt - tmpInt1
                    rawDataIntArr[i] = tmpInt
                    if isPressureOnMeanCurve[i]:
                        if tmpInt2 < 0 and abs(tmpInt2) > rawDataToPressureFromLoadCurveRMSEOnADCDicts[i,tmpInt1]:
                            PressureCurveChangeCounters[i] += 1
                            if PressureCurveChangeCounters[i] > 3:
                                isPressureOnMeanCurve[i] = False
                                PressureDataIntArr[i] = rawDataToPressureFromUnloadCurveMeanDicts[i,tmpInt]
                                PressureCurveChangeCounters[i] = 0
                            else:
                                PressureDataIntArr[i] = rawDataToPressureFromLoadCurveMeanDicts[i,tmpInt]
                        else:                            
                            PressureDataIntArr[i] = rawDataToPressureFromLoadCurveMeanDicts[i,tmpInt]
                            PressureCurveChangeCounters[i] = 0                            
                    else:
                        if tmpInt2 > 0 and abs(tmpInt2) > rawDataToPressureFromUnloadCurveRMSEOnADCDicts[i,tmpInt1]:
                            PressureCurveChangeCounters[i] += 1
                            if PressureCurveChangeCounters[i] > 3:
                                isPressureOnMeanCurve[i] = True
                                PressureDataIntArr[i] = rawDataToPressureFromLoadCurveMeanDicts[i,tmpInt]
                                PressureCurveChangeCounters[i] = 0
                            else:
                                PressureDataIntArr[i] = rawDataToPressureFromUnloadCurveMeanDicts[i,tmpInt]
                        else:                            
                            PressureDataIntArr[i] = rawDataToPressureFromUnloadCurveMeanDicts[i,tmpInt]
                            PressureCurveChangeCounters[i] = 0           
                self.rawAxYData[:,-1] = rawDataIntArr
                self.PressureAxYData[:,-1] = PressureDataIntArr
                if self.isMatLabConnected:
                    self.dataPipe.send(rawDataIntArr.tolist()+PressureDataIntArr.tolist())
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
                    self.PressureA0.setData(self.x,self.PressureAxYData[0])
                    self.PressureA1.setData(self.x,self.PressureAxYData[1])
                    self.PressureA2.setData(self.x,self.PressureAxYData[2])
                    self.PressureA3.setData(self.x,self.PressureAxYData[3])
                    self.PressureA4.setData(self.x,self.PressureAxYData[4])
                    self.PressureA5.setData(self.x,self.PressureAxYData[5])
                    self.PressureA6.setData(self.x,self.PressureAxYData[6])
                    self.PressureA7.setData(self.x,self.PressureAxYData[7])
                    self.PressureDistributionMap.updateColor(PressureDataIntArr)
                    self.currentGaitPhase.updateGait(PressureDataIntArr)
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

rawDataToPressureFromLoadCurveMeanDicts = np.zeros([8,1024],dtype=int)
rawDataToPressureFromLoadCurveRMSEOnADCDicts = np.zeros([8,1024],dtype=int)
rawDataToPressureFromUnloadCurveMeanDicts = np.zeros([8,1024],dtype=int)
rawDataToPressureFromUnloadCurveRMSEOnADCDicts = np.zeros([8,1024],dtype=int)
maxSensiblePressure = 0
                
if __name__ == "__main__":
    print("\n\n\n==================SMART SHOE MONITOR=========================\n")
    
    for DataCategory in ['LoadCurveMean','LoadCurveRMSEOnADC','UnloadCurveMean','UnloadCurveRMSEOnADC']:
        for i in range(1,9,1):        
            f = None
            currentFileName = 'data/pyDictSen' + str(i) + DataCategory + '.sss'
            try:
                f = open(currentFileName,'r')
            except:
                eprint('Data File Not Found ' + currentFileName)
                sys.exit()
            aDict = []
            try:
                for line in f:                    
                    tmpFloat = float(line.strip())
                    if DataCategory in ['LoadCurveMean','UnloadCurveMean'] and tmpFloat > maxSensiblePressure:
                        maxSensiblePressure = tmpFloat
                    aDict.append(tmpFloat)
                if len(aDict) != 1024:
                    eprint('Missing Data In File ' + currentFileName)
                    sys.exit()
            except:
                eprint('Invalid Data File ' + currentFileName)
                sys.exit()
            f.close()
            if DataCategory == 'LoadCurveMean':
                rawDataToPressureFromLoadCurveMeanDicts[i-1] = aDict
            elif DataCategory == 'LoadCurveRMSEOnADC':
                rawDataToPressureFromLoadCurveRMSEOnADCDicts[i-1] = aDict
            elif DataCategory == 'UnloadCurveMean':
                rawDataToPressureFromUnloadCurveMeanDicts[i-1] = aDict
            else:
                rawDataToPressureFromUnloadCurveRMSEOnADCDicts[i-1] = aDict
      
    childControlPipe, parentControlPipe = Pipe(True)
    childDataPipe, parentDataPipe = Pipe(False)    
    MatLabCommunication(childControlPipe,childDataPipe).start()
    SmartShoeMonitor(parentControlPipe,parentDataPipe).run()

