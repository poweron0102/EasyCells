import math

import pygame as pg

from Components.Camera import Camera
from Components.Camera import Drawable
from Components.Component import Transform


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

        Camera.instance.to_draw.append(self)

    def loop(self):
        self.word_position = Transform.Global

    def draw(self, cam_x: float, cam_y: float, scale: float):
        position = self.word_position * scale
        position.scale *= scale

        # Crop image without lose alpha channel
        image = pg.Surface(self.size, pg.SRCALPHA)
        image.blit(
            self.image,
            (0, 0),
            (self.index * self.size[0], 0, self.size[0], self.size[1])
        )

        # Flip image
        if self.horizontal_flip or self.vertical_flip:
            image = pg.transform.flip(image, self.horizontal_flip, self.vertical_flip)

        # Get size and apply nearest neighbor scaling
        original_size = image.get_size()
        new_size = (int(original_size[0] * position.scale), int(original_size[1] * position.scale))
        image = pg.transform.scale(image, new_size)

        # Rotate image
        image = pg.transform.rotate(image, -math.degrees(position.angle))

        # Draw image
        size = image.get_size()
        self.game.screen.blit(
            image,
            (
                position.x - cam_x - size[0] // 2,
                position.y - cam_y - size[1] // 2
            )
        )
