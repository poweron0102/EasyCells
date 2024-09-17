import math
from typing import Callable

import pygame as pg

from Components.Component import Component, Transform


class Drawable(Component):

    def init(self):
        Camera.instance.to_draw.append(self)

    def draw(self, cam_x: float, cam_y: float, scale: float):
        pass

    def on_destroy(self):
        Camera.instance.to_draw.remove(self)


class Camera(Component):
    instance: 'Camera'
    size: tuple[float, float]

    def __init__(self, scale_with: int = 0):
        """scale_with[0: width, 1: height]"""

        Camera.instance = self
        self.scale_with = scale_with
        self.to_draw: list[Drawable] = []
        self.debug_draws: list[Callable] = []

    def init(self):
        self.size = self.game.screen.get_size()

    def loop(self):
        self.to_draw.sort(key=lambda drawable: -drawable.transform.z)

        # Correct to camera size
        scale = self.game.screen.get_size()[self.scale_with] / self.size[self.scale_with]

        position = Transform.Global
        cam_x = position.x * scale - self.game.screen.get_width() / 2
        cam_y = position.y * scale - self.game.screen.get_height() / 2

        for drawable in self.to_draw:
            drawable.draw(cam_x, cam_y, scale)

        for function in self.debug_draws:
            function(cam_x, cam_y, scale)

        self.debug_draws.clear()

    @staticmethod
    def draw_debug_line(start: tuple[float, float], end: tuple[float, float], color: pg.Color, width: int = 1):
        """
        This function needs be called on the loop method of a component to work
        It uses locale coordinates from the current loop function of the component
        """
        misc = [start, end, Transform.Global.clone()]

        def draw(cam_x: float, cam_y: float, scale: float):
            start = misc[0]
            end = misc[1]
            position = misc[2] * scale
            position.scale *= scale

            start = position.apply_transform(start)
            end = position.apply_transform(end)

            pg.draw.line(
                Camera.instance.game.screen,
                color,
                start - pg.Vector2(cam_x, cam_y),
                end - pg.Vector2(cam_x, cam_y),
                width
            )

        Camera.instance.debug_draws.append(draw)

    @staticmethod
    def draw_debug_ray(start: tuple[float, float], angle: float, length: float, color: pg.Color, width: int = 1):
        """
        This function needs be called on the loop method of a component to work
        It uses locale coordinates from the current loop function of the component
        """
        Camera.draw_debug_line(
            start,
            (start[0] + length * math.cos(angle), start[1] + length * math.sin(angle)),
            color,
            width
        )

