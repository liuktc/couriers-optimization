import numpy as np
import itertools

#165
for n in range(13):
    l = np.arange(n)

    # Calculate all the permutations of the list
    all_permutations = list(itertools.permutations(l))
    p = np.array(all_permutations)

    print(n, np.sum(np.sum(p == l, axis=1) == n - 3))