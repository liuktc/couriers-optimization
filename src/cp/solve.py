from .minizinc_utils import minizincSolve, parseInstanceForMinizinc
import pathlib
import os
import math
import time
import logging
logger = logging.getLogger(__name__)



def _solutionExtractorFromForwardPath(variables):
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
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": None
    },
    {
        "name": "vrp-gecode-lns-symm_weak",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/vrp-gecode-symm_weak.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": None
    },
    {
        "name": "vrp-gecode-lns-symm_strong",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/vrp-gecode-symm_strong.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": None
    },
    {
        "name": "vrp-chuffed",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/vrp-chuffed.mzn"),
        "solver": "chuffed",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": None
    },
    {
        "name": "vrp-chuffed-lns-symm_weak",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/vrp-chuffed-symm_weak.mzn"),
        "solver": "chuffed",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": None
    },
    {
        "name": "vrp-chuffed-lns-symm_strong",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/vrp-chuffed-symm_strong.mzn"),
        "solver": "chuffed",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": None
    },
    {
        "name": "vrp-gecode-lns2",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/vrp-gecode2.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": None
    },
    {
        "name": "vrp-gecode-lns-symm_weak2",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/vrp-gecode-symm_weak2.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": None
    }
]


def solve(instance, timeout, cache={}, random_seed=42):
    instance_path = os.path.join(pathlib.Path(__file__).parent.resolve(), ".instance.dzn")
    out_results = {}

    for experiment in experiments_setup:
        logger.info(f"Starting model {experiment['name']} with {experiment['solver']}")

        # Check if result is in cache
        if experiment["name"] in cache:
            logger.info(f"Cache hit")
            out_results[experiment["name"]] = cache[experiment["name"]]
            continue

        dzn_content = parseInstanceForMinizinc(instance)
        start_time = time.time()

        # Create instance input file
        if experiment["preprocessing"] is not None:
            dzn_content += experiment["preprocessing"](experiment, instance, random_seed)
        with open(instance_path, "w") as f:
            f.write(dzn_content)
        preprocess_time = time.time() - start_time
        
        # Solve instance
        outcome, solutions, statistics = minizincSolve(
            model_path = experiment["model_path"],
            data_path = instance_path,
            solver = experiment["solver"],
            timeout_ms = math.floor(timeout - preprocess_time)*1000,
            seed = random_seed
        )
        solve_time = time.time() - start_time

        if (outcome["mz_status"] is None) and (len(solutions) > 0):
            # Solver crashed before finishing but there are intermediate solutions.
            # Consider as if it timed out.
            outcome["mz_status"] = "UNKNOWN"

        # Parse results
        if (outcome["mz_status"] is None) or (len(solutions) == 0):
            if outcome['crash_reason'] is not None:
                logger.warning(f"Instance crashed. Reason: {outcome['crash_reason']}")
            overall_time = timeout
            optimality = False
            objective = None
            solution = None
            crash_reason = outcome["crash_reason"]
        else:
            overall_time = timeout if outcome["mz_status"] in ["UNKNOWN", "SATISFIED"] else math.floor(solve_time)
            optimality = outcome["mz_status"] == "OPTIMAL_SOLUTION"
            objective = solutions[-1]["variables"]["obj"]
            solution = experiment["solution_extractor_fn"](solutions[-1]["variables"])
            crash_reason = outcome["crash_reason"]

        out_results[experiment["name"]] = {
            "time": overall_time,
            "optimal": optimality,
            "obj": objective,
            "sol": solution,
            "_extras": {
                "statistics": statistics,
                "crash_reason": crash_reason,
                "time_to_last_solution": None if len(solutions) == 0 else (preprocess_time + solutions[-1]["time_ms"]/1000)
            }
        }
        os.remove(instance_path)

    return out_results