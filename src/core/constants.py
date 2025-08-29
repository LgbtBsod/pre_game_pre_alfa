#!/usr/bin/env python3
"""
Оптимизированный модуль констант для AI-EVOLVE
Модульная архитектура с принципом единой ответственности
"""

from enum import Enum
from typing import Dict, Any, Optional, Union, Type, TypeVar, Generic
from dataclasses import dataclass, field
from types import MappingProxyType
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# БАЗОВЫЕ ТИПЫ
# ============================================================================

class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"
    PIERCING = "piercing"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"
    ARCANE = "arcane"
    MAGIC = "magic"
    TRUE = "true"
    ACID = "acid"
    COLD = "cold"
    NECROTIC = "necrotic"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SHADOW = "shadow"
    SOUND = "sound"
    VIBRATION = "vibration"
    ENERGY = "energy"
    CHAOS = "chaos"
    WIND = "wind"
    EARTH = "earth"
    GENETIC = "genetic"
    EMOTIONAL = "emotional"

class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    TOOL = "tool"
    GEM = "gem"
    SCROLL = "scroll"
    BOOK = "book"
    KEY = "key"
    CURRENCY = "currency"

class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    DIVINE = "divine"

class SkillType(Enum):
    """Типы навыков"""
    ATTACK = "attack"
    UTILITY = "utility"
    PASSIVE = "passive"
    ACTIVE = "active"
    ULTIMATE = "ultimate"
    MOVEMENT = "movement"
    DEFENSIVE = "defensive"
    SUPPORT = "support"
    REACTIVE = "reactive"

class StatType(Enum):
    """Типы характеристик"""
    HEALTH = "health"
    MANA = "mana"
    STAMINA = "stamina"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPEED = "speed"
    INTELLIGENCE = "intelligence"
    STRENGTH = "strength"
    AGILITY = "agility"
    CONSTITUTION = "constitution"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
    LUCK = "luck"
    CRITICAL_CHANCE = "critical_chance"
    CRITICAL_MULTIPLIER = "critical_multiplier"
    DODGE_CHANCE = "dodge_chance"
    BLOCK_CHANCE = "block_chance"
    RESISTANCE = "resistance"

class CombatState(Enum):
    """Состояния боя"""
    IDLE = "idle"
    IN_COMBAT = "in_combat"
    VICTORY = "victory"
    DEFEAT = "defeat"
    ESCAPED = "escaped"
    PREPARING = "preparing"
    ATTACKING = "attacking"
    DEFENDING = "defending"
    STUNNED = "stunned"
    RETREATING = "retreating"

class AIBehavior(Enum):
    """Типы поведения AI"""
    PASSIVE = "passive"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    CAUTIOUS = "cautious"
    BERSERK = "berserk"
    TACTICAL = "tactical"
    SUPPORT = "support"
    EXPLORER = "explorer"
    TRADER = "trader"
    CRAFTER = "crafter"

class AIState(Enum):
    """Состояния AI"""
    IDLE = "idle"
    PATROLLING = "patrolling"
    CHASING = "chasing"
    ATTACKING = "attacking"
    FLEEING = "fleeing"
    SEARCHING = "searching"
    RESTING = "resting"
    THINKING = "thinking"
    DECIDING = "deciding"
    ACTING = "acting"
    LEARNING = "learning"
    SLEEPING = "sleeping"

class AIDifficulty(Enum):
    """Уровни сложности AI"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"

class EntityType(Enum):
    """Типы сущностей"""
    PLAYER = "player"
    ENEMY = "enemy"
    NPC = "npc"
    BOSS = "boss"
    MUTANT = "mutant"
    CREATURE = "creature"
    OBJECT = "object"

# ============================================================================
# МОДУЛЬ БАЗОВЫХ ЗНАЧЕНИЙ
# ============================================================================

@dataclass
class BaseStats:
    """Базовые характеристики"""
    health: int = 100
    mana: int = 50
    stamina: int = 100
    attack: int = 10
    defense: int = 5
    speed: float = 1.0
    intelligence: int = 10
    strength: int = 10
    agility: int = 10
    constitution: int = 10
    wisdom: int = 10
    charisma: int = 10
    luck: int = 5
    critical_chance: float = 0.05
    critical_multiplier: float = 2.0
    dodge_chance: float = 0.1
    block_chance: float = 0.15
    parry_chance: float = 0.1
    evasion_chance: float = 0.1
    resist_chance: float = 0.1
    toughness: int = 100
    toughness_resistance: float = 0.0
    stun_resistance: float = 0.0
    break_efficiency: float = 1.0

class BaseStatsManager:
    """Менеджер базовых характеристик"""
    
    @staticmethod
    def get_default_stats() -> Dict[str, Any]:
        """Получение базовых характеристик по умолчанию"""
        stats = BaseStats()
        return {
            "health": stats.health,
            "mana": stats.mana,
            "stamina": stats.stamina,
            "attack": stats.attack,
            "defense": stats.defense,
            "speed": stats.speed,
            "intelligence": stats.intelligence,
            "strength": stats.strength,
            "agility": stats.agility,
            "constitution": stats.constitution,
            "wisdom": stats.wisdom,
            "charisma": stats.charisma,
            "luck": stats.luck,
            "critical_chance": stats.critical_chance,
            "critical_multiplier": stats.critical_multiplier,
            "dodge_chance": stats.dodge_chance,
            "block_chance": stats.block_chance,
            "parry_chance": stats.parry_chance,
            "evasion_chance": stats.evasion_chance,
            "resist_chance": stats.resist_chance,
            "toughness": stats.toughness,
            "toughness_resistance": stats.toughness_resistance,
            "stun_resistance": stats.stun_resistance,
            "break_efficiency": stats.break_efficiency,
            "resistance": {},
            "damage_multipliers": {}
        }
    
    @staticmethod
    def apply_template(base_stats: Dict[str, Any], template_name: str, level: int = 1) -> Dict[str, Any]:
        """Применение шаблона к базовым характеристикам"""
        templates = {
            "tank": {
                "health": 2.0, "defense": 2.5, "speed": 0.6, "attack": 0.8,
                "toughness": 1.5, "toughness_resistance": 1.5, "stun_resistance": 2.0
            },
            "assassin": {
                "health": 0.7, "defense": 0.5, "speed": 2.5, "attack": 2.0,
                "critical_chance": 2.0, "critical_multiplier": 1.5, "dodge_chance": 2.0
            },
            "mage": {
                "health": 0.8, "mana": 3.0, "defense": 0.6, "intelligence": 2.5,
                "wisdom": 2.0, "attack": 0.5
            }
        }
        
        if template_name not in templates:
            return base_stats
        
        template = templates[template_name]
        modified_stats = base_stats.copy()
        
        for stat, multiplier in template.items():
            if stat in modified_stats and isinstance(modified_stats[stat], (int, float)):
                modified_stats[stat] = int(modified_stats[stat] * multiplier * level)
        
        return modified_stats

# ============================================================================
# МОДУЛЬ СИСТЕМНЫХ ЛИМИТОВ
# ============================================================================

@dataclass
class SystemLimits:
    """Лимиты систем"""
    max_entities: int = 10000
    max_items: int = 100000
    max_effects: int = 1000
    max_skills: int = 1000
    max_ai_entities: int = 1000
    max_level: int = 100
    max_active_combats: int = 100
    max_combat_participants: int = 50
    max_combat_duration: float = 1800.0
    max_combat_effects: int = 100
    max_inventory_slots: int = 100
    max_inventory_weight: float = 1000.0
    max_equipment_slots: int = 10
    max_item_stack_size: int = 999
    max_item_level: int = 100
    max_skills_per_entity: int = 20
    max_skill_level: int = 100
    max_effects_per_entity: int = 50
    max_effect_duration: float = 3600.0
    max_effect_stacks: int = 99
    max_damage_modifiers: int = 50
    max_damage_combinations: int = 20
    max_genes_per_entity: int = 20
    max_evolution_stages: int = 10
    max_emotions_per_entity: int = 10
    max_emotion_intensity: int = 100
    max_emotion_duration: float = 3600.0
    max_crafting_sessions: int = 10
    max_crafting_queue: int = 5
    target_fps: int = 60
    max_draw_distance: float = 1000.0
    max_particles: int = 10000
    max_ui_elements: int = 500
    max_ui_layers: int = 10
    max_world_objects: int = 1000
    max_quests: int = 50
    max_party_size: int = 4
    max_guild_size: int = 100
    max_trade_items: int = 20
    max_currency_amount: int = 999999
    max_experience: int = 999999999

class SystemLimitsManager:
    """Менеджер системных лимитов"""
    
    @staticmethod
    def get_limits() -> Dict[str, Any]:
        """Получение всех системных лимитов"""
        limits = SystemLimits()
        return {
            "max_entities": limits.max_entities,
            "max_items": limits.max_items,
            "max_effects": limits.max_effects,
            "max_skills": limits.max_skills,
            "max_ai_entities": limits.max_ai_entities,
            "max_level": limits.max_level,
            "max_active_combats": limits.max_active_combats,
            "max_combat_participants": limits.max_combat_participants,
            "max_combat_duration": limits.max_combat_duration,
            "max_combat_effects": limits.max_combat_effects,
            "max_inventory_slots": limits.max_inventory_slots,
            "max_inventory_weight": limits.max_inventory_weight,
            "max_equipment_slots": limits.max_equipment_slots,
            "max_item_stack_size": limits.max_item_stack_size,
            "max_item_level": limits.max_item_level,
            "max_skills_per_entity": limits.max_skills_per_entity,
            "max_skill_level": limits.max_skill_level,
            "max_effects_per_entity": limits.max_effects_per_entity,
            "max_effect_duration": limits.max_effect_duration,
            "max_effect_stacks": limits.max_effect_stacks,
            "max_damage_modifiers": limits.max_damage_modifiers,
            "max_damage_combinations": limits.max_damage_combinations,
            "max_genes_per_entity": limits.max_genes_per_entity,
            "max_evolution_stages": limits.max_evolution_stages,
            "max_emotions_per_entity": limits.max_emotions_per_entity,
            "max_emotion_intensity": limits.max_emotion_intensity,
            "max_emotion_duration": limits.max_emotion_duration,
            "max_crafting_sessions": limits.max_crafting_sessions,
            "max_crafting_queue": limits.max_crafting_queue,
            "target_fps": limits.target_fps,
            "max_draw_distance": limits.max_draw_distance,
            "max_particles": limits.max_particles,
            "max_ui_elements": limits.max_ui_elements,
            "max_ui_layers": limits.max_ui_layers,
            "max_world_objects": limits.max_world_objects,
            "max_quests": limits.max_quests,
            "max_party_size": limits.max_party_size,
            "max_guild_size": limits.max_guild_size,
            "max_trade_items": limits.max_trade_items,
            "max_currency_amount": limits.max_currency_amount,
            "max_experience": limits.max_experience
        }

# ============================================================================
# МОДУЛЬ ВРЕМЕННЫХ КОНСТАНТ
# ============================================================================

@dataclass
class TimeConstants:
    """Временные константы"""
    tick_rate: float = 60.0
    update_interval: float = 1.0 / 60.0
    save_interval: float = 300.0
    cleanup_interval: float = 60.0
    combat_timeout: float = 300.0
    ai_decision_delay: float = 0.5
    effect_update_interval: float = 0.1
    effect_cleanup_interval: float = 60.0
    skill_cooldown_tolerance: float = 0.1
    skill_animation_duration: float = 1.0
    item_use_delay: float = 0.5
    equipment_change_delay: float = 0.2
    inventory_update_interval: float = 0.1
    memory_update_interval: float = 1.0
    mutation_check_interval: float = 10.0
    evolution_trigger_delay: float = 5.0
    evolution_cooldown: float = 60.0
    emotion_update_interval: float = 0.5
    emotion_decay_interval: float = 10.0
    crafting_progress_interval: float = 0.1
    combat_turn_duration: float = 1.0
    frame_time_target: float = 1.0 / 60.0
    ui_update_interval: float = 0.016
    ui_animation_duration: float = 0.3
    quest_expiration_time: float = 86400.0
    offer_expiration_time: float = 604800.0
    interaction_cooldown: float = 300.0

class TimeConstantsManager:
    """Менеджер временных констант"""
    
    @staticmethod
    def get_constants() -> Dict[str, float]:
        """Получение всех временных констант"""
        constants = TimeConstants()
        return {
            "tick_rate": constants.tick_rate,
            "update_interval": constants.update_interval,
            "save_interval": constants.save_interval,
            "cleanup_interval": constants.cleanup_interval,
            "combat_timeout": constants.combat_timeout,
            "ai_decision_delay": constants.ai_decision_delay,
            "effect_update_interval": constants.effect_update_interval,
            "effect_cleanup_interval": constants.effect_cleanup_interval,
            "skill_cooldown_tolerance": constants.skill_cooldown_tolerance,
            "skill_animation_duration": constants.skill_animation_duration,
            "item_use_delay": constants.item_use_delay,
            "equipment_change_delay": constants.equipment_change_delay,
            "inventory_update_interval": constants.inventory_update_interval,
            "memory_update_interval": constants.memory_update_interval,
            "mutation_check_interval": constants.mutation_check_interval,
            "evolution_trigger_delay": constants.evolution_trigger_delay,
            "evolution_cooldown": constants.evolution_cooldown,
            "emotion_update_interval": constants.emotion_update_interval,
            "emotion_decay_interval": constants.emotion_decay_interval,
            "crafting_progress_interval": constants.crafting_progress_interval,
            "combat_turn_duration": constants.combat_turn_duration,
            "frame_time_target": constants.frame_time_target,
            "ui_update_interval": constants.ui_update_interval,
            "ui_animation_duration": constants.ui_animation_duration,
            "quest_expiration_time": constants.quest_expiration_time,
            "offer_expiration_time": constants.offer_expiration_time,
            "interaction_cooldown": constants.interaction_cooldown
        }
    
    @staticmethod
    def get_constant(name: str, default: float = 0.0) -> float:
        """Безопасное получение временной константы"""
        constants = TimeConstantsManager.get_constants()
        return constants.get(name, default)

# ============================================================================
# МОДУЛЬ ВЕРОЯТНОСТЕЙ
# ============================================================================

@dataclass
class ProbabilityConstants:
    """Константы вероятностей"""
    base_critical_chance: float = 0.05
    base_dodge_chance: float = 0.1
    base_block_chance: float = 0.15
    base_mutation_chance: float = 0.01
    base_adaptation_chance: float = 0.05
    base_evolution_chance: float = 0.1
    base_drop_chance: float = 0.1
    base_craft_success: float = 0.8
    base_resist_chance: float = 0.1
    base_evasion_chance: float = 0.1
    base_luck: float = 0.05
    base_damage_penetration: float = 0.0
    base_elemental_affinity: float = 1.0
    base_armor_reduction: float = 0.01
    base_resistance_cap: float = 0.95
    base_damage_floor: int = 1
    base_damage_ceiling: int = 999999
    base_combination_chance: float = 0.1
    base_catalytic_chance: float = 0.05
    base_damage_combination_threshold: int = 3
    max_critical_chance: float = 0.95
    min_critical_multiplier: float = 1.5
    max_critical_multiplier: float = 10.0
    hidden_quest_chance: float = 0.1
    epic_quest_chance: float = 0.05
    quest_completion_bonus: float = 1.2
    quest_failure_penalty: float = 0.8
    quest_time_bonus: float = 1.1
    transaction_fee: float = 0.05
    tax_rate: float = 0.02
    reputation_impact: float = 0.1
    price_volatility: float = 0.1
    bulk_discount_rate: float = 0.1
    relationship_decay_rate: float = 0.01
    reputation_decay_rate: float = 0.005
    faction_influence: float = 0.1
    interaction_success_rate: float = 0.8
    betrayal_chance: float = 0.05

class ProbabilityConstantsManager:
    """Менеджер констант вероятностей"""
    
    @staticmethod
    def get_constants() -> Dict[str, Any]:
        """Получение всех констант вероятностей"""
        constants = ProbabilityConstants()
        return {
            "base_critical_chance": constants.base_critical_chance,
            "base_dodge_chance": constants.base_dodge_chance,
            "base_block_chance": constants.base_block_chance,
            "base_mutation_chance": constants.base_mutation_chance,
            "base_adaptation_chance": constants.base_adaptation_chance,
            "base_evolution_chance": constants.base_evolution_chance,
            "base_drop_chance": constants.base_drop_chance,
            "base_craft_success": constants.base_craft_success,
            "base_resist_chance": constants.base_resist_chance,
            "base_evasion_chance": constants.base_evasion_chance,
            "base_luck": constants.base_luck,
            "base_damage_penetration": constants.base_damage_penetration,
            "base_elemental_affinity": constants.base_elemental_affinity,
            "base_armor_reduction": constants.base_armor_reduction,
            "base_resistance_cap": constants.base_resistance_cap,
            "base_damage_floor": constants.base_damage_floor,
            "base_damage_ceiling": constants.base_damage_ceiling,
            "base_combination_chance": constants.base_combination_chance,
            "base_catalytic_chance": constants.base_catalytic_chance,
            "base_damage_combination_threshold": constants.base_damage_combination_threshold,
            "max_critical_chance": constants.max_critical_chance,
            "min_critical_multiplier": constants.min_critical_multiplier,
            "max_critical_multiplier": constants.max_critical_multiplier,
            "hidden_quest_chance": constants.hidden_quest_chance,
            "epic_quest_chance": constants.epic_quest_chance,
            "quest_completion_bonus": constants.quest_completion_bonus,
            "quest_failure_penalty": constants.quest_failure_penalty,
            "quest_time_bonus": constants.quest_time_bonus,
            "transaction_fee": constants.transaction_fee,
            "tax_rate": constants.tax_rate,
            "reputation_impact": constants.reputation_impact,
            "price_volatility": constants.price_volatility,
            "bulk_discount_rate": constants.bulk_discount_rate,
            "relationship_decay_rate": constants.relationship_decay_rate,
            "reputation_decay_rate": constants.reputation_decay_rate,
            "faction_influence": constants.faction_influence,
            "interaction_success_rate": constants.interaction_success_rate,
            "betrayal_chance": constants.betrayal_chance
        }

# ============================================================================
# МОДУЛЬ ТИПОВ УРОНА
# ============================================================================

class DamageTypeManager:
    """Менеджер типов урона"""
    
    @staticmethod
    def generate_resistances() -> Dict[DamageType, float]:
        """Генерация сопротивлений по умолчанию"""
        resistances = {}
        for damage_type in DamageType:
            if damage_type == DamageType.TRUE:
                resistances[damage_type] = 0.0
            elif damage_type in [DamageType.PHYSICAL, DamageType.PIERCING]:
                resistances[damage_type] = 0.0
            elif damage_type in [DamageType.FIRE, DamageType.ICE, DamageType.LIGHTNING]:
                resistances[damage_type] = 0.0
            elif damage_type in [DamageType.GENETIC, DamageType.EMOTIONAL]:
                resistances[damage_type] = 0.0
            else:
                resistances[damage_type] = 0.0
        return resistances
    
    @staticmethod
    def generate_multipliers() -> Dict[DamageType, float]:
        """Генерация множителей урона по умолчанию"""
        multipliers = {}
        for damage_type in DamageType:
            if damage_type == DamageType.TRUE:
                multipliers[damage_type] = 5.0
            elif damage_type in [DamageType.PHYSICAL, DamageType.PIERCING]:
                multipliers[damage_type] = 1.2
            elif damage_type in [DamageType.FIRE, DamageType.ICE, DamageType.LIGHTNING]:
                multipliers[damage_type] = 1.5
            elif damage_type in [DamageType.GENETIC, DamageType.EMOTIONAL]:
                multipliers[damage_type] = 2.0
            else:
                multipliers[damage_type] = 1.0
        return multipliers
    
    @staticmethod
    def normalize_damage_type(value: Optional[str]) -> Optional[DamageType]:
        """Нормализация типа урона"""
        if not value:
            return None
        
        aliases = {
            "magical": "magic",
            "elec": "lightning",
            "ice": "cold",
            "psy": "psychic"
        }
        
        key = value.lower().strip()
        key = aliases.get(key, key)
        
        try:
            return DamageType(key)
        except ValueError:
            return None

# ============================================================================
# МОДУЛЬ ВАЛИДАЦИИ
# ============================================================================

class ValidationManager:
    """Менеджер валидации"""
    
    @staticmethod
    def validate_damage_type(damage_type: str) -> bool:
        """Валидация типа урона"""
        try:
            DamageType(damage_type)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_item_type(item_type: str) -> bool:
        """Валидация типа предмета"""
        try:
            ItemType(item_type)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_rarity(rarity: str) -> bool:
        """Валидация редкости"""
        try:
            ItemRarity(rarity)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_skill_type(skill_type: str) -> bool:
        """Валидация типа навыка"""
        try:
            SkillType(skill_type)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_stat_type(stat_type: str) -> bool:
        """Валидация типа характеристики"""
        try:
            StatType(stat_type)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_combat_state(state: str) -> bool:
        """Валидация состояния боя"""
        try:
            CombatState(state)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_ai_behavior(behavior: str) -> bool:
        """Валидация поведения AI"""
        try:
            AIBehavior(behavior)
            return True
        except ValueError:
            return False

# ============================================================================
# МОДУЛЬ УТИЛИТ
# ============================================================================

class UtilsManager:
    """Менеджер утилит"""
    
    @staticmethod
    def get_enum_values(enum_class) -> list:
        """Получение всех значений перечисления"""
        return [e.value for e in enum_class]
    
    @staticmethod
    def get_enum_names(enum_class) -> list:
        """Получение всех имен перечисления"""
        return [e.name for e in enum_class]
    
    @staticmethod
    def is_valid_enum_value(enum_class, value: str) -> bool:
        """Проверка валидности значения перечисления"""
        try:
            enum_class(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def enum_to_dict(enum_class) -> Dict[str, str]:
        """Конвертация перечисления в словарь"""
        return {e.name: e.value for e in enum_class}
    
    @staticmethod
    def dict_to_enum(enum_class, data: Dict[str, str]):
        """Конвертация словаря в перечисление"""
        return {k: enum_class(v) for k, v in data.items()}
    
    @staticmethod
    def freeze_constants(mapping: Dict[str, Any]) -> MappingProxyType:
        """Возвращает read-only proxy для защиты словарей констант"""
        return MappingProxyType(mapping)

# ============================================================================
# ГЛАВНЫЙ МЕНЕДЖЕР КОНСТАНТ
# ============================================================================

class ConstantsManager:
    """Главный менеджер всех констант"""
    
    def __init__(self):
        self.base_stats = BaseStatsManager()
        self.system_limits = SystemLimitsManager()
        self.time_constants = TimeConstantsManager()
        self.probability_constants = ProbabilityConstantsManager()
        self.damage_types = DamageTypeManager()
        self.validation = ValidationManager()
        self.utils = UtilsManager()
        
        # Генерируем константы
        self._resistances = self.damage_types.generate_resistances()
        self._multipliers = self.damage_types.generate_multipliers()
        
        # Создаем read-only версии
        self._base_stats_ro = self.utils.freeze_constants(self.base_stats.get_default_stats())
        self._system_limits_ro = self.utils.freeze_constants(self.system_limits.get_limits())
        self._time_constants_ro = self.utils.freeze_constants(self.time_constants.get_constants())
        self._probability_constants_ro = self.utils.freeze_constants(self.probability_constants.get_constants())
    
    def get_base_stats(self) -> MappingProxyType:
        """Получение базовых характеристик (read-only)"""
        return self._base_stats_ro
    
    def get_system_limits(self) -> MappingProxyType:
        """Получение системных лимитов (read-only)"""
        return self._system_limits_ro
    
    def get_time_constants(self) -> MappingProxyType:
        """Получение временных констант (read-only)"""
        return self._time_constants_ro
    
    def get_probability_constants(self) -> MappingProxyType:
        """Получение констант вероятностей (read-only)"""
        return self._probability_constants_ro
    
    def get_resistances(self) -> Dict[DamageType, float]:
        """Получение сопротивлений"""
        return self._resistances.copy()
    
    def get_multipliers(self) -> Dict[DamageType, float]:
        """Получение множителей"""
        return self._multipliers.copy()
    
    def get_damage_type(self, name: str) -> Optional[DamageType]:
        """Получение типа урона по имени"""
        return self.damage_types.normalize_damage_type(name)
    
    def validate_constant(self, constant_type: str, value: str) -> bool:
        """Валидация константы по типу"""
        validators = {
            "damage_type": self.validation.validate_damage_type,
            "item_type": self.validation.validate_item_type,
            "rarity": self.validation.validate_rarity,
            "skill_type": self.validation.validate_skill_type,
            "stat_type": self.validation.validate_stat_type,
            "combat_state": self.validation.validate_combat_state,
            "ai_behavior": self.validation.validate_ai_behavior
        }
        
        validator = validators.get(constant_type)
        if validator:
            return validator(value)
        return False

# ============================================================================
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ============================================================================

# Создаем глобальный экземпляр менеджера констант
constants_manager = ConstantsManager()

# Экспортируем основные константы для обратной совместимости
BASE_STATS = constants_manager.get_base_stats()
SYSTEM_LIMITS = constants_manager.get_system_limits()
TIME_CONSTANTS = constants_manager.get_time_constants()
PROBABILITY_CONSTANTS = constants_manager.get_probability_constants()
DEFAULT_RESISTANCES = constants_manager.get_resistances()
DAMAGE_MULTIPLIERS = constants_manager.get_multipliers()

# Экспортируем read-only версии
BASE_STATS_RO = constants_manager.get_base_stats()
SYSTEM_LIMITS_RO = constants_manager.get_system_limits()
TIME_CONSTANTS_RO = constants_manager.get_time_constants()
PROBABILITY_CONSTANTS_RO = constants_manager.get_probability_constants()

# Экспортируем утилиты
def get_float(mapping: Dict[str, Any], key: str, default: float) -> float:
    """Безопасное получение float значения"""
    value = mapping.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def get_int(mapping: Dict[str, Any], key: str, default: int) -> int:
    """Безопасное получение int значения"""
    value = mapping.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def get_bool(mapping: Dict[str, Any], key: str, default: bool) -> bool:
    """Безопасное получение bool значения"""
    value = mapping.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.lower().strip() in ("1", "true", "yes", "y", "on")
    return default

def canonicalize_damage_type(value: Union[str, DamageType, None]) -> Optional[DamageType]:
    """Канонизация типа урона"""
    return constants_manager.get_damage_type(str(value)) if value else None

def create_validation_rule(validation_type: str, rule_data: Dict[str, Any], 
                          error_message: str = "Валидация не пройдена") -> Dict[str, Any]:
    """Создание правила валидации"""
    return {
        "validation_type": validation_type,
        "rule_data": rule_data,
        "error_message": error_message
    }
