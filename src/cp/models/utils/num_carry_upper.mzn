include "globals.mzn";
include "gecode.mzn";


% --- Parameters ---
int: m;
int: n;

set of int: COURIERS = 1..m;
set of int: PACKS = 1..n;
set of int: ORDERING = 1..n;
int: DEPOT = n+1;

array[COURIERS] of int: l;
array[PACKS] of int: s;
array[1..DEPOT, 1..DEPOT] of int: D;
int: MIN_STEP = min(D);
int: MIN_PATH = max(p in PACKS)(D[DEPOT, p] + D[p, DEPOT]);
int: MAX_PATH = sum(d in 1..DEPOT)(max(D[d, ..]));


% --- Decision variables ---
array[PACKS] of var COURIERS: assignments;

% --- Auxiliary variables ---
array[COURIERS] of var 0..n: carry_num;
array[COURIERS, PACKS] of var 0..n: packs_per_courier;

% --- Objective ---
var ceil(n/m)..n: obj;
constraint obj = max(carry_num);



% --- Capacity ---
constraint bin_packing_capa(l, assignments, s);


% --- Auxiliary variables ---
constraint forall(c in COURIERS)(
  carry_num[c] = count(p in PACKS)(assignments[p] == c)
);


constraint symmetry_breaking_constraint(
  forall(c in COURIERS)(
    forall(p in PACKS where assignments[p] != c)(packs_per_courier[c, p] = 0)
    /\ forall(p in PACKS where assignments[p] == c)(packs_per_courier[c, p] = p)
  )
  /\ forall(c1, c2 in COURIERS where c1 < c2 /\ l[c1] == l[c2])(
    lex_less( packs_per_courier[c1, ..], packs_per_courier[c2, ..] )
  )
);


solve 
  :: seq_search([
      int_search(assignments, first_fail, indomain_random),
  ])
  :: restart_luby( n )
  :: relax_and_reconstruct(assignments, if n <= 10 then 0 else 90 endif)
minimize obj;
