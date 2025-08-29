#!/usr/bin/env python3
"""
Система социального взаимодействия - управление отношениями между сущностями
"""

from .social_system import SocialSystem
from .social_types import RelationshipType, InteractionType, ReputationType
from .social_data import Relationship, Interaction, Reputation

__all__ = [
    'SocialSystem',
    'RelationshipType',
    'InteractionType',
    'ReputationType',
    'Relationship',
    'Interaction',
    'Reputation'
]
