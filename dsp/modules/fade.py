from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule


class FadeModule(BaseModule):
    def __init__(self):
        self.fade_time = 500  # ms

    def process(self, audio: AudioSequence) -> AudioSequence:
        l, r = audio / 2

        samples = int(self.fade_time / 1000 * audio.freq)
        step_size = int(samples / 10)

        for i in range(10):
            # fade in
            l.audio[i * step_size:(i + 1) * step_size] = l.audio[i * step_size:(i + 1) * step_size] * 0.1 * i
            r.audio[i * step_size:(i + 1) * step_size] = r.audio[i * step_size:(i + 1) * step_size] * 0.1 * i

            # fade out
            l.audio[-(i+1) * step_size:-i * step_size] = l.audio[-(i+1) * step_size:-i * step_size] * 0.1 * i
            r.audio[-(i+1) * step_size:-i * step_size] = r.audio[-(i+1) * step_size:-i * step_size] * 0.1 * i

        return l * r
