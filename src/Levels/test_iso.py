from random import randint

from Components.Camera import Camera
from Components.Spritestacks import SpriteStacks, voxel2img
from Components.TileMapIsometricRender import TileMapIsometricRenderer, TileMap3D
from UserComponents.Player import Player
from main import Game
from scheduler import Scheduler

iso_map: TileMapIsometricRenderer


def init(game: Game):
    global iso_map

    #img = voxel2img("Assets/chr_knight.vox")  # teapot.vox  chr_knight.vox monu3.vox

    cam = game.CreateItem()
    cam.AddComponent(Camera())

    mapa = game.CreateItem()
    mapa.AddComponent(TileMap3D.load_from_csv("IsoMap2"))
    iso_map = mapa.AddComponent(TileMapIsometricRenderer("iso_tile_export.png", (32, 32)))

    player = game.CreateItem()
    #player.AddComponent(Sprite("player32.png", (32, 32)))
    player.AddComponent(SpriteStacks(*voxel2img("Assets/SpaceShips/DualStriker.vox"), 1))
    player.AddComponent(Player(iso_map))
    player.transform.scale = 5

    def ale():
        x = randint(0, 14)
        y = randint(0, 14)
        mapa.GetComponent(TileMap3D).set_tile(x, y, 1, 64)
        Scheduler.instance.add(0.4, ale)

    # Scheduler.instance.add(0.4, ale)


def loop(game: Game):
    pass
    # cam_pos = Camera.get_global_mouse_position()
    # print(iso_map.get_tile_word_position(cam_pos))
