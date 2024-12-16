import os

import pygame as pg

from Components.Camera import Camera
from Components.Component import Item
from Components.Sprite import Sprite
from Components.Spritestacks import voxel2img, SpriteStacks
from Geometry import Vec2
from UiComponents.Button import Button
from UiComponents.UiComponent import panel_maker, UiAlignment
from UserComponents.SpaceShip import SpaceShip
from main import Game

ships: Item
ships_sprite_stacks: list[SpriteStacks] = []


def init(game: Game):
    global ships

    game.CreateItem().AddComponent(Camera())

    base_size = 300

    base_panel = panel_maker(Vec2(base_size, base_size), pg.image.load("Assets/Ui/Panel/panel-000.png"))
    hover_panel = panel_maker(Vec2(base_size, base_size), pg.image.load("Assets/Ui/Panel/panel-001.png"))

    ships = game.CreateItem()
    ships.transform.x = -game.screen.get_width() // 2 + base_size // 2 + 25

    models: dict[str, tuple[pg.Surface, tuple[int, int]]] = {}
    for i, file in enumerate(sorted(os.listdir("Assets/SpaceShips"))):
        ship = ships.CreateChild()
        ship.AddComponent(Sprite(base_panel))
        ship.transform.position = Vec2(i * (base_size + 25), 0)

        ship_img, size = voxel2img(f"Assets/SpaceShips/{file}")
        models[file] = ship_img, size
        ship_sprite_stacks = ship.CreateChild().AddComponent(SpriteStacks(ship_img, size, 1))

        ship_sprite_stacks.transform.scale = base_size / max(ship_sprite_stacks.image.get_size())
        ships_sprite_stacks.append(ship_sprite_stacks)

        def click(string: str):
            print(string)

            def _click():
                print(string)
                SpaceShip.player_model = string
                game.new_game("space_game")

            return _click

        button = ship.CreateChild()
        button.AddComponent(Button(
            Vec2(0, int(base_size / 2) + 60),
            file.split(".")[0],
            base_panel,
            font_size=22,
            hover_panel=hover_panel,
            on_click=click(file),
            alignment=UiAlignment.GAME_SPACE
        ))

    SpaceShip.models = models


def loop(game: Game):
    if pg.key.get_pressed()[pg.K_d]:
        ships.transform.x -= 180 * game.delta_time
    if pg.key.get_pressed()[pg.K_a]:
        ships.transform.x += 180 * game.delta_time

    for ship in ships_sprite_stacks:
        ship.transform.angle += 0.4 * game.delta_time
