from .total_sat import Unified_Model, call_model

def solve(instance, timeout, cache={}, random_seed=42, **kwargs):
    
    models = {
        'Unified Model': Unified_Model
    }

    results = {
    }

    for model in models.keys():
    
        # Declaration of the Model class
        def_model = models[model](instance)

        # Setting timeout
        # def_model.solver.set('timeout', 4000)

        results[model] = call_model(def_model, instance, timeout, random_seed)
    
    # print(results)
    
    return results