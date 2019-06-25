from bot.bot import MusicBot
from bot.structures.config import Config
import os

if __name__ == "__main__":
    
    if os.path.exists("./config.json"):
        cfg = Config.from_file("./config.json")
    else:
        cfg = Config.from_environment()

    bot = MusicBot(cfg)
    bot.run()
