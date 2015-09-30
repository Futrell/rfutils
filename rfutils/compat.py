""" compat

Make Python 2 just a little more like Python 3.

Usage:

from compat import *

"""
from __future__ import print_function
import itertools as _it

print = print

try:
    range = xrange
except NameError:
    pass

try:
    map = _it.imap
    filter = _it.ifilter
    zip = _it.izip
except AttributeError:
    pass

