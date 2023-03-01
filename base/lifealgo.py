from __future__ import annotations
import abc
import ctypes
import enum
import io
import sys
import typing
import numba
import numpy
import numpy as np

from overloading import overload

import liferender
import viewport
import lifepoll

cint = ctypes.c_int
uchar = numpy.ubyte
ptr = ctypes.pointer
point = ctypes.byref

# this must not be increased beyond 32767, because we use a bigint
# multiply that only supports multiplicands up to that size.
MAX_FRAME_COUNT = cint(32000)

TGridType = enum.Enum("TGridType", ["SQUARE_GRID", "TRI_GRID", "HEX_GRID", "VN_GRID"])


class TimeLine:
    """Timeline support is pretty generic."""
    recording: cint
    frame_count: cint
    base: cint
    expo: cint
    save_timeline: cint
    start: int
    inc: int
    next_: int
    end: int
    frames: list

    def __init__(self):
        recording, frame_count, save_timeline = cint(0), cint(0), cint(1)
        start, inc, next_, end = 0, 0, 0, 0
        frames: list = []


class LifeAlgo(object, metaclass=abc.ABCMeta):
    _poller: lifepoll.LifePoll
    _verbose: cint
    _max_cell_states: cint  # keep up to date; set_cell depends on it
    _generation: int
    _increment: int
    _timeline: TimeLine
    _grid_type: enum.Enum

    # support for a bounded universe with various topologies:
    # plane, cylinder, torus, Klein bottle, cross-surface, sphere
    grid: dict[str: int] = {
        "wd": 0, "ht": 0,       # bounded universe if either is > 0
        "left": 0, "right": 0,  # undefined if grid[wd] is 0
        "top": 0, "bottom": 0   # undefined if grid[ht] is 0
    }
    bounded_plane: bool         # topology is a bounded plane?
    sphere: bool                # topology is a sphere?
    twist: dict[str: bool] = {  # Klein bottle if either is true,
        "v": False, "h": False  # or cross-surface if both are true
    }
    shift: dict[str: int] = {
        "v": 0, "h": 0          # torus with horizontal or vertical shift
    }

    unbounded: bool
    # algorithms that use a finite universe should set this flag false
    # so the GUI code won't call create_border_cells or delete_border_cells

    clipped_cells: typing.Any
    # algorithms that use a finite universe need to save live cells
    # that might be clipped when a setter.rule call reduces the size of
    # the universe (this allows the GUI code to restore the cells
    # if the rule change is undone)

    def __init__(self):
        self._generation = 0
        self._increment = 0
        self._timeline = TimeLine()
        self._grid_type = TGridType["SQUARE_GRID"]

        self._poller = lifepoll.default_poller
        self.grid["wd"] = self.grid["ht"] = 0   # default is an unbounded universe
        self.unbounded = True                   # most algorithms use an unbounded universe

    def __del__(self):
        self._poller = lifepoll.LifePoll()
        self._max_cell_states = cint(2)

    # @abc.abstractmethod
    def set_cell(self, x: cint, y: cint, new_state: cint) -> cint:
        return cint(0)

    # @abc.abstractmethod
    def get_cell(self, x: cint, y: cint) -> cint:
        return cint(0)

    # @abc.abstractmethod
    def next_cell(self, x: cint, y: cint, v: cint) -> cint:
        return cint(0)

    def get_cells(self, buf, x: cint, y: cint, w: cint, h: cint) -> None:
        vp = viewport.Viewport(w, h)
        vp.set_position_mag(x.value + (w.value >> 1), y.value + (h.value >> 1), cint(0))
        hsr = liferender.StateRender(buf, w, h)
        buf = "0" * w.value * h.value
        self.draw(vp, hsr)

    def end_of_pattern(self):
        """call after set_cell calls"""
        return cint(0)

    @property
    def increment(self) -> int:
        return self._increment

    @increment.setter
    def increment(self, inc: int | cint) -> None:
        pass

    @property
    def generation(self) -> int:
        return self._generation

    @generation.setter
    def generation(self, gen):
        pass

    @property
    def population(self) -> int:
        return 0

    def is_empty(self) -> cint:
        return cint(0)

    def hyper_capable(self) -> cint:
        """can we do the gen count doubling? only hashlife"""
        return cint(0)

    @property
    def max_memory(self) -> cint:
        """never alloc more than this"""
        return cint(0)

    @max_memory.setter
    def max_memory(self, value: cint):
        pass

    @property
    def rule(self):
        """get current rule set"""
        return

    @rule.setter
    def rule(self, value):
        """new rules; returns err msg"""
        pass

    def step(self) -> None:
        """do inc gens"""
        ...

    def draw(self, view: viewport.Viewport, renderer: liferender.LifeRender) -> None:
        ...

    def fit(self, view: viewport.Viewport, force: cint) -> None:
        ...

    def find_edges(self, tt: int, ll: int, bb: int, rr: int) -> None:
        ...

    def lower_right_pixel(self, x: int, y: int, mag: cint) -> None:
        ...

    def write_native_format(self, os: io.StringIO, comments: str) -> str:
        ...

    @property
    def poll(self) -> lifepoll.LifePoll:
        return self._poller

    @poll.setter
    def poll(self, poller_arg: lifepoll.LifePoll) -> None:
        self._poller = poller_arg

    def read_macrocell(self, *d) -> str:
        return "Cannot read macrocell format."

    @property
    def verbose(self) -> cint:
        """Verbosity crosses algorithms.  We need to embed this sort of option
           into some global shared thing or something rather than use static."""
        return self._verbose

    @verbose.setter
    def verbose(self, v: cint) -> None:
        self._verbose = v

    @property
    def default_rule(self) -> str:
        return "B3/S23"

    @property
    def num_cell_states(self) -> cint:
        """return number of cell states in this universe (2..256)"""
        return cint(2)

    @property
    def num_randomized_cell_states(self):
        """return number of states to use when setting random cells"""
        return self.num_cell_states

    # timeline support

    @property
    def current_state(self):
        return

    @current_state.setter
    def current_state(self, value):
        pass

    def start_recording(self, base: cint, expo: cint) -> cint:
        """Right now, the base/expo should match the current increment.
           We do not check this."""
        if self._timeline.frame_count:
            # already have a timeline; skip to its end
            self.go_to_frame(cint(self._timeline.frame_count.value - 1))
        else:
            # use the current frame and increment to start a new timeline
            now = self.current_state
            if now == 0:
                return cint(0)
            self._timeline.base = base
            self._timeline.expo = expo
            self._timeline.frames.append(now)
            self._timeline.frame_count = cint(1)
            self._timeline.end = self._timeline.start = self._generation
            self._timeline.inc = self._increment

        self._timeline.next_ = self._timeline.end
        self._timeline.next_ += self._timeline.inc
        self._timeline.recording = cint(1)
        return self._timeline.frame_count

    def stop_recording(self) -> tuple[cint, cint]:
        self._timeline.recording = cint(0)
        self._timeline.next = 0
        return self._timeline.base, self._timeline.expo

    @property
    def base_expo(self) -> tuple[cint, cint]:
        return self._timeline.base, self._timeline.expo

    def extended_timeline(self) -> None:
        if self._timeline.recording and self._generation == self._timeline.next_:
            now = self.current_state
            if now and self._timeline.frame_count < MAX_FRAME_COUNT:
                self._timeline.frames.append(now)
                self._timeline.frame_count += 1
                self._timeline.end = self._timeline.next_
                self._timeline.next_ += self._timeline.inc

    def prune_frames(self) -> None:
        """Note that this *also* changes inc, so don't call unless this is
           what you want to do.  It does not update or change the base or
           expo if the base != 2, so they can get out of sync.

           Currently this is only used by bgolly, and it will only work
           properly if the increment argument is a power of two."""
        if self._timeline.frame_count.value > 1:
            for i in range(2, self._timeline.frame_count.value, 2):
                self._timeline.frames[i >> 1] = self._timeline.frames[i]
            self._timeline.frame_count = cint((self._timeline.frame_count.value + 1) >> 1)
            self._timeline.inc += self._timeline.inc
            self._timeline.end = self._timeline.inc
            self._timeline.end *= self._timeline.frame_count.value - 1
            self._timeline.end += self._timeline.start
            self._timeline.next = self._timeline.end
            self._timeline.next += self._timeline.inc
            if self._timeline.base == 2:
                self._timeline.expo = cint(self._timeline.expo.value + 1)

    @property
    def timeline_start(self) -> int:
        return self._timeline.start

    @property
    def timeline_end(self) -> int:
        return self._timeline.end

    @property
    def timeline_inc(self) -> int:
        return self._timeline.inc

    @property
    def timeline_frame_count(self) -> cint:
        return self._timeline.frame_count

    @property
    def is_recording(self) -> cint:
        return self._timeline.recording

    def go_to_frame(self, i: int) -> cint:
        if i < 0 or i >= self._timeline.frame_count.value:
            return cint(0)
        self.current_state = (self._timeline.frames[i])
        # AKT: avoid mul_smallint(i) crashing with divide-by-zero if i is 0
        if i > 0:
            self.generation = self._timeline.inc * i
        else:
            self.generation = 0
        self.generation += self._timeline.start
        return self._timeline.frame_count

    def destroy_timeline(self) -> None:
        self._timeline.frames.clear()
        self._timeline.recording = cint(0)
        self._timeline.frame_count = cint(0)
        self._timeline.end = 0
        self._timeline.start = 0
        self._timeline.inc = 0
        self._timeline.next_ = 0

    def save_timeline_with_frame(self, yesno: cint) -> None:
        self._timeline.save_timeline = yesno

    @property
    def grid_size(self) -> str:
        """use in setter.rule to parse a suffix like ":T100,200" and set
           the above parameters"""
        return

    # @grid_size.setter
    def set_grid_size(self, suffix: str) -> str:
        """parse a rule suffix like ":T100,200" and set the various grid parameters;
           note that we allow any legal partial suffix -- this lets people type a
           suffix into the Set Rule dialog without the algorithm changing to UNKNOWN"""
        p = 0
        topology = 0
        self.grid["wd"] = self.grid["ht"] = 0
        self.shift["h"] = self.shift["v"] = 0
        self.twist["h"] = self.twist["v"] = False
        self.bounded_plane = False
        self.sphere = False
        suffix = suffix.lower() + chr(0)

        p += 1
        d = suffix[p]
        if d == chr(0):
            return chr(0)                 # treat ":" like ":T0,0"
        if d == 't':
            # torus or infinite tube
            topology = 'T'
        elif d == 'p':
            self.bounded_plane = True
            topology = 'P'
        elif d == 's':
            self.sphere = True
            topology = 'S'
        elif d == 'k':
            # Klein bottle (either twist[h] or twist[v] should become true)
            topology = 'K'
        elif d == 'c':
            # cross-surface
            self.twist["h"] = self.twist["v"] = True
            topology = 'C';
        else:
            return "Unknown grid topology."

        p += 1
        d = suffix[p]
        if d == chr(0):
            return chr(0)                 # treat ":<char>" like ":T0,0"

        while d.isdigit():
            if self.grid["wd"] >= 200000000:
                self.grid["wd"] =  2000000000           # keep width within editable limits
            else:
                self.grid["wd"] = 10 * self.grid["wd"] + int(d)
            p += 1
            d = suffix[p]

        if d == '*':
            if topology != 'K':
                return "Only specify a twist for a Klein bottle."
            self.twist["h"] = True
            p += 1
            d = suffix[p]
        if d in ('+', '-'):
            if topology == 'P':
                return "Plane can't have a shift."
            if topology == 'S':
                return "Sphere can't have a shift."
            if topology == 'C':
                return "Cross-surface can't have a shift."
            if topology == 'K' and not self.twist['h']:
                return "Shift must be on twisted edges."
            if self.grid["wd"] == 0:
                return "Can't shift infinite width."
            sign: int = 1 if d == '+' else -1
            p += 1
            d = suffix[p]
            while d.isdigit():
               self.shift['h'] = 10 * self.shift['h'] + int(d)
               p += 1
               d = suffix[p]
            if self.shift['h'] >= self.grid['wd']:
                self.shift['h'] = self.shift['h'] % self.grid['wd']
            self.shift['h'] *= sign
        if d == ',' and topology != 'S':
            p += 1
            d = suffix[p]
        elif d:
            return "Unexpected stuff after grid width."
        # grid[wd] has been set
        if (topology in ('K', "C", 'S')) and not self.grid['wd']:
            return "Given topology can't have an infinite width."

        if ord(d) == 0:
            # grid height is not specified so set it to grid width;
            # ie. treat ":T100" like ":T100,100";
            # this also allows us to have ":S100" rather than ":S100,100"
            self.grid['ht'] = self.grid['wd']
        else:
            while d.isdigit():
                if self.grid['ht'] >= 200000000:
                   self.grid['ht'] =  2000000000     # keep height within editable limits
                else:
                   self.grid['ht'] = 10 * self.grid['ht'] + ord(d) - ord('0')
                p += 1
                d = suffix[p]
            if d == '*':
                if topology != 'K':
                    return "Only specify a twist for a Klein bottle."
                if self.twist['h']:
                    return "Klein bottle can't have both horizontal and vertical twists."
                self.twist['v'] = True
                p += 1
                d = suffix[p]
            if d in ('+', '-'):
                if topology == 'P':
                    return "Plane can't have a shift."
                if topology == 'C':
                    return "Cross-surface can't have a shift."
                if topology == 'K' and not self.twist['v']:
                    return "Shift must be on twisted edges."
                if self.shift['h'] != 0:
                    return "Can't have both horizontal and vertical shifts."
                if self.grid['ht'] == 0:
                    return "Can't shift infinite height."
                sign: int = 1 if d == '+' else -1
                p += 1
                d = suffix[p]
                while d.isdigit():
                   self.shift['v'] = 10 * self.shift['v'] + int(d)
                   p += 1
                   d = suffix[p]
                if self.shift['v'] >= self.grid['ht']:
                    self.shift['v'] = self.shift['v'] % self.grid['ht']
                self.shift['v'] *= sign
            if d:
                return "Unexpected stuff after grid height."
        # grid[ht] has been set
        if topology in ('K', 'C') and not self.grid['ht']:
            return "Klein bottle or cross-surface can't have an infinite height."

        if topology == 'K' and not (self.twist['h'] or self.twist['v']):
            # treat ":K10,20" like ":K10,20*"
            self.twist['v'] = True

        if (self.shift['h'] or self.shift['v']) and (not self.grid['wd'] or not self.grid['ht']):
            return "Shifting is not allowed if either grid dimension is unbounded."

        # now ok to set grid edges
        if self.grid['wd'] > 0:
            self.grid['left']= -self.grid['wd'] // 2
            self.grid['right'] = self.grid['wd'] - 1
            self.grid['right'] += self.grid['left']
        else:
            # play safe and set these to something
            self.grid['left'] = 0
            self.grid['right'] = 0
        if self.grid['ht'] > 0:
            self.grid['top'] = -self.grid['ht'] // 2
            self.grid['bottom'] = self.grid['ht'] - 1
            self.grid['bottom'] += self.grid['top']
        else:
            # play safe and set these to something
            self.grid['top'] = 0
            self.grid['bottom'] = 0
        return chr(0)

    @property
    def grid_type(self) -> enum.Enum:
        return self._grid_type

    def canonical_suffix(self) -> str:
        """use in setter.rule to return the canonical version of suffix;
           eg. ":t0020" would be converted to ":T20,0"""
        if self.grid['wd'] > 0 or self.grid['ht'] > 0:
            bounds: str
            if self.bounded_plane:
                bounds = f":P{self.grid['wd']},{self.grid['ht']}"
            elif self.sphere:
                # sphere requires a square grid (grid[wd] == grid[ht])
                bounds = f":S{self.grid['wd']}"
            elif self.twist['h'] and self.twist['v']:
                # cross-surface if both horizontal and vertical edges are twisted
                bounds = f":C{self.grid['wd']},{self.grid['ht']}"
            elif self.twist['h']:
                # Klein bottle if only horizontal edges are twisted
                if self.shift['h'] and not (self.grid['wd'] & 1):
                    # twist and shift is only possible if grid[wd] is even and shift[h] is 1
                    bounds = f":K{self.grid['wd']}*+1,{self.grid['ht']}"
                else:
                    bounds = f":K{self.grid['wd']}*,{self.grid['ht']}"
            elif self.twist['v']:
                # Klein bottle if only vertical edges are twisted
                if self.shift['v'] and not (self.grid['ht'] & 1):
                    # twist and shift is only possible if gridht is even and vshift is 1
                    bounds = f":K{self.grid['wd']},{self.grid['ht']}*+1"
                else:
                    bounds = f":K{self.grid['wd']},{self.grid['ht']}*"
            elif self.shift['h'] < 0:
                # torus with -ve horizontal shift
                bounds = f":T{self.grid['wd']}{self.shift['h']},{self.grid['ht']}"
            elif self.shift['h'] > 0:
                # torus with +ve horizontal shift
                bounds = f":T{self.grid['wd']}+{self.shift['h']},{self.grid['ht']}"
            elif self.shift['v'] < 0:
                # torus with -ve vertical shift
                bounds = f":T{self.grid['wd']},{self.grid['ht']}{self.shift['v']}"
            elif self.shift['v'] > 0:
                # torus with +ve vertical shift
                bounds = f":T{self.grid['wd']},{self.grid['ht']}+{self.shift['v']}"
            else:
                # unshifted torus, or an infinite tube
                bounds = f":T{self.grid['wd']},{self.grid['ht']}"
            return bounds
        else:
            # unbounded universe
            return chr(0)

    # the above routines can be called around step() to create the
    # illusion of a bounded universe (note that increment must be 1);
    # they return false if the pattern exceeds the editing limits

    def create_border_cells(self) -> bool:
        ...

    def delete_border_cells(self) -> bool:
        ...

    # following are called by create_border_cells() to join edges in various ways

    def join_twisted_edges(self) -> None:
        ...

    def join_twisted_and_shifted_edges(self) -> None:
        ...

    def join_shifted_edges(self) -> None:
        ...

    def join_adjacent_edges(self, pt: cint, pl: cint, pb: cint, pr: cint) -> None:
        ...

    def join_edges(self, pt: cint, pl: cint, pb: cint, pr: cint) -> None:
        ...

    # following is called by delete_border_cells()

    def clear_rect(self,  top: cint,  left: cint,  bottom: cint,  right: cint):
        ...


class StaticAlgoInfo(object):
    """If you need any static information from a LifeAlgo, this class can be
       called (or overridden) to set up all that data.  Right now the
       functions do nothing; override if you need that info. These are
       called one by a static method in the algorithm itself,
       if that information is available. The ones marked optional need
       not be called."""

    def __init__(self):
        ...

    def __del__(self):
        ...

    # mandatory
    @property
    def algorithm_name(self):
        return self.algo_name

    @algorithm_name.setter
    def algorithm_name(self, s: str):
        self.algo_name = s

    @property
    def algorithm_creator(self):
        return self.creator

    @algorithm_creator.setter
    def algorithm_creator(self, value: ptr[LifeAlgo]):
        self.creator = value

    # // optional; override if you want to retain this data
    # virtual void setDefaultBaseStep(int) {}
    # virtual void setDefaultMaxMem(int) {}

    # minimum and maximum number of cell states supported by this algorithm;
    # both must be within 2..256
    min_states: cint
    max_states: cint

    # default color scheme
    def_gradient: bool                      # use color gradient?
    def1 = {"r": uchar(), "g": uchar(), "b": uchar()}     # color at start of gradient
    def2 = {"r": uchar(), "g": uchar(), "b": uchar()}     # color at end of gradient
    # if def_gradient is false then use these colors for each cell state
    defn = np.array((3, 256), cint)  # r, g, b
    # default icon data (in XPM format)
    def_xpm7x7: str     # 7x7 icons
    def_xpm15x15: str   # 15x15 icons
    def_xpm31x31: str   # 31x31 icons
    # basic data
    algo_name: str
    creator: ptr[LifeAlgo]
    id: cint  # my index
    next: StaticAlgoInfo

    # support:  give me sequential algorithm IDs
    next_algo_id: cint

    @property
    def num_algos(self) -> cint:
        return self.next_algo_id

    def tick(self) -> StaticAlgoInfo:  # &tick()
        ...

    head: StaticAlgoInfo  # *head

    def by_name(self, s: str) -> StaticAlgoInfo:  # *byName(const char *s)
        ...

    def name_to_index(self, s: str) -> cint:
        ...
