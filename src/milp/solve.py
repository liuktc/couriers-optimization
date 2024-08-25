import os
import json
#import subprocess
import logging 
import pathlib
#import re
from amplpy import AMPL, add_to_path, DataFrame
#import matplotlib.pylab as plt

logger = logging.getLogger(__name__)

# Lista dei solver da testare, da aggiungerene altri e/o da testare modificadone parametri
SOLVERS = ['scip', 'highs']
#SOLVERS = ['highs']

#def generate_initial_solution(m, n, l, s, D):
#    """
#    Genera una soluzione iniziale per il problema di routing dei corrieri.
#    
#    :param m: Numero di corrieri
#    :param n: Numero di pacchi
#    :param l: Lista delle capacità dei corrieri
#    :param s: Lista delle dimensioni dei pacchi
#    :param D: Matrice delle distanze
#    :return: Due dizionari rappresentanti A_start e X_start
#    """
#    DEPOT = n + 1
#    A_start = {(i, k): 0 for i in range(1, n+1) for k in range(1, m+1)}
#    X_start = {(i, j, k): 0 for i in range(1, n+2) for j in range(1, n+2) for k in range(1, m+1)}
#    
#    unassigned = set(range(1, n+1))
#    
#    for k in range(1, m+1):
#        current = DEPOT
#        remaining_capacity = l[k-1]
#        
#        while unassigned and remaining_capacity > 0:
#            next_pack = min(unassigned, key=lambda x: D[current-1][x-1] if s[x-1] <= remaining_capacity else float('inf'))
#            if D[current-1][next_pack-1] == float('inf'):
#                break
#            
#            A_start[(next_pack, k)] = 1
#            X_start[(current, next_pack, k)] = 1
#            remaining_capacity -= s[next_pack-1]
#            unassigned.remove(next_pack)
#            current = next_pack
#        
#        X_start[(current, DEPOT, k)] = 1
#    
#    # Assegna eventuali pacchi rimasti al corriere con più capacità residua
#    for pack in unassigned:
#        best_courier = max(range(1, m+1), key=lambda k: l[k-1] - sum(s[i-1] for i in range(1, n+1) if A_start[(i, k)] == 1))
#        A_start[(pack, best_courier)] = 1
#    
#    return A_start, X_start
#
def run_ampl_model(model_file, data_file, solver, timeout):
    
    #add_to_path(r'c:/Users/cmaio/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/AMPL IDE.lnk') #Damodificareperreproducibilità
    ampl = AMPL()
    try:
        ampl.read(model_file)
        ampl.readData(data_file)
        
       # ######Warm Start#######
       # m = ampl.get_parameter('m').value()
       # n = ampl.get_parameter('n').value()
       # l = [ampl.get_parameter('l')[i] for i in range(1, m+1)]
       # s = [ampl.get_parameter('s')[i] for i in range(1, n+1)]
       # D = [[ampl.get_parameter('D')[i,j] for j in range(1, n+2)] for i in range(1, n+2)]
       # 
       # 
       # A_start, X_start = generate_initial_solution(m, n, l, s, D)
       # A_data = {'i': [], 'k': [], 'A_value': []}
       # for i in range(1, n+1):
       #      for k in range(1, m+1):
       #          A_data['i'].append(str(i))
       #          A_data['k'].append(str(k))
       #          A_data['A_value'].append(str(A_start[(i, k)]))
       # A_df = DataFrame.fromDict(A_data)
       #
       # X_data = {'i' : [], 'j' : [], 'k' : [], 'X_value' : []}
       # for i in range(1,n+2):
       #     for j in range(1,n+2):
       #         for k in range(1,m+1):
       #             X_data['i'].append(str(i))
       #             X_data['j'].append(str(j))
       #             X_data['k'].append(str(k))
       #             X_data['X_value'].append(str(X_start[(i,j,k)]))
       # X_df = DataFrame.fromDict(X_data)
       # print('aaaaaaaaaa')
       # # Passa la soluzione iniziale ad AMPL
       # ampl.set_data(A_df, 'A')
       # ampl.set_data(X_df, 'X')
       # 
       # #####endWarmStart######
       
        ampl.setOption('solver', solver)
        ampl.setOption(solver + '_options', f'timelimit={timeout}')
        
        #DA MOGLIORARE
        #if solver == 'cbc':
            #ampl.option['cbc_options'] = "preprocess=on roundingHeuristic=on greedyHeuristic=on"
        #elif solver == 'scip':
            #ampl.option['scip_options'] = "heuristics/shiftandpropagate/freq = 1 numerics/feastol = 1e-6"
        if solver == 'highs':
            ampl.option['highs_options'] = "presolve=on parallel=on mip_heuristic_effort=0.5 mip_rel_gap=1e-4" 
        
        ampl.solve()
        objective = ampl.getObjective('ObjectiveMaxDistance').value()
        is_optimal = ampl.getValue('solve_result') == "solved"
        solve_time = ampl.getValue('_solve_time')
        if ampl.getValue('solve_result') == 'failure' or ampl.getValue('solve_result') == 'infeasible' or ampl.getValue('solve_result') == 'limit'  : raise Exception
        
        #iterations = ampl.getValue('_solve_problem.niter')
        #solve_result = ampl.getOutput('solve;')
        #memory_used = ampl.getValue('solve_result_memory_used')
        #cuts = ampl.getValue('solve_result_num_cuts')
        #gap = ampl.getValue('solve_mip_gap')
        #simplex_iterations = ampl.getValue('solve_simplex_iterations')
        
        # Estrai la soluzione
        A = ampl.getVariable('A')
        X = ampl.getVariable('X')
        m = ampl.getValue('m')
        n = ampl.getValue('n')
        
        #Questa soluzione mostra i pacchi che prende ciascun corrriere -> non so se effettivamente è ordinato...
        #solution = []
        #for couriers in range(1,m+1):
            #couriers_packages = []
            #for packs in range(1,n+1):
                #if A[packs, couriers].value() == 1:
                    #couriers_packages.append(packs)
            #solution.append(couriers_packages)
         
        #for packs in range(1,n+1):
        #    for couriers in range(1, m+1):
        #        print(round(A[packs, couriers].value()), end=' ')
        #    print()
        
        #IN ALCUNI CASI MI VA IN UN LOOP INFINITO, C'E' QUALCHE PROBELMA COL MODELLO...  
        solution = []
        for couriers in range(1,m+1):
            couriers_packs = []
            packs = n + 1
            while round(X[packs, n+1, couriers].value()) == 0:
                for i in range(1, n + 1):
                    if round(X[packs, i, couriers].value()) == 1:
                        couriers_packs.append(i)
                        packs = i
                        break
            solution.append(couriers_packs)
        
    
        return {
            "time": solve_time,
            "optimal": is_optimal,
            "obj": int(objective),
            "sol": solution,
            #'iterations' : iterations,
            #'nodes' : nodes,
            #'memory used' : memory_used,
            #'cuts' : cuts
        }
    except Exception as e:
        print(f"Error with solver {solver} and model {model_file}: {str(e)}")
        return {
            "time": timeout,
            "optimal": False,
            "obj": None,
            "sol": None
        }
    finally:
        ampl.close()

models_setup = [
    {
        "name": "initial-model",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/initial_model.mod"),
    },
    {
        "name": "implied-model",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/model_with_implied_constraint.mod"),
    },
    {
        "name": "symmetry-model",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/model_with_symmetry_breaking.mod"),
    },
    #{
     #   "name": "warm-start-model",
     #   "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/warmstart_model.mod"),
    #},
    
]


def solve(instance, instance_number, timeout=300, cache={}, random_seed = 42):
    
    data_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), './data')
    data_instance = sorted([f for f in os.listdir(data_dir) if f.endswith('.dat')])[instance_number-1]
    data_file = os.path.join(data_dir, data_instance)
    
    out_results = {}
    for model in models_setup:
        for solver in SOLVERS:
            logger.info(f"Starting model {model['name']} with {solver}")
            model_str = model['name'] + '_' + solver
            # Check if result is in cache
            if model_str in cache:
                logger.info(f"Cache hit")
                out_results[model_str] = cache[model_str]
                continue
        
        # Solve instance
            result = run_ampl_model(
                model_file = model["model_path"],
                data_file = data_file,
                solver = solver,
                timeout = timeout
            )
            
            out_results[model_str] = result
            #print(out_results)
    return out_results

if __name__ == '__main__':
   solve('', 1, 300)
