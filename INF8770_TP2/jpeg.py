import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt
from Huffman import huffman


# https://www.hdm-stuttgart.de/~maucher/Python/MMCodecs/html/jpegUpToQuant.html

def rle_size(tuples):
    size = 0
    for t in tuples:
        size += 8 + t[1] # 8 bits pour le nombre de zéros (4 bits) et la longueur du code Huffman (4 bits)
        # plus le code Huffman lui-même
    return size

def huffman_size(table):
    size = 0
    for key, value in table.items():
        size += 32 + len(value) # 32 bits pour l'entier représenté, plus sa longueur en code Huffman
    return size

def rle(arr, ac_table):
    symbols = []
    try:
        zero_encoding = ac_table['0']
    except KeyError:
        zero_encoding = '0'
    last_nonzero = -1
    for idx, elm in enumerate(arr):
        if elm != zero_encoding:
            last_nonzero = idx

    consecutive_zeroes = 0
    for idx, elm in enumerate(arr):
        if idx > last_nonzero:
            symbols.append((0, 0, zero_encoding))
            break
        elif elm == zero_encoding and consecutive_zeroes < 15:
            consecutive_zeroes += 1
        else:
            symbols.append((consecutive_zeroes, len(elm), elm))
            consecutive_zeroes = 0
    return symbols

def main(argv):
    np.set_printoptions(edgeitems=10, linewidth=200)
    B = 8
    filename = argv.strip()
    img1 = cv2.imread(filename, cv2.IMREAD_COLOR)
    h, w = np.array(img1.shape[:2]) // B * B

    orig_s = h*w*24
    print("Taille originale de l'image :", str(orig_s), "bits.")

    # Convert BGR to RGB
    img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    # plt.imshow(img2)
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
    factorIndicatorStr = "20"
    QF = 20
    if 50 > QF > 1:
        scale = np.floor(5000 / QF)
    elif QF < 100:
        scale = 200 - 2 * QF
    else:
        print("Quality Factor must be in the range [1..99]")
        exit(1)
    scale = scale / 100.0
    Q = [QY * scale, QC * scale, QC * scale]

    zigzag_indexes = [0, 1, 5, 6, 14, 15, 27, 28,
                      2, 4, 7, 13, 16, 26, 29, 42,
                      3, 8, 12, 17, 25, 30, 41, 43,
                      9, 11, 18, 24, 31, 40, 44, 53,
                      10, 19, 23, 32, 39, 45, 52, 54,
                      20, 22, 33, 38, 46, 51, 55, 60,
                      21, 34, 37, 47, 50, 56, 59, 61,
                      35, 36, 48, 49, 57, 58, 62, 63]

    all_channels_dc = []
    all_channels_rle = []
    all_channels_tables = []
    for idx, channel in enumerate(imSub):
        channel_dc = []
        channel_rle = []
        channel_tables = []
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
                to_zig = np.round(currentblock / Q[idx]).flatten()
                zigged = np.zeros(64, np.int32)
                for i, zig in enumerate(zigzag_indexes):
                    zigged[zig] = to_zig[i]
                ac, ac_table = huffman(zigged[1:])
                channel_dc.append(zigged[0])
                channel_rle.append(rle(ac, ac_table))
                channel_tables.append(ac_table)
        all_channels_dc.append(channel_dc)
        all_channels_rle.append(channel_rle)
        all_channels_tables.append(channel_tables)

    dc_s = 0
    for channel in all_channels_dc:
        dc_s += len(channel)*32 # Nombres de blocs par canal * 32 bits par valeur DC
    print("Taille des valeurs DC :", str(dc_s), "bits.")

    rle_s = 0
    for channel in all_channels_rle:
        for block in channel:
            rle_s += rle_size(block)
    print("Taille des blocs RLE :", str(rle_s), "bits.")

    huff_s = 0
    for channel in all_channels_tables:
        for block in channel:
            huff_s += huffman_size(block)
    print("Taille des tables Huffman :", str(huff_s), "bits.")

    total_s = dc_s + rle_s
    print("Taille totale de l'image JPEG sans tables :", str(total_s), "bits.")
    print("Taille totale de l'image JPEG avec tables :", str(total_s+huff_s), "bits.")
    print("Taux de compression sans tables :", str((1 - total_s / orig_s) * 100), "%.")
    print("Taux de compression avec tables :", str((1 - (total_s+huff_s) / orig_s)*100), "%.")

    channel_shapes = [(h, w), (h//SSV, w//SSH), (h//SSV, w//SSH)]
    DecAll = np.zeros((h, w, 3), np.uint8)
    all_blocks = []
    for i, channel in enumerate(all_channels_dc):
        blocks = np.zeros(channel_shapes[i], np.int32)
        for j, dc in enumerate(channel):
            block = [dc]
            for k, elm in enumerate((all_channels_rle[i])[j]):
                if elm[0] == 0 and elm[1] == 0:
                    zero_burst = [0] * (64 - len(block))
                    block.extend(zero_burst)
                    break
                else:
                    zero_burst = [0] * elm[0]
                    block.extend(zero_burst)
                    for key, value in ((all_channels_tables[i])[j]).items():
                        if value == elm[2]:
                            block.append(int(key))
                            break
            real_block = np.zeros(64, np.int32)
            for z in range(64):
                real_block[z] = block[zigzag_indexes[z]]
            real_block = real_block.reshape(8, 8)
            row = j // (channel_shapes[i][1] // 8)
            col = j % (channel_shapes[i][1] // 8)
            blocks[row * 8:(row + 1) * 8, col * 8:(col + 1) * 8] = real_block
        all_blocks.append(blocks)

    for idx, channel in enumerate(all_blocks):
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
    #plt.imshow(reImg)
    #plt.show()
    reImg = cv2.cvtColor(reImg, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename + factorIndicatorStr + ".png", reImg);



if __name__ == "__main__":
    main(sys.argv[1])
