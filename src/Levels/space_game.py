import random
import random
import sys

import pygame as pg

from Components.Camera import Camera
from Components.NetworkComponent import NetworkManager
from Components.Sprite import SimpleSprite
from Game import Game
from Geometry import Vec2
from UserComponents.SlowCamera import SlowCamera
from UserComponents.SpaceShip import SpaceShip


def init(game: Game):
    camera = game.CreateItem()
    camera.AddComponent(Camera())
    camera.AddComponent(SlowCamera(300))

    background = game.CreateItem()
    img = pg.image.load(f"Assets/487516.jpg").convert()
    scale_factor = 2
    SlowCamera.word_border_size = Vec2(img.get_width() * scale_factor, img.get_height() * scale_factor)
    background.AddComponent(SimpleSprite(
        pg.transform.scale(img, SlowCamera.word_border_size.to_tuple)
    ))
    background.transform.z = 1

    if NetworkManager.instance.is_server:
        NetworkManager.instance.connect_callbacks.append(SpaceShip.instantiate_all)

    SpaceShip.SpaceShip_instantiate(
        SpaceShip.player_model,
        NetworkManager.instance.id,
        random.randint(0, sys.maxsize)
    )


def loop(game: Game):
    pass
