function [a, b, c] = parseData(file, min, max, raw_data_dir, XY_rescale, Z_rescale)
    fid = fopen([raw_data_dir,'/',file.name],'r');
    
    if XY_rescale
        tline_a = fgetl(fid);
        a = rescale(str2num(tline_a),min,max);
        
        tline_b = fgetl(fid);
        b = rescale(str2num(tline_b),min,max);
    else
        tline_a = fgetl(fid);
        a = str2num(tline_a);
        
        tline_b = fgetl(fid);
        b = str2num(tline_b);
    end
    
    c = zeros(length(a), length(b));
    ii = 1;
    while (true)
        tline_c = fgetl(fid);
        if ~ischar(tline_c)
            break;
        end
        ci = str2num(tline_c);
        c(ii, 1:length(ci)) = ci;
        ii = ii + 1;
    end
    fclose(fid);
    
    if Z_rescale
        %c = rescale(c, min, max); % not good!
        c = (max-min) * c / mean(c(:));
    end
end