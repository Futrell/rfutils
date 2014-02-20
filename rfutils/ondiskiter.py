import os
import os.path
import uuid
from collections import Iterable
try:
    import cPickle as pickle
except ImportError:
    import pickle

TMP_DIR = "/tmp"

class OnDiskIterable(Iterable):
    """ An on-disk iterable

    An iterable stored in a file on disk.

    This is for when you have a potentially large iterable that you want to 
    store on disk rather than in memory. The entire iterable is consumed and
    stored on disk.

    For example, I might want to temporarily store a list of strings I'm 
    getting from some lazy iterator, but not do that in memory, I'd do this:

    >>> iterable_on_disk = OnDiskIterable(xrange(10))
    >>> [x for x in iterable_on_disk]
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    """
    def __init__(self, iterable, filename=None):
        """ Put the contents of an iterable into a file. """
        if filename is None:
            self.filename = os.path.join(TMP_DIR, str(uuid.uuid1()))
        else:
            self.filename = filename

        with open(self.filename, 'rb') as outfile:
            for item in iterable:
                print >>outfile, self.encode(item)

    def encode(self, x):
        return pickle.dumps(x)

    def decode(self, x):
        return pickle.loads(x)

    def __iter__(self):
        with open(self.filename, 'rb') as infile:
            for line in infile:
                yield self.decode(line.split())

    def __del__(self):
        os.remove(self.filename)

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
