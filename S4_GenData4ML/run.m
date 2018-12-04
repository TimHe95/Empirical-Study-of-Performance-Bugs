runmod = 'train';
[raw_data_dir, data4ML_dir, res_file] = dir_init(runmod);

XY_rescale = true;
Z_rescale = true;
max = 10;   % need rescale = true
min = -10;  % need rescale = true
step = 1;   % need rescale = true

% which means (10-(-10)+1)^2=441 points will be used to describe a curve.
map = genSampleMap(min, max, step);

files = dir(fullfile(raw_data_dir, '*'));
LengthFiles = length(files);

% for each sample(in form of points need fiting) in raw_data folder
for i = 1:LengthFiles
    if (files(i).isdir) || strcmp(files(i).name, '.DS_Store')
        continue;
    end
    % parse the points into 3 vectors which represent for 'x,y,z' and
    % rescale it to [min, max]^3 (like a cube)
    [a, b, c] = parseData(files(i), min, max, raw_data_dir, XY_rescale, Z_rescale);

    % curve fitting
    [fitresult, gof] = createFit_inter(a, b, c, files(i).name, data4ML_dir);
    
    % the way I am using now to discribe a curve.
    rescontent = fitresult(map)';
    
    % write it to file.
    dlmwrite(res_file, rescontent, '-append', 'precision', '%.3f', 'delimiter', ' ')
    
    % progress report.
    if mod(i, 50)==0
        disp([int2str(i),'/',int2str(LengthFiles),' Finished']);
    end
end
