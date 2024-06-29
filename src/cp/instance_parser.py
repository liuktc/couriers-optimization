def parseForMinizinc(instance):
    out = ""
    out += f"m = {instance['m']};\n"
    out += f"n = {instance['n']};\n"
    out += f"l = [ {','.join([str(x) for x in instance['l']])} ];\n"
    out += f"s = [ {','.join([str(x) for x in instance['s']])} ];\n"
    out += "D = ["
    for d in instance["D"]:
        out += f"| {','.join([str(x) for x in d])} "
    out += "|];\n"
    
    return out