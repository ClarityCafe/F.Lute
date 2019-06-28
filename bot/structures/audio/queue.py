from abc import abstractmethod, ABC
from itertools import zip_longest
from typing import Dict, List, Tuple

from discord import AudioSource
from discord.ext.commands import Context


class QABC(ABC):
    @abstractmethod
    def add(self, ctx: Context, source: AudioSource):
        ...

    @abstractmethod
    def add_raw(self, uid: int, source: AudioSource):
        ...

    @abstractmethod
    def pop_pair(self) -> Tuple[int, AudioSource]:
        ...

    @abstractmethod
    def pop(self) -> AudioSource:
        ...

    @abstractmethod
    def peek(self) -> AudioSource:
        ...

    @abstractmethod
    def list(self) -> List[AudioSource]:
        ...

    def __bool__(self) -> bool:
        return False


class Queue(QABC):
    """ Simple FIFO queue """

    def __init__(self):
        self._users: List[int] = []
        self._queue: List[AudioSource] = []

    def list(self) -> List[AudioSource]:
        return self._queue

    def add(self, ctx: Context, source: AudioSource):
        self.add_raw(ctx.author.id, source)

    def add_raw(self, uid: int, source: AudioSource):
        self._users.append(uid)
        self._queue.append(source)

    def pop_pair(self):
        return self._users.pop(), self._queue.pop()

    def pop(self):
        self._users.pop()
        return self._queue.pop(0)

    def peek(self):
        return self._queue[0]

    def __bool__(self) -> bool:
        try:
            self.peek()
            return True
        except IndexError:
            return False


class RotatingQueue(QABC):
    def __init__(self):
        self._queues: Dict[int, List[AudioSource]] = {}
        self._users: List[int] = []

    def list(self) -> List[AudioSource]:
        res = []
        for items in zip_longest(*self._queues.values()):
            for it in items:
                if it is not None:
                    res.append(it)

        return res

    def add_raw(self, uid: int, source: AudioSource):
        if uid not in self._users:
            self._users.append(uid)
            self._queues[uid] = []

        self._queues[uid].append(source)

    def add(self, ctx: Context, source: AudioSource):
        self.add_raw(ctx.author.id, source)

    def pop_pair(self):
        user = self._users[0]
        return user, self.pop()

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

    def __bool__(self) -> bool:
        try:
            self.peek()
            return True
        except IndexError:
            return False
