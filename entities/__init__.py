"""Модуль сущностей игры."""

from .base_entity import BaseEntity
from .player import Player
from .enemy import Enemy
from .entity_factory import EntityFactory
from .effect import Effect

__all__ = [
    'BaseEntity',
    'Player',
    'Enemy',
    'EntityFactory',
    'Effect'
]
