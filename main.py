from bot.bot import MusicBot
from bot.structures.config import Config
import os

if __name__ == "__main__":
    cfg = Config.from_file("./config.json")

    if not os.path.exists("./config.json"):
        # Make sure we also pull from environment
        cfg = Config.from_environment()

    bot = MusicBot(cfg)
    bot.run()
