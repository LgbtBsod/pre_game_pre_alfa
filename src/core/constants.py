#!/usr/bin/env python3
"""
Централизованные константы для всего проекта AI-EVOLVE
"""

from enum import Enum
from typing import Dict, Any

# ============================================================================
# ТИПЫ УРОНА
# ============================================================================

class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"
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

# ============================================================================
# ТИПЫ ЭФФЕКТОВ
# ============================================================================

class EffectCategory(Enum):
    """Категории эффектов"""
    INSTANT = "instant"
    OVER_TIME = "over_time"
    BUFF = "buff"
    DEBUFF = "debuff"
    DOT = "dot"
    HOT = "hot"
    AURA = "aura"
    TRIGGER = "trigger"

class TriggerType(Enum):
    """Типы триггеров для эффектов"""
    ON_HIT = "on_hit"
    ON_CRIT = "on_crit"
    ON_KILL = "on_kill"
    ON_TAKE_DAMAGE = "on_take_damage"
    ON_HEAL = "on_heal"
    ON_SPELL_CAST = "on_spell_cast"
    ON_ITEM_USE = "on_item_use"
    ON_LEVEL_UP = "on_level_up"
    ON_RESIST = "on_resist"
    ON_EVOLUTION = "on_evolution"
    ON_DEATH = "on_death"
    ON_RESPAWN = "on_respawn"
    ON_ENTER_COMBAT = "on_enter_combat"
    ON_EXIT_COMBAT = "on_exit_combat"

# ============================================================================
# ТИПЫ ПРЕДМЕТОВ
# ============================================================================

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

class ItemCategory(Enum):
    """Категории предметов"""
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

# ============================================================================
# ТИПЫ СКИЛЛОВ
# ============================================================================

class SkillType(Enum):
    """Типы навыков"""
    COMBAT = "combat"
    UTILITY = "utility"
    PASSIVE = "passive"
    ACTIVE = "active"
    ULTIMATE = "ultimate"
    MOVEMENT = "movement"
    DEFENSIVE = "defensive"
    SUPPORT = "support"
    REACTIVE = "reactive"

class SkillCategory(Enum):
    """Категории навыков"""
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"
    HEALING = "healing"
    BUFF = "buff"
    DEBUFF = "debuff"
    MOVEMENT = "movement"
    DEFENSE = "defense"
    UTILITY = "utility"

# ============================================================================
# ТИПЫ ГЕНОВ
# ============================================================================

class GeneType(Enum):
    """Типы генов"""
    STRENGTH = "strength"
    AGILITY = "agility"
    INTELLIGENCE = "intelligence"
    CONSTITUTION = "constitution"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
    LUCK = "luck"
    VITALITY = "vitality"
    RESISTANCE = "resistance"
    ADAPTATION = "adaptation"
    MUTATION = "mutation"
    EVOLUTION = "evolution"

class GeneRarity(Enum):
    """Редкость генов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    DIVINE = "divine"

# ============================================================================
# ТИПЫ ЭВОЛЮЦИИ
# ============================================================================

class EvolutionStage(Enum):
    """Стадии эволюции"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"
    MASTER = "master"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    DIVINE = "divine"

class EvolutionType(Enum):
    """Типы эволюции"""
    NATURAL = "natural"
    FORCED = "forced"
    MUTATION = "mutation"
    FUSION = "fusion"
    ABSORPTION = "absorption"
    TRANSFORMATION = "transformation"

# ============================================================================
# ТИПЫ ЭМОЦИЙ
# ============================================================================

class EmotionType(Enum):
    """Типы эмоций"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    LOVE = "love"
    HATE = "hate"
    CONFUSION = "confusion"
    EXCITEMENT = "excitement"
    CALMNESS = "calmness"
    ANXIETY = "anxiety"

class EmotionIntensity(Enum):
    """Интенсивность эмоций"""
    MINIMAL = "minimal"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    INTENSE = "intense"
    OVERWHELMING = "overwhelming"

# ============================================================================
# ТИПЫ ВРАГОВ И БОССОВ
# ============================================================================

class EnemyType(Enum):
    """Типы врагов"""
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"
    FLYING = "flying"
    UNDEAD = "undead"
    BEAST = "beast"
    HUMAN = "human"
    DEMON = "demon"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    CONSTRUCT = "construct"
    ABERRATION = "aberration"

class BossType(Enum):
    """Типы боссов"""
    MINI_BOSS = "mini_boss"
    AREA_BOSS = "area_boss"
    DUNGEON_BOSS = "dungeon_boss"
    WORLD_BOSS = "world_boss"
    FINAL_BOSS = "final_boss"
    RAID_BOSS = "raid_boss"
    EVENT_BOSS = "event_boss"

# ============================================================================
# ТИПЫ AI
# ============================================================================

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

# ============================================================================
# ТИПЫ БОЯ
# ============================================================================

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

class AttackType(Enum):
    """Типы атак"""
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"
    SPECIAL = "special"
    COUNTER = "counter"
    AREA = "area"
    CHAIN = "chain"
    PIERCING = "piercing"

# ============================================================================
# ТИПЫ ХАРАКТЕРИСТИК
# ============================================================================

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

class StatCategory(Enum):
    """Категории характеристик"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    COMBAT = "combat"
    DEFENSIVE = "defensive"
    UTILITY = "utility"
    HIDDEN = "hidden"

# ============================================================================
# ТИПЫ КОНТЕНТА
# ============================================================================

class ContentType(Enum):
    """Типы контента"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    GENE = "gene"
    SKILL = "skill"
    EFFECT = "effect"
    MATERIAL = "material"
    ENEMY = "enemy"
    BOSS = "boss"
    NPC = "npc"
    QUEST = "quest"
    LOCATION = "location"

class ContentRarity(Enum):
    """Редкость контента"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    DIVINE = "divine"

# ============================================================================
# ТИПЫ UI
# ============================================================================

class UIElementType(Enum):
    """Типы UI элементов"""
    BUTTON = "button"
    LABEL = "label"
    INPUT = "input"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    LIST = "list"
    GRID = "grid"
    PANEL = "panel"
    WINDOW = "window"
    TOOLTIP = "tooltip"
    PROGRESS_BAR = "progress_bar"
    INVENTORY_SLOT = "inventory_slot"
    SKILL_SLOT = "skill_slot"
    STAT_DISPLAY = "stat_display"
    HEALTH_BAR = "health_bar"
    MANA_BAR = "mana_bar"
    EXPERIENCE_BAR = "experience_bar"

class UIState(Enum):
    """Состояния UI элементов"""
    NORMAL = "normal"
    HOVERED = "hovered"
    PRESSED = "pressed"
    DISABLED = "disabled"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FOCUSED = "focused"
    SELECTED = "selected"

# ============================================================================
# ТИПЫ РЕНДЕРИНГА
# ============================================================================

class RenderQuality(Enum):
    """Качество рендеринга"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    CUSTOM = "custom"

class RenderLayer(Enum):
    """Слои рендеринга"""
    BACKGROUND = "background"
    TERRAIN = "terrain"
    OBJECTS = "objects"
    ENTITIES = "entities"
    EFFECTS = "effects"
    UI = "ui"
    OVERLAY = "overlay"

# ============================================================================
# ТИПЫ СИСТЕМ
# ============================================================================

class SystemPriority(Enum):
    """Приоритеты систем"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"

class SystemState(Enum):
    """Состояния систем"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    PAUSED = "paused"
    ERROR = "error"
    DESTROYED = "destroyed"

# ============================================================================
# ТИПЫ СОБЫТИЙ
# ============================================================================

class EventType(Enum):
    """Типы событий"""
    # Системные события
    SYSTEM_INITIALIZED = "system_initialized"
    SYSTEM_ERROR = "system_error"
    SYSTEM_SHUTDOWN = "system_shutdown"
    
    # События сущностей
    ENTITY_CREATED = "entity_created"
    ENTITY_DESTROYED = "entity_destroyed"
    ENTITY_MOVED = "entity_moved"
    ENTITY_DAMAGED = "entity_damaged"
    ENTITY_HEALED = "entity_healed"
    ENTITY_LEVEL_UP = "entity_level_up"
    ENTITY_DIED = "entity_died"
    ENTITY_RESPAWNED = "entity_respawned"
    
    # Боевые события
    COMBAT_STARTED = "combat_started"
    COMBAT_ENDED = "combat_ended"
    ATTACK_PERFORMED = "attack_performed"
    DAMAGE_DEALT = "damage_dealt"
    DAMAGE_TAKEN = "damage_taken"
    RESIST_TAKEN = "resist_taken"
    BLOCK_TAKEN = "block_taken"
    EVASION_TAKEN = "evasion_taken"
    ENEMY_KILLED = "enemy_killed"
    ENEMY_ESCAPED = "enemy_escaped"
    ENEMY_EVADED = "enemy_evaded"
    ENEMY_BLOCKED = "enemy_blocked"
    ENEMY_DODGED = "enemy_dodged"
    ENEMY_RESISTED = "enemy_resisted"
    ENEMY_REFLECTED = "enemy_reflected"
    ENEMY_ABSORBED = "enemy_absorbed"
    ENEMY_DISPELLED = "enemy_dispelled"
    ENEMY_DIED = "enemy_died"
    ENEMY_HEALED = "enemy_healed"
    HEALING_RECEIVED = "healing_received"
    
    # События предметов
    ITEM_CREATED = "item_created"
    ITEM_DESTROYED = "item_destroyed"
    ITEM_USED = "item_used"
    ITEM_EQUIPPED = "item_equipped"
    ITEM_UNEQUIPPED = "item_unequipped"
    ITEM_ADDED_TO_INVENTORY = "item_added_to_inventory"
    ITEM_REMOVED_FROM_INVENTORY = "item_removed_from_inventory"
    
    # События навыков
    SKILL_LEARNED = "skill_learned"
    SKILL_USED = "skill_used"
    SKILL_LEVEL_UP = "skill_level_up"
    
    # События эффектов
    EFFECT_APPLIED = "effect_applied"
    EFFECT_REMOVED = "effect_removed"
    EFFECT_TRIGGERED = "effect_triggered"
    
    # События эволюции
    EVOLUTION_TRIGGERED = "evolution_triggered"
    EVOLUTION_COMPLETED = "evolution_completed"
    MUTATION_TRIGGERED = "mutation_triggered"
    
    # События AI
    AI_DECISION_MADE = "ai_decision_made"
    AI_ACTION_PERFORMED = "ai_action_performed"
    AI_STATE_CHANGED = "ai_state_changed"
    
    # События контента
    CONTENT_GENERATED = "content_generated"
    CONTENT_LOADED = "content_loaded"
    CONTENT_SAVED = "content_saved"

# ============================================================================
# КОНСТАНТЫ ЗНАЧЕНИЙ
# ============================================================================

# Базовые значения характеристик
BASE_STATS = {
    "health": 100,
    "mana": 50,
    "stamina": 100,
    "attack": 10,
    "defense": 5,
    "speed": 1.0,
    "intelligence": 10,
    "strength": 10,
    "agility": 10,
    "constitution": 10,
    "wisdom": 10,
    "charisma": 10,
    "luck": 5   
}

# Множители опыта
EXPERIENCE_MULTIPLIERS = {
    "normal": 1.0,
    "easy": 1.5,
    "hard": 0.7,
    "nightmare": 0.5
}

# Лимиты систем
SYSTEM_LIMITS = {
    "max_entities": 10000,
    "max_items": 100000,
    "max_effects": 1000,
    "max_skills": 1000,
    "max_ai_entities": 1000,
    "max_active_combats": 100,
    "max_inventory_slots": 100,
    "max_skill_tree_depth": 10
}

# Временные константы
TIME_CONSTANTS = {
    "tick_rate": 60.0,  # тиков в секунду
    "update_interval": 1.0 / 60.0,  # интервал обновления
    "save_interval": 300.0,  # интервал сохранения (5 минут)
    "cleanup_interval": 60.0,  # интервал очистки (1 минута)
    "combat_timeout": 300.0,  # таймаут боя (5 минут)
    "ai_decision_delay": 0.5,  # задержка решений AI
    "effect_update_interval": 1.0,  # интервал обновления эффектов
}

# Вероятности и шансы
PROBABILITY_CONSTANTS = {
    "base_critical_chance": 0.05,
    "base_dodge_chance": 0.1,
    "base_block_chance": 0.15,
    "base_mutation_chance": 0.01,
    "base_evolution_chance": 0.1,
    "base_drop_chance": 0.1,
    "base_craft_success": 0.8,
    "base_resist_chance": 0.1,
    "base_block_chance": 0.1,
    "base_dodge_chance": 0.1,
    "base_crit_chance": 0.05,
    "base_crit_multiplier": 2.0,
    "base_evasion_chance": 0.1,
}

# Множители урона по типам
DAMAGE_MULTIPLIERS = {
    DamageType.PHYSICAL: 1.0,
    DamageType.FIRE: 1.0,
    DamageType.ICE: 1.0,
    DamageType.LIGHTNING: 1.0,
    DamageType.POISON: 1.0,
    DamageType.HOLY: 1.0,
    DamageType.DARK: 1.0,
    DamageType.ARCANE: 1.0,
    DamageType.MAGIC: 1.0,
    DamageType.TRUE: 5.0,
    DamageType.ACID: 1.0,
    DamageType.COLD: 1.0,
    DamageType.NECROTIC: 1.0,
    DamageType.PSYCHIC: 1.0,
    DamageType.RADIANT: 1.0,
    DamageType.SHADOW: 1.0,
}

# Сопротивления по умолчанию
DEFAULT_RESISTANCES = {
    DamageType.PHYSICAL: 0.0,
    DamageType.FIRE: 0.0,
    DamageType.ICE: 0.0,
    DamageType.LIGHTNING: 0.0,
    DamageType.POISON: 0.0,
    DamageType.HOLY: 0.0,
    DamageType.DARK: 0.0,
    DamageType.ARCANE: 0.0,
    DamageType.MAGIC: 0.0,
    DamageType.TRUE: 0.0,
    DamageType.ACID: 0.0,
    DamageType.COLD: 0.0,
    DamageType.NECROTIC: 0.0,
    DamageType.PSYCHIC: 0.0,
    DamageType.RADIANT: 0.0,
    DamageType.SHADOW: 0.0,
}

# ============================================================================
# УТИЛИТЫ ДЛЯ РАБОТЫ С КОНСТАНТАМИ
# ============================================================================

def get_damage_type_by_name(name: str) -> DamageType:
    """Получение типа урона по имени"""
    try:
        return DamageType(name.lower())
    except ValueError:
        return DamageType.PHYSICAL

def get_item_type_by_name(name: str) -> ItemType:
    """Получение типа предмета по имени"""
    try:
        return ItemType(name.lower())
    except ValueError:
        return ItemType.MATERIAL

def get_rarity_by_name(name: str) -> ItemRarity:
    """Получение редкости по имени"""
    try:
        return ItemRarity(name.lower())
    except ValueError:
        return ItemRarity.COMMON

def get_enum_values(enum_class) -> list:
    """Получение всех значений перечисления"""
    return [e.value for e in enum_class]

def get_enum_names(enum_class) -> list:
    """Получение всех имен перечисления"""
    return [e.name for e in enum_class]

def is_valid_enum_value(enum_class, value: str) -> bool:
    """Проверка валидности значения перечисления"""
    try:
        enum_class(value)
        return True
    except ValueError:
        return False

# ============================================================================
# КОНВЕРТЕРЫ ДЛЯ СЕРИАЛИЗАЦИИ
# ============================================================================

def enum_to_dict(enum_class) -> Dict[str, str]:
    """Конвертация перечисления в словарь"""
    return {e.name: e.value for e in enum_class}

def dict_to_enum(enum_class, data: Dict[str, str]):
    """Конвертация словаря в перечисление"""
    return {k: enum_class(v) for k, v in data.items()}

# ============================================================================
# ВАЛИДАТОРЫ
# ============================================================================

def validate_damage_type(damage_type: str) -> bool:
    """Валидация типа урона"""
    return is_valid_enum_value(DamageType, damage_type)

def validate_item_type(item_type: str) -> bool:
    """Валидация типа предмета"""
    return is_valid_enum_value(ItemType, item_type)

def validate_rarity(rarity: str) -> bool:
    """Валидация редкости"""
    return is_valid_enum_value(ItemRarity, rarity)

def validate_skill_type(skill_type: str) -> bool:
    """Валидация типа навыка"""
    return is_valid_enum_value(SkillType, skill_type)

def validate_gene_type(gene_type: str) -> bool:
    """Валидация типа гена"""
    return is_valid_enum_value(GeneType, gene_type)

def validate_emotion_type(emotion_type: str) -> bool:
    """Валидация типа эмоции"""
    return is_valid_enum_value(EmotionType, emotion_type)

def validate_ai_behavior(behavior: str) -> bool:
    """Валидация поведения AI"""
    return is_valid_enum_value(AIBehavior, behavior)

def validate_combat_state(state: str) -> bool:
    """Валидация состояния боя"""
    return is_valid_enum_value(CombatState, state)

def validate_stat_type(stat_type: str) -> bool:
    """Валидация типа характеристики"""
    return is_valid_enum_value(StatType, stat_type)
