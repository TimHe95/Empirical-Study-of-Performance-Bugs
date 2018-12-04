function [raw_data_dir, data4ML_dir, res_file] = dir_init(runmod)
    if strcmp(runmod, 'test')
        raw_data_dir = 'raw_data_test';
        data4ML_dir = 'data4MLtest';
        res_file = 'res_test.txt'; 
    else
        if strcmp(runmod, 'train')
            raw_data_dir = 'raw_data_train';
            data4ML_dir = 'data4MLtrain';
            res_file = 'res_train.txt';
        else
            disp('[ERROR] set runmod to "test" or "train"');
            exit;
        end
    end
    
    [status, message, messageid] = rmdir(data4ML_dir, 's')
    if status == 1
        disp('[NOTE] old files deleted.');
    end
    mkdir(data4ML_dir);
    
    if exist(res_file, 'file')
        delete(res_file);
    end
end