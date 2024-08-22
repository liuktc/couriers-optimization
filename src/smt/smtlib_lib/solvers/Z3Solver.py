from . import Solver



class Z3Solver(Solver):
    def __init__(self, model, timeout, random_seed=42):
        super().__init__(model, ["z3", "-in", "smt.random_seed=42"], timeout)