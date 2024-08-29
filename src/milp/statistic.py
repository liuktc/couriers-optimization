import os
import json
import time
import logging 
import pathlib
from amplpy import AMPL, add_to_path
from io import StringIO 
import sys
import matplotlib.pyplot as plt



class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout



logger = logging.getLogger(__name__)

# Lista dei solver da testare, da aggiungerene altri e/o da testare modificadone parametri -> con highs non so cosa succeda...
SOLVERS = ['scip', 'highs']
#SOLVERS = ['highs']

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
        if ampl.getValue('solve_result') == 'failure' or ampl.getValue('solve_result') == 'infeasible' or ampl.getValue('solve_result') == 'limit' : raise Exception
        
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
    simplex_iterations = {}
    branching_nodes = {}

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
            terminal_txts = ""
            with Capturing() as output:
                result = run_ampl_model(
                    model_file = model["model_path"],
                    data_file = data_file,
                    solver = solver,
                    timeout = timeout
                )
                terminal_txts = output

            result["__extras"] = {}
            for line in terminal_txts:
                print(line)
                if "simplex iterations" in line:
                    result["__extras"]["simplex_iterations"] = int(line.split(" ")[0])
                elif "branching nodes" in line:
                    result["__extras"]["branching_nodes"] = int(line.split(" ")[0])
            simplex_iterations[model_str] = result["__extras"]["simplex_iterations"]
            branching_nodes[model_str] = result["__extras"]["branching_nodes"]
            out_results[model_str] = result
            #print(out_results)
    return out_results, simplex_iterations, branching_nodes


def access_statistics():
    iterations_initial_model_scip = []
    iterations_initial_model_highs = []
    iterations_implied_model_scip = []
    iterations_implied_model_highs = []
    iterations_symmetry_model_scip = []
    iterations_symmetry_model_highs = []
    nodes_initial_model_scip = []
    nodes_initial_model_highs = []
    nodes_implied_model_scip = []
    nodes_implied_model_highs = []
    nodes_symmetry_model_scip = []
    nodes_symmetry_model_highs = []
    
    for istance in range(1,11):
        _, si, bn= solve('', istance, 300)
        iterations_initial_model_scip.append(si['initial-model_scip'])
        iterations_initial_model_highs.append(si['initial-model_highs'])
        iterations_implied_model_scip.append(si['implied-model_scip'])
        iterations_implied_model_highs.append(si['implied-model_highs'])
        iterations_symmetry_model_scip.append(si['symmetry-model_scip'])
        iterations_symmetry_model_highs.append(si['symmetry-model_highs'])
        nodes_initial_model_scip.append(bn['initial-model_scip'])
        nodes_initial_model_highs.append(bn['initial-model_highs'])
        nodes_implied_model_scip.append(bn['implied-model_scip'])
        nodes_implied_model_highs.append(bn['implied-model_highs'])
        nodes_symmetry_model_scip.append(bn['symmetry-model_scip'])
        nodes_symmetry_model_highs.append(bn['symmetry-model_highs'])
    
    
    plt.subplot(1,2,1)
    plt.plot(range(1,11), iterations_implied_model_scip, marker='o', linestyle='-')
    plt.plot(range(1,11), iterations_initial_model_scip, marker='o', linestyle='-')
    plt.plot(range(1,11), iterations_symmetry_model_scip, marker='o', linestyle='-'  )
    plt.title('scip')
    plt.legend(['implied-model', 'initial-model', 'symmetry-model'])
    plt.xlabel('Istances')
    plt.ylabel('Simplex iterations')
    plt.subplot(1,2,2)
    plt.plot(range(1,11), iterations_implied_model_highs, marker='o', linestyle='-')
    plt.plot(range(1,11), iterations_initial_model_highs, marker='o', linestyle='-')
    plt.plot(range(1,11), iterations_symmetry_model_highs, marker='o', linestyle='-')
    plt.title('highs')
    plt.legend(['implied-model', 'initial-model', 'symmetry-model'])
    plt.xlabel('Istances')
    plt.ylabel('Simplex iterations')
    plt.show()
    
    plt.subplot(1,2,1)
    plt.plot(range(1,11), nodes_implied_model_scip, marker='o', linestyle='-')
    plt.plot(range(1,11), nodes_initial_model_scip, marker='o', linestyle='-')
    plt.plot(range(1,11), nodes_symmetry_model_scip, marker='o', linestyle='-')
    plt.title('scip')
    plt.legend(['implied-model', 'initial-model', 'symmetry-model'])
    plt.xlabel('Istances')
    plt.ylabel('Branching nodes')
    plt.subplot(1,2,2)
    plt.plot(range(1,11), nodes_implied_model_highs, marker='o', linestyle='-')
    plt.plot(range(1,11), nodes_initial_model_highs, marker='o', linestyle='-')
    plt.plot(range(1,11), nodes_symmetry_model_highs, marker='o', linestyle='-')
    plt.title('highs')
    plt.legend(['implied-model', 'initial-model', 'symmetry-model'])
    plt.xlabel('Istances')
    plt.ylabel('Branching nodes')
    plt.show()


if __name__ == '__main__':
    access_statistics()