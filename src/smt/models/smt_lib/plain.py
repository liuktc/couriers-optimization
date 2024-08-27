import os, pathlib, sys
sys.path.append(os.path.join(pathlib.Path(__file__).parent.resolve(), "../.."))
from smtlib_lib import *
from smtlib_lib.solvers import *



def model(m, n, l, s, D):
    COURIERS = range(m)
    PACKS = range(n)
    LOCATIONS = range(n+1)
    DEPOT = n
    OBJ_LOWER = max([D[DEPOT][p] + D[p][DEPOT] for p in PACKS])

    model = SMTLIBModel(
        logic = "QF_LIA",
        imports = [ libs.max("Int") ]
    )

    # Variables
    assignments = [ Integer(f"assignment_{p}") for p in PACKS ]
    carry_num = [ Integer(f"carry_num_{c}") for c in COURIERS ]
    paths = [ [Integer(f"path_{c}_{l}") for l in LOCATIONS] for c in COURIERS ]
    paths_cost = [ Integer(f"path_cost_{c}") for c in COURIERS ]
    u = [ [Integer(f"u_{c}_{l}") for l in LOCATIONS] for c in COURIERS ]
    obj = Integer("obj")

    # Domains
    model.add(CommentLine("Variables domain"))
    [ model.add( (0 <= assignments[p]) & (assignments[p] < m) ) for p in PACKS ]
    [ model.add( (0 <= paths[c][l]) & (paths[c][l] <= DEPOT) ) for c in COURIERS for l in LOCATIONS ]
    [ model.add( (1 <= u[c][l]) & (u[c][l] <= n+1) ) for c in COURIERS for l in LOCATIONS ]
    model.add( obj >= OBJ_LOWER )

    # Constraints
    model.add(CommentLine("-- Load capacity"))
    for c in COURIERS:
        model.add( Sum([ ITE(assignments[p] == c, s[p], 0) for p in PACKS]) <= l[c] )

    model.add(CommentLine("-- Number of packages per courier"))
    for c in COURIERS:
        for p in PACKS:
            model.add( carry_num[c] == Sum([ ITE(assignments[p] == c, 1, 0) for p in PACKS]) )

    model.add(CommentLine("-- Locations excluded from path"))
    for c in COURIERS:
        model.add( Implies(carry_num[c] > 0, paths[c][DEPOT] != DEPOT) )
        model.add( Implies(carry_num[c] == 0, paths[c][DEPOT] == DEPOT) )
        for p in PACKS:
            model.add( Implies(assignments[p] != c, paths[c][p] == p) )
            model.add( Implies(assignments[p] == c, paths[c][p] != p) )

    model.add(CommentLine("-- MTZ Subtour elimination"))
    for c in COURIERS:
        model.add( Distinct([ paths[c][l] for l in LOCATIONS ]) )

        for p in PACKS:
            model.add( Implies(paths[c][DEPOT] == p, u[c][p] == 1) )

        for l1 in PACKS:
            for l2 in LOCATIONS:
                if l1 == l2: continue
                model.add( Implies(paths[c][l1] == l2, u[c][l2] >= (u[c][l1] + 1)) )

        for l1 in PACKS:
            for l2 in LOCATIONS:
                if l1 == l2: continue
                model.add( (u[c][l1] - u[c][l2] + 1) <= ((n-1) * ITE(paths[c][l1] == l2, 0, 1)) )

    model.add(CommentLine("-- Path cost per courier"))
    for c in COURIERS:
        model.add( paths_cost[c] == Sum([ ITE(paths[c][l1] == l2, D[l1][l2], 0) for l1 in LOCATIONS for l2 in LOCATIONS if l1 != l2]) )

    model.add(CommentLine("-- Objective function"))
    constr = paths_cost[0]
    for i in range(1, m):
        constr = FnCall("max", constr, paths_cost[i])
    model.add(obj == constr)

    return model
