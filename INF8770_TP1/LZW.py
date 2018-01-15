import math


def lzw(filename):

    message = ""
    with open(filename) as f:
        message = f.read().strip()
    #dictionnaire contenant les symboles et leur representation
    dict = {}
    distinctSymbols = list(set(message))
    bitsNeeded = findNumberOfBits(len(distinctSymbols))
    #Remplissage du dictionnaire de depart
    for idx, symbol in enumerate(distinctSymbols):
        dict[symbol] = format(idx, '0'+str(bitsNeeded)+'b')
    print(dict)

    i=0
    substr = ""
    encoded_message = ""
    encodage = ""
    while i < len(message):
        substr += message[i]
        subcode = dict.get(substr)
        if subcode is None:
            encoded_message += encodage
            size = len(dict)
            dict[substr] = format(size, '0'+str(findNumberOfBits(size+1))+'b')
            for key in dict.keys():
                dict[key] = format(int(dict[key],2), '0'+str(findNumberOfBits(len(dict)))+'b')
            substr = ""
            i -= 1
        else:
            encodage = subcode
            if i == len(message)-1:
                encoded_message += encodage

        i += 1

    print(dict)

    return encoded_message

#Fonction calculant le nombre de bits neessaire pour le dictionnaire de depart
def findNumberOfBits(nSymbols):

    return math.ceil(math.log2(nSymbols))


print(findNumberOfBits(5))
print(lzw("input.txt"))
