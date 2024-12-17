import math
import random

import pygame as pg

from Components.Camera import Camera
from Components.Component import Component, Transform
from Components.NetworkComponent import NetworkComponent, NetworkManager, Rpc, SendTo
from Components.NetworkTransform import NetworkTransform
from Components.Spritestacks import SpriteStacks
from Components.TileMapIsometricRender import TileMapIsometricRenderer
from Geometry import Vec2

from Game import Game
from UserComponents.SlowCamera import SlowCamera
from scheduler import Scheduler

MAX_SPEED = 400.0  # 400.0
ACCELERATION = 100.0
DECELERATION = 40.0


class SpaceShip(NetworkComponent):  # NetworkComponent Component
    player_model: str
    models: dict[str, tuple[pg.Surface, tuple[int, int]]]

    player: 'SpaceShip'
    player_name: str

    spawned_ships: list[tuple[str, int, int]] = []

    def __init__(self, identifier: int, owner: int):
        super().__init__(identifier, owner)

        self.speed = MAX_SPEED / 2
        if NetworkManager.instance.id == owner:
            SpaceShip.player = self
            self.loop = self.player_loop

    @Rpc(SendTo.ALL, require_owner=False)
    @staticmethod
    def instantiate(player_model: str, owner: int, identifier: int):
        print(f"Instantiating player: {owner} with model: {player_model} and identifier: {identifier}")
        if (player_model, owner, identifier) in SpaceShip.spawned_ships:
            print("Ja esta")
            return
        SpaceShip.spawned_ships.append((player_model, owner, identifier))
        game = Game.instance

        ship = game.CreateItem()
        ship.AddComponent(SpaceShip(identifier, owner))
        ship.AddComponent(SpriteStacks(*SpaceShip.models[player_model], 1))
        ship.AddComponent(NetworkTransform(identifier, owner, sync_angle=True))

        ship.transform.x = (-SlowCamera.word_border_size.x / 2) + random.random() * SlowCamera.word_border_size.x
        ship.transform.y = (-SlowCamera.word_border_size.y / 2) + random.random() * SlowCamera.word_border_size.y

        print(f"Instantiated player: {owner} with model: {player_model} and identifier: {identifier}")

    @staticmethod
    def instantiate_all(client_id: int):
        def d():
            print("instantiate_all:", client_id)
            for ship in SpaceShip.spawned_ships:
                NetworkManager.instance.network_server.send(
                    ("Rpc", ("instantiate", None, ship)), client_id
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

        self.transform.position += Vec2.from_angle(self.transform.angle - math.pi / 2) * (
                self.speed * self.game.delta_time)

        # print(self.speed)
