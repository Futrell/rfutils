""" flatten

Useful functions for dealing with nested iterable
data structures.

"""
def deepmap(fn, iterable):
    """ deep map

    Apply a function to all elements of a nested iterable
    data structure.

    """
    itertype = type(iterable)

    def apply_or_recurse(item):
        if hasattr(item, '__iter__'):
            return map(apply_or_recurse, item)
        return fn(item)

    return map(apply_or_recurse, iterable)

def deepiter(iterable):
    """ deep iter

    Yield elements of a recursively nested iterables.

    """
    for item in iterable:
        if hasattr(item, '__iter__'):
            for item2 in deepiter(item):
                yield item2
        else:
            yield item

def flatten(iterable, itertype=None):
    """ Return a flattened list.

    Optional keyword itertype determines what types to recurse into;
    if it is unspecified, recurse into the type of the original iterable.

    """
    if itertype is None:
        itertype = type(iterable)
    lst = []
    for item in iterable:
        if isinstance(item, itertype):
            lst.extend(flatten(item, itertype=itertype))
        else:
            lst.append(item)
    return lst

