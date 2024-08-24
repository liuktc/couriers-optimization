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


# Definition of Unified Model
class Unified_MILPlike_Model():
    def __init__(self, instance):
        self.solver, self.X, self.T = create_model(
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
        solution_ls = []
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
                break

            ## Checking timeout:
            if (time.time() >= timeout_timestamp) or status == unknown:
                break
            model = self.solver.model()

            # obtain Objective value
            # objective = max([
            #     sum([
            #         self.distances[loc1][loc2] if model.evaluate(self.paths[c][loc1][loc2]) else 0
            #             for loc1 in LOCATIONS for loc2 in LOCATIONS if loc1!=loc2
            #     ])
            # for c in COURIERS ])

            solution = []
            path_distances = []
            for c in COURIERS:
                # Init each courier path
                courier_path = []

                # Compose first step and insert it in the path
                first_step = sum([loc+1 if model.evaluate(self.T[c][0][loc]) else 0 for loc in LOCATIONS])
                courier_path.append(first_step)

                distance = 0
                for k in PACKS:
                    if k==0:
                        # Compose destination of first step
                        next_step = sum([loc+1 if model.evaluate(self.T[c][k][loc]) else 0 for loc in LOCATIONS])
                        courier_path.append(next_step)

                        distance += self.distances[self.instance['n']+1][ next_step ]
                    elif (model.evaluate(self.T[c][k][0])==True and model.evaluate(self.T[c][k-1][0])==False):
                        # Compose last step
                        last_step = self.instance['n']
                        courier_path.append(last_step)

                        distance += self.distances[ sum([loc+1 if model.evaluate(self.T[c][k-1][loc]) else 0 for loc in LOCATIONS]) ][ last_step ]
                    elif model.evaluate(self.T[c][k][0])==False:
                        # Compose next step
                        next_step = sum([loc+1 if model.evaluate(self.T[c][k][loc]) else 0 for loc in LOCATIONS])
                        courier_path.append(next_step)

                        distance += self.distances[ sum([loc+1 if model.evaluate(self.T[c][k-1][loc]) else 0 for loc in LOCATIONS]) ][ next_step ]
                    else:
                        distance += 0
                solution.append(courier_path)
                path_distances.append(distance)
            solution_ls.append(solution)

            objective = max(path_distances)


            for c in COURIERS:
                total_distance = Sum([
                    If(
                        k==0,
                        self.distances[self.instance['n']+1][ sum([loc+1 if model.evaluate(self.T[c][k][loc]) else 0 for loc in LOCATIONS]) ],
                        If(
                            (model.evaluate(self.T[c][k][0])==True and model.evaluate(self.T[c][k-1][0])==False),
                            self.distances[ sum([loc+1 if model.evaluate(self.T[c][k-1][loc]) else 0 for loc in LOCATIONS]) ][ self.instance['n'] ],
                            If(
                                model.evaluate(self.T[c][k][0])==False,
                                self.distances[ sum([loc+1 if model.evaluate(self.T[c][k-1][loc]) else 0 for loc in LOCATIONS]) ][ sum([loc+1 if model.evaluate(self.T[c][k][loc]) else 0 for loc in LOCATIONS]) ],
                                0
                            )
                        )
                    )
                    for k in PACKS])
                self.solver.add(total_distance<objective)


            '''
            [ sum(k in 1..n)(
            if k == 1 then
                D[ n+1, T[i, k] ]
            elseif T[i, k] == 0 /\ T[i, k-1] != 0 then
                D[ T[i, k-1], n+1 ]
            elseif T[i, k] != 0 then
                D[ T[i, k-1], T[i, k] ]
            else
                0
            endif
            ) | i in 1..m ] 
            '''

            # for c in COURIERS:
            #     total_distance = Sum([If(self.paths[c][loc1][loc2], self.distances[loc1][loc2], 0) for loc1 in LOCATIONS for loc2 in LOCATIONS if loc1!=loc2])
            #     self.solver.add(total_distance < objective)
            
            # Constraint to ensure new assignments are different than ones already tried
            # self.solver.add(Not(And([model.evaluate(self.assignment[p][c]) == self.assignment[p][c] for c in COURIERS for p in PACKS])))

            # Provare a inserire le statistiche come output della solve
            # print ("statistics for the last check method...")
            # print (s.statistics())
            # # Traversing statistics
            # for k, v in s.statistics():
            #     print ("%s : %s" % (k, v))
        
        if (objective is not None):
            return objective, solution_ls[-1], optimality, solve_time
        else:
            return None, None, False, solve_time
    

def create_model(m, n, loads, sizes, distances):
    ## Useful ranges
    PACKS = range(n)
    COURIERS = range(m)
    DEPOT = (n)
    LOCATIONS = range(DEPOT+1)

    solver_unified = Solver()

    ## Decision variables
    X = [[[Bool(f'x_{c}_{p1}_{p2}') for p2 in PACKS] for p1 in PACKS] for c in COURIERS] # X matrix
    T = [[[Bool(f't_{c}_{p1}_{loc}') for loc in LOCATIONS] for p1 in PACKS] for c in COURIERS]

    ## Constraint - Capacity of each courier
    solver_unified.add(And([Sum([If(X[c][p1][p2], sizes[p2], 0) for p2 in PACKS for p1 in PACKS]) <= loads[c] for c in COURIERS]))
    # for c in COURIERS:
    #     solver_unified.add(Sum([If(X[c][p1][p2], sizes[p2], 0) for p2 in PACKS for p1 in PACKS]) <= loads[c])

    ## Constraint - All packages should be taken by exactly one courier
    for c in COURIERS:
        for p in PACKS:
            solver_unified.add(exactly_one([X[c][p][k] for k in PACKS]))
    
    # For every row, the deliveries must not have discontinuities
    for c in COURIERS:
        for k in range(1, n):
            solver_unified.add(Implies(Sum([If(Not(X[c][p][k-1]), 1, 0) for p in PACKS]) == n, Sum([If(Not(X[c][p][k]), 1, 0) for p in PACKS]) == n))

    # Each courier must deliver all different packs (except the deposit = n)
    for c in COURIERS:
        all_different_except_n(solver_unified,[Sum([If(T[c][k][loc], loc, 0) for loc in LOCATIONS]) for k in PACKS], n)
    
    # Order of packs delivered by each courier
    for c in COURIERS:
        for k in PACKS:
            for loc in PACKS:
                solver_unified.add(Implies(X[c][loc][k]==True, T[c][k][loc]==True))
    
    ##### Estimated distance for the minimum path
    lower_bound = max([distances[DEPOT][p] + distances[p][DEPOT] for p in PACKS])

    path_distances = []
    for c in COURIERS:
        courier_distance = Sum([
            If(k==0,
               Sum([If(T[c][k][loc], distances[n][loc], 0) for loc in LOCATIONS]),
               If(And(T[c][k][0], Not(T[c][k-1][0])),
                  Sum([If(T[c][k-1][loc], distances[loc][n], 0) for loc in LOCATIONS]),
                  If(Not(T[c][k][0]),
                     Sum([If(And(T[c][k-1][loc1], T[c][k][loc2]), distances[loc1][loc2], 0) for loc2 in LOCATIONS for loc1 in LOCATIONS]),
                     0))) for k in PACKS])
        path_distances.append(courier_distance)

    Objective = Max(path_distances)

    solver_unified.add(Objective >= lower_bound)

    return solver_unified, X, T