import abc
from dataclasses import dataclass
from ctypes import c_int as cint
from time import monotonic as get_time


"""
def life_fatal(s: str) -> None:
def life_warning(s: str) -> None:
def life_status(s: str) -> None:
def life_begin_progress(dlg_title: str) -> None:
def life_abort_progress(frac_done: float, new_msg: str) -> bool:
def life_end_progress() -> None:
def life_get_user_rules() -> str:
def life_get_rules_dir() -> str:
def is_aborted() -> bool:
def get_debug_file() -> TextIO:

def second_count() -> float:
"""


class HLifeErrors(object, metaclass=abc.ABCMeta):
    """Sick of line ending woes.  This class takes care of this for us."""
    aborted: bool

    @abc.abstractmethod
    def fatal(self, s: str) -> None:
        return

    @abc.abstractmethod
    def warning(self, s: str) -> None:
        return

    @abc.abstractmethod
    def status(self, s: str) -> None:
        return

    @abc.abstractmethod
    def begin_progress(self, dlg_title: str) -> None:
        return

    @abc.abstractmethod
    def abort_progress(self, frac_done: float, new_msg: str) -> bool:
        return False

    @abc.abstractmethod
    def end_progress(self) -> None:
        return

    @abc.abstractmethod
    def get_user_rules(self) -> str:
        return ""

    @abc.abstractmethod
    def get_rules_dir(self) -> str:
        return ""

    def set_error_handler(self, obj) -> None:
        return


class HHPerf(object, metaclass=abc.ABCMeta):
    """Performance data.  We keep running values here.  We can copy this
       to "mark" variables, and then report performance for deltas."""
    fast_node_inc: cint = cint(0)
    frames: float = 0.0
    nodes_calculated: float = 0.0
    half_nodes: float = 0.0
    depth_sum: float = 0.0
    time_stamp: float = 0.0
    gen_val: float = 0.0
    report_mask: cint = cint(0)
    report_interval: float = 0.0

    def clear(self) -> None:
        self.fast_node_inc = cint(0)
        self.frames = 0.0
        self.nodes_calculated = 0.0
        self.half_nodes = 0.0
        self.depth_sum = 0.0
        self.time_stamp = get_time()
        self.gen_val = 0.0

    @abc.abstractmethod
    def report(self, mark, verbose: cint) -> None:
        return

    @abc.abstractmethod
    def report_step(self, mark, rate_mark, gen_val: float, verbose: cint) -> None:
        return

    def fast_inc(self, depth: cint, half: cint) -> cint:
        self.depth_sum += depth
        if half:
            self.half_nodes += 1
        self.fast_node_inc += 1
        return cint(not (self.fast_node_inc and self.report_mask))

    def get_report_interval(self) -> float:
        return self.report_interval

    def set_report_interval(self, v: float) -> None:
        self.report_interval = v
