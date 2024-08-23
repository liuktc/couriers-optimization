""" from .model_plain import SMT_plain
from .model_penalty import SMT_penalty
from .model_twosolver import SMT_twosolver  """
from .model_local_search import SMT_local_search


import logging
logger = logging.getLogger(__name__)

""" experiments = [
    {
        "name": "plain",
        "model": SMT_plain,
        "symmetry_breaking": False,
        "implied_constraints": False
    },
    {
        "name": "penalty",
        "model": SMT_penalty,
        "symmetry_breaking": False,
        "implied_constraints": False
    },
    {
        "name": "plain_symm",
        "model": SMT_plain,
        "symmetry_breaking": True,
        "implied_constraints": False
    },
    {
        "name": "twosolver",
        "model": SMT_twosolver,
        "symmetry_breaking": False,
        "implied_constraints": False
    },
    {
        "name": "twosolver_symm",
        "model": SMT_twosolver,
        "symmetry_breaking": True,
        "implied_constraints": False
    }
] """

experiments = [
    {
        "name": "local_search",
        "model": SMT_local_search,
        "symmetry_breaking": False,
        "implied_constraints": False
    }
]

def solve(instance, timeout, cache={}, **kwargs):
    results = {}
    
    for experiment in experiments:
        logger.info(f"Starting model {experiment['name']}")
        name, model, symmetry_breaking, implied_constraints = experiment["name"], experiment["model"], experiment["symmetry_breaking"], experiment["implied_constraints"]

        # Redo experiment 11
        """ if instance["m"] == 20 and instance["n"] == 143 and instance["l"][0] == 200:
            results[name] = model(instance["m"],
                              instance["n"],
                              instance["l"],
                              instance["s"],
                              instance["D"],
                              timeout=timeout,
                              implied_constraints=implied_constraints,
                              symmetry_breaking=symmetry_breaking,
                              **kwargs)
        else:
            if name in cache:
                logger.info(f"Cache hit")
                results[name] = cache[name]
                continue
            else:
                results[name] = {
                        "time": timeout,
                        "optimal": False,
                        "obj": None,
                        "sol": None
                    }
        continue """
        # Check if result is in cache
        """ if name in cache:
            logger.info(f"Cache hit")
            results[name] = cache[name]
            continue """
        
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