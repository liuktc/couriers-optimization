include "globals.mzn";
include "chuffed.mzn";



% --- Parameters ---
int: m;
int: n;

set of int: COURIERS = 1..m;
set of int: PACKS = 1..n;
set of int: ORDERING = 1..n;
int: DEPOT = n+1;
set of int: LOCATIONS = 1..DEPOT;

array[COURIERS] of int: l;
array[PACKS] of int: s;
array[LOCATIONS, LOCATIONS] of int: D;
int: MIN_PATH = max(p in PACKS)(D[DEPOT, p] + D[p, DEPOT]);
int: MAX_PATH = sum(d in LOCATIONS)(max(D[d, ..]));



% --- Decision variables ---
array[PACKS] of var COURIERS: assignments;
array[COURIERS, LOCATIONS] of var LOCATIONS: path;

% --- Auxiliary variables ---
array[COURIERS] of var int: carry_num;



% --- Objective ---
var MIN_PATH..MAX_PATH: obj;
constraint obj = max(c in COURIERS)( sum(j in LOCATIONS where path[c, j] != j)(D[j, path[c, j]]) );



% --- Capacity ---
constraint bin_packing_capa(l, assignments, s);


% --- Auxiliary variables ---
constraint forall(c in COURIERS)(
  carry_num[c] = count(p in PACKS)(assignments[p] == c)
);


% --- Path related constraints ---
constraint forall(c in COURIERS)(
  if carry_num[c] > 0 then 
    path[c, DEPOT] != DEPOT
  else
    path[c, DEPOT] == DEPOT
  endif

  /\ forall(p in PACKS)(
    if assignments[p] == c then
      path[ c, p ] != p
    else
      path[ c, p ] == p
    endif
  )
  
  /\ subcircuit(path[c, ..])
);



solve 
  :: seq_search([
      int_search(assignments, first_fail, indomain_split),
      seq_search([ 
        int_search(path[c, ..], first_fail, indomain_split)
      | c in reverse(arg_sort(l)) ]),
  ])
minimize obj;