from . import Solver



def restart2index(restart_str):
    if restart_str == "geometric": return 0
    if restart_str == "inner-outer-geometric": return 1
    if restart_str == "luby": return 2
    if restart_str == "fixed": return 3
    if restart_str == "arithmetic": return 4


class Z3Solver(Solver):
    def __init__(self, model, timeout, restart="inner-outer-geometric", random_seed=42):
        super().__init__(model, ["z3", "-in", "unsat_core=true", f"smt.restart_strategy={restart2index(restart)}", f"smt.random_seed={random_seed}"], timeout)