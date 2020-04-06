person(a). person(b). person(c).

0.2::stress(a).
0.2::stress(b).
0.2::stress(c).

t(0.5)::friends(a,b).
t(0.5)::friends(a,c).
t(0.5)::friends(b,a).
t(0.5)::friends(b,c).
t(0.5)::friends(c,a).
t(0.5)::friends(c,b).


smokes(X) :- stress(X).
smokes(X) :- friends(X,Y), smokes(Y).

query(stress(a)).
query(stress(b)).
query(stress(c)).
query(smokes(a)).
query(smokes(b)).
query(smokes(c)).


