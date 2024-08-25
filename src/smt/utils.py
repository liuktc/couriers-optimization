from z3 import *
import itertools

def maximum(a):
    m = a[0]
    for v in a[1:]:
        m = If(v > m, v, m)
    return m

def minimum(a):
    m = a[0]
    for v in a[1:]:
        m = If(v < m, v, m)
    return m

def precedes(a1, a2):
    if not a1:
        return True
    if not a2:
        return False
    return Or(a1[0] < a2[0], And(a1[0] == a2[0], precedes(a1[1:], a2[1:])))

def millisecs_left(t, timeout):
    return int((timeout - t) * 1000)    

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
    
""" def get_element_at_index(arr, idx):
    # Create a Z3 array from the list
    z3_array = Array('z3_array', IntSort(), IntSort())
    for i in range(len(arr)):
        z3_array = Store(z3_array, i, arr[i])
    
    # Use Select to get the element at the given index
    return Select(z3_array, idx) """

# -----------------------------------------------------------------------------%
# Constrains the elements of 'path' to define a subcircuit where 'x[i] = j'
# means that 'j' is the successor of 'i' and 'x[i] = i' means that 'i'
# is not in the circuit.
# assignments[i] = j means that packet 'i' is assigned to courier 'j'.
# -----------------------------------------------------------------------------%
def subcircuit(x, tag):
    S = range(len(x))  # index_set(x)
    l = min(S)
    u = max(S)
    n = len(S)

    # Variables
    # order = IntVector(f'order_{tag}', n)
    order = Array(f"order_{tag}", IntSort(), IntSort())
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
    # non_empty_conditions.append(get_element_at_index(order, firstin) == 1)
    non_empty_conditions.append(Select(order, firstin) == 1)

    # The lastin node is greater than firstin.
    non_empty_conditions.append(lastin > firstin)

    # The lastin node points at firstin.
    non_empty_conditions.append(get_element_at_index(x, lastin) == firstin + 1)

    # And both are in
    non_empty_conditions.append(get_element_at_index(ins, lastin))
    non_empty_conditions.append(get_element_at_index(ins, firstin))

    # The successor of each node except where it is firstin is
    # numbered one more than the predecessor.
    #non_empty_conditions.append(And([Implies(And(ins[i], x[i] - 1 != firstin), 
    #                                         get_element_at_index(order, x[i] - 1) == get_element_at_index(order, i) + 1)
    #                                 for i in S]))

    non_empty_conditions.append(And([Implies(And(ins[i], x[i] - 1 != firstin),
                                             Select(order, x[i] - 1) == Select(order, i) + 1)
                                     for i in S]))

    # Each node that is not in is numbered after the lastin node.
    # non_empty_conditions.append(And([Or(ins[i], get_element_at_index(order, lastin) < get_element_at_index(order, i))
    #                                  for i in S]))

    non_empty_conditions.append(And([Or(ins[i], Select(order, lastin) < Select(order, i))
                                      for i in S]))

    constraints.append(Implies(Not(empty), And(non_empty_conditions)))

    return constraints

def subcircuitMTZ(path, tag):
    constraints = []
    n = len(path) - 1
    ITEMS = range(len(path)-1)
    LOCATIONS = range(len(path))
    DEPOT_IDX = len(path)-1

    u = [ Int(f"u_{tag}_{l}") for l in LOCATIONS ]

    for p in ITEMS:
        constraints.append( Implies( path[DEPOT_IDX] == p, u[p] == 1 ) )

    for l1 in ITEMS:
        for l2 in LOCATIONS:
            if l1 == l2: continue
            constraints.append( Implies( path[l1] == l2+1, u[l2] >= (u[l1] + 1) ) )
            constraints.append( u[l1] - u[l2] + 1 <= (n-1) * If(path[l1] == l2+1, 0, 1) )

    return constraints

def get_best_neighbor(path_model, courier_to_optimize, solver, DEPOT, PATH,COURIERS, obj, DISTANCES, D, best_objective, one_courier_solver):
    
    # one_courier_solver = Solver()
    # one_courier_solver.add(Distinct(PATH[courier_to_optimize]))
    # one_courier_solver.add(subcircuit(PATH[courier_to_optimize], f"{courier_to_optimize}_extra"))
    # D_array = Array(f"D_array_{courier_to_optimize}", IntSort(), IntSort())
    # for i in range(DEPOT):
    #     for j in range(DEPOT):
    #         # one_courier_solver.add(Store(D_array, i*DEPOT + j , D[i][j]))
    #         D_array = Store(D_array, i*DEPOT + j , D[i][j])
    # dist = Sum([If(PATH[courier_to_optimize][j] != j + 1, get_element_at_index(D[j], PATH[courier_to_optimize][j] - 1), 0) for j in range(DEPOT)])
    # # dist = Sum([If(PATH[courier_to_optimize][j] != j + 1, D_array[j*DEPOT + PATH[courier_to_optimize][j] - 1], 0) for j in range(DEPOT)]) 
    # 
    # # solver.add(DISTANCES[courier_to_optimize] == dist)
    # one_courier_solver.add(obj == dist)
    one_courier_solver.push()
    one_courier_solver.add(obj < best_objective)
    
    
    # solver.push()
    solutions = 0
    objective = 9999999
    items_delivered = [j for j in range(DEPOT) if path_model[courier_to_optimize][j] != j + 1]
    if len(items_delivered) <= 1:
        return path_model[courier_to_optimize], objective
    best_path = path_model[courier_to_optimize]
    """ for i in COURIERS:
        if i != courier_to_optimize:
            for j in range(DEPOT):
                solver.add(PATH[i][j] == path_model[i][j]) """
    t = 0
    model = None
    for combination in itertools.combinations(items_delivered, 3):
        # print(f"Combination = {combination}")
        sol_per_perm = 0
        for perm in [[combination[1], combination[2], combination[0]],[combination[2], combination[0], combination[1]]]:
            # print(f"Permutation = {perm}")
            if perm == combination:
                continue
            one_courier_solver.push()
            has_to_continue = True
            for j in range(DEPOT):
                if j in perm:
                    if j + 1 == path_model[courier_to_optimize][perm[combination.index(j)]]:
                        has_to_continue = False
                        break
                    one_courier_solver.add(PATH[courier_to_optimize][j] == path_model[courier_to_optimize][perm[combination.index(j)]])
                else:
                    one_courier_solver.add(PATH[courier_to_optimize][j] == path_model[courier_to_optimize][j])
            if not has_to_continue:
                one_courier_solver.pop()
                continue
            # Discard solution that are surely not good
            
            """ solver.add(And([
                PATH[courier_to_optimize][j] == path_model[courier_to_optimize][perm[combination.index(j)]] if j in perm else PATH[courier_to_optimize][j] == path_model[courier_to_optimize][j] for j in range(DEPOT)
            ]))   """      
            
            t += 1
            if one_courier_solver.check() == sat:
                sol_per_perm += 1
                solutions += 1
                model = one_courier_solver.model()
                objective = model[obj].as_long()
                best_path = [model[PATH[courier_to_optimize][j]].as_long() for j in range(DEPOT)]
                # print(f"Sol {solutions}: {objective}")

            one_courier_solver.pop()
            one_courier_solver.add(obj < objective)
    # print(f"Tried {t} solutions")
    solver.pop()
    one_courier_solver.pop()
    return best_path, objective
    
    
def get_solution(path, COURIERS, DEPOT):
    solution = []
    for i in COURIERS:
        items_delivered = []
        
        first_item = int(path[i][DEPOT - 1])
        next_item = first_item
        while next_item != DEPOT:
            items_delivered.append(next_item)
            next_item = int(path[i][next_item - 1])
        
        solution.append(items_delivered)

    return solution