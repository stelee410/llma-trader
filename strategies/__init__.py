from .base import BaseStrategy
from .dry_strategies import DryStrategy
from .openai_strategies import OpenAIStrategy

def load_strategy(name):
    mapping = {
        "dry": DryStrategy,
        "openai": OpenAIStrategy
    }
    if name not in mapping:
        raise ValueError('invalid strategy name')
    return mapping[name]

__all__ = ['load_strategy']
