import pygame as pg

from EasyCells import Vec2, Game
from EasyCells.Components import Sprite
from EasyCells.NetworkComponents import Rpc, SendTo, NetworkComponent
from EasyCells.PhysicsComponents import RectCollider, Collider

pg.mixer.init()
_shot_sound = pg.mixer.Sound('Assets/Audio/shot.wav')
class Shot(NetworkComponent):
    shots: set['Shot'] = set()

    def __init__(self, identifier: int, owner: int, direction: Vec2[float], start: Vec2[float], collider: Collider):
        super().__init__(identifier, owner)

        self.direction = direction
        self.start = start
        self.collider = collider

        self.speed = 600.0

        Shot.shots.add(self)

    def init(self):
        self.transform.position = self.start
        self.transform.angle = self.direction.to_angle
        self.game.scheduler.add(5, self.item.Destroy)

    def on_destroy(self):
        Shot.shots.remove(self)
        self.on_destroy = lambda: None

    def loop(self):
        self.transform.position += self.direction * (self.speed * self.game.delta_time)

    @Rpc(SendTo.ALL, require_owner=False)
    @staticmethod
    def Shot_instantiate(identifier: int, owner: int,  direction: Vec2[float], start: Vec2[float]):
        game = Game.instance()

        shot = game.CreateItem()

        coll = shot.AddComponent(RectCollider(pg.Rect(0, 0, 8, 8), debug=False, mask=owner))

        shot.AddComponent(Shot(identifier, owner, direction, start, coll))
        _shot_sound.play()

        img = pg.Surface((8, 8))
        img.fill((255, 255, 255))
        shot.AddComponent(Sprite(img))


