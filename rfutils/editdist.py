""" edit distance

Highly optimized pure Python Levenshtein distance and alignment on 
arbitrary sequences. 

Though this is not as fast as C modules, its primary advantages are:
(1) It allows comparison of any sequences, rather than just strings,
(2) It allows you to specify deletion, insertion, and substitution cost 
functions, for example functions that index into a cost matrix,
(3) It runs in pypy.

"""
from __future__ import print_function
import sys

class EditDister(object):
    def __init__(self,
                 delete_cost_fn=None,
                 insert_cost_fn=None,
                 sub_cost_fn=None):
        if delete_cost_fn:
            self.delete_cost = delete_cost_fn
        else:
            self.delete_cost = lambda x: 1
        if insert_cost_fn:
            self.insert_cost = insert_cost_fn
        else:
            self.insert_cost = lambda x: 1
        if sub_cost_fn:
            self.sub_cost = sub_cost_fn
        else: 
            self.sub_cost = lambda x, y: 0 if x == y else 1

    def _align(self, xs, ys):
        def generate_alignment(xs, ys, backtrace):
            x = len(xs)
            y = len(ys)
            
            while x > 0 or y > 0:
                new_x, new_y = backtrace[x, y]
                
                if new_x == x:
                    yield None, ys[y-1]
                elif new_y == y:
                    yield xs[x-1], None
                else:
                    yield xs[x-1], ys[y-1]

                x = new_x
                y = new_y
                    
        _, backtrace = self.editdist_with_backtrace(xs, ys)
        result = reversed(list(generate_alignment(xs, ys, backtrace)))
        return result

    def _editdist_with_backtrace(self, xs, ys):
        """ Edit distance with backtrace matrix

        Calculate the Levenshtein distance between xs and ys, which can be any
        kind of sequence, according to the costs for insertion, deletion, and 
        substitution specified in this EditDister instance. Also, return the 
        backtrace matrix.

        Params:
            - xs, ys: Sequences to be compared.
        
        Returns:
            A positive number representing edit distance, and the backtrace
            matrix.
       
        """
        # broken
        backtrace = {}

        _insert_cost = self.insert_cost
        _delete_cost = self.delete_cost
        _sub_cost = self.sub_cost

        len_xs = len(xs)
        range_len_xs = range(len_xs)
        len_xs_plus_1 = len_xs + 1

        current = [0]*len_xs_plus_1
        _delete_cost_x = [0]*len_xs
        for i in range_len_xs:
            cost = _delete_cost(xs[i])
            ip1 = i + 1
            current[ip1] = current[i] + cost
            _delete_cost_x[i] = cost
            backtrace[ip1, 0] = i, 0

        for j, y in enumerate(ys):
            _insert_cost_y = _insert_cost(ys[j])
            previous_row, current = current, [0]*len_xs_plus_1
            current[0] = previous_row[0] + _insert_cost_y
            jp1 = j + 1
            backtrace[0, jp1] = 0, j
            for i in range_len_xs:
                ip1 = i + 1
                insert = previous_row[ip1] + _insert_cost_y
                delete = current[i] + _delete_cost_x[i]
                substitute = previous_row[i] + _sub_cost(xs[i], y)
                if insert < delete:
                    if insert < substitute:
                        current[ip1] = insert
                        backtrace[jp1, ip1] = j+1, i
                    else:
                        current[ip1] = substitute
                        backtrace[jp1, ip1] = j, i
                else:
                    if delete < substitute:
                        current[ip1] = delete
                        backtrace[jp1, ip1] = j, ip1
                    else:
                        current[ip1] = substitute
                        backtrace[jp1, ip1] = j, i
            
        return current[-1], backtrace
        
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
        _insert_cost = self.insert_cost
        _delete_cost = self.delete_cost
        _sub_cost = self.sub_cost

        len_xs = len(xs)
        range_len_xs = range(len_xs)
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
                insert = previous_row[ip1] + _insert_cost_y
                delete = current[i] + _delete_cost_x[i]
                substitute = previous_row[i] + _sub_cost(xs[i], y)
                if insert < delete:
                    if insert < substitute:
                        current[ip1] = insert
                    else:
                        current[ip1] = substitute
                else:
                    if delete < substitute:
                        current[ip1] = delete
                    else:
                        current[ip1] = substitute
            
        return current[-1]
    
e = EditDister()

def editdist(one, two, e=e):
    return e.editdist(one, two)    

def main(one, two, e=e):
    #alignment = e.align(one, two)
    #one_aligned, two_aligned = zip(*alignment)
    #for tier in [one_aligned, two_aligned]:
    #    for item in tier:
    #        print("*" if item is None else item, end=" ")
    #    print() # newline
    print(editdist(one, two, e=e))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
