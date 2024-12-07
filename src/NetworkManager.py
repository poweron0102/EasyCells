import socket
import pickle
import threading

SIZE_SIZE = 4


class NetworkManagerServer:
    def __init__(self, ip: str, port: int, on_connect: callable = lambda: None):
        self.ip = ip
        self.port = port
        self.clients: list[socket] = [None]
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()
        print(f"Server running on {(self.ip, self.port)}")

        self.accept_thread = threading.Thread(target=self.accept_clients)
        self.accept_thread.start()

    def accept_clients(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection established with {addr}, id: {len(self.clients)}")
            self.clients.append(client_socket)

            # Send the client their ID
            self.send(len(self.clients) - 1, len(self.clients) - 1)

    def send(self, data: object, client_id: int):
        data = pickle.dumps(data)
        size = len(data).to_bytes(SIZE_SIZE, "big")

        self.clients[client_id].sendall(size)
        self.clients[client_id].sendall(data)

    def read(self, client_id: int):
        client_socket = self.clients[client_id]
        size = int.from_bytes(client_socket.recv(SIZE_SIZE), "big")
        data = client_socket.recv(size)
        return pickle.loads(data)

    def broadcast(self, data: object):
        for i in range(1, len(self.clients)):
            self.send(data, i)

    def close(self):
        for i in range(1, len(self.clients)):
            self.send("close", i)
            self.clients[i].close()
        self.clients = [None]
        self.server_socket.close()
        print("Server closed")

    def close_client(self, client_id: int):
        if self.clients[client_id]:
            self.send("close", client_id)
            self.clients[client_id].close()
            self.clients.pop(client_id)


class NetworkManagerClient:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))

        # Get the client ID from the server
        self.id = self.read()
        print(f"Connected to server with id {self.id}")

    def send(self, data: object):
        data = pickle.dumps(data)
        size = len(data).to_bytes(SIZE_SIZE, "big")

        self.client_socket.sendall(size)
        self.client_socket.sendall(data)

    def read(self):
        size = int.from_bytes(self.client_socket.recv(SIZE_SIZE), "big")
        data = self.client_socket.recv(size)
        return pickle.loads(data)

    def close(self):
        self.send("close")
        self.client_socket.close()


# Test
# IP = "localhost"
# PORT = 25765
#
# is_server = bool(int(input("Server(1) or Client(0): ")))
#
# if is_server:
#     server = NetworkManagerServer(IP, PORT)
#
#     while len(server.clients) == 1:
#         pass
#
#     while True:
#         data = server.read(1)
#         print(data)
#         response = input("Response: ")
#         server.send(response, 1)
#
# else:
#     client = NetworkManagerClient(IP, PORT)
#
#     while True:
#         response = input("Data: ")
#         client.send(response)
#         data = client.read()
#         print(data)

