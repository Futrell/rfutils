from __future__ import division
import random
from math import log as _log
from collections import Counter
import copy

from probcounter import ProbCounter
from manytoone import NamedManyToOneDict

inf = float("inf")
def log(x):
    try:
        return _log(x)
    except ValueError:
        return -inf


class NamedManyToOneCounter(Counter, NamedManyToOneDict):
    def __init__(self, variable_names, *args, **kwargs):
        super(NamedManyToOneCounter, self).__init__(*args, **kwargs)
        self.variables = variable_names


class NamedJointProbCounter(ProbCounter):
    """ Named Joint Prob Counter

    A Prob Counter for joint distributions with explicit variable names.
    
    """
    counter_class = NamedManyToOneCounter

    def __init__(self, variable_names, *args, **kwargs):
        self.counter = self.counter_class(variable_names, *args, **kwargs)
        self.norm = 0
        self.variables = variable_names

    def matching_items(self, key):
        return self.counter.matching_items(key)

    @classmethod
    def from_iterable(cls, iterable):
        iterator = iter(iterable)
        first = next(iterator)
        self = cls(first.keys())
        self.observe(first)
        self.observe_iterable(iterator)
        return self

    @classmethod
    def from_probcounter(cls, probcounter, variable_name="x"):
        self = cls([variable_name])
        for key, val in probcounter.iteritems():
            self[{variable_name:key}] = val
        return self

    def p(self, **values):
        """ Get a probability.

        For example, if we are observing joint counts for values
        of x and y, you can get the probability as:
        
        >>> joint_prob_counter.p(x=1, y=2)

        this is P(x=1, y=2).

        If not all variables are specified, then the remaining
        variables are marginalized out.

        """
        return self.marginal_count(**values) / self.norm

    def logp(self, **values):
        """ Get a log probability. 

        For example, if we are observing joint counts for values
        of x and y, you can get the probability as:
        
        >>> joint_prob_counter.logp(x=1, y=2)

        this is logP(x=1, y=2).

        If not all variables are specified, then the remaining
        variables are summed out.
      
        """
        return log(self.marginal_count(**values)) - log(self.norm)


    def marginal_count(self, **values):
        """ Marginal count
        
        Get the sum count of the subset of joint variable values that
        matches the key.

        For example, if the counter has joint counts:
            (a=1, b=1):1, (a=1, b=2):1, (a=2, b=2):2
        and you do this:
            >>> joint_prob_counter.marginal_count(a=1)
        you will get 2, the total count of observations where a=1.

        """
        if len(values) < len(self.variables):
            return sum(count for vals, count in self.matching_items(values))
        else:
            return self[values]

    def condition_on_values(self, **condition):
        """ Condition on values

        Get the joint prob counter of observations that
        fulfill the condition.

        """
        new_variables = set(self.variables) - set(condition.iterkeys()) 
        conditioned_jpc = type(self)(new_variables)

        for values, count in self.matching_items(condition):
            values = {k:v for k,v in values.iteritems() if k not in condition}
            conditioned_jpc[values] = count

        return conditioned_jpc

    def condition_on_variables(self, *variables):
        """ Condition on variables

        Get a dict of ProbCounters representing a conditional distribution.

        """
        conditional_distro = NamedManyToOneDict()
        rest_variables = set(self.variables) - set(variables)

        for values, count in self.iteritems():
            given_values = {}
            rest_values = {}
            for variable, value in values.iteritems():
                (given_values if variable in variables else rest_values)[variable] = value

            if given_values not in conditional_distro:
                conditional_distro[given_values] = type(self)(rest_variables)
            conditional_distro[given_values][rest_values] = count

        return conditional_distro
        
    def marginalize_on(self, *variables):
        """ 
        f(x) = p(x) = sum_x sum_y p(x,y,z)
        f(x,y) = p(x,y) = sum_z p(x,y,z)

        """
        complement_variables = set(self.variables).difference(variables)
        return self.marginalize_out(*complement_variables)

    def marginalize_out(self, *variables):
        """
        f(x) = p(y,z) = sum_x p(x,y,z)

        """
        new_variables = set(self.variables) - set(variables)
        marginalized_jpc = type(self)(new_variables)
        for values, count in self.iteritems():
            values = {k:v for k,v in values.iteritems() if k not in variables}
            marginalized_jpc[values] += count
        return marginalized_jpc

    def observe(self, **key):
        """ Observe one object; increase the counter for it by one. """
        self[key] += 1


if __name__ == "__main__":
    # Tests

    njpc = NamedJointProbCounter(list("abc"))
    
    njpc[{'a':1, 'b':1, 'c':1}] = 1
    assert njpc[{'a':1, 'b':1, 'c':1}] == 1
    assert njpc.norm == 1
    assert njpc.p(a=1, b=1, c=1) == 1
    assert njpc.logp(a=1, b=1, c=1) == 0

    njpc[{'a':2, 'b':2, 'c':2}] = 2
    assert njpc[{'a':2, 'b':2, 'c':2}] == 2
    assert njpc.norm == 1 + 2
    assert njpc.p(a=2, b=2, c=2) == 2 / 3
    assert njpc.logp(a=2, b=2, c=2) == log(2) - log(3)

    njpc[{'a':3, 'b':3, 'c':3}] = 3
    assert njpc[{'a':3, 'b':3, 'c':3}] == 3
    assert njpc.norm == 1 + 2 + 3
    assert njpc.p(a=3, b=3, c=3) == 3 / (1 + 2 + 3)

    del njpc[{'a':3, 'b':3, 'c':3}]
    assert njpc[{'a':3, 'b':3, 'c':3}] == 0
    assert njpc.norm == 1 + 2
    assert njpc.p(a=3, b=3, c=3) == 0

    njpc.observe(a=4, b=4, c=4)
    assert njpc[{'a':4, 'b':4, 'c':4}] == 1
    assert njpc.norm == 1 + 2 + 1
    del njpc[{'a':4, 'b':4, 'c':4}]
    assert {'a':4, 'b':4, 'c':4} not in njpc
    assert njpc.norm == 1 + 2

    # test marginal counts
    assert njpc.p(a=1) == 1 / (1 + 2)
    assert njpc.p(b=2, c=2) == 2 / (1 + 2)
    assert njpc.p(c=3) == 0
    
    njpc.observe(a=1, b=2, c=3)
    assert njpc.p(a=1) == 2 / (1 + 2 + 1)

    marginal = njpc.marginalize_out("c")
    assert marginal[{"a":1, "b":1}] == 1
    assert marginal.p(a=1, b=1) == 1 / (1 + 2 + 1)
    assert njpc.p(a=1, b=1, c=1) == 1 / (1 + 2 + 1) # make sure unchanged
    assert marginal.norm == njpc.norm

    marginal = njpc.marginalize_on("a")
    assert marginal[{"a":1}] == 2 
    assert marginal.p(a=1) == 2 / (1 + 2 + 1)
    assert marginal.norm == njpc.norm

    conditional = njpc.condition_on_values(a=1)
    assert njpc.p(a=1, b=2, c=3) == 1 / (1 + 2 + 1) # make sure unchanged
    assert conditional[{"b":1, "c":1}] == 1
    assert conditional[{"b":2, "c":3}] == 1
    assert conditional.norm == 2
    assert conditional.p(b=1) == 1 / 2
    assert conditional.p(c=3) == 1 / 2
    
    conditional = njpc.condition_on_variables("a")
    assert njpc.p(a=1, b=1, c=1) == 1 / (1 + 2 + 1) # make sure unchanged
    assert conditional[{"a":1}].p(b=1) == 1 / 2
    assert conditional[{"a":2}].p(b=1) == 0
    assert conditional[{"a":2}].p(b=2) == 1
