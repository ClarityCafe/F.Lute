from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule
from dsp.utils import multiplier_from_db


class VolumeModule(BaseModule):
    def __init__(self):
        self.volume: float = 0.0

    def process(self, data: AudioSequence) -> AudioSequence:
        return data ** multiplier_from_db(self.volume)
