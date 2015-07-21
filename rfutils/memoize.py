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
            args = args + _tuple(kwargs.items())
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

def _test_memoized(memoized_fn):
    nose.tools.assert_equal(memoized_fn(0), memoized_fn(0))
    nose.tools.assert_equal(memoized_fn(1), memoized_fn(1))
    nose.tools.assert_not_equal(memoized_fn(0), memoized_fn(1))

def _test_memoized_cache(memoized_fn):
    import uuid
    cachelen = len(get_cache(memoized_fn))
    
    memoized_fn(uuid.uuid4())
    nose.tools.assert_equal(len(get_cache(memoized_fn)), cachelen+1)

    memoized_fn(uuid.uuid4())
    nose.tools.assert_equal(len(get_cache(memoized_fn)), cachelen+2)

def test_memoize_fn():
    import uuid
    
    @memoize
    def cool(x):
        return uuid.uuid4()

    _test_memoized(cool)
    _test_memoized_cache(cool)

def test_memoize_instancemethod():
    import uuid
    
    class Cool(object):
        @memoize
        def hey(self, x):
            return uuid.uuid4()
    cool = Cool()

    _test_memoized(cool.hey)

if __name__ == '__main__':
    import nose
    nose.runmodule()
