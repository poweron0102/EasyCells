import pygame as pg
import math

from Components.Component import Component, Item
from Geometry import Vec2


def lerp(a: Vec2 | float, b: Vec2 | float, t: float) -> Vec2:
    return a + (b - a) * t


class SlowCamera(Component):
    word_border_size: Vec2[float]

    def __init__(self, speed: float):
        self.target: Item | None = None
        self.speed = speed

    def init(self):
        self.game.scheduler.add_generator(self.follow())

    def follow(self):
        from UserComponents.SpaceShip import SpaceShip

        while not hasattr(SpaceShip, "player"):
            yield

        self.target = SpaceShip.player.item

        word_rect = pg.Rect(
            -SlowCamera.word_border_size.x / 2,
            -SlowCamera.word_border_size.y / 2,
            SlowCamera.word_border_size.x,
            SlowCamera.word_border_size.y
        )

        while True:
            self.transform.position = (
                    self.target.transform.position -
                    Vec2.from_angle(self.target.transform.angle + math.pi / 2) * (SpaceShip.player.speed / 1.5)
            )

            cam_rect = pg.Rect(
                -self.game.screen.get_width() / 2 + self.transform.x,
                -self.game.screen.get_height() / 2 + self.transform.y,
                self.game.screen.get_width(),
                self.game.screen.get_height()
            )
            if cam_rect.left < word_rect.left:
                cam_rect.left = word_rect.left
            if cam_rect.right > word_rect.right:
                cam_rect.right = word_rect.right
            if cam_rect.top < word_rect.top:
                cam_rect.top = word_rect.top
            if cam_rect.bottom > word_rect.bottom:
                cam_rect.bottom = word_rect.bottom

            self.transform.position = Vec2(*cam_rect.center)
            yield
