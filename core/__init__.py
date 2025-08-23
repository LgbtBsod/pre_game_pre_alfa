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

try:
    from .skill_system import (
        SkillType, SkillElement, SkillTarget, SkillRequirement,
        SkillEffect, SkillCombo, Skill, SkillManager, SkillLearningAI
    )
except ImportError as e:
    # Fallback imports for missing components
    from .skill_system import SkillType, SkillElement
    SkillTarget = None
    SkillRequirement = None
    SkillEffect = None 
    SkillCombo = None
    Skill = None
    SkillManager = None
    SkillLearningAI = None

from .enhanced_combat_ai import (
    CombatPhase, CombatTactic, EnhancedCombatContext,
    CombatDecision, EnhancedCombatAI
)

# Новые системы
from .generational_memory_system import (
    MemoryType, MemoryIntensity, GenerationalMemory, 
    MemoryCluster, GenerationalMemorySystem
)

from .emotional_ai_influence import (
    EmotionalInfluenceType, EmotionalModifier, EmotionalAIState,
    EmotionalAIInfluenceSystem
)

from .enhanced_combat_learning import (
    CombatPhase as CombatLearningPhase, CombatTactic as CombatLearningTactic,
    CombatContext, CombatDecision as CombatLearningDecision,
    EnhancedCombatLearningSystem
)

from .trap_and_hazard_system import (
    HazardType, TrapType, ChestType, HazardDifficulty,
    HazardPattern, GeneratedHazard, ChestReward, GeneratedChest,
    TrapAndHazardSystem
)

from .database_manager import DatabaseManager, database_manager

# Дополнительные системы
from .trading_system import TradingSystem, ItemCategory, TradeType
from .social_system import SocialSystem, RelationshipType, NPCPersonality
from .quest_system import QuestSystem, QuestType, QuestStatus
from .crafting_system import CraftingSystem, CraftingRecipe, CraftingStation
from .computer_vision_system import ComputerVisionSystem, VisionAction
from .object_creation_system import ObjectCreationSystem, ObjectType
from .secure_database import SecureDatabase
from .spatial_system import SpatialSystem, SpatialIndex
from .session_manager import SessionManager, UserSession
from .event_system import EventSystem, EventPriority

# Новые системы Enhanced Edition
from .curse_blessing_system import (
    CurseType, BlessingType, CurseBlessingEffect, CurseBlessingSystem
)

from .risk_reward_system import (
    RiskLevel, RiskCategory, RiskFactor, RiskRewardEvent, RiskRewardSystem
)

from .meta_progression_system import (
    MetaCurrency, MetaUpgrade, InheritanceTrait, Achievement, MetaProgressionSystem
)

from .enhanced_content_generator import EnhancedContentGenerator

from .enhanced_skill_system import (
    SkillManager, SkillLearningAI
)

from .enhanced_inventory_system import EnhancedInventorySystem

from .enhanced_ui_system import EnhancedUISystem, UIState

from .enhanced_game_master import (
    GamePhase, DifficultyMode, GameSession, EnhancedGameMaster
)

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
    'EvolutionStage', 'EvolutionBonusType', 'EvolutionBonus', 'EvolutionData', 
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
    
    # Новые системы
    'MemoryType', 'MemoryIntensity', 'GenerationalMemory', 
    'MemoryCluster', 'GenerationalMemorySystem',
    
    'EmotionalInfluenceType', 'EmotionalModifier', 'EmotionalAIState',
    'EmotionalAIInfluenceSystem',
    
    'CombatLearningPhase', 'CombatLearningTactic', 'CombatContext', 
    'CombatLearningDecision', 'EnhancedCombatLearningSystem',
    
    'HazardType', 'TrapType', 'ChestType', 'HazardDifficulty',
    'HazardPattern', 'GeneratedHazard', 'ChestReward', 'GeneratedChest',
    'TrapAndHazardSystem',
    
    # Менеджер базы данных
    'DatabaseManager', 'database_manager',
    
    # Дополнительные системы
    'TradingSystem', 'ItemCategory', 'TradeType',
    'SocialSystem', 'RelationshipType', 'NPCPersonality',
    'QuestSystem', 'QuestType', 'QuestStatus',
    'CraftingSystem', 'CraftingRecipe', 'CraftingStation',
    'ComputerVisionSystem', 'VisionAction',
    'ObjectCreationSystem', 'ObjectType',
    'SecureDatabase',
    'SpatialSystem', 'SpatialIndex',
    'SessionManager', 'UserSession',
    'EventSystem', 'EventPriority',
    
    # Новые системы Enhanced Edition
    'CurseType', 'BlessingType', 'CurseBlessingEffect', 'CurseBlessingSystem',
    'RiskLevel', 'RiskCategory', 'RiskFactor', 'RiskRewardEvent', 'RiskRewardSystem',
    'MetaCurrency', 'MetaUpgrade', 'InheritanceTrait', 'Achievement', 'MetaProgressionSystem',
    'EnhancedContentGenerator',
    'SkillManager', 'SkillLearningAI',
    'EnhancedInventorySystem',
    'EnhancedUISystem', 'UIState',
    'GamePhase', 'DifficultyMode', 'GameSession', 'EnhancedGameMaster',
]
