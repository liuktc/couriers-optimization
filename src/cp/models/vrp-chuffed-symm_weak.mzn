include "globals.mzn";
include "chuffed.mzn";


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
int: MIN_PATH = max(p in PACKS)(D[DEPOT, p] + D[p, DEPOT]);
int: MAX_PATH = sum(d in 1..DEPOT)(max(D[d, ..]));


% --- Decision variables ---
array[PACKS] of var COURIERS: assignments;
array[COURIERS, 1..DEPOT] of var 1..DEPOT: path;

% --- Auxiliary variables ---
array[COURIERS] of var int: carry_load;
array[COURIERS] of var int: carry_num;

var MIN_PATH..MAX_PATH: obj = max(c in COURIERS)( sum(j in 1..DEPOT where path[c, j] != j)(D[j, path[c, j]]) );



% --- Capacity ---
constraint bin_packing_capa(l, assignments, s);


% --- Auxiliary variables ---
constraint forall(c in COURIERS)(
  carry_load[c] = sum(p in PACKS where assignments[p] == c)(s[p])
  /\ carry_num[c] = count(p in PACKS)(assignments[p] == c)
);


% --- Path related constraints ---

constraint forall(c in COURIERS)(
  if carry_num[c] > 0 then 
    path[c, DEPOT] != DEPOT
  else
    path[c, DEPOT] == DEPOT
  endif
);

constraint forall(p in PACKS)(
  path[ assignments[p], p ] != p
  /\ forall(c in COURIERS where c != assignments[p])( path[c, p] == p )
);

constraint implied_constraint(
  forall(p1 in PACKS, c in COURIERS where c != assignments[p1])(
    forall(p2 in PACKS where p1 != p2)( 
      path[c, p2] != p1
    )
  )
);

constraint forall(c in COURIERS)(
  subcircuit(path[c, ..])
);



constraint symmetry_breaking_constraint(
  forall(c1, c2 in COURIERS where c1 < c2 /\ l[c1] == l[c2])(
    lex_less( path[c1, ..], path[c2, ..] )
  )
);

% constraint symmetry_breaking_constraint(
%   forall(c1, c2 in COURIERS where c1 < c2 /\ max(carry_load[c1], carry_load[c2]) <= min(l[c1], l[c2]))(
%     lex_less( path[c1, ..], path[c2, ..] )
%   )
% );



solve 
  :: seq_search([
      int_search(assignments, random_order, indomain_split),
      int_search(path, first_fail, indomain_split) 
%       seq_search([ 
%         int_search(path[c, ..], dom_w_deg, indomain_random)
%       | c in COURIERS ])
  ])
  :: restart_luby(min((n*m), 100))
minimize obj;