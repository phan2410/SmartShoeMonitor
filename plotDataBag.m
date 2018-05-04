figure();
hold on;
grid on;
a0plot = plot(DataBag(1,:),'color',[128 0 0]/255);%brown-sensor1
a1plot = plot(DataBag(2,:),'color',[255 0 0]/255);%red-sensor2
a2plot = plot(DataBag(3,:),'color',[255 102 0]/255);%orange-sensor3
a3plot = plot(DataBag(4,:),'color',[255,255,0]/255);%yellow-sensor4
a4plot = plot(DataBag(5,:),'color',[0,255,0]/255);%green-sensor5
a5plot = plot(DataBag(6,:),'color',[0,0,255]/255);%blue-sensor6
a6plot = plot(DataBag(7,:),'color',[153 153 255]/255);%violet-sensor7
a7plot = plot(DataBag(8,:),'color',[0 0 0]/255);%black-sensor8
set(a0plot,'YDataSource','DataBag(1,:)');
set(a1plot,'YDataSource','DataBag(2,:)');
set(a2plot,'YDataSource','DataBag(3,:)');
set(a3plot,'YDataSource','DataBag(4,:)');
set(a4plot,'YDataSource','DataBag(5,:)');
set(a5plot,'YDataSource','DataBag(6,:)');
set(a6plot,'YDataSource','DataBag(7,:)');
set(a7plot,'YDataSource','DataBag(8,:)');

%If streaming, the following lines will update plot with rate of 1 FPS
%CAUTION: Comment out these lines if using cpu less than 4 real core.
%Otherwise, this matlab session and the smart shoe monitor will crash!!!
t = timer('TimerFcn', 'linkdata on;','StartDelay',1);
start(t)

