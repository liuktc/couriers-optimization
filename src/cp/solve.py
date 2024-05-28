from minizinc import Instance, Model, Solver
from minizinc.result import Status
import pathlib
import os
from datetime import timedelta
import math
import logging
logger = logging.getLogger(__name__)


experiments_setup = [
    {
        "name": "milp_like",
        "model": Model( os.path.join(pathlib.Path(__file__).parent.resolve(), "./milp_like.mzn") ),
        "solvers": [
            "gecode", 
            "chuffed"
        ]
    },
    {
        "name": "n_n_matrix",
        "model": Model( os.path.join(pathlib.Path(__file__).parent.resolve(), "./n_n_matrix.mzn") ),
        "solvers": [
            "gecode", 
            "chuffed"
        ]
    },
    {
        "name": "n_n_matrix_symm",
        "model": Model( os.path.join(pathlib.Path(__file__).parent.resolve(), "./n_n_matrix_symm.mzn") ),
        "solvers": [
            "gecode", 
            "chuffed"
        ]
    }
]


def solve(instance, timeout, cache={}, random_seed=42):
    out_results = {}

    for experiment in experiments_setup:
        logger.info(f"Starting model {experiment['name']}")
        model = experiment["model"]

        for solver_name in experiment["solvers"]:
            logger.info(f"Solving with {solver_name}")
            result_key = f"{experiment['name']}-{solver_name}"

            # Check if result is in cache
            if result_key in cache:
                logger.info(f"Cache hit")
                out_results[result_key] = cache[result_key]
                continue

            solver = Solver.lookup(solver_name)
            instance_data = Instance(solver, model)

            # Set input data
            for key, value in instance.items():
                instance_data[key] = value

            try:
                result = instance_data.solve(
                    timeout = timedelta(seconds=timeout),
                    random_seed = random_seed
                )
            except Exception as e:
                logger.error(e)
                time = timeout
                optimal = False
                objective_value = None
                sol = None
                minizinc_statistics_str = None
                out_of_memory = (str(e) == "out of memory" or "std::bad_alloc" in str(e))
                has_crashed = True
            else:
                if ((result.status == Status.UNKNOWN) or 
                    (result.status == Status.SATISFIED) or 
                    ("solveTime" not in result.statistics)
                ): 
                    time = timeout
                else:
                    time = math.floor(result.statistics["solveTime"].total_seconds())
                optimal = (result.status == Status.OPTIMAL_SOLUTION)
                if result.solution is None:
                    objective_value = None
                    sol = None
                else:
                    objective_value = result["objective"]
                    sol = [[x for x in sol if x != 0] for sol in result["T"]]
                minizinc_statistics_str = str(result.statistics)
                out_of_memory = False
                has_crashed = False

            out_results[result_key] = {
                "time": time,
                "optimal": optimal,
                "obj": objective_value,
                "sol": sol,
                "_extras": {
                    "minizinc_statistics": minizinc_statistics_str,
                    "out_of_memory": out_of_memory,
                    "has_crashed": has_crashed
                }
            }

    return out_results