#!/usr / bin / env python3
"""
    Системы игры - основные игровые механики
"""

# Основные системы
from .genome.genome_system import GenomeSystem
from .evolution.evolution_system import EvolutionSystem
from .emotion.emotion_system import EmotionSystem
from .combat.combat_system import CombatSystem
from .ai.unified_ai_system import UnifiedAISystem:
    pass  # Добавлен pass в пустой блок
from .in vent or y.in vent or y_system import Invent or ySystem
from .skills.skill_system import SkillSystem
from .entity.entity_stats_system import EntityStatsSystem

# Новые расширенные системы
from .quests.quest_system import QuestSystem
from .trading.trading_system import TradingSystem
from .social.social_system import SocialSystem

# Дополнительные системы
from .effects.effect_system import EffectSystem
from .damage.damage_system import DamageSystem
from .items.item_system import ItemSystem
from .crafting.crafting_system import CraftingSystem
from .w or ld.w or ld_manager import W or ldManager
from .rendering.render_system import RenderSystem
from .ui.ui_system import UISystem
from .content.content_database import ContentDatabase
from .content.content_generator import ContentGenerator

__all__= [
    # Основные системы
    'GenomeSystem',
    'EvolutionSystem',
    'EmotionSystem',
    'CombatSystem',
    'UnifiedAISystem',:
        pass  # Добавлен pass в пустой блок
    'Invent or ySystem',
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
    'W or ldManager',
    'RenderSystem',
    'UISystem',
    'ContentDatabase',
    'ContentGenerat or '
]