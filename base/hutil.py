from dataclasses import dataclass
from typing import TextIO

from ctypes import c_int as cint


def life_fatal(s: str) -> None:
    return
def life_warning(s: str) -> None:
    return
def life_status(s: str) -> None:
    return
def life_begin_progress(dlg_title: str) -> None:
    return
def life_abort_progress(frac_done: float, new_msg: str) -> bool:
    return False
def life_get_user_rules() -> str:
    return ""
def life_get_rules_dir() -> str:
    return ""
def is_aborted() -> bool:
    return False
def get_debug_file() -> TextIO:
    return TextIO()


class LifeErrors:
    """Sick of line ending woes.  This class takes care of this for us."""
    aborted: bool

    def fatal(self, s: str) -> None:
        return

    def warning(self, s: str) -> None:
        return

    def status(self, s: str) -> None:
        return

    def begin_progress(self, dlgtitle: str) -> None:
        return

    def abort_progress(self, frac_done: float, new_msg: str) -> bool:
        return False

    def end_progress(self) -> None:
        return

    def get_user_rules(self) -> str:
        return ""

    def get_rules_dir(self) -> str:
        return ""

    def set_error_handler(self, obj) -> None:
        return


def second_count() -> float:
    return 0.0


@dataclass
class HPerf:
    """Performance data.  We keep running values here.  We can copy this
       to "mark" variables, and then report performance for deltas."""
    fast_node_inc: cint
    frames: float
    nodes_calculated: float
    half_nodes: float
    depth_sum: float
    time_stamp: float
    gen_val: float
    report_mask: cint
    report_interval: float

    def clear(self) -> None:
        self.fast_node_inc = cint(0)
        self.frames = 0.0
        self.nodes_calculated = 0.0
        self.half_nodes = 0.0
        self.depth_sum = 0.0
        self.time_stamp = second_count()
        self.gen_val = 0.0

    def report(self, mark, verbose: cint) -> None:
        return

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
