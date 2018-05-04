function makePythonData(SenLoadCurveMean,SenUnloadCurveMean)
    SenMeanCurve = (SenLoadCurveMean + SenUnloadCurveMean)/2;
    pythonDict = generatePythonDictFromSensorMeanCurve(SenMeanCurve);
    figure();
    hold on;
    grid on;
    plot(SenLoadCurveMean(:,2),SenLoadCurveMean(:,1),'r');
    plot(SenUnloadCurveMean(:,2),SenUnloadCurveMean(:,1),'b');
    plot(SenMeanCurve(:,2),SenMeanCurve(:,1),'k');
    plot(pythonDict(:,1),pythonDict(:,2),'g--o');
    assignin('base','pythonDict',pythonDict);
end
