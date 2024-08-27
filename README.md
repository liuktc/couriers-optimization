# couriers-optimization


## Status
<!-- Do NOT remove the comments below -->
<!-- begin-status -->
| Instance | [CP](./method-statuses/cp-status.md) | [SAT](./method-statuses/sat-status.md) | [SMT](./method-statuses/smt-status.md) | [MILP](./method-statuses/milp-status.md) |
|:-:| :---:|:---:|:---:|:---:|
| $1$ | $\color{green}\text{0 s (obj: 14)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{0 s (obj: 14)}$</br>$\color{green}\text{smt2-plain-linear-z3}$ | $\color{red}\text{Inconsistent}$ | 
| $2$ | $\color{green}\text{0 s (obj: 226)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{1 s (obj: 226)}$</br>$\color{green}\text{plain-symm}$ | $\color{red}\text{Inconsistent}$ | 
| $3$ | $\color{green}\text{0 s (obj: 12)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{0 s (obj: 12)}$</br>$\color{green}\text{smt2-plain-linear-z3}$ | $\color{red}\text{Inconsistent}$ | 
| $4$ | $\color{green}\text{0 s (obj: 220)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{1 s (obj: 220)}$</br>$\color{green}\text{plain-symm}$ | $\color{red}\text{Inconsistent}$ | 
| $5$ | $\color{green}\text{0 s (obj: 206)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{0 s (obj: 206)}$</br>$\color{green}\text{smt2-plain-linear-z3}$ | $\color{red}\text{Inconsistent}$ | 
| $6$ | $\color{green}\text{0 s (obj: 322)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{0 s (obj: 322)}$</br>$\color{green}\text{smt2-plain-linear-z3}$ | $\color{red}\text{Inconsistent}$ | 
| $7$ | $\color{green}\text{0 s (obj: 167)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{291 s (obj: 167)}$</br>$\color{green}\text{smt2-plain-linear-yices2}$ | $\color{red}\text{Inconsistent}$ | 
| $8$ | $\color{green}\text{0 s (obj: 186)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{1 s (obj: 186)}$</br>$\color{green}\text{plain}$ | $\color{red}\text{Inconsistent}$ | 
| $9$ | $\color{green}\text{0 s (obj: 436)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{1 s (obj: 436)}$</br>$\color{green}\text{plain-impl}$ | $\color{red}\text{Inconsistent}$ | 
| $10$ | $\color{green}\text{0 s (obj: 244)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{green}\text{1 s (obj: 244)}$</br>$\color{green}\text{plain-symm}$ | $\color{red}\text{Inconsistent}$ | 
| $11$ | $\color{orange}\text{300 s (obj: 564)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 547)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $12$ | $\color{orange}\text{300 s (obj: 388)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 435)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $13$ | $\color{orange}\text{300 s (obj: 686)}$</br>$\color{orange}\text{vrp-gecode-lns-symm-strong}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 632)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $14$ | $\color{orange}\text{300 s (obj: 917)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 1177)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $15$ | $\color{orange}\text{300 s (obj: 900)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 1140)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $16$ | $\color{green}\text{11 s (obj: 286)}$</br>$\color{green}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 303)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $17$ | $\color{orange}\text{300 s (obj: 1337)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 1525)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $18$ | $\color{orange}\text{300 s (obj: 774)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 917)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $19$ | $\color{orange}\text{300 s (obj: 354)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 398)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $20$ | $\color{orange}\text{300 s (obj: 1286)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 1378)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 
| $21$ | $\color{orange}\text{300 s (obj: 653)}$</br>$\color{orange}\text{vrp-gecode-lns}$ | $\color{red}\text{Inconsistent}$ | $\color{orange}\text{300 s (obj: 648)}$</br>$\color{orange}\text{local-search}$ | $\color{red}\text{Inconsistent}$ | 

<!-- end-status -->