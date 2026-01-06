from EasyCells import Game, Vec2
from EasyCells.Components import Camera
from EasyCells.GuiWrapper.GuiManager import GuiManager
from EasyCells.GuiWrapper.GuiButton import GuiButton
from EasyCells.UiComponents import UiAlignment


def init(game: Game):
    game.CreateItem().AddComponent(Camera())

    # Create an Item to hold the UI components
    ui_item = game.CreateItem()

    # Initialize the GuiManager
    # We assume a theme file exists at 'themes/theme.json', or you can adjust the path.
    gui_manager = ui_item.AddComponent(GuiManager(
        position=Vec2(0, 0),
        size=Vec2(1280, 720),
        alignment=UiAlignment.CENTER,
        theme_path="themes/theme.json",
    ))

    # Create a GuiButton
    # We pass the gui_manager so the button can register with the underlying UIManager
    button = GuiButton(
        position=Vec2(50, 50),
        size=Vec2(200, 60),
        text="Test Button",
        on_click=lambda: print("Button Clicked!"),
        on_hover=lambda: print("Button Hovered!"),
    )

    # Register the button with the GuiManager to handle updates and events
    gui_manager.add_component(button)


def loop(game: Game):
    pass
