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


def _preproCarryUpperBound(experiment, instance, random_seed):
    instance_path = os.path.join(pathlib.Path(__file__).parent.resolve(), ".instance.dzn")
    dzn_content = parseInstanceForMinizinc(instance)
    with open(instance_path, "w") as f:
        f.write(dzn_content)

    outcome, solutions, statistics = minizincSolve(
        model_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/utils/num_carry_upper.mzn"),
        data_path = instance_path,
        solver = "gecode",
        timeout_ms = 5000,
        seed = random_seed
    )

    if outcome["mz_status"] == "UNKNOWN":
        max_carry_per_courier = instance["n"]
    else:
        max_carry_per_courier = solutions[-1]["variables"]["obj"]

    return f"MAX_CARRY = {max_carry_per_courier};\n"


def _setLNSPercentage(percentage):
    def __set(*args, **kwargs):
        return f"LNS_PERC = {percentage};\n"
    return __set


experiments_setup = [
    {
        "name": "vrp-plain-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-plain.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": []
    },
    {
        "name": "vrp-luby-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-luby.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": []
    },
    {
        "name": "vrp-lns50-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(50) ]
    },
    {
        "name": "vrp-lns80-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(80) ]
    },
    {
        "name": "vrp-lns90-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(90) ]
    },
    {
        "name": "vrp-lns95-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95) ]
    },
    {
        "name": "vrp-lns97-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(97) ]
    },
    {
        "name": "vrp-lns99-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(99) ]
    },
    {
        "name": "vrp-lns95-symm_amount-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_amount.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95) ]
    },
        {
        "name": "vrp-lns95-symm_packs-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_packs.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95) ]
    },
    {
        "name": "vrp-lns95-symm_amount_strong-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_amount_strong.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95) ]
    },
    {
        "name": "vrp-lns95-symm_packs_strong-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_packs_strong.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95) ]
    },
    {
        "name": "vrp-lns95-symm_all-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_all.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95) ]
    },
    {
        "name": "vrp-lns95-triang-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-triang.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95), _preproCarryUpperBound ]
    },
    {
        "name": "vrp-lns95-triang-symm_amount-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-triang-symm_amount.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95), _preproCarryUpperBound ]
    },
    {
        "name": "vrp-lns95-triang-symm_packs-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-triang-symm_packs.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95), _preproCarryUpperBound ]
    },
    {
        "name": "vrp-lns95-triang-symm_all-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-triang-symm_all.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [ _setLNSPercentage(95), _preproCarryUpperBound ]
    },
    {
        "name": "vrp-plain-chuffed",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/chuffed/vrp-plain.mzn"),
        "solver": "chuffed",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": []
    },
    {
        "name": "vrp-luby-chuffed",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/chuffed/vrp-luby.mzn"),
        "solver": "chuffed",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": []
    },
    {
        "name": "vrp-plain-or_tools",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/or_tools/vrp-plain.mzn"),
        "solver": "com.google.ortools.sat",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": []
    },
    {
        "name": "vrp-luby-or_tools",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/or_tools/vrp-luby.mzn"),
        "solver": "com.google.ortools.sat",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": []
    },
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
        if len(experiment["preprocessing"]) > 0:
            for prepro_fn in experiment["preprocessing"]:
                dzn_content += prepro_fn(experiment, instance, random_seed)
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