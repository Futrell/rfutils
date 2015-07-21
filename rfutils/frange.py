""" Float range """

from __future__ import division
from itertools import count

def frange(stop=None, start=None, step=None, steps=None):
    """ range of floats """
    if start is not None:
        start, stop = stop, start
    if step is None and steps is None:
        step = 1.0
    elif step is None: # so steps must be something
        step = (stop - start) / steps

    for i in count():
        curr = start + i*step
        if curr >= stop or i >= steps:
            break
        else:
            yield curr
