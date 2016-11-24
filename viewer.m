clear all;
% ITU-R BT.709, RGB limited range, results in the following transform matrix:
%  1.000   0.000   1.570
%  1.000  -0.187  -0.467
%  1.000   1.856   0.000
T = [1.000   0.000   1.570;
     1.000  -0.187  -0.467;
     1.000   1.856   0.000];

Y = double(dlmread('Luma'));
Cb = imresize(dlmread('Cb'),2, 'nearest') - 128;
Cr = imresize(dlmread('Cr'),2, 'nearest') - 128;
% YCbCr = cat(3, Y, Cb, Cr);

% rgb = zeros(size(Y,1),size(Y,2),3);
R = T(1,1) * Y + T(1,2) * Cb + T(1,3) * Cr;
G = T(2,1) * Y + T(2,2) * Cb + T(2,3) * Cr;
B = T(3,1) * Y + T(3,2) * Cb + T(3,3) * Cr;
RGB_255 = cat(3,R,G,B);
RGB = uint8(round(RGB_255));
% RGB = RGB_255 / 255;
imshow(RGB);
dlmwrite('output_rgb.txt', RGB);
imwrite(RGB, 'output.png');