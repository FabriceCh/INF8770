class Node(object):
    left = None
    right = None
    item = None
    weight = 0

    def __init__(self, i, w):
        self.item = i
        self.weight = w

    def setChildren(self, ln, rn):
        self.left = ln
        self.right = rn

    def __eq__(self, other):
        return (self.weight == other.weight)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self.weight < other.weight)

    def __repr__(self):
        return "%s - %s — %s _ %s" % (self.item, self.weight, self.left, self.right)
