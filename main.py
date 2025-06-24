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

import Levels.space_selector

if __name__ == '__main__':
    GAME = Game(Levels.space_selector, "Spaceship", True, (1280, 720))
    GAME.run()
    # asyncio.run(GAME.run_async())
