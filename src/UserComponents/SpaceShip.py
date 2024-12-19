import math
import random
import sys

import pygame as pg

from Components.NetworkComponent import NetworkComponent, NetworkManager, Rpc, SendTo
from Components.NetworkTransform import NetworkTransform
from Components.Spritestacks import SpriteStacks
from Game import Game
from Geometry import Vec2
from UserComponents.Life import Life
from UserComponents.Shot import Shot
from UserComponents.SlowCamera import SlowCamera
from scheduler import Scheduler, Tick

MAX_SPEED = 400.0  # 400.0
ACCELERATION = 100.0
DECELERATION = 40.0
SHOT_COOLDOWN = 0.5


class SpaceShip(NetworkComponent):  # NetworkComponent Component
    player_model: str
    models: dict[str, tuple[pg.Surface, tuple[int, int]]]

    player: 'SpaceShip'
    player_name: str

    spawned_ships: list[tuple[str, int, int]] = []

    def __init__(self, identifier: int, owner: int):
        super().__init__(identifier, owner)

        self.max_life = 100
        self.life = self.max_life
        self.shot_cooldown = Tick(SHOT_COOLDOWN)

        self.speed = MAX_SPEED / 2
        if NetworkManager.instance.id == owner:
            SpaceShip.player = self
            self.loop = self.player_loop

    @Rpc(SendTo.ALL, require_owner=False)
    @staticmethod
    def SpaceShip_instantiate(player_model: str, owner: int, identifier: int):
        print(f"Instantiating player: {owner} with model: {player_model} and identifier: {identifier}")
        if (player_model, owner, identifier) in SpaceShip.spawned_ships:
            print("Já esta")
            return
        SpaceShip.spawned_ships.append((player_model, owner, identifier))
        game = Game.instance

        ship = game.CreateItem()
        ship_comp = ship.AddComponent(SpaceShip(identifier, owner))
        ship.AddComponent(SpriteStacks(*SpaceShip.models[player_model], 1))
        ship.AddComponent(NetworkTransform(identifier, owner, sync_angle=True))

        ship.transform.x = (-SlowCamera.word_border_size.x / 2) + random.random() * SlowCamera.word_border_size.x
        ship.transform.y = (-SlowCamera.word_border_size.y / 2) + random.random() * SlowCamera.word_border_size.y

        life = ship.CreateChild()
        life.AddComponent(Life(ship_comp))

        print(f"Instantiated player: {owner} with model: {player_model} and identifier: {identifier}")

    @staticmethod
    def instantiate_all(client_id: int):
        def d():
            print("instantiate_all:", client_id)
            for ship in SpaceShip.spawned_ships:
                NetworkManager.instance.network_server.send(
                    ("Rpc", ("SpaceShip_instantiate", None, ship)), client_id
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

        if self.life <= 0:
            self.speed = 0

        self.transform.position += Vec2.from_angle(self.transform.angle - math.pi / 2) * (
                self.speed * self.game.delta_time)

        if pg.key.get_pressed()[pg.K_SPACE] and self.shot_cooldown():
            Shot.Shot_instantiate(
                random.randint(0, sys.maxsize),
                Vec2.from_angle(self.transform.angle - math.pi / 2),
                self.transform.position
            )

        # print(self.speed)
