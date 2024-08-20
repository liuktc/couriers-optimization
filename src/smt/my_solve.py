from model_arrays import SMT_array
from model_plain import SMT_plain
from model_penalty import SMT_penalty

models = {
    "plain": SMT_plain,
    "penalty": SMT_penalty
}

def solve(instance, timeout, **kwargs):
    results = {}
    
    for model_name, model in models.items():
        results[model_name] = model(instance["m"], instance["n"], instance["l"], instance["s"], instance["D"], timeout=timeout,**kwargs)
        
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
    
    for instance_number, instance in instances[6:7]:
        print(instance)
        print(solve(instance, timeout=30))
    