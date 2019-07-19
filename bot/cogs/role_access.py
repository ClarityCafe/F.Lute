from typing import Dict

from discord import Guild, TextChannel, Member, Reaction, Role
from discord.abc import GuildChannel
from discord.utils import get

from bot.bot import MusicBot
from bot.cogs.events import DBOTS_GUILD
from bot.structures.cog import Cog
from bot.structures.menu import MenuContext, event_class, event
from utils.logging import info, debug


@event_class
class RoleAccess(MenuContext):
    id = "Role Access"

    def __init__(self, channel: TextChannel, bot: MusicBot):
        self.selected_role = channel.guild.default_role
        self.all_roles = channel.guild.roles[::-1]
        super().__init__(channel, bot)

    async def setup(self):
        await super().setup()
        await self.update_roles()

    async def refresh_role_list(self):
        self.all_roles = self.channel.guild.roles[::-1]
        if self.selected_role not in self.all_roles:
            self.selected_role = self.channel.guild.default_role
        await self.update_roles()

    async def update_roles(self):
        roles = "\n".join(f"{'->'[role == self.selected_role]} {role.name.replace('@', '[@]')}"
                          for role in self.channel.guild.roles[::-1])

        await self.set_message(
            (f"""
Select a role that's allowed to use commands:
{roles}
            """).strip()
        )

    async def load(self):
        content = self.msg_object.content
        message = content[7 + len(self.id):-3]
        lines = message.split("\n")
        role_name = ""
        for line in lines[1:]:
            if line.startswith("> "):
                role_name = line[2:]
                break

        self.selected_role = get(self.channel.guild.roles, name=role_name) or self.channel.guild.default_role

    @event("\N{UP-POINTING SMALL RED TRIANGLE}")
    async def select_up(self):
        index = self.all_roles.index(self.selected_role)
        new_index = max(0, index - 1)
        self.selected_role = self.all_roles[new_index]
        await self.update_roles()

    @event("\N{DOWN-POINTING SMALL RED TRIANGLE}")
    async def select_down(self):
        index = self.all_roles.index(self.selected_role)
        new_index = min(len(self.all_roles) - 1, index + 1)
        self.selected_role = self.all_roles[new_index]
        await self.update_roles()

    @event("\N{BLACK UP-POINTING DOUBLE TRIANGLE}")
    async def first(self):
        self.selected_role = self.all_roles[0]
        await self.update_roles()

    @event("\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}")
    async def last(self):
        self.selected_role = self.all_roles[len(self.all_roles) - 1]
        await self.update_roles()


class RoleAccessCog(Cog):
    def __init__(self, bot: MusicBot):
        super().__init__(bot)
        self.contexts: Dict[int, RoleAccess] = {}

    def get_access_role(self, guild: Guild):
        return self.contexts[guild.id].selected_role

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member):
        if not isinstance(user, Member) or user.bot:
            return

        ctx = self.contexts[user.guild.id]
        await ctx.on_reaction_add(reaction, user)

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.id == DBOTS_GUILD:
                continue

            info(f"Setting up RoleAccess for guild {guild.name}")
            await self.bot.get_cog('Events').wait_for_ready_complete(guild)
            channel = get(guild.text_channels, name=self.bot.channel_name)
            ctx = RoleAccess(channel, self.bot)
            await ctx.setup()
            self.contexts[guild.id] = ctx
            self.bot._connection._messages.append(ctx.msg_object)  # Manually adding it to cache since history() doesn't
        info("RoleAccess finished setting up")

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        debug(f"Setting up RoleAccess for guild {guild.name}")

        await self.bot.get_cog('Events').wait_for_join_complete(guild)
        channel = get(guild.text_channels, name=self.bot.channel_name)

        ctx = RoleAccess(channel, self.bot)
        await ctx.setup()
        self.contexts[guild.id] = ctx

    @Cog.listener()
    async def on_guild_role_create(self, role: Role):
        if role.guild.id in self.contexts:
            await self.contexts[role.guild.id].refresh_role_list()

    @Cog.listener()
    async def on_guild_role_delete(self, role: Role):
        if role.guild.id in self.contexts:
            await self.contexts[role.guild.id].refresh_role_list()

    @Cog.listener()
    async def on_guild_role_update(self, before: Role, after: Role):
        if after.guild.id in self.contexts:
            await self.contexts[after.guild.id].refresh_role_list()

    @Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        if channel.name == self.bot.channel_name:
            del self.contexts[channel.guild.id]


def setup(bot: MusicBot):
    bot.add_cog(RoleAccessCog(bot))
