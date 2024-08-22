import os
import json
import time
import logging 
import pathlib
from amplpy import AMPL, add_to_path

logger = logging.getLogger(__name__)

# Lista dei solver da testare, da aggiungerene altri e/o da testare modificadone parametri -> con highs non so cosa succeda...
#SOLVERS = ['scip', 'highs', 'gcg']
SOLVERS = ['scip']

def run_ampl_model(model_file, data_file, solver, timeout):
    
    #add_to_path(r'c:/Users/cmaio/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/AMPL IDE.lnk') #Damodificareperreproducibilità
    ampl = AMPL()
    try:
        ampl.read(model_file)
        ampl.readData(data_file)
        ampl.setOption('solver', solver)
        ampl.setOption(solver + '_options', f'timelimit={timeout}')
        
        #DA MOGLIORARE
        #if solver == 'cbc':
            #ampl.option['cbc_options'] = "preprocess=on roundingHeuristic=on greedyHeuristic=on"
        #elif solver == 'scip':
            #ampl.option['scip_options'] = "heuristics/shiftandpropagate/freq = 1 numerics/feastol = 1e-6"
        #elif solver == 'highs':
            #ampl.option['highs_options'] = "presolve=on parallel=on mip_heuristic_effort=0.5 mip_rel_gap=1e-4"
        #else:
            #raise ValueError(f"Solver non supportato: {solver}")
        
        ampl.solve()
        objective = ampl.getObjective('ObjectiveMaxDistance').value()
        is_optimal = ampl.getValue('solve_result') == "solved"
        solve_time = ampl.getValue('_solve_time')
        
        #ALTRI PARAMETRI DA STAMPARE NELLA SOLUZIONE
        #iterations = ampl.getValue('solve_iterations')
        #nodes = ampl.getValue('solve_nodes')
        #memory_used = ampl.getValue('solve_result_memory_used')
        #cuts = ampl.getValue('solve_result_num_cuts')
        
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
        
        #solution = np.zeros((n+1,n+1,m))
        #for i in range(1,n+2):
            #for j in range(1,n+2):
                #for k in range(1,m+1):
                    #if X[i,j,k].value() == 1:
                        #solution[i-1,j-1,k-1] = 1
        
        #print(solution)
        
        #Da aggiungere altre info al risultiato finale!!!
        return {
            "time": int(solve_time),
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
            print(out_results)
    return out_results



#def main():
    #model_dir = 'src/milp/models/'
    #models_file = ['initial_model.mod', 'model_with_implied_constraint.mod', 'model_with_symmetry_breaking.mod']
    #data_dir = 'src/milp/data'  
    #results_dir = 'results/MILP'
    #num_instances = 1
    
    #Salva i risultati nei file json specificati per istanza
    #for i in range(1,num_instances+1):
        #print(f'Testing on instance number {i}')
        #models_result = {}
        #for model_file in models_file:
            #percorso_model = os.path.join(model_dir, model_file)
            #for solver in SOLVERS: 
                #print(f'Testing on model: {model_file} with solver {solver}')
                #results = test_model(percorso_model, data_dir, i-1, solver)
                #models_result[model_file + ' using ' + solver] = results
        #percorso = os.path.join(results_dir, f'{i}.json')
        #with open(percorso, 'w') as f:
            #json.dump(models_result, f, indent=2)
    
    #print(f"Test completati. Risultati salvati nell'apposita directory.")

if __name__ == '__main__':
    solve(instance=' ', instance_number = 4, timeout=300)
    
