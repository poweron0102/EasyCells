import pygame as pg

from Components.Button import Button
from Components.Sprite import Sprite, convert_to_grayscale
from Geometry import Vec2
from UserComponents.Door import Door
from UserComponents.Map import Map
from UserComponents.Medusa import Medusa
from UserComponents.Pushable import Pushable
from UserComponents.TiledObj import TiledObj


class Player(TiledObj):
    sprite: Sprite

    def __init__(self, start_tile: Vec2[int], looking: Vec2[int], moves: int):
        self.position = start_tile
        self.is_moving = False
        self.alive = True
        self.moves = moves
        self.looking = looking

        self.transparent = False
        self.transparent_after_mirror = False

    def init(self):
        self.teleport(self.position)
        self.sprite = self.GetComponent(Sprite)

    def loop(self):
        if pg.key.get_pressed()[pg.K_r]:
            self.game.new_game(self.game.current_level)
        if not self.alive:
            return

        if not self.is_moving:
            if pg.key.get_pressed()[pg.K_a]:
                self.move(Vec2(-1, 0))
                self.sprite.horizontal_flip = True
            elif pg.key.get_pressed()[pg.K_d]:
                self.move(Vec2(1, 0))
                self.sprite.horizontal_flip = False
            elif pg.key.get_pressed()[pg.K_w]:
                self.move(Vec2(0, -1))
            elif pg.key.get_pressed()[pg.K_s]:
                self.move(Vec2(0, 1))

    def move(self, direction: Vec2[int]):
        self.looking = direction
        new_pos = self.position + direction
        if Map.instance.is_solid(new_pos):
            self.update_state()
            return

        next_obj = TiledObj.AllObjs.get(new_pos.to_tuple, None)
        if next_obj is not None:
            if isinstance(next_obj, Pushable):
                if not next_obj.push(direction):
                    self.update_state()
                    return
            elif isinstance(next_obj, Door):
                if not next_obj.is_open:
                    self.update_state()
                    return
                self.game.new_game(next_obj.pass_level)
            else:
                self.update_state()
                return

        self.moves -= 1
        self.is_moving = True
        self.game.scheduler.add_generator(self.rotate(new_pos.x - self.position.x))
        self.game.scheduler.add_generator(self.slow_move(new_pos, self.update_state))

    def petrify(self):
        sprite = self.GetComponent(Sprite)
        for i in range(10):
            sprite.image = convert_to_grayscale(sprite.image, i / 10)
            yield 0.1

    def update_state(self):
        if Medusa.is_looking_to_medusa(self.position, self.looking):
            self.game.scheduler.add_generator(self.petrify())
            self.death()
        elif self.moves <= 0:
            self.death()

        Medusa.update_state()

    def death(self):
        self.alive = False
        dead = self.item.CreateChild()
        dead.AddComponent(Button(
            Vec2(0, -18),
            "You died",
            base_panel=pg.image.load("Assets/UI/Panel/panel-018.png"),
            hover_panel=pg.image.load("Assets/UI/Border/panel-border-018.png"),
            on_click=lambda: self.game.new_game(self.game.current_level),
            screen_space=False
        ))
        dead.transform.scale = 0.3



