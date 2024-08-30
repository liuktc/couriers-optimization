include "globals.mzn";

int: m;
int: n;
array[1..m] of int: l;
array[1..n] of int: s;
array[1..n+1, 1..n+1] of int: D;

array[1..m, 1..n, 1..n] of var bool: X;
array[1..m, 1..n] of var 0..n: T;


% Capacity of each courier.
constraint forall(i in 1..m)(
    sum( j in 1..n, k in 1..n where X[i, j, k] == true )(s[j]) <= l[i]
);

% All packages should be taken by exactly one courier.
constraint forall(j in 1..n)(
  count_eq( [X[i, j, k] | i in 1..m, k in 1..n], true, 1 )
);

% For every row, the deliveries must not have discontinuities.
constraint forall(i in 1..m)(
  forall(k in 2..n)(
    forall(j in 1..n)(X[i, j, k-1] == false) -> forall(j in 1..n)(X[i, j, k] == false)
  )
);

% Position travelled by each courier.
constraint all_different_except_0(T);
constraint forall(i in 1..m, k in 1..n, j in 1..n where X[i, j, k] == true)(
  T[i, k] == j
);


solve minimize max( 
  [ sum(k in 1..n)(
      if k == 1 then
        D[ n+1, T[i, k] ]
      elseif T[i, k] == 0 /\ T[i, k-1] != 0 then
        D[ T[i, k-1], n+1 ]
      elseif T[i, k] != 0 then
        D[ T[i, k-1], T[i, k] ]
      else
        0
      endif
    ) | i in 1..m ] 
);