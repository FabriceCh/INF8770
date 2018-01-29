from strgen import StringGenerator
from Huffman import huffman
from LZW import lzw
import time

def test_random_string(string_size, gen_template):
    print(gen_template)
    string_to_encode = StringGenerator(gen_template+"{"+str(string_size)+"}").render()
    start_huf = time.time()
    encoded_Huffman = huffman(string_to_encode)
    end_huf = time.time()
    start_lzw = time.time()
    encoded_LZW = lzw(string_to_encode)
    end_lzw = time.time()

    time_huf = end_huf - start_huf
    time_lzw = end_lzw - start_lzw

    len_huf = len(encoded_Huffman[0])
    for key, value in encoded_Huffman[1].items():
        len_huf += 8 + len(value)

    len_lzw = len(encoded_LZW[0])
    for key, value in encoded_LZW[1].items():
        len_lzw += 8 + len(value)

    print("------------------------------------")
    print("TEST RANDOM STRING ")
    print("string size: " + str(string_size) + ", template: " + gen_template + "\n")

    print("string to encode      (size: "+str(8*string_size)+" bits): " + string_to_encode)
    print(
        "encoded using huffman (size: "
        + str(len_huf)
        + " bits) (time: "
        + str(time_huf)[0:7]
        + " seconds): "
        + encoded_Huffman[0]
    )
    print(
        "encoded using lzw     (size: "
        + str(len_lzw)
        + " bits) (time: "
        + str(time_lzw)#[0:7]
        + " seconds): "
        + encoded_LZW[0]
    )
    print("------------------------------------")

test_random_string(10000, "[A-B]")