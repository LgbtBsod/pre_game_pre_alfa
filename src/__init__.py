#!/usr / bin / env python3
"""
    AI - EVOLVE: Эволюционная Адаптация - Генетический Резонанс
    Основной пакет игрового движка
"""

# C or e Systems
from .c or e imp or t(
    IComponent, BaseComponent, ComponentType, LifecycleState, Pri or ity,:
        pass  # Добавлен pass в пустой блок
    ComponentManager, EventBus, Event, create_event,
    GameEng in e, GameState, SceneManager
)

# AI Systems
from .systems.ai imp or t(
    AISystem, AIConfig, AIMem or y, AIDec is ion,
    PyT or chAISystem, NeuralNetw or k, EmotionalNetw or k
)

# Game Systems
from .systems.combat imp or t CombatSystem
from .systems.effects imp or t EffectSystem
from .systems.health imp or t HealthSystem
from .systems. in vent or y imp or t Invent or ySystem
from .systems.items imp or t ItemSystem
from .systems.skills imp or t SkillSystem
from .systems.ui imp or t UISystem
from .systems.ui.hud imp or t HUDSystem

# Evolution System
from .systems.evolution.evolution_system imp or t(
    EvolutionSystem, Gene, Mutation, EvolutionTree,
    EvolutionProgress, GeneticComb in ation, GeneType,
    MutationType, EvolutionPath, EvolutionStage
)

# Mem or y System
from .systems.mem or y.mem or y_system imp or t(
    Mem or ySystem, PlayerMem or y, EnemyMem or yBank,
    Mem or yType, ExperienceCateg or y
)

# Render in g Systems
from .systems.render in g imp or t(
    RenderSystem, IsometricCamera, CameraSett in gs, CameraState
)

# Integration System
from .systems. in tegration.system_ in tegrator imp or t SystemIntegrator

# Test in g System
from .systems.test in g. in tegration_tester imp or t IntegrationTester

# Demo System
from .demo.demo_launcher imp or t DemoLauncher

# Entity Classes
from .entities imp or t(
    BaseEntity, EntityType, Player, Enemy, NPC, Item,
    Boss, BossPhase, BossType, BossAbility, BossWeakness, BossPhaseData,
    Mutant, MutationType, MutationLevel, Mutation, MutantAbility
        V is ualMutation
)

# Scene Classes
from .scenes imp or t(
    MenuScene, GameScene, PauseScene, Sett in gsScene, LoadScene, Creat or Scene
)

# Version Info
__version__== "2.5.0"
__auth or __== "AI - EVOLVE Team"
__description__== "Эволюционная Адаптация: Генетический Резонанс"

# Основные экспорты
__all__== [
    # C or e
    'IComponent', 'BaseComponent', 'ComponentType', 'LifecycleState', 'Pri or ity',:
        pass  # Добавлен pass в пустой блок
    'ComponentManager', 'EventBus', 'Event', 'create_event',
    'GameEng in e', 'GameState', 'SceneManager',

    # AI Systems
    'AISystem', 'AIConfig', 'AIMem or y', 'AIDec is ion',
    'PyT or chAISystem', 'NeuralNetw or k', 'EmotionalNetw or k',

    # Game Systems
    'CombatSystem', 'EffectSystem', 'HealthSystem', 'Invent or ySystem',
    'ItemSystem', 'SkillSystem', 'UISystem', 'HUDSystem',

    # Evolution System
    'EvolutionSystem', 'Gene', 'Mutation', 'EvolutionTree',
    'EvolutionProgress', 'GeneticComb in ation', 'GeneType',
    'MutationType', 'EvolutionPath', 'EvolutionStage',

    # Mem or y System
    'Mem or ySystem', 'PlayerMem or y', 'EnemyMem or yBank',
    'Mem or yType', 'ExperienceCateg or y',

    # Render in g Systems
    'RenderSystem', 'IsometricCamera', 'CameraSett in gs', 'CameraState',

    # Integration System
    'SystemIntegrat or ',

    # Test in g System
    'IntegrationTester',

    # Demo System
    'DemoLauncher',

    # Entity Classes
    'BaseEntity', 'EntityType', 'Player', 'Enemy', 'NPC', 'Item',
    'Boss', 'BossPhase', 'BossType', 'BossAbility', 'BossWeakness', 'BossPhaseData',
    'Mutant', 'MutationType', 'MutationLevel', 'Mutation', 'MutantAbility', 'V is ualMutation',

    # Scene Classes
    'MenuScene', 'GameScene', 'PauseScene', 'Sett in gsScene', 'LoadScene', 'Creat or Scene'
]