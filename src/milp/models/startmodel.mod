set COURIERS;
set PACKAGES;
param Depot := card(PACKAGES) + 1;
set NODES := PACKAGES union {Depot};  

param capacity{COURIERS};
param size{PACKAGES};
param distance{i in NODES, j in NODES};

var x{i in NODES, j in NODES, k in COURIERS} binary;
var u{i in PACKAGES, k in COURIERS} >= 0;
var y{i in PACKAGES, k in COURIERS} binary;

minimize TotalDistance:
    sum{i in NODES, j in NODES, k in COURIERS} distance[i,j] * x[i,j,k];

subject to VisitOnce{j in PACKAGES}:
    sum{i in NODES, k in COURIERS: i != j} x[i,j,k] = 1;

subject to FlowConservation{j in NODES, k in COURIERS}:
    sum{i in NODES: i != j} x[i,j,k] = sum{i in NODES: i != j} x[j,i,k];

subject to StartAtDepot{k in COURIERS}:
    sum{j in PACKAGES} x[Depot,j,k] = 1;

subject to EndAtDepot{k in COURIERS}:
    sum{i in PACKAGES} x[i,Depot,k] = 1;

subject to SubtourElimination{i in PACKAGES, j in PACKAGES, k in COURIERS: i != j}:
    u[i,k] - u[j,k] + card(PACKAGES) * x[i,j,k] <= card(PACKAGES) - 1;

subject to LinkXY{i in PACKAGES, k in COURIERS}:
    sum{j in NODES: j != i} x[i,j,k] = y[i,k];

subject to CapacityConstraint{k in COURIERS}:
    sum{i in PACKAGES} size[i] * y[i,k] <= capacity[k];

subject to AssignPackage{i in PACKAGES}:
    sum{k in COURIERS} y[i,k] = 1;