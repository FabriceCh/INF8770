import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np


def main(argv):
    filename = argv.strip()
    img = mpimg.imread(filename)
    if filename.split(".")[1] == "png" or "PNG":
        img = np.uint8(255*img)
    img = img[:, :, 0:3]
    print(img.shape)
    y, cbcr = convert_to_YCbCr(img)
    print(y.shape)
    print(cbcr.shape)
    yblocks = convert_to_blocks(y)
    print(yblocks.shape)
    print(y.shape)
    plt.imshow(y)
    plt.show()
    #plt.imshow()
   # plt.show()


def convert_to_YCbCr(img):
    y = img[:, :, 0:1]
    cbcr = np.empty(shape=(img.shape[0] // 2, img.shape[1] // 2, 2))
    for i, line in enumerate(img):
        for j, pixel in enumerate(line):
            R = pixel[0]
            G = pixel[1]
            B = pixel[2]
            Y = 0.299*R+0.587*G+0.114*B
            y[i][j] = Y
            if i%2 == 0 and j%2 == 0:
                Cb = 128 + 0.564 * (B - Y)
                Cr = 128 + 0.713 * (R - Y)
                cbcr[i//2][j//2] = [Cb, Cr]
    return y, cbcr

"""
def convert_to_420_from_444(img):
    y = img[:, :, 0]
    cbcr = np.empty(shape=(img.shape[0]//2, img.shape[1]//2, 2))
    for i in range(0, img.shape[0], 2):
        for j in range(0, img.shape[1], 2):
            cbcr[i//2, j//2] = img[i, j, 1:2]
    return y, cbcr
"""

# Source : https://stackoverflow.com/questions/42297115/numpy-split-cube-into-cubes/42298440#42298440
def convert_to_blocks(img):
    oldshape = img.shape
    newshape = (8, 8, oldshape[2])
    repeats = (oldshape[0]//8, oldshape[0]//8, 1)
    tmpshape = np.column_stack([repeats, newshape]).ravel()
    order = np.arange(len(tmpshape))
    order = np.concatenate([order[::2], order[1::2]])
    return img.reshape(tmpshape).transpose(order).reshape(-1, *newshape)


if __name__ == "__main__":
    main(sys.argv[1])
