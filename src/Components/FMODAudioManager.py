import os
from Components.Component import Component

FMOD_BASE_PATH = "Assets/fmod_studio/"

os.environ["PYFMODEX_DLL_PATH"] = FMOD_BASE_PATH + "lib/fmod.dll"
os.environ["PYFMODEX_STUDIO_DLL_PATH"] = FMOD_BASE_PATH + "lib/fmodstudio.dll"
import pyfmodex.studio


class FMODAudioManager(Component):
    instance: 'FMODAudioManager'

    _is_playing: bool = False

    @property
    def is_playing(self):
        return self._is_playing

    @is_playing.setter
    def is_playing(self, value):
        self._is_playing = value
        if value:
            self.music_instance.start()
        else:
            self.music_instance.stop()
        self.studio_system.update()

    def __init__(self, banks: list[str], start_event: str | None = None):
        FMODAudioManager.instance = self

        self.studio_system = pyfmodex.studio.StudioSystem()
        self.studio_system.initialize()

        for bank in banks:
            self.studio_system.load_bank_file(FMOD_BASE_PATH + bank)

        self.music_reference = None
        self.music_instance = None

        if start_event:
            self.play(start_event)

    def on_destroy(self):
        self.studio_system.release()
        self.music_instance.release()
        self.music_reference.release()
        self.studio_system.release()
        self.studio_system.update()
        FMODAudioManager.instance = None

    def play(self, event_name: str):
        if self.is_playing:
            self.music_instance.stop()
        self.music_reference = self.studio_system.get_event(f"event:/{event_name}")
        self.music_instance = self.music_reference.create_instance()
        self.is_playing = True
