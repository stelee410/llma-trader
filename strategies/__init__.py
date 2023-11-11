from .base import BaseStrategy
from .dry_strategies import DryStrategy
from .openai_strategies import OpenAIStrategy
from .openai_f_strategies import OpenAIFutureStrategy

def load_strategy(name):
    mapping = {
        "dry": DryStrategy,
        "openai": OpenAIStrategy,
        "openaif": OpenAIFutureStrategy
    }
    if name not in mapping:
        raise ValueError('invalid strategy name')
    return mapping[name]

__all__ = ['load_strategy']
