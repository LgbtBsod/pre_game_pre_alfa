#!/usr/bin/env python3
"""
Entity Package - Системы характеристик и управления сущностями
"""

from .entity_stats_system import (
    EntityType, StatType, BaseStats, StatModifier, EntityStats
)

__all__ = [
    'EntityType', 'StatType', 'BaseStats', 'StatModifier', 'EntityStats'
]
