from z3 import *
import time
from .utils import maximum, precedes, millisecs_left, Min, get_element_at_index, subcircuit
import logging
logger = logging.getLogger(__name__)
    
def SMT_optimizer(m, n, l, s, D, implied_constraints=False, symmetry_breaking=False, timeout=300, **kwargs):
    try:
        DEPOT = n + 1
        COURIERS = range(m)
        ITEMS = range(n)
        
        solver = Optimize()

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
        
        for i in COURIERS:
            for j in ITEMS:
                solver.add(And([If(ASSIGNMENTS[j] != i + 1, PACKS_PER_COURIER[i][j] == 0, PACKS_PER_COURIER[i][j] == j) for j in ITEMS]))
        
        
        
        solver.add(And([And(ASSIGNMENTS[j] >= 1, ASSIGNMENTS[j] <= m) for j in ITEMS]))
                
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
        
        # Count constraints
        for i in COURIERS:
            solver.add(COUNT[i] == Sum([If(ASSIGNMENTS[j] == i + 1, 1, 0) for j in ITEMS]))
            
        # Subcircuit constraints  
        for i in COURIERS:
            solver.add(subcircuit(PATH[i], i))
                            
        # Total weight constraints
        for i in COURIERS:
            solver.add(Sum([If(ASSIGNMENTS[j] == i + 1, s[j], 0) for j in ITEMS]) <= l[i])
                        
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
                
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Objective function
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # Minimize the maximum distance traveled
        obj = Int('obj')
        solver.add(obj == maximum(DISTANCES))
        
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Search strategy
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
        solver.push()    
        solver.set('timeout', millisecs_left(start_timestamp, timeout_timestamp))
                
        # Minimize the objective
        solver.minimize(obj)
        model = None
        start = time.time()
        if solver.check() == sat:
            end = time.time()
            logger.debug(f"Checking model in {end - start} seconds")
            model = solver.model()
            result_objective = model[obj].as_long()
            
            logger.debug(f"New optimal found: {result_objective}")
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
                logger.debug(row)

            solver.pop()
            solver.push()
            solver.add(obj < result_objective)

        result = {
            "time": math.floor(time.time() - start_timestamp),
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