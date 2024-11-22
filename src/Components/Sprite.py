import math

import pygame as pg

from Components.Camera import Drawable
from Components.Component import Transform

import pygame as pg


def convert_to_grayscale(surface: pg.Surface, strength: float = 1) -> pg.Surface:
    # Cria uma nova superfície com o mesmo tamanho e formato
    grayscale_surface = pg.Surface(surface.get_size(), pg.SRCALPHA)

    # Converte para um formato apropriado para píxel access
    surface_locked = surface.copy()

    # Percorre cada pixel da superfície
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            # Obtém a cor do pixel
            r, g, b, a = surface_locked.get_at((x, y))

            # Calcula a tonalidade de cinza usando a média
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)

            # Define a nova cor (tons de cinza) na nova superfície
            grayscale_surface.set_at(
                (x, y),
                (
                    int(r * (1 - strength) + gray * strength),
                    int(g * (1 - strength) + gray * strength),
                    int(b * (1 - strength) + gray * strength),
                    a
                )
            )

    return grayscale_surface


class Sprite(Drawable):
    image: pg.Surface
    index: int = 0
    size: tuple[int, int] = (0, 0)

    def __init__(self, image_path: str, size: tuple[int, int] = None):
        self.image = pg.image.load(f"Assets/{image_path}").convert_alpha()
        self.size = size if size else self.image.get_size()

        self.horizontal_flip = False
        self.vertical_flip = False

        self.word_position = Transform()

    def loop(self):
        self.word_position = Transform.Global

    def draw(self, cam_x: float, cam_y: float, scale: float):
        position = self.word_position * scale
        position.scale *= scale

        # Crop base_image without lose alpha channel
        image = pg.Surface(self.size, pg.SRCALPHA)
        image.blit(
            self.image,
            (0, 0),
            (self.index * self.size[0], 0, self.size[0], self.size[1])
        )

        # Flip base_image
        if self.horizontal_flip or self.vertical_flip:
            image = pg.transform.flip(image, self.horizontal_flip, self.vertical_flip)

        # Get size and apply nearest neighbor scaling
        original_size = image.get_size()
        new_size = (int(original_size[0] * position.scale), int(original_size[1] * position.scale))
        image = pg.transform.scale(image, new_size)

        # Rotate base_image
        image = pg.transform.rotate(image, -math.degrees(position.angle))

        # Draw base_image
        size = image.get_size()
        self.game.screen.blit(
            image,
            (
                position.x - cam_x - size[0] // 2,
                position.y - cam_y - size[1] // 2
            )
        )
