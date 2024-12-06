import pygame as pg

from Components.Camera import Camera
from Geometry import Vec2
from UiComponents.Button import Button
from UiComponents.TextInput import TextInput
from UiComponents.UiComponent import UiComponent, UiAlignment
from main import Game


def init(game: Game):
    game.CreateItem().AddComponent(Camera())

    ui_element = game.CreateItem()
    ui_element.AddComponent(UiComponent(
        Vec2(100, 100),
        pg.image.load("Assets/player24.png"),
        alignment=UiAlignment.TOP_LEFT
    ))

    ui_button = game.CreateItem()

    def ir():
        ui_button.transform.y += 10

    ui_button.AddComponent(Button(
        Vec2(0, 0),
        "Button",
        pg.image.load("Assets/Ui/Panel/panel-000.png"),
        on_click=ir,
        on_hover=lambda: print("Button hovered"),
        hover_panel=pg.image.load("Assets/Ui/Panel/panel-001.png"),
        alignment=UiAlignment.CENTER
    ))

    ui_text_input = game.CreateItem()
    ui_text_input.AddComponent(TextInput(
        Vec2(0, 80),
        "Text Input",
        pg.image.load("Assets/Ui/Panel/panel-007.png"),
        size=Vec2(200, 50),
        on_active=lambda: print("Text Input active"),
        on_write=lambda x: print("Text Input written:", x),
        on_enter=lambda x: print("Text Input entered:", x),
        on_inactive=lambda: print("Text Input inactive"),
        active_panel=pg.image.load("Assets/Ui/Panel/panel-008.png"),
        alignment=UiAlignment.CENTER
    ))


def loop(game: Game):
    pass
