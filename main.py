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
from EasyCells import Game


if __name__ == '__main__':
    GAME = Game("space_selector", "Spaceship", True)
    GAME.run()
