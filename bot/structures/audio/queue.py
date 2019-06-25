from discord import AudioSource
from discord.ext.commands import Context


class Queue:
    """ Simple FIFO queue """

    def __init__(self):
        self._queue = []

    def add(self, ctx: Context, source: AudioSource):
        self._queue.append(source)

    def pop(self):
        return self._queue.pop(0)

    def peek(self):
        return self._queue[0]

