from __future__ import annotations
from ctypes import c_int as cint

import lifealgo
from overloading import overload


MAX_MAG: cint = cint(4)
# maximum cell size is 2^MAX_MAG (default is 2^4, but devices with
# high-resolution screens will probably want a bigger cell size)


class Viewport:
    """This class holds information on where in space the user's window is.
       It provides the functions to zoom, unzoom, move, etc.

       The reason we need a whole class is because doing this in a universe
       that may be billions of billions of cells on a side, but we still
       want single cell precision, is a bit tricky."""
    # cell at center of viewport
    x: int
    y: int
    width: cint
    height: cint
    mag: cint  # plus is zoom in; neg is zoom out
    x0: int
    y0: int
    x0f: float
    y0f: float
    xymf: float  # always = 2**-mag

    def __init__(self, width: cint, height: cint):
        self.init()
        self.resize(width, height)

    def init(self):
        self.x = self.y = self.x0 = self.y0 = 0
        self.height = self.width = cint(8)
        self.mag = cint(0)
        self.x0f = self.y0f = self.xymf = 0.0

    def reposition(self):
        """recalculate *0* and *m* values"""
        self.xymf = 2.0 ** -self.mag.value
        w: int = self.get_width().value
        w = self.mul_pow2(w, -self.mag.value)
        w >>= 1
        self.x0 = self.x
        self.x0 -= w
        w = self.get_height().value
        w = self.mul_pow2(w, -self.mag.value)
        w >>= 1
        self.y0 = self.y
        self.y0 -= w
        self.y0f = float(self.y0)
        self.x0f = float(self.x0)

    @overload
    def zoom(self: Viewport) -> None:
        if self.mag >= MAX_MAG:
            return
        self.mag += 1
        self.reposition()

    @overload
    def zoom(self: Viewport, xx: cint, yy: cint) -> None:
        if self.mag >= MAX_MAG:
            return
        old_pos = self.at(xx, yy)  # save cell pos for use below
        self.x += self.mul_pow2(xx.value * 2 - self.get_x_max().value, -self.mag.value - 2)
        self.y += self.mul_pow2(yy.value * 2 - self.get_y_max().value, -self.mag.value - 2)
        self.mag += 1
        self.reposition()
        # adjust cell position if necessary to avoid any drift`
        if self.mag.value >= 0:
            drift = self.at(xx, yy)
            drift[0] -= old_pos[0]
            drift[1] -= old_pos[1]
            # drifts will be -1, 0 or 1
            if drift[0]:
                self.move(cint(-drift[0] << self.mag.value), cint(0))
            if drift[1]:
                self.move(cint(0), cint(-drift[1] << self.mag.value))

    @overload
    def unzoom(self: Viewport) -> None:
        self.mag -= 1
        self.reposition()

    @overload
    def unzoom(self: Viewport, xx: cint, yy: cint) -> None:
        old_pos = self.at(xx, yy)  # save cell pos for use below
        self.mag -= 1
        self.x -= self.mul_pow2(xx.value * 2 - self.get_x_max().value, -self.mag.value - 2)
        self.y -= self.mul_pow2(yy.value * 2 - self.get_y_max().value, -self.mag.value - 2)
        self.reposition()
        if self.mag.value >= 0:
            # adjust cell position if necessary to avoid any drift
            drift = self.at(xx, yy)
            drift[0] -= old_pos[0]
            drift[1] -= old_pos[1]
            # drifts will be -1, 0 or 1
            if drift[0]:
                self.move(cint(-drift[0] << self.mag.value), cint(0))
            if drift[1]:
                self.move(cint(0), cint(-drift[1] << self.mag.value))

    def center(self):
        ...

    def at(self, x: cint, y: cint) -> tuple[int, int]:
        r: list[int, int] = [x.value, y.value]
        r[0] = self.mul_pow2(r[0], -self.mag.value)
        r[1] = self.mul_pow2(r[0], -self.mag.value)
        r[0] += self.x0
        r[1] += self.y0
        return tuple(r)

    def atf(self, xx, yy) -> float:
        ...

    def screen_pos_of(self, x: int,  y: int, algo: lifealgo.LifeAlgo) -> tuple[cint, cint]:
        """Returns the screen position of a particular pixel. Note that this
           is a tiny bit more complicated than you might expect, because it
           has to take into account exactly how a life algorithm compresses
           multiple pixels into a single pixel (which depends not only on the
           LifeAlgo, but in the case of QLifeAlgo, *also* depends on the
           generation count).  In the case of mag < 0, it always returns
           the upper left pixel; it's up to the caller to adjust when
           mag<0."""
        ...

    def resize(self, new_width: cint, new_height: cint):
        ...

    def move(self, dx: cint, dy: cint):   # dx and dy are given in pixels
        ...

    def get_mag(self) -> cint:
        return self.mag

    def set_mag(self, mag_arg: cint) -> None:
        self.mag = mag_arg
        self.reposition()

    @overload
    def set_position_mag(self, x_arg: int, y_arg: int, mag_arg: cint) -> None:
        ...

    @overload
    def set_position_mag(self, xlo: int, xhi: int, ylo: int, yhi: int, mag_arg: cint) -> None:
        ...

    def get_width(self) -> cint:
        return self.width

    def get_height(self) -> cint:
        return self.height

    def get_x_max(self) -> cint:
        return cint(self.width.value - 1)

    def get_y_max(self) -> cint:
        return cint(self.height.value - 1)

    def contains(self, x: int, y: int):
        ...

    @staticmethod
    def mul_pow2(num: int, power: int) -> int:
        if power > 0:
            num <<= power
        elif power < 0:
            num >>= power
        return power
