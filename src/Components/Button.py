from typing import Callable

import pygame as pg

from Components.Camera import Drawable, Camera
from Components.Component import Transform
from Geometry import Vec2

pg.font.init()


def panel_maker(size: Vec2[int], base_panel: pg.Surface) -> pg.Surface:
    pieces_size = (base_panel.get_width() // 3, base_panel.get_height() // 3)
    pieces = [
        [
            base_panel.subsurface(
                (x * pieces_size[0], y * pieces_size[1], pieces_size[0], pieces_size[1])
            )
            for x in range(3)
        ]
        for y in range(3)
    ]

    # size = first multiple of pieces_size that is bigger than size
    size = Vec2(
        (size.x // pieces_size[0] + 1) * pieces_size[0],
        (size.y // pieces_size[1] + 1) * pieces_size[1]
    )

    panel = pg.Surface(size.to_tuple, pg.SRCALPHA)
    # panel = pg.Surface(size.to_tuple)

    num_of_pieces = (size.x // pieces_size[0], size.y // pieces_size[1])
    for y in range(1, num_of_pieces[1] - 1):
        for x in range(1, num_of_pieces[0] - 1):
            panel.blit(pieces[1][1], (x * pieces_size[0], y * pieces_size[1]))

    for x in range(1, num_of_pieces[0] - 1):
        panel.blit(pieces[0][1], (x * pieces_size[0], 0))
        panel.blit(pieces[2][1], (x * pieces_size[0], (num_of_pieces[1] - 1) * pieces_size[1]))

    for y in range(1, num_of_pieces[1] - 1):
        panel.blit(pieces[1][0], (0, y * pieces_size[1]))
        panel.blit(pieces[1][2], ((num_of_pieces[0] - 1) * pieces_size[0], y * pieces_size[1]))

    panel.blit(pieces[0][0], (0, 0))
    panel.blit(pieces[2][0], (0, (num_of_pieces[1] - 1) * pieces_size[1]))
    panel.blit(pieces[0][2], ((num_of_pieces[0] - 1) * pieces_size[0], 0))
    panel.blit(pieces[2][2], ((num_of_pieces[0] - 1) * pieces_size[0], (num_of_pieces[1] - 1) * pieces_size[1]))

    return panel


class Button(Drawable):
    _draw_on_screen_space = True

    @property
    def draw_on_screen_space(self):
        return self._draw_on_screen_space

    @draw_on_screen_space.setter
    def draw_on_screen_space(self, value: bool):
        self._draw_on_screen_space = value
        self.draw = self.draw_screen_space if value else self.draw_world_space

    def __init__(
            self,
            position: Vec2[float],
            text: str,
            base_panel: pg.Surface,
            font_size: int = 32,
            font_color: pg.Color = pg.Color("Black"),
            z: int = -101,
            hover_panel: pg.Surface = None,
            on_click: Callable = None,
            on_hover: Callable = None,
            font: str = None,
            screen_space: bool = True
    ):
        self.word_position = Transform()
        self.is_clicked = False

        font = pg.font.Font(f"Assets/{font}", font_size) if font is not None else pg.font.Font(None, font_size)
        text_surface = font.render(text, True, font_color)

        self.base_image = panel_maker(
            Vec2(text_surface.get_width() + font_size, text_surface.get_height() + font_size), base_panel
        )

        self.base_image.blit(
            text_surface,
            (
                self.base_image.get_width() / 2 - text_surface.get_width() / 2,
                self.base_image.get_height() / 2 - text_surface.get_height() / 2
            )
        )
        if hover_panel is None:
            self.hover_image = self.base_image
        else:
            self.hover_image = panel_maker(
                Vec2(text_surface.get_width() + font_size, text_surface.get_height() + font_size), hover_panel
            )
            self.hover_image.blit(
                text_surface,
                (
                    self.hover_image.get_width() / 2 - text_surface.get_width() / 2,
                    self.hover_image.get_height() / 2 - text_surface.get_height() / 2
                )
            )

        self.image = self.base_image

        self.position = position
        self.z = z

        self.on_click = on_click if on_click is not None else lambda: None
        self.on_hover = on_hover if on_hover is not None else lambda: None

        self.draw_on_screen_space = screen_space

    def init(self):
        super().init()
        self.transform.z = self.z
        self.transform.position = self.position
        del self.position
        del self.z

    def draw_screen_space(self, cam_x: float, cam_y: float, scale: float):
        self.game.screen.blit(
            self.image,
            (
                self.transform.position.x - self.image.get_width() // 2,
                self.transform.position.y - self.image.get_height() // 2
            )
        )

    def draw_world_space(self, cam_x: float, cam_y: float, scale: float):
        position = self.word_position * scale
        position.scale *= scale

        # Get size and apply nearest neighbor scaling
        original_size = self.image.get_size()
        new_size = (int(original_size[0] * position.scale), int(original_size[1] * position.scale))
        image = pg.transform.scale(self.image, new_size)

        # Draw base_image
        size = image.get_size()
        self.game.screen.blit(
            image,
            (
                position.x - cam_x - size[0] // 2,
                position.y - cam_y - size[1] // 2
            )
        )

    def loop(self):
        self.word_position = Transform.Global

        if not pg.mouse.get_pressed()[0]:
            self.is_clicked = False

        if self.is_mouse_over():
            self.on_hover()
            self.image = self.hover_image
            if pg.mouse.get_pressed()[0] and not self.is_clicked:
                self.is_clicked = True
                self.on_click()
        else:
            self.image = self.base_image

    def is_mouse_over(self) -> bool:
        if self.draw_on_screen_space:
            return self.base_image.get_rect(
                topleft=(
                    self.transform.position.x - self.base_image.get_width() // 2,
                    self.transform.position.y - self.base_image.get_height() // 2
                )
            ).collidepoint(pg.mouse.get_pos())
        else:
            mouse = Camera.get_global_mouse_position()
            size = Vec2(*self.image.get_size()) * self.transform.scale
            top_left = Transform.Global.position - Vec2(size.x // 2, size.y // 2)

            return pg.Rect(top_left.to_tuple, size.to_tuple).collidepoint(mouse.to_tuple)
