import json
from dataclasses import dataclass, field
from typing import List, Union

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
