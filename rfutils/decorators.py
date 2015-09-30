""" Some useful decorators. """
import functools
import inspect

_SENTINEL = object()

def singleton(klass):
    """ Decorator for singleton class. """
    # we have to make sure the class has a different name from its object,
    # lest the object become impossible to pickle.
    # hence some nastiness to inject the class into the module namespace
    # with a name distinct from its object:
    class_name = "%s_singleton_class" % klass.__name__ # or qualname?
    klass.__name__ = class_name
    klass.__qualname__ = class_name
    the_object = klass()
    for attr_name in dir(the_object):
        attr = getattr(the_object, attr_name)
        if inspect.ismethod(attr):
            globals = attr.__globals__
            break
    else:
        raise ValueError(("Singleton decorator requires that class %s have "
                          + "at least one method") % klass)
    globals[class_name] = klass
    return the_object

