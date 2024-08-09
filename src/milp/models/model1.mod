#Ok gira senza warning ma mi dà risultati non ottimali nonostante mi dica siano ottimali

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

#Da migliorare
#param UpperBound := sum{i in NODES, j in NODES} D[i,j]; 
#param LowerBound := 0;

#####################

#A[i,k] = 1 iff the courier K bring the pakcs j
var A{i in PACKS, k in COURIERS} binary;
#X[i,j,k] = 1 iff the couriers k start from the point i and end to the point j 
var X{i in NODES, j in NODES, k in COURIERS} binary;
#var u[i,k] used of the soubtur elimination following the MTZ approach
var u{i in PACKS, k in COURIERS} >= 0;
#MaxDistance of each courier
var MaxDistance >= 0;

#minimize TotalDistance:
	#sum{i in NODES, j in NODES, k in COURIERS} D[i,j] * X[i,j,k];

minimize ObjectiveMaxDistance: MaxDistance;
#####################

#DefinitionOfMaxDistance (like the variable that is greater than all the distance cover by the couriers)
subject to DefineMaxDistance {k in COURIERS}:
	MaxDistance >= sum{i in NODES, j in NODES} D[i,j]*X[i,j,k];

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

#Subtour elimination (Da capire meglio!) -> MTZ formultation
subject to SubtourElimination{i in PACKS, j in PACKS, k in COURIERS}:
    u[i,k] - u[j,k] + n * X[i,j,k] <= n - 1;
    
#Objective boundaries constraints
#subject to UpBound:
	#MaxDistance <= UpperBound;
	
#subject to LowBound:
	#MaxDistance >= LowerBound;	


#Adding 2 constraints, the implied one and the symmetry breaking one
#subject to ImpliedConstraint {k in COURIERS}:
	#sum{i in PACKS} A[i,k] >= 1;
	
#subject to SymmetryBreaking {k in COURIERS: k < m}:
    #sum{i in PACKS} i * A[i,k] <= sum{i in PACKS} i * A[i,k+1];

