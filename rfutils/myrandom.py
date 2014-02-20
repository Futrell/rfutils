import itertools as it
import math
from random import *

def prob_choice(iterable, key=None):
    """ choice by probability

    Choose an element from iterable according to its probability.

    Interface can be used similarly to max, min, sorted, etc:
        * If given an iterable of (probability, ...) sequences, select 
            according to the first sequence element.
        * If given a key function, use that to calculate probability.
    
    This function assumes that probabilities are normalized and will break if 
    they are not. To use unnormalized probabilities, use weighted_choice. If 
    you want to use log probabilities, you can use prob_choice with 
    key=lambda x: exp(x[0]) or similar.

    Arguments:
        iterable: Any iterable of (probability, ...) sequences, or of anything
        whose probability will be calculated by a given key function.
        key: Optional function for calculating probabilities.

    Returns:
        An item from iterable.

    Examples:
        >>> prob_choice([1, 2, 3], key=lambda x: 1 if x == 2 else 0)
        2

        >>> prob_choice([(1, "cat"), (0, "dog")])
        (1, 'cat')

    """
    rnd = random()

    if key is not None:
        for x in iterable:
            rnd -= key(x)
            if rnd < 0:
                return x        
    else:    
        for sequence in iterable:
            rnd -= sequence[0]
            if rnd < 0:
                return sequence

    raise Exception("Probabilities not valid.")

def weighted_choice(iterable, key=None):
    """ choice by weights

    Choose an element from iterable according to specified weights, which 
    differ from probabilities in that they don't have to be normalized.

    Interface is similar to max, min, sorted, etc:
        * If given an iterable of (weight, ...) sequences, select according to
         the first sequence element.
        * If given a key function, use that to calculate weight.
    
    If you want to use log weights, you can use weighted_choice with 
    key=lambda x: exp(x[0]).

    The iterable will be loaded into memory.

    Arguments:
        iterable: Any iterable of (weight, ...) sequences, or of anything 
        whose weight will be calculated by a given key function.
        key: Optional function for calculating weights.

    Returns:
        An item from iterable.

    Examples:
        >>> prob_choice([1, 2, 3], key=lambda x: 100 if x == 2 else 0)
        2

        >>> prob_choice([(10000, "cat"), (0, "dog")])
        (10000, 'cat')

    """
    iterable = list(iterable)

    if key is not None:
        weights = [key(x) for x in iterable]
    else:
        weights = [x[0] for x in iterable]

    rnd = random() * math.fsum(weights)
    for weight, item in it.izip(weights, iterable):
        rnd -= weight
        if rnd < 0:
            return item

    raise Exception("Shouldn't get here.")

def sample(sequence, size):
    return [choice(sequence) for _ in xrange(size)]

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
