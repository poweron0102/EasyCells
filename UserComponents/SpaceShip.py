import dataclasses
import math
import random
import sys

import pygame as pg

from EasyCells import Scheduler, Vec2, Game, Tick
from EasyCells.Components import SpriteStacks, Camera
from EasyCells.Components.Sprite import SimpleSprite
from EasyCells.NetworkComponents import NetworkComponent, NetworkVariable, NetworkTransform, Rpc, SendTo, NetworkManager
from EasyCells.PhysicsComponents import Collider, RectCollider
from EasyCells.UiComponents import Button, UiAlignment
from UserComponents.Life import Life
from UserComponents.Shot import Shot
from UserComponents.SlowCamera import SlowCamera


@dataclasses.dataclass
class SpaceShipConfig:
    max_speed: float
    acceleration: float
    deceleration: float
    shot_cooldown: float
    dano: float
    life: int


MODELS_CONFIGS: dict[str, SpaceShipConfig] = {
    "CamoStellarJet.vox": SpaceShipConfig(max_speed=1100.0, acceleration=90.0, deceleration=70.0, shot_cooldown=0.8, dano=150.0, life=12),
    "DualStriker.vox": SpaceShipConfig(max_speed=850.0, acceleration=60.0, deceleration=45.0, shot_cooldown=0.3, dano=100.0, life=20),
    "InfraredFurtive.vox": SpaceShipConfig(max_speed=1000.0, acceleration=100.0, deceleration=80.0, shot_cooldown=1.2, dano=120.0, life=10),
    "MeteorSlicer.vox": SpaceShipConfig(max_speed=700.0, acceleration=50.0, deceleration=40.0, shot_cooldown=0.6, dano=180.0, life=17),
    "MicroRecon.vox": SpaceShipConfig(max_speed=1200.0, acceleration=120.0, deceleration=100.0, shot_cooldown=2.0, dano=40.0, life=2),
    "RedFighter.vox": SpaceShipConfig(max_speed=950.0, acceleration=75.0, deceleration=55.0, shot_cooldown=0.4, dano=140.0, life=15),
    "Transtellar.vox": SpaceShipConfig(max_speed=600.0, acceleration=40.0, deceleration=30.0, shot_cooldown=1.0, dano=200.0, life=25),
    "UltravioletIntruder.vox": SpaceShipConfig(max_speed=1000.0, acceleration=110.0, deceleration=90.0, shot_cooldown=0.9, dano=110.0, life=11),
    "Warship.vox": SpaceShipConfig(max_speed=500.0, acceleration=20.0, deceleration=15.0, shot_cooldown=0.2, dano=240.0, life=40)
}

pg.mixer.init()

# Carregamento dos sons (pode ser feito uma vez globalmente)
_destruct_sound = pg.mixer.Sound('Assets/Audio/destruct.wav')


class SpaceShip(NetworkComponent):  # NetworkComponent Component
    player_model: str
    models: dict[str, tuple[pg.Surface, tuple[int, int]]]
    models_configs: dict[str, SpaceShipConfig] = MODELS_CONFIGS
    ships_by_identifier: dict[int, 'SpaceShip'] = {}

    player: 'SpaceShip'
    player_name: str

    mini_map_camera: Camera

    spawned_ships: list[tuple[str, str, int, int]] = []

    def __init__(self, identifier: int, owner: int, collider: Collider, config: SpaceShipConfig):
        super().__init__(identifier, owner)

        self.max_life = config.life
        self.life = NetworkVariable(self.max_life, identifier, owner)
        self.shot_cooldown = Tick(config.shot_cooldown)
        self.collider = collider
        self.config = config
        self.is_dead = False

        self.speed = config.max_speed / 2.0
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

        ship_comp = ship.AddComponent(SpaceShip(identifier, owner, coll, SpaceShip.models_configs[player_model]))
        SpaceShip.ships_by_identifier[identifier] = ship_comp
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

    @Rpc(SendTo.ALL, require_owner=False)
    @staticmethod
    def SpaceShip_destroy(identifier: int):
        print(f"Destroying ship with identifier: {identifier}")
        if identifier in SpaceShip.ships_by_identifier:
            ship = SpaceShip.ships_by_identifier.pop(identifier)
            ship.item.Destroy()
            _destruct_sound.play()
            print(f"Destroyed ship with identifier: {identifier}")
        else:
            print(f"Ship with identifier: {identifier} not found")

    @staticmethod
    def instantiate_all(client_id: int):
        def d():
            print("instantiate_all:", client_id)
            for ship in SpaceShip.spawned_ships:
                NetworkManager.instance.call_rpc_on_client(
                    client_id, SpaceShip.SpaceShip_instantiate, *ship
                )

        Scheduler.instance.add(3, d)

    def player_loop(self):
        if self.is_dead:
            return
        self.speed -= self.config.deceleration * self.game.delta_time if self.speed > self.config.max_speed * 0.4 else -self.config.deceleration * self.game.delta_time
        if pg.key.get_pressed()[pg.K_a]:
            self.transform.angle -= 0.8 * self.game.delta_time
        if pg.key.get_pressed()[pg.K_d]:
            self.transform.angle += 0.8 * self.game.delta_time
        if pg.key.get_pressed()[pg.K_w]:
            self.speed += self.config.acceleration * self.game.delta_time if self.speed < self.config.max_speed else 0.0
        if pg.key.get_pressed()[pg.K_s]:
            self.speed -= self.config.acceleration * self.game.delta_time / 2 if self.speed > 0 else 0.0



        self.transform.position += Vec2.from_angle(self.transform.angle - math.pi / 2) * (
                self.speed * self.game.delta_time)

        # Check if the ship is out of the map
        map_rect = pg.Rect(
            -SlowCamera.word_border_size.x / 2,
            -SlowCamera.word_border_size.y / 2,
            SlowCamera.word_border_size.x,
            SlowCamera.word_border_size.y
        )
        if self.transform.x < map_rect.left:
            self.transform.x += map_rect.width
        if self.transform.x > map_rect.right:
            self.transform.x -= map_rect.width
        if self.transform.y < map_rect.top:
            self.transform.y += map_rect.height
        if self.transform.y > map_rect.bottom:
            self.transform.y -= map_rect.height

        if pg.key.get_pressed()[pg.K_SPACE] and self.shot_cooldown():
            mouse_pos = Camera.get_global_mouse_position()
            Shot.Shot_instantiate(
                random.randint(0, sys.maxsize),
                self.owner,
                (mouse_pos - self.transform.position).normalize(),
                self.transform.position
            )

        for shot in Shot.shots:
            if shot.owner != self.owner:
                if self.collider.check_collision_global(shot.collider):
                    self.life.value -= self.config.dano * self.game.delta_time

        if self.life.value <= 0:
            self.is_dead = True
            SpaceShip.SpaceShip_destroy(self.identifier)
            SpaceShip.SpaceShip_instantiate(
                random.choice(list(SpaceShip.models.keys())),
                SpaceShip.player_name,
                NetworkManager.instance.id,
                random.randint(0, sys.maxsize)
            )

        # print(self.speed)
        # print(self.transform.position)
