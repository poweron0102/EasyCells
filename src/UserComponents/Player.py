import pygame as pg
from Components.Component import Component


class Player(Component):

    def loop(self):
        if pg.key.get_pressed()[pg.K_a]:
            self.transform.x -= 100 * self.game.delta_time
        elif pg.key.get_pressed()[pg.K_d]:
            self.transform.x += 100 * self.game.delta_time
        elif pg.key.get_pressed()[pg.K_w]:
            self.transform.y -= 100 * self.game.delta_time
        elif pg.key.get_pressed()[pg.K_s]:
            self.transform.y += 100 * self.game.delta_time





