from z3 import *
import time
from utils import maximum, precedes, millisecs_left, get_element_at_index, subcircuit, get_best_neighbor, get_solution
import itertools
import logging
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)
    
def SMT_local_search(m, n, l, s, D, implied_constraints=False, symmetry_breaking=False, timeout=300, **kwargs):
    try:
        encoding_start = time.time()
        
        DEPOT = n + 1
        COURIERS = range(m)
        ITEMS = range(n)
        
        solver = Optimize()
        solver_assignment = Optimize() # Using Optimize instead of Solver to use soft constraints 
        one_courier_solvers = [Solver() for i in COURIERS] # Used for performance improvements
        
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
        
        PACKS_PER_COURIER = [[Int(f"packs_per_courier_{j}_{i}") for j in ITEMS] for i in COURIERS]
        
        
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

            # --- Ordering on the index of the delivered packages ---
            for i1 in COURIERS:
                for i2 in COURIERS:
                    if i1 < i2 and l[i1] == l[i2]:
                        solver.add(precedes(PACKS_PER_COURIER[i1], PACKS_PER_COURIER[i2]))
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
        
        for i in COURIERS:
            one_courier_solvers[i].add(Distinct(PATH[i]))
            one_courier_solvers[i].add(subcircuit(PATH[i], f"{i}_extra"))
            dist = Sum([If(PATH[i][j] != j + 1, get_element_at_index(D[j], PATH[i][j] - 1), 0) for j in range(DEPOT)])
            one_courier_solvers[i].add(obj == dist)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Soft constraints
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # The solver_assignment first try to find more equally distributed items
        solver_assignment.add_soft(And([COUNT[i] <= (n//m) + 1 for i in COURIERS]))
        solver_assignment.add_soft(And([COUNT[i] >= n//m for i in COURIERS]))
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Upper and lower bounds
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        lower_bound = max([D[n][j] + D[j][n] for j in ITEMS])
        
        max_distances = [max(D[i][:-1]) for i in range(n)]
        max_distances.sort()
        upper_bound = sum(max_distances[1:]) + max(D[n]) + max([D[j][n] for j in range(n)])

        solver.add(obj >= lower_bound)
        solver.add(obj <= upper_bound)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Searching
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        timeout_timestamp = time.time() + timeout
        start_timestamp = time.time()
        
        solver.set('timeout', millisecs_left(start_timestamp, timeout_timestamp))
        solver_assignment.set('timeout', millisecs_left(start_timestamp, timeout_timestamp))
        
        logger.debug(f"Econding took {time.time() - encoding_start} seconds")        
        
        
        best_objective = upper_bound
        best_path = None
        while solver_assignment.check() == sat:
            model_assignment = solver_assignment.model()
            result_assignment = [model_assignment.evaluate(ASSIGNMENTS[j]).as_long() for j in ITEMS]
            
            logger.debug(f"Result assignment = {result_assignment}")
            logger.debug(f"COUNT = {[model_assignment.evaluate(COUNT[i]).as_long() for i in COURIERS]}")

            # Set the found assignment solution to the solver
            solver.push()
            solver_assignment.push()
            for j in ITEMS:
                solver.add(ASSIGNMENTS[j] == result_assignment[j])
                
            now = time.time()
            if now >= timeout_timestamp:
                break
            
            solver.set('timeout', millisecs_left(now, timeout_timestamp))
            solver.push()
            start = time.time()

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
                        solver.add(PATH[i][delivered_per_courier[i][j] - 1] == delivered_per_courier[i][j + 1])
                    else:
                        solver.add(PATH[i][delivered_per_courier[i][j] - 1] == delivered_per_courier[i][0])

            if solver.check() == sat:
                courier_to_optimize = 0
                new_optimal = False
                model = solver.model()
                solver.pop()
                result_objective = model[obj].as_long()
                
                path_model = [[model[PATH[i][j]].as_long() for j in range(DEPOT)] for i in COURIERS]
                distances = [model[DISTANCES[i]].as_long() for i in COURIERS]
                already_optimized = [distances[i] < result_objective for i in COURIERS]

                logger.debug(f"Found a new solution with objective value {result_objective} in {time.time() - start} seconds")
                logger.debug(f"Distances = {distances}")
                logger.debug(f"Couriers to optimize = {[i for i in range(m) if not already_optimized[i]]}")
                
                
                if result_objective < best_objective:
                    best_objective = result_objective
                    best_path = path_model
                    print(f"\n-----------------------------------\nFound a new best solution with objective value {best_objective} in {time.time() - start} seconds\n-----------------------------------\n")
                
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # LOCAL SEARCH
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                #
                # Calculate the neighboring path solutions, by only considering the permutations
                # of 3 items that are valid. In this way, we can reduce the search space and find
                # an approximation of the optimal solution faster.
                while courier_to_optimize < m:
                    # Check timeout
                    if time.time() >= timeout_timestamp:
                        break
                    if not already_optimized[courier_to_optimize]:
                        logger.debug(f"Courier to optimize = {courier_to_optimize}")
                        new_path, last_objective = get_best_neighbor(path_model, courier_to_optimize,  obj, best_objective, one_courier_solvers[courier_to_optimize], timeout_timestamp, upper_bound,DEPOT, PATH)

                        # If no improvement found
                        if new_path == path_model[courier_to_optimize]:
                            logger.debug(f"No improvement found for courier {courier_to_optimize}")
                            already_optimized[courier_to_optimize] = True
                        else:
                            new_optimal = True
                            path_model[courier_to_optimize] = new_path
                            logger.debug(f"Found a new best path for courier {courier_to_optimize} with distance {last_objective}")
                            
                            # Check the found solution
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
                            path_model = [[model[PATH[i][j]].as_long() for j in range(DEPOT)] for i in COURIERS]
                            distances = [model[DISTANCES[i]].as_long() for i in COURIERS]
                            logger.debug("New distances = ", distances)
                            
                            if result_objective < best_objective:
                                best_objective = result_objective
                                best_path = path_model
                                print(f"\n-----------------------------------\nFound a new best solution with objective value {best_objective} in {time.time() - start} seconds\n-----------------------------------\n")
                    
                    if time.time() >= timeout_timestamp:
                        break  
                    
                    # If optimized all the couriers in this step
                    if courier_to_optimize == m - 1:
                        # If new optimal found, repeat the optimization
                        if new_optimal:
                            # Find the values by fixing the path values
                            solver.push()
                            for i in COURIERS:
                                for j in range(DEPOT):
                                    solver.add(PATH[i][j] == path_model[i][j])
                                    
                            if not solver.check() == sat:
                                logger.debug("Error: model is not satisfiable")
                                break
                            model = solver.model()
                            solver.pop()
                            result_objective = model[obj].as_long()
                            
                            # Restart the optimization
                            courier_to_optimize = 0
                                
                            path_model = [[model[PATH[i][j]].as_long() for j in range(DEPOT)] for i in COURIERS]
                            distances = [model[DISTANCES[i]].as_long() for i in COURIERS]
                            already_optimized =  [distances[i] < result_objective for i in COURIERS]
                            
                            logger.debug(f"New step to find new solution with obj val {result_objective}")
                            logger.debug("New distances = ", distances)
                            logger.debug(f"Couriers to optimize = {[i for i in range(m) if not already_optimized[i]]}")
                            
                            if result_objective < best_objective:
                                best_objective = result_objective
                                best_path = path_model
                                print(f"\n-----------------------------------\nFound a new best solution with objective value {best_objective} in {time.time() - start} seconds\n-----------------------------------\n")
                            new_optimal = False
                            continue
                        else:
                            # If no improvement found, break the optimization
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
                    path_model = [[model[PATH[i][j]].as_long() for j in range(DEPOT)] for i in COURIERS]
                    if objective_new < best_objective:
                        best_objective = objective_new
                        best_path = path_model
                        print(f"\n-----------------------------------\nFound a new best solution with objective value {best_objective} in {time.time() - start} seconds\n-----------------------------------\n")
                    
                else:
                    logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nModel is not satisfiable\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                    logger.debug(f"PATH = {[path_model[i][j] for i in COURIERS for j in range(DEPOT)]}")
                solver.pop()
                
            logger.debug(f"Popping solver and adding objective constraint with objective value {best_objective}")
            solver.pop()
            solver.pop()    
            
            # The new solution must be different from the previous one
            solver_assignment.add(Or([ASSIGNMENTS[j] != result_assignment[j] for j in ITEMS]))
            
            now = time.time()
            if now >= timeout_timestamp:
                break
            
            solver_assignment.set('timeout', millisecs_left(now, timeout_timestamp))
        
        result = {
            "time": math.ceil(time.time() - start_timestamp),
            "optimal": False,
            "obj": None,
            "sol": None
        }
        if best_path is not None:
            if result["time"] >= timeout:
                result["time"] = timeout
                result["optimal"] = False
            else:
                result["optimal"] = True
                
            result["obj"] = best_objective
            result["sol"] = get_solution(best_path, COURIERS, DEPOT)
            
        return result
    except z3types.Z3Exception as e:
        print(e)
        if best_path is not None:
            return {
                "time": timeout,
                "optimal": False,
                "obj": best_objective,
                "sol": get_solution(best_path, COURIERS, DEPOT)
            }
        else:
            return  {
                "time": timeout,
                "optimal": False,
                "obj": None,
                "sol": None
            }
        
    """ except Exception as e:
        print(e)
        if best_path is not None:
            return {
                "time": timeout,
                "optimal": False,
                "obj": best_objective,
                "sol": get_solution(best_path, COURIERS, DEPOT)
            }
        else:
            return  {
                "time": timeout,
                "optimal": False,
                "obj": None,
                "sol": None
            } """