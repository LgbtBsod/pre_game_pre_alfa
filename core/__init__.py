"""Основные системы игры."""

# Core systems for Evolutionary Adaptation: Genetic Resonance
# Основные системы для "Эволюционная Адаптация: Генетический Резонас"

from .effect_system import EffectSystem, EffectDatabase, EffectCode
from .genetic_system import AdvancedGeneticSystem
from .emotion_system import AdvancedEmotionSystem
from .ai_system import AdaptiveAISystem, QLearningAgent
from .content_generator import ContentGenerator, GeneratedWorld
from .evolution_system import EvolutionCycleSystem
from .global_event_system import GlobalEventSystem
from .dynamic_difficulty import DynamicDifficultySystem
from .advanced_entity import AdvancedGameEntity, PygameGameEntity
from .game_loop import GameLoop

# Новые системы боевого ИИ
from .combat_learning_system import CombatLearningSystem, CombatAction, EnemyVulnerability
from .advanced_weapon_system import AdvancedWeapon, WeaponType, WeaponRarity, WeaponFactory, WeaponManager
from .integrated_combat_ai import IntegratedCombatAI, CombatStrategy, CombatContext, CombatDecision

__all__ = [
    # Основные системы
    'EffectSystem',
    'EffectDatabase', 
    'EffectCode',
    'AdvancedGeneticSystem',
    'AdvancedEmotionSystem',
    'AdaptiveAISystem',
    'QLearningAgent',
    'ContentGenerator',
    'GeneratedWorld',
    'EvolutionCycleSystem',
    'GlobalEventSystem',
    'DynamicDifficultySystem',
    'AdvancedGameEntity',
    'PygameGameEntity',
    'GameLoop',
    
    # Системы боевого ИИ
    'CombatLearningSystem',
    'CombatAction',
    'EnemyVulnerability',
    'AdvancedWeapon',
    'WeaponType',
    'WeaponRarity',
    'WeaponFactory',
    'WeaponManager',
    'IntegratedCombatAI',
    'CombatStrategy',
    'CombatContext',
    'CombatDecision'
]
