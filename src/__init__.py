#!/usr/bin/env python3
"""
AI-EVOLVE: Эволюционная Адаптация - Генетический Резонанс
Основной пакет с игровыми системами
"""

# Core Architecture
from .core.architecture import (
    BaseComponent,
    ComponentType,
    Priority,
    ComponentManager,
    EventBus,
    StateManager,
    RepositoryManager
)

from .core.game_engine import GameEngine

# AI Systems
from .systems.ai.unified_ai_system import UnifiedAISystem
from .systems.ai.ai_integration_system import AISystemAdapter
from .systems.ai.ai_system import AISystem
from .systems.ai.pytorch_ai_system import PyTorchAISystem

# Game Systems
from .systems.effects.effect_system import EffectSystem, Effect, SpecialEffect
from .systems.damage.damage_system import DamageSystem, DamageInstance, DamageType
from .systems.inventory.inventory_system import InventorySystem, Item, ItemType
from .systems.skills.skill_system import SkillSystem, Skill, SkillType
from .systems.combat.combat_system import CombatSystem, CombatAction, CombatResult
from .systems.health.health_system import HealthSystem, HealthStatus, ResourceType

# UI Systems
from .systems.ui.ui_system import UISystem, UIElement, UIElementType, UIState
from .systems.ui.hud_system import HUDSystem, HUDElement, HUDType, HUDLayout

# Legacy Systems (для обратной совместимости)
try:
    from .systems.emotion.emotion_system import EmotionSystem
    from .systems.evolution.evolution_system import EvolutionSystem
    from .systems.rendering.render_system import RenderSystem
    from .systems.content.content_generator import ContentGenerator
    from .systems.social.social_system import SocialSystem
except ImportError:
    # Системы могут быть не реализованы полностью
    pass

# Entity Classes
from .entities.base_entity import BaseEntity
from .entities.player import Player
from .entities.npc import NPC
from .entities.enemies import Enemy
from .entities.items import Item as ItemEntity

# Scene Classes
from .scenes.menu_scene import MenuScene
from .scenes.game_scene import GameScene
from .scenes.pause_scene import PauseScene
from .scenes.settings_scene import SettingsScene
from .scenes.load_scene import LoadScene
from .scenes.creator_scene import CreatorScene

# Version Info
__version__ = "2.2.0"
__author__ = "AI-EVOLVE Team"
__description__ = "Эволюционная Адаптация: Генетический Резонанс"

# Основные экспорты
__all__ = [
    # Core
    'BaseComponent',
    'ComponentType', 
    'Priority',
    'ComponentManager',
    'EventBus',
    'StateManager',
    'RepositoryManager',
    'GameEngine',
    
    # AI Systems
    'UnifiedAISystem',
    'AISystemAdapter',
    'AISystem',
    'PyTorchAISystem',
    
    # Game Systems
    'EffectSystem',
    'Effect',
    'SpecialEffect',
    'DamageSystem',
    'DamageInstance',
    'DamageType',
    'InventorySystem',
    'Item',
    'ItemType',
    'SkillSystem',
    'Skill',
    'SkillType',
    'CombatSystem',
    'CombatAction',
    'CombatResult',
    'HealthSystem',
    'HealthStatus',
    'ResourceType',
    
    # UI Systems
    'UISystem',
    'UIElement',
    'UIElementType',
    'UIState',
    'HUDSystem',
    'HUDElement',
    'HUDType',
    'HUDLayout',
    
    # Legacy Systems
    'EmotionSystem',
    'EvolutionSystem',
    'RenderSystem',
    'ContentGenerator',
    'SocialSystem',
    
    # Entities
    'BaseEntity',
    'Player',
    'NPC',
    'Enemy',
    'ItemEntity',
    
    # Scenes
    'MenuScene',
    'GameScene',
    'PauseScene',
    'SettingsScene',
    'LoadScene',
    'CreatorScene',
    
    # Version
    '__version__',
    '__author__',
    '__description__'
]
