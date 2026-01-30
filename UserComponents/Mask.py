import os
from EasyCells import Vec2
from EasyCells.Components import Camera
from EasyCells.UiComponents import UiComponent, UiAlignment
import pygame as pg

start_position = Vec2(-170, 255)

class Mask(UiComponent):
    Masks: list[Mask] = []
    dragged_mask = None

    def __init__(self, file_name: str, total: int = 3):

        position = start_position + Vec2(len(Mask.Masks) * (610 // total), 0)

        super().__init__(
            position,
            pg.image.load(f"Assets/Masks/{file_name}").convert_alpha(),
            -200,
            UiAlignment.CENTER
        )

        Mask.Masks.append(self)

        self.last_mouse: bool = False
        self.mouse_pos_dif: Vec2 = Vec2(0, 0)


    # # abstract method
    # def init(self):
    #     pass

    # abstract method
    def loop(self):
        super().loop()

    @staticmethod
    def static_loop():
        mouse = pg.mouse.get_pressed()[0]
        
        # Se o mouse não estiver pressionado, limpa o objeto arrastado
        if not mouse:
            Mask.dragged_mask = None
            return

        # Se já existe um objeto sendo arrastado, atualiza apenas ele
        if Mask.dragged_mask:
            Mask.dragged_mask.transform.position = Camera.get_global_mouse_position() + Mask.dragged_mask.mouse_pos_dif
            return
        
        for mask in Mask.Masks:
            if mask.is_mouse_over():
                Mask.dragged_mask = mask
                mask.mouse_pos_dif = mask.transform.position - Camera.get_global_mouse_position()
                
                # Define o Z como o menor atual - 1 para sobrepor os outros
                if Mask.Masks:
                    mask.transform.z = Mask.Masks[0].transform.z - 1
                break

        Mask.Masks.sort(key=lambda mask: mask.transform.z)

    def on_destroy(self):
        Mask.Masks.remove(self)

    @staticmethod
    def get_available_mask_files() -> list[str]:
        path = "Assets/Masks/"
        if not os.path.exists(path):
            return []
        # Retorna apenas arquivos, ignorando diretórios
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
