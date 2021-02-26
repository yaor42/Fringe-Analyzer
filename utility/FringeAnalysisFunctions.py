import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.fftpack
import scipy.ndimage
from skimage.restoration import unwrap_phase


def testImage(pitch=20, dim0=1000, dim1=1250, imgName='fringe_test.png'):
    """Generate and save a test fringe image
        pitch: period of cosine function in px
        dim0: number of rows
        dim1: number of coloumns

        return: ndarray image with dtype of uint8 
    """
    x = np.arange(0, dim1, 1)
    # y = 128 + 128 * np.cos(2 * np.pi / pitch * x)
    y = 255 / 2 * (1 + np.cos(2 * np.pi / pitch * x))
    im = np.empty([dim0, y.shape[0]])
    im[:] = y
    im = im.astype(np.uint8)
    plt.imsave(imgName, im, cmap='gray')
    # plt.imshow(im, cmap='gray')
    # plt.show()
    return im


def testSlopeImage(pitch=20, dim0=1000, dim1=1250, slope=0.1, imgName='slope.png'):
    """Generate and save a test slope fringe image
        pitch: period of cosine function in px
        dim0: number of rows
        dim1: number of coloumns
        slope: slope of the inclined surface in radians

        return: ndarray image with dtype of uint8
    """
    x = np.arange(0, dim1, 1)
    # y = 128 + 128 * np.cos(2 * np.pi / pitch * x - slope * x)
    y = 255 / 2 * (1 + np.cos(2 * np.pi / pitch * x - slope * x))
    im = np.empty([dim0, y.shape[0]])
    im[:] = y
    im = im.astype(np.uint8)
    plt.imsave(imgName, im, cmap='gray')
    # plt.imshow(im, cmap='gray')
    # plt.show()
    return im


def getPitch(img):
    """Get the pitch of the reference image
        img: ndarray that contains the image 

        return: pitch as an integer
    """
    dim0, dim1 = img.shape
    row = img[int(dim0 / 2), :]
    # plt.plot(row)
    # plt.show()
    yf = scipy.fftpack.fft(row)
    yfMag = 2 / dim1 * np.abs(yf[:int(dim1 / 2)])
    xf = np.linspace(0, 0.5, int(dim1 / 2))
    maxIndex = np.argmax(yfMag[3:])
    # plt.plot(xf, yfMag)
    # plt.show()

    return int(1 / xf[maxIndex])


def imgNormalize(img, pitch):
    """Normalize the image when the illuminance is not uniform"""
    return


def fiveStepShift(img, pitch, maskHoles=False):
    """Calculate the phase map based on 5-step shift method
        img: ndarray that contains the image
        pitch: pitch of the reference image in integer

        return: phase map with dtype of float64
    """
    if maskHoles:
        img = maskCircle(img)

    img = img.astype(np.float64)
    img1 = scipy.ndimage.shift(img, (0, -pitch / 2))
    img2 = scipy.ndimage.shift(img, (0, -pitch / 4))
    img3 = img
    img4 = scipy.ndimage.shift(img, (0, pitch / 4))
    img5 = scipy.ndimage.shift(img, (0, pitch / 2))
    # phase = np.arctan(2*(img2 - img4) / (2*img3 - img5 - img1))
    phase = np.arctan2(2 * (img2 - img4), 2 * img3 - img5 - img1)
    # plt.imshow(img1, cmap='gray')
    # plt.show()
    return phase


def centralDiff(array1, array2, array3, dt):
    """Calculate the derivative using central difference
    """
    deri = (array3 - array1) / 2 / dt
    return deri


def centralDiff2(array1, array2, array3, dt):
    """Calculate the derivative using central difference
    """
    deri = (array3 - 2 * array2 + array1) / dt ** 2
    return deri


def fileNameGen(prefix, index, fileType, folderName=''):
    """Generate file name based on the prefix and index number"""
    if index < 10:
        fileName = prefix + str(index) + '.' + fileType
    elif index >= 10 and index < 100:
        fileName = prefix[:-1] + str(index) + '.' + fileType
    elif index >= 100 and index < 1000:
        fileName = prefix[:-2] + str(index) + '.' + fileType
    else:
        fileName = prefix[:-3] + str(index) + '.' + fileType

    if folderName != '':
        fileName = os.path.join(os.getcwd(), folderName, fileName);
    # print(fileName)

    return fileName


def maskCircle_2(img, minRadius=10, maxRadius=40, color=(0, 0, 0)):
    """Detect circular holes in the image and mask with color"""
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 100,
                               param1=100, param2=30,
                               minRadius=minRadius, maxRadius=maxRadius)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle outline
            radius = int(i[2] * 1.1)
            cv2.circle(img, center, radius, color, -1)
    return img


def maskCircle(img, minRadius=10, maxRadius=40, maskRadiusFactor=1.2):
    """Detect circular holes in the image and mask the holes
        Return: masked ndarray
    """
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 100,
                               param1=100, param2=30,
                               minRadius=minRadius, maxRadius=maxRadius)

    mask = np.zeros_like(img, dtype=np.int)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = int(i[2] * maskRadiusFactor)
            cv2.circle(mask, center, radius, 1, -1)

    mask = (mask > 0).tolist()
    mask = np.asarray(mask)
    maskedImg = np.ma.array(img, mask=mask)
    return maskedImg


def unwrapPhase(diffPhase):
    """Unwrap phase"""
    unwrappedPhase = unwrap_phase(diffPhase)
    return unwrappedPhase


def analyze_phase(ref_phase, obj_img, ks, pitch):
    obj_phase = [fiveStepShift(img, pitch) for img in obj_img]
    diff_phase = [phase - ref_phase for phase in obj_phase]
    unwrapped_phase = [unwrapPhase(phase) for phase in diff_phase]
    depth_map = [phase * ks for phase in unwrapped_phase]

    return obj_phase, diff_phase, unwrapped_phase, depth_map


def find_range(input_map):
    min_value = float('inf')
    max_value = -float('inf')

    for row in input_map:
        for elem in row:
            if min_value > elem:
                min_value = elem
            if max_value < elem:
                max_value = elem

    return min_value, max_value
