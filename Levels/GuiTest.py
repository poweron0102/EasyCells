from EasyCells import Game, Vec2
from EasyCells.Components import Camera
from EasyCells.GuiWrapper.GuiManager import GuiManager
from EasyCells.UiComponents import UiAlignment
import pygame as pg
import pygame_gui
from pygame_gui.elements import (
    UIButton,
    UILabel,
    UIPanel,
    UITextEntryLine,
    UIHorizontalSlider,
    UIDropDownMenu,
    UIProgressBar,
    UISelectionList
)


def init(game: Game):
    game.CreateItem().AddComponent(Camera())

    # Create an Item to hold the UI components
    ui_item = game.CreateItem()

    # Initialize the GuiManager
    # Define o tamanho da área de UI (geralmente o tamanho da janela)
    gui_component = GuiManager(
        position=Vec2(0, 0),
        size=Vec2(1280, 720),
        alignment=UiAlignment.CENTER,
        theme_path="themes/theme.json",
    )
    gui_manager = ui_item.AddComponent(gui_component)

    # Acessa o 'manager' nativo do pygame_gui através do componente wrapper
    manager = gui_component.ui_manager

    # --- Criando um Painel Central (Container) ---
    # Centralizando um painel de tamanho 500x620 na tela 1280x720
    panel_width, panel_height = 500, 620
    screen_width, screen_height = 1280, 720

    panel_rect = pg.Rect(0, 0, panel_width, panel_height)
    panel_rect.center = (screen_width // 2, screen_height // 2)

    panel = UIPanel(
        relative_rect=panel_rect,
        manager=manager,
        margins={'left': 20, 'right': 20, 'top': 20, 'bottom': 20}
    )

    # --- Título ---
    UILabel(
        relative_rect=pg.Rect(0, 0, panel_width - 40, 50),
        text="Configurações do Jogo",
        manager=manager,
        container=panel,
        object_id='#main_title'  # Útil se você for editar o theme.json depois
    )

    # --- Entrada de Texto (Nome) ---
    UILabel(
        relative_rect=pg.Rect(0, 60, panel_width - 40, 25),
        text="Nome de Usuário:",
        manager=manager,
        container=panel
    )

    name_input = UITextEntryLine(
        relative_rect=pg.Rect(0, 90, panel_width - 40, 35),
        manager=manager,
        container=panel,
        placeholder_text="Digite seu nickname..."
    )

    # --- Slider (Volume) ---
    UILabel(
        relative_rect=pg.Rect(0, 140, panel_width - 40, 25),
        text="Volume Mestre:",
        manager=manager,
        container=panel
    )

    volume_slider = UIHorizontalSlider(
        relative_rect=pg.Rect(0, 170, panel_width - 40, 25),
        start_value=0.75,
        value_range=(0.0, 1.0),
        manager=manager,
        container=panel
    )

    # --- Dropdown (Dificuldade) ---
    UILabel(
        relative_rect=pg.Rect(0, 210, panel_width - 40, 25),
        text="Nível de Dificuldade:",
        manager=manager,
        container=panel
    )

    difficulty_drop = UIDropDownMenu(
        options_list=["Fácil", "Médio", "Difícil", "Lendário"],
        starting_option="Médio",
        relative_rect=pg.Rect(0, 240, panel_width - 40, 35),
        manager=manager,
        container=panel
    )

    # --- Selection List (Servidor/Mapa) ---
    UILabel(
        relative_rect=pg.Rect(0, 290, panel_width - 40, 25),
        text="Selecione o Servidor:",
        manager=manager,
        container=panel
    )

    server_list = UISelectionList(
        relative_rect=pg.Rect(0, 320, panel_width - 40, 100),
        item_list=["Servidor BR-01", "Servidor US-East", "Servidor EU-West", "Localhost"],
        manager=manager,
        container=panel,
        allow_multi_select=False
    )

    # --- Progress Bar (Status) ---
    UILabel(
        relative_rect=pg.Rect(0, 440, panel_width - 40, 25),
        text="Ping / Latência:",
        manager=manager,
        container=panel
    )

    ping_bar = UIProgressBar(
        relative_rect=pg.Rect(0, 470, panel_width - 40, 25),
        manager=manager,
        container=panel
    )
    ping_bar.set_current_progress(0.15)  # Exemplo de ping baixo (bom)

    # --- Botões de Ação (Rodapé) ---
    btn_width = 200
    spacing = (panel_width - 40 - (btn_width * 2))  # Calcula espaço restante para alinhar

    save_btn = UIButton(
        relative_rect=pg.Rect(0, 540, btn_width, 40),
        text="Salvar & Sair",
        manager=manager,
        container=panel
    )

    cancel_btn = UIButton(
        relative_rect=pg.Rect(btn_width + spacing, 540, btn_width, 40),
        text="Cancelar",
        manager=manager,
        container=panel
    )

frame_c = 0

def loop(game: Game):
    # Loop de exemplo para processar eventos específicos da UI
    # Nota: O GuiManager já desenha e atualiza a UI, aqui pegamos apenas a lógica de "Gameplay/Menu"7

    global frame_c
    for event in Game.events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(f"{frame_c}: Botão Pressionado: {event.ui_element.text}")

        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            # Exibe o valor formatado (ex: 0.75)
            print(f"{frame_c}: Volume alterado: {event.value:.2f}")

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            print(f"{frame_c}: Dificuldade alterada para: {event.text}")

        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            print(f"{frame_c}: Servidor selecionado: {event.text}")

    frame_c += 1