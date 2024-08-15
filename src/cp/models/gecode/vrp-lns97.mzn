include "globals.mzn";
include "gecode.mzn";



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

array[LOCATIONS] of int: MIN_PER_POS = [ min(D[i, ..]) | i in LOCATIONS ];



% --- Decision variables ---
array[PACKS] of var COURIERS: assignments;
array[COURIERS, LOCATIONS] of var LOCATIONS: path;

% --- Auxiliary variables ---
array[COURIERS] of var 0..n: carry_num;



% --- Objective ---
var MIN_PATH..MAX_PATH: obj;
constraint implied_constraint(
  obj >= max(c in COURIERS)( sum(p in PACKS where assignments[p] == c)(MIN_PER_POS[p]) + 2*MIN_PER_POS[DEPOT] )
);
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
      int_search(assignments, dom_w_deg, indomain_random),
      seq_search([ 
        int_search(path[c, ..], first_fail, indomain_random)
      | c in reverse(arg_sort(l)) ]),
  ])
  :: restart_luby( n )
  :: relax_and_reconstruct(assignments, if n <= 10 then 0 else 97 endif)
minimize obj;