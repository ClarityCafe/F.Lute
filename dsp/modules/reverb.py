import numpy

from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule


class ReverbModule(BaseModule):
    def __init__(self):
        self.delay = 300  # ms
        self.decay = 0.55

    def comb(self, audio: AudioSequence, delay: float, decay: float) -> numpy.ndarray:
        reverb_samples = int(delay * (audio.freq/1000))
        samp = audio.audio.copy()
        res = audio.audio.copy()
        for i in range(int((samp.shape[0]-reverb_samples) / reverb_samples)):
            start_index = i * reverb_samples
            end_index = start_index + reverb_samples
            start_r_index = end_index
            end_r_index = end_index + reverb_samples
            decayed = samp[start_index:end_index] * decay
            samp[start_r_index:end_r_index] += decayed
            res[start_r_index:end_r_index] = decayed
        return res

    def transform(self, audio: AudioSequence) -> numpy.ndarray:
        comb_1 = self.comb(audio, self.delay, self.decay)
        comb_2 = self.comb(audio, (self.delay - 11.73), (self.decay - 0.1313))
        comb_3 = self.comb(audio, (self.delay + 19.31), (self.decay - 0.2743))
        comb_4 = self.comb(audio, (self.delay - 7.97), (self.decay - 0.31))

        comb_total = comb_1 + comb_2 + comb_3 + comb_4

        wet = 25
        dry = 100 - wet

        new_audio = audio.audio * (dry/100) + comb_total * (wet/100)

        return new_audio

    def process(self, audio: AudioSequence) -> AudioSequence:
        left, right = audio / 2

        new_left = self.transform(left)
        new_right = self.transform(right)

        return left.new(new_left) * right.new(new_right)
