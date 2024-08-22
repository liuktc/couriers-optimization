from __future__ import annotations
from . import Constraint



class SMTLIBModel:
    def __init__(self, logic: str="LIA", imports: list[str]=[]):
        self.logic = logic
        self.imports = imports
        self.variables = set()
        self.constraints = []

    def add(self, constraint: Constraint):
        self.variables = self.variables.union(constraint.getVariables())
        self.constraints.append(constraint)
        return constraint

    def __str__(self):
        return (
            f"(set-logic {self.logic})\n"
            "\n"
            "; --- Imports --- \n"
            f"{'\n'.join(self.imports)}"
            "\n"
            "; --- Variables ---\n"
            f"{'\n'.join([v.define() for v in self.variables])}\n"
            "\n"
            "; --- Constraints ---\n"
            f"{'\n'.join([c.define() for c in self.constraints])}\n"
            "\n"
            "(check-sat)\n"
            "(get-model)"
        )