import os

import pygame as pg

from Components.Camera import Camera
from Components.Component import Item
from Components.Sprite import Sprite, SimpleSprite
from Components.Spritestacks import voxel2img, SpriteStacks
from Geometry import Vec2
from UiComponents.Button import Button
from UiComponents.UiComponent import panel_maker, UiAlignment
from UserComponents.SlowCamera import SlowCamera
from UserComponents.SpaceShip import SpaceShip
from main import Game


def init(game: Game):
    camera = game.CreateItem()
    camera.AddComponent(Camera())

    player = game.CreateItem()
    player.AddComponent(SpaceShip(
        0, 0
    ))
    player.AddComponent(SpriteStacks(*SpaceShip.models[SpaceShip.player_model], 1))

    camera.AddComponent(SlowCamera(300, player))
    # player.AddChild(camera)
    # camera.transform.y = -190

    obj1 = game.CreateItem()
    img = pg.image.load(f"Assets/487516.jpg").convert()
    scale_factor = 2
    SlowCamera.word_border_size = Vec2(img.get_width() * scale_factor, img.get_height() * scale_factor)
    obj1.AddComponent(SimpleSprite(
        pg.transform.scale(img, SlowCamera.word_border_size.to_tuple)
    ))
    obj1.transform.z = 1


def loop(game: Game):
    pass
