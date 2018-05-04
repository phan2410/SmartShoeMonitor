function plotBag(aBag,isBagStreaming)
    BagName = inputname(1);
    figure();
    hold on;
    grid on;
    a0plot = plot(aBag(1,:),'color',[128 0 0]/255);%brown-sensor1
    a1plot = plot(aBag(2,:),'color',[255 0 0]/255);%red-sensor2
    a2plot = plot(aBag(3,:),'color',[255 102 0]/255);%orange-sensor3
    a3plot = plot(aBag(4,:),'color',[255,255,0]/255);%yellow-sensor4
    a4plot = plot(aBag(5,:),'color',[0,255,0]/255);%green-sensor5
    a5plot = plot(aBag(6,:),'color',[0,0,255]/255);%blue-sensor6
    a6plot = plot(aBag(7,:),'color',[153 153 255]/255);%violet-sensor7
    a7plot = plot(aBag(8,:),'color',[0 0 0]/255);%black-sensor8
    set(a0plot,'YDataSource',strcat(BagName,'(1,:)'));
    set(a1plot,'YDataSource',strcat(BagName,'(2,:)'));
    set(a2plot,'YDataSource',strcat(BagName,'(3,:)'));
    set(a3plot,'YDataSource',strcat(BagName,'(4,:)'));
    set(a4plot,'YDataSource',strcat(BagName,'(5,:)'));
    set(a5plot,'YDataSource',strcat(BagName,'(6,:)'));
    set(a6plot,'YDataSource',strcat(BagName,'(7,:)'));
    set(a7plot,'YDataSource',strcat(BagName,'(8,:)'));

    %If streaming, the following lines will update plot with rate of 1 FPS
    %CAUTION: Comment out these lines if using cpu less than 4 real core.
    %Otherwise, this matlab session and the smart shoe monitor will crash!!!
    if exist('isBagStreaming','var') && isBagStreaming
        t = timer('TimerFcn', 'linkdata on;','StartDelay',1);
        start(t)
    end
end