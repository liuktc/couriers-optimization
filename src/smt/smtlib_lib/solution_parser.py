import re

def smtlibModelParser(solution: str):
    pattern = re.compile(r"\s*\(\s*define-fun\s+(?P<name>.*?)\s+\(\)\s+(?P<sort>.*?)\s+(?P<value>.*?)\)")
    pos = 0
    out = {}

    while (match := pattern.search(solution, pos)) is not None:
        pos = match.end()
        casting = str
        if match.group("sort") == "Int": casting = int
        out[match.group("name")] = casting(match.group("value"))

    return out


def smtlibUnsatCoreParser(unsat: str):
    unsat = unsat.strip()[1:-1]
    return unsat.split(" ")
