import asyncio
from contextlib import suppress
from typing import Type

from discord import VoiceChannel, AudioSource
from discord.ext.commands import Context

from bot.structures.audio.numpy_source import NumpyAudioSource
from bot.structures.audio.queue import Queue, QABC
from bot.structures.audio.ytdl_source import YTDLSource
from utils.logging import info


class VoiceContext:
    def __init__(self):
        self.client = None
        self.queue: QABC = Queue()
        self.source = ContextAudioSource(self)

    def play_source(self, ctx: Context, source: AudioSource):
        self.queue.add(ctx, source)
        if not self.client.is_playing():
            self.play()

    def play(self, *_):
        if self.queue and not self.client.is_playing():
            info("Playing song!")
            self.client.play(self.source, after=self.play)

    async def connect(self, channel: VoiceChannel):
        if self.client is None:
            client = await channel.connect()
            await client.disconnect(force=True)  # If we were still here from before reboot
            self.client = await channel.connect(reconnect=True)
            self.play()
        else:
            await self.client.move_to(channel)

    def swap_queue(self, new_queue: Type[QABC]):
        queued = []
        while self.queue:
            queued.append(self.queue.pop_pair())

        self.queue = new_queue()
        for item in queued:
            self.queue.add_raw(item[0], item[1])


class ContextAudioSource(AudioSource):
    def __init__(self, context: VoiceContext):
        self.ctx = context
        self.current_source: YTDLSource = None

    def next_source(self):
        self.current_source = self.ctx.queue.pop()

    def read(self) -> bytes:
        if self.current_source is None:
            if self.ctx.queue:
                self.next_source()
            else:
                return b""

        data = self.current_source.read()
        if not data:
            self.current_source.cleanup()
            if self.ctx.queue:
                self.next_source()
                data = self.current_source.read()
            else:
                self.current_source = None

        return data
