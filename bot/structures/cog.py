from discord.ext import commands

from bot.bot import MusicBot


class Cog(commands.Cog):
    def __init__(self, bot: MusicBot):
        self.bot = bot
