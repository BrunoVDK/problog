from problog.program import PrologString, LogicProgram
from problog.formula import LogicFormula, LogicDAG
from problog.logic import Term
from problog.ddnnf_formula import DDNNF
from problog.cnf_formula import CNF

# p = PrologString("""
# 0.2::a.
# 0.4::b.
# 0.3::a :- b.
# 0.5::b :- a.
# query(a).
# evidence(b).
# """)

p = PrologString("""
0.4::heads(1). 0.7::heads(2). 0.5::heads(3). 
win :- heads(1). 
win :- heads(2), heads(3).
query(win).
""")

lf = LogicFormula.create_from(p, avoid_name_clash=True, keep_order=True, label_all=True)   # ground the program
# print(lf)
# print(LogicFormula.to_prolog(lf))
dag = LogicDAG.create_from(lf, avoid_name_clash=True, keep_order=True, label_all=True)     # break cycles in the ground program
# print(dag)
# print(LogicFormula.to_prolog(dag))
cnf = CNF.create_from(dag)         # convert to CNF
# for clause in cnf._clauses:
#     print(clause)
ddnnf = DDNNF.create_from(cnf)       # compile CNF to ddnnf
# Outcome for the a/b thing with query(a) is 0,2+(0,8*0,3*0,4)
#  but if evidence(b) : (0,2*0,4+0,2*0,5*0,6+0,4*0,3*0,8) / (0,4+0,6*0,5*0,2) [Formula for conditional probability P(a|b) = ...]
# For coin thing : 1-0,6*0,3*0,5-0,6*0,3*0,5-0,6*0,7*0,5 = 0,61
# print(ddnnf.evaluate())

#
# ASSIGNMENT
#

p2 = PrologString("""
person(a). 
person(b). 
person(c). 
0.2::stress(X) :- person(X). 
0.1::friends(X,Y) :- person(X), person(Y). 
0.3::smokes(X) :- stress(X). 
0.4::smokes(X) :- friends(X,Y), smokes(Y). 
query(smokes(a)).
""")
lf2 = LogicFormula.create_from(p2, avoid_name_clash=True, keep_order=True, label_all=True)
# print(LogicFormula.to_prolog(lf2))
dag2 = LogicDAG.create_from(lf2, avoid_name_clash=True, keep_order=True, label_all=True)
print(dag2)
print(LogicFormula.to_prolog(dag2))
cnf2 = CNF.create_from(dag2)
# for clause in cnf2._clauses:
#     print(clause)
ddnnf2 = DDNNF.create_from(cnf2)
print(ddnnf2.evaluate())

import PyBool_public_interface as Bool

expr = Bool.parse_std("input.txt")
expr = expr["main_expr"]
expr = Bool.exp_cnf(expr)
print(Bool.print_expr(Bool.simplify(expr)))