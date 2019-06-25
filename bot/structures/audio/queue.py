from abc import abstractmethod, ABC
from typing import Dict, List

from discord import AudioSource
from discord.ext.commands import Context


class QABC(ABC):
    @abstractmethod
    def add(self, ctx: Context, source: AudioSource):
        ...

    @abstractmethod
    def pop(self) -> AudioSource:
        ...

    @abstractmethod
    def peek(self) -> AudioSource:
        ...


class Queue(QABC):
    """ Simple FIFO queue """

    def __init__(self):
        self._queue: List[AudioSource] = []

    def add(self, ctx: Context, source: AudioSource):
        self._queue.append(source)

    def pop(self):
        return self._queue.pop(0)

    def peek(self):
        return self._queue[0]


class RotatingQueue(QABC):
    def __init__(self):
        self._queues: Dict[int, List[AudioSource]] = {}
        self._users: List[int] = []

    def add(self, ctx: Context, source: AudioSource):
        if ctx.author.id not in self._users:
            self._users.append(ctx.author.id)
            self._queues[ctx.author.id] = []

        self._queues[ctx.author.id].append(source)

    def pop(self):
        user = self._users.pop(0)
        song = self._queues[user].pop(0)
        if not self._queues[user]:
            del self._queues[user]
        else:
            self._users.append(user)

        return song

    def peek(self):
        user = self._users[0]
        song = self._queues[user][0]
        return song
