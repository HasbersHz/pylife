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

"""
(Re-)building pre-compiled headers (options: -O2 -march=native); this may take a minute ...
In file included from input_line_3:2:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\string:11:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xstring:14:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xmemory:16:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xutility:12:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\__msvc_iter_core.hpp:11:
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:151:9: error: expected member name or ';' after declaration specifiers
        !conjunction_v<_Is_implicitly_default_constructible<_Uty1>, _Is_implicitly_default_constructible<_Uty2>>)
        ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:151:9: error: expected ')'
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:150:23: note: to match this '('
    constexpr explicit(
                      ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:190:24: error: expected member name or ';' after declaration specifiers
    constexpr explicit(!conjunction_v<is_convertible<const _Other1&, _Ty1>, is_convertible<const _Other2&, _Ty2>>)
    ~~~~~~~~~~~~~~~~~~ ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:190:24: error: expected ')'
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:190:23: note: to match this '('
    constexpr explicit(!conjunction_v<is_convertible<const _Other1&, _Ty1>, is_convertible<const _Other2&, _Ty2>>)
                      ^
In file included from input_line_3:2:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\string:11:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xstring:17:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xpolymorphic_allocator.h:11:
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:268:9: error: expected member name or ';' after declaration specifiers
        !conjunction_v<_Is_implicitly_default_constructible<_This2>, _Is_implicitly_default_constructible<_Rest>...>)
        ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:268:9: error: expected ')'
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:267:23: note: to match this '('
    constexpr explicit(
                      ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:302:5: error: non-static data member cannot be constexpr; did you intend to make it const?
    constexpr explicit(_Tuple_conditional_explicit_v<tuple, const _Other&...>)
    ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:302:24: error: member '_Tuple_conditional_explicit_v' declared as a template
    constexpr explicit(_Tuple_conditional_explicit_v<tuple, const _Other&...>)
                       ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:302:79: error: expected ';' at end of declaration list
    constexpr explicit(_Tuple_conditional_explicit_v<tuple, const _Other&...>)
                                                                              ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:94:14: error: redefinition of 'wcscat_s'
    errno_t, wcscat_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:94:14: note: previous definition is here
    errno_t, wcscat_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:114:14: error: redefinition of 'wcscpy_s'
    errno_t, wcscpy_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:114:14: note: previous definition is here
    errno_t, wcscpy_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:161:38: error: redefinition of 'wcsnlen_s'
    static __inline size_t __CRTDECL wcsnlen_s(
                                     ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:161:38: note: previous definition is here
    static __inline size_t __CRTDECL wcsnlen_s(
                                     ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:172:14: error: redefinition of 'wcsncat_s'
    errno_t, wcsncat_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:172:14: note: previous definition is here
    errno_t, wcsncat_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:194:14: error: redefinition of 'wcsncpy_s'
    errno_t, wcsncpy_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:194:14: note: previous definition is here
    errno_t, wcsncpy_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:239:40: error: redefinition of '_wcstok'
    static __inline wchar_t* __CRTDECL _wcstok(
                                       ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:239:40: note: previous definition is here
    static __inline wchar_t* __CRTDECL _wcstok(
                                       ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:253:35: error: redefinition of 'wcstok'
        inline wchar_t* __CRTDECL wcstok(
                                  ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:253:35: note: previous definition is here
        inline wchar_t* __CRTDECL wcstok(
                                  ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:280:14: error: redefinition of '_wcserror_s'
    errno_t, _wcserror_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:280:14: note: previous definition is here
    errno_t, _wcserror_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:299:14: error: redefinition of '__wcserror_s'
    errno_t, __wcserror_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:299:14: note: previous definition is here
    errno_t, __wcserror_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:336:14: error: redefinition of '_wcsnset_s'
    errno_t, _wcsnset_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:336:14: note: previous definition is here
    errno_t, _wcsnset_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:361:14: error: redefinition of '_wcsset_s'
    errno_t, _wcsset_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:361:14: note: previous definition is here
    errno_t, _wcsset_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:379:14: error: redefinition of '_wcslwr_s'
    errno_t, _wcslwr_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:379:14: note: previous definition is here
    errno_t, _wcslwr_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:396:14: error: redefinition of '_wcslwr_s_l'
    errno_t, _wcslwr_s_l,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:396:14: note: previous definition is here
    errno_t, _wcslwr_s_l,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:415:14: error: redefinition of '_wcsupr_s'
    errno_t, _wcsupr_s,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:415:14: note: previous definition is here
    errno_t, _wcsupr_s,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:432:14: error: redefinition of '_wcsupr_s_l'
    errno_t, _wcsupr_s_l,
             ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:432:14: note: previous definition is here
    errno_t, _wcsupr_s_l,
             ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:529:31: error: redefinition of 'wcschr'
    inline wchar_t* __CRTDECL wcschr(_In_z_ wchar_t* _String, wchar_t _C)
                              ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:529:31: note: previous definition is here
    inline wchar_t* __CRTDECL wcschr(_In_z_ wchar_t* _String, wchar_t _C)
                              ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:535:31: error: redefinition of 'wcspbrk'
    inline wchar_t* __CRTDECL wcspbrk(_In_z_ wchar_t* _String, _In_z_ wchar_t const* _Control)
                              ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:535:31: note: previous definition is here
    inline wchar_t* __CRTDECL wcspbrk(_In_z_ wchar_t* _String, _In_z_ wchar_t const* _Control)
                              ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:541:31: error: redefinition of 'wcsrchr'
    inline wchar_t* __CRTDECL wcsrchr(_In_z_ wchar_t* _String, _In_ wchar_t _C)
                              ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:541:31: note: previous definition is here
    inline wchar_t* __CRTDECL wcsrchr(_In_z_ wchar_t* _String, _In_ wchar_t _C)
                              ^
In file included from input_line_4:4:
In file included from C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\string.h:14:
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:548:31: error: redefinition of 'wcsstr'
    inline wchar_t* __CRTDECL wcsstr(_In_z_ wchar_t* _String, _In_z_ wchar_t const*_SubStr)
                              ^
C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt\corecrt_wstring.h:548:31: note: previous definition is here
    inline wchar_t* __CRTDECL wcsstr(_In_z_ wchar_t* _String, _In_z_ wchar_t const*_SubStr)
                              ^
fatal error: too many errors emitted, stopping now [-ferror-limit=]
Error: Error loading the default header files.
C:\...\AppData\Roaming\Python\Python310\site-packages\cppyy_backend\loader.py:139: UserWarning: No precompiled header available (failed to build); this may impact performance.
  warnings.warn('No precompiled header available (%s); this may impact performance.' % msg)
In file included from input_line_3:1:
In file included from C:/.../AppData/Roaming/Python/Python310/site-packages/cppyy_backend\include\Rtypes.h:179:
In file included from C:/.../AppData/Roaming/Python/Python310/site-packages/cppyy_backend\include/TGenericClassInfo.h:15:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\string:11:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xstring:14:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xmemory:16:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xutility:12:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\__msvc_iter_core.hpp:11:
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:151:9: error: expected member name or ';' after declaration specifiers
        !conjunction_v<_Is_implicitly_default_constructible<_Uty1>, _Is_implicitly_default_constructible<_Uty2>>)
        ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:151:9: error: expected ')'
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:150:23: note: to match this '('
    constexpr explicit(
                      ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:190:24: error: expected member name or ';' after declaration specifiers
    constexpr explicit(!conjunction_v<is_convertible<const _Other1&, _Ty1>, is_convertible<const _Other2&, _Ty2>>)
    ~~~~~~~~~~~~~~~~~~ ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:190:24: error: expected ')'
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\utility:190:23: note: to match this '('
    constexpr explicit(!conjunction_v<is_convertible<const _Other1&, _Ty1>, is_convertible<const _Other2&, _Ty2>>)
                      ^
In file included from input_line_3:1:
In file included from C:/.../AppData/Roaming/Python/Python310/site-packages/cppyy_backend\include\Rtypes.h:179:
In file included from C:/.../AppData/Roaming/Python/Python310/site-packages/cppyy_backend\include/TGenericClassInfo.h:15:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\string:11:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xstring:17:
In file included from C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\xpolymorphic_allocator.h:11:
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:268:9: error: expected member name or ';' after declaration specifiers
        !conjunction_v<_Is_implicitly_default_constructible<_This2>, _Is_implicitly_default_constructible<_Rest>...>)
        ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:268:9: error: expected ')'
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:267:23: note: to match this '('
    constexpr explicit(
                      ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:302:5: error: non-static data member cannot be constexpr; did you intend to make it const?
    constexpr explicit(_Tuple_conditional_explicit_v<tuple, const _Other&...>)
    ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:302:24: error: member '_Tuple_conditional_explicit_v' declared as a template
    constexpr explicit(_Tuple_conditional_explicit_v<tuple, const _Other&...>)
                       ^
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.34.31933\include\tuple:302:79: error: expected ';' at end of declaration list
    constexpr explicit(_Tuple_conditional_explicit_v<tuple, const _Other&...>)
                                                                              ^
Traceback (most recent call last):
  File "C:\Program Files\Python310\lib\code.py", line 90, in runcode
    exec(code, self.locals)
  File "<input>", line 1, in <module>
  File "D:/Programming/Python/old/life/life/base/test.py", line 1, in <module>
    import cppyy
  File "C:\...\AppData\Roaming\Python\Python310\site-packages\cppyy\__init__.py", line 80, in <module>
    from ._cpython_cppyy import *
  File "C:\...\AppData\Roaming\Python\Python310\site-packages\cppyy\_cpython_cppyy.py", line 21, in <module>
    c = loader.load_cpp_backend()
  File "C:\...\AppData\Roaming\Python\Python310\site-packages\cppyy_backend\loader.py", line 92, in load_cpp_backend
    raise RuntimeError("could not load cppyy_backend library, details:\n%s" %
RuntimeError: could not load cppyy_backend library, details:
"""