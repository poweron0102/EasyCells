import pygame as pg

from Components.Component import Component
from Geometry import Vec2


class Player(Component):

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

        if direction != Vec2(0, 0):
            self.transform.position += direction.normalize() * (100 * self.game.delta_time)






