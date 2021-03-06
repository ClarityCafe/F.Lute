from io import BytesIO

import numpy
from discord import AudioSource
from discord.opus import Encoder


class NumpyAudioSource(AudioSource):
    def __init__(self, audio: numpy.ndarray, sample_rate: int):
        # top_bound = numpy.max(numpy.abs(audio))

        # - Assume normalized -
        typ = numpy.int16
        top_bound = 1.0
        self.audio = (audio / top_bound * numpy.iinfo(typ).max).astype(typ)
        self.buffer = BytesIO(self.audio.tobytes())
        self.sample_rate = sample_rate

    def read(self):
        # audio = self.buffer.read(int(Encoder.FRAME_SIZE / 48000 * self.sample_rate))
        audio = self.buffer.read(Encoder.FRAME_SIZE)
        return audio

    def cleanup(self):
        pass
