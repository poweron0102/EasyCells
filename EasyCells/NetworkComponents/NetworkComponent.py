import ipaddress
from weakref import WeakValueDictionary
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

# ID reservado para RPCs estáticos/globais
STATIC_NET_ID = 0


class SendTo(Enum):
    ALL = 0  # Envia para todos (incluindo eu, se for Server)
    SERVER = 1  # Envia para o Server
    CLIENTS = 2  # Server envia para todos os clientes
    OWNER = 3  # Envia apenas para o dono do objeto
    NOT_ME = 4  # Envia para todos, exceto quem enviou


def Rpc(send_to: SendTo = SendTo.ALL, require_owner: bool = True):
    """
    Decorador que suporta métodos de instância (NetworkComponent),
    métodos estáticos (@staticmethod) e funções livres.
    """

    def decorator(func: Callable):
        # Registra RPC estático se não for método de instância óbvio no momento da definição
        # (Nota: A distinção real acontece no wrapper, em tempo de execução)
        if func.__qualname__ != func.__name__:
            # Pode ser um método de classe, mas garantimos o registro no wrapper dinâmico
            pass

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Tenta identificar se é uma chamada de instância
            instance = None
            if args and isinstance(args[0], NetworkComponent):
                instance = args[0]

            # --- Caminho de Instância ---
            if instance:
                if not getattr(instance, "_is_executing_rpc", False):
                    # args[1:] remove o 'self' para o envio, pois o receptor recolocará o self dele
                    instance.send_rpc(func.__name__, args[1:], send_to)

                    if NetworkManager.instance.is_server and send_to == SendTo.ALL:
                        return func(instance, *args[1:], **kwargs)
                    return None

                # Execução local vinda da rede
                return func(instance, *args[1:], **kwargs)

            # --- Caminho Estático / Função Livre ---
            else:
                # Usa o componente estático global para enviar
                static_comp = NetworkComponent.get_static_instance()

                # Garante que a função está registrada para recebimento
                if func.__name__ not in NetworkComponent._static_rpcs:
                    NetworkComponent._static_rpcs[func.__name__] = func

                # Evita loop infinito se chamado pela própria rede
                if not getattr(static_comp, "_is_executing_rpc", False):
                    static_comp.send_rpc(func.__name__, args, send_to)

                    if NetworkManager.instance.is_server and send_to == SendTo.ALL:
                        return func(*args, **kwargs)
                    return None

                # Execução local vinda da rede
                return func(*args, **kwargs)

        wrapper._rpc_config = {
            "send_to": send_to,
            "require_owner": require_owner
        }

        # Se for função livre ou estática, registramos o nome logo para lookup reverso
        # (Otimização para evitar register on-the-fly sempre)
        NetworkComponent._static_rpcs[func.__name__] = wrapper

        return wrapper

    return decorator


class NetworkComponent(Component):
    # Registro estático para roteamento de ID -> Instância
    _active_components: dict[int, "NetworkComponent"] = {}

    # Suporte para RPCs Estáticos
    _static_instance: "NetworkComponent" = None
    _static_rpcs: dict[str, Callable] = {}

    def __init__(self, identifier: int, owner: int):
        self.identifier = identifier
        self.owner = owner
        self._is_executing_rpc = False  # Flag de controle de recursão

        if identifier == STATIC_NET_ID:
            NetworkComponent._static_instance = self

    def init(self):
        """Chamado pela engine ao iniciar."""
        if self.identifier is not None:
            NetworkComponent._active_components[self.identifier] = self

    @classmethod
    def get_static_instance(cls):
        """Lazy initialization do componente estático."""
        if cls._static_instance is None:
            cls._static_instance = NetworkComponent(STATIC_NET_ID, 0)
            # Força registro manual pois o init() normal depende da engine
            cls._active_components[STATIC_NET_ID] = cls._static_instance
        return cls._static_instance

    def on_destroy(self):
        """Remove o objeto do registro quando ele é destruído."""
        if self.identifier in NetworkComponent._active_components:
            del NetworkComponent._active_components[self.identifier]

        # Sobrescreve para evitar chamadas futuras
        self.on_destroy = lambda: None

    def send_rpc(self, method_name: str, args: tuple, send_to: SendTo):
        """Encapsula e envia o pacote."""
        packet = (OP_RPC, self.identifier, method_name, args)
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

        method = None
        config = None

        # Verifica se é este componente é o Manipulador Estático
        if self.identifier == STATIC_NET_ID:
            # Procura na lista de RPCs estáticos registrados
            if method_name in NetworkComponent._static_rpcs:
                original_func = NetworkComponent._static_rpcs[method_name]
                method = original_func
                config = method._rpc_config
            else:
                print(f"Erro: RPC Estático '{method_name}' não registrado.")
                return
        else:
            # Comportamento padrão de Instância
            if not hasattr(self, method_name):
                print(f"Erro: RPC '{method_name}' não encontrado no objeto {self.identifier}")
                return
            method = getattr(self, method_name)
            if hasattr(method, "_rpc_config"):
                config = method._rpc_config

        if method is None or config is None:
            return

        # Validação de Dono (Segurança no Server)
        if NetworkManager.instance.is_server and config["require_owner"]:
            if sender_id != self.owner:
                # Para estáticos, owner geralmente é 0 (Server), então clientes não podem chamar se require_owner=True
                print(f"Negado: RPC {method_name} no objeto {self.identifier} exige permissão de dono.")
                return

        # Execução Protegida
        try:
            self._is_executing_rpc = True
            if self.identifier == STATIC_NET_ID:
                method(*args)  # Chama sem self
            else:
                method(*args)  # Chama com self embutido (bound method)
        finally:
            self._is_executing_rpc = False

        # Se for Server, retransmite se necessário
        if NetworkManager.instance.is_server:
            self._server_relay_rpc(method_name, args, config["send_to"], sender_id)

    def _server_relay_rpc(self, method_name: str, args: tuple, send_to: SendTo, sender_id: int):
        """Lógica de retransmissão do servidor (Relay)."""
        packet = (OP_RPC, self.identifier, method_name, args)
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
    _active_variables: WeakValueDictionary[int, 'NetworkVariable'] = WeakValueDictionary()

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

    def handle_network_update(self, sub_op: int, args: tuple, sender_id: int):
        """Processa pacotes OP_VAR recebidos pelo NetworkManager."""
        nm = NetworkManager.instance

        if sub_op == VAR_SET:
            new_val = args[0]

            if nm.is_server:
                # Servidor validando escrita de um cliente
                if self.require_owner and sender_id != self.owner:
                    print(f"Negado: Cliente {sender_id} tentou modificar Variável {self.var_id} sem permissão.")
                    # Opcional: Forçar rollback no cliente enviando o valor antigo de volta
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

    def __init__(
            self,
            ip: str,
            port: int,
            is_server: bool,
            connect_callback: Callable[[int], None] = None
    ):
        NetworkManager.instance = self
        self.is_server = is_server
        self.ip = ip
        self.port = port
        self.id = 0 if is_server else -1

        # Configuração de Callbacks (como no original)
        self.connect_callbacks: list[Callable[[int], None]] = []
        if connect_callback is not None:
            self.connect_callbacks.append(connect_callback)

        # Lógica de Versão de IP (IPv4 vs IPv6)
        if ip == "localhost":
            ip_version = 4
        else:
            try:
                ip_version = ipaddress.ip_address(ip).version
            except ValueError:
                # Fallback para IPv4 se houver erro ou for um hostname não resolvido aqui
                ip_version = 4

        # Inicialização do Servidor/Cliente passando os callbacks
        if self.is_server:
            # Assumindo assinatura original: (ip, port, ip_version, callback)
            self.server = NetworkServer(ip, port, ip_version, self.server_callback)
        else:
            self.client = NetworkClient(ip, port, ip_version, self.client_callback)

    def client_callback(self, client_id: int):
        """Chamado quando este cliente se conecta (recebe seu ID)."""
        self.id = client_id
        for call in self.connect_callbacks:
            call(client_id)

    def server_callback(self, client_id: int):
        """Chamado no servidor quando um novo cliente se conecta."""
        for call in self.connect_callbacks:
            call(client_id)

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
            
    def call_rpc_on_client(self, client_id: int, rpc_method: Callable, *args):
        if not self.is_server:
            return

        target_id = STATIC_NET_ID
        method_name = rpc_method.__name__

        if hasattr(rpc_method, "__self__") and isinstance(rpc_method.__self__, NetworkComponent):
            target_id = rpc_method.__self__.identifier

        packet = (OP_RPC, target_id, method_name, args)
        self.server.send(packet, client_id)

    @staticmethod
    def process_packet(data: tuple, sender_id: int):
        """Roteador central de pacotes."""
        try:
            # Estrutura: (OP_CODE, TARGET_ID, PAYLOAD, ARGS)
            op_code, target_id, payload, args = data

            if op_code == OP_RPC:
                component = NetworkComponent._active_components.get(target_id)
                if component:
                    component.handle_incoming_rpc(payload, args, sender_id)

            elif op_code == OP_VAR:
                variable = NetworkVariable._active_variables.get(target_id)
                if variable:
                    variable.handle_network_update(payload, args, sender_id)
                else:
                    pass

        except ValueError:
            print("Pacote malformado recebido.")
        except Exception as e:
            print(f"Erro processando pacote: {e}")

    def on_destroy(self):
        if self.is_server:
            self.server.close()
        else:
            self.client.close()