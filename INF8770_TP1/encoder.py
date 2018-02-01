import sys
from Huffman import huffman
from LZW import lzw
import imageio
import time

def main(argv):
    filename = argv.strip()
    contents = []
    try:
        contents = imageio.imread(filename).flatten().tolist()
    except ValueError:
        print("File read as a text file.")
        with open(filename) as f:
            contents = list(f.read().strip())

    choix = ""

    while choix.upper() != "O" and choix.upper() != "N":
        choix = input("Voulez-vous encoder le fichier par triplets RGB (24 bits)? [O/N]")

    data = []
    entry_size = 8
    if choix.upper() == "O":
        entry_size = 24
        for i in range(0, int(len(contents)/3)):
            data.append(int(contents[i] << 16) + int(contents[i+1] << 8) + int(contents[i+2]))
    else:
        data = contents

    with open("huffman.txt", 'w') as f:
        print("Calcul de Huffman...")

        start_huf = time.time()
        res = huffman(data)
        end_huf = time.time()
        time_huf = end_huf - start_huf
        print("Calcul de Huffman complété. Temps pris: " + str(time_huf) + " s")
        print("Écriture du résultat de Huffman dans le fichier huffman.txt...")
        f.write("Huffman:\n" + res[0] + "\n")
        f.write("Dictionnaire:\n" + str(res[1]) + "\n")
        l = len(res[0])
        print("Longueur de l'encodage (sans le dictionnaire) : " + str(l) + " bits ("+ str(int(l/8)) + " octets).")
        for key, value in res[1].items():
            l += entry_size + len(value)
        print("Longueur de l'encodage (comprenant le dictionnaire) : " + str(l) + " bits ("+ str(int(l/8)) + " octets).")

    with open("lzw.txt", 'w') as f:
        print("Calcul de LZW...")
        start_lzw = time.time()
        res = lzw(data)
        end_lzw = time.time()
        time_lzw = end_lzw - start_lzw
        print("Calcul de LZW complété. Temps pris: " + str(time_lzw) + " s")
        print("Écriture du résultat de LZW dans le fichier lzw.txt...")
        f.write("LZW:\n" + res[0] + "\n")
        f.write("Dictionnaire initial:\n" + str(res[1]) + "\n")
        l = len(res[0])
        print("Longueur de l'encodage (sans le dict initial) : " + str(l) + " bits ("+ str(int(l/8)) + " octets).")
        for key, value in res[1].items():
            l += entry_size + len(value)
        print("Longueur de l'encodage (comprenant le dict initial) : " + str(l) + " bits ("+ str(int(l/8)) + " octets).")

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        print("Entrez un fichier comme argument pour le script.\nUsage: encoder.py fichier.abc")
