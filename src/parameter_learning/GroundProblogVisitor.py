from sys import exc_info
from six import reraise
from random import random
from parsimonious import NodeVisitor, VisitationError, UndefinedLabel
from GroundProblog import *


# noinspection PyAbstractClass,PyMethodMayBeStatic
class GroundProblogVisitor(NodeVisitor):
    """ A visitor for parse trees of ground Problog programs that builds a GroundProblog object. """
    def __init__(self, logging=False):
        self.logging = logging

    def print(self, *args):
        if self.logging:
            print(*args)

    def visit(self, node):
        """Walk a parse tree, transforming it into another representation."""
        # Do nothing for following expressions
        skip_nodes = ["_", "dot", "comma", "semicolon", "lparen", "rparen", "slash",
                      "doublecolon", "turnstile", "negation", "tunable", "tunable_empty"]
        if node.expr_name in skip_nodes:
            return

        method = getattr(self, 'visit_' + node.expr_name, self.generic_visit)

        # Call that method, and show where in the tree it failed if it blows up.
        try:
            return method(node, [self.visit(n) for n in node])
        except (VisitationError, UndefinedLabel):
            # Don't catch and re-wrap already-wrapped exceptions.
            raise
        except self.unwrapped_exceptions:
            raise
        except Exception:
            # Catch any exception, and tack on a parse tree so it's easier to
            # see where it went wrong.
            exc_class, exc, tb = exc_info()
            reraise(VisitationError, VisitationError(exc, exc_class, node), tb)

    def visit_program(self, node, visited_children):
        self.print("visit_program", map(str, visited_children))
        self.print('====================================================')
        return GroundProblog(visited_children[1])

    def visit_clauses(self, node, visited_children):
        self.print("visit_clauses", map(str, visited_children))
        return visited_children

    def visit_clause(self, node, visited_children):
        self.print("visit_clause", map(str, visited_children))
        return visited_children[0]

    def visit_predicate(self, node, visited_children):
        self.print("visit_predicate", map(str, visited_children))
        return visited_children[0]

    def visit_rule(self, node, visited_children):
        self.print("visit_rule", map(str, visited_children))
        return Rule(visited_children[0], visited_children[2])

    def visit_conjunction(self, node, visited_children):
        self.print("visit_conjunction", map(str, visited_children))
        if visited_children[1] is not None:
            return [visited_children[0]] + visited_children[1]
        else:
            return [visited_children[0]]

    def visit_conjunction_opt(self, node, visited_children):
        exists_conjunction = len(visited_children) != 0
        self.print("visit_conjunction_opt", visited_children, exists_conjunction)
        return visited_children[0] if exists_conjunction else None

    def visit_conjunction_more(self, node, visited_children):
        self.print("visit_conjunction_more", map(str, visited_children))
        return visited_children[1]

    def visit_prob_ann(self, node, visited_children):
        self.print("visit__prob_ann", map(str, visited_children))
        if len(visited_children[0]) == 1 and visited_children[1] is None:
            return visited_children[0][0]
        return ProbabilisticAnnotation(visited_children[0], visited_children[1])

    def visit_prob_ann_heads(self, node, visited_children):
        self.print("visit__prob_ann_heads", map(str, visited_children))
        if visited_children[1] is not None:
            return [visited_children[0]] + visited_children[1]
        else:
            return [visited_children[0]]

    def visit_prob_fact_opt(self, node, visited_children):
        exist_prob_facts = len(visited_children) != 0
        self.print("visit__prob_fact_opt", map(str, visited_children))
        return visited_children[0] if exist_prob_facts else None

    def visit_prob_fact_more(self, node, visited_children):
        self.print("visit__prob_fact_more", map(str, visited_children))
        return visited_children[1]

    def visit_prob_ann_rule_opt(self, node, visited_children):
        exists_rule = len(visited_children) != 0
        self.print("visit__prob_ann_rule_opt", map(str, visited_children))
        return visited_children[0] if exists_rule else None

    def visit_prob_ann_rule(self, node, visited_children):
        self.print("visit__prob_ann_rule", map(str, visited_children))
        return visited_children[1]

    def visit_prob_fact(self, node, visited_children):
        self.print("visit_prob_fact", map(str, visited_children))
        term = visited_children[2]
        term.is_tunable = visited_children[0]["tunable"]
        term.probability = visited_children[0]["probability"]
        return term

    def visit_rule_predicate(self, node, visited_children):
        self.print("visit_rule_predicate", map(str, visited_children))
        return visited_children[0]

    def visit_term(self, node, visited_children):
        self.print("visit_term", map(str, visited_children))
        return Term(visited_children[1], visited_children[0], visited_children[2])

    def visit_word_or_num(self, node, visited_children):
        self.print("visit_word_or_num", map(str, visited_children))
        return str(visited_children[0])

    def visit_negation_opt(self, node, visited_children):
        exists_negation = len(visited_children) != 0
        self.print("visit_negation_opt", visited_children, exists_negation)
        return exists_negation

    def visit_arguments_opt(self, node, visited_children):
        exist_arguments = len(visited_children) != 0
        self.print("visit_arguments_opt", visited_children, exist_arguments)
        return visited_children[0] if exist_arguments else None

    def visit_arguments(self, node, visited_children):
        self.print("visit_arguments", map(str, visited_children))
        return visited_children[1]

    def visit_arguments_list(self, node, visited_children):
        self.print("visit_arguments_list", map(str, visited_children))
        if visited_children[1] is not None:
            return [visited_children[0]] + visited_children[1]
        else:
            return [visited_children[0]]

    def visit_arguments_more_o(self, node, visited_children):
        exist_more_arguments = len(visited_children) != 0
        self.print("visit_arguments_more_o", visited_children, "more arguments exist: ", exist_more_arguments)
        return visited_children[0] if exist_more_arguments else None

    def visit_arguments_more(self, node, visited_children):
        self.print("visit_arguments_more", map(str, visited_children))
        return visited_children[1]

    def visit_probability(self, node, visited_children):
        self.print("visit_probability", map(str, visited_children))
        return visited_children[0]

    def visit_prob_num(self, node, visited_children):
        self.print("visit_prob_num", map(str, visited_children))
        return {"tunable": False, "probability": visited_children[0]}

    def visit_prob_tunable_num(self, node, visited_children):
        self.print("visit_prob_tunable_num", map(str, visited_children))
        return {"tunable": True, "probability": visited_children[3]}

    def visit_prob_tunable_none(self, node, visited_children):
        self.print("visit_prob_tunable_none", map(str, visited_children))
        return {"tunable": True, "probability": round(random(), 4)}

    def visit_decimal_or_frac(self, node, visited_children):
        self.print("vidit_decimal_or_frac", map(str, visited_children))
        return visited_children[0]

    def visit_fraction(self, node, visited_children):
        self.print("visit_fraction", visited_children[0], visited_children[2], " => ", float(visited_children[0]) / float(visited_children[2]))
        return float(visited_children[0]) / float(visited_children[2])

    def visit_word(self, node, visited_children):
        self.print("visit_word", node.full_text[node.start:node.end])
        return node.full_text[node.start:node.end]

    def visit_number(self, node, visited_children):
        self.print("visit_number", int(node.full_text[node.start:node.end]))
        return int(node.full_text[node.start:node.end])

    def visit_decimal(self, node, visited_children):
        self.print("visit_decimal", float(node.full_text[node.start:node.end]))
        return float(node.full_text[node.start:node.end])

    def visit_meaninglessness(self, nodes, visited_children):
        pass