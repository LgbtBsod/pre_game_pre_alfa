#!/usr/bin/env python3
"""
Game Systems - Основные игровые системы
"""

# Основные системы
from .evolution.evolution_system import EvolutionSystem
from .ai.ai_system import AISystem
from .combat.combat_system import CombatSystem
from .crafting.crafting_system import CraftingSystem
from .inventory.inventory_system import InventorySystem

# Улучшенные системы
from .effects import EffectSystem, TriggerSystem
from .items import EnhancedItemSystem, ItemFactory
from .skills import EnhancedSkillSystem, SkillFactory

# Перечисления и классы данных
from .evolution.evolution_system import (
    EvolutionStage,
    EvolutionType,
    EvolutionStats,
    EvolutionRequirement
)

from .ai.ai_system import (
    AIState,
    AIPersonality,
    ActionType,
    AIDecision,
    AIPattern
)

from .combat.combat_system import (
    CombatState,
    AttackType,
    DamageType as CombatDamageType,
    CombatStats,
    AttackResult,
    CombatAction
)

from .crafting.crafting_system import (
    ItemType,
    ItemRarity,
    CraftingDifficulty,
    Item,
    Recipe,
    CraftingResult
)

from .inventory.inventory_system import (
    ItemCategory,
    InventorySlot,
    Inventory
)

__all__ = [
    # Основные системы
    "EvolutionSystem",
    "AISystem", 
    "CombatSystem",
    "CraftingSystem",
    "InventorySystem",
    
    # Улучшенные системы
    "EffectSystem",
    "TriggerSystem",
    "EnhancedItemSystem",
    "ItemFactory",
    "EnhancedSkillSystem",
    "SkillFactory",
    
    # Перечисления и классы данных
    "EvolutionStage",
    "EvolutionType", 
    "EvolutionStats",
    "EvolutionRequirement",
    "AIState",
    "AIPersonality",
    "ActionType",
    "AIDecision",
    "AIPattern",
    "CombatState",
    "AttackType",
    "CombatDamageType",
    "CombatStats",
    "AttackResult",
    "CombatAction",
    "ItemType",
    "ItemRarity",
    "CraftingDifficulty",
    "Item",
    "Recipe",
    "CraftingResult",
    "ItemCategory",
    "InventorySlot",
    "Inventory"
]
