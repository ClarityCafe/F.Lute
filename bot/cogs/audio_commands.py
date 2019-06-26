from typing import Dict

from discord import Guild, VoiceChannel
from discord.abc import GuildChannel
from discord.ext.commands import command, Context

from bot.bot import MusicBot
from bot.structures.audio.voice_context import VoiceContext
from bot.structures.cog import Cog
from utils.audio_tools import load_audio_file
from utils.logging import debug, info


class Commands(Cog):
    def __init__(self, bot: MusicBot):
        super().__init__(bot)
        self.contexts: Dict[int, VoiceContext] = {}

    @command()
    async def play(self, ctx: Context, *, song: str):
        ct = self.contexts[ctx.guild.id]
        source = load_audio_file("/home/mart/git/rpi_audio/music/Kamex_PMD2_DFTTF.flac")  # Use a local file to test
        ct.play_source(ctx, source)

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            info(f"Setting up VoiceContext for guild {guild.name}")
            ctx = VoiceContext()
            self.contexts[guild.id] = ctx
        info("VoiceContext finished setting up")

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        debug(f"Setting up VoiceContext for guild {guild.name}")
        ctx = VoiceContext()
        self.contexts[guild.id] = ctx

    @Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        if channel.name == self.bot.channel_name:
            del self.contexts[channel.guild.id]


def setup(bot: MusicBot):
    bot.add_cog(Commands(bot))
