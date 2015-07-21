""" debug

Utilities for debugging.

"""
from __future__ import print_function
import sys
import inspect
from itertools import *

def tap(x, prefix='', end='\n', file=sys.stdout):
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
    def _fn(*args, **kwargs):
        binding = inspect.getcallargs(fn, *args, **kwargs)
        arg_spec = inspect.getargspec(fn)
        keys = ifilter(None, chain(arg_spec.args, [arg_spec.varargs, arg_spec.keywords]))
        binding_str = ", ".join("%s=%s" % (key, binding[key]) for key in keys)
        signature = fn.__name__ + "(%s)" % binding_str
        print(signature, file=sys.stderr)
        return fn(*args, **kwargs)
    return _fn

def log_calls_and_returns(fn):
    """ Log calls and returns

    Print out the signatures and return values of calls of the 
    decorated function.

    """
    def _fn(*args, **kwargs):
        binding = inspect.getcallargs(fn, *args, **kwargs)
        arg_spec = inspect.getargspec(fn)
        keys = ifilter(None, chain(arg_spec.args, [arg_spec.varargs, arg_spec.keywords]))
        binding_str = ", ".join("%s=%s" % (key, binding[key]) for key in keys)
        signature = fn.__name__ + "(%s)" % binding_str
        print(signature, file=sys.stderr)
        ret = fn(*args, **kwargs)
        print("=> %s" % str(ret))
    return _fn

def assert_equal(x, y):
    if x != y:
        print("Assertion error: %s != %s" % (x,y), file=sys.stderr)
        raise AssertionError

def interruptable(xs):
    try:
        for x in xs:
            yield x
    except KeyboardInterrupt:
        pass
        
                            
