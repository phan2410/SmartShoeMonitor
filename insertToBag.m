function returnCode = insertToBag(dblArr16x1)
    %insertToDataBag
    if ismember('DataBag',evalin('base','who'))
        DataBag = evalin('base', 'DataBag');
        DataBag = circshift(DataBag,[0 -1]);
        if sum(DataBag(:,1)) ~= 0
            DataBag = [zeros(8,5000) DataBag];
        end
    else
        DataBag = int16(zeros(8,5000));        
    end
    DataBag(:,end) = int16(dblArr16x1(1:8));
    assignin('base','DataBag',DataBag);
    clear DataBag;
    %insertToPressureBag
    if ismember('PressureBag',evalin('base','who'))
        PressureBag = evalin('base', 'PressureBag');
        PressureBag = circshift(PressureBag,[0 -1]);
        if sum(PressureBag(:,1)) ~= 0
            PressureBag = [zeros(8,5000) PressureBag];
        end
    else
        PressureBag = double(zeros(8,5000));        
    end
    PressureBag(:,end) = dblArr16x1(9:16);
    assignin('base','PressureBag',PressureBag);
    returnCode = true;
end