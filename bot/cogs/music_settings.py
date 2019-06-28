from typing import Dict

from discord import Member, Reaction, Guild
from discord.utils import get

from bot.bot import MusicBot
from bot.structures.cog import Cog
from bot.structures.menu import MenuContext, event
from dsp.audio_object import AudioSequence
from dsp.modules import VolumeModule, PanModule
from utils.logging import info, debug


class MusicSettings(MenuContext):
    def __init__(self):
        self.enabled = False
        self.fx = None

    def process(self, audio: AudioSequence) -> AudioSequence:
        return audio

    @event("\N{WHITE HEAVY CHECK MARK}")
    def enable(self):
        self.enabled = True

    @event("\N{NEGATIVE SQUARED CROSS MARK}")
    def enable(self):
        self.enabled = False

    """
    
    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        await self.update()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        await self.update()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        await self.update()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        await self.update()
    """


class VolumeSettings(MusicSettings):
    def __init__(self):
        super().__init__()
        self.fx = VolumeModule()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        await self.set_message(f"""
Enabled: {self.enabled}
Volume: {self.fx.volume}dB
        """)

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines[1:]:
            if line.startswith("Enabled: "):
                self.enabled = line.endswith("True")
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


class PanSettings(MusicSettings):
    def __init__(self):
        super().__init__()
        self.fx = PanModule()

    def process(self, audio: AudioSequence) -> AudioSequence:
        return self.fx.process(audio)

    async def update(self):
        await self.set_message(f"""
Enabled: {self.enabled}
Pan: {self.fx.angle} degrees
        """)

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        for line in lines[1:]:
            if line.startswith("Enabled: "):
                self.enabled = line.endswith("True")
            elif line.startswith("Pan: "):
                self.fx.volume = float(line[5:-8])

    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        self.fx.volume = min(self.fx.angle+1, 45)
        await self.update()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        self.fx.volume = max(self.fx.angle - 1, -45)
        await self.update()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        self.fx.volume = min(self.fx.angle + 5, 45)
        await self.update()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        self.fx.volume = max(self.fx.angle - 5, -45)
        await self.update()


class MusicSettingsCog(Cog):
    EXT_CLASSES = (VolumeSettings, PanSettings)

    def __init__(self, bot: MusicBot):
        super().__init__(bot)
        self.contexts: Dict[int, Dict[str, MusicSettings]] = {}

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member):
        if not isinstance(user, Member) or user.bot:
            return

        ctx = self.contexts[user.guild.id]
        for name, ct in ctx.items():
            await ct.on_reaction_add(reaction, user)

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
        self.contexts[guild.id] = data

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
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
        info("MusicSettings finished setting up")


def setup(bot: MusicBot):
    bot.add_cog(MusicSettingsCog(bot))
