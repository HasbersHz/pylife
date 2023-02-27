import ctypes
import itertools as it
import numpy as np
from string import ascii_letters, digits

_all_letters = list(ascii_letters + digits) + ['_', '']

del ascii_letters, digits


def find_func(dll: ctypes.CDLL = None) -> np.ndarray:
    def suma(s):
        return

    if dll is None:
        return np.array([])
    fined = np.array(0, dtype=str)
    for i in map(lambda x: ''.join(x), it.product(*([_all_letters] * 20))):
        try:
            dll.__getattr__()
    return fined


print(find_func(1))
