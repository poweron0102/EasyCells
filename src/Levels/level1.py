from main import Game


def init(game: Game):
    print("init1: ")


def loop(game: Game):
    print("loop1: ")
    if game.run_time > 0.05:
        exit(0)
