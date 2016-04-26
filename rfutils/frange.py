""" Float range """

from __future__ import division
from itertools import count as _count

def frange(start, stop, step):
    """ range of floats """
    for i in _count():
        curr = start + i*step
        if curr >= stop:
            break
        else:
            yield curr
