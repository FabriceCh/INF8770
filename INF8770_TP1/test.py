from strgen import StringGenerator
from Huffman import huffman
from LZW import lzw
import time

def test():
    size = 5000
    string_to_encode = StringGenerator("[A-Z]{"+str(size)+"}").render()
    start_huf = time.time()
    encoded_Huffman = huffman(string_to_encode)
    end_huf = time.time()
    start_lzw = time.time()
    encoded_LZW = lzw(string_to_encode)
    end_lzw = time.time()

    time_huf = end_huf - start_huf
    time_lzw = end_lzw - start_lzw

    print("string to encode: " + string_to_encode)
    print(
        "encoded using huffman (used "
        + str(len(encoded_Huffman))
        + " bits) (time: "
        + str(time_huf)[0:7]
        + " seconds): "
        + encoded_Huffman
    )
    print(
        "encoded using lzw: (used "
        + str(len(encoded_LZW))
        + " bits) (time: "
        + str(time_lzw)[0:7]
        + " seconds): "
        + encoded_LZW
    )

test()