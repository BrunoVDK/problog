"""
A parser for ground ProbLog programs.
"""

from parsimonious.grammar import Grammar
from GroundProblogVisitor import GroundProblogVisitor


class GroundProblogParser:
    def __init__(self):
        self._visitor = GroundProblogVisitor(logging=False)

    def _grammar(self):
        # A PEG grammar for ground Problog. It is written in a very weird way
        # in order to make the visiting of the parse tree work.
        return Grammar(r"""
            program           = _ clauses
            clauses           = clause*
            clause            = predicate dot
            predicate         = prob_ann / rule / term

            rule              = term turnstile conjunction
            conjunction       = term conjunction_opt
            conjunction_opt   = conjunction_more?
            conjunction_more  = comma conjunction

            prob_ann          = prob_ann_heads prob_ann_rule_opt
            prob_ann_heads    = prob_fact prob_fact_opt
            prob_fact_opt     = prob_fact_more?
            prob_fact_more    = semicolon prob_ann_heads
            prob_ann_rule_opt = prob_ann_rule?
            prob_ann_rule     = turnstile conjunction
            prob_fact         = probability doublecolon term

            term              = negation_opt word_or_num arguments_opt
            word_or_num       = decimal_or_frac / word
            negation_opt      = negation?
            arguments_opt     = arguments?
            arguments         = lparen arguments_list rparen
            arguments_list    = term arguments_more_o
            arguments_more_o  = arguments_more?
            arguments_more    = comma arguments_list

            probability       = prob_num / prob_tunable_num / prob_tunable_none
            prob_num          = decimal_or_frac _
            prob_tunable_num  = _ tunable lparen decimal_or_frac rparen _
            prob_tunable_none = _ tunable_empty _
            decimal_or_frac   = decimal / fraction
            fraction          = number slash number
            # could to this in a better way, but this works and we are way over time already
            word              = ~r"([a-zA-Z0-9_\[\]]+|\"[a-zA-Z0-9_\-\'\.\/\=\<\>\+\[\]]*\"|\'[a-zA-Z0-9_\-\'\.\/\=\<\>\+\[\]]*\')"
            number            = ~r"[0-9]*"
            decimal           = ~r"[0-9]*\.[0-9]*"
            dot               = _ "." _
            comma             = _ "," _
            semicolon         = _ ";" _
            lparen            = _ "(" _
            rparen            = _ ")" _
            slash             = _ "/" _
            doublecolon       = _ "::" _
            turnstile         = _ ":-" _
            negation          = _ ~r"\\\+" _
            tunable           = _ "t" _
            tunable_empty     = "t(_)"

            _                 = meaninglessness*
            meaninglessness   = ~r"\s+"
        """)

    def parse(self, program):
        """ Parses a ground problog program and returns the root node of the parse tree. """
        return self._grammar().parse(program)

    def parse_tree_to_problog(self, root_node):
        """ Visits a ground problog program's parse tree and
        returns a GroundProblog object that represents the program. """
        return self._visitor.visit(root_node)

    def program_to_problog(self, program):
        """ Takes a ground problog program and returns a GroundProblog object that represents the program. """
        return self.parse_tree_to_problog(self.parse(program))
