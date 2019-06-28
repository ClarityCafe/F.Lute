from typing import Tuple, Callable, Iterable

import essentia
from essentia.standard import Resample, AudioWriter, StereoMuxer, StereoDemuxer, FrameGenerator
import numpy

from bot.structures.audio.numpy_source import NumpyAudioSource


class AudioSequence:
    def __init__(self,
                 audio: numpy.ndarray,
                 freq: int = 44100):
        self.audio: numpy.ndarray = essentia.array(audio)
        self.fs: int = int(freq / 50)
        self.hs: int = int(freq / 50)
        self.freq: int = int(freq)

    def new(self, audio: numpy.ndarray) -> 'AudioSequence':
        return AudioSequence(audio, self.freq)

    def __getitem__(self, item):
        left, right = self / 2
        resample_rate = self.freq / item
        res_func = Resample(outputSampleRate=resample_rate, quality=0)
        new_left = left.new(res_func(left.audio))
        new_right = left.new(res_func(right.audio))
        return new_left * new_right

    def apply(self, func: Callable, seq=False):
        x = func(self.audio)
        if seq:
            x = self.new(x)
        return x

    def __pow__(self, power, _=None):
        return self.new(self.audio * power)

    def __eq__(self, other):
        if isinstance(other, AudioSequence):
            return self.hs == other.hs and self.fs == other.fs and self.freq == other.freq
        return False

    def __ne__(self, other):
        return not self == other

    def __iter__(self) -> Iterable['AudioSequence']:
        return (self.new(x) for x in FrameGenerator(
            self.audio, frameSize=self.fs, hopSize=self.hs))

    def __radd__(self, _):  # for sum() support
        return self

    def __add__(self, other) -> 'AudioSequence':
        if not isinstance(other, (AudioSequence, numpy.ndarray)):
            raise ValueError("Can only append AudioSequence or numpy.ndarray!")

        if isinstance(other, AudioSequence):
            if self != other:
                raise ValueError(
                    "Frequency, Hopsize and framesize should be equal!")
            other = other.audio

        return self.new(numpy.concatenate([self.audio, other]))

    def __truediv__(self, other) -> Tuple['AudioSequence', 'AudioSequence']:
        if other != 2:
            raise ValueError("Can only split audio sequence in two tracks!")

        left, right = StereoDemuxer()(self.audio)
        if not list(right):
            right = left.copy()
        return self.new(left), self.new(right)

    def __mul__(self, other) -> 'AudioSequence':
        if not isinstance(other, AudioSequence):
            raise ValueError("Can only concatenate two audio channels!")

        return self.new(StereoMuxer()(self.audio, other.audio))

    def save(self, filename: str):
        AudioWriter(filename=filename)(self.audio)

    def get_source(self) -> NumpyAudioSource:
        return NumpyAudioSource(self.audio, self.freq)
