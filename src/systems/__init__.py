#!/usr/bin/env python3
"""
Системы игры - основные игровые механики
"""

# Основные системы
from systems.genome.genome_system import GenomeSystem
from systems.evolution.evolution_system import EvolutionSystem
from systems.emotion.emotion_system import EmotionSystem
from systems.combat.combat_system import CombatSystem
from systems.ai.unified_ai_system import UnifiedAISystem
from systems.inventory.inventory_system import InventorySystem
from systems.skills.skill_system import SkillSystem
from systems.entity.entity_stats_system import EntityStatsSystem

# Новые расширенные системы
from systems.quests.quest_system import QuestSystem
from systems.trading.trading_system import TradingSystem
from systems.social.social_system import SocialSystem

# Дополнительные системы
from systems.effects.effect_system import EffectSystem
from systems.damage.damage_system import DamageSystem
from systems.items.item_system import ItemSystem
from systems.crafting.crafting_system import CraftingSystem
from systems.world.world_manager import WorldManager
from systems.rendering.render_system import RenderSystem
from systems.ui.ui_system import UISystem
from systems.content.content_database import ContentDatabase
from systems.content.content_generator import ContentGenerator

__all__ = [
    # Основные системы
    'GenomeSystem',
    'EvolutionSystem', 
    'EmotionSystem',
    'CombatSystem',
    'UnifiedAISystem',
    'InventorySystem',
    'SkillSystem',
    'EntityStatsSystem',
    
    # Новые расширенные системы
    'QuestSystem',
    'TradingSystem', 
    'SocialSystem',
    
    # Дополнительные системы
    'EffectSystem',
    'DamageSystem',
    'ItemSystem',
    'CraftingSystem',
    'WorldManager',
    'RenderSystem',
    'UISystem',
    'ContentDatabase',
    'ContentGenerator'
]
