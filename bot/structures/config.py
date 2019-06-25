import json
from dataclasses import dataclass, field
from typing import List, Union
import os

DEFAULT_PATH = "./config.json"


@dataclass
class Config:
    prefix: str
    bot_id: int
    token: Union[str, List[str]] = field(default_factory=list)

    @classmethod
    def from_file(cls, file_name: str = DEFAULT_PATH) -> 'Config':
        with open(file_name) as f:
            return cls(**json.load(f))
        
    @classmethod
    def from_environment(cls) -> 'Config':

        # derive a config from a dict
        derived_config = {
            "prefix": os.environ["FLUTE_PREFIX"],
            "bot_id": int(os.environ["FLUTE_BOT_ID"]),
            "token": os.environ["FLUTE_BOT_TOKEN"]
        }

        return cls(**derived_config)
