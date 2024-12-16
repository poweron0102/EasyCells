import math

import pygame as pg

from Components.Camera import Camera
from Components.Component import Component, Transform
from Components.NetworkComponent import NetworkComponent
from Components.Spritestacks import SpriteStacks
from Components.TileMapIsometricRender import TileMapIsometricRenderer
from Geometry import Vec2

MAX_SPEED = 400.0
ACCELERATION = 100.0
DECELERATION = 40.0


class SpaceShip(Component):  # NetworkComponent Component
    player_model: str
    models: dict[str, tuple[pg.Surface, tuple[int, int]]]

    player: 'SpaceShip'

    def __init__(self, identifier: int, owner: int):
        # super().__init__(identifier, owner)

        self.speed = MAX_SPEED / 2
        SpaceShip.player = self

    def loop(self):
        self.speed -= DECELERATION * self.game.delta_time if self.speed > MAX_SPEED * 0.4 else -DECELERATION * self.game.delta_time
        if pg.key.get_pressed()[pg.K_a]:
            self.transform.angle -= 0.8 * self.game.delta_time
        if pg.key.get_pressed()[pg.K_d]:
            self.transform.angle += 0.8 * self.game.delta_time
        if pg.key.get_pressed()[pg.K_w]:
            self.speed += ACCELERATION * self.game.delta_time if self.speed < MAX_SPEED else 0.0
        if pg.key.get_pressed()[pg.K_s]:
            self.speed -= ACCELERATION * self.game.delta_time / 2 if self.speed > 0 else 0.0

        self.transform.position += Vec2.from_angle(self.transform.angle - math.pi / 2) * (
                    self.speed * self.game.delta_time)

        # print(self.speed)
