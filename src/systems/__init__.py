#!/usr/bin/env python3
"""
Systems Package - Игровые системы
"""

# Импорт существующих систем
from .evolution.evolution_system import EvolutionSystem
from .combat.combat_system import CombatSystem
from .crafting.crafting_system import CraftingSystem
from .inventory.inventory_system import InventorySystem

# Импорт новых систем
from .effects.effect_system import (
    Effect, SpecialEffect, EffectCategory, DamageType, TargetType, TriggerType,
    EffectVisuals, EffectBalance, EffectCondition, HealthCondition, ElementCondition,
    OptimizedTriggerSystem, CombinationSystem, EffectStatistics
)

from .items.item_system import (
    BaseItem, Weapon, Armor, Accessory, Consumable, ItemFactory,
    ItemRarity, ItemType, ItemStats
)

from .skills.skill_system import (
    Skill, CombatSkill, UtilitySkill, SkillTree, SkillFactory,
    SkillType, SkillTarget, SkillRequirements, SkillCooldown
)

from .ai.ai_entity import (
    AIEntity, EntityType, MemoryType, MemoryEntry, GenerationMemory
)

from .genome.genome_system import (
    Gene, Chromosome, Genome, GenomeManager, genome_manager,
    GeneType, GeneDominance
)

# Экспорт всех систем
__all__ = [
    # Существующие системы
    'EvolutionSystem',
    'CombatSystem', 
    'CraftingSystem',
    'InventorySystem',
    
    # Система эффектов
    'Effect',
    'SpecialEffect',
    'EffectCategory',
    'DamageType',
    'TargetType',
    'TriggerType',
    'EffectVisuals',
    'EffectBalance',
    'EffectCondition',
    'HealthCondition',
    'ElementCondition',
    'OptimizedTriggerSystem',
    'CombinationSystem',
    'EffectStatistics',
    
    # Система предметов
    'BaseItem',
    'Weapon',
    'Armor',
    'Accessory',
    'Consumable',
    'ItemFactory',
    'ItemRarity',
    'ItemType',
    'ItemStats',
    
    # Система скиллов
    'Skill',
    'CombatSkill',
    'UtilitySkill',
    'SkillTree',
    'SkillFactory',
    'SkillType',
    'SkillTarget',
    'SkillRequirements',
    'SkillCooldown',
    
    # Система AI Entity
    'AIEntity',
    'EntityType',
    'MemoryType',
    'MemoryEntry',
    'GenerationMemory',
    
    # Система генома
    'Gene',
    'Chromosome',
    'Genome',
    'GenomeManager',
    'genome_manager',
    'GeneType',
    'GeneDominance'
]
