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

% Capacity constraint 
constraint forall(i in COURIERS)(
  sum(j in PACKS, k in ORDERING where A[j, k] = i)(
    s[j]
  ) <= l[i]
);

% All packages should be taken by exactly one courier.
constraint forall(j in PACKS)(
  count_eq( [ A[j, k] | k in ORDERING], 0, n-1 )
);


% For every row, the orders must not have discontinuities.
constraint forall(i in COURIERS)(
  forall(k in 2..n)(
    exists(j in PACKS)( A[j, k] = i ) -> exists(p in PACKS)( A[p, k-1] = i )
  )
);


% Return time travelled for each courier.
array[COURIERS, ORDERING] of var 0..n: T;

constraint all_different_except_0(T);
constraint forall(i in COURIERS)(
  forall(j in PACKS, k in ORDERING where A[j, k] = i)( T[i, k] = j )
);


solve minimize max( 
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