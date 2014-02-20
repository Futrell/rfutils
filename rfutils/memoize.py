""" memoize """
import functools
import inspect

def get_cache(memoized_fn):
    if inspect.isbuiltin(memoized_fn):  # fast_memoize
        return memoized_fn.__self__
    else:
        return memoized_fn.cache

def _keywords(f):
    argspec = inspect.getargspec(f)
    if argspec.defaults is None:
        return []
    return argspec.args[-len(argspec.defaults):]

def memoize(f):
    """ Memoize 

    Decorator to memoize a routine so that returned values are cached.

    """
    if (not inspect.ismethod(f) and len(inspect.getargspec(f).args) == 1 
        and inspect.getargspec(f).varargs is None):
        return fast_memoize(f)

    cache = {}

    if _keywords(f):
        _tuple = tuple
        def wrapper(*args, **kwargs):
            args = args + _tuple(kwargs.iteritems())
            if args in cache:
                return cache[args]
            cache[args] = result = f(*args, **kwargs)
            return result

    else:
        def wrapper(*args):
            if args in cache:
                return cache[args]
            cache[args] = result = f(*args)
            return result

    wrapper.cache = cache
    wrapper = functools.wraps(f)(wrapper)
    return wrapper

def fast_memoize(f):
    """ Fast Memoize

    A faster memoizer for one-argument functions.
    
    """
    #Based on Oren Tirosh's code at
    #http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/

    class Memodict(dict):
        def __missing__(self, key):
            result = self[key] = f(key)
            return result
        
    memodict = Memodict()
    wrapper = memodict.__getitem__
    return wrapper
