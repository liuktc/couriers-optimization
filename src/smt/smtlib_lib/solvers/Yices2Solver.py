from . import Solver



class Yices2Solver(Solver):
    def __init__(self, model, timeout, random_seed=42):
        super().__init__(model, [
            "yices-smt2",
            "--smt2-model-format",
            "--incremental",
        ], timeout)