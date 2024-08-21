# from model_arrays import SMT_array
from model_plain import SMT_plain
# from model_penalty import SMT_penalty
from model_twosolver import SMT_twosolver

import logging
logger = logging.getLogger(__name__)

experiments = [
    {
        "name": "plain",
        "model": SMT_plain,
        "symmetry_breaking": False,
        "implied_constraints": False
    },
    {
        "name": "twosolver",
        "model": SMT_twosolver,
        "symmetry_breaking": False,
        "implied_constraints": False
    },
    {
        "name": "twosolver_implied",
        "model": SMT_twosolver,
        "symmetry_breaking": False,
        "implied_constraints": True
    }
]

def solve(instance, timeout, cache={}, **kwargs):
    results = {}
    
    for experiment in experiments[0:1]:
        logger.info(f"Starting model {experiment['name']}")
        name, model, symmetry_breaking, implied_constraints = experiment["name"], experiment["model"], experiment["symmetry_breaking"], experiment["implied_constraints"]

        # Check if result is in cache
        if name in cache:
            logger.info(f"Cache hit")
            results[name] = cache[name]
            continue
        
        results[name] = model(instance["m"],
                              instance["n"],
                              instance["l"],
                              instance["s"],
                              instance["D"],
                              timeout=timeout,
                              implied_constraints=implied_constraints,
                              symmetry_breaking=symmetry_breaking,
                              **kwargs)
        
    return results
import re

def __cleanLine(line):
    return re.sub(r" +", " ", line.strip())

def parseInstanceFile(path):
    with open(path, "r") as f:
        num_couriers = int(__cleanLine(f.readline()))
        num_packages = int(__cleanLine(f.readline()))
        capacities = [int(l) for l in __cleanLine(f.readline()).split(" ")]
        sizes = [int(s) for s in __cleanLine(f.readline()).split(" ")]
        distances = []

        for _ in range(num_packages+1):
            distances.append( [int(d) for d in __cleanLine(f.readline()).split(" ")] )

    return {
        "m": num_couriers,
        "n": num_packages,
        "l": capacities,
        "s": sizes,
        "D": distances
    }
    
if __name__ == "__main__":
    import os
    
    instances = [ (i+1, parseInstanceFile(os.path.join("../instances", f))) for i, f in enumerate(sorted(os.listdir("../instances"))) ]
    
    instance_number = 3
    
    for instance_number, instance in instances[instance_number-1:instance_number]:
        print(instance)
        print(solve(instance, timeout=30))
    