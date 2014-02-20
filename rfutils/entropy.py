from __future__ import division
from math import log
from collections import Counter, defaultdict
from itertools import imap

base = log(2)
def log2(x):
    return log(x, 2)

def entropy(counts):
    """ entropy

    Fast calculation of Shannon entropy from an iterable of positive numbers. 
    Numbers are normalized to form a probability distribution, then entropy is
    computed.

    Generators are welcome.

    Params:
        counts: An iterable of positive numbers.

    Returns:
        Entropy of the counts, a positive number.

    """
    total = 0.0
    clogc = 0.0
    for c in counts:
        total += c
        try:
            clogc += c * log(c)
        except ValueError:
            pass
    return -(clogc/total - log(total)) / base


def conditional_entropy_of_counts(iterable_of_iterables):
    """ conditional entropy of counts

    Conditional entropy of a conditional distribution represented as an 
    iterable of iterables of counts.

    """
    entropy = 0.0
    grand_total = 0.0
    for counts in iterable_of_iterables:
        total = 0.0
        clogc = 0.0
        for c in counts:
            total += c
            try:
                clogc += c * log(c)
            except ValueError:
                pass
        grand_total += total
        entropy += total * -(clogc/total - log(total)) / base
    return entropy / grand_total

def mutual_information(counts):
    """ mutual information
    
    Takes iterable of tuples of form ((x_value, y_value), count)
    or counter whose keys are tuples (x_value, y_value).

    Stores marginal counts in memory.

    """
    if isinstance(counts, dict):
        counts = counter.iteritems()

    total = 0
    c_x = Counter()
    c_y = Counter()
    clogc = 0

    for (x, y), c_xy in counts:
        total += c_xy
        c_x[x] += c_xy
        c_y[y] += c_xy
        try:
            clogc += c_xy * log(c_xy)
        except ValueError:
            pass

    return (log(total)
            + (clogc
               - sum(c*log(c) for c in c_x.itervalues())
               - sum(c*log(c) for c in c_y.itervalues()))
            / total) / base

def _generate_counts(lines):
    first_line = next(lines)
    first_line_elems = first_line.split()
    if any(x.isdigit() for x in first_line_elems):
        yield _get_count(first_line)
        for line in lines:
            yield _get_count(line)
    counts = Counter(lines)
    counts[line] += 1
    for count in counts.itervalues():
        yield count
      
def _get_count(line):
    line = line.split()
    for x in line:
        if x.isdigit():
            return float(x)

if __name__ == "__main__":
    import sys
    lines = sys.stdin
    result = entropy(_generate_counts(lines))
    print(result)
