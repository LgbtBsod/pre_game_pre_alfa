"""Модуль сущностей игры."""

from .entity import Entity
from .entity_refactored import Entity as EntityRefactored
from .player import Player
from .enemy import Enemy, EnemyGenerator
from .boss import Boss, BossGenerator
from .npc import NPCEnemy
from .entity_factory import EntityFactory
from .effect import Effect

__all__ = [
    'Entity',
    'EntityRefactored',
    'Player',
    'Enemy',
    'EnemyGenerator',
    'Boss',
    'BossGenerator',
    'NPCEnemy',
    'EntityFactory',
    'Effect'
]
