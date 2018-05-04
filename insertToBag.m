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
    %insertToWeightBag
    if ismember('WeightBag',evalin('base','who'))
        WeightBag = evalin('base', 'WeightBag');
        WeightBag = circshift(WeightBag,[0 -1]);
        if sum(WeightBag(:,1)) ~= 0
            WeightBag = [zeros(8,5000) WeightBag];
        end
    else
        WeightBag = double(zeros(8,5000));        
    end
    WeightBag(:,end) = dblArr16x1(9:16);
    assignin('base','WeightBag',WeightBag);
    returnCode = true;
end