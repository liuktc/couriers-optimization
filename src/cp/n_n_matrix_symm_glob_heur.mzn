include "globals.mzn";

% Parameters
int: m;
int: n;

set of int: COURIERS = 1..m;
set of int: PACKS = 1..n;
set of int: ORDERING = 1..n;

array[COURIERS] of int: l;
array[PACKS] of int: s;
array[1..n+1, 1..n+1] of int: D;

array[PACKS, ORDERING] of var 0..m: A;
array[COURIERS, ORDERING] of var 0..n: T;

% --- Capacity constraint 
% constraint forall(i in COURIERS)(
%   sum(j in PACKS, k in ORDERING where A[j, k] = i)(
%     s[j]
%   ) <= l[i]
% );
constraint forall(i in COURIERS)(
  sum(k in ORDERING where T[i, k] != 0)( s[ T[i, k] ] ) <= l[i]
);


% --- All packages should be taken by exactly one courier.
constraint forall(j in PACKS)(
  count_eq( [ A[j, k] | k in ORDERING], 0, n-1 )
);


% --- For every row, the orders must not have discontinuities.
% constraint forall(i in COURIERS)(
%   forall(k in 2..n)(
%     exists(j in PACKS)( A[j, k] = i ) -> exists(p in PACKS)( A[p, k-1] = i )
%   )
% );
constraint forall(i in COURIERS)(
  not exists(k in 1..n-1)( T[i, k] = 0 /\ T[i, k+1] != 0 )
);



% --- Return time travelled for each courier.
constraint all_different_except_0(T);
constraint forall(i in COURIERS)(
  forall(j in PACKS, k in ORDERING where A[j, k] = i)( T[i, k] = j )
);


% --- Symmetry breaking
constraint symmetry_breaking_constraint(
  forall(i, j in COURIERS where l[i] = l[j] /\ i < j)(
    lex_less([T[i, k] | k in ORDERING], [T[j, k] | k in ORDERING])
  )
);


solve 
  :: seq_search([
      int_search(T, dom_w_deg, indomain_min)
  ])
  minimize max( 
    [ sum(k in ORDERING)(
        if k == 1 then
          D[ n+1, T[i, k] ]
        elseif T[i, k] == 0 /\ T[i, k-1] != 0 then
          D[ T[i, k-1], n+1 ]
        elseif T[i, k] != 0 then
          D[ T[i, k-1], T[i, k] ]
        else
          0
        endif
      ) | i in COURIERS ] 
  );