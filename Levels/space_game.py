import random
import sys

import pygame as pg

from EasyCells import Game, Vec2
from EasyCells.Components import Camera
from EasyCells.Components.Sprite import SimpleSprite
from EasyCells.NetworkComponents import NetworkManager
from EasyCells.UiComponents import UiComponent, UiAlignment
from UserComponents.SlowCamera import SlowCamera
from UserComponents.SpaceShip import SpaceShip

# Configs
scale_factor = 2


def init(game: Game):
    camera = game.CreateItem()
    camera.AddComponent(Camera())
    camera.AddComponent(SlowCamera(300))

    background = game.CreateItem()
    img = pg.image.load(f"Assets/space.jpg").convert()
    SlowCamera.word_border_size = Vec2(img.get_width() * scale_factor, img.get_height() * scale_factor)
    background.AddComponent(SimpleSprite(
        pg.transform.scale(img, SlowCamera.word_border_size.to_tuple)
    ))
    background.transform.z = 1

    if NetworkManager.instance.is_server:
        NetworkManager.instance.connect_callbacks.append(SpaceShip.instantiate_all)

    # UI
    # Mine map
    map_scale = 0.08
    map_size = (img.get_width() * map_scale, img.get_height() * map_scale)
    mine_map = game.CreateItem()
    mine_background = background.AddComponent(SimpleSprite(
        pg.transform.scale(img, map_size)
    ))
    mini_map_suf = pg.Surface(
        map_size,
        pg.SRCALPHA
    )
    SpaceShip.mini_map_camera = game.CreateItem().AddComponent(Camera(
        SlowCamera.word_border_size.to_tuple,
        0,
        mini_map_suf,
        (0, 0, 0, 255)
    ))
    mine_background.add_camera(SpaceShip.mini_map_camera)
    game.scheduler.add(0, mine_background.remove_main_camera)

    mine_map.AddComponent(UiComponent(
        Vec2(map_size[0] / 2 + 10, -(map_size[1] / 2 + 10)),
        mini_map_suf,
        -200,
        UiAlignment.BOTTOM_LEFT
    ))
    # End UI

    SpaceShip.SpaceShip_instantiate(
        SpaceShip.player_model,
        SpaceShip.player_name,
        NetworkManager.instance.id,
        random.randint(0, sys.maxsize)
    )


def loop(game: Game):
    pass
