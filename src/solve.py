from cp.solve import solve as cp_solve
from sat.solve import solve as sat_solve
from smt.solve import solve as smt_solve
from milp.solve import solve as milp_solve
from input_parser import parseInstanceFile
import argparse
import os
import json
import logging
logger = logging.getLogger(__name__)


def __loadCache(results_file_path):
    if not os.path.isfile(results_file_path): return {}

    with open(results_file_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Instance solver")
    parser.add_argument("--instances-path", type=str, default="./instances")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    parser.add_argument("--output-path", type=str, default="./res")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--overwrite-old", action="store_true", help="If set, old results with the same name will be run again")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARN)

    instances = [ parseInstanceFile(os.path.join(args.instances_path, f)) for f in sorted(os.listdir(args.instances_path)) ]


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
        logger.info(f"Starting processing for {out_dir}")

        for i, instance in enumerate(instances):
            # Init cache
            if args.overwrite_old:
                cached_results = {}
            else:
                cached_results = __loadCache(os.path.join(out_dir, f"{i+1}.json"))

            # Solving instance
            logger.info(f"Starting instance {i+1}")
            instance_results = solve_fn(
                instance = instance,
                timeout = args.timeout,
                cache = cached_results
            ) 

            for key in cached_results:
                if key not in instance_results:
                    instance_results[key] = cached_results[key]

            # Saving instance results
            results_file_path = os.path.join(out_dir, f"{i+1}.json")
            with open(results_file_path, "w") as f:
                logger.info(f"Saving results in {results_file_path}")
                json.dump(instance_results, f, indent=3)


