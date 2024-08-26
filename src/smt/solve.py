from .model_plain import SMT_plain
from .model_twosolver import SMT_twosolver 
from .model_local_search import SMT_local_search
from .model_plain_mtz import SMT_plain_mtz

import logging
logger = logging.getLogger(__name__)

experiments = [
    {
        "name": "plain",
        "model": SMT_plain,
        "symmetry_breaking": False,
        "implied_constraints": False,
        "instance_limit": 11,
    },
    {
        "name": "plain_symm",
        "model": SMT_plain,
        "symmetry_breaking": True,
        "implied_constraints": False,
        "instance_limit": 11,
    },
    {
        "name": "plain_impl",
        "model": SMT_plain,
        "symmetry_breaking": False,
        "implied_constraints": True,
        "instance_limit": 11,
    },
    {
        "name": "twosolver",
        "model": SMT_twosolver,
        "symmetry_breaking": False,
        "implied_constraints": False,
        "instance_limit": 22,
    },
    {
        "name": "twosolver_symm",
        "model": SMT_twosolver,
        "symmetry_breaking": True,
        "implied_constraints": False,
        "instance_limit": 22,
    },
    {
        "name": "twosolver_impl",
        "model": SMT_twosolver,
        "symmetry_breaking": False,
        "implied_constraints": True,
        "instance_limit": 22,
    },
    {
        "name": "local_search",
        "model": SMT_local_search,
        "symmetry_breaking": False,
        "implied_constraints": False,
        "instance_limit": 22,
    }
]


def solve(instance, timeout, cache={}, instance_number=0, **kwargs):
    results = {}
    
    for experiment in experiments:
        logger.info(f"Starting model {experiment['name']}")
        name, model, symmetry_breaking, implied_constraints = experiment["name"], experiment["model"], experiment["symmetry_breaking"], experiment["implied_constraints"]

        # Check if result is in cache
        if name in cache:
            logger.info(f"Cache hit")
            results[name] = cache[name]
            continue
        
        if instance_number >= experiment["instance_limit"]:
            logger.info(f"Model {name} skip instance {instance_number}")
            results[name] =  {
                "time": timeout,
                "optimal": False,
                "obj": None,
                "sol": None
            }
        
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