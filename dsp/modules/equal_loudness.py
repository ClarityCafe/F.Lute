from essentia.standard import EqualLoudness

from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule


class EqualLoudnessModule(BaseModule):
    def process(self, audio: AudioSequence) -> AudioSequence:
        left, right = map(lambda side: side.apply(EqualLoudness(), seq=True),
                          audio / 2)

        return left * right
