import pygame as pg

from Components.Camera import Camera
from Components.NetworkComponent import NetworkManager
from Geometry import Vec2
from UiComponents.Button import Button

from UiComponents.TextInput import TextInput
from UiComponents.UiComponent import UiAlignment
from main import Game


def init(game: Game):
    game.CreateItem().AddComponent(Camera())

    ip_text_box = game.CreateItem().AddComponent(
        TextInput(
            Vec2(0, 150),
            "localhost",
            pg.image.load("Assets/Ui/Panel/panel-007.png"),
            active_panel=pg.image.load("Assets/Ui/Panel/panel-008.png"),
            alignment=UiAlignment.CENTER
        )
    )

    port_text_box = game.CreateItem().AddComponent(
        TextInput(
            Vec2(0, 50),
            "5000",
            pg.image.load("Assets/Ui/Panel/panel-007.png"),
            active_panel=pg.image.load("Assets/Ui/Panel/panel-008.png"),
            alignment=UiAlignment.CENTER
        )
    )

    def start_server():
        print("Starting server")
        game.CreateItem().AddComponent(
            NetworkManager(
                ip_text_box.text if ip_text_box.text != "" else "localhost",
                int(port_text_box.text) if port_text_box.text != "" else 5000,
                True,
                6,
                lambda x: game.scheduler.add(1, lambda: game.new_game('net_2'))
            )
        )

    server_btn = game.CreateItem()
    server_btn.AddComponent(Button(
        Vec2(0, -50),
        "Start server",
        pg.image.load("Assets/Ui/Panel/panel-000.png"),
        on_click=start_server,
        hover_panel=pg.image.load("Assets/Ui/Panel/panel-001.png"),
        alignment=UiAlignment.CENTER
    ))

    def start_client():
        print("Starting client")
        game.CreateItem().AddComponent(
            NetworkManager(
                ip_text_box.text if ip_text_box.text != "" else "localhost",
                int(port_text_box.text) if port_text_box.text != "" else 5000,
                False,
                6,
                lambda x: game.scheduler.add(1, lambda: game.new_game('net_2'))  # 'net_2' 'net_pong2'
            )
        )

    client_btn = game.CreateItem()
    client_btn.AddComponent(Button(
        Vec2(0, -150),
        "Start client",
        pg.image.load("Assets/Ui/Panel/panel-000.png"),
        on_click=start_client,
        hover_panel=pg.image.load("Assets/Ui/Panel/panel-001.png"),
        alignment=UiAlignment.CENTER
    ))


def loop(game: Game):
    pass
