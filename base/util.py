from sys import stderr, exit as s_exit
from typing import TextIO

from hutil import *


class BaseLifeErrors(HLifeErrors):
    """For now error just uses stderr."""
    def fatal(self, s: str) -> None:
        print(s, file=stderr)
        s_exit(10)

    def warning(self, s: str) -> None:
        print(s, file=stderr)

    def status(self, s: str) -> None:
        print(s, file=stderr)

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


errorhandler: HLifeErrors = BaseLifeErrors()


def set_error_handler(o: HLifeErrors):
    global errorhandler
    if not o:
        errorhandler = BaseLifeErrors()
    else:
        errorhandler = o


HLifeErrors.set_error_handler = set_error_handler


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


def get_debug_file() -> TextIO:
    return open("trace.txt", "w", encoding="utf-8")


perf_status_line: str = ""  # Buffer for status updates.


class HPerf(HHPerf):
    report_mask: cint = cint((1 << 16) - 1)  # node count between checks
    report_interval: float = 2.0  # time between update status bar

    def report(self, mark: HHPerf, verbose: cint) -> HHPerf:
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
            perf_status_line = "RATE noderate {} depth {} half {}".format(node_count / elapsed,
                                                                          1 + depth_delta / node_count,
                                                                          half_frac)
            life_status(perf_status_line)
        return self

    def report_step(self, mark: HHPerf, rate_mark: HHPerf, new_gen: float, verbose: cint) -> tuple[HHPerf, HHPerf]:
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
            perf_status_line = "PERF gps {} nps {} fps {} depth {} half {} npg {} nodes {}"\
                .format(gens_per_sec, node_count / elapsed, fps, 1 + depth_delta / node_count,
                        half_frac, nodes_per_gen, node_count)
            life_status(perf_status_line)
        self.gen_val = new_gen
        return self, self
