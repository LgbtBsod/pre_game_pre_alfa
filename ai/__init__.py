"""
Модуль AI для игровых сущностей.
Включает улучшенную систему искусственного интеллекта с модульной архитектурой.
"""

from .ai_core import AICore, AIState, AIPriority, AIPersonality, AIKnowledge, AIEmotion

from .ai_manager import (
    AIManager,
    ai_manager,
    GroupCoordinator,
    SpatialHash,
    UpdateQueue,
)

from .advanced_ai import AdvancedAIController
from .behavior_tree import BehaviorTree, generate_tree_for_personality
from .cooperation import AICoordinator, GroupTactics
from .decision_maker import DecisionMaker
from .emotion_genetics import EmotionGeneticSynthesizer
from .learning import LearningSystem, PlayerLearning, EnemyLearning, BossLearning
from .memory import AIMemory
from .pattern_recognizer import PatternRecognizer

__all__ = [
    # Основные AI компоненты
    "AICore",
    "AIState",
    "AIPriority",
    "AIPersonality",
    "AIKnowledge",
    "AIEmotion",
    # Менеджер AI
    "AIManager",
    "ai_manager",
    "GroupCoordinator",
    "SpatialHash",
    "UpdateQueue",
    # Устаревшие компоненты (для совместимости)
    "AdvancedAIController",
    "BehaviorTree",
    "generate_tree_for_personality",
    "AICoordinator",
    "GroupTactics",
    "DecisionMaker",
    "EmotionGeneticSynthesizer",
    "LearningSystem",
    "PlayerLearning",
    "EnemyLearning",
    "BossLearning",
    "AIMemory",
    "PatternRecognizer",
]
