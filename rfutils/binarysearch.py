class NotFoundException(Exception):
    pass

def binary_find(data, target, cmp_fn=cmp, key=None, index=False):
    """ binary find

    Generic binary search in a list of sorted values yielding potentially 
    multiple matching values. Run time is O(logN + M), where N is the length 
    of data and M is the number of matches in data.

    Arguments:
        data: A list or tuple of sorted data.
        target: The value that data must match.
        cmp_fn: The function f(target, item) comparing target to an element of
                data. Should return 0 if the item matches the target. Should 
                return 1 if we should search to the right and -1 if we should 
                search to the left.
        index: If True, yield the indices of the matching items rather than 
                the items.

    Yields:
        Matching elements of data, or their indices.

    """
    start = 0
    end = len(data)
    span = end - start
    while span:
        middle = start + (span // 2)
        if key is None:
            comparison = cmp_fn(target, data[middle])
        else:
            comparison = cmp_fn(key(target), key(data[middle]))
        if not comparison: # match
            match_index = middle
            break
        if comparison > 0: # target is to the right of middle
            start = middle + 1 # search to the right
        else: # target is to the left of middle
            end = middle  # search to the left
        span = end - start
    else:
        raise NotFoundException(target)
    while not cmp_fn(target, data[match_index - 1]): # back up to the first matching value
        match_index -= 1
    while not cmp_fn(target, data[match_index]): # yield the matches in order
        yield match_index if index else data[match_index]
        match_index += 1


def binary_find_one(target, data, cmp_fn=cmp, key=None, index=False):
    """ binary find one

    Generic binary search in a list of sorted values returning only the first 
    matching value. Slightly faster for this purpose than the generator 
    version.

    Arguments:
        target: The value that data must match.
        data: A list or tuple of sorted data.
        cmp_fn: The function f(target, item) comparing target to an element of 
                data. Should return 0 if the item matches the target. Should 
                return 1 if we should search to the right and -1 if we should 
                search to the left.
        index: If true, return the index of the matching item rather than 
                the item.

    Returns:
        First matching element of data found, or its index.

    """
    start = 0
    end = len(data)
    span = end - start
    while span:
        middle = start + (span // 2)
        if key is None:
            comparison = cmp_fn(target, data[middle])
        else:
            comparison = cmp_fn(key(target), key(data[middle]))
        if not comparison: # match
            return middle if index else data[middle]
        if comparison > 0: # target is to the right of middle
            start = middle + 1 # search to the right
        else: # target is to the left of middle
            end = middle  # search to the left
        span = end - start
    raise NotFoundException(target)

