from builtins import list, range, len, str, map, zip

from factor import Factor
from network import BayesianNetwork

# A class representing encodings of Bayesian networks by logical formulae.
# Unreadable code, made quickly with the assumption in mind that it wouldn't be modified in the future.
class Encoding:

    def __init__(self, network, encoding="ENC1"):
        self.network = network
        self.weights = []
        self.dimacs = []
        self.latex = []
        self.maxidx = 0
        self.__init_indicator_clauses()
        self.latex = self.latex + ["---------- END OF INDICATOR CLAUSES ------------"]
        self.encoding = encoding
        if encoding == "ENC1":
            self.__init_ENC1()
        else:
            self.__init_ENC2()

    def __init_indicator_clauses(self):
        # Return the indicator clauses (Chavira, 2008, p. 778).
        for var in network.variables:
            values = network.values(var)
            start = network.index(var, values[0])
            indices = range(start, start + len(values))
            self.weights = self.weights + len(values) * [1.0]
            self.dimacs = self.dimacs + [" ".join(list(map(str, indices))) + " 0"]
            self.latex = self.latex + [" \lor ".join(["\lambda_{"+ var + "=" + v +"}" for v in values])]
            for i in indices:
                for j in range(i + 1, start + len(values)):
                    self.dimacs = self.dimacs + ["-" + str(i) + " -" + str(j) + " 0"]
                    self.latex = self.latex + ["\lnot\lambda_{" + var + "=" + values[indices.index(i)]
                                               + "} \lor \lnot\lambda_{" + var + "=" + values[indices.index(j)] + "}"]

    def __init_ENC1(self):
        # Return the parameter clauses for encoding 1 (Chavira, 2008, p. 779).
        # For every factor there's a parameter
        param_idx = network.maxidx() - 1
        for var in network.variables:
            if network.is_noisy(var):
                self.dimacs = self.dimacs + ["-" + str(network.index(var, "true")) + " " + " ".join([str(network.index(p, "true")) for p in network.parents(var)]) + " 0"]
                for p in network.parents(var):
                    self.dimacs = self.dimacs + [str(network.index(var, "true")) + " -" + str(network.index(p, "true")) + " 0"]
                self.latex = self.latex + ["\lambda_{" + var + "=true} \Leftrightarrow " + " \lor ".join(["\lambda_{" + p + "=true}" for p in network.parents(var)])]
            else:
                for combo in network.combinations(var):
                    param_idx = param_idx + 1
                    if network.is_leaf(var):
                        self.dimacs = self.dimacs + [str(param_idx) + " -" + str(combo[0][0][1]) + " 0"]
                        self.dimacs = self.dimacs + [str(combo[0][0][1]) + " -" + str(param_idx) + " 0"]
                        self.latex = self.latex + ["\lambda_{" + combo[0][0][0] + "}" +
                                                   " \Leftrightarrow \\theta_{" + combo[0][0][0] + "}"]
                    else:
                        self.dimacs = self.dimacs + [str(param_idx) + " " + " ".join(["-" + str(v[1]) for v in combo[0]]) + " 0"]
                        for v in combo[0]:
                            self.dimacs = self.dimacs + ["-" + str(param_idx) + " " + str(v[1]) + " 0"]
                        self.latex = self.latex + [" \land ".join(["\lambda_{" + str(v[0]) + "}" for v in combo[0]]) +
                                                   " \Leftrightarrow \\theta_{" + combo[0][-1][0] + "|" + " \land ".join([v[0] for v in combo[0][:-1]]) + "}"]
                    self.weights = self.weights + [combo[1]] # Probability
        self.maxidx = param_idx

    def __init_ENC2(self):
        # Return the parameter clauses for encoding 2.
        # Currently assumes boolean variables for sake of simplicity
        self.weights = self.weights * 2
        param_idx = network.maxidx() - 1
        for var in network.variables:
            if network.is_noisy(var):
                self.dimacs = self.dimacs + ["-" + str(network.index(var, "true")) + " " + " ".join([str(network.index(p, "true")) for p in network.parents(var)]) + " 0"]
                for p in network.parents(var):
                    self.dimacs = self.dimacs + [str(network.index(var, "true")) + " -" + str(network.index(p, "true")) + " 0"]
                self.latex = self.latex + ["\lambda_{" + var + "=true} \Leftrightarrow " + " \lor ".join(["\lambda_{" + p + "=true}" for p in network.parents(var)])]
            else:
                values = network.values(var)
                for combo in network.combinations(var, full=True):
                    # Firs the True one will be considered as a combo, then the False one
                    # Only one new parameter per True one
                    if combo[0][-1][0][1] == values[0]:
                        param_idx = param_idx + 1
                        out = " ".join(["-" + str(v[1]) for v in combo[0][:-1]]) + ("-" if network.is_leaf(var) else " -") + str(param_idx) + " " + str(combo[0][-1][1]) + " 0"
                        self.dimacs = self.dimacs + [out]
                        self.latex = self.latex + [" \land ".join(["\lambda_{" + v[0][2] + "}" for v in combo[0][:-1]])
                                                   + (" \land " if not network.is_leaf(var) else "")
                                                   + "\\rho_{" + var + "=true}" + " \Rightarrow " + "\lambda_{" + str(combo[0][-1][0][2]) + "}"]
                        # print(out)
                        # print(combo)
                        self.weights = self.weights + [combo[1]]  # Probability
                    else: # False
                        out = " ".join(["-" + str(v[1]) for v in combo[0][:-1]]) + ("" if network.is_leaf(var) else " ") + str(param_idx) + " " + str(combo[0][-1][1]) + " 0"
                        self.dimacs = self.dimacs + [out]
                        self.latex = self.latex + [" \land ".join(["\lambda_{" + v[0][2] + "}" for v in combo[0][:-1]])
                                                   + (" \land " if not network.is_leaf(var) else "")
                                                   + "\lnot\\rho_{" + var + "=true}" + " \Rightarrow " + "\lambda_{" + str(combo[0][-1][0][2]) + "}"]
                        # print(out)
                        # print(combo)
                        self.weights = self.weights + [combo[1]]  # Probability
        self.maxidx = param_idx

    def add_query(self, atom, value):
        self.dimacs = self.dimacs + [str(network.index(atom, value)) + " 0"]

    def print_dimacs(self):
        print("p cnf " + str(self.maxidx) + " " + str(len(self.dimacs)))
        self.print_weights()
        print("\n".join(self.dimacs))

    def print_latex(self):
        print("\\\\\n".join(self.latex))

    def print_weights(self):
        if self.encoding == "ENC1":
            print("c weights " + "".join([str(w) + " 1.0 " for w in self.weights]))
        else:
            print("c weights " + " ".join([str(w) for w in self.weights]))

# Bayesian network specification

factors = {
'stress(a)': Factor(probabilities=[0.2, 0.8]),
'stress(b)': Factor(probabilities=[0.2, 0.8]),
'stress(c)': Factor(probabilities=[0.2, 0.8]),
'aux1': Factor(parents=['stress(a)'], probabilities=[0.3, 0.7, 0.0, 1.0]),
'aux2': Factor(parents=['stress(b)'], probabilities=[0.3, 0.7, 0.0, 1.0]),
'aux3': Factor(parents=['stress(c)'], probabilities=[0.3, 0.7, 0.0, 1.0]),
'friends(a,b)': Factor(probabilities=[0.1, 0.9]),
'friends(a,c)': Factor(probabilities=[0.1, 0.9]),
'friends(b,c)': Factor(probabilities=[0.1, 0.9]),
'friends(c,b)': Factor(probabilities=[0.1, 0.9]),
'aux4': Factor(parents=['friends(b,c)', 'aux3'], probabilities=[0.4, 0.6, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]),
'aux5': Factor(parents=['friends(c,b)', 'aux2'], probabilities=[0.4, 0.6, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]),
'smokes(b)': Factor(parents=['aux4', 'aux2'], probabilities=[1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0], noisy=False),
'smokes(c)': Factor(parents=['aux5', 'aux3'], probabilities=[1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0], noisy=False),
'aux6': Factor(parents=['friends(a,b)', 'smokes(b)'], probabilities=[0.4, 0.6, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]),
'aux7': Factor(parents=['friends(a,c)', 'smokes(c)'], probabilities=[0.4, 0.6, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]),
'smokes(a)': Factor(parents=['aux1', 'aux6', 'aux7'],
                    probabilities=[1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0],
                    noisy=False),
}

network = BayesianNetwork(factors)

encoding = Encoding(network, encoding="ENC2")
encoding.add_query(atom="friends(a,b)", value="true")
encoding.add_query(atom="friends(a,c)", value="true")
encoding.add_query(atom="smokes(a)", value="true")
encoding.print_dimacs()

# Illustration of workings of LogicFormula from ProbLog

# formula = logic.LogicDAG()
# id1 = formula.add_atom("ok", 1.0)
# id2 = formula.add_atom("ak", 1.0)
# print(id1)
# print(formula.add_or([id1, id2]))
#
# id3 = formula.add_atom("weee", 1.0)
# id4 = formula.add_atom("waaa", 1.0)
# print(id3)
# print(formula.add_and([id3, id4]))
#
# d = CNF.create_from(formula).to_dimacs(weighted=False)
# print(d)