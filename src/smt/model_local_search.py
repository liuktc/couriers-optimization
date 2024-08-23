from z3 import *
import time
from utils import maximum, precedes, millisecs_left, Min, get_element_at_index, subcircuit, get_best_neighbor, minimum
import itertools
import logging
logger = logging.getLogger(__name__)
# Disable debug logging
# logger.setLevel(logging.INFO)

# from tqdm import tqdm

best_objective = 99999999
best_path = None
  
    
def SMT_local_search(m, n, l, s, D, implied_constraints=False, symmetry_breaking=False, timeout=300, **kwargs):
    try:
        encoding_start = time.time()
        
        DEPOT = n + 1
        COURIERS = range(m)
        ITEMS = range(n)
        
        solver = Optimize()
        solver_assignment = Optimize()
        one_courier_solvers = [Solver() for i in COURIERS]
        
            

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
        # Decision variables
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # Assignments[j] == i means that item j is assigned to courier i
        ASSIGNMENTS = [Int(f"x__{j}") for j in ITEMS]
        
        # Path[i][j] == j means that courier i doesn't deliver item j
        # Path[i][j] == k != j means that courier i delivers item j and goes from pack j to pack k
        PATH = [[Int(f"path_{i}_{j}") for j in range(DEPOT)] for i in COURIERS]

        # Rapresents the distance traveled by each courier
        DISTANCES = [Int(f"distance_{i}") for i in COURIERS]
        
        # Count[i] == k means that courier i delivered k items
        COUNT = [Int(f"count_{i}") for i in COURIERS]
        
        # PACKS_PER_COURIER = [[Int(f"packs_per_courier_{j}_{i}") for j in ITEMS] for i in COURIERS]
        
        """ for i in COURIERS:
            for j in ITEMS:
                solver.add(And([If(ASSIGNMENTS[j] != i + 1, PACKS_PER_COURIER[i][j] == 0, PACKS_PER_COURIER[i][j] == j) for j in ITEMS]))
        """       # solver_assignment.add(And([If(ASSIGNMENTS[j] != i + 1, PACKS_PER_COURIER[i][j] == 0, PACKS_PER_COURIER[i][j] == j) for j in ITEMS]))
        
        
        

        
        
        
        solver.add(And([And(ASSIGNMENTS[j] >= 1, ASSIGNMENTS[j] <= m) for j in ITEMS]))
        solver_assignment.add(And([And(ASSIGNMENTS[j] >= 1, ASSIGNMENTS[j] <= m) for j in ITEMS]))
                
        for i in COURIERS:
            for j in ITEMS:
                solver.add(If(ASSIGNMENTS[j] == i + 1, PATH[i][j] != j + 1, PATH[i][j] == j + 1))
                
            for j in range(DEPOT):
                solver.add(PATH[i][j] >= 1)
                solver.add(PATH[i][j] <= DEPOT)
                if j == DEPOT - 1:
                    solver.add(Implies(COUNT[i] > 0,PATH[i][j] != n + 1))
        
        for i in COURIERS:
            solver.add(Distinct(PATH[i]))
        
        # Count constraints
        for i in COURIERS:
            solver.add(COUNT[i] == Sum([If(ASSIGNMENTS[j] == i + 1, 1, 0) for j in ITEMS]))
            solver_assignment.add(COUNT[i] == Sum([If(ASSIGNMENTS[j] == i + 1, 1, 0) for j in ITEMS]))
            
        # Subcircuit constraints  
        for i in COURIERS:
            solver.add(subcircuit(PATH[i], i))
                            
        # Total weight constraints
        for i in COURIERS:
            solver.add(Sum([If(ASSIGNMENTS[j] == i + 1, s[j], 0) for j in ITEMS]) <= l[i])
            solver_assignment.add(Sum([If(ASSIGNMENTS[j] == i + 1, s[j], 0) for j in ITEMS]) <= l[i])
                        
        # Calculate the distance traveled by each courier
        for i in COURIERS:
            dist = Sum([If(PATH[i][j] != j + 1, get_element_at_index(D[j], PATH[i][j] - 1), 0) for j in range(DEPOT)])
            solver.add(DISTANCES[i] == dist)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        # Simmetry breaking constraints
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if symmetry_breaking:
            # --- Ordering on the amount of delivered packages ---
            for i1 in COURIERS:
                for i2 in COURIERS:
                    if i1 < i2 and l[i1] == l[i2]:
                        solver.add(COUNT[i1] <= COUNT[i2])
                        # solver_assignment.add(COUNT[i1] <= COUNT[i2])
                        
            # --- Ordering on the index of the delivered packages ---
            for i1 in COURIERS:
                for i2 in COURIERS:
                    if i1 < i2 and l[i1] == l[i2]:
                        solver.add(precedes(PACKS_PER_COURIER[i1], PACKS_PER_COURIER[i2]))
                        # solver_assignment.add(precedes(PACKS_PER_COURIER[i1], PACKS_PER_COURIER[i2]))
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        # Implied constraints
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if implied_constraints:
            for i in COURIERS:
                solver.add(COUNT[i] > 0)
                solver_assignment.add(COUNT[i] > 0)
                    
                
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Objective function
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # Minimize the maximum distance traveled
        obj = Int('obj')
        solver.add(obj == maximum([DISTANCES[i] for i in COURIERS]))
        # solver.minimize(obj)
        
        for i in COURIERS:
            one_courier_solvers[i].add(Distinct(PATH[i]))
            one_courier_solvers[i].add(subcircuit(PATH[i], f"{i}_extra"))
            dist = Sum([If(PATH[i][j] != j + 1, get_element_at_index(D[j], PATH[i][j] - 1), 0) for j in range(DEPOT)])
            one_courier_solvers[i].add(obj == dist)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Soft constraints
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # As a first solution for the solver, set the elements of PATH to be ordered in increasing order
        """ solver.push()
        for i in COURIERS:
            for j in ITEMS:
                solver.add_soft(Implies(ASSIGNMENTS[j] == i + 1, PATH[i][j] > j + 1)) """
        
        ABS_DIFF = [[Int(f"abs_diff_{i}_{j}") for j in COURIERS] for i in COURIERS]

        for i in COURIERS:
            for j in COURIERS:
                if i < j:
                    solver_assignment.add(ABS_DIFF[i][j] == Abs(COUNT[i] - COUNT[j]))
                else:
                    solver_assignment.add(ABS_DIFF[i][j] == 0)
                    
        sum_abs_diff = maximum([ABS_DIFF[i][j] for i in COURIERS for j in COURIERS if i < j]) 
        # solver_assignment.minimize(sum_abs_diff)
        solver_assignment.add_soft(And([COUNT[i] <= ((n*3)//(m*2)) for i in COURIERS]))
        solver_assignment.add_soft(And([COUNT[i] >= n//m for i in COURIERS]))
        
        
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
        
        
        timeout_timestamp = time.time() + timeout
        start_timestamp = time.time()
        
        solver.set('timeout', millisecs_left(start_timestamp, timeout_timestamp))
        solver_assignment.set('timeout', millisecs_left(start_timestamp, timeout_timestamp))
        
        logger.debug(f"Econding took {time.time() - encoding_start} seconds")        
        
        
        model = None
        global best_objective
        global best_path
        best_objective = 99999999
        best_path = None
        while solver_assignment.check() == sat:
            model_assignment = solver_assignment.model()
            result_assignment = [model_assignment.evaluate(ASSIGNMENTS[j]).as_long() for j in ITEMS]
            
            logger.debug(f"Result assignment = {result_assignment}")
            # logger.debug COUNT
            logger.debug(f"COUNT = {[model_assignment.evaluate(COUNT[i]).as_long() for i in COURIERS]}")
            solver.push()
            solver_assignment.push()
            for j in ITEMS:
                solver.add(ASSIGNMENTS[j] == result_assignment[j])
                # solver_assignment.add(ASSIGNMENTS[j] == result_assignment[j])
                
            now = time.time()
            if now >= timeout_timestamp:
                break
            
            solver.set('timeout', millisecs_left(now, timeout_timestamp))
            solver.push()
            start = time.time()
            objective = None
            logger.debug("Try to find a path for the given assignment")
            # Find the trivial assignments
            delivered_per_courier = []
            for i in COURIERS:
                d = []
                for j in ITEMS:
                    if model_assignment.evaluate(ASSIGNMENTS[j]).as_long() == i + 1:
                        d.append(j + 1)
                        
                d.append(DEPOT)
                delivered_per_courier.append(d)

            logger.debug(f"Delivered per courier = {delivered_per_courier}")
            solver.push()
            for i in COURIERS:
                for j in range(len(delivered_per_courier[i])):
                    if j < len(delivered_per_courier[i]) - 1:
                        solver.add_soft(PATH[i][delivered_per_courier[i][j] - 1] == delivered_per_courier[i][j + 1])
                        # logger.debug(f"PATH[{i}][{delivered_per_courier[i][j] - 1}] == {delivered_per_courier[i][j + 1]}")
                    else:
                        solver.add_soft(PATH[i][delivered_per_courier[i][j] - 1] == delivered_per_courier[i][0])
                        # logger.debug(f"PATH[{i}][{delivered_per_courier[i][j] - 1}] == {delivered_per_courier[i][0]}")

            if solver.check() == sat:
                courier_to_optimize = 0
                new_optimal = False
                model = solver.model()
                solver.pop()
                result_objective = model[obj].as_long()
                objective = result_objective
                
                if objective < best_objective:
                    best_objective = objective
                    logger.debug(f"\n-----------------------------------\nFound a new best solution with objective value {best_objective} in {time.time() - start} seconds\n-----------------------------------\n")
                    
                
                
                logger.debug(f"Found a new solution with objective value {result_objective} in {time.time() - start} seconds")
                # solver.add(obj < result_objective)
                path_model = [[model[PATH[i][j]].as_long() for j in range(DEPOT)] for i in COURIERS]
                # logger.debug("PATH = ", path_model)
                distances = [model[DISTANCES[i]].as_long() for i in COURIERS]
                logger.debug("Distances = ", distances)
                already_optimized = [distances[i] < result_objective for i in COURIERS]
                logger.debug(f"Couriers to optimize = {[i for i in range(m) if not already_optimized[i]]}")
                while courier_to_optimize < m:
                    # Check timeout
                    if time.time() >= timeout_timestamp:
                        break
                    if not already_optimized[courier_to_optimize]:
                        logger.debug(f"Courier to optimize = {courier_to_optimize}")
                        
                        # logger.debug(f"PATH = {path_model}")
                        #implementation of local search
                        
                        # Calculate all the permutations of each path row
                        # By only considering the permutations that are valid, we can reduce the search space
                        # So we take 3 elements from each path row and shuffle them
                        """ solver.push()
                        # FIX ALL THE PATH EXCEPT THE ONES THAT ARE BEING OPTIMIZED
                        for i in COURIERS:
                            for j in range(DEPOT):
                                if i != courier_to_optimize:
                                    solver.add(PATH[i][j] == path_model[i][j]) """
                        new_path, last_objective = get_best_neighbor(path_model, courier_to_optimize, solver, DEPOT, PATH,COURIERS, obj, DISTANCES, D, best_objective, one_courier_solvers[courier_to_optimize])
                        # solver.pop()
                        if new_path == path_model[courier_to_optimize]:
                            logger.debug(f"No improvement found for courier {courier_to_optimize}")
                            already_optimized[courier_to_optimize] = True
                        else:
                            new_optimal = True
                            logger.debug(f"Found a new best path for courier {courier_to_optimize} with distance {last_objective}")
                            """ if last_objective < objective:
                                objective = last_objective """
                            # solver.add(obj < last_objective)
                            # objective = last_objective
                            # Constraint the best path on courier courier_to_optimize
                            path_model[courier_to_optimize] = new_path
                            best_path = path_model
                            """ for j in range(DEPOT):
                                solver.add(PATH[courier_to_optimize][j] == best_path[j]) """
                        
                    
                    if courier_to_optimize == m - 1:
                        if new_optimal:
                            # Find the values by fixing the path values
                            solver.push()
                            for i in COURIERS:
                                for j in range(DEPOT):
                                    solver.add(PATH[i][j] == path_model[i][j])
                                    
                            is_sat = solver.check() == sat
                            if not is_sat:
                                logger.debug("Error: model is not satisfiable")
                                break
                            model = solver.model()
                            solver.pop()
                            
                            result_objective = model[obj].as_long()
                            objective = result_objective
                            
                            
                            courier_to_optimize = 0
                            logger.debug(f"New step to find new solution with obj val {objective}")
                                
                            # solver.add(obj < objective)
                            path_model = [[model[PATH[i][j]].as_long() for j in range(DEPOT)] for i in COURIERS]
                            distances = [model[DISTANCES[i]].as_long() for i in COURIERS]
                            logger.debug("New distances = ", distances)
                            already_optimized =  [distances[i] < result_objective for i in COURIERS]
                            logger.debug(f"Couriers to optimize = {[i for i in range(m) if not already_optimized[i]]}")
                            
                            if objective < best_objective:
                                best_objective = objective
                                best_path = path_model
                                logger.debug(f"\n-----------------------------------\nFound a new best solution with objective value {best_objective} in {time.time() - start} seconds\n-----------------------------------\n")
                            new_optimal = False
                            continue
                        else:
                            break
                    
                    courier_to_optimize += 1
                logger.debug("Finished optimizing")       
                # Add the optimized path_model to the constraints
                solver.push()
                for i in COURIERS:
                    for j in range(DEPOT):
                        solver.add(PATH[i][j] == path_model[i][j])
                        
                # Check if the model is satisfiable and in that case, save it
                if solver.check() == sat:
                    logger.debug("Checking model")
                    model = solver.model()
                    objective_new = model[obj].as_long()
                    logger.debug(f"Found a new solution with objective value {objective_new} in {time.time() - start} seconds")
                    if objective_new < best_objective:
                        best_objective = objective_new
                        logger.debug(f"\n-----------------------------------\nFound a new best solution with objective value {best_objective} in {time.time() - start} seconds\n-----------------------------------\n")
                    
                else:
                    logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nModel is not satisfiable\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                    logger.debug(f"PATH = {[path_model[i][j] for i in COURIERS for j in range(DEPOT)]}")
                solver.pop()
                
            logger.debug(f"Popping solver and adding objective constraint with objective value {objective}")
            solver.pop()
            solver.pop()
            # if objective is not None:
            #     solver.add(obj < objective)
            if objective is not None and objective < best_objective:
                best_objective = objective
                best_path = path_model
                logger.debug(f"\n-----------------------------------\nFound a new best solution with objective value {best_objective} in {time.time() - start} seconds\n-----------------------------------\n")
                
            
            # The new solution must be different from the previous one
            solver_assignment.add(Or([ASSIGNMENTS[j] != result_assignment[j] for j in ITEMS]))
            
            now = time.time()
            if now >= timeout_timestamp:
                break
            
            solver_assignment.set('timeout', millisecs_left(now, timeout_timestamp))
            
            
            """ logger.debug(f"New optimal found: {result_objective}")
            logger.debug(f"Distances = {[model[DISTANCES[i]].as_long() for i in COURIERS]}")
            logger.debug(f"Counts = {[model[COUNT[i]].as_long() for i in COURIERS]}")
            logger.debug(f"Assignments = {[model[ASSIGNMENTS[j]].as_long() for j in ITEMS]}")
            
            logger.debug("PATH = ")
            for i in COURIERS:
                row = [model[PATH[i][j]].as_long() for j in range(DEPOT)]
                logger.debug(row)
                
            logger.debug("PACKS_PER_COURIER = ")
            for i in COURIERS:
                row = [model[PACKS_PER_COURIER[i][j]].as_long() for j in ITEMS]
                logger.debug(row) """
        
        result = {
            "time": math.ceil(time.time() - start_timestamp),
            "optimal": False,
            "obj": None,
            "sol": None
        }
        if model is not None:
            if result["time"] >= timeout:
                result["time"] = timeout
                result["optimal"] = False
            else:
                result["optimal"] = True
                
            result["obj"] = best_objective
            
            # Calculate the solution
            solution = []
            path = best_path
            for i in COURIERS:
                items_delivered = []
                
                first_item = int(path[i][DEPOT - 1])
                next_item = first_item
                while next_item != DEPOT:
                    items_delivered.append(next_item)
                    next_item = int(path[i][next_item - 1])
                
                solution.append(items_delivered)

            result["sol"] = solution
            
        return result
    except z3types.Z3Exception as e:
        logger.debug(e)
        return  {
            "time": timeout,
            "optimal": False,
            "obj": None,
            "sol": None
        }
        
    except Exception as e:
        logger.debug(e)
        return  {
            "time": timeout,
            "optimal": False,
            "obj": None,
            "sol": None
        }