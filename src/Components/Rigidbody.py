import math
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
        self.size: Vec2[float] = Vec2(0, 0)

        self.on_collision: list[Callable[[Collider], None]] = []
        self.mask = mask
        self.is_ground = False

    def init(self):
        self.collider = self.GetComponent(Collider)
        self.size = Vec2.from_tuple(self.collider.bounding_box().size)

    def loop(self):
        # Apply gravity
        print(self.velocity)
        self.velocity.y += self.gravity * self.item.game.delta_time

        # Apply velocity by transform.angle
        self.velocity = self.velocity.rotate(self.transform.angle)

        self.collider.word_position.x += self.velocity.x * self.item.game.delta_time
        self.collider.word_position.y += self.velocity.y * self.item.game.delta_time

        # Check collision
        for other in Collider.colliders:
            if other.mask & self.mask == 0:
                continue

            if self.collider.check_collision_global(other):
                for callback in self.on_collision:
                    callback(other)

                result = other.ray_cast(
                    self.item.transform.position,
                    self.velocity.normalize(),
                    self.size.y * 0.8
                )

                if result:
                    point, normal = result
                    self.velocity = self.velocity.reflect(normal)
                    self.transform.angle = normal.to_angle + math.pi / 2
                    print(f"Position: {self.transform.position}, Velocity: {self.velocity}")
                    print(f"---> Position: {self.transform.position}")
                    self.is_ground = True
                    self.transform.position += self.velocity
                else:
                    self.is_ground = False

                self.velocity = Vec2(0, 0)
                return  # Exit on collision

        # Don't find any collision
        self.is_ground = False
        self.transform.position += self.velocity
        self.velocity = Vec2(0, 0)







