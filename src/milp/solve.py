import os
import json
import time
from amplpy import AMPL, add_to_path

# Lista dei solver da testare, da aggiungerene altri e/o da testare modificadone parametri
SOLVERS = ['cbc', 'scip']

def run_ampl_model(model_file, data_file, solver):
    
    add_to_path(r'c:/Users/cmaio/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/AMPL IDE.lnk') #Damodificareperreproducibilità
    ampl = AMPL()
    
    try:
        ampl.read(model_file)
        ampl.readData(data_file)
        ampl.setOption('solver', solver)
        ampl.setOption(solver + '_options', 'timelimit=300')
        ampl.solve()
        
        objective = ampl.getObjective('ObjectiveMaxDistance').value()
        is_optimal = ampl.getValue('solve_result') == "solved"
        solve_time = ampl.getValue('_solve_time')
        
        # Estrai la soluzione
        assignments = ampl.getVariable('A')
        path = ampl.getVariable('X')
        m = ampl.getValue('m')
        n = ampl.getValue('n')
        
        #Questa soluzione mostra i pacchi che prende ciascun corrriere
        solution = []
        for couriers in range(1,m+1):
            couriers_packages = []
            for packs in range(1,n+1):
                if assignments[packs, couriers].value() == 1:
                    couriers_packages.append(packs)
            solution.append(couriers_packages)
            
        #solution = [[[] for _ in range(1,n+2)] for _ in range (1,n+2)]
        #for i in range(1,n+2):
            #for j in range(1,n+2):
                #for k in range(1,m+1):
                    #solution[i,j,k] = path[i,j,k].value()
                    
        #Da aggiungere altre info al risultiato finale!!!
        return {
            "time": solve_time,
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
            #start_time = time.time()
            result = run_ampl_model(model_file, data_file, solver)
            #end_time = time.time()
            #result['time'] = end_time - start_time 
            
            instance_results[solver] = result
        
        results[instance_name] = instance_results
    
    return results

def main():
    model_file = 'src/milp/models/model1.mod'  
    data_dir = 'src/milp/data'  
    results_dir = 'results/MILP'
    num_instances = 10
    
    results = test_model(model_file, data_dir, num_instances)
    
    # Salva i risultati in un file JSON (da modificare!)
    results_file = os.path.join(results_dir, 'test_results_multi_solver_experiment.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Test completati. Risultati salvati in '{results_file}'.")

if __name__ == "__main__":
    main()