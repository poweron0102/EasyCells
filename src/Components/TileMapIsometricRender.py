import math
from typing import Callable
import os
from functools import cache

import pygame as pg

from Components.Camera import Drawable, Camera
from Components.Component import Transform, Component
from Geometry import Vec2


class TileMap3D(Component):
    def __init__(self, matrix: list[list[list[int]]]):
        self.matrix = matrix
        self.size: tuple[int, int, int] = (len(matrix[0][0]), len(matrix[0]), len(matrix))

        self.on_tile_change: list[Callable[[int, int, int, int], None]] = []

    def get_tile(self, x: int, y: int, z) -> int:
        return self.matrix[z][y][x]

    def set_tile(self, x: int, y: int, z: int, value: int):
        self.matrix[z][y][x] = value
        for callback in self.on_tile_change:
            callback(x, y, z, value)

    @staticmethod
    def load_from_csv(dir_path: str) -> 'TileMap3D':
        mat: list[list[list[int]]] = []

        for file in sorted(os.listdir(f"Assets/{dir_path}")):
            with open(f"Assets/{dir_path}/{file}") as f:
                mat.append([list(map(int, line.split(","))) for line in f.readlines()])

        for index, mat0 in enumerate(mat):
            mat1: list[list[int]] = [[-1 for _ in range(len(mat0[0]))] for _ in range(len(mat0))]
            for i in range(index, len(mat0) - index):
                for j in range(index, len(mat0[i]) - index):
                    mat1[i][j] = mat0[i-index][j-index]

            mat[index] = mat1

        return TileMap3D(mat)


class TileMapIsometricRenderer(Drawable):
    tile_map: TileMap3D

    def __init__(self, tile_set: str | pg.Surface, tile_size: tuple[int, int]):
        if isinstance(tile_set, str):
            self.tile_set = pg.image.load(f"Assets/{tile_set}").convert_alpha()
        else:
            self.tile_set = tile_set

        self.tile_size: tuple[int, int] = tile_size

        size = self.tile_set.get_size()
        self.word_position = Transform()
        self.matrix_size = (size[0] // tile_size[0], size[1] // tile_size[1])
        Camera.instance.to_draw.append(self)
        self.image = None

    def init(self):
        self.tile_map = self.GetComponent(TileMap3D)
        self.tile_map.on_tile_change.append(
            lambda x, y, z, value: self.update_image()
        )
        self.update_image()

    def int2coord(self, value: int) -> tuple[int, int]:
        return value % self.matrix_size[0], value // self.matrix_size[0]

    def coord2int(self, coord: tuple[int, int]) -> int:
        return coord[0] + coord[1] * self.matrix_size[0]

    @cache
    def get_tile(self, x: int, y: int) -> pg.Surface:
        return self.tile_set.subsurface(
            (x * self.tile_size[0], y * self.tile_size[1], self.tile_size[0], self.tile_size[1])
        )

    def get_tile_word_position(self, pos: Vec2[float]) -> tuple[int, int, int] | None:
        pass  # TODO

    def world_to_isometric(self, x: float, y: float, z: float) -> tuple[int, int]:
        pass  # TODO

    def loop(self):
        self.word_position = Transform.Global

    def update_image(self):
        size = (
            sum(self.tile_map.size) * self.tile_size[0] // 2,
            sum(self.tile_map.size) * self.tile_size[1] // 4 + self.tile_size[1] // 2
        )

        self.image = pg.Surface(
            size,
            pg.SRCALPHA
        )

        hx = self.image.get_size()[0] // 2 - self.tile_size[0] // 2

        for z in range(self.tile_map.size[2]):
            for y in range(self.tile_map.size[1]):
                for x in range(self.tile_map.size[0]):
                    tile = self.tile_map.get_tile(x, y, z)
                    if tile == -1:
                        continue
                    self.image.blit(
                        self.get_tile(*self.int2coord(tile)),
                        (
                            hx + (x - y) * self.tile_size[0] // 2,
                            (x + y) * self.tile_size[1] // 4 - z * self.tile_size[1] // 2
                        )
                    )

    def draw(self, cam_x: float, cam_y: float, scale: float):
        position = self.word_position * scale
        position.scale *= scale

        image = self.image.copy()

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
