import sys
from importlib import import_module
from types import ModuleType
from typing import Callable

import pygame as pg
from pygame.event import Event

from Components.Component import Item
from NewGame import NewGame


class Game:
    instance: 'Game'
    level: ModuleType
    events: list[Event]

    _game_name: str

    @property
    def game_name(self) -> str:
        return self._game_name

    @game_name.setter
    def game_name(self, value: str):
        self._game_name = value
        if not self.show_fps:
            pg.display.set_caption(value)

    def __init__(
            self,
            start_level: str,
            game_name: str,
            show_fps: bool = False,
            screen: pg.Surface | None = None,
    ):
        Game.instance = self
        # imports: -=-=-=-=-
        from scheduler import Scheduler
        # imports: -=-=-=-=-

        if screen is None:
            self.screen: pg.Surface = pg.display.set_mode((800, 600), pg.RESIZABLE)  # (1280, 720)
        else:
            self.screen: pg.Surface = screen

        Game.events = pg.event.get()

        self.show_fps = show_fps
        self.game_name = game_name

        self.clock = pg.time.Clock()
        self.time = pg.time.get_ticks()
        self.last_time = pg.time.get_ticks()
        self.delta_time = 0
        self.run_time = 0
        self.scheduler = Scheduler(self)
        self.item_list: list[Item] = []
        self.to_init: list[Callable] = []
        self.current_level = start_level
        self.new_game(self.current_level, supress=True)
        # pg.mouse.set_visible

    def new_game(self, level: str, supress=False):
        self.level = import_module(f".{level}", "Levels")
        self.current_level = level
        self.run_time = 0

        for item in list(self.item_list):
            if item.destroy_on_load:
                item.Destroy()

        self.scheduler.clear()
        self.level.init(self)

        self.update()

        if not supress:
            raise NewGame

    def CreateItem(self) -> 'Item':
        return Item(self)

    def update(self):
        Game.events = pg.event.get()
        for event in Game.events:
            if event.type == pg.QUIT:  # or (event.type == pg.KEYDOWN and event.key == pg.k_ESCAPE):
                pg.quit()
                sys.exit()

        pg.display.flip()
        self.screen.fill((30, 30, 30))  # Cinza
        self.clock.tick(1000)
        self.last_time = self.time
        self.time = pg.time.get_ticks()
        self.delta_time = (self.time - self.last_time) / 1000.0
        self.run_time += self.delta_time

        if self.show_fps:
            pg.display.set_caption(f'{self.game_name}   FPS: {self.clock.get_fps():.0f}')

    def run(self):
        while True:
            self.update()
            try:
                for function in self.to_init:
                    function()
                self.to_init.clear()

                for item in list(self.item_list):
                    item.update()

                self.level.loop(self)

                self.scheduler.update()
            except NewGame:
                pass

    def run_once(self):
        self.update()
        try:
            for function in self.to_init:
                function()
            self.to_init.clear()

            for item in list(self.item_list):
                item.update()

            self.level.loop(self)

            self.scheduler.update()
        except NewGame:
            pass
