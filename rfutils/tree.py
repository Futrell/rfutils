from collections import namedtuple

class TreeNode(object):
    __slots__ = ["value", "children"]

    def __init__(self):
        self.value = None
        self.children = {}

    def __repr__(self):
        return "TreeNode(%s, %s)" % (str(self.value), str(self.children))


class Tree(object):
    """ Tree

    Simple, efficient unordered tree data structure.

    """
    def __init__(self, value=None, children=None):
        self.root = TreeNode()
        if value is not None:
            self.root.value = value
        if children is not None:
            self.root.children = children

    def insert(self, keys, value=None):
        curr = self.root
        for key in keys:
            if key not in curr.children:
                curr.children[key] = TreeNode()
            curr = curr.children[key]
        curr.value = value

    def extract(self, keys):
        curr = self.root
        for key in keys:
            curr = curr.children[key]
        return curr.value

    def extract_node(self, keys):
        curr = self.root
        for key in keys:
            curr = curr.children[key]
        return curr

    def pop(self, keys):
        curr = self.root
        for key in keys:
            curr = curr.children[keys]
        curr.value = None # need to actually delete the node sometimes...
        return curr.value

    def __contains__(self, keys):
        curr = self.root
        for key in keys:
            if key in curr.children:
                curr = curr.children[key]
            else:
                return False
        return curr.value is not None

    def __repr__(self):
        return str(self.root)


class Trie(Tree):

    def observe(self, keys):
        self.insert(keys, True)

    def unobserve(self, keys):
        self.pop(keys)

    def is_prefix(self, keys):
        curr = self.root
        for key in keys:
            if key in curr.children:
                curr = curr.children[key]
            else:
                return False
        return True


class PrefixCountTree(Tree):
    def __init__(self):
        self.root = TreeNode()
        self.root.value = 0
    
    def observe(self, keys):
        curr = self.root
        for key in keys:
            if key not in curr.children:
                curr.children[key] = TreeNode()
                curr.children[key].value = 0
            curr.value += 1
            curr = curr.children[key]
        curr.value += 1
        
    def unobserve(self, keys):
        curr = self.root
        for key in keys:
            curr.value -= 1
            curr = curr.children[key]
