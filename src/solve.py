from cp.solve import solve as cp_solve
from sat.solve import solve as sat_solve
from smt.solve import solve as smt_solve
from milp.solve import solve as milp_solve
import argparse
import os
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Instance solver")
    parser.add_argument("--output-path", type=str, default="./res")
    args = parser.parse_args()


    # Create output directories
    results_dir = args.output_path
    cp_dir = os.path.join(results_dir, "CP/")
    sat_dir = os.path.join(results_dir, "SAT/")
    smt_dir = os.path.join(results_dir, "SMT/")
    milp_dir = os.path.join(results_dir, "MILP/")

    for dir in [results_dir, cp_dir, sat_dir, smt_dir, milp_dir]:
        os.makedirs((dir), exist_ok=True)

    
    # Dump results
    output_hierarchy = [
        (cp_dir, cp_solve),
        (sat_dir, sat_solve),
        (smt_dir, smt_solve),
        (milp_dir, milp_solve)
    ]

    for out_dir, solve_fn in output_hierarchy:
        results = solve_fn()
        for i, instance_result in enumerate(results):
            with open(os.path.join(out_dir, f"{i+1}.json"), "w") as f:
                json.dump(instance_result, f, indent=3)


