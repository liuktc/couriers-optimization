import subprocess
from .. import SMTLIBModel, Constraint, smtlibModelParser, smtlibUnsatCoreParser
import threading
import time



class _SolverThread(threading.Thread):
    def __init__(self, model: SMTLIBModel, cmd: list[str], timeout: int):
        super().__init__()
        self.timeout = timeout
        self.model = model
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.terminate_event = threading.Event()


    def run(self):
        self.terminate_event.wait(self.timeout)
        self.proc.kill()


    def compile(self):
        self.proc.stdin.write(str(self.model))
        self.proc.stdin.flush()


    def checkSat(self):
        self.proc.stdin.write("(check-sat)\n")
        self.proc.stdin.flush()
        status = ";"
        while status[0] == ";": # OpenSMT prints some comments
            status = self.proc.stdout.readline().strip()
        return status
    

    def getModel(self):
        self.proc.stdin.write("(get-model)\n")
        self.proc.stdin.flush()
        opened_brackets, closed_brackets = 0, 0 # Check end of stdout by counting brackets
        model = ""
        while True:
            buff = self.proc.stdout.readline().strip()
            model += buff + "\n"
            opened_brackets += buff.count("(")
            closed_brackets += buff.count(")")
            if opened_brackets == closed_brackets: break
        return smtlibModelParser(model)

    def getUnsatCore(self):
        self.proc.stdin.write("(get-unsat-core)\n")
        self.proc.stdin.flush()

        opened_brackets, closed_brackets = 0, 0 # Check end of stdout by counting brackets
        core = ""
        while True:
            buff = self.proc.stdout.readline().strip()
            core += buff + "\n"
            opened_brackets += buff.count("(")
            closed_brackets += buff.count(")")
            if opened_brackets == closed_brackets: break
        return smtlibUnsatCoreParser(core)


    def push(self, n: int):
        self.proc.stdin.write(f"(push {n})\n")
        self.proc.stdin.flush()


    def pop(self, n: int):
        self.proc.stdin.write(f"(pop {n})\n")
        self.proc.stdin.flush()


    def addConstraint(self, constraint: Constraint):
        self.proc.stdin.write(f"{constraint.define()}\n")
        self.proc.stdin.flush()


    def terminate(self):
        self.proc.kill()
        self.terminate_event.set()



class Solver:
    def __init__(self, model: SMTLIBModel, cmd: list[str]=[], timeout: int=300):
        self._thread = _SolverThread(model, cmd, timeout)
        self._thread.start()

    def compile(self):
        return self._thread.compile()

    def checkSat(self):
        return self._thread.checkSat()

    def getModel(self):
        return self._thread.getModel()
    
    def getUnsatCore(self):
        return self._thread.getUnsatCore()

    def push(self, n: int=1):
        return self._thread.push(n)

    def pop(self, n: int=1):
        return self._thread.pop(n)

    def addConstraint(self, constraint: Constraint):
        return self._thread.addConstraint(constraint)

    def terminate(self):
        self._thread.terminate()
