from builtins import list, len, map, range, zip, str
from itertools import accumulate, product


class BayesianNetwork:
    # Represents Bayesian networks.

    def __init__(self, factors={}):
        self.__factors = factors
        self.variables = list(factors.keys())
        self.__varidx = list(map(lambda x: x+1, accumulate([0] + [len(self.values(var)) for var in self.variables])))

    def __startidx(self, variable):
        return self.__varidx[self.variables.index(variable)]

    def index(self, variable, value):
        return self.__startidx(variable) + self.values(variable).index(value)

    def maxidx(self):
        return self.__varidx[-1]

    def values(self, variable):
        return self.__factors.get(variable).possible_values

    def values_indices(self, variable):
        start = self.__startidx(variable)
        length = len(self.__factors.get(variable).possible_values)
        return zip([variable + "=" + str(v) for v in self.values(variable)], list(range(start, start + length)))

    def __probabilities(self, variable):
        return self.__factors.get(variable).probabilities

    def parents(self, variable):
        return self.__factors.get(variable).parents

    def combinations(self, variable):
        # Returns combinations of values of the given variable and its parents.
        #   together with the corresponding probability as a tuple : (tuple of values, probability).
        indices = [self.values_indices(parent) for parent in self.parents(variable)] + [self.values_indices(variable)]
        pi = 0 # index of probability
        for combo in product(*indices):
            yield (combo, self.__probabilities(variable)[pi])
            pi = pi + 1

    def is_leaf(self, variable):
        return self.__factors.get(variable).parents == []
