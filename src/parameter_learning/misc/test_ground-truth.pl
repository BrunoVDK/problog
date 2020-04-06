0.2::stress(a).
0.2::stress(b).
0.2::stress(c).

0.1::friends(a,b).
0.1::friends(a,c).
0.1::friends(b,a).
0.1::friends(b,c).
0.1::friends(c,a).
0.1::friends(c,b).


smokes(X) :- stress(X).
smokes(X) :- friends(X,Y), smokes(Y).

query(stress(a)).
query(stress(b)).
query(stress(c)).
query(smokes(a)).
query(smokes(b)).
query(smokes(c)).


