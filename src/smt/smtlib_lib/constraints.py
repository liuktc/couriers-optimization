from __future__ import annotations



class Constraint:
    def __init__(self, operator: str, *vars: list[Constraint]):
        self.operator = operator
        self.vars = vars
        self._comment = None
        self._name = None

    def __str__(self):
        return f"({self.operator} {' '.join([str(v) for v in self.vars])})"
    
    def define(self):
        constr_str = str(self)
        if self._name is not None:
            constr_str = f"(! {constr_str} :named {self._name})"
        return f"(assert {constr_str}) {f'; {self._comment}' if self._comment else ''}"
    
    def comment(self, comment: str):
        self._comment = comment
        return self
    
    def named(self, name: str):
        self._name = name
        return self
    
    def getVariables(self):
        out = set()
        for v in self.vars:
            if isinstance(v, Constraint):
                out = out.union(v.getVariables())
        return out
    

    def __eq__(self, other: Constraint) -> Constraint:
        return Constraint("=", self, other)
    
    def __ne__(self, other: Constraint) -> Constraint:
        return Not(self == other)
    
    def __lt__(self, other: Constraint) -> Constraint:
        return Constraint("<", self, other)
    
    def __le__(self, other: Constraint) -> Constraint:
        return Constraint("<=", self, other)
    
    def __gt__(self, other: Constraint) -> Constraint:
        return Constraint(">", self, other)
    
    def __ge__(self, other: Constraint) -> Constraint:
        return Constraint(">=", self, other)
    
    def __neg__(self) -> Constraint:
        return Constraint("-", self)
    
    def __add__(self, other: Constraint) -> Constraint:
        return Constraint("+", self, other)
    
    def __radd__(self, other: Constraint) -> Constraint:
        return Constraint("+", other, self)
    
    def __sub__(self, other: Constraint) -> Constraint:
        return Constraint("-", self, other)

    def __rsub__(self, other: Constraint) -> Constraint:
        return Constraint("-", other, self)
     
    def __mul__(self, other: Constraint) -> Constraint:
        return Constraint("*", self, other)
    
    def __rmul__(self, other: Constraint) -> Constraint:
        return Constraint("*", other, self)
    
    def __floordiv__(self, other: Constraint) -> Constraint:
        return Constraint("div", self, other)
    
    def __rfloordiv__(self, other: Constraint) -> Constraint:
        return Constraint("div", other, self)
    
    def __mod__(self, other: Constraint) -> Constraint:
        return Constraint("mod", self, other)
    
    def __rmod__(self, other: Constraint) -> Constraint:
        return Constraint("mod", other, self)
    
    def __abs__(self) -> Constraint:
        return Constraint("abs", self)
    
    def __and__(self, other: Constraint) -> Constraint:
        return Constraint("and", self, other)

    def __or__(self, other: Constraint) -> Constraint:
        return Constraint("or", self, other)


def Not(var: Constraint):
    return Constraint("not", var)


def Implies(var1: Constraint, var2: Constraint):
    return Constraint("=>", var1, var2)


def Sum(vars: list[Constraint]):
    return Constraint("+", *vars)


def ITE(var1: Constraint, var2: Constraint, var3: Constraint):
    return Constraint("ite", var1, var2, var3)


def Distinct(vars: list[Constraint]):
    return Constraint("distinct", *vars)


def FnCall(fn_name, *vars: list[Constraint]):
    return Constraint(fn_name, *vars)
