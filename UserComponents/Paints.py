from EasyCells import Vec2
from EasyCells.Components import Camera
from EasyCells.UiComponents import UiComponent, UiAlignment
import pygame as pg



class Paints(UiComponent):
    color: pg.Color | None = None

    colors: list[pg.Color] = [
        pg.Color(255, 0, 255),
        pg.Color(0, 38, 255),
        pg.Color(0, 255, 144),
        pg.Color(255, 0, 0),
        pg.Color(128, 128, 128),
    ]

    def __init__(self, position: Vec2):
        super().__init__(
            position,
            pg.image.load(f"Assets/Tintas.png").convert_alpha(),
            alignment=UiAlignment.CENTER
        )

    # abstract method
    def loop(self):
        super().loop()

        if self.is_mouse_over() and pg.mouse.get_just_pressed()[0]:
            pos = Camera.get_global_mouse_position() - self.transform.position

            if pos.y < 0:
                if pos.x < -38:
                    Paints.color = None
                elif pos.x > 38:
                    Paints.color = Paints.colors[1]
                else:
                    Paints.color = Paints.colors[0]
            else:
                if pos.x < -38:
                    Paints.color = Paints.colors[2]
                elif pos.x > 38:
                    Paints.color = Paints.colors[4]
                else:
                    Paints.color = Paints.colors[3]

            print(Paints.color)


