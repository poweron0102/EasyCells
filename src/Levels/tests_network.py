# Example usage

from Components.NetworkComponent import NetworkComponent, SendTo, Rpc, NetworkManager
from Game import Game


class ExampleComponent(NetworkComponent):
    def __init__(self, identifier: int, owner: int):
        super().__init__(identifier, owner)

    @Rpc(send_to=SendTo.ALL, require_owner=True)
    def example_rpc(self, some_value: int):
        print(f"RPC ALL called with value: {some_value}")
        # print backtrace
        # print("".join(traceback.format_stack()))

    @Rpc(send_to=SendTo.CLIENTS, require_owner=True)
    def example_rpc_to_clients(self, some_value: int):
        print(f"RPC CLIENTS called with value: {some_value}")
        # print backtrace
        # print("".join(traceback.format_stack()))

    @Rpc(send_to=SendTo.SERVER, require_owner=True)
    def example_rpc_to_server(self, some_value: int):
        print(f"RPC SERVER called with value: {some_value}")
        # print backtrace
        # print("".join(traceback.format_stack()))


def init(game: Game):
    is_server = bool(int(input("Server(1) or Client(0): ")))
    network_manager = game.CreateItem().AddComponent(NetworkManager("localhost", 1234, is_server=is_server))

    # Example usage
    a = game.CreateItem().AddComponent(ExampleComponent(1, 1))
    b = game.CreateItem().AddComponent(ExampleComponent(2, 1))

    def t():
        a.example_rpc(55)
        b.example_rpc_to_clients(100)
        b.example_rpc_to_server(200)
        game.scheduler.add(10, t)

    if not is_server:
        game.scheduler.add(10, t)


def loop(game: Game):
    pass
