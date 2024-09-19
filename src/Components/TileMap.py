import math

import pygame as pg

from Components.Camera import Drawable, Camera
from Components.Component import Component, Transform


class TileMap(Component):

    def __init__(self, matrix: list[list[int]]):
        self.matrix = matrix
        self.size = (len(matrix[0]), len(matrix))


class TileMapRenderer(Drawable):
    tile_map: TileMap

    def __init__(self, tile_set: str, tile_size: int):
        self.tile_set = pg.image.load(f"Assets/{tile_set}").convert_alpha()
        self.tile_size = tile_size

        size = self.tile_set.get_size()
        self.word_position = Transform()
        self.matrix_size = (size[0] // tile_size, size[1] // tile_size)
        Camera.instance.to_draw.append(self)

    def init(self):
        self.tile_map = self.GetComponent(TileMap)

    def int2coord(self, value: int) -> tuple[int, int]:
        return value % self.matrix_size[0], value // self.matrix_size[0]

    def coord2int(self, coord: tuple[int, int]) -> int:
        return coord[0] + coord[1] * self.matrix_size[0]

    def get_tile(self, x: int, y: int) -> pg.Surface:
        return self.tile_set.subsurface((x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))

    def loop(self):
        self.word_position = Transform.Global

    def draw(self, cam_x: float, cam_y: float, scale: float):
        position = self.word_position * scale
        position.scale *= scale

        # Create a new surface to draw the tile map
        image = pg.Surface(
            (self.tile_size * self.tile_map.size[0], self.tile_size * self.tile_map.size[1]),
            pg.SRCALPHA
        )

        # Draw the tile map
        for y, row in enumerate(self.tile_map.matrix):
            for x, tile in enumerate(row):
                image.blit(self.get_tile(*self.int2coord(tile)), (x * self.tile_size, y * self.tile_size))

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
