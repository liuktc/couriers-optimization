include "globals.mzn";



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
array[COURIERS] of var 0..n: carry_num;
array[COURIERS, PACKS] of var 0..n: packs_per_courier;



% --- Objective ---
var MIN_PATH..MAX_PATH: obj;
constraint obj = max(c in COURIERS)( sum(j in LOCATIONS where path[c, j] != j)(D[j, path[c, j]]) );



% --- Capacity ---
constraint bin_packing_capa(l, assignments, s);


% --- Auxiliary variables ---
constraint forall(c in COURIERS)(
  carry_num[c] = count(p in PACKS)(assignments[p] == c)
);

constraint forall(c in COURIERS)(
  forall(p in PACKS where assignments[p] != c)(packs_per_courier[c, p] = 0)
  /\ forall(p in PACKS where assignments[p] == c)(packs_per_courier[c, p] = p)
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


% --- Ordering on the index of the delivered packages ---
constraint symmetry_breaking_constraint(
  forall(c1, c2 in COURIERS where c1 < c2 /\ l[c1] == l[c2])(
    lex_less( packs_per_courier[c1, ..], packs_per_courier[c2, ..] )
  )
);



solve 
  :: seq_search([
      int_search(assignments, dom_w_deg, indomain_random),
      seq_search([ 
        int_search(path[c, ..], first_fail, indomain_random)
      | c in reverse(arg_sort(l)) ]),
  ])
minimize obj;