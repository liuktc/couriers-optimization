from . import Solver



class OpenSMTSolver(Solver):
    def __init__(self, model, timeout, random_seed=42):
        super().__init__(model, [
            "opensmt",
            f"-r {random_seed}"
        ], timeout)