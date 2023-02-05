import os

import pygame
from pygame.surface import Surface, SurfaceType


class Button:
    def __init__(
            self, text_load: str | int, color: tuple[int, int, int], ignore: tuple[int, int, int],
            path_image: str, image: str, font: pygame.font.Font, screen: Surface | SurfaceType,
            pos: None | list[int, int] = None
    ):
        self.font = font
        self.color = color
        self.button = pygame.image.load(os.path.join(path_image, image))
        self.button.set_colorkey(ignore)
        self.res_image = (self.button.get_width(), self.button.get_height())
        self.surf = pygame.Surface(self.res_image, pygame.SRCALPHA, 32).convert_alpha()
        self.surf.blit(self.button, (0, 0))
        self.text = self.font.render(str(text_load), True, self.color)
        self.width = self.surf.get_width()
        self.height = self.surf.get_height()
        self.pos_text: tuple[int, int] = (
            self.button.get_width() // 2 - self.text.get_width() // 2,
            self.button.get_height() // 2 - self.text.get_height() // 2
        )
        self.surf.blit(self.text, self.pos_text)
        if pos is None:
            self.pos_button: list[int, int] = [
                screen.get_width() // 2 - self.width // 2,
                screen.get_height() // 2 - self.height // 2
            ]
        else:
            self.pos_button: list[int, int] = pos

    def update_text(self, text_load: str) -> Surface | SurfaceType:
        self.text = self.font.render(str(text_load), True, self.color)
        return self.text

    def draw(self, screen, text_load: None | str = None):
        if text_load is not None:
            self.surf.blit(self.update_text(text_load), self.pos_text)
        screen.blit(self.surf, tuple(self.pos_button))

    def update(self, x, y):
        return self.pos_button[0] <= x <= self.pos_button[0] + self.width and \
               self.pos_button[1] <= y <= self.pos_button[1] + self.height
