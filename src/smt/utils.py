from z3 import *

def maximum(a):
    m = a[0]
    for v in a[1:]:
        m = If(v > m, v, m)
    return m

def precedes(a1, a2):
    if not a1:
        return True
    if not a2:
        return False
    return Or(a1[0] < a2[0], And(a1[0] == a2[0], precedes(a1[1:], a2[1:])))

def millisecs_left(t, timeout):
    return int((timeout - t) * 1000)    

def Min(lst):
    # Start with the first element as the minimum.
    min_value = lst[0]
    
    # Iterate through the list, updating min_value with the smallest element found.
    for elem in lst[1:]:
        min_value = If(elem < min_value, elem, min_value)
    
    return min_value

def get_element_at_index(arr, idx):
    # Start with the first element as the default
    selected = arr[0]
    
    # Iterate through the list, select the element where the index matches
    for i in range(1, len(arr)):
        selected = If(idx == i, arr[i], selected)
    
    return selected

# -----------------------------------------------------------------------------%
# Constrains the elements of 'path' to define a subcircuit where 'x[i] = j'
# means that 'j' is the successor of 'i' and 'x[i] = i' means that 'i'
# is not in the circuit.
# assignments[i] = j means that packet 'i' is assigned to courier 'j'.
# -----------------------------------------------------------------------------%
def subcircuit(x, tag):
    S = range(len(x))  # index_set(x)
    l = min(S)
    u = max(S)
    n = len(S)

    # Variables
    # order = IntVector(f'order_{tag}', n)
    order = Array(f"order_{tag}", IntSort(), IntSort())
    ins = [Bool(f'ins_{i}_{tag}') for i in S]
    for i in S:
        ins[i] = (x[i] != i + 1)

    firstin = Int(f'firstin_{tag}')
    lastin = Int(f'lastin_{tag}')
    empty = Bool(f'empty_{tag}')

    constraints = []

    # Constraints for order and firstin
    constraints.append(Distinct(x))
    constraints.append(Distinct(order))
    constraints.append(firstin == Min([If(ins[i], i, u+1) for i in S]))
    constraints.append(empty == (firstin > u))

    # If the subcircuit is empty, then each node points at itself.
    for i in S:
        constraints.append(Implies(empty, Not(ins[i])))

    # If the subcircuit is non-empty, then order numbers the subcircuit.
    non_empty_conditions = []

    # The firstin node is numbered 1.
    # non_empty_conditions.append(get_element_at_index(order, firstin) == 1)
    non_empty_conditions.append(Select(order, firstin) == 1)

    # The lastin node is greater than firstin.
    non_empty_conditions.append(lastin > firstin)

    # The lastin node points at firstin.
    non_empty_conditions.append(get_element_at_index(x, lastin) == firstin + 1)

    # And both are in
    non_empty_conditions.append(get_element_at_index(ins, lastin))
    non_empty_conditions.append(get_element_at_index(ins, firstin))

    # The successor of each node except where it is firstin is
    # numbered one more than the predecessor.
    #non_empty_conditions.append(And([Implies(And(ins[i], x[i] - 1 != firstin), 
    #                                         get_element_at_index(order, x[i] - 1) == get_element_at_index(order, i) + 1)
    #                                 for i in S]))

    non_empty_conditions.append(And([Implies(And(ins[i], x[i] - 1 != firstin),
                                             Select(order, x[i] - 1) == Select(order, i) + 1)
                                     for i in S]))

    # Each node that is not in is numbered after the lastin node.
    # non_empty_conditions.append(And([Or(ins[i], get_element_at_index(order, lastin) < get_element_at_index(order, i))
    #                                  for i in S]))

    non_empty_conditions.append(And([Or(ins[i], Select(order, lastin) < Select(order, i))
                                      for i in S]))

    constraints.append(Implies(Not(empty), And(non_empty_conditions)))

    return constraints
