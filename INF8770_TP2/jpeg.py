import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np


def main(argv):
    filename = argv.strip()
    img = mpimg.imread(filename)
    if filename.split(".")[1] == "png" or "PNG":
        img = np.uint8(255*img)
    print(img)
    imgplot = plt.imshow(img)
    ycbcr = convert_to_YCbCr(img)
    plt.show()

def convert_to_YCbCr(img):
    res = img.copy()
    for line in res:
        for pixel in line:
            R = pixel[0]
            G = pixel[1]
            B = pixel[2]
            Y = 0.299*R+0.587*G+0.114*B
            Cb = 128 + 0.564*(B-Y)
            Cr = 128 + 0.713*(R-Y)
            pixel[0] = Y
            pixel[1] = Cb
            pixel[2] = Cr
    return res

if __name__ == "__main__":
    main(sys.argv[1])
