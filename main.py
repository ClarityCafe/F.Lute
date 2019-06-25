from bot.bot import MusicBot
from bot.structures.config import Config
import os

if __name__ == "__main__":
    
    if not os.path.exists("config.json"):
        cfg = Config.from_environment()
    else:
        cfg = Config.from_file("config.json")

    bot = MusicBot(cfg)
    bot.run()
