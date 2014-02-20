from dictutils import HashableDict

class ManyToOneDict(dict):
    """ A dictionary with multiple values (tuples) as keys. 
    
    For use as a many-to-one mapping.

    """
    def __init__(self, variables=None):
        self._super_setitem = super(ManyToOneDict, self).__setitem__
        self._super_getitem = super(ManyToOneDict, self).__getitem__
        self._super_contains = super(ManyToOneDict, self).__contains__

    def __setitem__(self, key, val):
        self._super_setitem(tuple(key), val)

    def __getitem__(self, key):
        return self._super_getitem(tuple(key))

    def __contains__(self, key):
        return self._super_contains(tuple(key))


class NamedManyToOneDict(dict):
    """ A dictionary with mappings as keys. 
    
    For use as a named many-to-one mapping.

    """
    def __init__(self):
        self._super_setitem = super(NamedManyToOneDict, self).__setitem__
        self._super_getitem = super(NamedManyToOneDict, self).__getitem__
        self._super_delitem = super(NamedManyToOneDict, self).__delitem__
        self._super_contains = super(NamedManyToOneDict, self).__contains__

    def __setitem__(self, key, val):
        key = HashableDict(key)
        self._super_setitem(key, val)

    def __delitem__(self, key):
        key = HashableDict(key)
        return self._super_delitem(key)

    def __getitem__(self, key):
        key = HashableDict(key)
        return self._super_getitem(key)

    def __contains__(self, key):
        key = HashableDict(key)
        return self._super_contains(key)

    def matching_items(self, key):
        return (item for item in self.iteritems() 
                if all(item[0][k] == v for k, v in key.iteritems()))
