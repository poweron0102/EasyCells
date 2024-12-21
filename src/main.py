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
    GAME = Game("net_pong1")  # space_selector level0
    GAME.run()
