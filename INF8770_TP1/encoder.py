import sys
from Huffman import huffman
from LZW import lzw
import imageio

def main(argv):
    filename = argv.strip()
    #extension = filename.split(".")[1]
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
    if choix.upper() == "O":
        for i in range(0, int(len(contents)/3)):
            data.append(int(contents[i] << 16) + int(contents[i+1] << 8) + int(contents[i+2]))
    else:
        data = contents

    with open("huffman.txt", 'w') as f:
        print("Calcul de Huffman...")
        res = huffman(data)
        print("Écriture du résultat de Huffman dans le fichier huffman.txt...")
        f.write("Huffman:\n" + res + "\n")
        l = len(res)
        print("Longueur de l'encodage : " + str(l) + " bits ("+ str(int(l/8)) + " octets).")

    with open("lzw.txt", 'w') as f:
        print("Calcul de LZW...")
        res = lzw(data)
        print("Écriture du résultat de LZW dans le fichier lzw.txt...")
        f.write("LZW:\n" + res + "\n")
        l = len(res)
        print("Longueur de l'encodage : " + str(l) + " bits ("+ str(int(l/8)) + " octets).")
    

if __name__ == "__main__":
    main(sys.argv[1])

