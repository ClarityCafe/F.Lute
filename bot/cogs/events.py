from asyncio import Event
from typing import Dict

from discord import Guild, PermissionOverwrite
from discord.abc import GuildChannel
from discord.utils import get

from bot.bot import MusicBot
from bot.structures.cog import Cog
from utils.logging import debug


DBOTS_GUILD = 110373943822540800


class Events(Cog):
    join_locks: Dict[int, Event] = {}
    ready_locks: Dict[int, Event] = {}

    @staticmethod
    def permission_check(guild: Guild):
        permissions = guild.me.guild_permissions
        return True
        # return permissions.manage_channels and permissions.manage_messages

    async def wait_for_join_complete(self, guild: Guild):
        if guild.id not in self.join_locks:
            self.join_locks[guild.id] = Event()
        await self.join_locks[guild.id].wait()

    async def wait_for_ready_complete(self, guild: Guild):
        if guild.id not in self.ready_locks:
            self.ready_locks[guild.id] = Event()
        await self.ready_locks[guild.id].wait()

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            # If it got added to a guild that keeps crashing, log the invite
            # print(guild.name, await guild.channels[0].create_invite())
            if guild.id not in self.ready_locks:
                self.ready_locks[guild.id] = Event()

            if guild.id != DBOTS_GUILD:
                channel = get(guild.text_channels, name=self.bot.channel_name)
                if channel is None:
                    await self.on_guild_join(guild)
                    continue
            self.ready_locks[guild.id].set()

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        if guild.id not in self.join_locks:
            self.join_locks[guild.id] = Event()

        if guild.id == DBOTS_GUILD:
            return

        debug(f"Setting up Configuration for guild {guild.name}")

        if not self.permission_check(guild):
            await guild.text_channels[0].send("I don't have the correct permissions, make sure manage_channels and"
                                              " manage_messages are enabled.")
            await guild.leave()
            return

        overwrites = {
            guild.default_role: PermissionOverwrite(read_messages=False),
            guild.me: PermissionOverwrite(read_messages=True, manage_messages=True),
            **{role: PermissionOverwrite(read_messages=True)
               for role in guild.roles
               if role.permissions.manage_channels}
        }

        channel = await guild.create_text_channel(
            self.bot.channel_name,
            overwrites=overwrites,
            topic="This is the configuration channel for f-lute, please do NOT delete this, or the bot will leave"
        )

        self.join_locks[guild.id].set()

    @Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        if channel.name == self.bot.channel_name:
            await channel.guild.leave()


def setup(bot: MusicBot):
    bot.add_cog(Events(bot))
