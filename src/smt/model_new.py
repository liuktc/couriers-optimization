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
    

def Min(lst):
    # Start with the first element as the minimum.
    min_value = lst[0]
    
    # Iterate through the list, updating min_value with the smallest element found.
    for elem in lst[1:]:
        min_value = If(elem < min_value, elem, min_value)
    
    return min_value

def get_element_at_index(arr, idx):
    # Start with the first element as the default
    selected = arr[0]
    
    # Iterate through the list, select the element where the index matches
    for i in range(1, len(arr)):
        selected = If(idx == i, arr[i], selected)
    
    return selected
    
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
    for i in COURIERS:
        solver.add(Distinct(ORDERS[i]))
            
    for i in COURIERS:
        solver.add(And([And(ORDERS[i][j] <= n) for j in range(n + 1)])) 
        solver.add(And([If(assignments[j] == i + 1,
                           path[i][j] != j + 1,
                           path[i][j] == j + 1) for j in range(n + 1)]))
        solver.add(And([If(assignments[j] == i + 1,
                           ORDERS[i][j] + 1 == ORDERS[i][path[i][j] - 1],
                           ORDERS[i][j] == -j) for j in range(n + 1)])) 
        
def subcircuit_chatgpt(x, tag):
    S = range(len(x))  # index_set(x)
    l = min(S)
    u = max(S)
    n = len(S)

    # Variables
    order = IntVector(f'order_{tag}', n)
    ins = [Bool(f'ins_{i}_{tag}') for i in S]
    for i in S:
        ins[i] = (x[i] != i + 1)

    firstin = Int(f'firstin_{tag}')
    lastin = Int(f'lastin_{tag}')
    empty = Bool(f'empty_{tag}')

    constraints = []

    # Constraints for order and firstin
    constraints.append(Distinct(x))
    constraints.append(Distinct(order))
    constraints.append(firstin == Min([If(ins[i], i, u+1) for i in S]))
    constraints.append(empty == (firstin > u))

    # If the subcircuit is empty, then each node points at itself.
    for i in S:
        constraints.append(Implies(empty, Not(ins[i])))

    # If the subcircuit is non-empty, then order numbers the subcircuit.
    non_empty_conditions = []

    # The firstin node is numbered 1.
    non_empty_conditions.append(get_element_at_index(order, firstin) == 1)

    # The lastin node is greater than firstin.
    non_empty_conditions.append(lastin > firstin)

    # The lastin node points at firstin.
    #non_empty_conditions.append(x[lastin] == firstin)
    non_empty_conditions.append(get_element_at_index(x, lastin) == firstin + 1)

    # And both are in
    #non_empty_conditions.append(ins[lastin])
    #non_empty_conditions.append(ins[firstin])
    non_empty_conditions.append(get_element_at_index(ins, lastin))
    non_empty_conditions.append(get_element_at_index(ins, firstin))

    # The successor of each node except where it is firstin is
    # numbered one more than the predecessor.
    #for i in S:
    #    non_empty_conditions.append(Implies(And(ins[i], x[i] - 1 != firstin), 
    #                                         get_element_at_index(order, x[i] - 1) == get_element_at_index(order, i) + 1))

    non_empty_conditions.append(And([Implies(And(ins[i], x[i] - 1 != firstin), 
                                             get_element_at_index(order, x[i] - 1) == get_element_at_index(order, i) + 1)
                                     for i in S]))
    # Each node that is not in is numbered after the lastin node.
    # for i in S:
    #    non_empty_conditions.append(Or(ins[i], get_element_at_index(order, lastin) < get_element_at_index(order, i)))
    non_empty_conditions.append(And([Or(ins[i], get_element_at_index(order, lastin) < get_element_at_index(order, i))
                                      for i in S]))

    constraints.append(Implies(Not(empty), And(non_empty_conditions)))

    return constraints

def SMT_new(m, n, l, s, D, implied_constraints=False, simmetry_breaking=False, timeout=300, **kwargs):
    try:
        DEPOT = n + 1
        COURIERS = range(m)
        ITEMS = range(n)
        
        solver = Solver()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
        # Decision variables
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        ASSIGNMENTS = [Int(f"x__{j}") for j in ITEMS]

        solver.add(And([And(ASSIGNMENTS[j] >= 1, ASSIGNMENTS[j] <= m) for j in ITEMS]))

        PATH = [[Int(f"path_{i}_{j}") for j in range(DEPOT)] for i in COURIERS]
        
        solver.add(PATH[0][0] != PATH[1][0])
        
        for i in COURIERS:
            for j in ITEMS:
                solver.add(If(ASSIGNMENTS[j] == i + 1, PATH[i][j] != j + 1, PATH[i][j] == j + 1))
                
            for j in range(DEPOT):
                solver.add(PATH[i][j] >= 1)
                solver.add(PATH[i][j] <= DEPOT)
                if j == DEPOT - 1:
                    solver.add(PATH[i][j] != n + 1)
        
        for i in COURIERS:
            solver.add(Distinct(PATH[i]))
        
        # Rapresents the distance traveled by each courier
        DISTANCES = [Int(f"distance_{i}") for i in COURIERS]
        
        # Count[i] == k means that courier i delivered k items
        COUNT = [Int(f"count_{i}") for i in COURIERS]
        
        # Count constraints
        for i in COURIERS:
            solver.add(COUNT[i] == Sum([If(ASSIGNMENTS[j] == i + 1, 1, 0) for j in ITEMS]))
            
        for i in COURIERS:
            solver.add(subcircuit_chatgpt(PATH[i], i))
                            
        # Total weight constraints
        for i in COURIERS:
            solver.add(Sum([If(ASSIGNMENTS[j] == i + 1, s[j], 0) for j in ITEMS]) <= l[i])
                        
        start = time.time()
        # Calculate the distance traveled by each courier
        for i in COURIERS: 
            dist = Sum([
                Sum([If(And(ASSIGNMENTS[j1] == i + 1,
                            ASSIGNMENTS[j2] == i + 1, 
                            PATH[i][j1] == j2 + 1),
                        D[j1][j2],
                        0) for j2 in ITEMS])
                for j1 in ITEMS
                ])
            dist += Sum([If(PATH[i][j] == n + 1, D[j][n], 0) for j in range(DEPOT)])
            dist += Sum([If(j == PATH[i][n], D[n][j], 0) for j in range(DEPOT)])
            solver.add(DISTANCES[i] == dist)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        # Simmetry breaking constraints
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        # Implied constraints
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
        
        lower_bound = max([D[n][j] + D[j][n] for j in ITEMS])
        
        max_distances = [max(D[i][:-1]) for i in range(n)]
        max_distances.sort()
        if implied_constraints:
            upper_bound = sum(max_distances[m:]) + max(D[n]) + max([D[j][n] for j in range(n)])
        else:
            upper_bound = sum(max_distances[1:]) + max(D[n]) + max([D[j][n] for j in range(n)])

        solver.add(obj >= lower_bound)
        solver.add(obj <= upper_bound)
        
        
        timeout_timestamp = time.time() + timeout*1000
        start_timestamp = time.time()
        solver.push()    
        solver.set('timeout', millisecs_left(start_timestamp, timeout_timestamp))
        
        model = None
        while solver.check() == sat:
            model = solver.model()
            result_objective = model[obj].as_long()
            
            """ print(f"New optimal found: {result_objective}")
            print(f"Distances = {[model[DISTANCES[i]].as_long() for i in COURIERS]}")
            print(f"Counts = {[model[COUNT[i]].as_long() for i in COURIERS]}")
            print(f"Assignments = {[model[ASSIGNMENTS[j]].as_long() for j in ITEMS]}")
            
            print("PATH = ")
            for i in COURIERS:
                row = [model[PATH[i][j]].as_long() for j in range(DEPOT)]
                print(row) """

            solver.pop()
            solver.push()
            solver.add(obj < result_objective)
            
            now = time.time()
            if now >= timeout_timestamp:
                break
            solver.set('timeout', millisecs_left(now, timeout_timestamp))
        
        result = {
            "time": math.ceil(time.time() - start_timestamp),
            "optimal": "",
            "obj": "",
            "sol": ""
        }
        if model is not None:
            if result["time"] >= timeout:
                result["optimal"] = False
            else:
                result["optimal"] = True
                
            result["obj"] = model[obj].as_long()
            
            # Calculate the solution
            solution = []
            for i in COURIERS:
                items_delivered = []
                
                first_item = int(model[PATH[i][DEPOT - 1]].as_long())
                next_item = first_item
                while next_item != DEPOT:
                    items_delivered.append(next_item)
                    next_item = int(model[PATH[i][next_item - 1]].as_long())
                
                solution.append(items_delivered)

            result["sol"] = solution
            
        return result
    except z3.z3types.Z3Exception as e:
        return  {
            "time": "",
            "optimal": "",
            "obj": "",
            "sol": ""
        }