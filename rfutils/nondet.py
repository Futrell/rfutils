import functools
import itertools

def nondet_reduce(nf, xs, initial=None):
    """ nondeterministic reduce

    Given a nondeterministic function nf, which returns an iterator over
    its possible return values, and a list of values xs, yield all the
    possible reductions of xs by nf.

    Example:
       >>> def add_or_sub(x, y): yield x+y; yield x-y
       >>> list(nondet_reduce(add_or_sub, [1, 2, 3]))
       [6, 0, 2, -4]
    
    These are the computations:
    1+2+3 = 6
    1+2-3 = 0
    1-2+3 = 2
    1-2-3 = 4

    """
    def do_it(acc, xs):
        if not xs:
            yield acc
        else:
            x = xs[0]
            xs = xs[1:]
            for new_acc in nf(acc, x):
                for res in do_it(new_acc, xs):
                    yield res
    xs = tuple(xs)
    if initial is None:
        return do_it(xs[0], xs[1:])
    else:
        return do_it(initial, xs)

def nondet_map(nf, *xss):
    """ nondeterministic map

    Given a nondeterministic function nf, which returns an iterator over
    its possible return values, and lists of values xs, yield all the 
    possible values from mapping nf over the xs.

    Example:
        >>> def add_or_sub(x, y): yield x+y; yield x-y
        >>> list(nondet_map(add_or_sub, [1, 2], [3, 4]))
        [(4, 6), (4, -2), (-2, 6), (-2, -2)]

    These are the computations: 1+3=4, 1-3=2, 2+4=6, 2-4=-2

    """
    return itertools.product(*map(nf, *xss))

def nondet_filter(nf, xs):
    for mask in nondet_map(nf, xs):
        yield itertools.compress(xs, mask)

def deterministic(f):
    """ determniistic 

    Lift a deterministic function f so it can be used as a nondeterministic 
    function.

    """
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        yield f(*args, **kwds)
    return wrapper

if __name__ == '__main__':
    import doctest
    doctest.testmod()
