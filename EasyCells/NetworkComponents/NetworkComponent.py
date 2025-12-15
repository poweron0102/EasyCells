import ipaddress
from enum import Enum, auto
from functools import wraps
from typing import Callable, Any

from EasyCells.Components.Component import Component
from EasyCells.NetworkTCP import NetworkServerTCP as NetworkServer, NetworkClientTCP as NetworkClient

# from EasyCells.NetworkUDP import NetworkServerUDP as NetworkServer, NetworkClientUDP as NetworkClient

# --- Constantes de Protocolo ---
OP_RPC = 1
OP_VAR = 2

# Sub-operações para Variáveis
VAR_SET = 1
VAR_GET = 2


class SendTo(Enum):
    ALL = 0  # Envia para todos (incluindo eu, se for Server)
    SERVER = 1  # Envia para o Server
    CLIENTS = 2  # Server envia para todos os clientes
    OWNER = 3  # Envia apenas para o dono do objeto
    NOT_ME = 4  # Envia para todos, exceto quem enviou


def Rpc(send_to: SendTo = SendTo.ALL, require_owner: bool = True):
    """
    Decorador simples: Apenas marca o método com metadados.
    A lógica pesada foi movida para o NetworkComponent.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Se for uma chamada local (pelo código do jogo), roteia pela rede
            if not getattr(self, "_is_executing_rpc", False):
                self.send_rpc(func.__name__, args, send_to)

                # Se for SendTo.ALL e eu sou o servidor, executo localmente também
                if NetworkManager.instance.is_server and send_to == SendTo.ALL:
                    return func(self, *args, **kwargs)
                return None

            # Se a flag _is_executing_rpc for True, significa que o NetworkComponent
            # chamou isso vindo da rede. Executa a lógica real.
            return func(self, *args, **kwargs)

        wrapper._rpc_config = {
            "send_to": send_to,
            "require_owner": require_owner
        }
        return wrapper

    return decorator


class NetworkComponent(Component):
    # Registro estático apenas para roteamento de ID -> Instância
    _active_components: dict[int, "NetworkComponent"] = {}

    def __init__(self, identifier: int, owner: int):
        self.net_id = identifier
        self.owner = owner
        self._is_executing_rpc = False  # Flag de controle de recursão

    def init(self):
        """Chamado pela engine ao iniciar."""
        if self.net_id is not None:
            NetworkComponent._active_components[self.net_id] = self

    def on_destroy(self):
        """Remove o objeto do registro quando ele é destruído."""
        if self.net_id in NetworkComponent._active_components:
            del NetworkComponent._active_components[self.net_id]

        # Sobrescreve para evitar chamadas futuras
        self.on_destroy = lambda: None

    def send_rpc(self, method_name: str, args: tuple, send_to: SendTo):
        """Encapsula e envia o pacote."""
        packet = (OP_RPC, self.net_id, method_name, args)
        nm = NetworkManager.instance

        if nm.is_server:
            if send_to == SendTo.ALL or send_to == SendTo.CLIENTS:
                nm.server.broadcast(packet)
            elif send_to == SendTo.NOT_ME:
                nm.server.broadcast(packet)
            elif send_to == SendTo.OWNER and self.owner != 0:
                nm.server.send(packet, self.owner)
        else:
            nm.client.send(packet)

    def handle_incoming_rpc(self, method_name: str, args: tuple, sender_id: int):
        """Recebe o pacote da rede, verifica segurança e executa."""
        if not hasattr(self, method_name):
            print(f"Erro: RPC '{method_name}' não encontrado no objeto {self.net_id}")
            return

        method = getattr(self, method_name)

        if not hasattr(method, "_rpc_config"):
            return

        config = method._rpc_config

        # Validação de Dono (Segurança no Server)
        if NetworkManager.instance.is_server and config["require_owner"]:
            if sender_id != self.owner:
                print(
                    f"Negado: Cliente {sender_id} tentou chamar RPC protegido no objeto {self.net_id} (Dono: {self.owner})")
                return

        # Execução Protegida
        try:
            self._is_executing_rpc = True
            method(*args)
        finally:
            self._is_executing_rpc = False

        # Se for Server, retransmite se necessário
        if NetworkManager.instance.is_server:
            self._server_relay_rpc(method_name, args, config["send_to"], sender_id)

    def _server_relay_rpc(self, method_name: str, args: tuple, send_to: SendTo, sender_id: int):
        """Lógica de retransmissão do servidor (Relay)."""
        packet = (OP_RPC, self.net_id, method_name, args)
        srv = NetworkManager.instance.server

        if send_to == SendTo.ALL or send_to == SendTo.CLIENTS:
            srv.broadcast(packet)
        elif send_to == SendTo.NOT_ME:
            for cid in range(1, len(srv.clients)):
                if cid != sender_id:
                    srv.send(packet, cid)
        elif send_to == SendTo.OWNER and self.owner != sender_id:
            srv.send(packet, self.owner)


class NetworkVariable[T]:
    """
    Variável sincronizada automaticamente pela rede.
    Pode ser usada independentemente de um NetworkComponent, contanto que tenha um ID único.
    """
    _active_variables: dict[int, 'NetworkVariable'] = {}

    def __init__(self, value: T, identifier: int, owner: int, require_owner: bool = True):
        self.var_id = identifier
        self.owner = owner
        self.require_owner = require_owner
        self._value = value

        NetworkVariable._active_variables[identifier] = self

        # Se for cliente, solicita o valor atual ao servidor ao inicializar
        if not NetworkManager.instance.is_server:
            # Envia pedido de sincronização (GET)
            packet = (OP_VAR, self.var_id, VAR_GET, ())
            NetworkManager.instance.client.send(packet)

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new_value: T):
        """Define o valor localmente e envia para a rede."""
        self._value = new_value

        # Cria pacote de atualização (SET)
        packet = (OP_VAR, self.var_id, VAR_SET, (new_value,))
        nm = NetworkManager.instance

        if nm.is_server:
            # Servidor: Atualiza local e broadcast para todos os clientes
            nm.server.broadcast(packet)
        else:
            # Cliente: Atualiza local e envia para o servidor (que vai validar e retransmitir)
            nm.client.send(packet)

    def destroy(self):
        """Remove do registro para evitar memory leaks."""
        if self.var_id in NetworkVariable._active_variables:
            del NetworkVariable._active_variables[self.var_id]

    def handle_network_update(self, sub_op: int, args: tuple, sender_id: int):
        """Processa pacotes OP_VAR recebidos pelo NetworkManager."""
        nm = NetworkManager.instance

        if sub_op == VAR_SET:
            new_val = args[0]

            if nm.is_server:
                # Servidor validando escrita de um cliente
                if self.require_owner and sender_id != self.owner:
                    print(f"Negado: Cliente {sender_id} tentou modificar Variável {self.var_id} sem permissão.")
                    return

                # Atualiza valor no servidor
                self._value = new_val

                # Retransmite para outros clientes (Relay - NOT_ME)
                packet = (OP_VAR, self.var_id, VAR_SET, (new_val,))
                for cid in range(1, len(nm.server.clients)):
                    if cid != sender_id:
                        nm.server.send(packet, cid)
            else:
                # Cliente recebendo atualização do servidor
                self._value = new_val

        elif sub_op == VAR_GET:
            # Apenas servidor processa GETs
            if nm.is_server:
                # Responde ao solicitante com um SET contendo o valor atual
                packet = (OP_VAR, self.var_id, VAR_SET, (self._value,))
                nm.server.send(packet, sender_id)


class NetworkManager(Component):
    instance: 'NetworkManager' = None

    def __init__(self, ip: str, port: int, is_server: bool):
        NetworkManager.instance = self
        self.is_server = is_server
        self.ip = ip
        self.port = port
        self.my_id = 0 if is_server else -1

        if self.is_server:
            self.server = NetworkServer(ip, port)
        else:
            self.client = NetworkClient(ip, port)

    def init(self):
        if hasattr(self.item, "destroy_on_load"):
            self.item.destroy_on_load = False

    def loop(self):
        if self.is_server:
            self._server_loop()
        else:
            self._client_loop()

    def _server_loop(self):
        # Itera sobre clientes para ler mensagens
        for client_id in range(1, len(self.server.clients)):
            while data := self.server.read(client_id):
                self.process_packet(data, client_id)

    def _client_loop(self):
        while data := self.client.read():
            self.process_packet(data, 0)  # 0 é o ID do servidor

    @staticmethod
    def process_packet(data: tuple, sender_id: int):
        """Roteador central de pacotes."""
        try:
            # Estrutura: (OP_CODE, TARGET_ID, PAYLOAD, ARGS)
            # Para RPC: PAYLOAD = method_name
            # Para VAR: PAYLOAD = sub_op (VAR_SET/VAR_GET)
            op_code, target_id, payload, args = data

            if op_code == OP_RPC:
                component = NetworkComponent._active_components.get(target_id)
                if component:
                    component.handle_incoming_rpc(payload, args, sender_id)
                else:
                    # O objeto pode não ter sido criado ainda no cliente
                    pass

            elif op_code == OP_VAR:
                variable = NetworkVariable._active_variables.get(target_id)
                if variable:
                    # payload aqui é o sub_op (SET ou GET)
                    variable.handle_network_update(payload, args, sender_id)
                else:
                    print(f"Aviso: Variável {target_id} não encontrada para atualização.")

        except ValueError:
            print("Pacote malformado recebido.")
        except Exception as e:
            print(f"Erro processando pacote: {e}")

    def on_destroy(self):
        if self.is_server:
            self.server.close()
        else:
            self.client.close()