function returnCode = insertToWeightBag(dblArr8x1)
    if ismember('WeightBag',evalin('base','who'))
        WeightBag = evalin('base', 'WeightBag');
        WeightBag = circshift(WeightBag,[0 -1]);
        if sum(WeightBag(:,1)) ~= 0
            WeightBag = [zeros(8,5000) WeightBag];
        end
    else
        WeightBag = double(zeros(8,5000));        
    end
    WeightBag(:,end) = dblArr8x1;
    assignin('base','WeightBag',WeightBag);
    returnCode = true;
end