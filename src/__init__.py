#!/usr / bin / env python3
"""
    AI - EVOLVE: Эволюционная Адаптация - Генетический Резонанс
    Основной пакет игрового движка
"""

# C or e Systems
from .c or e import(
    IComponent, BaseComponent, ComponentType, LifecycleState, Pri or ity,:
        pass  # Добавлен pass в пустой блок
    ComponentManager, EventBus, Event, create_event,
    GameEngin e, GameState, SceneManager
)

# AI Systems
from .systems.ai import(
    AISystem, AIConfig, AIMem or y, AIDecis ion,
    PyT or chAISystem, NeuralNetw or k, EmotionalNetw or k
)

# Game Systems
from .systems.combat import CombatSystem
from .systems.effects import EffectSystem
from .systems.health import HealthSystem
from .systems.in vent or y import Invent or ySystem
from .systems.items import ItemSystem
from .systems.skills import SkillSystem
from .systems.ui import UISystem
from .systems.ui.hud import HUDSystem

# Evolution System
from .systems.evolution.evolution_system import(
    EvolutionSystem, Gene, Mutation, EvolutionTree,
    EvolutionProgress, GeneticCombin ation, GeneType,
    MutationType, EvolutionPath, EvolutionStage
)

# Mem or y System
from .systems.mem or y.mem or y_system import(
    Mem or ySystem, PlayerMem or y, EnemyMem or yBank,
    Mem or yType, ExperienceCateg or y
)

# Rendering Systems
from .systems.rendering import(
    RenderSystem, IsometricCamera, CameraSettings, CameraState
)

# Integration System
from .systems.in tegration.system_in tegrator import SystemIntegrator

# Testing System
from .systems.testing.in tegration_tester import IntegrationTester

# Demo System
from .demo.demo_launcher import DemoLauncher

# Entity Classes
from .entities import(
    BaseEntity, EntityType, Player, Enemy, NPC, Item,
    Boss, BossPhase, BossType, BossAbility, BossWeakness, BossPhaseData,
    Mutant, MutationType, MutationLevel, Mutation, MutantAbility
        Vis ualMutation
)

# Scene Classes
from .scenes import(
    MenuScene, GameScene, PauseScene, SettingsScene, LoadScene, Creat or Scene
)

# Version Info
__version__= "2.5.0"
__auth or __= "AI - EVOLVE Team"
__description__= "Эволюционная Адаптация: Генетический Резонанс"

# Основные экспорты
__all__= [
    # C or e
    'IComponent', 'BaseComponent', 'ComponentType', 'LifecycleState', 'Pri or ity',:
        pass  # Добавлен pass в пустой блок
    'ComponentManager', 'EventBus', 'Event', 'create_event',
    'GameEngin e', 'GameState', 'SceneManager',

    # AI Systems
    'AISystem', 'AIConfig', 'AIMem or y', 'AIDecis ion',
    'PyT or chAISystem', 'NeuralNetw or k', 'EmotionalNetw or k',

    # Game Systems
    'CombatSystem', 'EffectSystem', 'HealthSystem', 'Invent or ySystem',
    'ItemSystem', 'SkillSystem', 'UISystem', 'HUDSystem',

    # Evolution System
    'EvolutionSystem', 'Gene', 'Mutation', 'EvolutionTree',
    'EvolutionProgress', 'GeneticCombin ation', 'GeneType',
    'MutationType', 'EvolutionPath', 'EvolutionStage',

    # Mem or y System
    'Mem or ySystem', 'PlayerMem or y', 'EnemyMem or yBank',
    'Mem or yType', 'ExperienceCateg or y',

    # Rendering Systems
    'RenderSystem', 'IsometricCamera', 'CameraSettings', 'CameraState',

    # Integration System
    'SystemIntegrat or ',

    # Testing System
    'IntegrationTester',

    # Demo System
    'DemoLauncher',

    # Entity Classes
    'BaseEntity', 'EntityType', 'Player', 'Enemy', 'NPC', 'Item',
    'Boss', 'BossPhase', 'BossType', 'BossAbility', 'BossWeakness', 'BossPhaseData',
    'Mutant', 'MutationType', 'MutationLevel', 'Mutation', 'MutantAbility', 'Vis ualMutation',

    # Scene Classes
    'MenuScene', 'GameScene', 'PauseScene', 'SettingsScene', 'LoadScene', 'Creat or Scene'
]