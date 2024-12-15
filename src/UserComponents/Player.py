import math

import pygame as pg

from Components.Camera import Camera
from Components.Component import Component, Transform
from Components.TileMapIsometricRender import TileMapIsometricRenderer
from Geometry import Vec2


class Player(Component):
    def __init__(self, tile_render: TileMapIsometricRenderer):
        self.tile_render = tile_render

        self.tz = 0
        self.arrow = False

    def loop(self):
        direction = Vec2(0, 0)
        if pg.key.get_pressed()[pg.K_a]:
            direction.x -= 1
        if pg.key.get_pressed()[pg.K_d]:
            direction.x += 1
        if pg.key.get_pressed()[pg.K_w]:
            direction.y -= 1
        if pg.key.get_pressed()[pg.K_s]:
            direction.y += 1

        # if pg.key.get_pressed()[pg.K_q]:
        #     self.transform.angle -= 0.4 * self.game.delta_time
        # if pg.key.get_pressed()[pg.K_e]:
        #     self.transform.angle += 0.4 * self.game.delta_time

        self.transform.angle = (Transform.Global.position - Camera.get_global_mouse_position()).to_angle - math.pi / 2

        if direction != Vec2(0, 0):
            self.transform.position += direction.normalize() * (100 * self.game.delta_time)

        if pg.key.get_pressed()[pg.K_UP] and not self.arrow:
            self.tz += 1
            self.arrow = True
            print(self.tz)
        if pg.key.get_pressed()[pg.K_DOWN] and not self.arrow:
            self.tz -= 1
            self.arrow = True
            print(self.tz)

        self.transform.z = self.tile_render.get_draw_order(
            *self.tile_render.get_tile_word_position(*self.transform.position.to_tuple, self.tz),
            self.tz
        )

        if pg.key.get_pressed()[pg.K_SPACE] and not self.arrow:
            print(self.transform.position.to_tuple + (self.transform.z,))
            print(f"Player in tile: ",
                  self.tile_render.get_tile_word_position(*self.transform.position.to_tuple, self.tz),
                  "layer: ", self.tz
                  )
            self.arrow = True

        if not pg.key.get_pressed()[pg.K_UP] and not pg.key.get_pressed()[pg.K_DOWN] and not pg.key.get_pressed()[pg.K_SPACE]:
            self.arrow = False






