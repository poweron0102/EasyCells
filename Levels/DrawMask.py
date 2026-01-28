from EasyCells import Game, Vec2
from EasyCells.Components import Camera
from EasyCells.UiComponents import UiAlignment, UiComponent
import pygame as pg

from UserComponents.Mask import Mask
from UserComponents.Paints import Paints

import numpy as np
from numba import njit, prange
import random



board_surface: pg.Surface


def init(game: Game):
    global board_surface

    game.CreateItem().AddComponent(Camera())

    cellular = game.CreateItem().AddComponent(UiComponent(
        Vec2(-460, 0),
        pg.image.load(f"Assets/Celular.png").convert_alpha(), # (360, 720)
        alignment=UiAlignment.CENTER
    ))

    sup_bar = game.CreateItem().AddComponent(UiComponent(
        Vec2(125, -315),
        pg.image.load(f"Assets/BarraSuperior.png").convert_alpha(),  # (360, 720)
        alignment=UiAlignment.CENTER
    ))


    board_surface = pg.image.load(f"Assets/Board.png").convert_alpha() # (900, 420)
    board = game.CreateItem().AddComponent(UiComponent(
        Vec2(180, -60),
        board_surface,
        alignment=UiAlignment.CENTER
    ))

    for mask in Mask.get_available_mask_files():
        game.CreateItem().AddComponent(Mask(mask))

    paints = game.CreateItem().AddComponent(Paints(Vec2(490, 255)))

def loop(game: Game):

    if Paints.color is None:
        Mask.static_loop()

    elif pg.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_x -= 370
        mouse_y -= 90

        draw(
            (mouse_x, mouse_y),
            board_surface,
            get_masks_data(Mask.Masks),
            Paints.color,
            20,
            50
        )

        print("==========")
        for l in Mask.Masks: print(l, l.transform.z)












# =============================================================================
# LÓGICA DO NUMBA (Back-end Matemático)
# =============================================================================

@njit(fastmath=True)
def _spray_kernel(
        pos_x: int,
        pos_y: int,
        spreading: int,
        color_rgb: tuple,
        board_pixels: np.ndarray,
        masks_rgb_list: list,  # Lista de arrays (W, H, 3)
        masks_alpha_list: list,  # Lista de arrays (W, H)
        masks_offsets: np.ndarray,  # Array Nx2 com (offset_x, offset_y) de cada máscara
        density: int = 100
):
    """
    Kernel compilado JIT para calcular o spray e colisões.
    """
    board_w, board_h, _ = board_pixels.shape
    r, g, b = color_rgb

    # Gera 'density' partículas de tinta
    for _ in range(density):
        # Distribuição uniforme polar
        angle = random.random() * 2 * np.pi
        radius = np.sqrt(random.random()) * spreading

        offset_x = int(radius * np.cos(angle))
        offset_y = int(radius * np.sin(angle))

        px = pos_x + offset_x
        py = pos_y + offset_y

        # Verifica limites globais do board
        if px < 0 or px >= board_w or py < 0 or py >= board_h:
            continue

        painted = False

        # 1. Verifica as máscaras (Camadas superiores)
        # IMPORTANTE: A lista deve vir ordenada do TOPO para o FUNDO
        num_masks = len(masks_rgb_list)

        for i in range(num_masks):
            mask_rgb = masks_rgb_list[i]
            mask_alpha = masks_alpha_list[i]

            # Pega o offset específico desta máscara
            m_off_x = masks_offsets[i, 0]
            m_off_y = masks_offsets[i, 1]

            # Coordenada relativa à máscara atual
            mx = px - m_off_x
            my = py - m_off_y

            mw, mh = mask_alpha.shape

            # Verifica se o ponto cai dentro desta máscara
            if 0 <= mx < mw and 0 <= my < mh:
                # Verifica se o pixel na máscara NÃO é transparente
                if mask_alpha[mx, my] > 0:
                    mask_rgb[mx, my, 0] = r
                    mask_rgb[mx, my, 1] = g
                    mask_rgb[mx, my, 2] = b
                    mask_alpha[mx, my] = 255
                    painted = True
                    break  # Bateu nesta máscara, para de cair

        # 2. Se não bateu em nenhuma máscara, pinta o board (Fundo)
        if not painted:
            board_pixels[px, py, 0] = r
            board_pixels[px, py, 1] = g
            board_pixels[px, py, 2] = b


# =============================================================================
# WRAPPER PYTHON (Interface Pygame)
# =============================================================================

def draw(
        position: tuple[int, int],
        board: pg.Surface,
        masks: list[tuple[pg.Surface, tuple[int, int]]],  # Lista de (Surface, (x, y))
        color: pg.Color,
        spreading: int = 20,
        density: int = 50
):
    """
    Função principal.
    :param masks: Lista ordenada (Topo -> Fundo) de tuplas (Surface, (x, y)).
                  (x, y) deve ser a posição topleft da máscara no board.
    """
    x, y = position

    # Preparação dos dados para o Numba
    board_arr = pg.surfarray.pixels3d(board)

    masks_rgb = []
    masks_alpha = []
    masks_offsets = []

    # Itera sobre cada máscara individualmente
    for surf, offset in masks:
        masks_rgb.append(pg.surfarray.pixels3d(surf))
        masks_alpha.append(pg.surfarray.pixels_alpha(surf))
        masks_offsets.append(offset)

    # Converte offsets para array numpy int32 para velocidade no Numba
    # Se a lista for vazia, cria um array vazio compatível
    if masks_offsets:
        offsets_arr = np.array(masks_offsets, dtype=np.int32)
    else:
        offsets_arr = np.zeros((0, 2), dtype=np.int32)

    color_tuple = (color.r, color.g, color.b)

    _spray_kernel(
        x, y,
        spreading,
        color_tuple,
        board_arr,
        masks_rgb,
        masks_alpha,
        offsets_arr,
        density
    )


def get_masks_data(mask_objects: list[Mask]) -> list[tuple[pg.Surface, tuple[int, int]]]:
    """
    Converte a lista de objetos da classe Mask para o formato exigido pelo draw.
    Calcula a posição topleft assumindo que mask.transform.position é o CENTRO.
    Ordena do maior Z (frente) para o menor Z (fundo).
    """

    formatted_data = []

    for mask in mask_objects:
        # Assumindo que mask.sprite é a Surface do Pygame (padrão em engines)
        # Se o nome for diferente (ex: mask.image), ajuste aqui.
        surface = mask.image

        w, h = surface.get_size()

        # Converte posição do centro (EasyCells) para topleft (Pygame/Numpy)
        topleft_x = int(mask.transform.position.x - w / 2)
        topleft_y = int(mask.transform.position.y - h / 2)

        topleft_x += 270
        topleft_y += 270

        formatted_data.append((surface, (topleft_x, topleft_y)))

    return formatted_data
