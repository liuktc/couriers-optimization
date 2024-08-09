##Funzia ma objective sbagliata e non mi carica i risultati nonostante non mi appaiono sulla schermata
import os
import json
import time
from amplpy import AMPL, add_to_path

# Lista dei solver da testare
SOLVERS = ['cbc', 'glpk', 'scip']

def run_ampl_model(model_file, data_file, solver):
    add_to_path(r'c:/Users/cmaio/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/AMPL IDE.lnk') #Damodificareperreproducibilità
    ampl = AMPL()
    
    try:
        ampl.read(model_file)
        ampl.readData(data_file)
        ampl.setOption('solver', solver)
        ampl.solve()
        
        objective = ampl.getObjective('TotalDistance').value()
        is_optimal = ampl.getValue('solve_result') == "solved"
        solve_time = ampl.getValue('_solve_time')
        
        # Estrai la soluzione
        x = ampl.getVariable('x')
        solution = [[] for _ in range(ampl.getValue('m'))]
        for (i, j), value in x.getValues():
            if value > 0.5:  # Variabile binaria, dovrebbe essere molto vicina a 0 o 1
                solution[i-1].append(j)
        
        return {
            "time": int(solve_time),
            "optimal": is_optimal,
            "obj": objective,
            "sol": solution
        }
    except Exception as e:
        print(f"Error with solver {solver}: {str(e)}")
        return {
            "time": 300,
            "optimal": False,
            "obj": None,
            "sol": None
        }
    finally:
        ampl.close()

def test_model(model_file, data_dir, num_instances):
    results = {}
    instances = sorted([f for f in os.listdir(data_dir) if f.endswith('.dat')])[:num_instances]
    
    for instance in instances:
        instance_name = os.path.splitext(instance)[0]
        print(f"Testing on instance: {instance_name}")
        
        data_file = os.path.join(data_dir, instance)
        instance_results = {}
        
        for solver in SOLVERS:
            print(f"  Using solver: {solver}")
            start_time = time.time()
            result = run_ampl_model(model_file, data_file, solver)
            end_time = time.time()
            
            # Assicurati che il tempo sia almeno 1 secondo e non più di 300 secondi
            result['time'] = max(1, min(300, int(end_time - start_time)))
            
            instance_results[solver] = result
        
        results[instance_name] = instance_results
    
    return results

def main():
    model_file = 'src/milp/models/startmodel.mod'  # Specifica il percorso del tuo modello AMPL
    data_dir = 'src/milp/data'  # Specifica il percorso della directory con i dati convertiti
    results_dir = 'results/MILP'
    num_instances = 1
    
    results = test_model(model_file, data_dir, num_instances)
    
    # Salva i risultati in un file JSON
    results_file = os.path.join(results_dir, 'test_results_multi_solver_experiment.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Test completati. Risultati salvati in '{results_file}'.")

if __name__ == "__main__":
    main()