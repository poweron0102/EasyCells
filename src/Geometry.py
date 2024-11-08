import math
from dataclasses import dataclass


@dataclass
class Vec2[T]:
    x: T
    y: T

    def normalize(self) -> 'Vec2[T]':
        return Vec2(self.x / (self.x ** 2 + self.y ** 2) ** 0.5, self.y / (self.x ** 2 + self.y ** 2) ** 0.5)

    def reflect(self, normal: 'Vec2[T]') -> 'Vec2[T]':
        return self - normal * 2 * self.dot(normal)

    def dot(self, other: 'Vec2[T]') -> T:
        return self.x * other.x + self.y * other.y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: T):
        return Vec2(self.x * other, self.y * other)

    def __div__(self, other: T):
        return Vec2(self.x / other, self.y / other)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    @property
    def to_tuple(self):
        return self.x, self.y

    @property
    def to_angle(self):
        return math.atan2(self.y, self.x)

    @staticmethod
    def from_tuple(t: tuple[T, T]) -> 'Vec2[T]':
        return Vec2(t[0], t[1])

    @staticmethod
    def zero() -> 'Vec2[int]':
        return Vec2(0, 0)

    @staticmethod
    def from_angle(angle: float) -> 'Vec2[float]':
        return Vec2(math.cos(angle), math.sin(angle))

    def rotate(self, angle: T) -> 'Vec2[T]':
        return Vec2(
            self.x * math.cos(angle) - self.y * math.sin(angle),
            self.x * math.sin(angle) + self.y * math.cos(angle)
        )
