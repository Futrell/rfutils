import __main__

from itertools import *
from functools import reduce
import inspect

flat = chain.from_iterable

try:
    map = imap
    filter = ifilter
    filterfalse = ifilterfalse
except NameError:
    pass

def flatmap(f, *xss):
    return flat(map(f, *xss))

def take(xs, n):
    return islice(xs, None, n)

def drop(xs, n):
    return islice(xs, n, None)

def nth(xs, n):
    return next(islice(xs, n, None))

def starfilter(f, xss):
    for xs in xss:
        if f(*xs):
            yield xs

REVERSED_FS = {
    map,
    filter,
    reduce,
    flatmap,
    dropwhile,
    filterfalse,
    starmap,
    takewhile,
    str.join,
    starfilter,
}

    
class then_class(object):
    """  then

    An object then such that:
    x.a == m(a)

    """
    def __getattr__(self, name):
        return pipe_maker(lookup(name))

then = then_class()

class star_then_class(object):
    def __getattr__(self, name):
        return star_pipe_maker(lookup(name))

star_then = star_then_class
    
class pipe_maker(object):
    """ pipe maker

    An object m such that:

    m(f)(*args, **kwds) == t(f, args, kwds),
    where t is a pipe_into_me, and:

    m(f).a.b.c... == m(f.a.b.c...)

    """
    def __init__(self, thing):
        self.thing = thing

    def __call__(self, *args, **kwds):
        return pipe_into_me(self.thing, args, kwds)

    def __getattr__(self, name):
        return type(self)(getattr(self.thing, name))

class star_pipe_maker(pipe_maker):
    def __call__(self, args, **kwds):
        return pipe_into_me(self.thing, args, kwds)

class pipe_into_me(object):
    """ pipe into me

    An object t such that:

    x | t(f, args, kwds) == f(*([x] + args), **kwds)

    """
    def __init__(self, f, args, kwds):
        self.f = f
        self.args = args
        self.kwds = kwds

    def __ror__(self, other):
        return self.f(other, *self.args, **self.kwds)

def lookup(name):
    f = value_of(name)
    if f in REVERSED_FS:
        return lambda one, two, *rest: f(two, one, *rest)
    else:
        return f

def value_of(name):
    try:
        return eval(name)
    except NameError:
        try:
            return getattr(__main__, name)
        except AttributeError:
            try:
                # curr frame -> lookup -> then_class.__getattr__ -> caller
                caller = inspect.currentframe().f_back.f_back.f_back
                return caller.f_locals[name]
            except KeyError:
                try:
                    return caller.f_globals[name]
                except KeyError:
                    raise NameError("name '%s' is not defined" % name)
