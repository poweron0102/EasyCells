from typing import Callable

import pygame as pg
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton

from EasyCells import Vec2
from EasyCells.GuiWrapper.GuiComponent import GuiComponent
from EasyCells.GuiWrapper.GuiManager import GuiManager


class GuiButton(GuiComponent):

    element: UIButton


    def __init__(
            self,
            position: Vec2[float],
            size: Vec2[float],
            text: str,
            on_click: Callable = lambda: None,
            on_hover: Callable = lambda: None,
            object_id: str = None
    ):
        super().__init__()

        self.on_click_func = on_click
        self.on_hover_func = on_hover

        # Create the pygame_gui button
        # Note: relative_rect is relative to the GuiManager's surface, not the screen
        self.__rect = pg.Rect(position.to_tuple, size.to_tuple)

        self.__text = text
        self.__object_id = object_id

    def init(self, manager: GuiManager):
        self.element = UIButton(
            relative_rect=self.__rect,
            text=self.__text,
            manager=manager.ui_manager,
            object_id=self.__object_id,
            tool_tip_text = "Testendodo\n1\n2z\n3\ntestatndo"
        )

        self.manager = manager

        del self.__rect, self.__text, self.__object_id

    def handle_event(self, event: pg.event.Event):
        # Check if the event is a button press for THIS button
        # if event.type == pg.USEREVENT:
        if event.user_type == UI_BUTTON_PRESSED:
            if event.ui_element == self.element:
                self.on_click_func()

    def update(self):
        # Continuous hover check:
        # We ask the ui_manager for the mouse position (which it tracks via the offset events)
        # and check if it is inside our button's rect.
        mouse_pos = self.manager.ui_manager.get_mouse_position()

        # Simple collision check for hover
        if self.element.rect.collidepoint(mouse_pos):
            self.on_hover_func()