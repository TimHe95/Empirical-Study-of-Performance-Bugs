%CREATEFIT1(B,A,C)
%  Create a fit.
%
%  Data for 'untitled fit 1' fit:
%      X Input : b
%      Y Input : a
%      Z Output: c
%  Output:
%      fitresult : a fit object representing the fit.
%      gof : structure with goodness-of fit info.
function [fitresult, gof] = createFit_inter(a, b, c, name, data4ML_dir)

[xData, yData, zData] = prepareSurfaceData( b, a, c );

% Set up fittype and options.
ft = 'cubicinterp';

% Fit model to data.
[fitresult, gof] = fit( [xData, yData], zData, ft, 'Normalize', 'on' );

% Make contour plot.
fig = figure( 'Name', name );
plot( fitresult, [xData, yData], zData, 'Style', 'Contour' );
grid on

set(fig,'visible','off');
saveas(fig,[data4ML_dir,'/',name,'.jpg']);

%fig2 = figure('Name', [name,'_2']);
%plot( fitresult, [xData, yData], zData);
%grid on
%view( -13.1, 44.4 );
%set(fig2,'visible','off');
%saveas(fig2,[data4ML_dir,'/',name,'_2.jpg']);

end

