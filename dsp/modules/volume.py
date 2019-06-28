from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule
from dsp.utils import multiplier_from_db


class VolumeModule(BaseModule):
    def __init__(self):
        self.volume: float = 0.0

    def process(self, data: AudioSequence) -> AudioSequence:
        # Due to clipping, we can at max have a multiplier of 0 dB (maxes out audio)
        # So we half the volume by default by removing 10 dB
        # This allows the user to make the song twice as loud at 10dB (multiplier of 1),
        # Half as loud at -10dB (multiplier of 0.25)
        # Or leave it as default at 0dB (multiplier of 0.5)
        return data ** multiplier_from_db(self.volume - 10)
