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
    async def playlist(self, ctx: Context):
        """ Fetches the playlist """
        queue = self.contexts[ctx.guild.id].queue
        songs = queue.list()
        await ctx.send("\n".join(f"{song.title} - Requested by {song.requester.name}" for song in songs[:10]))

    @command()
    async def skip(self, ctx: Context):
        """ Skips the currently playing song """

        if self.bot.get_cog("RoleAccessCog").get_access_role(ctx.guild) not in ctx.author.roles:
            return await ctx.send("You do not have the role configured to skip songs!")

        self.contexts[ctx.guild.id].source.current_source.skip()
        await ctx.send("Skipping song!")

    @command()
    async def play(self, ctx: Context, *, song: str):
        """ Plays a song """
        async with ctx.typing():
            if self.bot.get_cog("RoleAccessCog").get_access_role(ctx.guild) not in ctx.author.roles:
                return await ctx.send("You do not have the role configured to play songs!")

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
