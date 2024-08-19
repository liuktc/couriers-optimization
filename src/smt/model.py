from z3 import *
import time

def maximum(a):
    m = a[0]
    for v in a[1:]:
        m = If(v > m, v, m)
    return m

def millisecs_left(t, timeout):
    return int((timeout - t) * 1000)

def precedes(a1, a2):
    if len(a1) == 1 and len(a2) == 1:
        return Not(And(Not(a1[0]), a2[0]))
    return Or(And(a1[0], Not(a2[0])),
              And(a1[0] == a2[0], precedes(a1[1:], a2[1:])))
    
# -----------------------------------------------------------------------------%
# Constrains the elements of 'path' to define a subcircuit where 'path[i] = j'
# means that 'j' is the successor of 'i' and 'path[i] = i' means that 'i'
# is not in the circuit.
# assignments[i] = j means that packet 'i' is assigned to courier 'j'.
# -----------------------------------------------------------------------------%
def subcircuit(COURIERS, ITEMS,m,n, path, assignments, solver):
    """ path = [| 3, 2, 4, 7, 5, 6, 1
                | 1, 5, 3, 4, 6, 7, 2
                |]; 
                
        assignments = [1, 2, 1, 1, 2, 2];
    """
    # Orders[i] is the order of item i
    ORDERS = [[Int(f"order_{i}_{j}") for j in range(n + 1)] for i in COURIERS]
    # All different constraints on orders
    solver.add(Distinct(ORDERS))
            
    for i in COURIERS:
        solver.add(And([And(ORDERS[i][j] <= n) for j in range(n + 1)])) 
        solver.add(And([If(assignments[j] == i + 1,
                           path[i][j] != j + 1,
                           path[i][j] == j + 1) for j in range(n + 1)]))
        solver.add(And([If(assignments[j] == i + 1,
                           ORDERS[i][j] + 1 == ORDERS[i][path[i][j] - 1],
                           ORDERS[i][j] == -j) for j in range(n + 1)])) 
        
           
 
    
    
def SMT(m, n, l, s, D, implied_constraints=False, simmetry_breaking=False, timeout=300):
    COURIERS = range(m)
    ITEMS = range(n)
    
    solver = Solver()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
    # Decision variables
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # X[i][j] == True means that item j is delivered by courier i 
    X = [[Bool(f"x_{i}_{j}") for j in ITEMS] for i in COURIERS]

    # Order[j] == k means that item j is delivered as its k-th item
    ORDERING = [Int(f"order_{j}") for j in ITEMS]
    
    # Rapresents the distance traveled by each courier
    DISTANCES = [Int(f"distance_{i}") for i in COURIERS]
    
    # Count[i] == k means that courier i delivered k items
    COUNT = [Int(f"count_{i}") for i in COURIERS]
    
    print("Adding count constraints")
    # Count constraints
    for i in COURIERS:
        solver.add(COUNT[i] == Sum([If(X[i][j], 1, 0) for j in ITEMS]))
        solver.add(COUNT[i] >= 1)
        # solver.add(COUNT[i] <= n // 2)
        
    
    # Every item is delivered by exactly one courier    
    for j in ITEMS:
        solver.add(Sum([If(X[i][j], 1, 0) for i in COURIERS]) == 1)
        
    for j in ITEMS:
        solver.add(ORDERING[j] >= 1)
    
    print("Adding order constraints")
    # Order constraints
    for i in COURIERS:
        order = [If(X[i][j], ORDERING[j], - j) for j in ITEMS]
        solver.add(Distinct(order))
        solver.add(And([order[j] <= COUNT[i] for j in ITEMS])) 
                        
    # Total weight constraints
    for i in COURIERS:
        solver.add(Sum([If(X[i][j], s[j], 0) for j in ITEMS]) <= l[i])
                    
    print("Adding distance constraints")
    start = time.time()
    # Calculate the distance traveled by each courier
    for i in COURIERS:
        dist = Sum([
            Sum([If(And(X[i][j1], X[i][j2], ORDERING[j1] + 1 == ORDERING[j2]),D[j1][j2], 0) for j2 in ITEMS])
            for j1 in ITEMS
            ])
        dist += Sum([If(And(X[i][j], ORDERING[j] == 1), D[n][j], 0) for j in ITEMS])
        dist += Sum([If(And(X[i][j], ORDERING[j] == COUNT[i]), D[j][n], 0) for j in ITEMS])
        solver.add(DISTANCES[i] == dist)
    
    print(f"Time to calculate distances = {time.time() - start}")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    # Simmetry breaking constraints
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print("Adding symmetry breaking constraints")
    if simmetry_breaking:
        # We don't care which courier delivers which item if they have the same load capacity
        LOADS = [Int(f"load_{i}") for i in COURIERS]
        for i in COURIERS:
            solver.add(LOADS[i] == Sum([If(X[i][j], s[j], 0) for j in ITEMS]))
            
        # Order the loads
        solver.add(And([LOADS[i] <= LOADS[i+1] for i in range(m-1)]))
        
        # If two couriers have the same load capacity, then we fix their order
        for i in range(m-1):
            solver.add(Implies(LOADS[i] == LOADS[i+1], precedes(X[i], X[i+1])))
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    # Implied constraints
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print("Adding implied constraints")
    if implied_constraints:
        solver.add(And([ORDERING[j] >= 0 for j in ITEMS] + [ORDERING[j] <= n for j in ITEMS]))
            
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Objective function
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # Minimize the maximum distance traveled
    obj = Int('obj')
    solver.add(obj == maximum([DISTANCES[i] for i in COURIERS]))
    
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Search strategy
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    """ lower_bound = max([D[n][j] + D[j][n] for j in ITEMS])
    
    max_distances = [max(D[i][:-1]) for i in range(n)]
    max_distances.sort()
    if implied_constraints:
        upper_bound = sum(max_distances[m:]) + max(D[n]) + max([D[j][n] for j in range(n)])
    else:
        upper_bound = sum(max_distances[1:]) + max(D[n]) + max([D[j][n] for j in range(n)])

    solver.add(obj >= lower_bound)
    solver.add(obj <= upper_bound) """
    
    timeout = time.time() + timeout*1000
    solver.push()
    print(f"Timeout = {timeout}, time = {time.time()}")
    print(f"Timeout = {millisecs_left(time.time(), timeout)} ms = {millisecs_left(time.time(), timeout) / 1000} s")
    solver.set('timeout', millisecs_left(time.time(), timeout))
    
    model = None
    while solver.check() == sat:
        model = solver.model()
        # print(model)
        result_objective = model[obj].as_long()
        
        print(f"New optimal found: {result_objective}")
        print(f"Distances = {[model[DISTANCES[i]].as_long() for i in COURIERS]}")
        print(f"Counts = {[model[COUNT[i]].as_long() for i in COURIERS]}")
        print(f"Orders = {[model[ORDERING[j]].as_long() for j in ITEMS]}")
        print("X = ")
        for i in COURIERS:
            row = [1 if model[X[i][j]] else 0 for j in ITEMS]
            print(row)

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
            if len(items_delivered) == 0:
                print(f"Courier {i} did not deliver any items")
                continue
            orders = {model[ORDERING[j]].as_long():j for j in items_delivered}
            print(orders)
            # Sort orders 
            items_delivered = [orders[i] for i in range(1,len(orders)+1)]
            
            print(f"Courier {i} delivered items {', '.join([str(j) for j in items_delivered])}")
            
            # Calculate the total distance traveled by the courier
            dist = D[n][items_delivered[0]]
            #print(f"From {n} to {items_delivered[0]} = {dist}")
            for j, item in enumerate(items_delivered[:-1]):
                dist += D[item][items_delivered[j+1]]
                # print(f"From {item} to {items_delivered[j+1]} = {D[item][items_delivered[j+1]]}")
            dist += D[items_delivered[-1]][n]
            #print(f"From {items_delivered[-1]} to {n} = {D[items_delivered[-1]][n]}")
            print(f"Courier {i} traveled {dist} units of distance")