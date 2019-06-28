from typing import List

import numpy
from essentia.standard import BandPass, HighPass, LowPass

from dsp.audio_object import AudioSequence
from dsp.base_module import BaseModule
from dsp.utils import multiplier_from_db


class PRESETS:
    FLAT                  = [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
    VOCAL_BOOST           = [ -2.5, -2.5,  0.0,  0.0,  0.0,  0.0,  0.6,  3.5,  1.5, -2.0]
    TREBLE_REDUCE         = [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -6.5, -4.0]
    TREBLE_BOOST          = [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  4.0,  6.5]
    SMALL_SPEAKERS        = [  6.5,  6.5,  4.0,  0.0,  0.0,  0.0,  0.0,  0.0, -6.5, -4.0]
    ROCK                  = [  4.5,  4.5,  2.8,  0.0,  0.0,  0.0,  0.0, -0.5,  2.8,  4.0]
    R_AND_B               = [  5.5,  5.5,  3.5,  0.0,  0.0,  0.0,  0.0, -1.8,  1.5,  2.5]
    DEEP                  = [  4.0,  4.0,  0.5,  0.0,  0.0,  0.0,  0.0,  1.5, -4.0, -4.5]
    CLASSICAL             = [  4.0,  4.0,  3.3,  1.0,  0.0,  0.0, -1.0, -0.5,  2.0,  3.5]
    BASS_REDUCE           = [-10.5, -6.5, -4.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
    BASS_BOOST            = [ 10.0,  6.5,  4.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]


class EqualizerModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.eq = PRESETS.FLAT

        sample_rate = 44100  # default
        self.filters = [                                                             # Frequency bands:
            LowPass(cutoffFrequency=31, sampleRate=sample_rate),                     # 0-31
            BandPass(cutoffFrequency=63, bandwidth=62, sampleRate=sample_rate),      # 63-125
            BandPass(cutoffFrequency=125, bandwidth=125, sampleRate=sample_rate),    # 125-250
            BandPass(cutoffFrequency=250, bandwidth=250, sampleRate=sample_rate),    # 250-500
            BandPass(cutoffFrequency=500, bandwidth=500, sampleRate=sample_rate),    # 500-1000
            BandPass(cutoffFrequency=1000, bandwidth=1000, sampleRate=sample_rate),  # 1000-2000
            BandPass(cutoffFrequency=2000, bandwidth=2000, sampleRate=sample_rate),  # 2000-4000
            BandPass(cutoffFrequency=4000, bandwidth=4000, sampleRate=sample_rate),  # 4000-8000
            BandPass(cutoffFrequency=8000, bandwidth=8000, sampleRate=sample_rate),  # 8000-16000
            HighPass(cutoffFrequency=16000, sampleRate=sample_rate)                  # 16000-inf
        ]

    def update_filters(self, sample_rate: int):
        self.filters = [                                                             # Frequency bands:
            LowPass(cutoffFrequency=31, sampleRate=sample_rate),                     # 0-31
            BandPass(cutoffFrequency=63, bandwidth=62, sampleRate=sample_rate),      # 63-125
            BandPass(cutoffFrequency=125, bandwidth=125, sampleRate=sample_rate),    # 125-250
            BandPass(cutoffFrequency=250, bandwidth=250, sampleRate=sample_rate),    # 250-500
            BandPass(cutoffFrequency=500, bandwidth=500, sampleRate=sample_rate),    # 500-1000
            BandPass(cutoffFrequency=1000, bandwidth=1000, sampleRate=sample_rate),  # 1000-2000
            BandPass(cutoffFrequency=2000, bandwidth=2000, sampleRate=sample_rate),  # 2000-4000
            BandPass(cutoffFrequency=4000, bandwidth=4000, sampleRate=sample_rate),  # 4000-8000
            BandPass(cutoffFrequency=8000, bandwidth=8000, sampleRate=sample_rate),  # 8000-16000
            HighPass(cutoffFrequency=16000, sampleRate=sample_rate)                  # 16000-inf
        ]

    def transform(self, audio: numpy.ndarray) -> numpy.ndarray:
        results = numpy.array(list(map(lambda f: f(audio), self.filters)))
        samples = []
        for i in range(10):
            samples.append(results[i] * multiplier_from_db(self.eq[i]))
        return numpy.sum(samples, axis=0)

    def process(self, audio: AudioSequence) -> AudioSequence:
        left, right = audio / 2

        self.update_filters(audio.freq)
        new_left = numpy.concatenate([self.transform(frame.audio) for frame in left])
        new_right = numpy.concatenate([self.transform(frame.audio) for frame in right])

        return left.new(new_left) * right.new(new_right)
