from __future__ import annotations
from . import constraints



class Variable(constraints.Constraint):
    def __init__(self, name: str, sort_: str):
        self.name = name
        self.sort = sort_
        self._comment = None

    def __str__(self):
        return f"{self.name}"

    def __hash__(self):
        return hash(self.name)
    
    def define(self):
        return f"(declare-const {self.name} {self.sort}) {f'; {self._comment}' if self._comment else ''}"

    def getVariables(self):
        return set([self])
    
    
class Integer(Variable):
    def __init__(self, name):
        super().__init__(name, "Int")