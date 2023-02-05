import numpy as np
from numba import njit, cuda


@njit
def clear_edges(array, how=False):
    la = len(array[0])
    lb = len(array)
    if how:
        array[0, :] = np.ones(la)
        array[-1, :] = np.ones(la)
        array[:, 0] = np.ones(lb)
        array[:, -1] = np.ones(lb)
    else:
        array[0, :] = np.zeros(la)
        array[-1, :] = np.zeros(la)
        array[:, 0] = np.zeros(lb)
        array[:, -1] = np.zeros(lb)
    return array


@njit  # cuda.jit('void(int64[:, :], int64[:], int64[:], int64)')
def cells_update(prev: np.ndarray, res: tuple, rules: tuple, order: int) -> np.ndarray:
    nex = prev.copy()
    for i in np.arange(1, res[0] - 1):
        for j in np.arange(1, res[1] - 1):
            match prev[i, j]:
                case 1:
                    summa = np.sum(prev[i - order:i + order + 1, j - order:j + order + 1]) - 1
                    if summa not in rules[1]:
                        nex[i, j] = 0
                case 0:
                    summa = np.sum(prev[i - order:i + order + 1, j - order:j + order + 1])
                    if summa in rules[0]:
                        nex[i, j] = 1
    return nex
