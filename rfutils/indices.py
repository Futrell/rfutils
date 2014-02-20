class Indices(dict):
    """ A dictionary of indices. """

    def __init__(self, starting_index=0):
        self.count = starting_index
        self.keylist = [None] * starting_index

    def __missing__(self, key):
        count = self.count
        self[key] = count
        self.keylist.append(key)
        self.count += 1
        return count

    def add(self, item):
        self[item] = self.count
        self.keylist.append(item)
        self.count += 1

    def update(self, items):
        new_items = set(items).difference(self.iterkeys())
        super(Indices, self).update({k:self.count+i for i,k in enumerate(new_items)})
        self.count += len(new_items)
        self.keylist.extend(new_items)
