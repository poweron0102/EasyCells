from Components.Camera import Camera
from Components.NetworkComponent import NetworkManager, NetworkVariable
from Components.NetworkTransform import NetworkTransform
from Components.Sprite import Sprite
from UserComponents.Player import Player
from Game import Game

player_comp: Player


def init(game: Game):
    global player_comp
    game.CreateItem().AddComponent(Camera())

    player1 = game.CreateItem()
    player1.AddComponent(Sprite("player32.png", (32, 32)))
    player1.AddComponent(NetworkTransform(1, 0))

    player2 = game.CreateItem()
    player2.AddComponent(Sprite("player24.png", (24, 24)))
    player2.AddComponent(NetworkTransform(2, 1))

    player = player1 if NetworkManager.instance.is_server else player2

    player_comp = player.AddComponent(Player())


def loop(game: Game):
    pass
