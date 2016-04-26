""" debug

Utilities for debugging.

"""
from __future__ import print_function
import sys
import itertools as it
import functools

err = functools.partial(print, file=sys.stderr)

def tap(x, prefix='', end='\n', file=sys.stderr):
    """ Tap

    Print the value of x and return it.
    Allows debugging of pipelines.

    """
    # based on funcy, http://github.com/Suor/funcy
    if prefix:
        print(prefix, end='', file=file)
    print(x, end=end, file=file)
    return x

def log_calls(fn):
    """ Log calls

    Print out the signatures of calls of the decorated function.

    """
    # based on funcy, http://github.com/Suor/funcy
    @functools.wraps(fn)
    def _fn(*args, **kwargs):
        binding = ", ".join(map(str, args))
        binding += ", ".join("%s=%s" % kv for kv in kwargs.items())
        signature = "%s(%s)" % (fn.__name__, binding)
        err(signature)
        return fn(*args, **kwargs)
    return _fn

def log_calls_and_returns(fn):
    """ Log calls and returns

    Print out the signatures and return values of calls of the 
    decorated function.

    """
    @functools.wraps(fn)
    def _fn(*args, **kwargs):
        binding = ", ".join(map(str, args))        
        binding += ", ".join("%s=%s" % kv for kv in kwargs.items())
        signature = "%s(%s)" % (fn.__name__, binding)
        ret = fn(*args, **kwargs)
        err("%s = %s" % (signature, ret))
        return ret
    return _fn

def interruptable(xs):
    try:
        for x in xs:
            yield x
    except KeyboardInterrupt:
        pass
        
                            
