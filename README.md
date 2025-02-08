# EasyCells

EasyCells is a Python game development framework inspired by Unity. It allows you to create **Items** (equivalent to Unity's GameObjects), organize game logic into **Levels** (equivalent to Unity's Scenes), and add **Components** to define object behaviors and functionalities.

## Project Structure

Your project should follow this structure:

```
your_game/
├── Levels/           # Game scenes
│   └── level1.py
├── Assets/           # Game resources
│   ├── Ui/
│   ├── Sounds/
│   └── image.png
└── main.py           # Entry point 
```

## Installation

Install the required dependencies with:

```sh
pip install pygame-ce numpy numba scipy pyfmodex midvoxio matplotlib
```

## Initializing the Game

The `Game` class should be created in `main.py`:

```python
from EasyCells import Game

if __name__ == '__main__':
    GAME = Game("level1")
    GAME.run()
```

## Creating a Level

Levels are files inside the `Levels/` folder. Each Level must contain two main functions:

- `init(game: Game)`: Initializes the objects in the Level.
- `loop(game: Game)`: Runs every frame.

Example of a basic Level:

```python
from EasyCells import Game
from EasyCells.Components import Sprite

# Initialize Level objects
def init(game: Game):
    camera = game.CreateItem()
    camera.AddComponent(Camera())
  
    item = game.CreateItem()  # Every Item already has a Transform automatically
    item.AddComponent(Sprite("image.png"))

# Game loop
def loop(game: Game):
    pass
```

## RPC (Remote Procedure Call) Example

EasyCells supports Remote Procedure Calls (RPC) to synchronize actions between the server and clients. Use the `@Rpc` decorator to mark functions that will be called remotely. See the example below with explanations for each `SendTo` option:

```python
from EasyCells.NetworkComponents import Rpc, NetworkComponent

class MyNetworkComponent(NetworkComponent):
    @Rpc(SendTo.ALL)
    def action_all(self):
        """Executed on all (ALL)."""
        print("RPC: Executed on all.")

    @Rpc(SendTo.SERVER)
    def action_server(self):
        """Executed only on the server."""
        print("RPC: Executed on the server.")

    @Rpc(SendTo.CLIENTS)
    def action_clients(self):
        """Executed on clients, except on the server."""
        print("RPC: Executed on clients.")

    @Rpc(SendTo.OWNER)
    def action_owner(self):
        """Executed only on the object owner client."""
        print("RPC: Executed on the owner client.")

    @Rpc(SendTo.NOT_ME)
    def action_not_me(self):
        """Executed on all except the sender."""
        print("RPC: Executed on all, except the sender.")
```

## Conclusion

EasyCells allows for modular and organized game development. Use **Levels** to structure game stages, **Items** to represent game objects, and **Components** to add behaviors. If needed, synchronize actions over the network with **RPC**. Explore the framework to build your game in a simple and efficient way!

