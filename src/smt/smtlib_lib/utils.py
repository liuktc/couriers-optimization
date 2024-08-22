from . import Constraint



class CommentLine(Constraint):
    def __init__(self, _comment):
        super().__init__("", [])
        self._comment = _comment

    def define(self):
        return f"; {self._comment}"

    def getVariables(self):
        return set()