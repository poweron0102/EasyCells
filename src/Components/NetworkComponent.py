from enum import Enum
from Components.Component import Component


class SendTo(Enum):
    ALL = 0
    SERVER = 1
    CLIENTS = 2
    OWNER = 2


class NetworkComponent(Component):
    Rpcs: dict[str, callable] = {}
    NetworkComponents: dict[int, "NetworkComponent"] = {}

    def __init__(self, identifier: int, owner: int):
        self.identifier = identifier
        NetworkComponent.NetworkComponents[identifier] = self
        self.owner = owner

    def Rpc(self, func: callable, send_to: SendTo = SendTo.ALL, require_owner: bool = False):
        NetworkComponent.Rpcs[func.__name__] = func

        return func
