import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm


# https://www.hdm-stuttgart.de/~maucher/Python/MMCodecs/html/jpegUpToQuant.html

def main(argv):
    B = 8
    filename = argv.strip()
    img1 = cv2.imread(filename, cv2.IMREAD_COLOR)
    h, w = np.array(img1.shape[:2]) // B * B

    # Convert BGR to RGB
    img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    plt.imshow(img2)

    # Format 4:2:0 (SSV = 2, SSH = 2)
    transcol = cv2.cvtColor(img2, cv2.COLOR_RGB2YCrCb)
    SSV = 2
    SSH = 2
    crf = transcol[:, :, 1]
    cbf = transcol[:, :, 2]
    crsub = crf[::SSV, ::SSH]
    cbsub = cbf[::SSV, ::SSH]
    imSub = [transcol[:, :, 0], crsub, cbsub]

    # Matrices standard JPEG
    QY = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                   [12, 12, 14, 19, 26, 48, 60, 55],
                   [14, 13, 16, 24, 40, 57, 69, 56],
                   [14, 17, 22, 29, 51, 87, 80, 62],
                   [18, 22, 37, 56, 68, 109, 103, 77],
                   [24, 35, 55, 64, 81, 104, 113, 92],
                   [49, 64, 78, 87, 103, 121, 120, 101],
                   [72, 92, 95, 98, 112, 100, 103, 99]])

    QC = np.array([[17, 18, 24, 47, 99, 99, 99, 99],
                   [18, 21, 26, 66, 99, 99, 99, 99],
                   [24, 26, 56, 99, 99, 99, 99, 99],
                   [47, 66, 99, 99, 99, 99, 99, 99],
                   [99, 99, 99, 99, 99, 99, 99, 99],
                   [99, 99, 99, 99, 99, 99, 99, 99],
                   [99, 99, 99, 99, 99, 99, 99, 99],
                   [99, 99, 99, 99, 99, 99, 99, 99]])

    QF = 2
    if QF < 50 and QF > 1:
        scale = np.floor(5000 / QF)
    elif QF < 100:
        scale = 200 - 2 * QF
    else:
        print("Quality Factor must be in the range [1..99]")
        exit(1)
    scale = scale / 100.0
    Q = [QY * scale, QC * scale, QC * scale]
    TransAllQuant = []
    for idx, channel in enumerate(imSub):
        channelrows = channel.shape[0]
        channelcols = channel.shape[1]
        TransQuant = np.zeros((channelrows, channelcols), np.float32)
        blocksV = channelrows // B
        blocksH = channelcols // B
        vis0 = np.zeros((channelrows, channelcols), np.float32)
        vis0[:channelrows, :channelcols] = channel
        vis0 = vis0 - 128
        for row in range(blocksV):
            for col in range(blocksH):
                currentblock = cv2.dct(vis0[row * B:(row + 1) * B, col * B:(col + 1) * B])
                TransQuant[row * B:(row + 1) * B, col * B:(col + 1) * B] = np.round(currentblock / Q[idx])
        TransAllQuant.append(TransQuant)

    plt.show()

    DecAll = np.zeros((h, w, 3), np.uint8)
    for idx, channel in enumerate(TransAllQuant):
        channelrows = channel.shape[0]
        channelcols = channel.shape[1]
        blocksV = channelrows // B
        blocksH = channelcols // B
        back0 = np.zeros((channelrows, channelcols), np.uint8)
        for row in range(blocksV):
            for col in range(blocksH):
                dequantblock = channel[row * B:(row + 1) * B, col * B:(col + 1) * B] * Q[idx]
                currentblock = np.round(cv2.idct(dequantblock)) + 128
                currentblock[currentblock > 255] = 255
                currentblock[currentblock < 0] = 0
                back0[row * B:(row + 1) * B, col * B:(col + 1) * B] = currentblock
        back1 = cv2.resize(back0, (w, h))
        DecAll[:, :, idx] = np.round(back1)

    reImg = cv2.cvtColor(DecAll, cv2.COLOR_YCrCb2RGB)
    plt.imshow(reImg)
    plt.show()

    # https://rosettacode.org/wiki/Zig-zag_matrix#Python
    zigzag_indexes = [0, 1, 5, 6, 14, 15, 27, 28,
                      2, 4, 7, 13, 16, 26, 29, 42,
                      3, 8, 12, 17, 25, 30, 41, 43,
                      9, 11, 18, 24, 31, 40, 44, 53,
                      10, 19, 23, 32, 39, 45, 52, 54,
                      20, 22, 33, 38, 46, 51, 55, 60,
                      21, 34, 37, 47, 50, 56, 59, 61,
                      35, 36, 48, 49, 57, 58, 62, 63]

if __name__ == "__main__":
    printzz(zigzag(8))
    #main(sys.argv[1])
