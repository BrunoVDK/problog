person(a). person(b). person(c).

0.2::stress(a).
0.2::stress(b).
0.2::stress(c).

t(_)::friends(a,b).
t(_)::friends(a,c).
t(_)::friends(b,a).
t(_)::friends(b,c).
t(_)::friends(c,a).
t(_)::friends(c,b).


smokes(X) :- stress(X).
smokes(X) :- friends(X,Y), smokes(Y).

query(stress(a)).
query(stress(b)).
query(stress(c)).
query(smokes(a)).
query(smokes(b)).
query(smokes(c)).


