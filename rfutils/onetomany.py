""" Classes for one-to-many maps. """
from collections import Counter

class OneToManyDict(dict):
    """ A dictionary matching keys to multiple values,
    stored in a collection of some type. """
    _coll = list
    _coll_add = list.append

    def iterflat(self):
        """ Iterate through the dictionary as (key, single value) tuples. 
        For example, if the dictionary contains {1: [1,2,3]}, then iterflat
        will produce (1,1), (1,2), (1,3).

        """
        for key, values in self.iteritems():
            for value in values:
                yield key, value

    def __missing__(self, key):
        x = self._coll()
        self[key] = x
        return x
        
    def clear_empty(self):
        """ Delete empty collections. """
        for key, val in self.iteritems():
            if not val:
                del self[key]

    @classmethod
    def from_tuples(cls, tuples):
        """ Make a one-to-many mapping from an iterable of tuples. 
        For example, an iterable with (1,1), (1,2), (2,2) would
        give the dictionary {1:[1,2], 2:[2]}. 

        Usage:
            >>> iterable = [(1,1), (1,2), (2,2)]
            >>> d = OneToManyDict.from_tuples(iterable)
            >>> d
            {1:[1,2], 2:[2]}

        """
        d = cls()
        for key, val in tuples:
            cls._coll_add(d[key], val)
        return d

class ListDict(OneToManyDict):
    """ A mapping of single keys to ordered lists of values. """
    _coll = list
    _coll_add = list.append

    def append(self, dict):
        for key, value in dict.iteritems():
            self[key].append(value)

class SetDict(OneToManyDict):
    """ A mapping of single keys to unordered sets of values. """
    _coll = set
    _coll_add = set.add

class CounterDict(OneToManyDict):
    """ A mapping of single keys to counters of values. """
    _coll = Counter

    @staticmethod
    def _coll_add(counter, val):
        counter[val] += 1

    def iterflat(self):
        """ Iterate through the dictionary as key, counter key, single value tuples. """
        for key, counter in self.iteritems():
            for counter_key, val in counter.iteritems():
                yield key, counter_key, val

