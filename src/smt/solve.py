from model import SMT
from model_arrays import SMT_array
from model_new import SMT_new

def solve(instance, timeout, **kwargs):
    res_dict = SMT_new(instance["m"], instance["n"], instance["l"], instance["s"], instance["D"], timeout=timeout,**kwargs)
    # return SMT(instance["m"], instance["n"], instance["l"], instance["s"], instance["D"], timeout=timeout,**kwargs)
    # return SMT_array(instance["m"], instance["n"], instance["l"], instance["s"], instance["D"], timeout=timeout,**kwargs)
    return {
        "smt_first": res_dict,
    }