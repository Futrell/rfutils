rfutils

These are some various chunks of python that I've found useful to keep
around. Many of them are useful, while some of them are just doodles 
that I haven't had a chance to use much yet. Some might be split off
into their own modules if they keep growing.

Stuff I use all the time:
* binarysearch -- Binary search.
* entropy -- Shannon entropy.
* filehandling -- Hassle-free filehandling.
* indices -- Automatically make unique indices.
* memoize -- Decorators for memoization.
* myitertools -- Iteration patterns I've needed.
* myrandom -- Weighted random choice.
* systemcall -- Easy bash calls.
* nl/isling -- Identify if a string is linguistic or not.

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

Richard Futrell, 2014
