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
    Skill, CombatSkill, UtilitySkill, SkillTree,
    SkillType, SkillTarget, SkillRequirements, SkillCooldown
)

from .ai.ai_entity import (
    AIEntity, EntityType, MemoryType, MemoryEntry, GenerationMemory
)

from .ai.ai_system import (
    AISystem, EmotionType, PersonalityType, Memory, Emotion, Personality
)

from .ai.pytorch_ai_system import PyTorchAISystem, NeuralNetwork, EmotionalNetwork

from .ai.ai_integration_system import AIIntegrationSystem, AIAgentState

from .genome.genome_system import (
    Gene, Chromosome, Genome, GenomeManager, genome_manager,
    GeneType, GeneDominance
)

from .emotion.emotion_system import (
    Emotion, EmotionSystem, EmotionManager, emotion_manager,
    EmotionType
)

from .entity.entity_stats_system import (
    EntityType as GameEntityType, StatType, BaseStats, StatModifier, EntityStats
)

from .content.content_database import (
    ContentDatabase, ContentItem, ContentType, ContentRarity,
    EnemyData, BossData, EnemyType, BossType, DamageType as ContentDamageType
)

from .content.content_generator import ContentGenerator, GenerationConfig

from .content.content_constants import (
    ENEMY_CONSTANTS, BOSS_CONSTANTS, ITEM_CONSTANTS,
    RANDOM_GENERATOR, GenerationBiome, GenerationTime, GenerationWeather
)

# Экспорт всех систем
__all__ = [
    # Основные системы
    'EvolutionSystem', 'CombatSystem', 'CraftingSystem', 'InventorySystem',
    
    # Система эффектов
    'Effect', 'SpecialEffect', 'EffectCategory', 'DamageType', 'TargetType', 'TriggerType',
    'EffectVisuals', 'EffectBalance', 'EffectCondition', 'HealthCondition', 'ElementCondition',
    'OptimizedTriggerSystem', 'CombinationSystem', 'EffectStatistics',
    
    # Система предметов
    'BaseItem', 'Weapon', 'Armor', 'Accessory', 'Consumable', 'ItemFactory',
    'ItemRarity', 'ItemType', 'ItemStats',
    
    # Система скиллов
    'Skill', 'CombatSkill', 'UtilitySkill', 'SkillTree',
    'SkillType', 'SkillTarget', 'SkillRequirements', 'SkillCooldown',
    
    # AI системы
    'AIEntity', 'EntityType', 'MemoryType', 'MemoryEntry', 'GenerationMemory',
    'AISystem', 'EmotionType', 'PersonalityType', 'Memory', 'Emotion', 'Personality',
    'PyTorchAISystem', 'NeuralNetwork', 'EmotionalNetwork',
    'AIIntegrationSystem', 'AIAgentState',
    
    # Система генома
    'Gene', 'Chromosome', 'Genome', 'GenomeManager', 'genome_manager',
    'GeneType', 'GeneDominance',
    
    # Система эмоций
    'Emotion', 'EmotionSystem', 'EmotionManager', 'emotion_manager',
    'EmotionType',
    
    # Система характеристик сущностей
    'GameEntityType', 'StatType', 'BaseStats', 'StatModifier', 'EntityStats',
    
    # Система контента
    'ContentDatabase', 'ContentItem', 'ContentType', 'ContentRarity',
    'EnemyData', 'BossData', 'EnemyType', 'BossType', 'ContentDamageType',
    'ContentGenerator', 'GenerationConfig',
    'ENEMY_CONSTANTS', 'BOSS_CONSTANTS', 'ITEM_CONSTANTS',
    'RANDOM_GENERATOR', 'GenerationBiome', 'GenerationTime', 'GenerationWeather'
]
