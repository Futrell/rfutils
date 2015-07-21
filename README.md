""" rfutils """

These are some various chunks of python that I've found useful to keep
around. Many of them are useful, while some of them are just doodles 
that I haven't had a chance to use much yet. Some might be split off
into their own modules if they keep growing.

All of this works in Python 2 and some but not all works in Python 3.

Especially useful:
* indices -- Automatically make unique indices.
* memoize -- Decorators for memoization.
* myitertools -- Iteration patterns I've needed.
* systemcall -- Easy bash calls.
* nl/isling -- Identify if a string is linguistic or not.
* decorators -- Useful decorators including a lazy @property.

Optimized stuff:
* editdist -- Fast edit distance of arbitrary sequences.
* listop -- Scalar and elementwise array operations.

Doodles:
* bigcounter -- A SQLite-backed Counter. Incredibly slow. Don't use this.
* manytoone -- Many-to-one mappings.
* myiter -- Scala-like iterator objects.
* ondiskiter -- An iterable stored on disk.
* onetomany -- One-to-many mappings.
* probcounter -- A Counter supplying probability-related methods.
* jointprobcounter --- Same thing, but for joint distributions.

Richard Futrell, 2015
