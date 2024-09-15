import sys
from importlib import import_module
from types import ModuleType

import pygame as pg

from Components.Component import Item, Transform

"""
Dependencies:
    - pygame
    - numpy
    - numba
    - scipy
"""


class NewGame(Exception):
    """Exception raised for handle new games."""
    pass


def check_events():
    for event in pg.event.get():
        if event.type == pg.QUIT:  # or (event.type == pg.KEYDOWN and event.key == pg.k_ESCAPE):
            pg.quit()
            sys.exit()


class Game:
    level: ModuleType

    def __init__(self, screen: pg.Surface | None = None):
        # imports: -=-=-=-=-
        from scheduler import Scheduler
        # imports: -=-=-=-=-

        if screen is None:
            self.screen: pg.Surface = pg.display.set_mode((1280, 720), pg.RESIZABLE)

        else:
            self.screen: pg.Surface = screen

        self.clock = pg.time.Clock()
        self.time = pg.time.get_ticks()
        self.lest_time = pg.time.get_ticks()
        self.delta_time = 0
        self.run_time = 0
        self.scheduler = Scheduler(self)
        self.item_list: list[Item] = []
        self.new_game("level0", supress=True)
        # pg.mouse.set_visible

    def new_game(self, level: str, supress=False):
        self.level = import_module(f".{level}", "Levels")
        self.run_time = 0

        for item in self.item_list:
            if item.destroy_on_load:
                item.Destroy()
                self.item_list.remove(item)

        self.level.init(self)

        if not supress:
            raise NewGame

    def CreateItem(self) -> 'Item':
        return Item(self)

    def update(self):
        pg.display.flip()
        self.screen.fill((30, 30, 30))  # Cinza
        self.clock.tick(1000)
        self.lest_time = self.time
        self.time = pg.time.get_ticks()
        self.delta_time = (self.time - self.lest_time) / 1000.0
        self.run_time += self.delta_time

        self.scheduler.update()

        for item in self.item_list:
            item.update()

        pg.display.set_caption(f'Game Name   FPS: {self.clock.get_fps():.0f}')

    def run(self):
        while True:
            check_events()
            self.update()
            try:
                self.level.loop(self)
            except NewGame:
                pass

    def run_once(self):
        self.update()
        try:
            self.level.loop(self)
        except NewGame:
            pass


if __name__ == '__main__':
    GAME = Game()
    GAME.run()
