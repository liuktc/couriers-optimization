from __future__ import annotations
from . import Constraint



class SMTLIBModel:
    def __init__(self, logic: str="LIA", imports: list[str]=[]):
        self._logic = logic
        self._imports = imports
        self._variables = set()
        self._constraints = []
        self.variables = {}


    def add(self, constraint: Constraint):
        self._variables = self._variables.union(constraint.getVariables())
        self._constraints.append(constraint)
        return constraint


    def compile(self):
        for v in self._variables: self.variables[v.name] = v

        return (
            f"(set-logic {self._logic})\n"
            "\n"
            "; --- Imports --- \n"
            f"{'\n'.join(self._imports)}"
            "\n"
            "; --- Variables ---\n"
            f"{'\n'.join([v.define() for v in self._variables])}\n"
            "\n"
            "; --- Constraints ---\n"
            f"{'\n'.join([c.define() for c in self._constraints])}\n"
            "\n"
        )
    

    def __str__(self):
        return self.compile()