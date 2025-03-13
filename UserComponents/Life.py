import pygame as pg

from EasyCells import Vec2
from EasyCells.Components import Transform
from EasyCells.UiComponents import UiComponent, UiAlignment

bar_width = 40
bar_height = 6


class Life(UiComponent):

    def __init__(self, ship):
        img = pg.Surface((bar_width, bar_height))
        super().__init__(Vec2(0, 30), img, alignment=UiAlignment.GAME_SPACE)
        self.ship = ship

    def loop(self):
        super().loop()
        self.image = pg.Surface((bar_width, bar_height), pg.SRCALPHA)
        pg.draw.rect(self.image, (0, 255, 0), (0, 0, bar_width * self.ship.life.value / self.ship.max_life, bar_height))
        pg.draw.rect(self.image, (138, 138, 138), (0, 0, bar_width, bar_height), 1)
        self.image = pg.transform.rotate(self.image, -Transform.Global.angle_deg)
