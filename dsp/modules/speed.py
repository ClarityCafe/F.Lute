from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule


class SpeedModule(BaseModule):
    def __init__(self):
        self.speed = 1

    def process(self, audio: AudioSequence) -> AudioSequence:
        return audio[self.speed]
