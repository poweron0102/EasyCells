import asyncio
import pickle
from asyncio import StreamReader, StreamWriter, AbstractEventLoop

SIZE_SIZE = 4


class NetworkManagerServer:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.clients: list[tuple[StreamReader, StreamWriter] | None] = [None]
        asyncio.run(self.start())

    async def start(self):
        async def handle_client(reader: StreamReader, writer: StreamWriter):
            addr = writer.get_extra_info('peername')
            print(f"Connection established with {addr}, id: {len(self.clients)}")
            self.clients.append((reader, writer))

            # sent the client their id
            self.send(len(self.clients) - 1, len(self.clients) - 1)
            response = await self.read(len(self.clients) - 1)
            print(f"Response from client {len(self.clients) - 1}: {response}")

        server = await asyncio.start_server(handle_client, self.ip, self.port)
        address = server.sockets[0].getsockname()
        print(f"Server running on {address}")

        async with server:
            await server.serve_forever()

    def send(self, data: object, client_id: int):
        data = pickle.dumps(data)
        self.clients[client_id][1].write(len(data).to_bytes(SIZE_SIZE, "big"))
        self.clients[client_id][1].write(data)

    async def read(self, client_id: int):
        client = self.clients[client_id][0]
        if client.at_eof():
            return None
        size = int.from_bytes(await client.read(SIZE_SIZE), "big")
        return pickle.loads(await client.read(size))

    def broadcast(self, data: object):
        for i in range(1, len(self.clients)):
            self.send(data, i)

    def close(self):
        for i in range(1, len(self.clients)):
            self.send("close", i)

        for i in range(1, len(self.clients)):
            self.clients[i][1].close()

        self.clients = [None]
        print("Server closed")

    def close_client(self, client_id: int):
        client = self.clients[client_id][1]
        self.send("close", client_id)
        self.clients.pop(client_id)
        client.close()


class NetworkManagerClient:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.id: int | None = None

        self.server: tuple[StreamReader, StreamWriter] | None = None
        asyncio.run(self.connect())

    async def connect(self):
        reader, writer = await asyncio.open_connection(self.ip, self.port)
        self.server = (reader, writer)

        # get the id from the server
        self.id = await self.read()

        print(f"Connected to server with id {self.id}")
        while True:
            await asyncio.sleep(1000)

    def send(self, data: object):
        data = pickle.dumps(data)
        print(f"Sending data: {data}")
        self.server[1].write(len(data).to_bytes(SIZE_SIZE, "big"))
        self.server[1].write(data)

    async def read(self):
        if self.server[0].at_eof():
            return None
        size = int.from_bytes(await self.server[0].read(SIZE_SIZE), "big")
        return pickle.loads(await self.server[0].read(size))


# test

IP = "localhost"
PORT = 25765

is_server = bool(int(input("Server(1) or Client(0): ")))

if is_server:
    server = NetworkManagerServer(IP, PORT)


    async def test():
        while True:
            for i in range(1, len(server.clients)):
                data = await server.read(i)
                print(f"Data from client {i}: {data}")
                out = input("Responder: ")
                server.send(out, i)

    asyncio.run(test())


else:
    client = NetworkManagerClient(IP, PORT)


    async def test():
        while True:
            data = input("Data: ")
            print(data)
            client.send(data)
            print(await client.read())

    asyncio.run(test())
