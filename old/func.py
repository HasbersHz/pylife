import ctypes
from typing import Mapping, Any
import pygame_menu as pgm

import pygame as pg
import numpy as np
from numba import njit, cuda
from config import *


@njit
def orderer(array, res, i, j, order=0):
    i_left = i - 1 if i > 1 else res[0]
    i_right = i + 1 if i < res[0] else 1
    j_top = j - 1 if j > 1 else res[1]
    j_bottom = j + 1 if j < res[1] else 1

    return array[i_left, j], array[i_right, j], array[i, j_top], array[i, j_bottom], \
           array[i_left, j_top], array[i_right, j_bottom], array[i_left, j_bottom], array[i_right, j_top]


@njit
def clear_edges(array, how=False):
    la = len(array[0])
    lb = len(array)
    if how:
        array[0, :] = np.ones(la)
        array[-1, :] = np.ones(la)
        array[:, 0] = np.ones(lb)
        array[:, -1] = np.ones(lb)
    else:
        array[0, :] = np.zeros(la)
        array[-1, :] = np.zeros(la)
        array[:, 0] = np.zeros(lb)
        array[:, -1] = np.zeros(lb)
    return array


@njit  # cuda.jit('void(int64[:, :], int64[:], int64[:], int64)')
def cells_update(prev: np.ndarray, res: tuple, rules: tuple, order: int) -> np.ndarray:
    nex = prev.copy()
    for i in np.arange(0, res[0]):
        for j in np.arange(0, res[1]):
            i_l = i - 1 if i >= 0 else res[0] - 1  # left
            i_r = i + 1 if i < res[0] - 1 else 0   # right
            j_t = j - 1 if j >= 0 else res[1] - 1  # top
            j_b = j + 1 if j < res[1] - 1 else 0   # bottom
            summa = prev[i_l, j] + prev[i_r, j] + prev[i, j_t] + prev[i, j_b] + prev[i_l, j_t] + \
                    prev[i_r, j_b] + prev[i_l, j_b] + prev[i_r, j_t]
            # nex[i, j] = rules.func(prev[i, j], summa)
            cell = prev[i, j]
            if cell == 1:
                if summa not in rules[1]:
                    nex[i, j] = 0
            elif cell == 0:
                if summa in rules[0]:
                    nex[i, j] = 1
    return nex


class Camera:
    def __init__(self, width, height):
        self.dx = 0
        self.dy = 0
        self.width, self.height = width, height

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - self.width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - self.height // 2)


class Cell(pg.sprite.Sprite):
    def __init__(self, group: pg.sprite.Group, pos: tuple[int, int], color: tuple[int, int, int]):
        super(Cell, self).__init__(group)
        self.rect = pg.Rect([pos[0] * SIZE, pos[1] * SIZE, SIZE, SIZE])
        self.image = pg.Surface((self.rect.width, self.rect.height))
        self.image.fill(color)
        self.pos = pos

    def update(self, array: np.ndarray, *args: Any, **kwargs: Any) -> None:
        if array[self.pos]:
            self.image.fill(ALIVE)
        else:
            self.image.fill(DEAD)
        # self.image.fill(CELL_COLORS.get(array[self.pos], ERROR_COLOR))


def start_screen(surf, clock):
    surf.fill(BLACK)
    menu = pgm.Menu("Pylife", theme=pgm.themes.THEME_DARK)

    while True:
        pg.display.flip()
        clock.tick(FPS)

"""
@njit  # cuda.jit('void(int64[:, :], int64[:], int64[:], int64)')
def cells_update(prev: np.ndarray, res: tuple, rules: tuple, order: int) -> np.ndarray:
    nex = prev.copy()
    for i in np.arange(0, res[0]):
        for j in np.arange(0, res[1]):
            summa = np.sum(orderer(prev, res, i, j))
            # nex[i, j] = rules.func(prev[i, j], summa)
            match prev[i, j]:
                case 1:
                    if summa not in rules[1]:
                        nex[i, j] = 0
                case 0:
                    if summa in rules[0]:
                        nex[i, j] = 1
    return nex


@njit
def _cells_update(prev: np.ndarray, res: tuple, rules: tuple, order: int) -> np.ndarray:
    nex = np.zeros((res[0] + 2, res[1] + 2), dtype=int)
    nex[1:-1, 1:-1] = prev.copy()

    for i in np.arange(1, res[0] + 1):
        for j in np.arange(1, res[1] + 1):
            summa = np.sum(prev[i - order:i + order + 1, j - order:j + order + 1]) - prev[i, j]

            # обработка граничных случаев на торе
            i_left = i - 1 if i > 1 else res[0]
            i_right = i + 1 if i < res[0] else 1
            j_top = j - 1 if j > 1 else res[1]
            j_bottom = j + 1 if j < res[1] else 1
            summa += prev[i_left, j] + prev[i_right, j] + prev[i, j_top] + prev[i, j_bottom] + prev[i_left, j_top] + \
                     prev[i_right, j_bottom] + prev[i_left, j_bottom] + prev[i_right, j_top]

            match prev[i, j]:
                case 1:
                    if summa not in rules[1]:
                        nex[i, j] = 0
                case 0:
                    if summa in rules[0]:
                        nex[i, j] = 1

    return nex[1:-1, 1:-1].copy()
"""
