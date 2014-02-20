""" edit distance

Pure Python Levenshtein distance and alignment on arbitrary sequences. 

Though this is not as fast as C modules, its primary advantages are:
(1) It allows comparison of any sequences, rather than just strings,
(2) It allows you to specify deletion, insertion, and substitution cost 
functions, for example functions that index into a cost matrix,
(3) It runs in pypy.

The core edit distance method is highly optimized.

"""
from __future__ import print_function
import sys

from memoize import memoize, get_cache

class EditDister(object):
    def __init__(self, delete_cost_fn=None, insert_cost_fn=None, sub_cost_fn=None):
        if delete_cost_fn:
            self.delete_cost = delete_cost_fn
        if insert_cost_fn:
            self.insert_cost = insert_cost_fn
        if sub_cost_fn:
            self.sub_cost = sub_cost_fn
        self.operations = [self.delete, self.insert, self.substitute] 
        
    def align(self, x, y):
        """ align

        Align sequences x and y.

        Params:
            - x, y: Sequences to be aligned.
        
        Returns:
            A list of tuples representing the alignment.

        """
        if isinstance(x, list):
            x = tuple(x)
        if isinstance(y, list):
            y = tuple(y)

        cost, matrix = self._editdist_with_matrix(x, y)
        alignment = self._interpret_backtrace(matrix, x, y)
        return cost, alignment

    def _editdist_with_matrix(self, x, y):
        """ edit distance

        Calculate edit distance, returning a backtrace matrix.

        This method is relatively slow (but elegant!).

        """
        @memoize
        def _dist(x, y):
            if not x and not y:
                return 0
            elif not y:
                operations = [self.delete]
            elif not x:
                operations = [self.insert]
            else:
                operations = self.operations
            transformed = (operation(x,y) for operation in operations)
            return min(cost+_dist(*rest) for cost, rest in transformed)
        
        get_cache(_dist).clear()

        cost = _dist(x,y)
        return cost, get_cache(_dist)

    def editdist(self, xs, ys):
        """ Edit distance

        Calculate the Levenshtein distance between xs and ys, which can be any
        kind of sequence, according to the costs for insertion, deletion, and 
        substitution specified in this EditDister instance.

        Params:
            - xs, ys: Sequences to be compared.
        
        Returns:
            A positive number representing edit distance.
       
        """
        # Extremely optimized for speed--here be ugly code.

        _min = min
        _len = len
        _range = range

        _insert_cost = self.insert_cost
        _delete_cost = self.delete_cost
        _sub_cost = self.sub_cost

        len_xs = _len(xs)
        range_len_xs = _range(len_xs)
        len_xs_plus_1 = len_xs + 1

        current = [0]*len_xs_plus_1
        _delete_cost_x = [0]*len_xs
        for i in range_len_xs:
            cost = _delete_cost(xs[i])
            current[i+1] = current[i] + cost
            _delete_cost_x[i] = cost

        for y in ys:
            _insert_cost_y = _insert_cost(y)
            previous_row, current = current, [0]*len_xs_plus_1
            current[0] = previous_row[0] + _insert_cost_y
            for i in range_len_xs:
                ip1 = i + 1
                current[ip1] = _min(previous_row[ip1] + _insert_cost_y,
                                  current[i] + _delete_cost_x[i],
                                  previous_row[i] + _sub_cost(xs[i], y)
                                  )
            
        return current[-1]
                
    def _interpret_backtrace(self, backtrace, x, y):
        alignment = list()
        while x or y:
            current = backtrace[(x,y)]

            if x and y:
                cost, new_x_y = self.substitute(x, y)
                if current == backtrace[new_x_y] + cost:
                    pair = x[0], y[0]
                    x, y = new_x_y
                    alignment.append(pair)
                    continue
                    
            if x:
                cost, new_x_y = self.delete(x, y)
                if current == backtrace[new_x_y] + cost:
                    pair = x[0], None
                    x, y = new_x_y
                    alignment.append(pair)
                    continue
                    
            if y:
                cost, new_x_y = self.insert(x, y)
                if current == backtrace[new_x_y] + cost:
                    pair = None, y[0]
                    x, y = new_x_y
                    alignment.append(pair)
                    continue

            raise Exception("Alignment failed!")

        return alignment

    def delete(self, x, y):
        deleted = x[0]
        cost = self.delete_cost(deleted)
        return cost, (x[1:], y)
    
    def insert(self, x, y):
        inserted = y[0]
        cost = self.insert_cost(inserted)
        return cost, (x, y[1:])
    
    def substitute(self, x, y):
        x_word, y_word = x[0], y[0]
        cost = self.sub_cost(x_word, y_word)
        return cost, (x[1:], y[1:])

    def transpose(self, x, y):
        transposed = x[:2]
        cost = self.transpose_cost(transposed)
        return cost, (x[1:], x[0:1] + y[2:])

    def delete_cost(self, x):
        return 1

    def insert_cost(self, y):
        return 1

    def sub_cost(self, x, y):
        if x == y:
            return 0
        return 2.1

    def transpose_cost(self, x):
        return 1

e = EditDister()

def editdist(one, two, e=e):
    return e.editdist(one, two)    

def main(one, two, e=e):
    alignment = e.align(one, two)[1]
    one_aligned, two_aligned = zip(*alignment)
    for tier in [one_aligned, two_aligned]:
        for item in tier:
            print("*" if item is None else item, end=" ")
        print() # newline

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
