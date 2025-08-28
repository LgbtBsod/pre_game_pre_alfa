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
    PIERCING = "piercing"  # Пробивающий урон
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
    COMBINED = "combined"

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
    ON_COMBINE = "on_combine"

# ============================================================================
# ТИПЫ ПРЕДМЕТОВ
# ============================================================================

class ItemType(Enum):
    """Типы предметов (основные категории)"""
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
    CURSED = "cursed"
    TAMED = "tamed"
    EXOTIC = "exotic"
    ULTIMATE = "ultimate"

# Убираем дублирующий ItemCategory, используем ItemType

class WeaponType(Enum):
    """Типы оружия"""
    SWORD = "sword"
    AXE = "axe"
    BOW = "bow"
    STAFF = "staff"
    DAGGER = "dagger"
    MACE = "mace"
    SPEAR = "spear"
    HAMMER = "hammer"
    CROSSBOW = "crossbow"
    WAND = "wand"
    GUN = "gun"
    LASER = "laser"
    PLASMA = "plasma"
    QUANTUM = "quantum"

class ArmorType(Enum):
    """Типы брони"""
    HELMET = "helmet"
    CHESTPLATE = "chestplate"
    GREAVES = "greaves"
    BOOTS = "boots"
    SHIELD = "shield"
    GLOVES = "gloves"
    PAULDRONS = "pauldrons"
    BELT = "belt"
    CLOAK = "cloak"
    ROBE = "robe"
    PLATE = "plate"
    LEATHER = "leather"
    CHAIN = "chain"
    CLOTH = "cloth"

class AccessoryType(Enum):
    """Типы аксессуаров"""
    RING = "ring"
    NECKLACE = "necklace"
    EARRING = "earring"
    BRACELET = "bracelet"
    AMULET = "amulet"
    TALISMAN = "talisman"
    MEDALLION = "medallion"
    CRYSTAL = "crystal"
    ORB = "orb"
    SCROLL = "scroll"
    POTION = "potion"
    ELIXIR = "elixir"
    BELT = "belt"  # Добавляем недостающий тип

class ConsumableType(Enum):
    """Типы расходников"""
    HEALTH_POTION = "health_potion"
    MANA_POTION = "mana_potion"
    STAMINA_POTION = "stamina_potion"
    ANTIDOTE = "antidote"
    CURE_POISON = "cure_poison"
    CURE_DISEASE = "cure_disease"
    CURE_CURSE = "cure_curse"
    RESURRECTION = "resurrection"
    TELEPORT = "teleport"
    INVISIBILITY = "invisibility"
    SPEED_BOOST = "speed_boost"
    STRENGTH_BOOST = "strength_boost"
    INTELLIGENCE_BOOST = "intelligence_boost"
    AGILITY_BOOST = "agility_boost"

# ============================================================================
# ТИПЫ СКИЛЛОВ
# ============================================================================

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
    COMBAT = "combat"


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
    DAMAGE_COMBINATION = "damage_combination"

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
# ТИПЫ ОБЪЕКТОВ МИРА (ТВОРЕЦ МИРА)
# ============================================================================

class WorldObjectType(Enum):
    """Типы объектов, которые может создавать пользователь"""
    OBSTACLE = "obstacle"           # Препятствие
    TRAP = "trap"                   # Ловушка
    CHEST = "chest"                 # Сундук с наградой
    ENEMY = "enemy"                 # Враг
    GEO_OBSTACLE = "geo_obstacle"   # Географическое препятствие
    DECORATION = "decoration"       # Декорация

class ObjectCategory(Enum):
    """Категории объектов для создания"""
    COMBAT = "combat"               # Боевые объекты
    EXPLORATION = "exploration"     # Исследовательские объекты
    ENVIRONMENT = "environment"     # Окружающая среда
    REWARDS = "rewards"             # Награды

class ObjectState(Enum):
    """Состояния объектов в мире"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DESTROYED = "destroyed"
    TRIGGERED = "triggered"
    LOCKED = "locked"

class CreatorMode(Enum):
    """Режимы создания объектов"""
    PLACEMENT = "placement"         # Размещение объектов
    EDIT = "edit"                   # Редактирование объектов
    PREVIEW = "preview"             # Предварительный просмотр
    CLEAR = "clear"                 # Очистка мира

class ToolType(Enum):
    """Типы инструментов для создания"""
    SELECT = "select"               # Выбор объектов
    PLACE = "place"                 # Размещение объектов
    MOVE = "move"                   # Перемещение объектов
    ROTATE = "rotate"               # Поворот объектов
    SCALE = "scale"                 # Масштабирование объектов
    DELETE = "delete"               # Удаление объектов
    COPY = "copy"                   # Копирование объектов
    PASTE = "paste"                 # Вставка объектов

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
    # Основные характеристики
    "health": 100,
    "mana": 50,
    "stamina": 100,
    
    # Боевые характеристики
    "attack": 10,
    "defense": 5,
    "speed": 1.0,
    
    # Атрибуты
    "intelligence": 10,
    "strength": 10,
    "agility": 10,
    "constitution": 10,
    "wisdom": 10,
    "charisma": 10,
    "luck": 5,
    
    # Механика стойкости
    "toughness": 100,
    "toughness_resistance": 0.0,
    "stun_resistance": 0.0,
    "break_efficiency": 1.0,
}

# Характеристики для предметов (наследуют от BASE_STATS)
ITEM_STATS = {
    "weapon": {
        # Боевые характеристики
        "attack": 0,
        "speed": 0,
        "critical_chance": 0,
        "critical_multiplier": 0,
        "damage_type": None,
        
        # Механика стойкости
        "toughness_damage": 0,
        "break_efficiency": 0,
    },
    "armor": {
        # Защитные характеристики
        "defense": 0,
        "health": 0,
        "mana": 0,
        "stamina": 0,
        "resistance": {},  # Сопротивления по типам урона
        
        # Механика стойкости
        "toughness_resistance": 0,
        "stun_resistance": 0,
    },
    "accessory": {
        # Атрибуты
        "intelligence": 0,
        "strength": 0,
        "agility": 0,
        "constitution": 0,
        "wisdom": 0,
        "charisma": 0,
        "luck": 0,
        
        # Специальные эффекты
        "special_effects": [],
    },
    "consumable": {
        # Восстановление
        "healing": 0,
        "mana_restore": 0,
        "stamina_restore": 0,
        "duration": 0,
        
        # Временные эффекты
        "effects": [],
    }
}

# Механика стойкости
TOUGHNESS_MECHANICS = {
    # Базовые параметры
    "base_toughness": 100,
    "break_threshold": 0,  # Порог пробития стойкости
    
    # Восстановление
    "toughness_regen_rate": 10,  # Восстановление стойкости в секунду
    "toughness_regen_delay": 3.0,  # Задержка перед восстановлением
    
    # Эффекты пробития
    "stun_duration": 2.0,  # Длительность оглушения при пробитии
    "weakness_multiplier": 2.0,  # Множитель урона по стойкости при слабости
    "break_efficiency_cap": 3.0,  # Максимальная эффективность пробития
}

# Типы слабостей врагов (какие типы урона эффективны против стойкости)
ENEMY_WEAKNESSES = {
    # Физические слабости
    "physical_weak": [DamageType.PHYSICAL, DamageType.PIERCING],
    
    # Элементальные слабости
    "fire_weak": [DamageType.FIRE, DamageType.ENERGY],
    "ice_weak": [DamageType.ICE, DamageType.COLD],
    "lightning_weak": [DamageType.LIGHTNING, DamageType.ENERGY],
    
    # Химические слабости
    "poison_weak": [DamageType.POISON, DamageType.ACID],
    
    # Магические слабости
    "holy_weak": [DamageType.HOLY, DamageType.RADIANT],
    "dark_weak": [DamageType.DARK, DamageType.SHADOW],
    "arcane_weak": [DamageType.ARCANE, DamageType.MAGIC],
    
    # Специальные слабости
    "genetic_weak": [DamageType.GENETIC, DamageType.EMOTIONAL],
    "chaos_weak": [DamageType.CHAOS, DamageType.VIBRATION],
}

# Множители опыта по сложности
EXPERIENCE_MULTIPLIERS = {
    "easy": 1.5,      # Легкий режим
    "normal": 1.0,    # Обычный режим
    "hard": 0.7,      # Сложный режим
    "nightmare": 0.5  # Кошмарный режим
}

# Лимиты систем
SYSTEM_LIMITS = {
    # Основные лимиты
    "max_entities": 10000,
    "max_items": 100000,
    "max_effects": 1000,
    "max_skills": 1000,
    "max_ai_entities": 1000,
    "max_level": 100,
    
    # Система боя
    "max_active_combats": 100,
    "max_combat_participants": 50,
    "max_combat_duration": 1800.0,  # 30 минут
    "max_combat_effects": 100,
    
    # Система инвентаря
    "max_inventory_slots": 100,
    "max_inventory_weight": 1000.0,
    "max_equipment_slots": 10,
    "max_item_stack_size": 999,
    "max_item_level": 100,
    
    # Система навыков
    "max_skills_per_entity": 20,
    "max_skill_level": 100,
    "max_skill_requirements": 10,
    "max_skill_tree_depth": 10,
    
    # Система эффектов
    "max_effects_per_entity": 50,
    "max_effect_duration": 3600.0,  # 1 час
    "max_effect_stacks": 99,
    "max_special_effects": 100,
    
    # Система урона
    "max_damage_modifiers": 50,
    "max_damage_combinations": 20,
    "max_catalytic_effects": 30,
    "max_resistance_types": 25,
    "max_armor_value": 1000,
    "max_damage_value": 10000,
    "max_critical_multiplier": 10.0,
    "max_penetration_value": 100.0,
    
    # Система генома и эволюции
    "max_genes_per_entity": 20,
    "max_gene_combinations": 100,
    "max_mutation_chance": 0.5,
    "max_evolution_stages": 10,
    
    # Система эмоций
    "max_emotions_per_entity": 10,
    "max_emotion_intensity": 100,
    "max_emotion_duration": 3600.0,
    "max_emotional_triggers": 50,
    
    # Система крафтинга
    "max_crafting_sessions": 10,
    "max_crafting_queue": 5,
    "max_recipe_requirements": 20,
    "max_crafting_time": 3600.0,
    
    # Система рендеринга
    "target_fps": 60,
    "max_draw_distance": 1000.0,
    "max_particles": 10000,
    "max_light_sources": 100,
    
    # Система UI
    "max_ui_elements": 500,
    "max_ui_layers": 10,
    "max_ui_animations": 100,
    "max_ui_events": 1000,
    
    # Режим "творец мира"
    "max_world_objects": 1000,
    "max_object_templates": 100,
    "max_creator_modes": 10,
    "max_grid_size": 200,
    "max_camera_zoom": 5.0,
    "min_camera_zoom": 0.1,
    
    # Другие системы
    "max_quests": 50,
    "max_party_size": 4,
    "max_guild_size": 100,
    "max_trade_items": 20,
    "max_currency_amount": 999999,
    "max_experience": 999999999,
    "max_reputation": 1000,
    "max_fame": 1000,
    "max_infamy": 1000,
    "max_honor": 1000,
    "max_disgrace": 1000,
    "max_enemy_level": 100,
    "max_memory_entries": 1000,
    "max_memory_level": 100,
    "max_experience_per_type": 999999,
    "max_skill_memory": 50,
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
    # Временные константы для режима "творца мира"
    "creator_update_interval": 1.0 / 30.0,  # интервал обновления творца мира
    "object_placement_delay": 0.1,  # задержка размещения объектов
    "ui_animation_duration": 0.3,  # длительность анимации UI
    "grid_update_interval": 1.0,  # интервал обновления сетки
    # Временные константы для системы урона
    "damage_effect_duration": 0.5,  # длительность эффекта урона
    "critical_hit_duration": 1.0,   # длительность критического удара
    "damage_combination_delay": 0.2, # задержка комбинации урона
    "catalytic_effect_duration": 2.0, # длительность каталитического эффекта
    "damage_modifier_cleanup": 5.0,   # интервал очистки модификаторов урона
    # Временные константы для системы эффектов
    "effect_cleanup_interval": 60.0,  # интервал очистки эффектов
    "effect_update_interval": 0.1,    # интервал обновления эффектов
    "effect_animation_duration": 0.5, # длительность анимации эффекта
    # Временные константы для системы скиллов
    "skill_cooldown_tolerance": 0.1,  # допуск для кулдауна скиллов
    "skill_animation_duration": 1.0,  # длительность анимации скилла
    "skill_effect_delay": 0.1,        # задержка эффекта скилла
    # Временные константы для системы инвентаря
    "item_use_delay": 0.5,            # задержка использования предмета
    "equipment_change_delay": 0.2,    # задержка смены экипировки
    "inventory_update_interval": 0.1, # интервал обновления инвентаря
    # Временные константы для системы памяти
    "memory_update_interval": 1.0,    # интервал обновления памяти
    "experience_decay_interval": 3600.0, # интервал затухания опыта
    "memory_cleanup_interval": 300.0,    # интервал очистки памяти
    # Временные константы для системы генома
    "mutation_check_interval": 10.0,  # интервал проверки мутаций
    "evolution_trigger_delay": 5.0,   # задержка триггера эволюции
    "gene_expression_interval": 1.0,  # интервал экспрессии генов
    # Временные константы для системы эмоций
    "emotion_update_interval": 0.5,   # интервал обновления эмоций
    "emotion_decay_interval": 10.0,   # интервал затухания эмоций
    "emotional_trigger_delay": 1.0,   # задержка эмоционального триггера
    # Временные константы для системы крафтинга
    "crafting_progress_interval": 0.1, # интервал прогресса крафтинга
    "recipe_validation_delay": 0.5,    # задержка валидации рецепта
    "crafting_completion_delay": 1.0,  # задержка завершения крафтинга
    # Временные константы для системы боя
    "combat_turn_duration": 1.0,      # длительность хода в бою
    "combat_effect_delay": 0.2,        # задержка эффекта в бою
    "combat_animation_duration": 0.5,  # длительность анимации боя
    # Временные константы для системы рендеринга
    "frame_time_target": 1.0 / 60.0,  # целевое время кадра
    "particle_update_interval": 0.016, # интервал обновления частиц
    "light_update_interval": 0.1,      # интервал обновления освещения
    # Временные константы для системы UI
    "ui_update_interval": 0.016,       # интервал обновления UI
    "ui_animation_duration": 0.3,      # длительность анимации UI
    "ui_event_delay": 0.1              # задержка событий UI
}

# Вероятности и шансы
PROBABILITY_CONSTANTS = {
    # Базовые шансы
    "base_critical_chance": 0.05,
    "base_dodge_chance": 0.1,
    "base_block_chance": 0.15,
    "base_mutation_chance": 0.01,
    "base_evolution_chance": 0.1,
    "base_drop_chance": 0.1,
    "base_craft_success": 0.8,
    "base_resist_chance": 0.1,
    "base_evasion_chance": 0.1,
    "base_luck": 0.05,
    
    # Система урона
    "base_damage_penetration": 0.0,
    "base_elemental_affinity": 1.0,
    "base_armor_reduction": 0.01,  # 1 armor = 1% reduction
    "base_resistance_cap": 0.95,   # Максимальное сопротивление 95%
    "base_damage_floor": 1,        # Минимальный урон
    "base_damage_ceiling": 999999, # Максимальный урон
    
    # Комбинации урона
    "base_combination_chance": 0.1,
    "base_catalytic_chance": 0.05,
    "base_damage_combination_threshold": 3,
    
    # Критические удары
    "max_critical_chance": 0.95,
    "min_critical_multiplier": 1.5,
    "max_critical_multiplier": 10.0
}

# Сопротивления по умолчанию (автоматически генерируются)
# DEFAULT_RESISTANCES = generate_damage_constants()[0]

# Автоматическое заполнение сопротивлений и бустов на основе типов урона
def generate_damage_constants():
    """Автоматическая генерация констант для типов урона"""
    resistances = {}
    boosts = {}
    
    for damage_type in DamageType:
        if damage_type == DamageType.TRUE:
            # Истинный урон нельзя сопротивляться, базовый буст 5.0
            resistances[damage_type] = 0.0
            boosts[damage_type] = 5.0
        elif damage_type in [DamageType.PHYSICAL, DamageType.PIERCING]:
            # Физические типы урона
            resistances[damage_type] = 0.0
            boosts[damage_type] = 1.2
        elif damage_type in [DamageType.FIRE, DamageType.ICE, DamageType.LIGHTNING]:
            # Элементальные типы урона
            resistances[damage_type] = 0.0
            boosts[damage_type] = 1.5
        elif damage_type in [DamageType.GENETIC, DamageType.EMOTIONAL]:
            # Специальные типы урона
            resistances[damage_type] = 0.0
            boosts[damage_type] = 2.0
        else:
            # Остальные типы урона
            resistances[damage_type] = 0.0
            boosts[damage_type] = 1.0
    
    return resistances, boosts

# Генерируем константы автоматически
DEFAULT_RESISTANCES, DAMAGE_MULTIPLIERS = generate_damage_constants()

# ============================================================================
# КОНСТАНТЫ РЕЖИМА "ТВОРЕЦ МИРА"
# ============================================================================

# Настройки мира по умолчанию
WORLD_SETTINGS = {
    # Лимиты
    "max_objects": 1000,
    "world_bounds": (-50, 50, -50, 50),
    
    # Физика и коллизии
    "collision_enabled": True,
    "physics_enabled": True,
    
    # Сетка и размещение
    "grid_snap": True,
    "grid_size": 1.0,
    
    # Дополнительные функции
    "weather_enabled": False,
    "show_preview": True,
    
    # Автосохранение
    "auto_save": True,
    "auto_save_interval": 300.0,  # 5 минут
}

# Настройки камеры по умолчанию
CAMERA_SETTINGS = {
    "default_zoom": 1.0,
    "min_zoom": 0.1,
    "max_zoom": 5.0,
    "zoom_speed": 0.1,
    "pan_speed": 1.0,
    "rotation_speed": 1.0,
    "orthographic": True,
    "film_size": (40, 30),
    "near_far": (-100, 100)
}

# Настройки UI по умолчанию
UI_SETTINGS = {
    "theme": "dark",
    "font_size": 14,
    "button_size": (100, 30),
    "panel_opacity": 0.8,
    "animation_enabled": True,
    "auto_layout_enabled": True,
    "theme_switching_enabled": True,
    "event_bubbling_enabled": True
}

# Шаблоны объектов по умолчанию
DEFAULT_OBJECT_TEMPLATES = {
    "wall": {
        "name": "Стена",
        "type": WorldObjectType.OBSTACLE,
        "category": ObjectCategory.ENVIRONMENT,
        "description": "Непроходимое препятствие",
        "icon": "🧱",
        "cost": 10,
        "unlock_level": 1,
        "properties": {
            "width": 2.0,
            "height": 3.0,
            "depth": 0.5,
            "color": (0.5, 0.5, 0.5, 1.0),
            "collision": True,
            "destructible": False
        }
    },
    "spikes": {
        "name": "Шипы",
        "type": WorldObjectType.TRAP,
        "category": ObjectCategory.COMBAT,
        "description": "Ловушка, наносящая урон",
        "icon": "🗡️",
        "cost": 25,
        "unlock_level": 2,
        "properties": {
            "width": 1.0,
            "height": 0.5,
            "depth": 1.0,
            "color": (0.8, 0.2, 0.2, 1.0),
            "damage": 20,
            "trigger_type": "step",
            "hidden": True
        }
    },
    "chest": {
        "name": "Сундук",
        "type": WorldObjectType.CHEST,
        "category": ObjectCategory.REWARDS,
        "description": "Содержит награды",
        "icon": "📦",
        "cost": 50,
        "unlock_level": 1,
        "properties": {
            "width": 1.0,
            "height": 1.0,
            "depth": 1.0,
            "color": (0.6, 0.4, 0.2, 1.0),
            "loot_quality": "common",
            "loot_count": 3,
            "locked": False
        }
    },
    "goblin": {
        "name": "Гоблин",
        "type": WorldObjectType.ENEMY,
        "category": ObjectCategory.COMBAT,
        "description": "Слабый, но быстрый враг",
        "icon": "👹",
        "cost": 30,
        "unlock_level": 1,
        "properties": {
            "width": 0.8,
            "height": 1.5,
            "depth": 0.8,
            "color": (0.2, 0.8, 0.2, 1.0),
            "health": 30,
            "damage": 8,
            "speed": 3.0,
            "ai_type": "aggressive",
            "loot_drop": True
        }
    }
}

# Цвета для UI элементов
UI_COLORS = {
    "primary": (51, 122, 183, 255),
    "secondary": (92, 184, 92, 255),
    "success": (92, 184, 92, 255),
    "warning": (240, 173, 78, 255),
    "danger": (217, 83, 79, 255),
    "info": (91, 192, 222, 255),
    "light": (248, 249, 250, 255),
    "dark": (52, 58, 64, 255),
    "white": (255, 255, 255, 255),
    "black": (0, 0, 0, 255),
    "transparent": (0, 0, 0, 0),
    "grid": (0.3, 0.3, 0.3, 0.5),
    "selection": (0, 255, 255, 0.5),
    "preview": (255, 255, 0, 0.3)
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

def validate_world_object_type(object_type: str) -> bool:
    """Валидация типа объекта мира"""
    return is_valid_enum_value(WorldObjectType, object_type)

def validate_object_category(category: str) -> bool:
    """Валидация категории объекта"""
    return is_valid_enum_value(ObjectCategory, category)

def validate_object_state(state: str) -> bool:
    """Валидация состояния объекта"""
    return is_valid_enum_value(ObjectState, state)

def validate_creator_mode(mode: str) -> bool:
    """Валидация режима создания"""
    return is_valid_enum_value(CreatorMode, mode)

def validate_tool_type(tool_type: str) -> bool:
    """Валидация типа инструмента"""
    return is_valid_enum_value(ToolType, tool_type)
