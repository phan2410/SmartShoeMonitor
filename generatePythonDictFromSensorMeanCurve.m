function PythonDict = generatePythonDictFromSensorMeanCurve(SenMeanCurve)
    SenMeanCurve(:,2) = round(SenMeanCurve(:,2));
    PythonDict = zeros(1024,2);
    for i = 1:(max(size(SenMeanCurve))-1)
        A = [SenMeanCurve(i,2) 1; SenMeanCurve(i+1,2) 1];
        B = [SenMeanCurve(i,1);SenMeanCurve(i+1,1)];
        X = linsolve(A,B);
        for j = SenMeanCurve(i,2):SenMeanCurve(i+1,2)
            PythonDict(j+1,:) = [j X(1)*j+X(2)];
        end
    end
    if j < 1023
        for k = j:1023
            PythonDict(k+1,:) = [k X(1)*k+X(2)];
        end
    end
    xlswrite('lastestPythonDict.xls',PythonDict)
end