import itertools as it
import random
from collections import Counter
import math

from .compat import *
from .reductions import mreduce_by_key, product

flat = it.chain.from_iterable

class Ordering(object):
    def count_orders(self, xs, all_possible=False):
        d = {}
        for x in xs:
            canonical_order = self.canonical_order(x)
            if canonical_order not in d:
                d[canonical_order] = Counter()
            if all_possible:
                order_indiceses = list(self.indices_in_canonical_order(x))
                c = 1 / len(order_indiceses)
                for order_indices in order_indiceses:
                    d[canonical_order][order_indices] += c
            else:
                order_indices = next(self.indices_in_canonical_order(x))
                d[canonical_order][order_indices] += 1
        return d

    def permutation_indices(self, original, new_to_canonical_indices):
        for original_to_canonical in self.indices_in_canonical_order(original):
            canonical_to_original = {j:i for i,j in enumerate(original_to_canonical)}
            yield [canonical_to_original[i] for i in new_to_canonical_indices]

    def permutations_equivalent(self, xs, one, two):
        xs = self.canonical_order(xs)
        return all(xs[i] == xs[j] for i, j in zip(one, two))

class SortedOrdering(Ordering):
    def canonical_order(self, xs):
        """ canonical order

        Give a "canonical" ordering for xs, so that permutations of xs can be 
        represented as indices in the canonical ordering.

        """
        # do with key=str because in python3 ordering is only defined among
        # values of the same type, so comparing strings, tuples, and NoneTypes
        # isn't allowed; therefore we need to cast everything to the same type
        # to get a canonical total order.
        return tuple(sorted(xs, key=str, reverse=True))

    def indices_in_canonical_order(self, xs):
        return indices_in(self.canonical_order(xs), xs)

sorted_ordering = SortedOrdering()    

def lists_by_key(kvs):
    return mreduce_by_key(list.append, kvs, list)

def indices_in(xs, perm):
    """ indices in 

    Given an iterable xs and an iterable perm, which is a permutation of xs,
    give the possible indices for each value of perm in xs.

    for all values I of indices_in(xs, perm),
        reorder(xs, I) == perm
        
    There are multiple such indices; so this function is a generator that 
    yields each one.

    The number of indices yielded is num_equivalent_permutations(xs).

    """
    xs = list(xs)
    perm = list(perm)
    assert len(xs) == len(perm)

    values_to_xs_indices = lists_by_key((x, i) for i, x in enumerate(xs))
    values_to_perm_indices = lists_by_key((x, i) for i, x in enumerate(perm))
    assert values_to_xs_indices.keys() == values_to_perm_indices.keys()

    # need to order the values consistently
    target_indices = lazy_product_map(it.permutations,
                                 [v for k, v in sorted(values_to_perm_indices.items())])
    for p in target_indices:
        mapping = flat(map(zip, p, [v for k, v in sorted(values_to_xs_indices.items())]))
        yield tuple(i for _, i in sorted(mapping))

def shuffled(xs):
    xs = list(xs)
    random.shuffle(xs)
    return xs

def sample_indices_in(xs, perm):
    """ a value drawn uniformly at random from indices_in(xs, perm) """
    xs = list(xs)
    perm = list(perm)
    assert len(xs) == len(perm)

    values_to_xs_indices = lists_by_key((x, i) for i, x in enumerate(xs))
    values_to_perm_indices = lists_by_key((x, i) for i, x in enumerate(perm))
    assert values_to_xs_indices.keys() == values_to_perm_indices.keys()

    p = map(shuffled, [v for k, v in sorted(values_to_perm_indices.items())])
    mapping = flat(map(zip, p, [v for k, v in sorted(values_to_xs_indices.items())]))
    return tuple(i for _, i in sorted(mapping))

def num_equivalent_permutations(xs):
    """ The number of permutations of xs which are == to each other. 
    If all elements of xs are unique, then this is 1. 
    Elements of xs must be hashable. 
    """
    return product(math.factorial(c) for c in Counter(xs).values())

def lazy_product_map(f, xs):
    """ equivalent to itertools.product(*map(f, xs)), but does not hold the values 
    resulting from map(f, xs) in memory. xs must be a sequence. """
    if not xs:
        yield []
    else:
        x = xs[0]
        for result in f(x):
            for rest in lazy_product_map(f, xs[1:]):
                yield [result] + rest
                    
def reorder(xs, indices):
    """ reorder

    Elements of xs in the order specified by indices.
    
    Example:
    >>> list(reorder(['a', 'b', 'c', 'd'], [3, 1, 2, 0]))
    ['d', 'b', 'c', 'a']

    """
    xs = list(xs)
    indices = list(indices)
    assert len(xs) == len(indices)
    return [xs[i] for i in indices]

def ranked(xs, key=None):
    """ ranked

    For each element x in xs, the tuple (r, x) where r is the index of x in the
    sorted version of the sequence xs. 

    All elements of xs are mapped to a unique r; identical elements of xs receive 
    values r according to their order in the original xs.

    ranked is the function such that:
        * sorted(ranked(xs)) == list(enumerate(sorted(xs))),
        * [x for r, x in ranked(xs)] == list(xs)

    Example:
    >>> list(ranked(['a', 'c', 'b']))
    [(0, 'a'), (2, 'c'), (1, 'b')]

    >>> list(ranked(['a', 'c', 'b', 'a']))
    [(0, 'a'), (3, 'c'), (2, 'b'), (1, 'a')]

    """
    if key is None:
        value_key = lambda x: x[1]
    else:
        value_key = lambda x: key(x[1])
    
    indexed = enumerate(xs)
    sorted_by_value = sorted(indexed, key=value_key)
    indexed_by_sort_position = enumerate(sorted_by_value)
    in_original_order = sorted(indexed_by_sort_position, key=lambda x: x[1][0])
    return [(i, x) for i, (j, x) in in_original_order]

def ranks(xs, key=None):
    """ ranks

    For each element x in xs, the index of x in the sorted version of xs.
    Identical elements of xs receive indices according to their original order.

    Example:
    >>> list(ranks(['a', 'c', 'b']))
    [0, 2, 1]

    >>> list(ranks(['a', 'c', 'b', 'a']))
    [0, 3, 2, 1]

    """
    return [r for r, x in ranked(xs, key=key)]

def test_ranked():
    xs = "abcbabdabcabcbabaadax"
    assert sorted(ranked(xs)) == list(enumerate(sorted(xs)))
    assert [x for r, x in ranked(xs)] == list(xs)
    assert ranked([]) == []

def test_reorder():
    a = ['a', 'b', 'c']
    b = list(reorder(a, [0, 2, 1]))
    assert b == ['a', 'c', 'b']
    
def test_indices_in_correct():
    tests = [[1, 2, 3, 1, 2],
             [1, 1, 1],
             [1, 2, 3, 2, 1, 1],
             list("CABCBC"),
             ]

    import operator, functools, math
    def product(xs):
        return functools.reduce(operator.mul, xs, 1)

    for test in tests:
        canonical = sorted(test)
        for indices in indices_in(canonical, test):
            assert list(reorder(canonical, indices)) == test

def test_indices_in_exhaustive():
    tests = [[1, 2, 3, 1, 2],
             [1, 1, 1],
             [1, 2, 3, 2, 1, 1],
             list("CABCBC"),
             ]
    
    import operator, functools, math
    def product(xs):
        return functools.reduce(operator.mul, xs, 1)    

    for test in tests:
        canonical = sorted(test)
        num_options = len(set(indices_in(canonical, test)))
        assert num_options == product(math.factorial(c) for c in Counter(test).values())
        

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
    import nose
    nose.runmodule()
