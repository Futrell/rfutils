""" my itertools

Useful functions on iterables, which return other iterables.
Where possible, the original iterable is not held in memory.
(The major exceptions are the combinatoric functions.)

"""
import itertools as it
from operator import add, itemgetter, __not__
from collections import deque
from functools import partial

try:
    map = it.imap
    filter = it.ifilter
    it.filterfalse = it.ifilterfalse
    zip = it.izip
    it.zip_longest = it.izip_longest
    range = xrange
except (NameError, AttributeError):
    pass

_SENTINEL = object()

consume = partial(deque, maxlen=0)
flat = it.chain.from_iterable

def blocks(iterable, size, fillvalue=None):
    """ Blocks

    Break the iterable into blocks of specified size.
    Differs from chunks() in that all blocks are of length size;
    when the given iterable runs out, the blocks are padded
    with fillvalue.

    Examples:
        >>> lst = ['foo', 'bar', 'baz', 'qux', 'zim']
        >>> list(blocks(lst, 2))
        [('foo', 'bar'), ('baz', 'qux'), ('zim', None)]

    """
    return it.zip_longest(*[iter(iterable)]*size, fillvalue=fillvalue)

def chunks(iterable, size):
    """ Chunks

    Break an iterable into chunks of specified size.
    Equivalent to map(list, ichunks(iterable, size)), but faster for
    small-sized chunks.

    Params:
        iterable: An iterable
        size: An integer size.

    Yields:
        Tuples of size (less than or equal to) n.

    Examples:
        >>> lst = ['foo', 'bar', 'baz', 'qux', 'zim', 'cat', 'dog']
        >>> list(chunks(lst, 3))
        [['foo', 'bar', 'baz'], ['qux', 'zim', 'cat'], ['dog']]

    """
    # Based on more-itertools by erikrose
    for group in (list(g) for g in it.zip_longest(*[iter(iterable)] * size,
                                                  fillvalue=_SENTINEL)):
        if group[-1] is _SENTINEL:
            # If this is the last group, shuck off the padding:
            del group[group.index(_SENTINEL):]
        yield group

def ichunks(iterable, size):
    """ Iterative Chunks

    Fully lazy version of chunks, returning iterator of iterators.
    For small size, this is slower than chunks. For large size, it's
    faster.

    This function is most appropriate for loops of the form:
        for chunk in ichunks(iterable, size):
            for item in chunk:
                ...

    Params:
        iterable: An iterable
        size: An integer size.

    Yields:
        Iterators length (less than or equal to) n.

    Examples:
        >>> lst = ['foo', 'bar', 'baz', 'qux', 'zim', 'cat', 'dog']
        >>> list(map(list, ichunks(lst, 3)))
        [['foo', 'bar', 'baz'], ['qux', 'zim', 'cat'], ['dog']]

    """
    xs = iter(iterable)
    while True:
        chunk = it.islice(xs, size)
        try:
            probe = next(chunk)
        except StopIteration: # need to do it this way in Python 3.5+
            raise StopIteration 
        yield it.chain([probe], chunk)
        consume(chunk)

def segments(iterable, breakpoints):
    """ Segments

    Break iterable into contiguous segments at specified index
    breakpoints. New iterators are formed starting with each breakpoint.

    Params:
        iterable: An iterable to be broken into segments.
        breakpoints: An iterable of integers representing indices
            for where to break the iterable.

    Yields:
        Iterators over items from iterable.

    Example:
        >>> lst = ['foo', 'bar', 'baz', 'qux', 'zim', 'cat', 'dog']
        >>> list(map(list, segments(lst, (3,4))))
        [['foo', 'bar', 'baz'], ['qux'], ['zim', 'cat', 'dog']]

    """
    xs = iter(iterable)
    previous_breakpoint = 0
    for breakpoint in breakpoints:
        subit = it.islice(xs, breakpoint - previous_breakpoint)
        yield subit
        consume(subit)
        previous_breakpoint = breakpoint
    yield xs

def segmentations(iterable):
    """ Segmentations

    Generate all possible ways to break an iterable into contiguous segments.

    Params:
        iterable: Any iterable; it will be consumed and held in memory.

    Yields:
        Tuples of tuples representing possible segmentations.

    Example:
    >>> xs = [1, 2, 3]
    >>> list(segmentations(xs))
    [((1, 2, 3),), ((1,), (2, 3)), ((1, 2), (3,)), ((1,), (2,), (3,))]

    """
    iterable = list(iterable)
    n = len(iterable)
    breakpoint_groups = (it.combinations(range(1, n), i) for i in range(n))
    for breakpoint_group in breakpoint_groups:
        for breakpoints in breakpoint_group:
            yield tuple(map(tuple, segments(iterable, breakpoints)))

def sliding(iterable, n):
    """ Sliding

    Yield adjacent elements from an iterable in a sliding window
    of size n.

    Parameters:
        iterable: Any iterable.
        n: Window size, an integer.

    Yields:
        Tuples of size n.

    Example:
        >>> lst = ['a', 'b', 'c', 'd', 'e']
        >>> list(sliding(lst, 2))
        [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e')]

    """
    its = it.tee(iterable, n)
    for i, iterator in enumerate(its):
        for _ in range(i):
            next(iterator)
    return zip(*its)

def one_thru_ngrams(iterable, n):
    """ 1-thru-N-grams

    Yield all m-grams from an iterable for m = 1:n inclusive.
    The order in which they come out is not guaranteed.

    Example:
        set(one_thru_ngrams("abc", 3))
        {('a', 'b', 'c'), ('a',), ('c',), ('a', 'b'), ('b',), ('b', 'c')}

    """
    if hasattr(iterable, '__next__') or hasattr(iterable, 'next'):
        iterators = it.tee(iterable, n)
        for i, iterator in enumerate(iterators):
            for _ in range(i):
                next(iterator)

        first_it = iterators[0]
        rest_its = iterators[1:]

        so_far = []
        so_far_append = so_far.append

        while True:
            del so_far[:]
            so_far_append(next(first_it))
            yield tuple(so_far)
            for iterator in rest_its:
                try:
                    so_far_append(next(iterator))
                    yield tuple(so_far)
                except StopIteration:
                    pass
    else:
        for x in flat(sliding(iterable, m) for m in range(n+1)):
            yield x

try:
    partition
except NameError:    
    def partition(pred, iterable):
        """ Partition
        
        Use a predicate to partition entries into true entries and false entries.
        
        Example:
        >>> def is_even(x): return x % 2 == 0
        >>> x, y = partition(is_even, range(10))
        >>> list(x)
        [0, 2, 4, 6, 8]
        >>> list(y)
        [1, 3, 5, 7, 9]
        
        """
        # Based on http://docs.python.org/3.4/library/itertools.html
        t1, t2 = it.tee(iterable)
        return filter(pred, t1), it.filterfalse(pred, t2)

try:
    accumulate
except NameError:
    def accumulate(iterable, fn=add):
        iterator = iter(iterable)
        total = next(iterator) 
        yield total
        for x in iterator:
            total = fn(total, x)
            yield total

def buildup(iterable):
    """ Build up

    Example:
    >>> list(buildup("abcd"))
    [('a',), ('a', 'b'), ('a', 'b', 'c'), ('a', 'b', 'c', 'd')]

    """
    so_far = []
    for x in iterable:
        so_far.append(x)
        yield tuple(so_far)

def unique(iterable, key=None):
    """ iterate over unique elements of iterable, preserving order 

    Example:
    >>> list(unique("aaabbbaaac"))
    ['a', 'b', 'c']

    """
    seen = set()
    seen_add = seen.add

    if key is None:
        for element in iterable:
            if element not in seen:
                seen_add(element)
                yield element
    else:
        for element in iterable:
            value = key(element)
            if value not in seen:
                seen_add(value)
                yield element

def itranspose(X):
    """ Given [[a, b, c], [d, e, f], [g, h, i]],
    yield [a, d, g], [b, e, h], [c, f, i],
    while only lazily evaluating the input interators """
    its = list(map(iter, X))
    N = len(X)
    while True:
        subit = list(map(next, its))
        if len(subit) < N:
            raise StopIteration
        else:
            yield subit

def uniq(iterable, key=None):
    """ uniq: Remove adjacent duplicates.

    Preserves order. Remember only the element just seen. Like Unix uniq.

    Examples:
        >>> list(uniq('AAAABBBCCDAABBB'))
        ['A', 'B', 'C', 'D', 'A', 'B']

        >>> list(uniq('ABBCcAD', key=str.lower))
        ['A', 'B', 'C', 'A', 'D']

    """
    if key is None: # fast path
        return (k for k, g in it.groupby(iterable))
    else:
        return map(next, map(itemgetter(1), it.groupby(iterable, key)))

def unsliding(iterable):
    """ unsliding

    Undo the sliding function: turn an iterable (a,b),(b,c),(c,d)... into
    a,b,c....

    Operates on any iterable of iterables.

    Examples:
        >>> foo = [('a', 'b', 'c'), ('b', 'c', 'd'), ('c', 'd', 'e')]
        >>> list(unsliding(foo))
        ['a', 'b', 'c', 'd', 'e']

        >>> bar = sliding(range(5), 3)
        >>> list(unsliding(bar))
        [0, 1, 2, 3, 4]

    """
    for group in iterable:
        group_it = iter(group)
        yield next(group_it) # the first item
    for item in group_it:
        yield item # and yield the rest of the last thing

def isplit(xs, sep, maxsplit=None):
    """ Iterative Split

    Like str.split but operates lazily on any iterable.

    Example:
        >>> foo = iter([0, 1, 2, 3, 'dog', 4, 5, 6, 7, 'dog', 8, 9])
        >>> [list(chunk) for chunk in isplit(foo, 'dog')]
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

    """
    xs_it = iter(xs)
    if maxsplit is None:
        while 1:
            subit = iter(partial(next, xs_it), sep)
            try:
                probe = next(subit)
            except StopIteration:
                raise StopIteration
            yield it.chain([probe], subit)
            consume(subit)
    else:
        count = 0
        while count < maxsplit:
            subit = iter(partial(next, xs_it), sep)
            try:
                probe = next(subit) 
            except StopIteration:
                raise StopIteration
            yield it.chain([probe], subit)
            consume(subit)
            count += 1

def partitions(xs):
    xs = list(xs)
    for mask in it.product(*[[True, False]] * len(xs)):
        left = tuple(it.compress(xs, mask))
        right = tuple(it.compress(xs, map(__not__, mask)))
        yield left, right

def items_in_context(xs):
    xs = tuple(xs)
    for i, x in enumerate(xs):
        yield xs[:i], x, xs[(i+1):]

def thing_and_rest(xs):
    xs = tuple(xs)
    for i, x in enumerate(xs):
        context = xs[:i] + xs[(i+1):]
        yield x, context

def cons(x, ys):
    return it.chain([x], ys)

def first_and_rest(xs):
    """ like car and cdr """
    xs_i = iter(xs)
    return next(xs_i), xs_i

def butfirst(xs):
    return first_and_rest(xs)[1]

def butlast(xs):
    def holder():
        hold = None
        for x in xs_i:
            yield hold
            hold = x
    return butfirst(holder())

def flatmap(f, *xss):
    return flat(map(f, *xss))

def starfilter(f, xss):
    for xs in xss:
        if f(*xs):
            yield xs

def zipmap(f, xs):
    one, two = it.tee(xs)
    return zip(one, map(f, two))

def take(xs, n):
    return it.islice(xs, None, n)

def drop(xs, n):
    return it.islice(xs, n, None)

def splice(xs, i):
    for j, x in enumerate(xs):
        if i != j:
            yield x

def test_chunks():
    nine = [None] * 9
    parts = list(chunks(nine, 3))
    assert len(parts) == 3 
    for part in parts:
        assert len(part) == 3
    
    ten = [None] * 10
    parts = list(chunks(ten, 3))
    assert len(parts) == 4
    for part in parts[:3]:
        assert len(part) == 3
    assert len(parts[-1]) == 1

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
    import nose
    nose.runmodule()

