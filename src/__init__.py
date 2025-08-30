#!/usr/bin/env python3
"""
AI-EVOLVE: Эволюционная Адаптация - Генетический Резонанс
Основной пакет игрового движка
"""

# Core Systems
from .core import (
    IComponent, BaseComponent, ComponentType, LifecycleState, Priority,
    ComponentManager, EventBus, Event, create_event,
    GameEngine, GameState, SceneManager
)

# AI Systems
from .systems.ai import (
    AISystem, AIConfig, AIMemory, AIDecision,
    PyTorchAISystem, NeuralNetwork, EmotionalNetwork
)

# Game Systems
from .systems.combat import CombatSystem
from .systems.effects import EffectSystem
from .systems.health import HealthSystem
from .systems.inventory import InventorySystem
from .systems.items import ItemSystem
from .systems.skills import SkillSystem
from .systems.ui import UISystem
from .systems.ui.hud import HUDSystem

# Evolution System
from .systems.evolution.evolution_system import (
    EvolutionSystem, Gene, Mutation, EvolutionTree, 
    EvolutionProgress, GeneticCombination, GeneType, 
    MutationType, EvolutionPath, EvolutionStage
)

# Memory System
from .systems.memory.memory_system import (
    MemorySystem, PlayerMemory, EnemyMemoryBank, 
    MemoryType, ExperienceCategory
)

# Rendering Systems
from .systems.rendering import (
    RenderSystem, IsometricCamera, CameraSettings, CameraState
)

# Integration System
from .systems.integration.system_integrator import SystemIntegrator

# Testing System
from .systems.testing.integration_tester import IntegrationTester

# Demo System
from .demo.demo_launcher import DemoLauncher

# Entity Classes
from .entities import (
    BaseEntity, EntityType, Player, Enemy, NPC, Item,
    Boss, BossPhase, BossType, BossAbility, BossWeakness, BossPhaseData,
    Mutant, MutationType, MutationLevel, Mutation, MutantAbility, VisualMutation
)

# Scene Classes
from .scenes import (
    MenuScene, GameScene, PauseScene, SettingsScene, LoadScene, CreatorScene
)

# Version Info
__version__ = "2.5.0"
__author__ = "AI-EVOLVE Team"
__description__ = "Эволюционная Адаптация: Генетический Резонанс"

# Основные экспорты
__all__ = [
    # Core
    'IComponent', 'BaseComponent', 'ComponentType', 'LifecycleState', 'Priority',
    'ComponentManager', 'EventBus', 'Event', 'create_event',
    'GameEngine', 'GameState', 'SceneManager',
    
    # AI Systems
    'AISystem', 'AIConfig', 'AIMemory', 'AIDecision',
    'PyTorchAISystem', 'NeuralNetwork', 'EmotionalNetwork',
    
    # Game Systems
    'CombatSystem', 'EffectSystem', 'HealthSystem', 'InventorySystem',
    'ItemSystem', 'SkillSystem', 'UISystem', 'HUDSystem',
    
    # Evolution System
    'EvolutionSystem', 'Gene', 'Mutation', 'EvolutionTree', 
    'EvolutionProgress', 'GeneticCombination', 'GeneType', 
    'MutationType', 'EvolutionPath', 'EvolutionStage',
    
    # Memory System
    'MemorySystem', 'PlayerMemory', 'EnemyMemoryBank', 
    'MemoryType', 'ExperienceCategory',
    
    # Rendering Systems
    'RenderSystem', 'IsometricCamera', 'CameraSettings', 'CameraState',
    
    # Integration System
    'SystemIntegrator',
    
    # Testing System
    'IntegrationTester',
    
    # Demo System
    'DemoLauncher',
    
    # Entity Classes
    'BaseEntity', 'EntityType', 'Player', 'Enemy', 'NPC', 'Item',
    'Boss', 'BossPhase', 'BossType', 'BossAbility', 'BossWeakness', 'BossPhaseData',
    'Mutant', 'MutationType', 'MutationLevel', 'Mutation', 'MutantAbility', 'VisualMutation',
    
    # Scene Classes
    'MenuScene', 'GameScene', 'PauseScene', 'SettingsScene', 'LoadScene', 'CreatorScene'
]
