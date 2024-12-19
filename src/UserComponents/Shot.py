import pygame as pg

from Components.NetworkComponent import NetworkComponent, SendTo, Rpc
from Components.Sprite import Sprite
from Game import Game
from Geometry import Vec2


class Shot(NetworkComponent):

    def __init__(self, identifier: int, owner: int, direction: Vec2[float], start: Vec2[float]):
        super().__init__(identifier, owner)

        self.direction = direction
        self.start = start

        self.speed = 1000.0

    def init(self):
        self.transform.position = self.start
        self.transform.angle = self.direction.to_angle
        self.game.scheduler.add(5, self.item.Destroy)

    def loop(self):
        self.transform.position += self.direction * (self.speed * self.game.delta_time)

    @Rpc(SendTo.ALL, require_owner=False)
    @staticmethod
    def Shot_instantiate(identifier: int, direction: Vec2[float], start: Vec2[float]):
        game = Game.instance

        shot = game.CreateItem()
        shot.AddComponent(Shot(identifier, 0, direction, start))

        img = pg.Surface((8, 8))
        img.fill((255, 0, 0))
        shot.AddComponent(Sprite(img))
