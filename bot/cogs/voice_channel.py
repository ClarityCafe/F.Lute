from typing import Dict

from discord import Guild, PermissionOverwrite, TextChannel, Member, Reaction, Role
from discord.abc import GuildChannel
from discord.utils import get

from bot.bot import MusicBot
from bot.structures.cog import Cog
from bot.structures.menu import MenuContext, event_class, event
from utils.logging import info, debug, warn


@event_class
class VoiceChannel(MenuContext):
    id = "Voice Channel"

    def __init__(self, channel: TextChannel):
        try:
            self.selected_channel = channel.guild.voice_channels[0]
        except IndexError:
            self.selected_channel = None
        self.all_channels = channel.guild.voice_channels[::-1]
        super().__init__(channel)

    async def setup(self):
        if self.selected_channel is None:
            await self.get_default_vc()
        await super().setup()
        await self.update_channels()

    async def get_default_vc(self):
        try:
            self.selected_channel = self.channel.guild.voice_channels[0]
        except IndexError:
            self.selected_channel = await self.channel.guild.create_voice_channel(
                "Flute Music",
                overwrites={
                    self.channel.guild.default_role: PermissionOverwrite(speak=False),
                    self.channel.guild.me: PermissionOverwrite(speak=True),
                }
            )

    async def refresh_role_list(self):
        self.all_channels = self.channel.guild.roles[::-1]
        if self.selected_channel not in self.all_channels:
            await self.get_default_vc()
        await self.update_channels()

    async def update_channels(self):
        channels = "\n".join(f"{'->'[channel == self.selected_channel]} {channel.name.replace('@', '[@]')}"
                             for channel in self.channel.guild.voice_channels[::-1])

        await self.set_message(
            (f"""
Select a voice channel for me to occupy:
{channels}
            """).strip()
        )

    async def load(self):
        content = self.msg_object.content
        message = content[7+len(self.id):-3]
        lines = message.split("\n")
        channel_name = ""
        for line in lines[1:]:
            if line.startswith("> "):
                channel_name = line[2:]
                break

        self.selected_channel = get(self.channel.guild.voice_channels, name=channel_name)

    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        index = self.all_channels.index(self.selected_channel)
        new_index = max(0, index - 1)
        self.selected_channel = self.all_channels[new_index]
        await self.update_channels()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        index = self.all_channels.index(self.selected_channel)
        new_index = min(len(self.all_channels) - 1, index + 1)
        self.selected_channel = self.all_channels[new_index]
        await self.update_channels()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        self.selected_channel = self.all_channels[0]
        await self.update_channels()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        self.selected_channel = self.all_channels[len(self.all_channels) - 1]
        await self.update_channels()


class VoiceChannelCog(Cog):
    def __init__(self, bot: MusicBot):
        super().__init__(bot)
        self.contexts: Dict[int, VoiceChannel] = {}

    def get_voice_channel(self, guild: Guild):
        return self.contexts[guild.id].selected_channel

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member):
        if not isinstance(user, Member) or user.bot:
            return

        ctx = self.contexts[user.guild.id]
        await ctx.on_reaction_add(reaction, user)

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            info(f"Setting up VoiceChannel for guild {guild.name}")
            await self.bot.get_cog('Events').wait_for_ready_complete(guild)
            channel = get(guild.text_channels, name="flute-configuration")
            ctx = VoiceChannel(channel)
            await ctx.setup()
            self.contexts[guild.id] = ctx
            self.bot._connection._messages.append(ctx.msg_object)  # Manually adding it to cache since history() doesn't
        info("VoiceChannel finished setting up")

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        debug(f"Setting up VoiceChannel for guild {guild.name}")

        await self.bot.get_cog('Events').wait_for_join_complete(guild)
        channel = get(guild.text_channels, name="flute-configuration")

        ctx = VoiceChannel(channel)
        await ctx.setup()
        self.contexts[guild.id] = ctx

    @Cog.listener()
    async def on_guild_channel_create(self, channel: GuildChannel):
        if isinstance(channel, VoiceChannel) and channel.guild.id in self.contexts:
            await self.contexts[channel.guild.id].refresh_role_list()

    @Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        if isinstance(channel, VoiceChannel) and channel.guild.id in self.contexts:
            await self.contexts[channel.guild.id].refresh_role_list()
        elif channel.name == "flute-configuration":
            del self.contexts[channel.guild.id]

    @Cog.listener()
    async def on_guild_channel_update(self, before: GuildChannel, after: GuildChannel):
        if isinstance(after, VoiceChannel) and after.guild.id in self.contexts:
            await self.contexts[after.guild.id].refresh_role_list()


def setup(bot: MusicBot):
    bot.add_cog(VoiceChannelCog(bot))
