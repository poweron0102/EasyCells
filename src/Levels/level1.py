from Game import Game


def init(game: Game):
    print("init1: ")


def loop(game: Game):
    print("loop1: ")
    if game.run_time > 2:
        game.new_game("level0")
