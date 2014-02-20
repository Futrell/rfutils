import __builtin__
from itertools import *
from operator import add, itemgetter
import collections
import functools

_SENTINEL = object()

consume = functools.partial(collections.deque, maxlen=0)

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
    return izip_longest(*[iter(iterable)]*size, fillvalue=fillvalue)

def chunks(iterable, size):
    """ Chunks

    Break an iterable into chunks of specified size. 
    Equivalent to imap(list, ichunks(iterable, size)), but faster for 
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
    for group in (list(g) for g in izip_longest(*[iter(iterable)] * size,
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
    it = iter(iterable)
    while 1:
        chunk = islice(it, size)
        probe = next(chunk) # raises StopIteration if nothing's there
        yield chain([probe], chunk)
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
    it = iter(iterable)
    previous_breakpoint = 0
    for breakpoint in breakpoints:
        subit = islice(it, breakpoint - previous_breakpoint)
        yield subit
        consume(subit)
        previous_breakpoint = breakpoint
    yield list(it)

def segmentations(iterable):
    """ Segmentations

    Generate all possible ways to segment an iterable. 

    Params:
        iterable: The iterable. It will be consumed and held in memory.

    Yields:
        Lists of lists representing possible segmentations.

    Example:
        >>> lst = ['foo', 'bar', 'baz']
        >>> list(segmentations(lst))
        [[['foo', 'bar', 'baz']], 
         [['foo'], ['bar', 'baz']], 
         [['foo', 'bar'], ['baz']], 
         [['foo'], ['bar'], ['baz']]] 

    """
    iterable = list(iterable)
    n = len(iterable)
    breakpoint_groups = (combinations(xrange(1, n), i) for i in xrange(n))
    for breakpoint_group in breakpoint_groups:
        for breakpoints in breakpoint_group:
            yield list(map(list, segments(iterable, breakpoints)))

def items_in_context(iterable):
    lst = list(iterable)
    for i, item in enumerate(lst):
        yield lst[:i], item, lst[(i+1):]

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
    its = tee(iterable, n)
    for i, it in enumerate(its):
        for _ in xrange(i):
            next(it)
    return izip(*its)

def one_thru_ngrams(iterable, n):
    """ 1-thru-N-grams

    Yield all m-grams from an iterable for m = 1:n.
    They'll come out in arbitrary order.

    Example:
        >>> set(one_thru_ngrams("abcd", 3))
        {('a',), ('a', 'b'), ('a', 'b', 'c'), ('b',), ('b', 'c'), 
        ('b', 'c', 'd'), ('c',), ('c', 'd'), ('d',)}

    """
    if isinstance(iterable, Iterator):
        its = tee(iterable, n)
        for i, it in enumerate(its):
            for _ in xrange(i):
                next(it)

        first_it = its[0]
        rest_its = its[1:]

        so_far = []
        so_far_append = so_far.append

        while 1:
            del so_far[:]
            so_far_append(next(first_it))
            yield tuple(so_far)
            for it in rest_its:
                try:
                    so_far_append(next(it))
                    yield tuple(so_far)
                except StopIteration:
                    pass
    else:
        for x in chain.from_iterable(sliding(iterable, m) for m in xrange(n)):
            yield x

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
    t1, t2 = tee(iterable)
    return ifilter(pred, t1), ifilterfalse(pred, t2)

def accumulate(iterable, fn=add, start=None):
    it = iter(iterable)
    total = next(it) if start is None else start
    yield total
    for x in it:
        total = fn(total, x)
        yield total
    
def unique(iterable, key=None):
    """ iterate over unique elements of iterable, preserving order """
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

def take(n, iterable):
    """ take

    Return a list containing the first n elements of iterable.

    """
    return list(islice(iterable, n))

def itranspose(X):
    its = list(imap(iter, X))
    while 1:
        subit = imap(next, its)
        probe = next(subit)
        yield chain([probe], subit)
        consume(subit)

def first(iterable, default=_SENTINEL):
    """ Return the first element of an iterable. """
    try:
        return next(iter(iterable))
    except StopIteration:
        if default is _SENTINEL:
            raise ValueError("Empty iterable passed to first.")
        else:
            return default

def first_and_rest(iterable, default=_SENTINEL):
    """ first and rest

    Return the first element of the iterable and an iterator for the rest.

    """
    it = iter(iterable)
    try:
        return next(it), it
    except StopIteration:
        if default is _SENTINEL:
            raise VaueError("Empty iterable passed to first_and_rest.")
        else:
            return default, it

def last(iterable, default=_SENTINEL):
    """ last

    Get the last element of an iterable.

    """
    try:
        return deque(iterable, 1).pop()
    except IndexError:
        if default is _SENTINEL:
            raise ValueError("Empty iterable passed to last.")
        else:
            return default
        
def uniq(iterable, key=None):
    """ uniq: Remove adjacent duplicates.

    Preserves order. Remember only the element just seen. Like Posix uniq.

    Examples:
        >>> list(uniq('AAAABBBCCDAABBB'))
        ['A', 'B', 'C', 'D', 'A', 'B']

        >>> list(uniq('ABBCcAD', key=str.lower))
        ['A', 'B', 'C', 'A', 'D']

    """
    if key is None: # fast path
        return (k for k, g in groupby(iterable)) 
    else:
        return imap(next, imap(itemgetter(1), groupby(iterable, key)))

def unsliding(iterable):
    """ unsliding

    Undo the sliding function: turn an iterable (a,b),(b,c),(c,d)... into 
    a,b,c....
    
    Operates on any iterable of iterables.

    Examples:
        >>> foo = [('a', 'b', 'c'), ('b', 'c', 'd'), ('c', 'd', 'e')]
        >>> list(unsliding(foo))
        ['a', 'b', 'c', 'd', 'e']
        
        >>> bar = sliding(xrange(5), 3)
        >>> list(unsliding(bar))
        [0, 1, 2, 3, 4]

    """
    for group in iterable:
        group_it = iter(group)
        yield next(group_it) # the first item
    for item in group_it:
        yield item # and yield the rest of the last thing

def isplit(iterable, sep, maxsplit=None):
    """ Iterative Split

    Like str.split but operates lazily on any iterable. 

    Example:
        >>> foo = iter([0, 1, 2, 3, 'dog', 4, 5, 6, 7, 'dog', 8, 9])
        >>> list(set(chunk) for chunk in isplit(foo, 'dog'))
        [set([0, 1, 2, 3]), set([4, 5, 6, 7]), set([8, 9])]

    """
    it = iter(iterable)
    if maxsplit is None:
        while 1:
            subit = iter(it.next, sep)
            probe = next(subit) # let StopIteration percolate up
            yield chain([probe], subit)
            consume(subit)
    else:
        count = 0
        while count < maxsplit:
            subit = iter(it.next, sep)
            probe = next(subit) # let StopIteration percolate up
            yield chain([probe], subit)
            consume(subit)
            count += 1

