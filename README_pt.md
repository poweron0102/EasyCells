# EasyCells

EasyCells é um framework para desenvolvimento de jogos em Python, inspirado no Unity. Ele permite criar **Items** (equivalentes aos GameObjects do Unity), organizar a lógica do jogo em **Levels** (equivalentes às Scenes do Unity) e adicionar **Componentes** para definir comportamentos e funcionalidades dos objetos.

## Estrutura do Projeto

O projeto deve seguir esta estrutura:

```
your_game/
├── Levels/           # Game scenes
│   └── level1.py
├── Assets/           # Game resources
│   ├── Ui/
│   └── Sounds/
└── main.py           # Entry point 
```

## Inicializando o Jogo

A classe `Game` deve ser criada no `main.py`:

```python
from EasyCells import Game

if __name__ == '__main__':
    GAME = Game("level1")
    GAME.run()
```

## Criando um Level

Os Levels são arquivos dentro da pasta `Levels/`. Cada Level deve conter duas funções principais:

- `init(game: Game)`: Inicializa os objetos do Level.
- `loop(game: Game)`: Executado a cada frame.

Exemplo de um Level básico:

```python
from EasyCells import Game
from EasyCells.Components import Sprite

# Inicializa os objetos do Level
def init(game: Game):
    camera = game.CreateItem()
    camera.AddComponent(Camera())
  
    item = game.CreateItem()  # Todo Item já possui Transform automaticamente
    item.AddComponent(Sprite("imagem.png"))

# Loop do jogo
def loop(game: Game):
    pass
```

## Exemplo de RPC (Remote Procedure Call)

EasyCells suporta chamadas de procedimento remoto (RPC) para sincronizar ações entre servidor e clientes. Utilize o decorador `@Rpc` para marcar funções que serão chamadas remotamente. Veja o exemplo abaixo com explicações para cada opção do parâmetro `SendTo`:

```python
from EasyCells.NetworkComponents import Rpc, NetworkComponent

class MeuComponenteDeRede(NetworkComponent):
    @Rpc(SendTo.ALL)
    def acao_todos(self):
        """Executado em todos (ALL)."""
        print("RPC: Executado em todos.")

    @Rpc(SendTo.SERVER)
    def acao_servidor(self):
        """Executado somente no servidor."""
        print("RPC: Executado no servidor.")

    @Rpc(SendTo.CLIENTS)
    def acao_clientes(self):
        """Executado nos clientes, exceto no servidor."""
        print("RPC: Executado nos clientes.")

    @Rpc(SendTo.OWNER)
    def acao_proprietario(self):
        """Executado somente no cliente proprietário."""
        print("RPC: Executado no cliente proprietário.")

    @Rpc(SendTo.NOT_ME)
    def acao_exceto_origem(self):
        """Executado em todos, exceto no originador da chamada."""
        print("RPC: Executado em todos, exceto no originador.")
```

## Conclusão

EasyCells permite desenvolver jogos de forma modular e organizada. Utilize **Levels** para estruturar as fases do jogo, **Items** para representar os objetos do jogo e **Componentes** para adicionar comportamentos. Se necessário, sincronize ações pela rede com **RPC**. Explore o framework para construir seu jogo de maneira simples e prática!

