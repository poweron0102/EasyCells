import os

import pygame as pg

from EasyCells.Components import Camera, Sprite, Item, SpriteStacks
from EasyCells.NetworkComponents import NetworkManager
from EasyCells.UiComponents import Button, TextInput, UiAlignment, panel_maker
from EasyCells import Game, Vec2
from pygame import MOUSEWHEEL

from UserComponents.SpaceShip import SpaceShip

import Levels.space_game

ships: Item
ships_sprite_stacks: list[SpriteStacks] = []
ship_selected: bool = False


def init(game: Game):
    global ships

    game.CreateItem().AddComponent(Camera())

    base_size = 300

    base_panel = panel_maker(Vec2(base_size, base_size), pg.image.load("Assets/Ui/Panel/panel-000.png"))
    hover_panel = panel_maker(Vec2(base_size, base_size), pg.image.load("Assets/Ui/Panel/panel-001.png"))

    ships = game.CreateItem()
    ships.transform.x = -game.screen.get_width() // 2 + base_size // 2 + 25

    models: dict[str, tuple[pg.Surface, tuple[int, int]]] = {}
    i = 0
    for file in sorted(os.listdir("Assets/SpaceShips")):
        if not file.endswith(".vox"):
            continue

        ship = ships.CreateChild()
        ship.AddComponent(Sprite(base_panel))
        ship.transform.position = Vec2(i * (base_size + 25), 0)

        if f"Assets/SpaceShips/{file[:-4]}.png" in os.listdir("Assets/SpaceShips"):
            ship_img = pg.image.load(f"Assets/SpaceShips/{file[:-4]}.png").convert_alpha()
            size = ship_img.get_size()
        else:
            ship_img, size = SpriteStacks.voxel2img(f"Assets/SpaceShips/{file}")
            pg.image.save(ship_img, f"Assets/SpaceShips/{file[:-4]}.png")
        models[file] = ship_img, size
        ship_sprite_stacks = ship.CreateChild().AddComponent(SpriteStacks(ship_img, size, 1))

        ship_sprite_stacks.transform.scale = base_size / max(ship_sprite_stacks.image.get_size())
        ships_sprite_stacks.append(ship_sprite_stacks)

        def click(string: str):
            print(string)

            def _click():
                print(string)
                global ship_selected
                ship_selected = True
                SpaceShip.player_model = string

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

        i += 1

    SpaceShip.models = models

    # Network -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    ip_text_box = game.CreateItem().AddComponent(
        TextInput(
            Vec2(-350, -225),
            "localhost",
            pg.image.load("Assets/Ui/Panel/panel-007.png"),
            size=Vec2(350, 50),
            font_size=25,
            active_panel=pg.image.load("Assets/Ui/Panel/panel-008.png"),
            alignment=UiAlignment.CENTER
        )
    )

    port_text_box = game.CreateItem().AddComponent(
        TextInput(
            Vec2(-50, -225),
            "5000",
            pg.image.load("Assets/Ui/Panel/panel-007.png"),
            active_panel=pg.image.load("Assets/Ui/Panel/panel-008.png"),
            alignment=UiAlignment.CENTER
        )
    )

    name_text_box = game.CreateItem().AddComponent(
        TextInput(
            Vec2(175, -225),
            "Name",
            pg.image.load("Assets/Ui/Panel/panel-007.png"),
            active_panel=pg.image.load("Assets/Ui/Panel/panel-008.png"),
            alignment=UiAlignment.CENTER
        )
    )

    def start_server():
        if not ship_selected:
            print("Please select a ship")
            return
        print("Starting server")
        SpaceShip.player_name = name_text_box.text if name_text_box.text != "" else "Player"
        game.scheduler.add(1, lambda: game.new_game(Levels.space_game))
        game.CreateItem().AddComponent(
            NetworkManager(
                ip_text_box.text.strip() if ip_text_box.text != "" else "localhost",
                int(port_text_box.text) if port_text_box.text != "" else 5000,
                True,
                # lambda x: game.scheduler.add(1, lambda: game.new_game('space_game'))
            )
        )

    server_btn = game.CreateItem()
    server_btn.AddComponent(Button(
        Vec2(335, -250),
        "Start server",
        pg.image.load("Assets/Ui/Panel/panel-000.png"),
        on_click=start_server,
        hover_panel=pg.image.load("Assets/Ui/Panel/panel-001.png"),
        alignment=UiAlignment.CENTER,
        font_size=18,
    ))

    def start_client():
        if not ship_selected:
            print("Please select a ship")
            return
        print("Starting client")
        SpaceShip.player_name = name_text_box.text if name_text_box.text != "" else "Player"
        # game.scheduler.add(1, lambda: game.new_game('space_game'))
        game.CreateItem().AddComponent(
            NetworkManager(
                ip_text_box.text if ip_text_box.text != "" else "localhost",
                int(port_text_box.text) if port_text_box.text != "" else 5000,
                False,
                connect_callback=lambda x: game.scheduler.add(1, lambda: game.new_game(Levels.space_game))
            )
        )

    client_btn = game.CreateItem()
    client_btn.AddComponent(Button(
        Vec2(335, -200),
        "Start client",
        pg.image.load("Assets/Ui/Panel/panel-000.png"),
        on_click=start_client,
        hover_panel=pg.image.load("Assets/Ui/Panel/panel-001.png"),
        alignment=UiAlignment.CENTER,
        font_size=18,
    ))


def loop(game: Game):
    if pg.key.get_pressed()[pg.K_d]:
        ships.transform.x -= 180 * game.delta_time
    if pg.key.get_pressed()[pg.K_a]:
        ships.transform.x += 180 * game.delta_time

    for evt in game.events:
        if evt.type == MOUSEWHEEL:
            if evt.y != 0:
                ships.transform.x += 1000 * game.delta_time * evt.y

    for ship in ships_sprite_stacks:
        ship.transform.angle += 0.4 * game.delta_time
