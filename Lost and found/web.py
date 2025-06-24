from collections.abc import Callable
from functools import wraps
import socket


class Web:
    def __init__(self, port: int = 8080, host: str = "localhost", debug: bool = False):
        self.port = port
        self.host = host
        self.is_debug = debug

        self.routes = {}

    def page(self, path: str):
        def decorator(func: Callable):
            if path in self.routes:
                raise ValueError(f"Path '{path}' is already registered.")

            self.routes[path] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def debug(self, *args):
        if self.is_debug:
            print(*args)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Server running on http://{self.host}:{self.port}/")

            while True:
                client_socket, addr = server_socket.accept()
                with client_socket:
                    self.debug(f"Connection from {addr}")
                    request = client_socket.recv(1024).decode()
                    self.debug(f"Request: {request}")

                    path = request.split(" ")[1]
                    args = self.read_json(request)

                    if path in self.routes:
                        if self.routes[path].__code__.co_argcount > 0:
                            response = "HTTP/1.1 200 OK\r\n\r\n" + self.routes[path](args)
                        else:
                            response = "HTTP/1.1 200 OK\r\n\r\n" + self.routes[path]()
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"

                    client_socket.sendall(response.encode())

    @staticmethod
    def read_json(request: str) -> dict | None:
        try:
            json_data = request.split("\r\n\r\n")[1]
            return eval(json_data)
        except IndexError:
            return None
        except SyntaxError:
            return None


# Example usage
web = Web(port=8080, host="localhost")


@web.page("/")
def index():
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Welcome to Lost and Found</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>Welcome to Lost and Found</h1>
            <p>This is the main page.</p>
            <a href="/about">About</a>
            <br>
            <input type="text" id="user_name" placeholder="Enter your name">
            <button onclick="
                const name = document.getElementById('user_name').value;
                const request = fetch('/set_user_name', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }},
                    body: JSON.stringify({{ name: name }})
                }});
                request.then(response => response.text())
                    .then(data => console.log(data));
                location.reload();
            ">Set username</button>
    
            <br>
            <p>User name: {user_name}</p>
        </body>
    </html>
"""


@web.page("/about")
def about():
    return "About Page"


user_name = ""


@web.page("/set_user_name")
def set_user_name(name: dict):
    global user_name
    user_name = name.get("name", "")
    print(f"User name set to: {user_name}")
    return "ok"


web.run()
