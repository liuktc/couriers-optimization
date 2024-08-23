from itertools import combinations
from z3 import *
import time
import math

## Utils
def at_least_one(bool_vars):
    return Or(bool_vars)
def at_most_one(bool_vars):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]
def exactly_one(bool_vars):
    return at_most_one(bool_vars) + [at_least_one(bool_vars)]

def Max(vs):
  m = vs[0]
  for v in vs[1:]:
    m = If(v > m, v, m)
  return m


# Definition of Unified Model
class Unified_Model():
    def __init__(self, instance):
        self.solver, self.assignment, self.paths = create_model(
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
            objective = max([
                sum([
                    self.distances[loc1][loc2] if model.evaluate(self.paths[c][loc1][loc2]) else 0
                        for loc1 in LOCATIONS for loc2 in LOCATIONS if loc1!=loc2
                ])
            for c in COURIERS ])
        
            # Compose solution
            solution = []
            # paths_distance = []
            for c in COURIERS:
                courier_path = []

                loc1 = DEPOT
                # distance = 0
                while True:
                    step = sum([loc2+1 if model.evaluate(self.paths[c][loc1][loc2]) else 0 for loc2 in LOCATIONS if loc1!=loc2])
                    if step == 0: break # This courier does not deliver anything

                    # distance += self.distances[loc1][step-1]
                    if (step-1) == DEPOT:
                        break
                    else:
                        loc1 = step-1
                        courier_path.append(step)

                solution.append(courier_path)
                # paths_distance.append(distance)
            solution_ls.append(solution)

            # objective = max(paths_distance)
        
            # solution = [[sum([loc2+1 for loc2 in LOCATIONS if (model.evaluate(paths[c][loc1][loc2]) and loc1!=loc2)]) for loc1 in LOCATIONS] for c in COURIERS]

            # print(f'Objective: {objective}')
            # print(f'Solution: {solution}')

            for c in COURIERS:
                total_distance = Sum([If(self.paths[c][loc1][loc2], self.distances[loc1][loc2], 0) for loc1 in LOCATIONS for loc2 in LOCATIONS if loc1!=loc2])
                self.solver.add(total_distance < objective)
            
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

    ###### Previous assignment model
    # Decision variables
    assignments = [[Bool(f"a_{p}_{c}") for c in COURIERS] for p in PACKS]


    solver_unified = Solver()

    # Capacity constraint - assure that sum of weights of a singular courier is under its load limit
    for c in COURIERS:
        sum_load = Sum([If(assignments[p][c], sizes[p], 0) for p in PACKS])
        solver_unified.add(sum_load <= loads[c])
    
    # Capacity constraint - ensure that each pack is delivered only by a courier
    for p in PACKS:
        solver_unified.add(exactly_one([assignments[p][c] for c in COURIERS]))
    

    

    ###### Previous paths model
    # Decision variables
    # assignments = [[Bool(f"a_{p}_{c}") for c in COURIERS] for p in PACKS]
    paths = [[[Bool(f'p_{c}_{loc1}_{loc2}') for loc2 in LOCATIONS] for loc1 in LOCATIONS] for c in COURIERS]

    # Auxiliar variables
    # carry_num = [[Bool(f'c_{c}_{p1}') for p1 in PACKS] for c in COURIERS] # Counter of how many packages a courier is delivering

    # for c in COURIERS:
    #     for p in PACKS:
    #         solver_unified.add(carry_num[c][p] == assignments[p][c])
    
    # Soft Constraint for symmetry breaking
    # for c1 in COURIERS:
    #     for c2 in COURIERS:
    #         if (c1 < c2 and loads[c1]==loads[c2]):
    #             for p1 in PACKS:
    #                 for p2 in PACKS:
    #                     solver_unified.add(Implies(And(carry_num[c1][p1], carry_num[c2][p2]), p1 <= p2))
                # solver_paths.add(carry_num[c1] <= carry_num[c2])

    ## Path related constraints
    # 1 - Nel path deve esistere uno step con valore del pacco True con indice = DEPOT (n+1)
    for c in COURIERS:
        # If courier has at_least_one package to deliver, its path[c][DEPOT] must have a destination != DEPOT
        solver_unified.add(Implies(at_least_one([assignments[p][c] for p in PACKS]), paths[c][DEPOT][DEPOT]==False))

        # If courier has no package to deliver, it can stay in DEPOT
        solver_unified.add(Implies(Not(at_least_one([assignments[p][c] for p in PACKS])), paths[c][DEPOT][DEPOT]==True))

        for p in PACKS:
            solver_unified.add(Implies(assignments[p][c], paths[c][p][p]==False))
            solver_unified.add(Implies(Not(assignments[p][c]), paths[c][p][p]==True))

    # 2 - ensuring pack is delivered by a single courier only once
    for c in COURIERS:
        for loc in LOCATIONS:
            solver_unified.add(exactly_one([paths[c][loc][ind] for ind in LOCATIONS]))

    ## Subcircuit constraint
    # 1 - alldifferent per ogni path di ogni courier
    for c in COURIERS:
        for loc in LOCATIONS:
            solver_unified.add(exactly_one([paths[c][ind][loc] for ind in LOCATIONS]))

    # 2 - subtour elimination
    # Variables: u[i] to prevent subtours
    u = [[[Bool(f"u_{i}_{j}_{k}") for k in PACKS] for j in PACKS] for i in COURIERS]

    # Constraining assignment of truth value of u decision variable
    for c in COURIERS:
        # u del primo pacco = 1
        for p in PACKS:
            solver_unified.add(Implies(paths[c][DEPOT][p], u[c][p][0]==True))

        # u_j >= u_i + 1
        for p1 in PACKS:
            for p2 in PACKS:
                if p1 == p2:
                    continue

                for k in PACKS:
                    solver_unified.add(Implies(And(paths[c][p1][p2], u[c][p1][k]), And(exactly_one([u[c][p2][i] for i in range(k+1, n)]))))

    ## Exatcly one true value for each u_p1
    for c in COURIERS:
        for p1 in PACKS:
            solver_unified.add(exactly_one(u[c][p1]))

    # Applying MTZ formulation constraint
    # u_i - u_j + 1 <= (n - 1) * (1 - paths[c, i, j])
    for c in COURIERS:
        for p1 in PACKS: # i
            for p2 in PACKS: #j
                if p1 == p2:
                    continue

                for k1 in PACKS:
                    for k2 in PACKS:
                        solver_unified.add(Implies(And(u[c][p1][k1], u[c][p2][k2]), k1 - k2 + 1 <= (n-1) * (1-If(paths[c][p1][p2], 1, 0))))
    

    ##### Estimated distance for the minimum path
    lower_bound = max([distances[DEPOT][p] + distances[p][DEPOT] for p in PACKS])

    Objective = Max([
        Sum([
            If(paths[c][loc1][loc2], distances[loc1][loc2], 0)
                for loc1 in LOCATIONS for loc2 in LOCATIONS if loc1!=loc2
        ])
    for c in COURIERS ])

    # Constraint - ensuring distance percurred by each courier to be greater than estimated lower bound
    solver_unified.add(Objective >= lower_bound)
    # for c in COURIERS:
    #     total_distance = Sum([If(self.paths[c][loc1][loc2], self.distances[loc1][loc2], 0) for loc1 in LOCATIONS for loc2 in LOCATIONS if loc1!=loc2])
    #     self.solver.add(total_distance >= lower_bound)

    return solver_unified, assignments, paths