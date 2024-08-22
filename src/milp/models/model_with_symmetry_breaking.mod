param m integer; #Number of couriers
param n integer; #Number of packages

#Auxiliary param, set
set COURIERS := 1..m;
set PACKS := 1..n;
set NODES := 1..n+1; 
param DEPOT := n+1;

param l{COURIERS} integer; #array of capacity of each coureirs
param s{PACKS} integer; #array of size of each packs
param D{i in NODES, j in NODES} integer; #matrix of distances

param UpperBound := sum{i in NODES, j in NODES} D[i,j]; 
param LowerBound := max{i in PACKS}(D[DEPOT,i] + D[i,DEPOT]);

#####################

#A[i,k] = 1 iff the courier k bring the pakcs j
var A{i in PACKS, k in COURIERS} binary;
#X[i,j,k] = 1 iff the couriers k start from the point i and end to the point j 
var X{i in NODES, j in NODES, k in COURIERS} binary;
#var u[i,k] used of the soubtur elimination following the MTZ approach
var u{i in NODES, k in COURIERS} >= 1;

minimize ObjectiveMaxDistance: 
	max{k in COURIERS} sum{i in NODES, j in NODES} D[i,j]*X[i,j,k];
#####################

#link XY constraints
subject to LinkXY1{i in PACKS, k in COURIERS}:
	sum{j in NODES} X[i,j,k] = A[i,k];

subject to LinkXY2{j in PACKS, k in COURIERS}:
	sum{i in NODES} X[i,j,k] = A[j,k];

#each packages has to be assigend constraint
subject to AssignPackage{i in PACKS}:
    sum{k in COURIERS} A[i,k] = 1;

#capacity constraint
subject to Capacity {k in COURIERS}:
	sum{i in PACKS} A[i,k] * s[i] <= l[k];

#No-self-loop constraints
subject to NoSelfLoop {k in COURIERS, i in NODES}:
	X[i,i,k] = 0;	

#Visit-once constraints (only to the internal nodes, not the depot that is visited by each couriers)
subject to OneArrivalPerNode {j in PACKS}:
	sum{i in NODES, k in COURIERS} X[i,j,k] = 1;
	
subject to OneDeparturePerNode {i in PACKS}:
	sum{j in NODES, k in COURIERS}  X[i,j,k] = 1;

#Flow-preseving constraints
subject to Flow {j in PACKS, k in COURIERS}:
	sum{i in NODES} X[i,j,k] = sum{i in NODES} X[j,i,k];

#Depot constraints 
subject to StartAtDepot {k in COURIERS}:
	sum{j in NODES} X[DEPOT, j, k] = 1;
	
subject to EndAtDepot {k in COURIERS}:
	sum{i in NODES} X[i, DEPOT, k] = 1;

#Subtour elimination (Da guardarci meglio!) -> MTZ formultation

subject to SubtourElimination1{k in COURIERS, i in PACKS, j in NODES: j!=i}:
	u[i,k] - u[j,k] + 1 <= n*(1-X[i,j,k]);

subject to SubtourElimination2{k in COURIERS, i in PACKS}:
	u[i,k] <= X[DEPOT,i,k] + (n+1)*(1-X[DEPOT,i,k]);

#subject to SubtourElimination3{k in COURIERS, i in PACKS, j in NODES: j!=i}:
	#u[j,k] >= u[i,k] + X[i,j,k];

#Objective boundaries constraints
subject to UpBound:
	max{k in COURIERS} sum{i in NODES, j in NODES} D[i,j]*X[i,j,k] <= UpperBound;
	
subject to LowBound:
	max{k in COURIERS} sum{i in NODES, j in NODES} D[i,j]*X[i,j,k] >= LowerBound;


#Adding 2 constraints, the implied one and the symmetry breaking one
#subject to ImpliedConstraint {k in COURIERS}:
	#sum{i in PACKS} A[i,k] >= 1;
	
subject to SymmetryBreaking {k in COURIERS: k < m: l[k] == l[k+1]}:   #-> problem beacusa not taking into accunt the capacity of the couriers
    sum{i in PACKS} i * A[i,k] <= sum{i in PACKS} i * A[i,k+1];
    
