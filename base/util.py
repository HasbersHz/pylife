from __future__ import annotations

import io
import sys
from typing import TextIO

import abc
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


class BaseLifeErrors(object, metaclass=abc.ABCMeta):
    """To substitute your own routines, use the following class."""
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

    @staticmethod
    def set_error_handler(o: BaseLifeErrors):
        global errorhandler
        if not o:
            errorhandler = BaseLifeErrors()
        else:
            errorhandler = o


class LifeErrors(BaseLifeErrors):
    """For now error just uses stderr."""

    def fatal(self, s: str) -> None:
        print(s, file=sys.stderr)
        sys.exit(10)

    def warning(self, s: str) -> None:
        print(s, file=sys.stderr)

    def status(self, s: str) -> None:
        print(s, file=sys.stderr)

    def begin_progress(self, dlg_title: str) -> None:
        self.aborted: bool = False

    def abort_progress(self, frac_done: float, new_msg: str) -> bool:
        return False

    def end_progress(self) -> None:
        # do nothing
        pass

    def get_user_rules(self) -> str:
        return ""

    def get_rules_dir(self) -> str:
        return ""


errorhandler: BaseLifeErrors = LifeErrors()


def life_fatal(s: str) -> None:
    errorhandler.fatal(s)


def life_warning(s: str) -> None:
    errorhandler.warning(s)


def life_status(s: str) -> None:
    errorhandler.status(s)


def life_begin_progress(dlg_title: str) -> None:
    errorhandler.begin_progress(dlg_title)


def life_abort_progress(frac_done: float, new_msg: str) -> bool:
    errorhandler.aborted |= errorhandler.abort_progress(frac_done, new_msg)
    return errorhandler.aborted


def is_aborted() -> bool:
    return errorhandler.aborted


def life_end_progress() -> None:
    errorhandler.end_progress()


def life_get_user_rules() -> str:
    return errorhandler.get_user_rules()


def life_get_rules_dir() -> str:
    return errorhandler.get_rules_dir()


def get_debug_file_name() -> str:
    return "trace.txt"


def get_debug_file() -> TextIO:
    return open(get_debug_file_name(), "w+", encoding="utf-8")


perf_status_line: io.StringIO = io.StringIO("")  # Buffer for status updates.


class HPerf(object):
    """Performance data.  We keep running values here.  We can copy this
       to "mark" variables, and then report performance for deltas."""
    fast_node_inc: cint = cint(0)
    frames: float = 0.0
    nodes_calculated: float = 0.0
    half_nodes: float = 0.0
    depth_sum: float = 0.0
    time_stamp: float = 0.0
    gen_val: float = 0.0
    report_mask: cint = cint((1 << 16) - 1)  # node count between checks
    report_interval: float = 2.0  # time between update status bar

    def clear(self) -> None:
        self.fast_node_inc = cint(0)
        self.frames = 0.0
        self.nodes_calculated = 0.0
        self.half_nodes = 0.0
        self.depth_sum = 0.0
        self.time_stamp = get_time()
        self.gen_val = 0.0

    def report(self, mark: HPerf, verbose: cint) -> HPerf:
        """Return value in mark"""
        global perf_status_line

        ts = get_time()
        elapsed = ts - mark.time_stamp
        if not self.report_interval or elapsed < self.report_interval:
            return mark
        self.time_stamp = ts
        self.nodes_calculated += self.fast_node_inc.value
        self.fast_node_inc = cint(0)
        if verbose:
            node_count = self.nodes_calculated - mark.nodes_calculated
            half_frac = 0.0
            if node_count > 0:
                half_frac = (self.half_nodes - mark.half_nodes) / node_count
            elif not node_count:
                node_count = 1.0
            depth_delta = self.depth_sum - mark.depth_sum
            perf_status_line.write("RATE noderate {} depth {} half {}".format(node_count / elapsed,
                                                                              1 + depth_delta / node_count,
                                                                              half_frac))
            life_status(perf_status_line.readline())
        return self

    def report_step(self, mark: HPerf, rate_mark: HPerf, new_gen: float, verbose: cint) -> tuple[HPerf, HPerf]:
        """Return value in mark and in rate_mark"""
        global perf_status_line

        self.nodes_calculated += self.fast_node_inc.value
        self.fast_node_inc = cint(0)
        self.frames += 1.0
        self.time_stamp = get_time()
        elapsed = self.time_stamp - mark.time_stamp
        if not elapsed:
            elapsed = 1.0
        if not self.report_interval or elapsed < self.report_interval:
            return mark, rate_mark
        if verbose:
            inc = new_gen - mark.gen_val
            if not inc:
                inc = 1e30
            node_count = self.nodes_calculated - mark.nodes_calculated
            half_frac = 0.0
            if node_count > 0:
                half_frac = (self.half_nodes - mark.half_nodes) / node_count
            elif not node_count:
                node_count = 1.0
            depth_delta = self.depth_sum - mark.depth_sum
            gens_per_sec = inc / elapsed
            nodes_per_gen = node_count / inc
            fps = (self.frames - mark.frames) / elapsed
            perf_status_line.write("PERF gps {} nps {} fps {} depth {} half {} npg {} nodes {}"
                                   .format(gens_per_sec, node_count / elapsed, fps, 1 + depth_delta / node_count,
                                           half_frac, nodes_per_gen, node_count))
            life_status(perf_status_line.readline())
        self.gen_val = new_gen
        return self, self

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
