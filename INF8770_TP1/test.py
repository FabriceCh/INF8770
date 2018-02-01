from strgen import StringGenerator
from Huffman import huffman
from LZW import lzw
import time

def test_random_string(string_size, gen_template):
    print("Exécution de tests pour la string " + str(string_size) + " " + str(gen_template))
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
    #plus size in dict
    for key, value in encoded_Huffman[1].items():
        len_huf += 8 + len(value)

    len_lzw = len(encoded_LZW[0])
    #plus size in dict
    for key, value in encoded_LZW[1].items():
        len_lzw += 8 + len(value)


    #log full verbose
    file = open("Full_verbose_results_from_random_string_generation.log", "a")

    file.writelines("------------------------------------" + "\n")
    file.writelines("TEST RANDOM STRING " + "\n")
    file.writelines("string size: " + str(string_size) + ", template: " + gen_template + "\n" + "\n")

    file.writelines("string to encode      (size: "+str(8*string_size)+" bits): " + string_to_encode + "\n")
    file.writelines(
        "encoded using huffman (size: "
        + str(len_huf)
        + " bits) (time: "
        + str(time_huf)[0:7]
        + " seconds): "
        + encoded_Huffman[0]
        + "\n"
    )
    file.writelines(
        "encoded using lzw     (size: "
        + str(len_lzw)
        + " bits) (time: "
        + str(time_lzw)#[0:7]
        + " seconds): "
        + encoded_LZW[0]
        + "\n"
    )
    file.writelines("------------------------------------" + "\n")
    file.close()

    #log general stats
    file = open("Stats_from_random_string_generation.log", "a")

    file.writelines("------------------------------------" + "\n")
    file.writelines("total number of symbols: " + str(string_size) + ", symbol types: " + gen_template + "\n" + "\n")

    file.writelines("initial string size: " + str(8 * string_size) + " bits" + "\n")
    file.writelines(
        "encoded using huffman size: "
        + str(len_huf)
        + " bits time: "
        + str(time_huf)[0:7]
        + " seconds "
        + "taux de compression: " + str(1-(len_huf / (8 * string_size)))[0:7]
        + "\n"
    )
    file.writelines(
        "encoded using lzw     size: "
        + str(len_lzw)
        + " bits time: "
        + str(time_lzw)  # [0:7]
        + " seconds "
        + "taux de compression: " + str(1-(len_lzw / (8 * string_size)))[0:7]
        + "\n"
    )
    file.writelines("------------------------------------" + "\n")
    file.close()

#clear log files
file = open("Stats_from_random_string_generation.log", "w")
file.close()
file = open("Full_verbose_results_from_random_string_generation.log", "a")
file.close()

#tests

#1 symbol, string size varies from 100 to 10000
for i in range(2, 5):
    test_random_string(10 ** i, "[A-A]")

#2 symbols, string size varies from 100 to 10000
for i in range(2, 5):
    test_random_string(10 ** i, "[A-B]")

#3 symbols, string size varies from 100 to 10000
for i in range(2, 5):
    test_random_string(10 ** i, "[A-C]")

#5 symbols, string size varies from 100 to 10000
for i in range(2, 5):
    test_random_string(10 ** i, "[A-E]")

#10 symbols, string size varies from 100 to 10000
for i in range(2, 5):
    test_random_string(10 ** i, "[A-J]")

#26 symbols, string size varies from 100 to 10000
for i in range(2, 5):
    test_random_string(10 ** i, "[A-Z]")

#62 symbols, string size varies from 100 to 10000
for i in range(2, 7):
    test_random_string(10 ** i, "[A-Aa-z0-9]")

print("Résultats ajoutés dans les fichiers ")


