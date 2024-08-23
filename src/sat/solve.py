from .total_sat import Unified_Model
import time
import signal
import logging
logger = logging.getLogger(__name__)



def signalHandler(signum, frame):
    raise Exception("Model init timeout")


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

        objective = None
        solution = None
        optimality = False
        solve_time = timeout

        # Declaration of the Model class
        try:
            start_model_init = time.time()

            # Signal to stop model creation on timeout
            signal.signal(signal.SIGALRM, signalHandler)
            signal.alarm(timeout)
            def_model = models[model](instance)
            signal.alarm(0)

            model_init_time = round(time.time() - start_model_init)
            logger.info(f"Model created")
            
            objective, solution, optimality, solve_time  = def_model.solve(timeout-model_init_time, random_seed)
        except Exception as e:
            logger.error(f"Exception {e}")
            
        if objective is not None:
            results[model] = {
                'obj': objective,
                'sol': solution,
                'optimal': optimality,
                'time': solve_time + model_init_time,
            }
        else:
            results[model] = {
                'obj': None,
                'sol': None,
                'optimal': False,
                'time': timeout,
            }
    return results