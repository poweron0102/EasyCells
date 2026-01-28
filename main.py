"""
Dependencies:
    - pygame-ce
    - numpy
    - numba
    - scipy
    - pyfmodex
    - midvoxio, matplotlib
    - pygame_gui

    pip install pygame-ce numpy numba scipy pyfmodex midvoxio matplotlib pygame_gui
"""
# import asyncio

from EasyCells import Game

import Levels.test_rigidbody
import Levels.space_selector
import Levels.GuiTest as gt
import Levels.DrawMask as dm

if __name__ == '__main__':
    #GAME = Game(gt, "Spaceship", True, (1280, 720))
    #GAME = Game(Levels.test_rigidbody, "Spaceship", True, (600, 400))
    GAME = Game(dm, "DrawMask", True, (1280, 720), )
    GAME.run()
    # asyncio.run(GAME.run_async())
