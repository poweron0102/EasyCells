from Components.Component import Component
from scheduler import Scheduler


class Drawable(Component):
    def draw(self, cam_x: float, cam_y: float, scale: float):
        pass

    def on_destroy(self):
        Camera.instance.to_draw.remove(self)


class Camera(Component):
    instance: 'Camera'
    size: tuple[float, float]

    def __init__(self, scale_with: int = 0):
        Camera.instance = self
        self.scale_with = scale_with
        self.to_draw: list[Drawable] = []
        Scheduler.instance.add(0, self.reset_scale)

    def reset_scale(self):
        self.size = self.game.screen.get_size()

    def loop(self):
        self.to_draw.sort(key=lambda drawable: -drawable.transform.z)

        position = self.transform.ToGlobal()
        cam_x = position.x - self.game.screen.get_width() / 2
        cam_y = position.y - self.game.screen.get_height() / 2

        # Correct to camera size
        scale = self.game.screen.get_size()[self.scale_with] / self.size[self.scale_with]

        for drawable in self.to_draw:
            drawable.draw(cam_x, cam_y, scale)
