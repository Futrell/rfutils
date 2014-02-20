""" listop

Optimized pure python elementwise list operations for everything in the 
operator module and a few other things.

The functions are as fast as they get in pure python.

Richard Futrell, 2013

"""
from __future__ import division
import operator
from itertools import repeat, imap
import inspect
from math import sqrt
from operator import mul

import listop # import the module itself so we can refer to it

# Begin metaprogramming voodoo.

_ONE_ARG_FUNCTIONS = {
    "abs" : None,
    "inv" : "~{}",
    "invert" : "~{}",
    "neg" : "-{}",
    "not_" : "not {}",
    "pos" : "+{}",
    "truth" : None,
}

_TWO_ARG_FUNCTIONS = {
    "add" : "{} + {}",
    "and_" : "{} and {}",
    "eq" : "{} == {}",
    "floordiv" :  " {} // {}",
    "ge" : "{} >= {}",
    "gt" : "{} > {}",
    "is_" : "{} is {}",
    "is_not" : "{} is not {}",
    "le" : "{} <= {}",
    "lt" : "{} < {}",
    "mod" : "{} % {}",
    "mul" : "{} * {}",
    "ne" : "{} != {}",
    "or_" : "{} or {}",
    "pow" : "{} ** {}",
    "sub" : "{} - {}",
    "truediv" : "{} / {}",
    "xor" : "{} ^ {}",
}

SCALAR_OP_TEMPLATE = \
    """def scalar_%(fn_name)s(list, scalar): 
        \""" %(fn_name)s all elements in list with scalar. \"""
        return [%(op_template)s for x in list]
    """

UNARY_OP_TEMPLATE = \
    """def %(fn_name)s(list): 
        \""" %(fn_name)s all elements in a list. \"""
        return [%(op_template)s for x in list]
    """

def _define_list_function(fn_name, fn, fn_maker):
    new_fn = fn_maker(fn_name, fn)
    setattr(listop, new_fn.__name__, new_fn)

def _make_binary_list_fn(fn_name, fn):
    def list_fn(one, two):
        return map(fn, one, two)
    list_fn.__name__ = fn_name
    list_fn.__doc__ = "%s elements in lists elementwise" % fn_name
    return list_fn

def _make_unary_list_fn(fn_name, fn):
    if _ONE_ARG_FUNCTIONS[fn_name] is not None:
        op_template = _ONE_ARG_FUNCTIONS[fn_name].format("x")
        definer = UNARY_OP_TEMPLATE % {  "fn_name" : fn_name,
                                         "op_template" : op_template,
                                        }
        exec definer in globals(), locals()
        return locals()[fn_name]
    def list_fn(list):
        return map(fn, list)
    list_fn.__name__ = fn_name
    list_fn.__doc__ = "%s elements in list elementwise" % fn_name
    return list_fn

def _make_scalar_fn(fn_name, fn):
    if _TWO_ARG_FUNCTIONS[fn_name] is not None:
        op_template = _TWO_ARG_FUNCTIONS[fn_name].format("x", "scalar")
        definer = SCALAR_OP_TEMPLATE % {"fn_name" : fn_name,
                                        "op_template" : op_template,
                                        }
        exec definer in globals(), locals()
        return locals()["scalar_" + fn_name]
    def scalar_fn(list, scalar):
        return map(fn, list, repeat(scalar, len(list)))
    scalar_fn.__name__ = "scalar_" + fn_name
    scalar_fn.__doc__ = "%s elements in list with a scalar" % fn_name
    return scalar_fn

def import_functions(module):
    functions = inspect.getmembers(module)
    for fn_name, fn in functions:
        if fn_name in _TWO_ARG_FUNCTIONS:
            _define_list_function(fn_name, fn, _make_binary_list_fn)
            _define_list_function(fn_name, fn, _make_scalar_fn)
        if fn_name in _ONE_ARG_FUNCTIONS:
            _define_list_function(fn_name, fn, _make_unary_list_fn)

import_functions(operator)

def dot(l1, l2):
    """ Get the dot product of two vectors. """
    return sum(imap(mul, l1, l2))

def l2_normalize(l):
    """ L2 normalize a list of floats. """
    norm = sqrt(sum(scalar_pow(l, 2)))
    try:
        return scalar_truediv(l, norm)
    except ZeroDivisionError:
        return [0] * len(l)
