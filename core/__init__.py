"""Основные системы игры."""

# Базовые компоненты
from .component import Component, ComponentManager
from .attributes import AttributeManager, Attribute

# Основные системы
from .effect_system import EffectDatabase, Effect, EffectType, EffectCode
from .genetic_system import AdvancedGeneticSystem, GeneCode, MutationType
from .emotion_system import AdvancedEmotionSystem, EmotionCode, EmotionIntensity
from .ai_system import AdaptiveAISystem, QLearningAgent
from .content_generator import ContentGenerator
from .evolution_system import EvolutionCycleSystem
from .global_event_system import GlobalEventSystem, EventType, EventSeverity
from .dynamic_difficulty import DynamicDifficultySystem, DifficultyLevel
from .game_loop import GameLoop, GameWorld

__all__ = [
    # Базовые компоненты
    "Component",
    "ComponentManager",
    "AttributeManager", 
    "Attribute",
    
    # Основные системы
    "EffectDatabase",
    "Effect",
    "EffectType",
    "EffectCode",
    "AdvancedGeneticSystem",
    "GeneCode",
    "MutationType",
    "AdvancedEmotionSystem",
    "EmotionCode",
    "EmotionIntensity",
    "AdaptiveAISystem",
    "QLearningAgent",
    "ContentGenerator",
    "EvolutionCycleSystem",
    "GlobalEventSystem",
    "EventType",
    "EventSeverity",
    "DynamicDifficultySystem",
    "DifficultyLevel",
    "GameLoop",
    "GameWorld",
]
