from z3 import *
import time

def maximum(arr):
    return If(len(arr) == 1, arr[0], If(arr[0] > arr[1], arr[0], arr[1]))

def millisecs_left(t, timeout):
    return int((timeout - t) * 1000)

def precedes(a1, a2):
    if len(a1) == 1 and len(a2) == 1:
        return Not(And(Not(a1[0]), a2[0]))
    return Or(And(a1[0], Not(a2[0])),
              And(a1[0] == a2[0], precedes(a1[1:], a2[1:])))
    
def SMT_array(m, n, l, s, D, implied_constraints=False, simmetry_breaking=False, timeout=300):
    COURIERS = range(m)
    ITEMS = range(n)
    
    solver = Solver()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
    # Decision variables
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # X[i][j] == True means that item j is delivered by courier i 
    # X = [[Bool(f"x_{j}_{i}") for j in ITEMS] for i in COURIERS]
    X = Array('X', IntSort(), BoolSort())

    # Order[j] == k means that item j is delivered as its k-th item
    # ORDERING = [Int(f"order_{j}") for j in ITEMS]
    ORDERING = Array('ORDERING', IntSort(), IntSort())
    
    # Rapresents the distance traveled by each courier
    # DISTANCES = [Int(f"distance_{i}") for i in COURIERS]
    DISTANCES = Array('DISTANCES', IntSort(), IntSort())
    
    # Count[i] == k means that courier i delivered k items
    # COUNT = [Int(f"count_{i}") for i in COURIERS]
    COUNT = Array('COUNT', IntSort(), IntSort())
    
    # Count constraints
    # for i in COURIERS:
    #    solver.add(COUNT[i] == Sum([If(X[i][j], 1, 0) for j in ITEMS]))
    for i in COURIERS:
        courier_items = [Select(X, i * n + j) for j in ITEMS]
        count_i = Sum([If(courier_items[j] == True, 1, 0) for j in ITEMS])
        solver.add(COUNT == Store(COUNT, i, count_i))
        # Store(COUNT, i, count_i)
    
    # Every item is delivered by exactly one courier
    for j in ITEMS:
        solver.add(Sum([If(Select(X, i * n + j), 1, 0) for i in COURIERS]) == 1)
        
    # Order constraints
    # for i in COURIERS:
    #    order = [If(X[i][j], ORDERING[j], -2 * ORDERING[j]) for j in ITEMS]
    #    solver.add(Distinct(order))
    #    solver.add(And([order[j] <= COUNT[i] for j in ITEMS])) 
                        
    for i in COURIERS:
        courier_items = [Select(X, i * n + j) for j in ITEMS]
        order_constraints = [If(courier_items[j], Select(ORDERING, j), -2 * Select(ORDERING, j)) for j in ITEMS]
        solver.add(Distinct(order_constraints))
        solver.add(And([order_constraints[j] <= Select(COUNT, i) for j in ITEMS]))
        
        dist = Sum([
            Sum([If(And(courier_items[j1], courier_items[j2], Select(ORDERING, j1) + 1 == Select(ORDERING, j2)), D[j1][j2], 0)
                for j2 in ITEMS])
            for j1 in ITEMS
        ])
        dist += Sum([If(And(courier_items[j], Select(ORDERING, j) == 1), D[n][j], 0) for j in ITEMS])
        dist += Sum([If(And(courier_items[j], Select(ORDERING, j) == Select(COUNT, i)), D[j][n], 0) for j in ITEMS])
        solver.add(DISTANCES == Store(DISTANCES, i, dist))
        # Store(DISTANCES, i, dist)
                    
    
    # Total weight constraints
    for i in COURIERS:
        solver.add(Sum([If(Select(X, i * n + j), s[j], 0) for j in ITEMS]) <= l[i])
                    
    # Calculate the distance traveled by each courier
    """ for i in COURIERS:
        dist = Sum([
            Sum([If(And(X[i][j1], X[i][j2], ORDERING[j1] + 1 == ORDERING[j2]),D[j1][j2], 0) for j2 in ITEMS])
            for j1 in ITEMS
            ])
        dist += Sum([If(And(X[i][j], ORDERING[j] == 1), D[n][j], 0) for j in ITEMS])
        dist += Sum([If(And(X[i][j], ORDERING[j] == COUNT[i]), D[j][n], 0) for j in ITEMS])
        solver.add(DISTANCES[i] == dist) """
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    # Simmetry breaking constraints
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
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
    
    if implied_constraints:
        solver.add(And([ORDERING[j] >= 0 for j in ITEMS] + [ORDERING[j] <= n for j in ITEMS]))
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Objective function
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # Minimize the maximum distance traveled
    obj = Int('obj')
    solver.add(obj == maximum([Select(DISTANCES, i) for i in COURIERS]))

    
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Search strategy
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    solver.push()
    solver.set('timeout', millisecs_left(time.time(), timeout))
    
    timeout = time.time() + timeout
    
    model = None
    while solver.check() == sat:
        model = solver.model()
        
        # Get the value of the objective function
        result_objective = model[obj].as_long()
        print(f"New optimal found: {result_objective}")
        
        # Retrieve and print distances
        distances = [model.eval(Select(DISTANCES, i)).as_long() for i in COURIERS]
        print(f"Distances = {distances}")

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
            # Get items delivered by courier i
            items_delivered = [j for j in ITEMS if model.eval(Select(X, i * n + j)) == True]
            
            if len(items_delivered) == 0:
                print(f"Courier {i} did not deliver any items")
                continue
            
            # Get the order in which items were delivered
            orders = {model.eval(Select(ORDERING, j)).as_long(): j for j in items_delivered}
            print(orders)
            
            # Sort items based on their delivery order
            items_delivered = [orders[o] for o in sorted(orders.keys())]
            
            print(f"Courier {i} delivered items {', '.join([str(j) for j in items_delivered])}")
            
            # Calculate the total distance traveled by the courier
            dist = D[n][items_delivered[0]]
            for j, item in enumerate(items_delivered[:-1]):
                dist += D[item][items_delivered[j + 1]]
            dist += D[items_delivered[-1]][n]
            print(f"Courier {i} traveled {dist} units of distance")
        
