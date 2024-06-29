from .minizinc_utils import minizincSolve
import pathlib
import os
import json
import math
import logging
logger = logging.getLogger(__name__)



def solutionExtractorFromForwardPath(variables):
    paths = variables["path"]
    depot_idx = len(paths[0])
    solution = []
    
    for i in range(len(paths)):
        route = []
        start = paths[i][-1]
        
        while start != depot_idx:
            route.append(start)
            start = paths[i][start-1]
        solution.append(route)

    return solution


experiments_setup = [
    {
        "name": "vrp-gecode-lns",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/vrp-gecode.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": solutionExtractorFromForwardPath
    }
]


def solve(instance, timeout, cache={}, random_seed=42):
    out_results = {}

    for experiment in experiments_setup:
        logger.info(f"Starting model {experiment['name']} with {experiment['solver']}")

        # Check if result is in cache
        if experiment["name"] in cache:
            logger.info(f"Cache hit")
            out_results[experiment["name"]] = cache[experiment["name"]]
            continue
        
        # Solve instance
        outcome, solutions, statistics = minizincSolve(
            model_path = experiment["model_path"],
            data_json = json.dumps(instance),
            solver = experiment["solver"],
            timeout_ms = timeout*1000,
            seed = random_seed
        )

        # Parse results
        if (outcome["mz_status"] is None) or (len(solutions) == 0):
            logger.warning(f"Instance crashed. Reason: {outcome['crash_reason']}")
            time = timeout
            optimality = False
            objective = None
            solution = None
            crash_reason = outcome["crash_reason"]
        else:
            time = timeout if outcome["mz_status"] in ["UNKNOWN", "SATISFIED"] else math.floor(outcome["time_ms"]/1000)
            optimality = outcome["mz_status"] == "OPTIMAL_SOLUTION"
            objective = solutions[-1]["variables"]["_objective"]
            solution = experiment["solution_extractor_fn"](solutions[-1]["variables"])
            crash_reason = outcome["crash_reason"]

        out_results[experiment["name"]] = {
            "time": time,
            "optimal": optimality,
            "obj": objective,
            "sol": solution,
            "_extras": {
                "statistics": statistics,
                "crash_reason": crash_reason,
                "time_to_last_solution": solutions[-1]["time_ms"]/1000
            }
        }

    return out_results