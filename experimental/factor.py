from builtins import len, ValueError

# Class representing conditional probability tables in Bayesian networks.
class Factor:

    def __init__(self, parents=[], possible_values=["true","false"], probabilities=[1.0, 0.0], noisy=False):
        self.parents = parents
        self.possible_values = possible_values
        self.noisy = noisy
        if len(probabilities) != len(possible_values) * (2**len(parents)):
            raise ValueError("Invalid number of probabilities.")
        self.probabilities = probabilities

    def nb_values(self):
        return len(self.possible_values)