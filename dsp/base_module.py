from abc import abstractmethod, ABC
from typing import Dict, Type

from dsp.audio_object import AudioSequence


EXTENSIONS: Dict[str, Type['BaseModule']] = {}


class ClassRegisterMeta(type):
    def __new__(mcs, *args, **kwargs):
        cls = type.__new__(mcs, *args, **kwargs)

        if issubclass(cls, BaseModule) and cls.__name__ == "BaseModule":
            EXTENSIONS[cls.__name__] = cls

        return cls


class BaseModule(ABC):
    @abstractmethod
    def process(self, audio: AudioSequence) -> AudioSequence:
        ...
