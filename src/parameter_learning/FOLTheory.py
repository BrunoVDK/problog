"""
A limited representation for First Order Logic theories with weighted atoms.

'Theories are collections of formulas. A formula is built out of atoms using universal and existential quantifiers
and the usual logical connectives negation, conjunction, disjunction, implication, equivalence.'
-- Inference in Probabilistic Logic Programs using Weighted CNF's
"""


class LogicFormula:
    """ Abstract class that represents a logical formula """

    def to_cnf(self):
        raise NotImplementedError


class Atom(LogicFormula):
    """ An atom is of the form p(t_1, ..., t_n) where p is a predicate of arity n and the t_i are terms. """

    def __init__(self, predicate, terms=None, weight_true=1, weight_false=1, is_tunable=False):
        self.predicate = predicate
        self.terms = terms if terms is not None else []
        self.arity = len(self.terms)
        self.weight_true = weight_true
        self.weight_false = weight_false
        self.is_tunable = is_tunable

    def __str__(self):
        out = ""
        if self.weight_true != 1:
            if self.is_tunable:
                out += "t(" + str(self.weight_true) + ")::"
            else:
                out += str(self.weight_true) + "::"
        out += self.str_no_weights()
        return out

    def str_no_weights(self):
        out = self.predicate
        if self.arity > 0:
            out += "(" + ", ".join(map(str, self.terms)) + ")"
        return out

    def __eq__(self, other):
        return isinstance(other, Atom) and self.predicate == other.predicate and self.terms == other.terms

    def to_cnf(self):
        return self

    @staticmethod
    def create_from_problog_term(term, weight_true, weight_false):
        predicate = term.name
        terms = [Atom.create_from_problog_term(arg, 1, 1) for arg in term.arguments] if len(term.arguments) else []

        atom = Atom(predicate, terms, weight_true, weight_false, term.is_tunable)

        return Negation(atom) if term.negation else atom


class Negation(LogicFormula):
    """ Represents the logical connective '¬'. """

    def __init__(self, formula):
        self.formula = formula

    def __str__(self):
        return "¬(" + str(self.formula) + ")"

    def __eq__(self, other):
        return isinstance(other, Negation) and self.formula == other.formula

    def to_cnf(self):
        """ Convert this formula to Conjunctive Normal Form. """
        # If formula is of form ¬(A) where A is an Atom, return A
        if isinstance(self.formula, Atom):
            return self

        # If formula is of form ¬(¬P), return P.to_cnf()
        elif isinstance(self.formula, Negation):
            return self.formula.formula.to_cnf()

        # If formula is of form ¬(P ∧ ... ∧ Q), return (¬P ∨ ... ∨ ¬Q).to_cnf() (de Morgan's Law)
        elif isinstance(self.formula, Conjunction):
            negated_subformulas = [Negation(f) for f in self.formula.formulas]
            return Disjunction(negated_subformulas).to_cnf()

        # If formula is of form ¬(P ∨ ... ∨ Q), return (¬P ∧ ... ∧ ¬Q).to_cnf() (de Morgan's Law)
        elif isinstance(self.formula, Disjunction):
            negated_subformulas = [Negation(f) for f in self.formula.formulas]
            return Conjunction(negated_subformulas).to_cnf()

        else:
            raise Exception("Unexpected formula type {}".format(type(self.formula)))


class Conjunction(LogicFormula):
    """ Represents the logical connective '∧'. """

    def __init__(self, formulas):
        self.formulas = []
        # Lift nested Conjunctions' formulas up into this one.
        for f in formulas:
            if isinstance(f, Conjunction):
                self.formulas += f.formulas
            else:
                self.formulas.append(f)

    def __str__(self):
        return "(" + " ∧ ".join(map(str, self.formulas)) + ")"

    def __eq__(self, other):
        if not isinstance(other, Conjunction):
            return False
        for f in self.formulas:
            if f not in other.formulas:
                return False
        for f in other.formulas:
            if f not in self.formulas:
                return False
        return True

    def to_cnf(self):
        """ Convert this formula to Conjunctive Normal Form. """
        if len(self.formulas) == 1:
            # If there is just one formula in the Conjunction, then return the CNF of that formula.
            return self.formulas[0].to_cnf()
        else:
            # Formula is of form (P ∧ ... ∧ Q)
            # P.to_cnf() must have the form P1 ∧ P2 ∧ ... ∧ Pm
            # Q.to_cnf() must have the form Q1 ∧ Q2 ∧ ... ∧ Qn
            # where all Pi and Qi are disjunctions of literals. => return P1 ∧ ... ∧ Pm ∧ Q1 ∧ ... ∧ Qm
            return Conjunction([f.to_cnf() for f in self.formulas])  # (P.to_cnf() ∧ ... ∧ Q.to_cnf())


class Disjunction(LogicFormula):
    """ Represents the logical connective '∨'. """

    def __init__(self, formulas):
        self.formulas = []
        # Lift nested Disjunction' formulas up into this one.
        for f in formulas:
            if isinstance(f, Disjunction):
                self.formulas += f.formulas
            else:
                self.formulas.append(f)

    def __str__(self):
        return "(" + " ∨ ".join(map(str, self.formulas)) + ")"

    def __eq__(self, other):
        if not isinstance(other, Disjunction):
            return False
        for f in self.formulas:
            if f not in other.formulas:
                return False
        for f in other.formulas:
            if f not in self.formulas:
                return False
        return True

    def to_cnf(self):
        """ Convert this formula to Conjunctive Normal Form. """
        if len(self.formulas) == 1:
            # If there is just one formula in the Disjunction, then return the CNF of that formula.
            return self.formulas[0].to_cnf()
        else:
            # Formula is of form (P ∨ ... ∨ Q)
            # P.to_cnf() must have the form P1 ∧ P2 ∧ ... ∧ Pm
            # Q.to_cnf() must have the form Q1 ∧ Q2 ∧ ... ∧ Qn
            # where all Pi and Qi are disjunctions of literals
            # We need a CNF formula equivalent to (P1 ∧ P2 ∧ ... ∧ Pm) ∨ (Q1 ∧ Q2 ∧ ... ∧ Qn)
            # => return (P1 ∨ Q1) ∧ (P1 ∨ Q2) ∧ ... ∧ (P1 ∨ Qn)
            #         ∧ (P2 ∨ Q1) ∧ (P2 ∨ Q2) ∧ ... ∧ (P2 ∨ Qn)
            #         ∧ ...
            #         ∧ (Pm ∨ Q1) ∧ (Pm ∨ Q1) ∧ ... ∧ (Pm ∨ Qn)
            # In other words, apply the distributive law where a disjunction occurs over a conjunction.
            formulas_cnf = [f.to_cnf() for f in self.formulas]

            if len([f for f in formulas_cnf if isinstance(f, Conjunction)]) == 0:
                # If there is no Conjunction in this Disjunction, the formula is already in CNF
                return Disjunction(formulas_cnf)

            # Build up the result as a Conjunction of Disjunctions
            result = Conjunction([formulas_cnf.pop(0)])
            while len(formulas_cnf) > 0:
                f = formulas_cnf.pop(0)
                f_formulas = [f] if isinstance(f, (Atom, Negation)) else f.formulas

                disjunctions = []
                for p in result.formulas:
                    for q in f_formulas:
                        disjunctions.append(Disjunction([p, q]))

                result = Conjunction(disjunctions)

            return result.to_cnf()


class Equivalence(LogicFormula):
    """ Represents the logical connective '↔'. E.g. "w ↔ r ∨ s" """

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "(" + str(self.lhs) + " ↔ " + str(self.rhs) + ")"

    def __eq__(self, other):
        return isinstance(other, Equivalence) and \
               (self.lhs == other.lhs and self.rhs == other.rhs or self.lhs == other.rhs and self.rhs == other.lhs)

    def to_cnf(self):
        """ Convert this formula to Conjunctive Normal Form. """
        # Formula is of form P ↔ Q
        a = Disjunction([self.lhs, Negation(self.rhs)])  # (P ∨ ¬Q)
        b = Disjunction([Negation(self.lhs), self.rhs])  # (¬P ∨ Q)
        return Conjunction([a, b]).to_cnf()              # ((P ∨ ¬Q) ∧ (¬P ∨ Q)).to_cnf()


class FOLTheory:
    """
    A FOL theory is a set of formulas that implicitly form a conjunction.
    """

    def __init__(self, formulas=None, evidence=None, queries=None):
        self.formulas = formulas if formulas is not None else []
        self.evidence = evidence if evidence is not None else []
        self.queries = queries if queries is not None else []

    def __str__(self):
        out = "Formulas ({}):\n\t".format(len(self.formulas))
        out += "\n\t".join(map(str, self.formulas))

        out += "\nEvidence ({}):\n\t".format(len(self.evidence))
        out += "\n\t".join(map(str, self.evidence))

        out += "\nQueries ({}):\n\t".format(len(self.queries))
        out += "\n\t".join(map(str, self.queries))

        return out

    def add_formula(self, formula):
        if not isinstance(formula, LogicFormula):
            raise Exception("Adding formula of wrong type")

        self.formulas.append(formula)
        return self

    def get_formulas(self):
        return self.formulas

    def add_evidence(self, evidence):
        if not isinstance(evidence, LogicFormula):
            raise Exception("Adding evidence of wrong type")

        self.evidence.append(evidence)
        return self

    def get_evidence(self):
        return self.evidence

    def add_query(self, query):
        if not isinstance(query, LogicFormula):
            raise Exception("Adding query of wrong type")

        self.queries.append(query)
        return self

    def add_query_from_problog_term(self, term):
        self.add_query(Atom.create_from_problog_term(term, 1, 1))
        return self

    def get_queries(self):
        return self.queries

    def delete_queries(self):
        self.queries = []
        return self

    def to_cnf(self):
        cnf = Conjunction([f.to_cnf() for f in self.formulas])

        for formula in cnf.formulas:
            # A formula in CNF consists of literals or of disjunctions of literals
            if not isinstance(formula, Atom) and not isinstance(formula, Disjunction):
                raise Exception("Unexpected formula type in FOL CNF: {}\n{}\nCNF:\n{}\n"
                                .format(type(formula), str(cnf), str(cnf)))

            if isinstance(formula, Disjunction):
                for f in formula.formulas:
                    if isinstance(f, Conjunction):
                        raise Exception("Unexpected Conjunction inside CNF Disjunction: {}\nCNF:\n{}\n"
                                        .format(str(formula), str(cnf)))

        return FOLTheory(formulas=[Conjunction([cnf])], evidence=self.evidence, queries=self.queries)

    def get_atoms(self):
        return [f for f in self.formulas if isinstance(f, Atom)]

    def get_conjunctions(self):
        return [f for f in self.formulas if isinstance(f, Conjunction)]

    @staticmethod
    def create_from_problog(ground_problog):
        """ Creates a FOLTheory from a GroundProblog instance. """
        ground_problog = ground_problog.convert_ads_with_body_to_rules()
        ground_problog = ground_problog.remove_duplicate_probabilistic_terms()
        theory = FOLTheory()

        # Problog facts can just be converted to FOL Atoms
        for fact in ground_problog.get_facts():
            theory.add_formula(Atom.create_from_problog_term(fact, fact.probability, 1-fact.probability))

        for evidence in ground_problog.get_evidence():
            # print(Atom.create_from_problog_term(evidence, 1, 1))
            theory.add_evidence(Atom.create_from_problog_term(evidence, 1, 1))

        for query in ground_problog.get_queries():
            theory.add_query(Atom.create_from_problog_term(query, 1, 1))

        # Problog rules are converted to FOL formulas by applying Clark's completion. This is done by grouping rule
        # bodies of rules with equal heads into disjunctions.
        rules = []  # a list of (head, body) tuples
        for rule in ground_problog.get_rules():
            # Create the corresponding head and body as FOL formulas.
            head = Atom.create_from_problog_term(rule.head, 1, 1)
            body_atoms = [Atom.create_from_problog_term(term, 1, 1) for term in rule.body]
            body = Conjunction(body_atoms) if len(body_atoms) > 1 else body_atoms[0]

            # Add the rule in the rules list. If the rule already exists, extend the disjunction of its body.
            i = next((i for (i, (h, b)) in enumerate(rules) if h == head), -1)
            if i == -1:
                rules.append((head, body))
            else:
                rules[i] = (rules[i][0], Disjunction([rules[i][1], body]))

        for (head, body) in rules:
            theory.add_formula(Equivalence(head, body))

        # add constraints that make sure only one fact in probabilistic annotations can be true
        for annotation in ground_problog.get_probabilistic_annotations():
            atoms = []

            # create a new predicate for the case where all heads of the annotated disjunction are false
            new_predicate = "none_of"
            weight_sum = 0
            for head in annotation.heads:
                new_predicate += "_" + head.str_no_prob()
                weight_sum += head.probability

                # add atom with correct weight to FOL Theory
                theory.add_formula(Atom.create_from_problog_term(head, weight_true=head.probability, weight_false=1))
                # add atom to local list with weights 1, 1
                atoms.append(Atom.create_from_problog_term(head, weight_true=1, weight_false=1))

            if len(annotation.heads) > 1 and weight_sum < 1:
                theory.add_formula(Atom(predicate=new_predicate, terms=None, weight_true=1-weight_sum, weight_false=1))
                atoms.append(Atom(predicate=new_predicate, terms=None, weight_true=1, weight_false=1))

            # create constraints that make sure only one of the values can be true
            # e.g. 0.1::a; 0.2::b; 0.3::c => (¬a ∨ ¬b) ∧ (¬a ∨ ¬c) ∧ (¬b ∨ ¬c) ∧ (a ∨ b v c ∨ none_of_a_b_c)
            for i in range(len(atoms)):
                for j in range(i+1, len(atoms)):
                    theory.add_formula(Disjunction([Negation(atoms[i]), Negation(atoms[j])]))
            theory.add_formula(Disjunction(atoms))

        return theory
