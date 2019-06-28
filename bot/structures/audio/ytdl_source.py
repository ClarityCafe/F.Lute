import asyncio
import os
import uuid
from functools import partial
from tempfile import NamedTemporaryFile

import aiohttp
import youtube_dl as ytdl
from discord import AudioSource
from discord.ext.commands import Context

from bot.bot import MusicBot
from bot.structures.audio.numpy_source import NumpyAudioSource
from dsp.handler import process_audio
from utils.audio_tools import load_audio_file
from utils.logging import info


class YTDLSource(AudioSource):
    opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'audioformat': 'flac/wav/opus',
        'source_address': '0.0.0.0',
        'quiet': True,
        'default_search': 'auto',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac',
            'preferredquality': '192'
        }]
    }

    def __init__(self, query, loop=None, executor=None):
        self.query = query
        self.executor = executor
        self.loop = loop or asyncio.get_event_loop()
        self._done = False
        self._fname = ""

        self.source = None
        self.duration = None
        self.url = None
        self.id = None
        self.raw_url = None
        self.views = None
        self.likes = None
        self.dislikes = None
        self.is_stream = None
        self.uploader = None
        self.thumbnail = None
        self.title = None
        self.description = None
        self.tags = None
        self.requester = None
        self.request_id = None

    def __repr__(self):
        return f"YTDLSource(title='{self.title}', url='{self.url}')"

    async def load(self):
        with ytdl.YoutubeDL(self.opts) as dl:
            f = partial(dl.extract_info, self.query, download=False)

            data = await self.loop.run_in_executor(self.executor, f)
            if "entries" in data:
                data = data["entries"][0]
            self.set_data(data)

    async def load_data(self, bot: MusicBot, ctx: Context, executor=None):
        if not self._done and not self.is_stream:
            self._done = True
            fname = uuid.uuid4().hex

            copts = {
                "outtmpl": f"/tmp/{fname}.%(ext)s"
            }

            path = f"/tmp/{fname}.flac"

            copts.update(self.opts)

            with ytdl.YoutubeDL(copts) as dl:
                f = partial(dl.download, [self.query])
                data = await self.loop.run_in_executor(executor, f)

                self._fname = path

                # load audio
                info(f"Loading audio: {path}")
                seq = load_audio_file(path)
                info("Processing")
                new_audio = process_audio(bot, ctx, seq)
                self.source = NumpyAudioSource(new_audio.audio, new_audio.freq)

    def set_data(self, data):
        self.duration = data.get("duration")
        self.url = data.get("webpage_url")
        self.id = data.get("id")
        self.raw_url = data.get("url")
        self.views = data.get("view_count")
        self.likes = data.get("like_count")
        self.dislikes = data.get("dislike_count")
        self.is_stream = data.get("is_live")
        self.uploader = data.get("uploader")
        self.thumbnail = data.get("thumbnail")
        self.title = data.get("title")
        self.description = data.get("description")
        self.tags = data.get("tags")

    def read(self):
        return self.source.read()

    def cleanup(self):
        if self.source is not None:
            os.system(f"rm {self._fname}")
            self.source.cleanup()

    def set_requester(self, requester):
        self.requester = requester
        self.request_id = requester.id
