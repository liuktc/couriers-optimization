# Multiple Couriers Optimization


## Introduction

Project for the Combinatorial Decision Making and Optimization course at the University of Bologna (A.Y. 2023-2024).


## Description

Solving the capacitated vehicle routing problem using constraint programming (CP), propositional satisfiability (SAT), satisfiability modulo theories (SMT), and mixed-integer linear programming (MIP).


## Build

The experiments can be run through a Docker container. To build the container run:
```
cd src
docker build . -t cdmo --build-arg="AMPL_KEY=<ampl-community-key>"
```


## Execution

To perform all the experiments, run:
```
docker run -v ./res:/cdmo/results cdmo  \
    --timeout=<timeout-per-model>       \
    [--mem-limit=<ram-limit>]           \
    [--verbose]
```

To run a specific model of a specific method on a specific instance, run:
```
docker run -v ./res:/cdmo/results cdmo  \
    --timeout=<timeout-per-model>       \
    --methods=<method-name>             \
    --models=<model-name>               \
    --instances=<instance-number>       \
    [--mem-limit=<ram-limit>]           \
    [--verbose]
```


## Results
<!-- Do NOT remove the comments below -->
<!-- begin-status -->
| Instance | [CP](./method-statuses/cp-status.md) | [SAT](./method-statuses/sat-status.md) | [SMT](./method-statuses/smt-status.md) | [MIP](./method-statuses/mip-status.md) |
|:-:| :---:|:---:|:---:|:---:|
| $1$ | $\color{green}\text{0 s (obj: 14)}$</br>$\color{green}\text{vrp-plain-gecode}$ | $\color{green}\text{0 s (obj: 14)}$</br>$\color{green}\text{un-symm-model}$ | $\color{green}\text{0 s (obj: 14)}$</br>$\color{green}\text{twosolver}$ | $\color{green}\text{0 s (obj: 14)}$</br>$\color{green}\text{initial-model-scip}$ | 
| $2$ | $\color{green}\text{0 s (obj: 226)}$</br>$\color{green}\text{vrp-plain-gecode}$ | $\color{green}\text{4 s (obj: 226)}$</br>$\color{green}\text{matrix-model}$ | $\color{green}\text{0 s (obj: 226)}$</br>$\color{green}\text{twosolver-impl}$ | $\color{green}\text{0 s (obj: 226)}$</br>$\color{green}\text{initial-model-highs}$ | 
| $3$ | $\color{green}\text{0 s (obj: 12)}$</br>$\color{green}\text{vrp-plain-gecode}$ | $\color{green}\text{1 s (obj: 12)}$</br>$\color{green}\text{un-model}$ | $\color{green}\text{0 s (obj: 12)}$</br>$\color{green}\text{twosolver}$ | $\color{green}\text{0 s (obj: 12)}$</br>$\color{green}\text{initial-model-scip}$ | 
| $4$ | $\color{green}\text{0 s (obj: 220)}$</br>$\color{green}\text{vrp-plain-gecode}$ | $\color{green}\text{6 s (obj: 220)}$</br>$\color{green}\text{matrix-model}$ | $\color{green}\text{0 s (obj: 220)}$</br>$\color{green}\text{local-search}$ | $\color{green}\text{0 s (obj: 220)}$</br>$\color{green}\text{initial-model-highs}$ | 
| $5$ | $\color{green}\text{0 s (obj: 206)}$</br>$\color{green}\text{vrp-plain-gecode}$ | $\color{green}\text{0 s (obj: 206)}$</br>$\color{green}\text{un-model}$ | $\color{green}\text{0 s (obj: 206)}$</br>$\color{green}\text{twosolver}$ | $\color{green}\text{0 s (obj: 206)}$</br>$\color{green}\text{initial-model-scip}$ | 
| $6$ | $\color{green}\text{0 s (obj: 322)}$</br>$\color{green}\text{vrp-plain-gecode}$ | $\color{green}\text{1 s (obj: 322)}$</br>$\color{green}\text{matrix-model}$ | $\color{green}\text{0 s (obj: 322)}$</br>$\color{green}\text{twosolver-impl}$ | $\color{green}\text{0 s (obj: 322)}$</br>$\color{green}\text{initial-model-scip}$ | 
| $7$ | $\color{green}\text{0 s (obj: 167)}$</br>$\color{green}\text{vrp-lns50-gecode}$ | $\color{orange}\text{300 s (obj: 222)}$</br>$\color{orange}\text{un-cumulative-constraints-model}$ | $\color{green}\text{6 s (obj: 167)}$</br>$\color{green}\text{local-search}$ | $\color{green}\text{2 s (obj: 167)}$</br>$\color{green}\text{initial-model-highs}$ | 
| $8$ | $\color{green}\text{0 s (obj: 186)}$</br>$\color{green}\text{vrp-luby-gecode}$ | $\color{green}\text{14 s (obj: 186)}$</br>$\color{green}\text{matrix-model}$ | $\color{green}\text{0 s (obj: 186)}$</br>$\color{green}\text{twosolver-impl}$ | $\color{green}\text{0 s (obj: 186)}$</br>$\color{green}\text{initial-model-highs}$ | 
| $9$ | $\color{green}\text{0 s (obj: 436)}$</br>$\color{green}\text{vrp-luby-gecode}$ | $\color{green}\text{16 s (obj: 436)}$</br>$\color{green}\text{matrix-model}$ | $\color{green}\text{0 s (obj: 436)}$</br>$\color{green}\text{twosolver-impl}$ | $\color{green}\text{0 s (obj: 436)}$</br>$\color{green}\text{initial-model-highs}$ | 
| $10$ | $\color{green}\text{0 s (obj: 244)}$</br>$\color{green}\text{vrp-luby-gecode}$ | $\color{green}\text{60 s (obj: 244)}$</br>$\color{green}\text{matrix-model}$ | $\color{green}\text{0 s (obj: 244)}$</br>$\color{green}\text{local-search}$ | $\color{green}\text{1 s (obj: 244)}$</br>$\color{green}\text{initial-model-highs}$ | 
| $11$ | $\color{orange}\text{300 s (obj: 490)}$</br>$\color{orange}\text{vrp-lns95-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 547)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 
| $12$ | $\color{green}\text{77 s (obj: 346)}$</br>$\color{green}\text{vrp-lns95-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 435)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 
| $13$ | $\color{orange}\text{300 s (obj: 574)}$</br>$\color{orange}\text{vrp-lns90-symm-amount-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 632)}$</br>$\color{orange}\text{local-search}$ | $\color{orange}\text{300 s (obj: 526)}$</br>$\color{orange}\text{symmetry-model-scip}$ | 
| $14$ | $\color{orange}\text{300 s (obj: 715)}$</br>$\color{orange}\text{vrp-lns95-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 1177)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 
| $15$ | $\color{orange}\text{300 s (obj: 659)}$</br>$\color{orange}\text{vrp-plain-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 1140)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 
| $16$ | $\color{green}\text{1 s (obj: 286)}$</br>$\color{green}\text{vrp-lns90-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 303)}$</br>$\color{orange}\text{local-search}$ | $\color{green}\text{127 s (obj: 286)}$</br>$\color{green}\text{initial-model-highs}$ | 
| $17$ | $\color{orange}\text{300 s (obj: 1076)}$</br>$\color{orange}\text{vrp-lns95-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 1525)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 
| $18$ | $\color{orange}\text{300 s (obj: 620)}$</br>$\color{orange}\text{vrp-lns95-symm-packs-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 917)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 
| $19$ | $\color{green}\text{32 s (obj: 334)}$</br>$\color{green}\text{vrp-lns97-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 398)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 
| $20$ | $\color{orange}\text{300 s (obj: 1059)}$</br>$\color{orange}\text{vrp-lns90-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 1378)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 
| $21$ | $\color{orange}\text{300 s (obj: 516)}$</br>$\color{orange}\text{vrp-lns95-gecode}$ | $\color{lightgray}\text{Timeout}$ | $\color{orange}\text{300 s (obj: 648)}$</br>$\color{orange}\text{local-search}$ | $\color{lightgray}\text{Timeout}$ | 

<!-- end-status -->