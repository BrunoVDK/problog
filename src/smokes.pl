person(a). 
person(b). 
person(c). 
0.2::stress(X) :- person(X). 
0.1::friends(X,Y) :- person(X), person(Y). 
0.3::smokes(X) :- stress(X). 
0.4::smokes(X) :- friends(X,Y), smokes(Y). 
query(smokes(a)).