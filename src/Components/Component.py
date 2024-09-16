from typing import Type, Tuple
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Game


class Item:
    """
    Class that represents an item that can have components and children.
    """
    transform: 'Transform'
    parent: 'Item | None'

    game: 'Game'

    def __init__(self, game: 'Game', parent=None):
        self.components: dict[Type, Component] = {}
        self.children: set[Item] = set()
        self.transform = Transform()
        self.parent = parent
        self.game = game
        self.destroy_on_load = True
        if parent:
            parent.AddChild(self)
        else:
            game.item_list.append(self)

    def CreateChild(self) -> 'Item':
        return Item(self.game, self)

    def AddChild(self, item: 'Item') -> None:
        self.children.add(item)
        item.parent = self
        try:
            self.game.item_list.remove(item)
        except ValueError:
            pass

    def AddComponent[T: 'Component'](self, component: T) -> T:
        self.components[component.__class__] = component
        component._inicialize_(self)
        return component

    def Destroy(self):
        self.parent.children.remove(self)
        for child in self.children:
            child.Destroy()
        for component in list(self.components.keys()):
            self.components[component].on_destroy()
        del self

    def update(self):
        if not self.parent:
            Transform.Global = Transform()
        self.transform.SetGlobal()
        for component in list(self.components.keys()):
            try:
                self.components[component].loop()
            except Exception as e:
                from main import NewGame
                if e == KeyboardInterrupt:
                    raise KeyboardInterrupt
                if e == SystemExit:
                    raise SystemExit
                if e == NewGame:
                    raise NewGame
                print(f"Error in {self.components[component]}:\n    {e}")

        for child in self.children:
            child.update()

    def GetComponent[T: Component](self, component: Type[T]) -> T | None:
        try:
            return self.components[component]
        except KeyError:
            if len(self.children) > 0:
                for child in self.children:
                    resp = child.GetComponent(component)
                    if resp:
                        return resp
            return None


class Component:
    item: Item

    # debug: bool = False  # Debug mode

    @property
    def transform(self) -> 'Transform':
        return self.item.transform

    @transform.setter
    def transform(self, value: 'Transform') -> None:
        self.item.transform = value

    @property
    def game(self) -> 'Game':
        return self.item.game

    def _inicialize_(self, item: Item):
        self.item = item
        self.init()

    # abstract method
    def init(self):
        pass

    # abstract method
    def loop(self):
        pass

    # abstract method
    def on_destroy(self):
        pass

    def GetComponent[T: Component](self, component: Type[T]) -> T | None:
        return self.item.GetComponent(component)


class Transform(Component):
    """
    Class that represents a transform with position, rotation and scale.
    """
    Global: 'Transform'

    x: float
    y: float
    z: float

    _scale: float

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value if value > 0.0001 else 0.0001

    _angle: float

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value % (2 * math.pi)

    @property
    def angle_deg(self):
        return math.degrees(self.angle)

    @angle_deg.setter
    def angle_deg(self, value):
        self.angle = math.radians(value)

    def __init__(self, x: float = 0, y: float = 0, z: float = 0, angle: float = 0, scale: float = 1):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.scale = scale

    def __add__(self, other):
        return Transform(self.x + other.x, self.y + other.y, self.z + other.z, self.angle + other.angle, self.scale)

    def __sub__(self, other):
        return Transform(self.x - other.x, self.y - other.y, self.z - other.z, self.angle - other.angle, self.scale)

    def __mul__(self, other: float):
        return Transform(self.x * other, self.y * other, self.z, self.angle, self.scale)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z and self.angle == other.angle and self.scale == other.scale

    def clone(self):
        return Transform(self.x, self.y, self.z, self.angle, self.scale)

    def ToGlobal(self) -> 'Transform':
        # Rotate point by Global.angle
        new_x = self.x * math.cos(Transform.Global.angle) - self.y * math.sin(Transform.Global.angle)
        new_y = self.x * math.sin(Transform.Global.angle) + self.y * math.cos(Transform.Global.angle)

        # Scale point
        new_x *= Transform.Global.scale
        new_y *= Transform.Global.scale

        return Transform(
            new_x + Transform.Global.x,
            new_y + Transform.Global.y,
            self.z + Transform.Global.z,
            self.angle + Transform.Global.angle,
            self.scale * Transform.Global.scale
        )

    def apply_transform(self, point: Tuple[float, float]) -> Tuple[float, float]:
        # Rotate point by self.angle
        new_x = point[0] * math.cos(self.angle) - point[1] * math.sin(self.angle)
        new_y = point[0] * math.sin(self.angle) + point[1] * math.cos(self.angle)

        # Scale point
        new_x *= self.scale
        new_y *= self.scale

        return new_x + self.x, new_y + self.y

    def SetGlobal(self):
        Transform.Global = self.ToGlobal()
