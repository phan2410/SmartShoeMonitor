function returnCode = insertToDataBag(intArr8x1)
    if ismember('DataBag',evalin('base','who'))
        DataBag = evalin('base', 'DataBag');
        DataBag = circshift(DataBag,[0 -1]);
        if sum(DataBag(:,1)) ~= 0
            DataBag = [zeros(8,5000) DataBag];
        end
    else
        DataBag = int16(zeros(8,5000));        
    end
    DataBag(:,end) = intArr8x1;
    assignin('base','DataBag',DataBag);
    returnCode = true;
end