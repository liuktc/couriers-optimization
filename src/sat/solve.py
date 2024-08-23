from .total_sat import Unified_Model
import time
import multiprocessing
import logging
logger = logging.getLogger(__name__)



def modelRunner(ModelClass, instance, timeout, random_seed, queue):
    objective = None
    solution = None
    optimality = False
    solve_time = timeout

    try:
        start_model_init = time.time()

        def_model = ModelClass(instance)
        model_init_time = round(time.time() - start_model_init)
        logger.info(f"Model created")
        
        objective, solution, optimality, solve_time = def_model.solve(timeout-model_init_time, random_seed)
        solve_time = solve_time + model_init_time
    except Exception as e:
        logger.error(f"Exception {e}")

    result = {}

    if objective is not None:
        result = {
            'obj': objective,
            'sol': solution,
            'optimal': optimality,
            'time': solve_time,
        }
    else:
        result = {
            'obj': None,
            'sol': None,
            'optimal': False,
            'time': timeout,
        }
    queue.put(result, block=False)


def solve(instance, timeout, cache={}, random_seed=42, **kwargs):
    
    models = {
        'unified-model': Unified_Model
    }

    results = {}

    for model in models.keys():
        logger.info(f"Starting model {model}")

        # Check if result is in cache
        if model in cache:
            logger.info(f"Cache hit")
            results[model] = cache[model]
            continue
        
        res = None
        runner_queue = multiprocessing.Queue()
        proc = multiprocessing.Process(target=modelRunner, args=(models[model], instance, timeout, random_seed, runner_queue))
        try:
            proc.start()
            res = runner_queue.get(block=True, timeout=timeout+1) # Tolerance to wait for Z3 timeout
        except Exception as e:
            logger.error(f"Exception {e}")
        finally:
            proc.terminate()

        if res is None:
            results[model] = {
                'obj': None,
                'sol': None,
                'optimal': False,
                'time': timeout,
            }
        else:
            results[model] = res

    return results