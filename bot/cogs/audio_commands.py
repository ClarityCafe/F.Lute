from discord.ext.commands import command

from bot.structures.cog import Cog


class Commands(Cog):
    @command()
    async def play(self, *, song: str):
        # TODO: Look up song
        # For now, use a local file
        # in my case '../rpi_audio/music/Kamex_PMD2_DFTTF.flac'
        ...

