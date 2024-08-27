from . import Solver



class CVC5Solver(Solver):
    def __init__(self, model, timeout, random_seed=42):
        super().__init__(model, [
            "cvc5",
            "--incremental",
            "--produce-models",
            f"--random-seed={random_seed}"
        ], timeout)