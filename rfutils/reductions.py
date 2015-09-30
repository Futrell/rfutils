from __future__ import division

def count(xs):
    i = (0,)
    for i in enumerate(xs, 1):
        pass
    return i[0]

def mean(xs):
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
    n = 0
    for w, x in wxs:
        total += w * x
        n += w
    try:
        return total/n
    except ZeroDivisionError:
        raise ValueError("Empty iterable passed to weighted_mean")

def product(xs):
    result = 1
    for x in xs:
        result *= x
    return result

def reduce_by_key(op, kvs, init):
    """ reduce by key """
    d = {}
    for k, v in kvs:
        if k not in d:
            d[k] = init
        d[k] = op(d[k], v)
    return d

def mreduce_by_key(op, kvs, init_thunk):
    """ mutably reduce by key

    op: A 2-argument function on acc, x which mutates the accumulator acc. E.g.,
        appending x to a list acc.
    kvs: An iterable of (key, value) pairs.
    init_thunk: a 0-argument function providing an initial value for acc.
    
    """
    d = {}
    for k, v in kvs:
        if k not in d:
            d[k] = init_thunk()
        op(d[k], v)
    return d

