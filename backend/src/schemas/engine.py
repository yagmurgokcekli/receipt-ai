from enum import Enum


class Engine(str, Enum):
    di = "di"
    openai = "openai"
    compare = "compare"
