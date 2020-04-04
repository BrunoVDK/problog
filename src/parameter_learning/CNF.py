import FOLTheory


class Literal:
    """ A literal of a CNF formula. """

    def __init__(self, name, negated=False, weight_true=1.0, weight_false=1.0, dimacs_assignment=None, tunable=False):
        self.name = name
        self.negated = negated
        self.weight_true = weight_true
        self.weight_false = weight_false
        self.dimacs_int = dimacs_assignment
        self.is_tunable = tunable

    def __str__(self):
        out = ""
        if self.weight_true != 1:
            if self.is_tunable:
                out += "t(" + str(self.weight_true) + ")::"
            else:
                out += str(self.weight_true) + "::"
        out += ("-" if self.negated else "") + self.name
        return out

    def __eq__(self, other):
        return self.name == other.name and self.negated == other.negated and \
               self.weight_true == other.weight_true and self.weight_false == other.weight_false

    @staticmethod
    def create_from_fol_formula(formula):
        if isinstance(formula, FOLTheory.Negation):
            name = str(formula.formula)
            negated = True
            w_true = formula.formula.weight_true
            w_false = formula.formula.weight_false
            is_tunable = formula.formula.is_tunable
        else:
            name = str(formula.str_no_weights())
            negated = False
            w_true = formula.weight_true
            w_false = formula.weight_false
            is_tunable = formula.is_tunable

        return Literal(name, negated, w_true, w_false, tunable=is_tunable)


class CNF:
    """ A formula in Conjunctive Normal Form with support for weights. """

    def __init__(self, literals=None, clauses=None, evidence=None, queries=None):
        # Dictionary of all the literals that are used in the clauses.
        self.literals = literals if literals is not None else {}
        # List of lists of Literal, which represents a conjunction of disjunctions of literals.
        self.clauses = clauses if clauses is not None else []
        # List of Literal.
        self.evidence = evidence if evidence is not None else []
        # List of Literal.
        self.queries = queries if queries is not None else []

    def __str__(self):
        out = "Literals ({}):\n\t".format(len(self.get_literals()))
        out += "\n\t".join(map(str, self.get_literals()))

        out += "\nClauses ({}):\n\t".format(len(self.clauses))
        out += "\n\t".join([" ∨ ".join(map(str, disjunction)) for disjunction in self.clauses])

        out += "\nEvidence ({}):\n\t".format(len(self.evidence))
        out += "\n\t".join(map(str, self.evidence))

        out += "\nQueries ({}):\n\t".format(len(self.queries))
        out += "\n\t".join(map(str, self.queries))

        return out

    def get_or_add_literal(self, lit):
        if not isinstance(lit, Literal):
            raise Exception("Adding literal of wrong type")

        if lit.name not in self.literals:
            dimacs_assignment = len(self.literals) + 1
            new_literal = Literal(lit.name, False, lit.weight_true, lit.weight_false, dimacs_assignment, lit.is_tunable)
            self.literals[lit.name] = new_literal
            return new_literal
        else:
            return self.literals[lit.name]

    def get_literals(self):
        return sorted(self.literals.values(), key=lambda lit: lit.dimacs_int)

    def get_tunable_literals_as_dict(self):
        return {l.name: l for l in self.get_literals() if l.is_tunable}

    def add_clause(self, clause):
        if not isinstance(clause, list):
            raise Exception("Adding clause of wrong type")

        for lit in clause:
            if not isinstance(lit, Literal):
                raise Exception("Adding clause with wrong type of literal")
            lit.dimacs_int = self.get_or_add_literal(lit).dimacs_int

        self.clauses.append(clause)
        return self

    def add_evidence(self, evidence):
        if not isinstance(evidence, Literal):
            raise Exception("Adding evidence of wrong type")

        evidence.dimacs_int = self.get_or_add_literal(evidence).dimacs_int
        self.evidence.append(evidence)
        return self

    def get_evidence(self):
        return self.evidence

    def set_literal_weights(self, literal_name, weight_true, weight_false):
        self.literals[literal_name].weight_true = weight_true
        self.literals[literal_name].weight_false = weight_false
        return self

    def get_evidence_with_dimacs_numbers(self):
        return [(lit, lit.dimacs_int) for lit in self.evidence]

    def add_query(self, query):
        if not isinstance(query, Literal):
            raise Exception("Adding query of wrong type")

        query.dimacs_int = self.get_or_add_literal(query).dimacs_int
        self.queries.append(query)
        return self

    def get_queries_with_dimacs_numbers(self):
        return [(lit, lit.dimacs_int) for lit in self.queries]

    def to_dimacs(self):
        """ Converts the CNF to a dimacs format that can be parsed by the minic2d package."""
        literals = self.get_literals()

        # Add a comment to check assignments of numbers to literals
        header = "p cnf {} {}\n".format(len(literals), len(self.clauses) + len(self.evidence))
        comment = "c ASSIGNMENTS: DIMACS_INT WEIGHT_TRUE WEIGHT_FALSE NAME\n"
        comment += "\n".join(
            ["c {:>2} {:.2f} {:.2f} {}".format(l.dimacs_int, float(l.weight_true), float(l.weight_false), l.name) for l
             in literals]) + "\n"
        comment += "c QUERIES: " + ", ".join([str(l.dimacs_int) for l in self.queries]) + "\n"

        weights = "c weights "
        weights += " ".join(["{} {}".format(l.weight_true, l.weight_false) for l in literals]) + "\n"

        dimacs = ""
        to_cachet = False
        if to_cachet:
            weights = ""
            dimacs = "\n".join(
                ["w {} {} {}".format(l.dimacs_int, l.weight_true, l.weight_false) for l in literals]) + "\n"

        for disjunction in self.clauses:
            disjunction_literals = ["{}{}".format("-" if l.negated else "", l.dimacs_int) for l in disjunction]
            dimacs += " ".join(disjunction_literals) + " 0"

            if disjunction != self.clauses[-1]:
                dimacs += "\n"

        dimacs += "\nc EVIDENCE:\n"
        dimacs += "\n".join(["{}{} 0".format("-" if l.negated else "", l.dimacs_int) for l in self.evidence])

        return weights + header + comment + dimacs

    @staticmethod
    def create_from_fol_theory(theory):
        cnf = CNF()
        theory = theory.to_cnf()

        # A formula in CNF consists of literals or of disjunctions of literals
        conjunction = theory.formulas[0]
        literals = [f for f in conjunction.formulas if isinstance(f, FOLTheory.Atom)]
        disjunctions = [f for f in conjunction.formulas if isinstance(f, FOLTheory.Disjunction)]

        # First go through literals so that all the declarations with weights are registered first in self.literals
        for formula in literals:
            cnf.get_or_add_literal(Literal.create_from_fol_formula(formula))

        for formula in disjunctions:
            clause = [Literal.create_from_fol_formula(f) for f in formula.formulas]
            cnf.add_clause(clause)

        for evidence in theory.get_evidence():
            cnf.add_evidence(Literal.create_from_fol_formula(evidence))

        for query in theory.get_queries():
            cnf.add_query(Literal.create_from_fol_formula(query))

        return cnf
