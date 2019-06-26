from essentia.standard import AudioLoader

from bot.structures.audio.numpy_source import NumpyAudioSource


def load_audio_file(path: str) -> NumpyAudioSource:
    audio, sample_rate, *_ = AudioLoader(filename=path)()
    return NumpyAudioSource(audio, sample_rate)
