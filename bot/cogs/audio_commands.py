from typing import Dict

from discord import Guild, VoiceChannel
from discord.abc import GuildChannel
from discord.ext.commands import command, Context

from bot.bot import MusicBot
from bot.structures.audio.voice_context import VoiceContext
from bot.structures.audio.ytdl_source import YTDLSource
from bot.structures.cog import Cog
from utils.logging import debug, info


class Commands(Cog):
    def __init__(self, bot: MusicBot):
        super().__init__(bot)
        self.contexts: Dict[int, VoiceContext] = {}

    @command()
    async def play(self, ctx: Context, *, song: str):
        ct = self.contexts[ctx.guild.id]
        source = YTDLSource(song)
        source.set_requester(ctx.author)
        await source.load()
        await source.load_data(self.bot, ctx)  # WILL MEMORY HOG!
        # TODO: Load_data only when it's in the next 2 songs to play?
        ct.play_source(ctx, source)
        info("Notifying user")
        await ctx.send(f"Added to Queue: {source.title}")

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
