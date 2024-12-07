from Components.Component import Component
from Components.NetworkComponent import NetworkComponent
from Network import NetworkServer, NetworkClient


class NetworkManager(Component):
    instance: "NetworkManager" = None

    def __init__(self, ip: str, port: int, is_server: bool):
        self.ip = ip
        self.port = port
        self.is_server = is_server
        NetworkManager.instance = self

        if is_server:
            self.network_server = NetworkServer(ip, port)
            self.loop = self.server_loop
        else:
            self.network_client = NetworkClient(ip, port)
            self.loop = self.client_loop

    def server_loop(self):
        for i in range(1, len(self.network_server.clients)):
            data = self.network_server.read(i)
            if data:
                self.handle_server(data, i)

    def client_loop(self):
        data = self.network_client.read()
        if data:
            self.handle_client(data)

    @staticmethod
    def handle_server(data: object, client_id: int):
        if isinstance(data, tuple):
            operation, data = data

            if operation == "Rpc":
                func_name, args = data
                NetworkComponent.Rpcs[func_name](client_id, *args)

    @staticmethod
    def handle_client(data: object):
        if isinstance(data, tuple):
            operation, data = data

            if operation == "Rpc":
                func_name, args = data
                NetworkComponent.Rpcs[func_name](*args)
