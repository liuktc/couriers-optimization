from subprocess import Popen, PIPE
import os
import json
import logging
logger = logging.getLogger(__name__)



def formatCommand(model_path, data_json, solver, timeout_ms, seed):
    return [
        "minizinc",
        "--json-stream",
        "--output-mode", "json",
        "--all",
        "--statistics",
        "--solver", f"{solver}",
        "--time-limit", f"{timeout_ms}",
        "--random-seed", f"{seed}",
        "--output-time",
        "--output-objective",
        "--model", f"{os.path.abspath(model_path)}",
        "--cmdline-json-data", f"{data_json}"
    ]


def minizincSolve(model_path: str, data_json: str, solver: str, timeout_ms: int, seed: int):
    """
        Calls MiniZinc on a model and returns solving statistics and all solutions.
    """
    solutions = []
    outcome = {
        "mz_status": None,
        "time_ms": None,
        "crash_reason": None
    }
    statistics = {
        "compiler": None,
        "solver": None,
        "solution": None
    }
    minizinc_cmd = formatCommand(model_path, data_json, solver, timeout_ms, seed)

    with Popen(minizinc_cmd, stdout=PIPE, stderr=PIPE) as pipe:
        while True:
            out_stream = pipe.stdout.readline().decode("utf-8")
            if len(out_stream) <= 0: break
            data = json.loads(out_stream)

            if data["type"] == "statistics":
                # MiniZinc outputs 3 statistics at different times.
                if statistics["compiler"] is None: 
                    statistics["compiler"] = data["statistics"]
                elif statistics["solver"] is None: 
                    statistics["solver"] = data["statistics"]
                elif statistics["solution"] is None: 
                    statistics["solution"] = data["statistics"]
                else: 
                    logger.warning("Unexpected statistics from MiniZinc")
            elif data["type"] == "solution":
                # Each intermediate solution is stored
                sol = {
                    "variables": data["output"]["json"],
                    "time_ms": data["time"]
                }
                solutions.append(sol)
            elif data["type"] == "status":
                outcome["mz_status"] = data["status"]
                outcome["time_ms"] = data["time"]

        pipe.wait()
        if pipe.returncode == [-6, -11]:
            outcome["crash_reason"] = "out-of-memory"
        elif pipe.returncode != 0:
            outcome["crash_reason"] = "yes"

    return outcome, solutions, statistics
