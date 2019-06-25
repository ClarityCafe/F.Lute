from bot.bot import MusicBot
from bot.structures.config import Config

if __name__ == "__main__":
    cfg = Config.from_file("config.json")

    bot = MusicBot(cfg)
    bot.run()
