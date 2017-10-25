""" reductions

Functions which reduce an iterable in some way.

"""
from __future__ import division
import itertools 
import functools

_SENTINEL = object()

def nth(xs, n):
    return next(itertools.islice(xs, n, None))

def the_only(xs):
    first_time = True
    x = _SENTINEL
    for x in xs:
        if first_time:
            first_time = False
        else:
            raise ValueError("Iterable passed to the_only had second value %s" % x)
    if x is _SENTINEL:
        raise ValueError("Empty iterable passed to the_only")
    else:
        return x

def first(xs):
    """ Return the first element of an iterable. """
    for x in xs:
        return x
    else:
        raise ValueError("Empty iterable passed to first.")

def last(xs):
    """ Return the last element of an iterable. """
    try:
        return deque(xs, 1)[0]
    except IndexError:
        raise ValueError("Empty iterable passed to last.")

def count(xs):
    """ Count elements in an iterable without loading it into memory. """
    i = (0,)
    for i in enumerate(xs, 1):
        pass
    return i[0]

def mean(xs):
    """ Mean of elements in an iterable. """
    total = 0
    n = 0
    for x in xs:
        total += x
        n += 1
    try:
        return total/n
    except ZeroDivisionError:
        raise ValueError("Empty iterable passed to mean")

def weighted_mean(wxs):
    total = 0
    Z = 0
    for w, x in wxs:
        total += w * x
        Z += w
    try:
        return total/Z
    except ZeroDivisionError:
        raise ValueError("Empty iterable passed to weighted_mean")

def product(xs):
    """ Product of elements in an iterable of numbers. 

    Examples:
    >>> xs = [1, 2, 3]
    >>> product(x**2 for x in xs)
    36
    >>> product([])
    1
    
    """
    # Weirdly, this is faster than functools.reduce(operator.mul, xs, 1)
    result = 1
    for x in xs:
        result *= x
    return result

def reduce_by_key(op, kvs, init):
    """ reduce by key 

    Example:
    >>> reduce_by_key(lambda a,x: a+x, [(1, "ab"), (2, "cd"), (1, "ef")], "")
    {1: 'abef', 2: 'cd'}

    """
    d = {}
    for k, v in kvs:
        if k not in d:
            d[k] = init
        d[k] = op(d[k], v)
    return d

def mreduce(op, xs, init_thunk):
    acc = init_thunk()
    for x in xs:
        op(acc, xs)
    return acc

def mreduce_by_key(op, kvs, init_thunk):
    """ mutably reduce by key

    op: A 2-argument function on acc, x which mutates the accumulator acc. E.g.,
        appending x to a list acc.
    kvs: An iterable of (key, value) pairs.
    init_thunk: a 0-argument function providing an initial value for acc.

    Example:
    >>> mreduce_by_key(list.append, [(1, "a"), (2, "b"), (1, "c")], list)
    {1: ['a', 'c'], 2: ['b']}
    
    """
    d = {}
    for k, v in kvs:
        if k not in d:
            d[k] = init_thunk()
        op(d[k], v)
    return d

def lists_by_key(xs):
    return mreduce_by_key(list.append, xs, list)

def sets_by_key(xs):
    return mreduce_by_key(set.add, xs, set)

foldl = functools.reduce

if __name__ == '__main__':
    import doctest
    doctest.testmod()
