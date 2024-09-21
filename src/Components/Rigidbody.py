from typing import Callable

from Components.Collider import Collider
from Components.Component import Component
from Geometry import Vec2


class Rigidbody(Component):
    collider: Collider

    def __init__(self, gravity: float = 10, mask: int = 1):
        """
        mask: int = Should collide with collider that have this mask
        """
        self.gravity = gravity
        self.velocity: Vec2[float] = Vec2(0, 0)
        self.acceleration: Vec2[float] = Vec2(0, 0)

        self.last_position: Vec2[float] = Vec2(0, 0)
        self.on_collision: list[Callable[[Collider], None]] = []
        self.mask = mask

    def init(self):
        self.collider = self.GetComponent(Collider)

        self.last_position.x = self.transform.x
        self.last_position.y = self.transform.y

    def loop(self):
        self.acceleration.y += self.gravity * self.game.delta_time

        self.velocity.x += self.acceleration.x * self.game.delta_time
        self.velocity.y += self.acceleration.y * self.game.delta_time

        self.acceleration.x = 0
        self.acceleration.y = 0

        collided = set()

        self.collider.word_position.x += self.velocity.x * self.game.delta_time
        self.transform.x += self.velocity.x * self.game.delta_time
        if self.collider is not None:
            for other_collider in Collider.colliders:
                if self.mask & other_collider.mask == 0:
                    continue

                if self.collider.check_collision_global(other_collider):
                    self.transform.x = self.last_position.x
                    self.velocity.x = 0

                    if len(self.on_collision) == 0:
                        break
                    if other_collider not in collided:
                        collided.add(other_collider)
                        for callback in self.on_collision:
                            callback(other_collider)

        self.collider.word_position.y += self.velocity.y * self.game.delta_time
        self.transform.y += self.velocity.y * self.game.delta_time
        if self.collider is not None:
            for other_collider in Collider.colliders:
                if other_collider == self.collider:
                    continue

                if self.collider.check_collision_global(other_collider):
                    self.transform.y = self.last_position.y
                    self.velocity.y = 0

                    if len(self.on_collision) == 0:
                        break
                    if other_collider not in collided:
                        collided.add(other_collider)
                        for callback in self.on_collision:
                            callback(other_collider)

        self.last_position.x = self.transform.x
        self.last_position.y = self.transform.y
