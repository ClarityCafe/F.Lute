from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule


class ReverseModule(BaseModule):
    def process(self, audio: AudioSequence) -> AudioSequence:
        return audio.new(audio.audio[::-1])
