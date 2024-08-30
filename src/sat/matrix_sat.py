from itertools import combinations
from z3 import *
import time
import math

## Utils
def at_least_one(bool_vars):
    return Or(bool_vars)
def at_most_one(bool_vars):
    return And([Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)])
def exactly_one(bool_vars):
    return And(at_most_one(bool_vars), at_least_one(bool_vars))

def Max(vs):
  m = vs[0]
  for v in vs[1:]:
    m = If(v > m, v, m)
  return m

def all_different_except_n(solver, x, n):
    for i in range(len(x)):
            solver.add([Implies(And(Or(x[i] != n, x[j] != n), j!=i), x[j] != x[i]) for j in range(len(x))])

def get_courier_distance(X, m, n, distances):
    ## Useful ranges
    PACKS = range(n)
    COURIERS = range(m)
    DEPOT = (n)
    LOCATIONS = range(DEPOT+1)

    path_distances = []
    for c in COURIERS:
        first_step = Sum([
            If(X[c][p1][0], distances[DEPOT][p1], 0) for p1 in PACKS
        ])
        courier_path = Sum([
            If(And(X[c][p1][k-1], X[c][p2][k]), distances[p1][p2], 0)
            for p2 in PACKS for p1 in PACKS for k in range(1, n) if p2!=p1
        ])
        last_step = Sum([
            Sum([
                If(X[c][p1][n-1], distances[DEPOT][p1], 0) for p1 in PACKS
            ]),
            Sum([
                If(
                    And(X[c][p1][k], Not(at_least_one([X[c][p2][k+1] for p2 in PACKS if p2!=p1]))),
                    distances[p1][DEPOT],
                    0
                )
                for p1 in PACKS for k in range(n-1)
            ])
        ])
        tot_courier_path = Sum([first_step, courier_path, last_step])
        path_distances.append(tot_courier_path)
    return path_distances

# Definition of Model class
class Matrix_Model():
    def __init__(self, instance):
        self.solver, self.X = create_model(
            m = instance['m'],
            n = instance['n'],
            loads = instance['l'],
            sizes = instance['s'],
            distances = instance['D']
        )
        self.instance = instance
        self.distances = instance['D']


    def solve(self, timeout, random_seed):
        set_option("sat.local_search", True)
        self.solver.set("random_seed", random_seed)

        ## Useful ranges
        PACKS = range(self.instance['n'])
        COURIERS = range(self.instance['m'])
        DEPOT = (self.instance['n'])
        LOCATIONS = range(DEPOT+1)

        # Init
        objective = None
        init_time = time.time()
        timeout_timestamp = init_time + timeout
        solve_time = timeout

        optimality = False

        while True:
            self.solver.set("timeout", math.floor(timeout_timestamp - time.time())*1000)
            status = self.solver.check()

            if status == unsat:
                optimality = (objective is not None)
                solve_time = math.floor(time.time() - init_time)
                # Provare a inserire le statistiche come output della solve
                # - :restart : number of restarts 
                # - :memory : max amount of memory needed
                # - :mk-bool-var : number of boolean variables
                # - :conflicts : number of assignments that happen in the theory subsolvers and that did not make the formula true
                print ("statistics for the last check method...")
                stat = self.solver.statistics()
                if 'restarts' in stat.keys():
                    restart = stat.get_key_value('restarts')
                else:
                    restart = 0
                
                if 'max memory' in stat.keys():
                    max_memory = stat.get_key_value('max memory')
                else:
                    max_memory = 0
                
                if 'mk bool var' in stat.keys():
                    mk_bool_var = stat.get_key_value('mk bool var')
                else:
                    mk_bool_var = 0
                
                if 'conflicts' in stat.keys():
                    conflicts = stat.get_key_value('conflicts')
                else:
                    conflicts = 0
                break

            ## Checking timeout:
            if (time.time() >= timeout_timestamp) or status == unknown:
                # Provare a inserire le statistiche come output della solve
                # - :restart : number of restarts 
                # - :memory : max amount of memory needed
                # - :mk-bool-var : number of boolean variables
                # - :conflicts : number of assignments that happen in the theory subsolvers and that did not make the formula true
                print ("statistics for the last check method...")
                stat = self.solver.statistics()
                if 'restarts' in stat.keys():
                    restart = stat.get_key_value('restarts')
                else:
                    restart = 0
                
                if 'max memory' in stat.keys():
                    max_memory = stat.get_key_value('max memory')
                else:
                    max_memory = 0
                
                if 'mk bool var' in stat.keys():
                    mk_bool_var = stat.get_key_value('mk bool var')
                else:
                    mk_bool_var = 0
                
                if 'conflicts' in stat.keys():
                    conflicts = stat.get_key_value('conflicts')
                else:
                    conflicts = 0
                break
            model = self.solver.model()

            

            solution = []
            for c in COURIERS:
                courier_path = []
                for k in PACKS:
                    item = None
                    for p in PACKS:
                        if model.evaluate(self.X[c][p][k]):
                            item = p
                            break
                    if item is None:
                        break
                    else:
                        courier_path.append(item+1)
                solution.append(courier_path)
            
            # Obtain objective value
            path_cost = []
            for c in COURIERS:
                if len(solution[c]) == 0:
                    path_cost.append(0)
                    continue

                cost = (
                    self.distances[DEPOT][solution[c][0]-1] +
                    sum([self.distances[solution[c][k]-1][solution[c][k+1]-1] for k in range(len(solution[c])-1)]) +
                    self.distances[solution[c][-1]-1][DEPOT]
                )

                path_cost.append(cost)
            objective = max(path_cost)

            # Estimating lower bound
            lower_bound = max([self.distances[DEPOT][p] + self.distances[p][DEPOT] for p in PACKS])
            
            if objective == lower_bound:
                optimality = (objective is not None)
                solve_time = math.floor(time.time() - init_time)
                # Provare a inserire le statistiche come output della solve
                # - :restart : number of restarts 
                # - :memory : max amount of memory needed
                # - :mk-bool-var : number of boolean variables
                # - :conflicts : number of assignments that happen in the theory subsolvers and that did not make the formula true
                print ("statistics for the last check method...")
                stat = self.solver.statistics()
                if 'restarts' in stat.keys():
                    restart = stat.get_key_value('restarts')
                else:
                    restart = 0
                
                if 'max memory' in stat.keys():
                    max_memory = stat.get_key_value('max memory')
                else:
                    max_memory = 0
                
                if 'mk bool var' in stat.keys():
                    mk_bool_var = stat.get_key_value('mk bool var')
                else:
                    mk_bool_var = 0
                
                if 'conflicts' in stat.keys():
                    conflicts = stat.get_key_value('conflicts')
                else:
                    conflicts = 0
                break

            # improving total distance travelled by any courier
            path_distances = get_courier_distance(self.X, self.instance['m'], self.instance['n'], self.instance['D'])
            self.solver.add(And([tot_courier_path<objective for tot_courier_path in path_distances]))
            
        
        if (objective is not None):
            return objective, solution, optimality, solve_time, restart, max_memory, mk_bool_var, conflicts
        else:
            return None, None, False, solve_time, restart, max_memory, mk_bool_var, conflicts
    

def create_model(m, n, loads, sizes, distances):
    ## Useful ranges
    PACKS = range(n)
    COURIERS = range(m)
    DEPOT = (n)
    LOCATIONS = range(DEPOT+1)

    solver_unified = Solver()

    ## Decision variables
    X = [[[Bool(f'x_{c}_{p1}_{p2}') for p2 in PACKS] for p1 in PACKS] for c in COURIERS] # X matrix

    ## Constraint - Capacity of each courier
    solver_unified.add(And([Sum([If(X[c][p1][p2], sizes[p1], 0) for p2 in PACKS for p1 in PACKS]) <= loads[c] for c in COURIERS]))
    
    # Implied constraint - each courier deliver at least one pack
    for c in COURIERS:
        solver_unified.add(exactly_one([X[c][p][0] for p in PACKS]))

    ## Constraint - All packages should be taken by exactly one courier in k-th order
    for p in PACKS:
        solver_unified.add(exactly_one([X[c][p][k] for k in PACKS for c in COURIERS]))

    # Every courier can deliver at most one pack for each order
    for c in COURIERS:
        for k in PACKS:
            solver_unified.add(at_most_one([X[c][p][k] for p in PACKS]))
    
    # For every row, the deliveries must not have discontinuities
    for c in COURIERS:
        for k in range(1, n):
            # for correctness, it should have been used exactly_one, but for performances reasons at_least_one
            solver_unified.add(Implies(
                at_least_one([X[c][p][k] for p in PACKS]),
                at_least_one([X[c][p][k-1] for p in PACKS])
            ))

    ##### Estimated distance for the minimum path
    lower_bound = max([distances[DEPOT][p] + distances[p][DEPOT] for p in PACKS])

    path_distances = get_courier_distance(X, m, n, distances)

    Objective = Max(path_distances)

    # Constraint - ensuring distance percurred by each courier to be greater than estimated lower bound
    solver_unified.add(Objective >= lower_bound)

    return solver_unified, X