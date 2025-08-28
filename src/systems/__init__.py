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
    Effect, SpecialEffect, EffectCategory, DamageType, TriggerType
)

from .items.item_system import (
    Item, SpecialEffect, ItemSystem,
    ItemRarity, ItemType
)

from .skills.skill_system import (
    Skill, SkillRequirements, SkillCooldown, SkillSystem
)

from .ai.unified_ai_system import (
    UnifiedAISystem, EntityType, MemoryType, MemoryEntry, AIDecision,
    AIConfig, Personality, NeuralNetwork, EmotionalNetwork
)

from .genome.genome_system import (
    GeneSequence, GeneticTrait, GenomeProfile, GenomeSystem
)

from .emotion.emotion_system import (
    Emotion, EmotionalState, EmotionalTrigger, EmotionSystem
)

from .entity.entity_stats_system import (
    StatModifier, EntityStats, EntityStatsSystem
)

from .content.content_database import (
    ContentDatabase, ContentItem, ContentSlot, ContentSession
)

from .content.content_generator import ContentGenerator, GenerationConfig, EnemyData, BossData



# Экспорт всех систем
__all__ = [
    # Основные системы
    'EvolutionSystem', 'CombatSystem', 'CraftingSystem', 'InventorySystem',
    
    # Система эффектов
    'Effect', 'SpecialEffect', 'EffectCategory', 'DamageType', 'TriggerType',
    
    # Система предметов
    'Item', 'SpecialEffect', 'ItemSystem',
    'ItemRarity', 'ItemType',
    
    # Система скиллов
    'Skill', 'SkillRequirements', 'SkillCooldown', 'SkillSystem',
    
    # AI системы
    'UnifiedAISystem', 'EntityType', 'MemoryType', 'MemoryEntry', 'AIDecision',
    'AIConfig', 'Personality', 'NeuralNetwork', 'EmotionalNetwork',
    
    # Система генома
    'GeneSequence', 'GeneticTrait', 'GenomeProfile', 'GenomeSystem',
    
    # Система эмоций
    'Emotion', 'EmotionalState', 'EmotionalTrigger', 'EmotionSystem',
    
    # Система характеристик сущностей
    'StatModifier', 'EntityStats', 'EntityStatsSystem',
    
    # Система контента
    'ContentDatabase', 'ContentItem', 'ContentSlot', 'ContentSession',
    'ContentGenerator', 'GenerationConfig', 'EnemyData', 'BossData',

]
