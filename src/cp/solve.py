from minizinc import Instance, Model, Solver
from minizinc.result import Status
import pathlib
import os
from datetime import timedelta


def solve(instance, timeout, random_seed=42):
    to_try_models = [
        Model( os.path.join(pathlib.Path(__file__).parent.resolve(), "./milp_like.mzn") )
    ]
    to_try_solvers = [
        Solver.lookup("gecode"),
        Solver.lookup("chuffed")
    ]
    out_results = []

    for model in to_try_models:
        for solver in to_try_solvers:
            instance_data = Instance(solver, model)

            for key, value in instance.items():
                instance_data[key] = value

            try:
                result = instance_data.solve(
                    timeout = timedelta(seconds=timeout),
                    random_seed = random_seed
                )
            except:
                time = timeout
                optimal = False
                objective_value = None
                sol = None
            else:
                time = round(result.statistics["solveTime"].total_seconds()) if ("solveTime" in result.statistics) else timeout
                optimal = result.status == Status.OPTIMAL_SOLUTION
                if result.solution is None:
                    objective_value = None
                    sol = None
                else:
                    objective_value = result["objective"]
                    sol = [[x for x in sol if x != 0] for sol in result["T"]]

            out_results.append({
                "milp_like_gecode": {
                    "time": time,
                    "optimal": optimal,
                    "obj": objective_value,
                    "sol": sol
                }
            })

    return out_results