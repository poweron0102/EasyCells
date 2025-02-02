"""
Dependencies:
    - pygame-ce
    - numpy
    - numba
    - scipy
    - pyfmodex
    - midvoxio, matplotlib

    pip install pygame-ce numpy numba scipy pyfmodex midvoxio matplotlib
"""

from Game import Game

if __name__ == '__main__':
    GAME = Game("space_selector", "SpaceSheep", True)  # space_selector level0 net_pong1
    GAME.run()
