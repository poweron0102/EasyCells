import pygame as pg

from Components.Camera import Drawable, Camera
from Components.Component import Component, Transform


class TileMap[T](Component):

    def __init__(self, matrix: list[list[T]]):
        self.matrix = matrix
        self.size = (len(matrix[0]), len(matrix))


class TileMapRenderer(Drawable):
    tile_map: TileMap[int]

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

        for y, row in enumerate(self.tile_map.matrix):
            for x, tile in enumerate(row):
                self.game.screen.blit(
                    pg.transform.scale(
                        self.get_tile(*self.int2coord(tile)),
                        (self.tile_size * position.scale, self.tile_size * position.scale)
                    ),
                    (
                        position.x - cam_x + (x - len(row) / 2) * self.tile_size * position.scale,
                        position.y - cam_y + (y - len(self.tile_map.matrix) / 2) * self.tile_size * position.scale
                    )
                )
