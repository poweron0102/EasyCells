from typing import Any

import pygame as pg
from pygame_gui.core.ui_element import UIElement

#from EasyCells.GuiWrapper.GuiManager import GuiManager


class GuiComponent:
    """
    Base wrapper class for pygame_gui elements to integrate with GuiManager.
    """

    manager: Any
    element: UIElement

    def handle_event(self, event: pg.event.Event):
        """Called by GuiManager when a USEREVENT occurs."""
        pass

    def update(self):
        """Called by GuiManager every frame."""
        pass

    def init(self, manager: "GuiManager"):
        """Called by GuiManager when the component is added to the GuiManager"""
        pass

    def kill(self):
        """Removes the element from pygame_gui and the manager."""
        if self.element:
            self.element.kill()
        if self in self.manager.components:
            self.manager.components.remove(self)


