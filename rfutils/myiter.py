from collections import Iterator, deque
from itertools import *

class MyIter(Iterator):
    """ My Iter

    An iterator enabling Ccala-like application of itertools functions. This 
    makes it easy to build lazy data processing pipelines, and allows some
    interface compatibility with tools like Spark.

    Example:
        # Create a lazy pipeline
        >>> it = MyIter(xrange(10)).map(lambda x: x+1).filter(lambda x: x < 5)

        # The underlying iterator is only traversed when I consume it
        >>> list(it)
        [1, 2, 3, 4]

    """
    def __init__(self, iterable):
        self.iter = iter(iterable)

    def chain(self, *others):
        """ chain

        Return a concatenated iterable.

        Example:
            >>> one = MyIter(xrange(4))
            >>> two = MyIter(xrange(3,-1,-1))
            >>> three = MyIter(xrange(4))
            >>> four = one.chain(two, three)
            >>> list(four)
            [0, 1, 2, 3, 3, 2, 1, 0, 0, 1, 2, 3]

        """
        return MyIter(chain(self.iter, *others))

    def compress(self, selectors):
        return MyIter(compress(self.iter, selectors))

    def drop(self, n):
        def dropper(iterator):
            next(islice(iterator, n, n), None)
            for x in iterator:
                yield x
        return MyIter(dropper(self.iter))

    def dropwhile(self, pred):
        return MyIter(dropwhile(pred, self.iter))

    def groupby(self, keyfunc=None):
        return MyIter(((key, MyIter(items)) 
            for key, items in groupby(self.iter, keyfunc)))

    def map(self, fn):
        """ map

        Apply a function to each element of the iterator.

        """
        return MyIter(imap(fn, self.iter))

    def filter(self, pred):
        """ filter

        Remove iterator elements where the function pred returns False.

        """
        return MyIter(ifilter(pred, self.iter))

    def slice(self, start, stop, step=1):
        return MyIter(islice(self.iter, start, stop, step))

    def starmap(self, fn):
        return MyIter(starmap(fn, self.iter))

    def tee(self, n):
        return tuple(MyIter(x) for x in tee(self.iter, n))

    def takewhile(self, pred):
        return MyIter(takewhile(pred, self.iter))

    def zip(self, *others):
        return MyIter(izip(self.iter, *others))

    def zip_longest(self, *others):
        return MyIter(izip_longest(self.iter, *others))

    def reduce(self, fn):
        return reduce(fn, self.iter)

    def flat_map(self, fn):
        return MyIter(chain.from_iterable(imap(fn, self.iter)))

    def reduceby(self, fn, keyfunc=None):
        return MyIter(((group, items.reduce(fn)) for group, items in self.groupby(keyfunc)))

    def cycle(self):
        return MyIter(cycle(self.iter))

    def product(self, repeat=1, *others):
        return MyIter(product(self.iter, repeat=repeat, *others))
    
    def permutations(self, r=None):
        return MyIter(permutations(self.iter, r=r))

    def combinations(self, r):
        return MyIter(combinations(self.iter, r))

    def combinations_with_replacement(self, r):
        return MyIter(combinations_with_replacement(self.iter, r))

    def take(self, n):
        return list(islice(self.iter, n))

    def consume(self, n):
        if n is None:
            deque(self.iter, maxlen=0)
        else:
            next(islice(iterator, n, n), None)

    def count(self, pred=None):
        """ count

        Count how many elements in the iterable.
        If you supply a function pred, then count how many elements
        in the iterable satisfy the predicate.

        Consumes the iterable.
        
        """
        if pred is None:
            for i, _ in enumerate(self.iter):
                pass
            return i
        else:
            return sum(pred(x) for x in self.iter)                

    def chunks(self, size):
        """ chunks

        Return an iterator yielding non-overlapping chunks of given size.

        """
        return MyIter(chunks(self.iter, size))

    def peek(self, n=1):
        """ peek

        Return up to the next n elements of the iterator, without consuming 
        those elements. If there are not n elements left, return everything 
        possible; so for example if there are 3 elements left in the iterator 
        and you call it.peek(4), you will get a list of those 3 elements. If 
        there are 0 elements left in the iterator, you get an empty list.

        Params:
            n (default 1): Maximum items to return.

        Example:
            >>> it = MyIter(xrange(5))
            >>> it.peek(3)
            [0,1,2]
            >>> it.peek(6)
            [0,1,2,3,4,5]
            >>> it.consume()
            >>> it.peek(3)
            []

        """
        peeked = [next(self.iter) for _ in xrange(n)]
        self.iter = chain(peeked, self.iter)
        return peeked

    def precompute(self, n=None):
        if n is None:
            self.iter = iter(list(self.iter))
        else:
            precomputed = [next(self.iter) for _ in xrange(n)]
            self.iter = chain(precomputed, self.iter)

    def limit(self, n):
        return MyIter(islice(self.iter, 0, n))

    def append(self, item):
        return self.chain([item])
        
    def __iter__(self):
        return self.iter

    def next(self):
        return next(self.iter)

    def __nonzero__(self):
        """ nonzero

        Return whether an iterator is empty or not.
        This works by peeking the first element.
        
        """
        return self.peek()
