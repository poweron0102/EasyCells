from enum import Enum
from functools import wraps
from typing import Callable, Any

from Components.Component import Component
from Network import NetworkServer, NetworkClient


class SendTo(Enum):
    ALL = 0
    SERVER = 1
    CLIENTS = 2
    OWNER = 3
    NOT_ME = 4


def Rpc(send_to: SendTo = SendTo.ALL, require_owner: bool = True):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Attach metadata to the function
        wrapper._rpc_metadata = {
            "send_to": send_to,
            "require_owner": require_owner
        }
        return wrapper

    return decorator


class NetworkComponent(Component):
    Rpcs: dict[str, Callable] = {}
    NetworkComponents: dict[int, "NetworkComponent"] = {}

    def __init__(self, identifier: int, owner: int):
        self.identifier = identifier
        self.owner = owner
        NetworkComponent.NetworkComponents[identifier] = self

        if NetworkManager.instance.is_server:
            NetworkManager.on_data_received["Rpc"] = NetworkComponent.rpc_handler_server
            NetworkManager.on_data_received["RpcT"] = NetworkComponent.rpct_handler_server
        else:
            NetworkManager.on_data_received["Rpc"] = NetworkComponent.rpc_handler_client
            NetworkManager.on_data_received["RpcT"] = NetworkComponent.rpct_handler_client

    def init(self):
        self.register_rpcs()

    def register_rpcs(self):
        """
        Automatically register methods decorated with @Rpc.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_rpc_metadata"):
                NetworkComponent.Rpcs[f"{attr_name}:{self.identifier}"] = attr

                # Use default argument to bind the current value of attr_name2
                def new_func(*args, attr_name=attr_name):
                    return self.invoke_rpc(attr_name, *args)

                setattr(self, attr_name, new_func)

    def invoke_rpc(self, func_name: str, *args):
        """
        Call an RPC function locally or send the call to the network manager.
        """
        if f"{func_name}:{self.identifier}" in NetworkComponent.Rpcs:
            func = NetworkComponent.Rpcs[f"{func_name}:{self.identifier}"]
            metadata = getattr(func, "_rpc_metadata", {})
            send_to = metadata.get("send_to", SendTo.ALL)
            require_owner = metadata.get("require_owner", True)

            if require_owner and not NetworkManager.instance.is_server and self.owner != NetworkManager.instance.id:
                raise PermissionError("This RPC requires ownership.")

            # Determine where to send the RPC
            if send_to == SendTo.ALL:
                self.send_rpc_to_all(func_name, *args)
            elif send_to == SendTo.SERVER:
                self.send_rpc_to_server(func_name, *args)
            elif send_to == SendTo.CLIENTS:
                self.send_rpc_to_clients(func_name, *args)
            elif send_to == SendTo.OWNER and self.owner:
                self.send_rpc_to_client(self.owner, func_name, *args)
            elif send_to == SendTo.NOT_ME:
                self.send_rpc_to_not_me(func_name, *args)
        else:
            raise ValueError(f"RPC function '{func_name}:{self.identifier}' not registered.")

    def send_rpc_to_server(self, func_name: str, *args):
        if NetworkManager.instance.is_server:
            NetworkComponent.Rpcs[f"{func_name}:{self.identifier}"](*args)
        else:
            data = ("Rpc", (func_name, self.identifier, args))
            NetworkManager.instance.network_client.send(data)

    def send_rpc_to_clients(self, func_name: str, *args):
        if NetworkManager.instance.is_server:
            NetworkManager.instance.network_server.broadcast(("Rpc", (func_name, self.identifier, args)))
        else:
            data = ("RpcT", (func_name, self.identifier, args))
            NetworkManager.instance.network_client.send(data)

    def send_rpc_to_client(self, client_id: int, func_name: str, *args):
        if NetworkManager.instance.is_server:
            data = ("Rpc", (func_name, self.identifier, args))
            NetworkManager.instance.network_server.send(data, client_id)
        else:
            data = ("RpcT", (func_name, self.identifier, args))
            NetworkManager.instance.network_client.send(data)

    def send_rpc_to_all(self, func_name: str, *args):
        self.send_rpc_to_clients(func_name, *args)
        if NetworkManager.instance.is_server:
            NetworkComponent.Rpcs[f"{func_name}:{self.identifier}"](*args)

    def send_rpc_to_not_me(self, func_name: str, *args):
        if NetworkManager.instance.is_server:
            self.send_rpc_to_clients(func_name, *args)
        else:
            data = ("RpcT", (func_name, self.identifier, args))
            NetworkManager.instance.network_client.send(data)

    @staticmethod
    def rpc_handler_server(client_id: int, func_name: str, obj_identifier: int, args: tuple):
        func = NetworkComponent.Rpcs[f"{func_name}:{obj_identifier}"]
        requer_owner = func._rpc_metadata.get("require_owner", True)

        if requer_owner and NetworkComponent.NetworkComponents[obj_identifier].owner != client_id:
            print("This RPC requires ownership.")
            return

        func(*args)

    @staticmethod
    def rpc_handler_client(func_name: str, obj_identifier: int, args: tuple):
        func = NetworkComponent.Rpcs[f"{func_name}:{obj_identifier}"]
        func(*args)

    @staticmethod
    def rpct_handler_server(client_id: int, func_name: str, obj_identifier: int, args: tuple):
        func = NetworkComponent.Rpcs[f"{func_name}:{obj_identifier}"]
        requer_owner = func._rpc_metadata.get("require_owner", True)

        if requer_owner and NetworkComponent.NetworkComponents[obj_identifier].owner != client_id:
            print("This RPC requires ownership.")
            return

        send_to = func._rpc_metadata.get("send_to", SendTo.ALL)

        if send_to == SendTo.ALL:
            NetworkManager.instance.network_server.broadcast(("Rpc", (func_name, obj_identifier, args)))
            func(*args)
        elif send_to == SendTo.CLIENTS:
            NetworkManager.instance.network_server.broadcast(("Rpc", (func_name, obj_identifier, args)))
        elif send_to == SendTo.OWNER:
            NetworkManager.instance.network_server.send(
                ("Rpc", (func_name, obj_identifier, args)),
                NetworkComponent.NetworkComponents[obj_identifier].owner
            )
        elif send_to == SendTo.NOT_ME:
            for i in range(1, len(NetworkManager.instance.network_server.clients)):
                if i != client_id:
                    NetworkManager.instance.network_server.send(("Rpc", (func_name, obj_identifier, args)), i)
            func(*args)

    @staticmethod
    def rpct_handler_client(func_name: str, obj_identifier: int, args: tuple):
        print("Received RPCT and I'm a client, this should not happen.")


class NetworkManager(Component):
    instance: 'NetworkManager' = None
    on_data_received: dict[str, Callable] = {}

    def __init__(
            self,
            ip: str,
            port: int,
            is_server: bool,
            ip_version: int = 4,
            connect_callback: Callable[[int], None] = lambda x: None,
    ):
        self.ip = ip
        self.port = port
        self.is_server = is_server
        NetworkManager.instance = self

        if is_server:
            self.network_server = NetworkServer(ip, port, ip_version, connect_callback)
            self.id = 0
            self.loop = self.server_loop
        else:
            self.network_client = NetworkClient(ip, port, ip_version, self.client_callback)
            self.loop = self.client_loop
            self.connect_callback = connect_callback

    def client_callback(self, client_id: int):
        self.id = client_id
        self.connect_callback(client_id)

    def init(self):
        self.item.destroy_on_load = False

    def server_loop(self):
        for i in range(1, len(self.network_server.clients)):
            data = self.network_server.read(i)
            if data:
                self.handle_data(data, i)

    def client_loop(self):
        data = self.network_client.read()
        if data:
            self.handle_client(data)

    def handle_data(self, data: Any, client_id: int):
        operation, data = data

        if operation in self.on_data_received:
            NetworkManager.on_data_received[operation](client_id, *data)

    @staticmethod
    def handle_client(data: object):
        operation, data = data

        if operation in NetworkManager.on_data_received:
            NetworkManager.on_data_received[operation](*data)
