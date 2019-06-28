from typing import Dict

from discord import Member, Reaction, Guild
from discord.utils import get

from bot.bot import MusicBot
from bot.structures.cog import Cog
from bot.structures.menu import MenuContext
from dsp.audio_object import AudioSequence
from utils.logging import info, debug


class MusicSettings(MenuContext):
    def __init__(self):
        self.enabled = False

    def process(self, audio: AudioSequence) -> AudioSequence:
        return audio


class MusicSettingsCog(Cog):
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
        # ctx = VoiceChannel(channel, self.bot)
        # await ctx.setup()
        # self.contexts[guild.id] = ctx
        self.contexts[guild.id] = data

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            info(f"Setting up MusicSettings for guild {guild.name}")
            await self.bot.get_cog('Events').wait_for_ready_complete(guild)
            channel = get(guild.text_channels, name=self.bot.channel_name)
            data = {}
            # ctx = VoiceChannel(channel, self.bot)
            # await ctx.setup()
            # self.contexts[guild.id] = ctx
            self.contexts[guild.id] = data
            # self.bot._connection._messages.append(ctx.msg_object)  # Manually adding it to cache since history() doesn't
        info("MusicSettings finished setting up")


def setup(bot: MusicBot):
    bot.add_cog(MusicSettingsCog(bot))
