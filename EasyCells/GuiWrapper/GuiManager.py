from pygame_gui import UIManager, UI_BUTTON_PRESSED
import pygame as pg

from EasyCells import Vec2, Game
from EasyCells.UiComponents import UiComponent, UiAlignment


class GuiManager(UiComponent):
    def __init__(
            self,
            position: Vec2[float],
            size: Vec2[float],
            theme_path: str = None,
            z: int = -101,
            alignment: UiAlignment = UiAlignment.TOP_LEFT,
            enable_live_theme_updates: bool = False,
    ):
        image = pg.Surface(size.to_tuple, pg.SRCALPHA)
        self.ui_manager = UIManager(
            size.to_tuple,
            f"Assets/{theme_path}" if theme_path is not None else None,
            enable_live_theme_updates,
        )

        super().__init__(position, image, z, alignment)

    def loop(self):
        # We process events to handle interactions
        for event in Game.events:
            # FIX: Previne processamento duplicado
            if getattr(event, '_ui_processed', False):
                continue

            # We must offset mouse events because the ui_manager thinks it's at (0,0)
            # but this component might be drawn elsewhere on screen.
            if event.type == pg.MOUSEMOTION:
                event.pos = (event.pos[0] - self.transform.position.x, event.pos[1] - self.transform.position.y)
            elif event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                event.pos = (event.pos[0] - self.transform.position.x, event.pos[1] - self.transform.position.y)

            self.ui_manager.process_events(event)

            # Marca o evento como processado
            event._ui_processed = True

        self.ui_manager.update(self.game.delta_time)

        self.image.fill((0, 0, 0, 0))
        self.ui_manager.draw_ui(self.image)

        super().loop()