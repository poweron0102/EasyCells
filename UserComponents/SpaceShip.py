import math
import random
import sys

import pygame as pg
from EasyCells import Scheduler, Vec2, Game, Tick
from EasyCells.Components import SpriteStacks, Camera
from EasyCells.Components.Sprite import SimpleSprite
from EasyCells.NetworkComponents import NetworkComponent, NetworkVariable, NetworkTransform, Rpc, SendTo, NetworkManager
from EasyCells.PhysicsComponents import Collider, RectCollider
from EasyCells.UiComponents import Button, UiAlignment, UiComponent

from UserComponents.Life import Life
from UserComponents.Shot import Shot
from UserComponents.SlowCamera import SlowCamera

MAX_SPEED = 400.0  # 400.0
ACCELERATION = 100.0
DECELERATION = 40.0
SHOT_COOLDOWN = 0.5


class SpaceShip(NetworkComponent):  # NetworkComponent Component
    player_model: str
    models: dict[str, tuple[pg.Surface, tuple[int, int]]]

    player: 'SpaceShip'
    player_name: str

    mini_map_camera: Camera

    spawned_ships: list[tuple[str, str, int, int]] = []

    def __init__(self, identifier: int, owner: int, collider: Collider):
        super().__init__(identifier, owner)

        self.max_life = 100
        self.life = NetworkVariable(self.max_life, identifier, owner)
        self.shot_cooldown = Tick(SHOT_COOLDOWN)
        self.collider = collider

        self.speed = MAX_SPEED / 2
        if NetworkManager.instance.id == owner:
            SpaceShip.player = self
            self.loop = self.player_loop

    @Rpc(SendTo.ALL, require_owner=False)
    @staticmethod
    def SpaceShip_instantiate(player_model: str, player_name: str, owner: int, identifier: int):
        print(f"Instantiating player: {owner} with model: {player_model} and identifier: {identifier}")
        if (player_model, player_name, owner, identifier) in SpaceShip.spawned_ships:
            print("Já esta")
            return
        SpaceShip.spawned_ships.append((player_model, player_name, owner, identifier))
        game: Game = Game.instance()

        ship = game.CreateItem()
        ship.transform.z = -1

        img, size = SpaceShip.models[player_model]
        coll = ship.AddComponent(RectCollider(pg.Rect(0, 0, size[0], size[1]), debug=False))

        ship_comp = ship.AddComponent(SpaceShip(identifier, owner, coll))
        ship_sprite = ship.AddComponent(SpriteStacks(img, size, 1))
        ship.AddComponent(NetworkTransform(identifier, owner, sync_angle=True))

        ship.transform.x = (-SlowCamera.word_border_size.x / 2) + random.random() * SlowCamera.word_border_size.x
        ship.transform.y = (-SlowCamera.word_border_size.y / 2) + random.random() * SlowCamera.word_border_size.y

        life = ship.CreateChild()
        life.AddComponent(Life(ship_comp))

        name = ship.CreateChild()
        base: pg.Surface = pg.Surface((32, 32), pg.SRCALPHA)
        name.AddComponent(Button(
            Vec2(0, 45),
            player_name,
            base,
            font_color=pg.Color("Cyan") if owner == NetworkManager.instance.id else pg.Color("Red"),
            font_size=16,
            alignment=UiAlignment.GAME_SPACE
        ))

        ship_radar_point = ship.CreateChild()
        point = pg.Surface((7, 7), pg.SRCALPHA)
        pg.draw.circle(
            point,
            pg.Color("Red") if owner != NetworkManager.instance.id else pg.Color("Cyan"),
            (3, 3),
            3,
            5
        )
        point = ship_radar_point.AddComponent(SimpleSprite(point))
        point.add_camera(SpaceShip.mini_map_camera)
        point.remove_main_camera()

        print(f"Instantiated player: {owner} with model: {player_model} and identifier: {identifier}")

    @staticmethod
    def instantiate_all(client_id: int):
        def d():
            print("instantiate_all:", client_id)
            for ship in SpaceShip.spawned_ships:
                NetworkComponent.CallRpc_on_client_id(
                    "SpaceShip_instantiate", None, client_id, *ship
                )

        Scheduler.instance.add(3, d)

    def player_loop(self):
        self.speed -= DECELERATION * self.game.delta_time if self.speed > MAX_SPEED * 0.4 else -DECELERATION * self.game.delta_time
        if pg.key.get_pressed()[pg.K_a]:
            self.transform.angle -= 0.8 * self.game.delta_time
        if pg.key.get_pressed()[pg.K_d]:
            self.transform.angle += 0.8 * self.game.delta_time
        if pg.key.get_pressed()[pg.K_w]:
            self.speed += ACCELERATION * self.game.delta_time if self.speed < MAX_SPEED else 0.0
        if pg.key.get_pressed()[pg.K_s]:
            self.speed -= ACCELERATION * self.game.delta_time / 2 if self.speed > 0 else 0.0

        if self.life.value <= 0:
            self.speed = 0

        self.transform.position += Vec2.from_angle(self.transform.angle - math.pi / 2) * (
                self.speed * self.game.delta_time)

        if pg.key.get_pressed()[pg.K_SPACE] and self.shot_cooldown():
            Shot.Shot_instantiate(
                random.randint(0, sys.maxsize),
                self.owner,
                Vec2.from_angle(self.transform.angle - math.pi / 2),
                self.transform.position
            )

        for shot in Shot.shots:
            if shot.owner != self.owner:
                if self.collider.check_collision_global(shot.collider):
                    self.life.value -= 10 * self.game.delta_time

        # print(self.speed)
        # print(self.transform.position)
