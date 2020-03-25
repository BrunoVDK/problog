from builtins import len, ValueError

# Class representing conditional probability tables in Bayesian networks.
class Factor:

    def __init__(self, parents=[], possible_values=["true","false"], probabilities=[1.0, 0.0]):
        self.parents = parents
        self.possible_values = possible_values
        if len(probabilities) != len(possible_values) * (2**len(parents)):
            raise ValueError("Invalid number of probabilities.")
        self.probabilities = probabilities

    def nb_values(self):
        return len(self.possible_values)