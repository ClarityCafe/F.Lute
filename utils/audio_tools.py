from essentia.standard import AudioLoader

from dsp.audio_object import AudioSequence


def load_audio_file(path: str) -> AudioSequence:
    audio, sample_rate, *_ = AudioLoader(filename=path)()
    return AudioSequence(audio, freq=sample_rate)
