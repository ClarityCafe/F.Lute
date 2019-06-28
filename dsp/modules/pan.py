import math

from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule


class PanModule(BaseModule):
    def __init__(self):
        self.angle = math.radians(0)

    def process(self, audio: AudioSequence) -> AudioSequence:
        angle = self.angle
        left, right = audio / 2

        mult = math.sqrt(2)/2

        left_new = mult * (math.cos(angle) - math.sin(angle)) * left.audio
        right_new = mult * (math.cos(angle) + math.sin(angle)) * right.audio

        return left.new(left_new) * right.new(right_new)
