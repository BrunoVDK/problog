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

# lf = LogicFormula.create_from(p, avoid_name_clash=True, keep_order=True, label_all=True)   # ground the program
# # print(lf)
# # print(LogicFormula.to_prolog(lf))
# dag = LogicDAG.create_from(lf, avoid_name_clash=True, keep_order=True, label_all=True)     # break cycles in the ground program
# # print(dag)
# # print(LogicFormula.to_prolog(dag))
# cnf = CNF.create_from(dag)         # convert to CNF
# # for clause in cnf._clauses:
# #     print(clause)
# ddnnf = DDNNF.create_from(cnf)       # compile CNF to ddnnf
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
evidence(friends(a,b), true).
evidence(friends(a,c), true).
query(smokes(a)).
""")
lf2 = LogicFormula.create_from(p2, avoid_name_clash=True, keep_order=True, label_all=True)
# print(LogicFormula.to_prolog(lf2))
dag2 = LogicDAG.create_from(lf2, avoid_name_clash=False, keep_order=True, label_all=True)



# # print(dag2)
# # print(LogicFormula.to_prolog(dag2))
cnf2 = CNF.create_from(dag2)
# # print(cnf2.to_dimacs(weighted=True, invert_weights=True))
ddnnf2 = DDNNF.create_from(cnf2)
#print(ddnnf2.evaluate())
#
# import PyBool_public_interface as Bool
# expr = Bool.parse_std("input.txt")
# expr = expr["main_expr"]
# expr = Bool.exp_cnf(expr)
# expr = Bool.simplify(expr)
# print(Bool.print_expr(expr))
# Bool.write_dimacs(Bool.cnf_list(expr), "/Users/Bruno/Desktop/dimacs.cnf")

# p3 = PrologString("""
# 0.2::stress(a).
# 0.2::stress(b).
# 0.2::stress(c).
#
# 0.1::friends(a,b).
# 0.1::friends(a,c).
# 0.1::friends(b,c).
# 0.1::friends(c,b).
#
# 0.3::p(a).
# 0.3::p(b).
# 0.3::p(c).
#
# 0.4::p(a,b).
# 0.4::p(a,c).
# 0.4::p(b,c).
# 0.4::p(c,b).
#
# smokes(a) :- stress(a), p(a).
# smokes(b) :- stress(b), p(b).
# smokes(c) :- stress(c), p(c).
#
# smokes(a) :-
#     friends(a,b), smokes(b), p(a,b).
# smokes(a) :-
#     friends(a,c), smokes(c), p(a,c).
# smokes(b) :-
#     friends(b,c), stress(c), p(c), p(b,c).
# smokes(c) :-
#     friends(c,b), stress(b), p(b), p(c,b).
#
# query(smokes(a)).
# """)
p3 = PrologString("""
person(a). 
person(b). 
person(c). 
0.2::stress(X) :- person(X). 
0.1::friends(X,Y) :- person(X), person(Y). 
0.3::smokes(X) :- stress(X). 
0.4::smokes(X) :- friends(X,Y), smokes(Y).
evidence(friends(a,b), true).
evidence(friends(a,c), true).
query(smokes(a)).
""")
lf3 = LogicFormula.create_from(p3, avoid_name_clash=True, keep_order=True, label_all=True)
# print(LogicFormula.to_prolog(lf2))
dag3 = LogicDAG.create_from(lf3, avoid_name_clash=False, keep_order=True, label_all=True)

# print(LogicDAG.to_prolog(dag3))

import problog.tasks.bayesnet
bn = problog.tasks.bayesnet.formula_to_bn(dag3)
# print(bn.to_graphviz())

cnf3 = CNF.create_from(dag3)
# print(cnf3.to_dimacs(weighted=True, invert_weights=False, names=True))
ddnnf3 = DDNNF.create_from(cnf3)
print(ddnnf3.evaluate())
# 0,10559646720000002