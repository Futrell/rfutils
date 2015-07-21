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
        
def uniquely_indexed(xs):
    xs = list(xs)
    c = Counter(xs)
    d = {x : it.permutations(range(n)) for x, n in c.items()}
    perms = map(dict, it.product(*[[(x,p) for p in perm]
                                   for x, perm in d.iteritems()]))
    for perm in perms:
        def gen():
            c_so_far = Counter()
            for x in xs:
                yield x, perm[x][c_so_far[x]]
                c_so_far[x] += 1
        yield list(gen())

