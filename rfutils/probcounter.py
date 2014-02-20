from __future__ import division
import random
from math import log as _log
from collections import Counter
import copy

inf = float("inf")
def log(x):
    try:
        return _log(x)
    except ValueError:
        return -inf

class ProbCounter(Counter):
    """ Prob Counter

    A Counter with methods for returning probability values
    based on stored counts of observations.

    """
    counter_class = Counter
    
    def __init__(self, *args, **kwargs):
        self.counter = self.counter_class(*args, **kwargs)

        self.norm = 0
        self.norm = sum(self.itervalues())


    # Interface with the wrapped Counter

    def __getitem__(self, key):
        return self.counter[key]

    def __setitem__(self, key, value):
        self.norm += value - self.counter[key]
        self.counter[key] = value

    def __delitem__(self, key):
        self.norm -= self.counter[key]
        del self.counter[key]
        
    def __contains__(self, key):
        return key in self.counter

    def update(self, iterable=None, **kwds):
        self.counter.update(iterable, **kwds)
        self.norm = sum(self.itervalues())

    def pop(self, key):
        res = self.counter[key]
        del self[key]
        return res

    def clear(self, key):
        self.counter.clear()
        self.norm = 0

    def popitem(self):
        key, value = self.counter.popitem()
        self.norm -= value

    def itervalues(self):
        return self.counter.itervalues()

    def iteritems(self):
        return self.counter.iteritems()
    
    def iterkeys(self):
        return self.counter.iterkeys()


    # Probability-related methods.

    def p(self, x):
        """ Return the probability of x. """
        return self[x] / self.norm

    def logp(self, x):
        """ Return the log probability of x. """
        return log(self[x]) - log(self.norm)

    def observe(self, x):
        """ Observe one object: increase the count for it by one. """
        self[x] += 1

    def observe_iterable(self, iterable):
        """ Observe each of the objects in the iterable. """
        for item in iterable:
            self[item] += 1

    def expectation(self, fn=None):
        """ Expected value of a function. """
        if fn is None:
            return sum(x * count for x, count in self.iteritems()) / self.norm
        else:
            return sum(fn(x) * count for x, count in self.iteritems()) / self.norm

    def sample(self):
        """ Sample

        Return a random object from the counter according to its
        MLE probability.
        
        """
        number = random.random() * self.norm
        running_sum = 0
        for key, val in self.iteritems():
            running_sum += val
            if number <= running_sum:
                return key
        raise Exception("Something went wrong")


if __name__ == "__main__":
    # Tests

    # Test get and set and del
    pc = ProbCounter()
    pc[1] = 1
    assert pc[1] == 1
    assert pc.norm == 1
    pc[2] = 2
    assert pc[2] == 2
    assert pc.norm == 1 + 2
    pc[3] = 3
    assert pc[3] == 3
    assert pc.norm == 1 + 2 + 3
    del pc[3]
    assert pc[3] == 0
    assert pc.norm == 1 + 2

    # Test init from counter
    c = Counter({1:1, 2:2, 3:3})
    pc = ProbCounter(c)
    assert pc[1] == 1
    assert pc.p(1) == 1 / (1 + 2 + 3)
    assert pc.logp(1) == log(1) - log(1+2+3)
    del pc[1]
    assert pc[1] == 0
    assert pc.norm == 2 + 3
    assert pc.p(2) == 2 / (2 + 3)
    pc.pop(2)
    assert pc[2] == 0
    assert pc.norm == 3, pc.norm

    # Test init from iterable
    pc = ProbCounter([1,2,2,3,3,3])
    assert pc[1] == 1, pc[1]
    assert pc.p(1) == 1 / (1 + 2 + 3)
    assert pc.norm == (1 + 2 + 3)

    # Test init from kwargs
    pc = ProbCounter(cat=1, dog=2)
    assert pc["cat"] == 1
    assert pc.norm == 3

    # Test observations
    pc = ProbCounter([1,2,2,3,3,3])
    pc.observe(4)
    assert pc[4] == 1
    assert pc.norm == 1 + 2 + 3 + 1

    pc.observe(4)
    assert pc[4] == 2
    assert pc.norm == 1 + 2 + 3 + 2

    pc.observe_iterable([4,4])
    assert pc[4] == 4
    assert pc.norm == 1 + 2 + 3 + 4

    pc.update([5,5,5,5,5])
    assert pc[5] == 5
    assert pc.norm == 1 + 2 + 3 + 4 + 5

    # Test expectation and entropy
    norm = 1 + 2 + 3 + 4 + 5
    assert pc.expectation() == (1*1 + 2*2 + 3*3 + 4*4 + 5*5) / norm
    assert pc.expectation(lambda x: x+1) == (2*1 + 3*2 + 4*3 + 5*4 + 6*5) / norm

