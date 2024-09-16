import os, sys
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

os.environ["PYFMODEX_DLL_PATH"] = resource_path("lib/fmod.dll")
os.environ["PYFMODEX_STUDIO_DLL_PATH"] = resource_path("lib/fmodstudio.dll")
import pyfmodex.studio
from Components.Component import Component

class FMODAudioManager(Component):

    def __init__(self):
        FMODAudioManager.studio_system = pyfmodex.studio.StudioSystem()
        FMODAudioManager.studio_system.initialize()
        # print(FMODAudioManager.studio_system.core_system.num_drivers)
        
        FMODAudioManager.studio_system.load_bank_file(resource_path("src/Assets/fmod_studio/Build/Desktop/Master.bank"))
        FMODAudioManager.studio_system.load_bank_file(resource_path("src/Assets/fmod_studio/Build/Desktop/Master.strings.bank"))

        FMODAudioManager.music_reference = FMODAudioManager.studio_system.get_event("event:/music")
        FMODAudioManager.music_instance = FMODAudioManager.music_reference.create_instance()

    def init(self):
        FMODAudioManager.music_instance.start()

    def loop(self):
        self.studio_system.update()

    def on_destroy(self):
        pass #Camera.instance.to_draw.remove(self)