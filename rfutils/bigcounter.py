from __future__ import print_function
import os
import random
from collections import Counter
import tempfile
import logging
import sqlite3

logger = logging.getLogger('bigcounter')

def one(it):
    try:
        return next(iter(it))
    except StopIteration:
        return None

def tap(x):
    print(x)
    return x


class BigCounter(Counter):
    def __init__(self, filename=None, tablename='unnamed', flag='c'):
        """
        Initialize a sqlite-backed Counter. The dictionary will be a table 
        `tablename` in database file `filename` with two columns: value and count. 

        Not thread-safe :(

        Iff no `filename` is given, a random file in temp will be used (and deleted
        from temp once the dict is closed/deleted). 
        Iff a filename is given, then that file will persist after this object dies.

        The `flag` parameter:
          'c': default mode, open for read/write, creating the db/table if necessary.
          'w': open for r/w, but drop `tablename` contents first (start with empty table)
          'n': create a new database (erasing any existing tables, not just `tablename`!).

        """
        # Based on sqlitedict
        self.in_temp = filename is None
        if self.in_temp:
            randpart = hex(random.randint(0, 0xffffff))[2:]
            self.filename = os.path.join(tempfile.gettempdir(), 'sqlcounter' + randpart)
        else:
            self.filename = filename
        if flag == 'n':
            if os.path.exists(self.filename):
                os.remove(self.filename)

        self.tablename = tablename

        logger.info("opening Sqlite table %r in %s" % (tablename, filename))
        MAKE_TABLE = 'CREATE TABLE IF NOT EXISTS %s (key TEXT PRIMARY KEY, value INTEGER)' % self.tablename

        self.conn = sqlite3.connect(self.filename, isolation_level=None, 
                                    check_same_thread=False)
        self.conn.execute(MAKE_TABLE)
        self.conn.commit()
        if flag == 'w':
            self.clear()

    def __str__(self):
        return "BigCounter(%s)" % self.filename

    def __len__(self):
        GET_LEN = "SELECT COUNT(*) FROM %s" % self.tablename
        rows = one(self.conn.execute(GET_LEN))[0]
        return rows if rows is not None else 0

    def __bool__(self):
        GET_LEN = "SELECT MAX(ROWID) FROM %s" % self.tablename
        return one(self.conn.execute(GET_LEN)) is not None

    def iterkeys(self):
        GET_KEYS = "SELECT key FROM %s ORDER BY rowid" % self.tablename
        for key in self.conn.execute(GET_KEYS):
            yield key[0]

    def itervalues(self):
        GET_VALUES = "SELECT value FROM %s ORDER BY rowid" % self.tablename
        for value in self.conn.execute(GET_VALUES):
            yield value[0]

    def iteritems(self):
        GET_ITEMS = "SELECT key, value FROM %s ORDER BY rowid" % self.tablename
        for key, value in self.conn.execute(GET_ITEMS):
            yield key, value

    def __contains__(self, key):
        HAS_ITEM = "SELECT 1 FROM %s WHERE key=?" % self.tablename
        return one(self.conn.execute(HAS_ITEM, (key,))) is not None
    
    def __getitem__(self, key):
        GET_ITEM = "SELECT value FROM %s WHERE key=?" % self.tablename
        item = one(self.conn.execute(GET_ITEM, (key,)))
        if item is None:
            return 0
        else:
            return item[0]

    def __setitem__(self, key, value):
        ADD_ITEM = "REPLACE INTO %s (key, value) VALUES (?,?)" % self.tablename
        self.conn.execute(ADD_ITEM, (key, value))
        self.conn.commit()

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        DEL_ITEM = "DELETE FROM %s WHERE key=?" % self.tablename
        self.conn.execute(DEL_ITEM, (key,))
        self.conn.commit()

    def update(self, iterable, **kwds):
        for item in iterable:
            self[item] += 1
        if kwds:
            self.update(kwds)

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def __iter__(self):
        return self.iterkeys()

    def clear(self):
        CLEAR_ALL = "DELETE FROM %s;" % self.tablename
        self.conn.commit()
        self.conn.execute(CLEAR_ALL)
        self.conn.commit()

    def delete_file(self):
        self.conn.commit()
        self.conn.close()
        try:
            os.remove(self.filename)
        except OSError:
            pass

    def __del__(self):
        try:
            if self.conn is not None:
                self.conn.close()
                self.conn = None
            if self.in_temp:
                self.delete_file()
        except:
            pass
        
    @classmethod
    def from_dict(cls, dict, **kwds):
        self = cls(**kwds)

        ADD_ITEM = "REPLACE INTO %s (key, value) VALUES (?,?)" % self.tablename


        self.conn.executemany(ADD_ITEM, ((key, self[key] + value) 
                                         for key, value in dict.iteritems()))
        self.conn.commit()
        return self

    @classmethod
    def from_iterable(cls, iterable, **kwds):
        self = cls(**kwds)
        self.update(iterable)
        return self

    @classmethod
    def from_csv(cls, filename, sep=",", header=False, **kwds):
        """ initialize from a csv of keys, counts """
        self = cls(**kwds)
        with open(filename, "rb") as infile:
            lines = (line.strip().split(sep) for line in infile)
            if header:
                next(lines) # dump the first line
            for line in lines:
                self[line[0]] = int(line[-1])
        return self


class BigNamedManyToOneCounter(BigCounter):
    def __init__(self, variables, filename=None, tablename='unnamed', flag='c'):
        self.in_temp = filename is None
        if self.in_temp:
            randpart = hex(random.randint(0, 0xffffff))[2:]
            self.filename = os.path.join(tempfile.gettempdir(), 'sqlmulticounter' + randpart)
        else:
            self.filename = filename
        if flag == 'n':
            if os.path.exists(filename):
                os.remove(filename)

        self.tablename = tablename

        logger.info("opening Sqlite table %r in %s" % (tablename, filename))
        cols = ",".join(["%s TEXT" % c for c in variables]) 
        MAKE_TABLE = 'CREATE TABLE IF NOT EXISTS %s (%s, PRIMARY KEY (%s))' % (self.tablename, 
                                                                               cols + ", value INTEGER", 
                                                                               ",".join(variables),
                                                                               )
        self.conn = sqlite3.connect(self.filename, isolation_level=None,
                                    check_same_thread=False)
        self.conn.execute(MAKE_TABLE)
        self.conn.commit()
        if flag == 'w':
            self.clear()
        self.variables = variables
        self._columns_select = ",".join(self.variables)
    
    def iterkeys(self):
        GET_KEYS = 'SELECT %s FROM %s ORDER BY rowid' % (self._columns_select, self.tablename)
        for key in self.conn.execute(GET_KEYS):
            yield dict(zip(self.variables, key))

    def iteritems(self):
        GET_ITEMS = 'SELECT %s, value FROM %s ORDER BY rowid' % (self._columns_select, self.tablename)
        for item in self.conn.execute(GET_ITEMS):
            yield dict(zip(self.variables, item[:-1])), item[-1]

    def _make_query(self, key):
        return " AND ".join(["%s=?" % col for col in key])


    def __contains__(self, key):
        HAS_ITEM = "SELECT 1 FROM %s WHERE %s" % (self.tablename, 
                                                  self._make_query(key)
                                                  )
        return one(self.conn.execute(HAS_ITEM, key.values())) is not None

    def __getitem__(self, key):
        if len(key) < len(self.variables):
            GET_VALUES = "SELECT SUM(value) FROM %s WHERE %s" % (self.tablename,
                                                            self._make_query(key),
                                                            )
            item = one(self.conn.execute(GET_VALUES, key.values()))
            return 0 if item is None else item[0]
        else:
            GET_VALUE = "SELECT value FROM %s WHERE %s" % (self.tablename, 
                                                      self._make_query(key),
                                                      )
            item = one(self.conn.execute(GET_VALUE, key.values()))
            return 0 if item is None else item[0]

    def matching_items(self, key):
        GET_ITEMS = "SELECT * FROM %s WHERE %s" % (self.tablename,
                                                   self._make_query(key),
                                                   )
        items = self.conn.execute(GET_ITEMS, key.values())
        for item in items:
            yield dict(zip(self.variables, item[:-1])), item[-1]

    def __setitem__(self, key, value):
        PLACEHOLDERS = ",".join(["?" for _ in xrange(len(key)+1)])
        ADD_ITEM = "REPLACE INTO %s (%s, value) VALUES (%s)" % (self.tablename,
                                                              ",".join(key.iterkeys()),
                                                              PLACEHOLDERS,
                                                              )
        self.conn.execute(ADD_ITEM, key.values() + [value]) # relies on order of values()...
        self.conn.commit()

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)

        DEL_ITEM = "DELETE FROM %s WHERE %s" % (self.tablename, 
                                                self._make_query(key)
                                                )
        self.conn.execute(DEL_ITEM, key.values()) # relies on order of values
        self.conn.commit()

    def update(self, iterable, **kwds): 
        if hasattr(iterable, "iteritems"):
            items = iterable.iteritems()
            first_key, first_val = next(items)
            keys = list(first_key.iterkeys())
            self[first_key] = first_val

            PLACEHOLDERS = ",".join(["?" for _ in xrange(len(keys)+1)])
            UPDATE_ITEMS = "REPLACE INTO %s (%s, value) VALUES (%s)" % (self.tablename,
                                                                        ",".join(keys),
                                                                        PLACEHOLDERS,
                                                                        )
            self.conn.executemany(UPDATE_ITEMS, (key.values() + [self[key] + value]
                                                 for key, value in items))
            self.conn.commit()
        else:
            for item in iterable:
                self[item] += 1

        if kwds:
            self.update(kwds)


    @classmethod
    def from_dict(cls, dict, **kwds):
        items = dict.iteritems()
        if "columns" in kwds:
            columns = kwds.pop("columns")
            self = cls(columns, **kwds)
        else:
            first_key, first_val = next(items)
            self = cls(first_key.keys(), **kwds)
            self[first_key] = first_val
        self.update(dict(items))
        return self

    @classmethod
    def from_iterable(cls, iterable, **kwds):
        it = iter(iterable)
        if "columns" in kwds:
            columns = kwds.pop("columns")
            self = cls(columns, **kwds)
        else:
            first_key = next(it)
            self = cls(first_key.keys(), **kwds)
            self[first_key] += 1
        self.update(it)
        return self

    @classmethod
    def from_csv(cls, filename, sep=",", header=False, columns=None, **kwds):
        """ initialize from a csv of keys, counts """
        with open(filename, "rb") as infile:
            lines = (line.strip().split(sep) for line in infile)
            if header: # sniff columns from header
                header = next(lines) # dump the first line
                self = cls(header, **kwds)
            elif columns: # use provided columns
                self = cls(columns, **kwds)
            else: # give default variable names a,b,c,...
                first_line = next(lines)
                columns = [chr(ord(x) + 97) for x in xrange(len(first_line)-1)]
                self = cls(columns, **kwds)
                self[dict(zip(columns, first_line[:-1]))] = int(first_line[-1]) 
            for line in lines:
                self[line[0]] = int(line[-1])
        return self


if __name__ == "__main__":
    bc = BigCounter()
    assert bc[1] == 0
    assert 1 not in bc
    bc[1] = 1
    assert 1 in bc
    assert bc[1] == 1
    bc[1] = 2
    assert bc[1] == 2
    del bc[1]
    assert bc[1] == 0
    bc2 = BigCounter.from_dict({"one":1, "two":2})
    assert bc2["one"] == 1
    assert bc2["two"] == 2
    del bc2
    bc3 = BigCounter.from_iterable(["one", "two", "two", "three", "three", "three"])
    assert bc3["one"] == 1
    assert bc3["two"] == 2
    assert bc3["three"] == 3
    del bc3

    nbc = BigNamedManyToOneCounter(["one", "two"])
    assert nbc[{"one":1, "two":2}] == 0
    assert {"one":1, "two":2} not in nbc
    nbc[{"one":1, "two":2}] = 1
    assert {"one":1, "two":2} in nbc
    assert nbc[{"one":1, "two":2}] == 1
    nbc[{"one":1, "two":2}] = 5
    assert nbc[{"one":1, "two":2}] == 5

    class HD(dict):
        def __hash__(self):
            return hash(tuple(self.iteritems()))

    nbc.clear()
    assert nbc[{"one":1, "two":2}] == 0
    assert nbc[{"one":1, "two":4}] == 0
    assert nbc[{"one":1, "two":6}] == 0
    nbc.update({HD({"one":1, "two":2}): 2, HD({"one":1, "two":4}): 4, HD({"one":1, "two":6}): 6})
    assert nbc[{"one":1, "two":2}] == 2
    assert nbc[{"one":1, "two":4}] == 4
    assert nbc[{"one":1}] == sum([2,4,6])
    del nbc

    print("tests OK")
