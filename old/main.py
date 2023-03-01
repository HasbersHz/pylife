# -*- coding: utf-8 -*-
r"""E:\Apps\Python\python.exe -m pyinstaller --add-data "config.py;." -w E:/life/main.py"""
from __future__ import annotations

import ctypes
import math
import sys
import time
import timeit

from pygame.surface import Surface, SurfaceType

from func import *
from menu import Button

from OpenGL.GL import *
from OpenGL.GLU import *


def draw_cells(cells: Mapping, x: int | None = None, y: int | None = None, w: int | None = None, h: int | None = None):
    if x is None:
        x = 0
    if y is None:
        y = 0
    if w is None:
        w = len(cells)
    if h is None:
        h = len(cells[0])
    for i in np.arange(x, w):
        for j in np.arange(y, h):
            cell = cells[i, j]
            if cell == 1:
                pg.draw.rect(surf, ALIVE, [i * SIZE, j * SIZE, SIZE, SIZE])
            elif cell == 0:
                pg.draw.rect(surf, DEAD, [i * SIZE, j * SIZE, SIZE, SIZE])
            else:
                pg.draw.rect(surf, ERROR_COLOR, [i * SIZE, j * SIZE, SIZE, SIZE])


def menu(wind, but_exit, but_return):
    wind.fill(COLOR_INTERFACE)
    but_exit.draw(wind)
    but_return.draw(wind)


def main():
    cell_type = np.ubyte

    cells: np.ndarray = np.random.randint(0, 2, RESOLUTION, dtype=cell_type)

    # for i in (False, True, False):
    #     cells = clear_edges(cells, i)

    clock: pg.time.Clock = pg.time.Clock()

    all_sprites: pg.sprite.Group = pg.sprite.Group()

    population = 0
    is_running: bool = True
    # work: dict[str: bool, str: bool] = {"p": False, "menu": False}
    is_pause = False
    is_menu = False
    is_edge = False
    looper: int = 0

    camera = Camera(WIDTH, HEIGHT)

    # Buttons
    but_exit = Button('Exit', BLACK, WHITE, IMAGES, 'button1.png', FONT, WINDOW)
    but_exit.pos_button[1] += but_exit.height * 5

    but_return = Button('R', BLACK, WHITE, IMAGES, 'close_button.png', FONT, WINDOW)
    but_return.pos_button = (HEIGHT - (but_return.height + 40), 20)

    for i, line in enumerate(cells):
        for j, _ in enumerate(line):
            Cell(all_sprites, (i, j), BLACK)

    while is_running:
        clock.tick(FPS)
        population += 1
        looper += SPEED

        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    if not is_menu:
                        is_pause = not is_pause
                elif event.key == pg.K_ESCAPE:
                    is_menu = not is_menu
                elif event.key == pg.K_r:
                    if not is_menu:
                        cells = np.random.randint(0, 2, (RESOLUTION[0], RESOLUTION[1]), dtype=cell_type)
                elif event.key == pg.K_DELETE:
                    if not is_menu:
                        cells = np.zeros(RESOLUTION, dtype=cell_type)
                        is_edge = False
                if event.key == pg.K_x:
                    # is_edge = not is_edge
                    # cells = clear_edges(cells, is_edge)
                    ...

        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # camera.update(...)

        pressed = pg.mouse.get_pressed()
        pos = pg.mouse.get_pos()
        if pressed and not is_menu:
            pos_size = tuple(map(lambda x: math.floor(x / SIZE), pos))
            if pressed[0]:
                cells[pos_size] = 1
            elif pressed[2]:
                cells[pos_size] = 0
        elif pressed and is_menu:
            if pressed[0]:
                if but_exit.update(*pos):
                    is_running = False
                elif but_return.update(*pos):
                    is_menu = False

        if is_menu:
            menu(WINDOW, but_exit, but_return)
        else:
            all_sprites.update(cells)
            all_sprites.draw(surf)
            WINDOW.blit(surf, (0, 0))

        if DEBUG:
            WINDOW.blit(FONT.render(str(int(clock.get_fps())), True, GREEN), (0, 0))

        if not (is_pause or is_menu) and looper >= FPS:
            looper = 0
            cells = cells_update(cells, RESOLUTION, RULES, ORDER)
            WINDOW.blit(surf, (0, 0))

        pg.display.flip()


if __name__ == '__main__':
    pg.init()
    pg.display.set_caption(f"Game Of Life <{TITLE}>")
    # pg.display.gl_set_attribute(pg.GL_ALPHA_SIZE, 8)
    # pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
    # pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
    WINDOW: Surface | SurfaceType = pg.display.set_mode((HEIGHT, WIDTH), pg.NOFRAME | pg.DOUBLEBUF)  # | pg.OPENGL
    surf = pg.Surface((HEIGHT, WIDTH))
    FONT = pg.font.SysFont(*FONTnSIZE)
    main()


time.sleep(0.1)
sys.exit(0)
