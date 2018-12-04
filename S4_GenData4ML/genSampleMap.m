function [map] = genSampleMap(min, max, step)
    points = ceil((max - min + 1) / step);

    map = zeros(points^2, 2);

    index = 1;
    for i = min:step:max
        for j = min:step:max
            map(index, 1) = i;
            map(index, 2) = j;
            index = index + 1;
        end
    end
end