#!/usr/bin/env python3
"""
Game Systems - Основные игровые системы
"""

# Основные системы
from .evolution.evolution_system import EvolutionSystem
from .combat.combat_system import CombatSystem
from .crafting.crafting_system import CraftingSystem
from .inventory.inventory_system import InventorySystem

# AI система (используется через интерфейс)
from .ai.ai_interface import (
    AISystemInterface, AISystemFactory, AISystemManager,
    AIState, AIPersonality, ActionType, AIDecision, AIEntity
)

# Перечисления и классы данных
from .evolution.evolution_system import (
    EvolutionStage,
    EvolutionType,
    EvolutionStats,
    EvolutionRequirement
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
    "CombatSystem",
    "CraftingSystem",
    "InventorySystem",
    
    # AI система
    "AISystemInterface",
    "AISystemFactory", 
    "AISystemManager",
    "AIState",
    "AIPersonality",
    "ActionType",
    "AIDecision",
    "AIEntity",
    
    # Перечисления и классы данных
    "EvolutionStage",
    "EvolutionType", 
    "EvolutionStats",
    "EvolutionRequirement",
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
