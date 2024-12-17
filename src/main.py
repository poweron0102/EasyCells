"""
Dependencies:
    - pygame
    - numpy
    - numba
    - scipy
    - pyfmodex
    - midvoxio, matplotlib
"""

from Game import Game

if __name__ == '__main__':
    GAME = Game("space_selector")
    GAME.run()
