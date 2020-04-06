"""
This file defines classes that are used to build GroundProblog instances that represent ground problog programs.
"""


class Clause:
    """ Abstract class that represents a clause? """


class Term(Clause):
    """ A term has a name, can be negated, and possibly has arguments. """
    def __init__(self, name, negation=False, arguments=None, probability=1.0, is_tunable=False):
        self.name = name
        self.negation = negation
        self.arguments = arguments if arguments is not None else []
        self.probability = probability
        self.is_tunable = is_tunable

    def __str__(self):
        out = ""
        if self.probability != 1.0:
            if self.is_tunable:
                out += "t(" + str(self.probability) + ")::"
            else:
                out += str(self.probability) + "::"
        out += self.str_no_prob()
        return out

    def str_no_prob(self):
        out = ("\+" if self.negation else "") + self.name
        if len(self.arguments):
            out += "(" + ",".join(map(str, self.arguments)) + ")"
        return out


class Rule(Clause):
    """ A rule has a head and a body.
    The head is a term. The body can only be a term or a conjunction of terms in the case of ground problog.
    """
    def __init__(self, head, body):
        self.head = head
        self.body = body

    def __str__(self):
        out = str(self.head) + " :- " + ", ".join(map(str, self.body))
        return out


class ProbabilisticAnnotation(Clause):
    """ A collection of probabilistic heads (terms) with optionally a rule body. """
    def __init__(self, heads, body=None):
        self.heads = heads
        self.body = body if body is not None else []

    def __str__(self):
        out = "; ".join(map(str, self.heads))
        if len(self.body):
            out += " :- " + ", ".join(map(str, self.body))
        return out


class GroundProblog:
    """ A ground problog program is a collection of clauses.
    A clause can be a fact (represented by just a Term here), a  Rule, or a ProbabilityPredicate.
    """
    def __init__(self, clauses):
        self.clauses = clauses

    def __str__(self):
        return ".\n".join(map(str, self.clauses)) + "."

    def get_facts(self):
        return [c for c in self.clauses if isinstance(c, Term) and c.name != "query" and c.name != "evidence"]

    def get_tunable_probabilities(self):
        return [c for c in self.clauses if isinstance(c, Term) and c.is_tunable]

    def get_tunable_probabilities_as_dict(self):
        probs = [c for c in self.clauses if isinstance(c, Term) and c.is_tunable]
        return {c.str_no_prob(): c.probability for c in probs}

    def get_queries(self):
        return [c.arguments[0] for c in self.clauses if isinstance(c, Term) and c.name == "query"]

    def get_evidence(self):
        return [c.arguments[0] for c in self.clauses if isinstance(c, Term) and c.name == "evidence"]

    def get_rules(self):
        return [c for c in self.clauses if isinstance(c, Rule)]

    def get_probabilistic_annotations(self):
        return [c for c in self.clauses if isinstance(c, ProbabilisticAnnotation)]

    def convert_ads_with_body_to_rules(self):
        """ Converts annotated disjunctions with rule bodies to normal rules.
        This is done by pulling the probabilities out to new probabilistic facts. A new normal rule is then created for
        each of the heads. Each new rule contains the new probabilistic fact that was created for its head.
        The new probabilistic facts are then added in a new annotated disjunction without rule body, to keep the
        constraint that only one of the new rules can be true.
        """
        new_clauses = []
        head_counts = {}

        for clause in self.clauses:
            if not isinstance(clause, ProbabilisticAnnotation):
                new_clauses.append(clause)

            else:
                if len(clause.body):
                    for head in clause.heads:
                        if head.str_no_prob() not in head_counts:
                            head_counts[head.str_no_prob()] = 0
                        else:
                            head_counts[head.str_no_prob()] += 1
                        new_prob_fact_name = "p_{}_{}".format(head.str_no_prob(), head_counts[head.str_no_prob()])

                        # Create the new probabilistic fact that hold the probability of the current head
                        new_prob_fact = Term(new_prob_fact_name, probability=head.probability, is_tunable=head.is_tunable)
                        new_clauses.append(new_prob_fact)

                        # Create a new head with no weights for the new normal rule
                        new_head_wo_prob = Term(head.name, arguments=head.arguments)
                        new_rule = Rule(new_head_wo_prob, clause.body + [new_prob_fact])
                        new_clauses.append(new_rule)
                else:
                    new_clauses.append(clause)

        return GroundProblog(new_clauses)

    def remove_duplicate_probabilistic_terms(self):
        """ Eliminates probabilistic facts and probabilistic annotations with the same names.
        E.g.    "0.1::a.   0.2::a.   0.3::a :- b."
        becomes "0.1::a_0. 0.2::a_1. 0.3::a_2 :- b.  a :- a_0.  a :- a_1.  a :- a_2."
        """
        new_clauses = self.clauses
        new_rules = []
        name_counts = {}
        name_probability = {}

        # count the amount of times different names occur
        for clause in new_clauses:
            if isinstance(clause, Term) and clause.probability != 1:
                name = clause.str_no_prob()
                name_probability[name] = True
                name_counts[name] = 0 if name not in name_counts else name_counts[name] + 1

            elif isinstance(clause, Rule):
                name = clause.head.str_no_prob()
                name_counts[name] = 0 if name not in name_counts else name_counts[name] + 1

            elif isinstance(clause, ProbabilisticAnnotation):
                for head in clause.heads:
                    name = head.str_no_prob()
                    name_probability[name] = True
                    name_counts[name] = 0 if name not in name_counts else name_counts[name] + 1

        # rename duplicate elements and create the new rules
        counts_copy = {}.fromkeys(name_counts, 0)
        for clause in new_clauses:
            if isinstance(clause, Term) and clause.probability != 1:
                name = clause.str_no_prob()

                if name_counts[name] > 0:
                    clause.name += "_" + str(counts_copy[name])
                    counts_copy[name] += 1
                    new_rules.append(Rule(Term(name), [clause]))

            elif isinstance(clause, Rule):
                name = clause.head.str_no_prob()

                if name in name_probability and name_probability[name] and name_counts[name] > 0:
                    clause.head.name += "_" + str(counts_copy[name])
                    counts_copy[name] += 1
                    new_rules.append(Rule(Term(name), [clause.head]))

            elif isinstance(clause, ProbabilisticAnnotation):
                for head in clause.heads:
                    name = head.str_no_prob()

                    if name_counts[name] > 0:
                        head.name += "_" + str(counts_copy[name])
                        counts_copy[name] += 1
                        new_rules.append(Rule(Term(name), [head]))

        new_clauses += new_rules
        return GroundProblog(new_clauses)
