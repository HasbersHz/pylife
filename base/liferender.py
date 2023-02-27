from __future__ import annotations
import abc
import typing
from ctypes import c_int as cint, c_ubyte as char
from numpy import arange


class LifeRender(object, metaclass=abc.ABCMeta):
    """Encapsulate a class capable of rendering a life universe.
       Note that we only use blit_bit calls (no set_pixel).
       Coordinates are in the same coordinate system as the
       viewport min/max values.

       Also note that the render is responsible for deciding how
       to scale bits up as necessary, whether using the graphics
       hardware or the CPU.  Blits will only be called with
       reasonable bitmaps (32x32 or larger, probably) so the
       overhead should not be horrible.  Also, the bitmap must
       have zeros for all pixels to the left and right of those
       requested to be rendered (just for simplicity).

       If clipping is needed, it's the responsibility of these
       routines, *not* the caller (although the caller should make
       every effort to not call these routines without of bound
       values)."""
    __just_state: cint

    def __init__(self, state: cint = cint(0)):
        self.__just_state = state

    @property
    def just_state(self) -> cint:
        return self.__just_state

    @abc.abstractmethod
    def pix_blit(self, x: cint, y: cint, w: cint, h: cint, pm: str, pm_scale: cint) -> None:
        """pix_blit is used to draw a pixel map by passing data in two formats:
           If pm_scale == 1 then pm data contains 4*w*h bytes where each
           byte quadruplet contains the RGBA values for the corresponding pixel.
           If pm_scale > 1 then pm data contains (w/pm_scale)*(h/pm_scale) bytes
           where each byte is a cell state (0..255).  This allows the rendering
           code to display either icons or colors."""
        pass

    @abc.abstractmethod
    def get_colors(self, rgb: tuple[str, str, str], dead_alpha: str, live_alpha: str) -> None:
        """The drawing code needs access to the current layer's colors,
           and to the transparency values for dead pixels and live pixels"""
        pass

    @abc.abstractmethod
    def state_blit(self, x: cint, y: cint, w: cint, h: cint, pm: str):
        """For state renderers, this just copies the cell state; no scaling is
           supported.  Only called for __just_state renderers."""
        pass


class StateRender(LifeRender, metaclass=abc.ABCMeta):
    __buf: typing.MutableSequence
    __vw: cint
    __vh: cint

    def __init__(self, _buf: char, _vw: cint, _vh: cint):
        super(StateRender, self).__init__(cint(1))
        __buf: char = _buf
        __vw: cint = _vw
        __vh: cint = _vh

    def pix_blit(self, x: cint, y: cint, w: cint, h: cint, pm: str, pm_scale: cint) -> None:
        raise NotImplementedError("pix_blit not implemented")

    def get_colors(self, rgb: tuple[str, str, str], dead_alpha: str, live_alpha: str) -> None:
        raise NotImplementedError("get_colors not implemented")

    @abc.abstractmethod
    def state_blit(self, x: cint, y: cint, w: cint, h: cint, pm: typing.MutableSequence) -> None:
        y_min = max(y.value, 0)
        y_max = min(self.__vh.value, y.value + h.value) - 1
        x_min = max(x.value, 0)
        x_max = min(self.__vw.value, x.value + w.value) - 1
        if y_max < y_min or x_max < x_min:
            return 0
        nb = x_max - x_min + 1
        for yy in arange(y_min, y_max + 1):
            # rp = pm[yy - y.value * w.value][x_min - x.value]
            # wp = self.__buf[yy * self.__vw.value][x_min]
            for _ in arange(nb):
                self.__buf[yy * self.__vw.value][x_min] += 1 + pm[yy - y.value * w.value][x_min - x.value]
                pm[yy - y.value * w.value][x_min - x.value] += 1
