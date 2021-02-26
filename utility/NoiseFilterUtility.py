from scipy.interpolate import griddata
import numpy as np
import matplotlib.pyplot as plt
import cv2
import math

from FringeAnalysisFunctions import *


# def func(x, y):
#     return x*(1-x)*np.cos(4*np.pi*x) * np.sin(4*np.pi*y**2)**2
#
#
# grid_x, grid_y = np.mgrid[0:1:100j, 0:1:200j]
#
# print(grid_x, grid_y)
#
# points = np.random.rand(1000, 2)
# values = func(points[:,0], points[:,1])
#
# print(points)
# print(values)
#
# grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
# grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
# grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')
#
# plt.subplot(221)
# plt.imshow(func(grid_x, grid_y).T, extent=(0,1,0,1), origin='lower')
# plt.plot(points[:,0], points[:,1], 'k.', ms=1)
# plt.title('Original')
# plt.subplot(222)
# plt.imshow(grid_z0.T, extent=(0,1,0,1), origin='lower')
# plt.title('Nearest')
# plt.subplot(223)
# plt.imshow(grid_z1.T, extent=(0,1,0,1), origin='lower')
# plt.title('Linear')
# plt.subplot(224)
# plt.imshow(grid_z2.T, extent=(0,1,0,1), origin='lower')
# plt.title('Cubic')
# plt.gcf().set_size_inches(6, 6)
# plt.show()


def apply_filter(image, method='nearest', blur="mean", ksize=(3, 3)):
    height, length = image.shape
    pitch = getPitch(image)

    print(f"image_size = {height}, {length}")
    print(f"pitch      = {pitch}")

    block_height = max(min(height // 60, int(pitch * 1.5)), pitch)
    block_length = max(min(length // 60, int(pitch * 1.5)), pitch)

    x_offset = block_height / 2
    y_offset = block_length / 2

    print(f"block_size = {block_height}, {block_length}")

    points = []
    values = []

    for x in range(0, height, block_height):
        for y in range(0, length, block_length):
            if x + x_offset < height and y + y_offset < length:
                points.append([x + x_offset, y + y_offset])
            else:
                points.append([(x + height - 1) / 2, (y + length - 1) / 2])

            block_sum = 0
            amount = 0
            for xx in range(0, block_height):
                for yy in range(0, block_length):
                    tx = x + xx
                    ty = y + yy

                    if tx < height and ty < length:
                        block_sum += image[tx][ty]
                        amount += 1

            values.append(block_sum / amount)

    points = np.array(points)
    values = np.array(values)

    grid_x, grid_y = np.mgrid[0: height, 0: length]

    mat_a = griddata(points, values, (grid_x, grid_y), method=method)

    # print(mat_a[100])
    # print(mat_a[:][100])

    mat_temp = image - mat_a

    # print(mat_temp[100])
    # print(mat_temp[:][100])

    # mat_temp = np.nan_to_num(image - mat_a, nan=0)

    values = []

    for x in range(0, height, block_height):
        for y in range(0, length, block_length):
            max_value = min_value = mat_temp[x][y]

            for xx in range(0, block_height):
                for yy in range(0, block_length):
                    tx = x + xx
                    ty = y + yy

                    if tx < height and ty < length and not math.isnan(mat_temp[tx][ty]):
                        if mat_temp[tx][ty] > max_value:
                            max_value = mat_temp[tx][ty]
                        elif mat_temp[tx][ty] < min_value:
                            min_value = mat_temp[tx][ty]

            values.append(max_value - min_value)

    values = np.array(values)
    print(values)

    mat_b = griddata(points, values, (grid_x, grid_y), method=method)

    # print(mat_b[100])
    # print(mat_b[:][100])

    mat_ni = mat_temp / mat_b

    min_value, max_value = find_range(mat_ni)
    print(f"range      = {min_value}, {max_value}")

    step = 255 / (max_value - min_value)
    offset = - min_value
    for x in range(0, height):
        for y in range(0, length):
            if math.isnan(mat_ni[x][y]):
                mat_ni[x][y] = 0
            else:
                mat_ni[x][y] = int((mat_ni[x][y] + offset) * step)

    mat_ni = mat_ni.astype('uint8')

    if blur == 'mean':
        return cv2.blur(mat_ni, ksize)
    elif blur == 'median':
        return cv2.medianBlur(mat_ni, ksize[0])
    else:
        return mat_ni


if __name__ == "__main__":

    image = cv2.imread('D:\\UTD\\Fringe-Analyzer\\TestPics\\2in-ref.jpg', cv2.IMREAD_GRAYSCALE)
    processed_image = apply_filter(image, method="linear", blur='median')

    cv2.imshow("Filtered Image", processed_image)
    cv2.waitKey()
