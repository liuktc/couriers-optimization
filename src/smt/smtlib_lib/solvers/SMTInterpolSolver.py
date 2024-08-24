from . import Solver



class SMTInterpolSolver(Solver):
    def __init__(self, model, timeout, random_seed=42):
        super().__init__(model, [
            "java", "-jar", "/usr/local/share/smtinterpol.jar",
            "-q",
            "-no-success",
            "-r", f"{random_seed}"
        ], timeout)