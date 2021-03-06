from asyncio import sleep
from typing import Dict

from discord import Member, Reaction, Guild
from discord.utils import get

from bot.bot import MusicBot
from bot.cogs.events import DBOTS_GUILD
from bot.structures.audio.queue import Queue, RotatingQueue
from bot.structures.cog import Cog
from bot.structures.menu import MenuContext, event, event_class
from dsp.audio_object import AudioSequence
from dsp.modules.equal_loudness import EqualLoudnessModule
from dsp.modules.equalizer import PRESETS, EqualizerModule
from dsp.modules.fade import FadeModule
from dsp.modules.pan import PanModule
from dsp.modules.reverb import ReverbModule
from dsp.modules.speed import SpeedModule
from dsp.modules.volume import VolumeModule
from utils.logging import info, debug


class MusicSettings(MenuContext):
    def __init__(self, *args):
        super().__init__(*args)
        self.enabled = False
        self.fx = None

    async def update(self):
        pass

    async def setup(self):
        await super().setup()
        await self.update()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return audio


@event_class
class VolumeSettings(MusicSettings):
    id = "Volume"

    def __init__(self, *args):
        super().__init__(*args)
        self.fx = VolumeModule()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        self.fx.volume = round(self.fx.volume * 10) / 10

        await self.set_message(f"""
Enabled: {self.enabled}
Volume: {self.fx.volume}dB
        """.strip())

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines:
            if line.startswith("Enabled: "):
                self.enabled = line.strip().endswith("True")
            elif line.startswith("Volume: "):
                self.fx.volume = float(line[8:-2])

    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        self.fx.volume = min(self.fx.volume+0.1, 10)
        await self.update()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        self.fx.volume = max(self.fx.volume - 0.1, -10)
        await self.update()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        self.fx.volume = min(self.fx.volume + 1, 10)
        await self.update()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        self.fx.volume = max(self.fx.volume - 1, -10)
        await self.update()

    @event("\N{WHITE HEAVY CHECK MARK}")
    async def enable(self):
        self.enabled = True
        await self.update()

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    async def disable(self):
        self.enabled = False
        await self.update()


@event_class
class PanSettings(MusicSettings):
    id = "Panning"

    def __init__(self, *args):
        super().__init__(*args)
        self.fx = PanModule()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        await self.set_message(f"""
Enabled: {self.enabled}
Pan: {self.fx.angle} degrees
        """.strip())

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines:
            if line.startswith("Enabled: "):
                self.enabled = line.strip().endswith("True")
            elif line.startswith("Pan: "):
                self.fx.angle = float(line[5:-8])

    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        self.fx.angle = min(self.fx.angle+1, 45)
        await self.update()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        self.fx.angle = max(self.fx.angle - 1, -45)
        await self.update()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        self.fx.angle = min(self.fx.angle + 5, 45)
        await self.update()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        self.fx.angle = max(self.fx.angle - 5, -45)
        await self.update()

    @event("\N{WHITE HEAVY CHECK MARK}")
    async def enable(self):
        self.enabled = True
        await self.update()

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    async def disable(self):
        self.enabled = False
        await self.update()


@event_class
class FadeSettings(MusicSettings):
    id = "Fade-In-Out"

    def __init__(self, *args):
        super().__init__(*args)
        self.fx = FadeModule()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        await self.set_message(f"""
Enabled: {self.enabled}
Fade time: {self.fx.fade_time}ms
        """.strip())

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines:
            if line.startswith("Enabled: "):
                self.enabled = line.strip().endswith("True")
            elif line.startswith("Fade time: "):
                self.fx.speed = float(line[11:-2])

    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        self.fx.fade_time = min(self.fx.fade_time + 10, 1000)
        await self.update()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        self.fx.fade_time = max(self.fx.fade_time - 10, 100)
        await self.update()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        self.fx.fade_time = min(self.fx.fade_time + 50, 1000)
        await self.update()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        self.fx.fade_time = max(self.fx.fade_time - 50, 100)
        await self.update()

    @event("\N{WHITE HEAVY CHECK MARK}")
    async def enable(self):
        self.enabled = True
        await self.update()

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    async def disable(self):
        self.enabled = False
        await self.update()


@event_class
class SpeedSettings(MusicSettings):
    id = "Playback-Speed"

    def __init__(self, *args):
        super().__init__(*args)
        self.fx = SpeedModule()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        self.fx.speed = round(self.fx.speed * 10) / 10

        await self.set_message(f"""
Enabled: {self.enabled}
Speed: {self.fx.speed}x
        """.strip())

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines:
            if line.startswith("Enabled: "):
                self.enabled = line.strip().endswith("True")
            elif line.startswith("Speed: "):
                self.fx.speed = float(line[7:-1])

    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        self.fx.speed = min(self.fx.speed + 0.1, 2)
        await self.update()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        self.fx.speed = max(self.fx.speed - 0.1, 0.1)
        await self.update()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        self.fx.speed = min(self.fx.speed + 0.5, 2)
        await self.update()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        self.fx.speed = max(self.fx.speed - 0.5, 0.1)
        await self.update()

    @event("\N{WHITE HEAVY CHECK MARK}")
    async def enable(self):
        self.enabled = True
        await self.update()

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    async def disable(self):
        self.enabled = False
        await self.update()


@event_class
class ReverberationSettings(MusicSettings):
    id = "Reverberation"

    def __init__(self, *args):
        super().__init__(*args)
        self.fx = ReverbModule()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        await self.set_message(f"""
Enabled: {self.enabled}
        """.strip())

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines:
            if line.startswith("Enabled: "):
                self.enabled = line.strip().endswith("True")

    @event("\N{WHITE HEAVY CHECK MARK}")
    async def enable(self):
        self.enabled = True
        await self.update()

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    async def disable(self):
        self.enabled = False
        await self.update()


@event_class
class EqualLoudnessSettings(MusicSettings):
    id = "EqualLoudness"

    def __init__(self, *args):
        super().__init__(*args)
        self.fx = EqualLoudnessModule()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        await self.set_message(f"""
Enabled: {self.enabled}
        """.strip())

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines:
            if line.startswith("Enabled: "):
                self.enabled = line.strip().endswith("True")

    @event("\N{WHITE HEAVY CHECK MARK}")
    async def enable(self):
        self.enabled = True
        await self.update()

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    async def disable(self):
        self.enabled = False
        await self.update()


@event_class
class EqualizerSettings(MusicSettings):
    id = "Equalizer"

    def __init__(self, *args):
        super().__init__(*args)
        self.fx = EqualizerModule()
        self.selected = "FLAT"
        self.options = [
            "FLAT",
            "VOCAL_BOOST",
            "TREBLE_REDUCE",
            "TREBLE_BOOST",
            "SMALL_SPEAKERS",
            "ROCK",
            "R_AND_B",
            "DEEP",
            "CLASSICAL",
            "BASS_REDUCE",
            "BASS_BOOST"
        ]

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        self.fx.eq = getattr(PRESETS, self.selected)

        EQ = "\n".join(f"{'->'[setting == self.selected]} {setting}"
                       for setting in self.options)

        await self.set_message(f"""
Enabled: {self.enabled}
{EQ}
    """.strip())

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        setting = ""
        for line in lines:
            if line.startswith("Enabled: "):
                self.enabled = line.strip().endswith("True")
            elif line.startswith("> "):
                setting = line[2:]
                break

        self.selected = setting

    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        index = self.options.index(self.selected)
        new_index = max(0, index - 1)
        self.selected = self.options[new_index]
        await self.update()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        index = self.options.index(self.selected)
        new_index = min(len(self.options) - 1, index + 1)
        self.selected = self.options[new_index]
        await self.update()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        self.selected = self.options[0]
        await self.update()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        self.selected = self.options[-1]
        await self.update()

    @event("\N{WHITE HEAVY CHECK MARK}")
    async def enable(self):
        self.enabled = True
        await self.update()

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    async def disable(self):
        self.enabled = False
        await self.update()


@event_class
class QueueSettings(MenuContext):
    id = "Queue"

    def __init__(self, *args):
        super().__init__(*args)
        self.fair = True

    async def setup(self):
        await super().setup()
        await self.update()

    async def update(self):
        await self.set_message(f"""
Fair Queue: {self.fair}
        """.strip())

        self.bot.get_cog('Commands').contexts[self.channel.guild.id].swap_queue(
            [Queue, RotatingQueue][self.fair]
        )

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines:
            if line.startswith("Fair Queue: "):
                self.fair = line.strip().endswith("True")

    @event("\N{WHITE HEAVY CHECK MARK}")
    async def enable(self):
        self.fair = True
        await self.update()

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    async def disable(self):
        self.fair = False
        await self.update()


class MusicSettingsCog(Cog):
    EXT_CLASSES = (VolumeSettings, EqualizerSettings, SpeedSettings,
                   ReverberationSettings, EqualLoudnessSettings, PanSettings,
                   FadeSettings)

    def __init__(self, bot: MusicBot):
        super().__init__(bot)
        self.contexts: Dict[int, Dict[str, MusicSettings]] = {}
        self.queue_settings: Dict[int, QueueSettings] = {}

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member):
        if not isinstance(user, Member) or user.bot:
            return

        ctx = self.contexts[user.guild.id]
        for name, ct in ctx.items():
            await ct.on_reaction_add(reaction, user)
        await self.queue_settings[user.guild.id].on_reaction_add(reaction, user)

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        debug(f"Setting up MusicSettings for guild {guild.name}")

        await self.bot.get_cog('Events').wait_for_join_complete(guild)
        channel = get(guild.text_channels, name=self.bot.channel_name)

        data = {}
        for cls in self.EXT_CLASSES:
            obj = cls(channel, self.bot)
            await obj.setup()
            data[cls.__name__] = obj
        obj = QueueSettings(channel, self.bot)
        await obj.setup()
        self.queue_settings[guild.id] = obj
        self.contexts[guild.id] = data

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.id == DBOTS_GUILD:
                continue

            info(f"Setting up MusicSettings for guild {guild.name}")
            await self.bot.get_cog('Events').wait_for_ready_complete(guild)
            channel = get(guild.text_channels, name=self.bot.channel_name)
            data = {}
            for cls in self.EXT_CLASSES:
                obj = cls(channel, self.bot)
                await obj.setup()
                data[cls.__name__] = obj
                self.bot._connection._messages.append(
                    obj.msg_object)  # Manually adding it to cache since history() doesn't
            self.contexts[guild.id] = data

            obj = QueueSettings(channel, self.bot)
            await obj.setup()
            self.queue_settings[guild.id] = obj
            self.bot._connection._messages.append(
                obj.msg_object)
        info("MusicSettings finished setting up")


def setup(bot: MusicBot):
    bot.add_cog(MusicSettingsCog(bot))
