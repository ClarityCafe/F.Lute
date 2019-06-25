import json
from dataclasses import dataclass, field
from typing import List, Union
import os

DEFAULT_PATH = "./config.json"


@dataclass
class Config:
    bot_id: int
    token: str
    channel_name: str
    prefix: List[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, file_name: str = DEFAULT_PATH) -> 'Config':
        with open(file_name) as f:
            return cls(**json.load(f))
        
    @classmethod
    def from_environment(cls) -> 'Config':

        # derive a config from a dict
        return cls(
            prefix=os.environ["FLUTE_PREFIX"].split(":"),
            bot_id=int(os.environ["FLUTE_BOT_ID"]),
            token=os.environ["FLUTE_BOT_TOKEN"],
            channel_name=os.environ["FLUTE_CHANNEL_NAME"]
        )
