from Components.NetworkComponent import NetworkManager
from Game import Game


def init(game: Game):
    ip = input('Digite o IP do servidor default "localhost": ')
    if ip == '':
        ip = 'localhost'

    port = input('Digite a porta do servidor default "5000": ')
    if port == '':
        port = '5000'
    port = int(port)

    is_server = input('Deseja ser servidor? (s/N): ')
    if is_server.lower() == 's':
        is_server = True
    else:
        is_server = False

    game.CreateItem().AddComponent(NetworkManager(ip, port, is_server, 6))

    print('Conectando ao servidor...')
    game.scheduler.add(1, lambda: game.new_game('net_2'))


def loop(game: Game):
    pass
