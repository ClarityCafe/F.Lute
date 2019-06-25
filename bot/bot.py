from discord.ext.commands import Bot, when_mentioned_or

from bot.structures.config import Config


class MusicBot(Bot):
    __cogs = (
        "bot.cogs.events",
        "bot.cogs.role_access",
        "bot.cogs.voice_channel"
    )

    def __init__(self, cfg: Config):
        if isinstance(cfg.prefix, str):
            super().__init__(when_mentioned_or(cfg.prefix))
        else:
            super().__init__(when_mentioned_or(*cfg.prefix))

        self.token = cfg.token

        for cog in self.__cogs:
            self.load_extension(cog)

    def run(self):
        return super().run(self.token)
