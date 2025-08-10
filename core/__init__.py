"""Основные системы игры."""

from .ai_update_scheduler import AIUpdateScheduler
from .attributes import AttributeManager, Attribute
from .combat_stats import CombatStatsManager, CombatStats
from .data_manager import DataManager
from .game_logic_manager import GameLogicManager
from .game_state_manager import GameStateManager
from .inventory import InventoryManager, Inventory, Equipment, EquipmentSlot
from .leveling_system import LevelingSystem
from .skill_system import SkillSystem
from .transform import TransformComponent

__all__ = [
    "AIUpdateScheduler",
    "AttributeManager",
    "Attribute",
    "CombatStatsManager",
    "CombatStats",
    "DataManager",
    "GameLogicManager",
    "GameStateManager",
    "InventoryManager",
    "Inventory",
    "Equipment",
    "EquipmentSlot",
    "LevelingSystem",
    "SkillSystem",
    "TransformComponent",
]
