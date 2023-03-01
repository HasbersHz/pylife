# -*- coding: utf-8 -*-
r"""E:\Apps\Python\python.exe -m pyinstaller --add-data "config.py;." -w E:/life/main.py"""
from __future__ import annotations

import math
import sys
import time
from typing import Mapping

import numpy as np
import pygame as pg
import asyncio as ai
from numba import njit
from pygame.surface import Surface, SurfaceType
from pygame_menu import Menu

from func import clear_edges, cells_update
from menu import Button

from config import *


async def draw_cells(cells: Mapping, x: int | None = None, y: int | None = None, w: int | None = None, h: int | None = None):
    if x is None:
        x = 0
    if y is None:
        y = 0
    if w is None:
        w = len(cells)
    if h is None:
        h = len(cells[0])
    async for i in np.arange(x, w):
        async for j in np.arange(y, h):
            match cells[i, j]:
                case 1:
                    pg.draw.rect(WINDOW, ALIVE, [i * SIZE, j * SIZE, SIZE, SIZE])
                case 0:
                    pg.draw.rect(WINDOW, DEAD, [i * SIZE, j * SIZE, SIZE, SIZE])
                case _:
                    pg.draw.rect(WINDOW, ERROR_COLOR, [i * SIZE, j * SIZE, SIZE, SIZE])


def menu(wind, but_exit, but_return):
    wind.fill(COLOR_INTERFACE)
    but_exit.draw(wind)
    but_return.draw(wind)


def main():
    cells: np.ndarray = np.random.randint(0, 2, RESOLUTION, dtype="byte")

    for i in (False, True, False):
        cells = clear_edges(cells, i)

    clock: pg.time.Clock = pg.time.Clock()

    all_sprites: pg.sprite.Group = pg.sprite.Group()

    population = 0
    is_running: bool = True
    # work: dict[str: bool, str: bool] = {"p": False, "menu": False}
    is_pause = False
    is_menu = False
    is_edge = False
    looper: int = 0

    # Buttons
    but_exit = Button('Exit', BLACK, WHITE, IMAGES, 'button1.png', FONT, WINDOW)
    but_exit.pos_button[1] += but_exit.height * 5

    but_return = Button('', BLACK, WHITE, IMAGES, 'close_button.png', FONT, WINDOW)
    but_return.pos_button = (HEIGHT - (but_return.height + 40), 20)

    while is_running:
        clock.tick(FPS)
        population += 1
        looper += SPEED

        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    is_running = False
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_SPACE:
                            if not is_menu:
                                is_pause = not is_pause
                        case pg.K_ESCAPE:
                            is_menu = not is_menu
                        case pg.K_r:
                            if not is_menu:
                                cells[1:-1, 1:-1] = np.random.randint(0, 2, (RESOLUTION[0] - 2, RESOLUTION[1] - 2),
                                                                      dtype="byte")
                        case pg.K_DELETE:
                            if not is_menu:
                                cells = np.zeros(RESOLUTION, dtype="byte")
                                is_edge = False
                        case pg.K_x:
                            is_edge = not is_edge
                            cells = clear_edges(cells, is_edge)

        pressed = pg.mouse.get_pressed()
        pos = pg.mouse.get_pos()
        if pressed and not is_menu:
            pos_size = tuple(map(lambda x: math.floor(x / SIZE), pos))
            if pressed[0]:
                cells[pos_size] = 1
            elif pressed[2]:
                cells[pos_size] = 0
            pg.display.update()
        elif pressed and is_menu:
            if pressed[0]:
                if but_exit.update(*pos):
                    is_running = False
                elif but_return.update(*pos):
                    is_menu = False

        if is_menu:
            menu(WINDOW, but_exit, but_return)
        else:
            draw_cells(cells)

        if not (is_pause or is_menu) and looper >= FPS:
            looper = 0
            cells = cells_update(cells, RESOLUTION, RULES, ORDER)

        pg.display.update()


if __name__ == '__main__':
    pg.init()
    pg.display.set_caption(f"Game Of Life <{TITLE}>")

    WINDOW: Surface | SurfaceType = pg.display.set_mode((HEIGHT, WIDTH), pg.NOFRAME)
    FONT = pg.font.SysFont(*FONTnSIZE)
    main()


time.sleep(0.1)
sys.exit(0)
