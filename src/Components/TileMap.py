import pygame as pg

from Components.Camera import Drawable
from Components.Component import Component


class TileMap(Component):

    def __init__(self, matrix: list[list[int]]):
        self.matrix = matrix
        self.size = (len(matrix[0]), len(matrix))

    # abstract method
    def init(self):
        pass

    # abstract method
    def loop(self):
        pass


class TileMapRenderer(Drawable):
    tile_map: TileMap

    def __init__(self, tile_set: str, tile_size: int):
        self.tile_set = pg.image.load(f"Assets/{tile_set}").convert_alpha()
        self.tile_size = tile_size

        size = self.tile_set.get_size()
        self.matrix_size = (size[0] // tile_size, size[1] // tile_size)

    def int2coord(self, value: int) -> tuple[int, int]:
        return value % self.matrix_size[0], value // self.matrix_size[0]

    def coord2int(self, coord: tuple[int, int]) -> int:
        return coord[0] + coord[1] * self.matrix_size[0]

    def get_tile(self, x: int, y: int) -> pg.Surface:
        return self.tile_set.subsurface((x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))

    def loop(self):
        pass

    def draw(self, cam_x: float, cam_y: float, scale: float):
        pass
