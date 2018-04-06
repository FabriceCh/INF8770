#Inspired from https://www.techrepublic.com/article/huffman-coding-in-python/
from itertools import groupby
from Node import Node
from heapq import *

def huffman(data):

    items = [Node(str(symb), len(list(group))) for symb, group in groupby(sorted(list(data)))]
    heapify(items)
    while len(items) > 1:
        left = heappop(items)
        right = heappop(items)
        n = Node(None, left.weight+right.weight)
        n.setChildren(left, right)
        heappush(items, n)

    codes = {}

    def encode(code, node):
        if node.item:
            if not code:
                codes[node.item] = "0"
            else:
                codes[node.item] = code
        else:
            encode(code+"0", node.left)
            encode(code+"1", node.right)

    encode("", items[0])

    encoded_message = []
    for symbol in data:
        encoded_message.append(codes[str(symbol)])

    return (encoded_message, codes)

