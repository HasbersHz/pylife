import abc
from ctypes import c_int as cint
from lifepoll import LifePoll

# this must not be increased beyond 32767, because we use a bigint
# multiply that only supports multiplicands up to that size.
MAX_FRAME_COUNT = cint(32000)


class HTimeLine(object, metaclass=abc.ABCMeta):
    """Timeline support is pretty generic."""
    recording, frame_count, base, expo, save_timeline = (cint(),) * 5
    start, inc, next_, end = (int(),) * 4

    def __init__(self):
        recording, frame_count, save_timeline = cint(0), cint(0), cint(1)
        start, inc, next_, end = 0, 0, 0, 0

    @abc.abstractmethod
    def frames(self) -> list[None]:
        pass


class HLifeAlgo:
    __poller = LifePoll()
    __verbose = cint()
    __maxCellStates = cint()  # keep up to date; set_cell depends on it
    __generation = int()
    __increment = int()
