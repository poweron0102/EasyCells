from enum import Enum
from functools import wraps
from typing import Callable

from Components.Component import Component
from Network import NetworkServer, NetworkClient


class SendTo(Enum):
    ALL = 0
    SERVER = 1
    CLIENTS = 2
    OWNER = 3


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

            if require_owner and not NetworkManager.instance.is_server and self.owner != NetworkManager.instance.network_client.id:
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
                func_name, obj_identifier, args = data
                func = NetworkComponent.Rpcs[f"{func_name}:{obj_identifier}"]
                requer_owner = func._rpc_metadata.get("require_owner", True)

                if requer_owner and NetworkComponent.NetworkComponents[obj_identifier].owner != client_id:
                    print("This RPC requires ownership.")
                    return

                func(*args)

            elif operation == "RpcT":
                func_name, obj_identifier, args = data
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

    @staticmethod
    def handle_client(data: object):
        if isinstance(data, tuple):
            operation, data = data

            if operation == "Rpc":
                func_name, obj_identifier, args = data
                func = NetworkComponent.Rpcs[f"{func_name}:{obj_identifier}"]
                func(*args)

            elif operation == "RpcT":
                print("Received RPCT and I'm a client, this should not happen.")
