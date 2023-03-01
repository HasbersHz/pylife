import os
from typing import Dict, Tuple


def tran(*args: int) -> tuple:
    """
    Made purely for convenience
    Use for rules
    :param args: in range
    :return: tuple of range
    """
    return tuple(range(*args))


BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
WHITE = (255, 255, 255)
GREY = (85, 85, 85)
DARK_GREY = (25, 25, 25)


COLORS: list[tuple[int, int, int]] = [
    BLACK,
    RED,
    GREEN,
    BLUE,
    CYAN,
    YELLOW,
    PURPLE,
    WHITE,
    GREY,
    DARK_GREY,
]

HEIGHT = 1920
WIDTH = 1080
SIZE: int = 10
RESOLUTION: tuple[int, int] = (HEIGHT // SIZE, WIDTH // SIZE)
ORDER = 1
CELLS_CORNER = 0
FONTnSIZE = ('Console Font', 30)

DEBUG = True

FPS: int = 120
SPEED: int = FPS

PATH = os.path.dirname(__file__)
IMAGES = os.path.join(PATH, "images")
SAVES = os.path.join(PATH, "saves")

ALL_RULES: list[tuple[str, int, tuple[tuple[int], tuple[int]]]] = [
    ("Original", 0,             ((3,), (2, 3))),
    ("Order 2", 1,              ((6,), (4, 6))),
    ("Day & Night", 2,          ((3, 6, 7, 8), (3, 4, 6, 7, 8))),
    ("Life without Death", 3,   ((3,), tran(9))),
    ("HighLife", 4,             ((3, 6), (2, 3))),
    ("Seeds", 5,                ((2,), ())),
    ("B0", 6,                   ((0,), (0,)))
]

CHOSEN: int = 0
TITLE, _, RULES = ALL_RULES[CHOSEN]
ALIVE: tuple[int, int, int] = WHITE
DEAD: tuple[int, int, int] = BLACK
COLOR_INTERFACE: tuple[int, int, int] = DARK_GREY
ERROR_COLOR: tuple[int, int, int] = RED
CELL_COLORS: dict[int, tuple[int, int, int]] = {
    0: DEAD,
    1: ALIVE
}
