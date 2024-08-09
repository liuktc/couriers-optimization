#Non funziona

# --- Parameters ---
param m integer;  # Number of couriers
param n integer;  # Number of packages

set COURIERS := 1..m;
set PACKS := 1..n;
set ORDERING := 1..n;
param DEPOT := n+1;

param l {COURIERS} integer;  # Courier capacities
param s {PACKS} integer;     # Package sizes
param D {1..DEPOT, 1..DEPOT} integer;  # Distance matrix

param MIN_PATH := max {p in PACKS} (D[DEPOT,p] + D[p,DEPOT]);
param MAX_PATH := sum {d in 1..DEPOT} max {j in 1..DEPOT} D[d,j];

# --- Decision Variables ---
var assignments {PACKS} integer >= 1, <= m;
var path {COURIERS, 1..DEPOT} integer >= 1, <= DEPOT;

# --- Auxiliary Variables ---
var carry_load {COURIERS} integer;
var carry_num {COURIERS} integer;

# --- Objective Function ---
var obj >= MIN_PATH, <= MAX_PATH;
minimize Objective: obj;

# --- Constraints ---

# Capacity constraint (bin packing)
subject to Capacity {c in COURIERS}:
    sum {p in PACKS: assignments[p] == c} s[p] <= l[c];

# Auxiliary variable definitions
subject to CarryLoad {c in COURIERS}:
    carry_load[c] = sum {p in PACKS: assignments[p] == c} s[p];

subject to CarryNum {c in COURIERS}:
    carry_num[c] = sum {p in PACKS} (if assignments[p] == c then 1 else 0);

subject to PathStart1 {c in COURIERS: carry_num[c] > 0}:
    path[c,DEPOT] != DEPOT;

subject to PathStart2 {c in COURIERS: carry_num[c] = 0}:
    path[c,DEPOT] = DEPOT;

subject to PackageVisit {p in PACKS}:
    path[assignments[p], p] != p;

subject to NoVisitOtherCourier {p in PACKS, c in COURIERS: c != assignments[p]}:
    path[c, p] = p;

# This is a simplified version and may not fully capture the subcircuit constraint
subject to SubcircuitApprox {c in COURIERS, i in 1..DEPOT}:
    path[c,i] != i ==> exists {j in 1..DEPOT: j != i} (path[c,j] = i);

# Objective definition
subject to ObjectiveDefinition:
    obj = max {c in COURIERS} (sum {j in 1..DEPOT: path[c,j] != j} D[j, path[c,j]]);
    
   