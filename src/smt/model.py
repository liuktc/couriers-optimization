from z3 import *
import time

def maximum(a):
    m = a[0]
    for v in a[1:]:
        m = If(v > m, v, m)
    return m

def millisecs_left(t, timeout):
    return int((timeout - t) * 1000)

def SMT(m, n, l, s, D, implied_constraints=True, timeout=300):
    COURIERS = range(m)
    ITEMS = range(n)
    
    solver = Solver()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
    # Decision variables
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # X[i][j] == True means that item j is delivered by courier i 
    X = [[Bool(f"x_{j}_{i}") for j in ITEMS] for i in COURIERS]

    # Order[j] == k means that item j is delivered as its k-th item
    ORDERING = [Int(f"order_{j}") for j in ITEMS]
    
    # Rapresents the distance traveled by each courier
    DISTANCES = [Int(f"distance_{i}") for i in COURIERS]
    
    # Count[i] == k means that courier i delivered k items
    COUNT = [Int(f"count_{i}") for i in COURIERS]
    
    # Count constraints
    for i in COURIERS:
        solver.add(COUNT[i] == Sum([If(X[i][j], 1, 0) for j in ITEMS]))
    
    # Exactly one item is delivered by each courier
    for j in ITEMS:
        solver.add(Sum([If(X[i][j], 1, 0) for i in COURIERS]) == 1)
        
    # Order constraints
    for i in COURIERS:
        order = [If(X[i][j], ORDERING[j], -2 * ORDERING[j]) for j in ITEMS]
        solver.add(Distinct(order))
        solver.add(And([order[j] <= COUNT[i] for j in ITEMS])) 
        
        
        
    for j in ITEMS:
        solver.add(ORDERING[j] >= 1)
            
    # Calculate the distance traveled by each courier
    for i in COURIERS:
        dist = Sum([
            Sum([If(And(X[i][j1], X[i][j2], ORDERING[j1] + 1 == ORDERING[j2]),D[j1][j2], 0) for j2 in ITEMS])
            for j1 in ITEMS
            ])
        dist += Sum([If(And(X[i][j], ORDERING[j] == 1), D[n][j], 0) for j in ITEMS])
        dist += Sum([If(And(X[i][j], ORDERING[j] == COUNT[i]), D[j][n], 0) for j in ITEMS])
        solver.add(DISTANCES[i] == dist)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    # Simmetry breaking constraints
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Objective function
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # Minimize the maximum distance traveled
    obj = Int('obj')
    solver.add(obj == maximum([DISTANCES[i] for i in COURIERS]))
    
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Search strategy
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    solver.push()
    solver.set('timeout', millisecs_left(time.time(), timeout))
    
    timeout = time.time() + timeout
    while solver.check() == sat:
        model = solver.model()
        # print(model)
        result_objective = model[obj].as_long()

        solver.pop()
        solver.push()
        solver.add(obj < result_objective)
        
        now = time.time()
        if now >= timeout:
            break
        solver.set('timeout', millisecs_left(now, timeout))
        
    if model is not None:
        # Pretty print the solution
        print(f"Optimal solution found with objective {result_objective}")
        for i in COURIERS:
            items_delivered = [j for j in ITEMS if model[X[i][j]] == True]
            orders = {model[ORDERING[j]].as_long(): j for j in items_delivered}
            # Sort the items by their order
            items_delivered.sort(key=lambda j: orders[model[ORDERING[j]].as_long()])
            print(f"Courier {i} delivered items {', '.join([str(j) for j in items_delivered])}")
