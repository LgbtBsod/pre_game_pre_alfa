"""
Основной модуль игровых систем.
Содержит все ключевые компоненты для эволюционной адаптации.
"""

# Основные системы
from .effect_system import (
    EffectType, EffectCode, Effect, EffectDatabase, 
    ActiveEffect, EffectSystem
)

from .genetic_system import (
    GeneCode, MutationType, Gene, GeneticAnomaly, 
    AdvancedGeneticSystem
)

from .emotion_system import (
    EmotionCode, EmotionIntensity, Emotion, 
    EmotionalState, AdvancedEmotionSystem
)

from .ai_system import (
    ActionType, AIState, AIAction, AIPersonality, 
    QLearningAgent, AdaptiveAISystem
)

from .content_generator import (
    BiomeType, EnemyType, WeaponType, ItemRarity,
    GeneratedEnemy, GeneratedWeapon, GeneratedItem, 
    GeneratedWorld, ContentGenerator
)

from .evolution_system import (
    EvolutionStage, EvolutionBonusType, EvolutionBonus, EvolutionData, 
    EvolutionPath, EvolutionCycleSystem
)

from .advanced_entity import (
    EntityType, DamageType, EntityStats, EntityPosition,
    AdvancedGameEntity, PygameGameEntity
)

# Игровой цикл теперь в refactored_game_loop.py

from .global_event_system import (
    EventType, EventSeverity, EventCategory, 
    GlobalEvent, EventTrigger, GlobalEventSystem
)

from .dynamic_difficulty import (
    DifficultyLevel, DifficultyFactor, DifficultyParameter,
    PlayerPerformance, DifficultyProfile, DynamicDifficultySystem
)

from .combat_learning_system import (
    CombatAction, VulnerabilityType, EnemyVulnerability,
    WeaponEffectiveness, ItemUsagePattern, CombatLearningSystem
)

from .advanced_weapon_system import (
    WeaponType as WeaponSystemType, DamageType as WeaponDamageType,
    WeaponRarity as WeaponSystemRarity, WeaponStats, WeaponEnhancement,
    AdvancedWeapon, WeaponFactory, WeaponManager
)

from .skill_system import (
    SkillType, SkillElement, SkillTarget, SkillRequirement,
    SkillEffect, SkillCombo, Skill, SkillManager, SkillLearningAI
)

from .enhanced_combat_ai import (
    CombatPhase, CombatTactic, EnhancedCombatContext,
    CombatDecision, EnhancedCombatAI
)

from .database_manager import DatabaseManager, database_manager

# Основные классы для импорта
__all__ = [
    # Системы эффектов
    'EffectType', 'EffectCode', 'Effect', 'EffectDatabase', 
    'ActiveEffect', 'EffectSystem',
    
    # Генетическая система
    'GeneCode', 'MutationType', 'Gene', 'GeneticAnomaly', 
    'AdvancedGeneticSystem',
    
    # Эмоциональная система
    'EmotionCode', 'EmotionIntensity', 'Emotion', 
    'EmotionalState', 'AdvancedEmotionSystem',
    
    # ИИ система
    'ActionType', 'AIState', 'AIAction', 'AIPersonality', 
    'QLearningAgent', 'AdaptiveAISystem',
    
    # Генератор контента
    'BiomeType', 'EnemyType', 'WeaponType', 'ItemRarity',
    'GeneratedEnemy', 'GeneratedWeapon', 'GeneratedItem', 
    'GeneratedWorld', 'ContentGenerator',
    
    # Система эволюции
    'EvolutionStage', 'EvolutionBonus', 'EvolutionData', 
    'EvolutionPath', 'EvolutionCycleSystem',
    
    # Игровые сущности
    'EntityType', 'DamageType', 'EntityStats', 'EntityPosition',
    'AdvancedGameEntity', 'PygameGameEntity',
    
    # Игровой цикл (теперь в refactored_game_loop.py)
    
    # Глобальные события
    'EventType', 'EventSeverity', 'EventCategory', 
    'GlobalEvent', 'EventTrigger', 'GlobalEventSystem',
    
    # Динамическая сложность
    'DifficultyLevel', 'DifficultyFactor', 'DifficultyParameter',
    'PlayerPerformance', 'DifficultyProfile', 'DynamicDifficultySystem',
    
    # Боевое обучение
    'CombatAction', 'VulnerabilityType', 'EnemyVulnerability',
    'WeaponEffectiveness', 'ItemUsagePattern', 'CombatLearningSystem',
    
    # Система оружия
    'WeaponSystemType', 'WeaponDamageType', 'WeaponSystemRarity',
    'WeaponStats', 'WeaponEnhancement', 'AdvancedWeapon', 
    'WeaponFactory', 'WeaponManager',
    
    # Система навыков
    'SkillType', 'SkillElement', 'SkillTarget', 'SkillRequirement',
    'SkillEffect', 'SkillCombo', 'Skill', 'SkillManager', 'SkillLearningAI',
    
    # Улучшенный боевой ИИ
    'CombatPhase', 'CombatTactic', 'EnhancedCombatContext',
    'CombatDecision', 'EnhancedCombatAI',
    
    # Менеджер базы данных
    'DatabaseManager', 'database_manager',
]
