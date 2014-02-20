""" flatten

Useful functions for dealing with nested iterable
data structures.

"""
def deepmap(fn, iterable):
    """ deep map

    Apply a function to all elements of a nested
    data structure (list of lists or tuple of tuples).

    """
    itertype = type(iterable)

    def apply_or_recurse(item, fn=fn, isinstance=isinstance, map=map):
        if isinstance(item, itertype):
            return map(apply_or_recurse, item)
        return fn(item)

    return map(apply_or_recurse, iterable)

def deepiter(iterable, itertype=None):
    """ deep iter

    Yield elements of a recursive data structure
    (list of lists, tuple of tuples, generator of generators, etc.).

    """
    def _deepiter(iterable, itertype):
        for item in iterable:
            if isinstance(item, itertype):
                for item2 in deepiter(item, itertype):
                    yield item2
            else:
                yield item

    if itertype is None:
        itertype = type(iterable)

    return _deepiter(iterable, itertype)

def flatten(iterable, itertype=None):
    """ Return a flattened list. """
    if itertype is None:
        itertype = type(iterable)
    lst = []
    for item in iterable:
        if isinstance(item, itertype):
            lst.extend(flatten(item, itertype=itertype))
        else:
            lst.append(item)
    return lst
