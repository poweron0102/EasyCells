import pygame as pg

from Components.Animator import Animator, Animation
from Components.Camera import Camera
from Components.Collider import Collider
from Components.Component import Item
from Components.FMODAudioManager import FMODAudioManager
from Components.RectCollider import RectCollider
from Components.Rigidbody import Rigidbody, Vec2
from Components.Sprite import Sprite
from Components.TileMap import TileMapRenderer, TileMap
from Components.TileMapCollider import TileMapCollider
from main import Game

player: Item
player_rg: Rigidbody
caixa: Item
camera: Camera
tile_map: Item
player_collider: Collider
tile_map_collider: Collider


def init(game: Game):
    global player
    global player_rg
    global caixa
    global camera
    global tile_map
    global player_collider
    global tile_map_collider

    # game.CreateItem().AddComponent(FMODAudioManager(["Master.bank", "Master.strings.bank"], "Music"))

    player = game.CreateItem()
    if True:
        camera = player.AddComponent(Camera())
    else:
        camera = game.CreateItem().AddComponent(Camera())

    player.AddComponent(Sprite("player32.png", (32, 32)))
    player.AddComponent(
        Animator(
            {
                "idle": Animation(100, [18]),
                "run": Animation(0.1, list(range(0, 7))),
                "death": Animation(0.2, list(range(8, 13)), "idle"),
                "rising": Animation(0.2, list(range(13, 18)), "boll"),
                "boll": Animation(0.2, [17]),
            },
            "run"
        )
    )
    player_collider = player.AddComponent(RectCollider(pg.Rect(0, 0, 32, 32), debug=True, mask=0))
    player_rg = player.AddComponent(Rigidbody(gravity=0, mask=1))
    player_rg.on_collision.append(lambda c: print("Collided with", c))
    player.transform.z = -1

    caixa = game.CreateItem()
    caixa.AddComponent(Sprite("player24.png", (24, 24))).index = 1
    caixa.transform.x = 150
    caixa.transform.y = 100
    caixa_filho = caixa.CreateChild()
    caixa_filho.AddComponent(Sprite("player24.png", (24, 24))).index = 1
    caixa_filho.transform.x = 50

    game.CreateItem().AddComponent(Sprite("player24.png", (24, 24))).index = 1

    tile_map = game.CreateItem()
    tile_map.AddComponent(TileMap([
        [5, 4, 4, 4, 3],
        [11, 1, 1, 1, 9],
        [12, 12, 12, 12, 12],
        [12, 12, 12, 12, 12],
        [17, 7, 7, 7, 15]
    ]))
    tile_map.AddComponent(TileMapRenderer("RockSet.png", 32))
    tile_map_collider = tile_map.AddComponent(TileMapCollider({1, 3, 4, 5, 7, 9, 11, 15, 17}, 32, debug=True))

    caixa.AddChild(tile_map)


def loop(game: Game):
    # print("Is player colliding with tile map? ", player_collider.check_collision_global(tile_map_collider))

    # test ray_cast
    player_word = player.GetComponent(Collider).word_position
    origem = Vec2(player_word.x, player_word.y)
    direction = Vec2(1, 1)
    inf = Collider.ray_cast(origem, direction, 64, 1)
    Camera.instance.draw_debug_ray(origem, direction.to_angle, 64, pg.Color("red"))
    if inf:
        col, point, normal = inf
        print("Ray cast:", col, point, normal)
        Camera.instance.draw_debug_line(point, point + normal * 50, pg.Color("blue"))

    if pg.mouse.get_pressed()[0]:
        Camera.instance.draw_debug_line(origem, Camera.get_global_mouse_position(), pg.Color("green"), 4)


    # player controls
    player_velocity: Vec2[float] = Vec2(0, 0)
    if pg.key.get_pressed()[pg.K_w]:
        player_velocity.y = -1
    if pg.key.get_pressed()[pg.K_s]:
        player_velocity.y = 1
    if pg.key.get_pressed()[pg.K_a]:
        player_velocity.x = -1
    if pg.key.get_pressed()[pg.K_d]:
        player_velocity.x = 1

    player.GetComponent(Sprite).horizontal_flip = player_velocity.x < 0
    if player_velocity != Vec2(0, 0):
        player_rg.velocity = player_velocity.normalize() * 100
    else:
        player_rg.velocity = player_velocity

    # player animations
    if pg.key.get_pressed()[pg.K_1]:
        player.GetComponent(Animator).current_animation = "idle"
    if pg.key.get_pressed()[pg.K_2]:
        player.GetComponent(Animator).current_animation = "run"
    if pg.key.get_pressed()[pg.K_3]:
        player.GetComponent(Animator).current_animation = "death"
    if pg.key.get_pressed()[pg.K_4]:
        player.GetComponent(Animator).current_animation = "rising"

    if pg.key.get_pressed()[pg.K_5]:
        FMODAudioManager.instance.is_playing = not FMODAudioManager.instance.is_playing
    if pg.key.get_pressed()[pg.K_6]:
        game.new_game("level1")

    to_rotate = caixa
    if pg.key.get_pressed()[pg.K_q]:
        to_rotate.transform.angle -= 0.8 * game.delta_time
    if pg.key.get_pressed()[pg.K_e]:
        to_rotate.transform.angle += 0.8 * game.delta_time

    if pg.key.get_pressed()[pg.K_UP]:
        to_rotate.transform.scale += 10 * game.delta_time
    if pg.key.get_pressed()[pg.K_DOWN]:
        to_rotate.transform.scale -= 10 * game.delta_time

    # camera zoom
    if pg.key.get_pressed()[pg.K_z]:
        camera.size = (camera.size[0] + 400 * game.delta_time, camera.size[1] + 100 * game.delta_time)
    if pg.key.get_pressed()[pg.K_x]:
        camera.size = (camera.size[0] - 400 * game.delta_time, camera.size[1] - 100 * game.delta_time)
    if pg.key.get_pressed()[pg.K_r]:
        camera.init()
