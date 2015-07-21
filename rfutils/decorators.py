""" Some useful decorators. """
import functools as ft

_SENTINEL = object()

def build_collection(collection_type):
    """ Use the decorated generator to build a collection. """
    def decorator(generator):
        """ Use the decorated generator to build a collection """
        @ft.wraps(generator)
        def wrapper(*args, **kwargs):
            return collection_type(generator(*args, **kwargs))
        return wrapper
    return decorator

build_list = build_collection(list)
build_set = build_collection(set)
build_dict = build_collection(dict)

def lazy_property(method):
    cached = []

    def _lazyprop(self):
        if cached:
            return cached[0]
        else:
            result = method(self)
            cached.append(result)
            return result

    _lazyprop.__doc__ = method.__doc__

    return property(_lazyprop)

def singleton(klass):
    """ Decorator for singleton class. """
    # we have to make sure the class has a different name from its object,
    # lest the object become impossible to pickle.
    # hence some nastiness:
    class_name = "%s_class" % klass.__name__
    globals()[class_name] = klass
    klass.__name__ = class_name
    return klass()

