#!/usr/bin/env python3
"""
Расширенные константы для AI-EVOLVE
Дополнительные константы для обратной совместимости
"""

from .constants import constants_manager, DamageType, ItemType, ItemRarity, SkillType, StatType

# ============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ТИПЫ
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
    BELT = "belt"

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
    FIRE_AFFINITY = "fire_affinity"
    ICE_AFFINITY = "ice_affinity"
    LIGHTNING_AFFINITY = "lightning_affinity"
    EARTH_AFFINITY = "earth_affinity"
    WIND_AFFINITY = "wind_affinity"
    WATER_AFFINITY = "water_affinity"
    LIGHT_AFFINITY = "light_affinity"
    DARK_AFFINITY = "dark_affinity"
    TELEPATHY = "telepathy"
    TELEKINESIS = "telekinesis"
    SHAPESHIFTING = "shapeshifting"
    REGENERATION = "regeneration"
    IMMORTALITY = "immortality"
    PHASING = "phasing"
    TIME_MANIPULATION = "time_manipulation"
    SPACE_MANIPULATION = "space_manipulation"
    EMOTIONAL_STABILITY = "emotional_stability"
    EMPATHY = "empathy"
    COURAGE = "courage"
    CALMNESS = "calmness"
    AGGRESSION = "aggression"
    FEAR_RESISTANCE = "fear_resistance"
    MEMORY_ENHANCEMENT = "memory_enhancement"
    LEARNING_SPEED = "learning_speed"
    CREATIVITY = "creativity"
    LOGICAL_THINKING = "logical_thinking"
    INTUITION = "intuition"
    FOCUS = "focus"
    WINGS = "wings"
    SCALES = "scales"
    FUR = "fur"
    CLAWS = "claws"
    FANGS = "fangs"
    HORNS = "horns"
    TAIL = "tail"
    EXTRA_LIMBS = "extra_limbs"
    FAST_METABOLISM = "fast_metabolism"
    SLOW_METABOLISM = "slow_metabolism"
    TOXIN_RESISTANCE = "toxin_resistance"
    DISEASE_RESISTANCE = "disease_resistance"
    HEALING_FACTOR = "healing_factor"
    AGING_RESISTANCE = "aging_resistance"
    LEADERSHIP = "leadership"
    DIPLOMACY = "diplomacy"
    INTIMIDATION = "intimidation"
    PERSUASION = "persuasion"
    TEAMWORK = "teamwork"
    SOLITARY = "solitary"
    CRAFTING_MASTERY = "crafting_mastery"
    COMBAT_MASTERY = "combat_mastery"
    MAGIC_MASTERY = "magic_mastery"
    STEALTH_MASTERY = "stealth_mastery"
    SURVIVAL_MASTERY = "survival_mastery"
    EXPLORATION_MASTERY = "exploration_mastery"

class GeneRarity(Enum):
    """Редкость генов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    DIVINE = "divine"

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
    
    def __lt__(self, other):
        if isinstance(other, EvolutionStage):
            order = {
                EvolutionStage.BASIC: 0,
                EvolutionStage.INTERMEDIATE: 1,
                EvolutionStage.ADVANCED: 2,
                EvolutionStage.ELITE: 3,
                EvolutionStage.MASTER: 4,
                EvolutionStage.LEGENDARY: 5,
                EvolutionStage.MYTHIC: 6,
                EvolutionStage.DIVINE: 7
            }
            return order[self] < order[other]
        return NotImplemented

class EvolutionType(Enum):
    """Типы эволюции"""
    NATURAL = "natural"
    FORCED = "forced"
    MUTATION = "mutation"
    FUSION = "fusion"
    ABSORPTION = "absorption"
    TRANSFORMATION = "transformation"
    FIRE_EVOLUTION = "fire_evolution"
    ICE_EVOLUTION = "ice_evolution"
    LIGHTNING_EVOLUTION = "lightning_evolution"
    EARTH_EVOLUTION = "earth_evolution"
    WIND_EVOLUTION = "wind_evolution"
    WATER_EVOLUTION = "water_evolution"
    LIGHT_EVOLUTION = "light_evolution"
    DARK_EVOLUTION = "dark_evolution"
    PSYCHIC_EVOLUTION = "psychic_evolution"
    TECHNOLOGICAL_EVOLUTION = "technological_evolution"
    SPIRITUAL_EVOLUTION = "spiritual_evolution"
    CHAOS_EVOLUTION = "chaos_evolution"
    ORDER_EVOLUTION = "order_evolution"
    VOID_EVOLUTION = "void_evolution"
    HYBRID_EVOLUTION = "hybrid_evolution"
    CHIMERA_EVOLUTION = "chimera_evolution"
    SYMBIOTIC_EVOLUTION = "symbiotic_evolution"
    PARASITIC_EVOLUTION = "parasitic_evolution"
    COSMIC_EVOLUTION = "cosmic_evolution"
    DIMENSIONAL_EVOLUTION = "dimensional_evolution"
    TEMPORAL_EVOLUTION = "temporal_evolution"
    QUANTUM_EVOLUTION = "quantum_evolution"

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
    EUPHORIA = "euphoria"
    CONTENTMENT = "contentment"
    GRATITUDE = "gratitude"
    HOPE = "hope"
    INSPIRATION = "inspiration"
    PRIDE = "pride"
    SATISFACTION = "satisfaction"
    WONDER = "wonder"
    AMUSEMENT = "amusement"
    ADMIRATION = "admiration"
    DESPAIR = "despair"
    RAGE = "rage"
    TERROR = "terror"
    SHAME = "shame"
    GUILT = "guilt"
    ENVY = "envy"
    JEALOUSY = "jealousy"
    DISAPPOINTMENT = "disappointment"
    FRUSTRATION = "frustration"
    LONELINESS = "loneliness"
    EMPATHY = "empathy"
    COMPASSION = "compassion"
    CONTEMPT = "contempt"
    INDIGNATION = "indignation"
    SYMPATHY = "sympathy"
    PITY = "pity"
    RESPECT = "respect"
    DISRESPECT = "disrespect"
    LOYALTY = "loyalty"
    CURIOSITY = "curiosity"
    INTEREST = "interest"
    BOREDOM = "boredom"
    FASCINATION = "fascination"
    PERPLEXITY = "perplexity"
    CERTAINTY = "certainty"
    DOUBT = "doubt"
    AWE = "awe"
    BEAUTY = "beauty"
    SUBLIME = "sublime"
    UGLINESS = "ugliness"
    HARMONY = "harmony"
    DISCORD = "discord"
    RIGHTEOUSNESS = "righteousness"
    REMORSE = "remorse"
    INNOCENCE = "innocence"
    CORRUPTION = "corruption"
    HONOR = "honor"
    DISHONOR = "dishonor"
    MEANINGFULNESS = "meaningfulness"
    MEANINGLESSNESS = "meaninglessness"
    TRANSCENDENCE = "transcendence"
    ISOLATION = "isolation"
    CONNECTION = "connection"
    DISCONNECTION = "disconnection"

class EmotionIntensity(Enum):
    """Интенсивность эмоций"""
    MINIMAL = "minimal"
    WEAK = "weak"
    LOW = "low"
    MODERATE = "moderate"
    MEDIUM = "medium"
    STRONG = "strong"
    HIGH = "high"
    INTENSE = "intense"
    EXTREME = "extreme"
    OVERWHELMING = "overwhelming"

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

class AttackType(Enum):
    """Типы атак"""
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"
    SPECIAL = "special"
    CRITICAL = "critical"
    COUNTER = "counter"
    AREA = "area"
    CHAIN = "chain"
    PIERCING = "piercing"

class StatCategory(Enum):
    """Категории характеристик"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    COMBAT = "combat"
    DEFENSIVE = "defensive"
    UTILITY = "utility"
    HIDDEN = "hidden"

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

class WorldObjectType(Enum):
    """Типы объектов мира"""
    OBSTACLE = "obstacle"
    TRAP = "trap"
    CHEST = "chest"
    ENEMY = "enemy"
    GEO_OBSTACLE = "geo_obstacle"
    DECORATION = "decoration"

class ObjectCategory(Enum):
    """Категории объектов"""
    COMBAT = "combat"
    EXPLORATION = "exploration"
    ENVIRONMENT = "environment"
    REWARDS = "rewards"

class ObjectState(Enum):
    """Состояния объектов"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DESTROYED = "destroyed"
    TRIGGERED = "triggered"
    LOCKED = "locked"

class CreatorMode(Enum):
    """Режимы создания"""
    PLACEMENT = "placement"
    EDIT = "edit"
    PREVIEW = "preview"
    CLEAR = "clear"

class ToolType(Enum):
    """Типы инструментов"""
    SELECT = "select"
    PLACE = "place"
    MOVE = "move"
    ROTATE = "rotate"
    SCALE = "scale"
    DELETE = "delete"
    COPY = "copy"
    PASTE = "paste"

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

class ItemCategory(Enum):
    """Категории предметов (для совместимости)"""
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

class ItemSlot(Enum):
    """Слоты экипировки"""
    WEAPON = "weapon"
    ARMOR_HEAD = "armor_head"
    ARMOR_CHEST = "armor_chest"
    ARMOR_LEGS = "armor_legs"
    ARMOR_FEET = "armor_feet"
    ACCESSORY_1 = "accessory_1"
    ACCESSORY_2 = "accessory_2"
    ACCESSORY_3 = "accessory_3"

# ============================================================================
# ДОПОЛНИТЕЛЬНЫЕ КОНСТАНТЫ
# ============================================================================

# Шаблоны генерации навыков
SKILL_GENERATION_TEMPLATES = {
    "attack": {
        "name_patterns": ["Slash", "Strike", "Thrust", "Cleave", "Smash"],
        "base_damage": 20,
        "mana_cost": 10,
        "cooldown": 3.0,
        "range": 1.5,
        "effects": ["damage"],
        "requirements": ["strength"],
        "animation": "attack"
    },
    "magic": {
        "name_patterns": ["Fireball", "Ice Bolt", "Lightning", "Arcane Blast", "Shadow Bolt"],
        "base_damage": 25,
        "mana_cost": 20,
        "cooldown": 5.0,
        "range": 5.0,
        "effects": ["damage", "elemental"],
        "requirements": ["intelligence"],
        "animation": "cast"
    },
    "healing": {
        "name_patterns": ["Heal", "Cure", "Restore", "Regenerate", "Revitalize"],
        "base_healing": 30,
        "mana_cost": 25,
        "cooldown": 8.0,
        "range": 3.0,
        "effects": ["healing"],
        "requirements": ["wisdom"],
        "animation": "heal"
    }
}

# Множители силы навыков
SKILL_POWER_MULTIPLIERS = {
    "common": 1.0,
    "uncommon": 1.2,
    "rare": 1.5,
    "epic": 2.0,
    "legendary": 3.0,
    "mythic": 4.0,
    "divine": 5.0
}

# Формулы расчета характеристик
STAT_CALCULATION_FORMULAS = {
    "health": lambda base, level, bonus: int(base * (1 + level * 0.1) + bonus),
    "mana": lambda base, level, bonus: int(base * (1 + level * 0.15) + bonus),
    "stamina": lambda base, level, bonus: int(base * (1 + level * 0.12) + bonus),
    "attack": lambda base, level, bonus: int(base * (1 + level * 0.08) + bonus),
    "defense": lambda base, level, bonus: int(base * (1 + level * 0.06) + bonus),
    "speed": lambda base, level, bonus: base * (1 + level * 0.02) + bonus,
    "critical_chance": lambda base, level, bonus: min(0.95, base + level * 0.01 + bonus),
    "critical_multiplier": lambda base, level, bonus: base + level * 0.05 + bonus
}

# Настройки мира
WORLD_SETTINGS = {
    "max_objects": 1000,
    "world_bounds": (-50, 50, -50, 50),
    "collision_enabled": True,
    "physics_enabled": True,
    "grid_snap": True,
    "grid_size": 1.0,
    "weather_enabled": False,
    "show_preview": True,
    "auto_save": True,
    "auto_save_interval": 300.0
}

# Настройки камеры
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

# Настройки UI
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

# Цвета для UI
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

# Шаблоны объектов
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
    }
}

# Экспортируем все для обратной совместимости
__all__ = [
    'EffectCategory', 'TriggerType', 'WeaponType', 'ArmorType', 'AccessoryType',
    'ConsumableType', 'SkillCategory', 'GeneType', 'GeneRarity', 'EvolutionStage',
    'EvolutionType', 'EmotionType', 'EmotionIntensity', 'EnemyType', 'BossType',
    'AttackType', 'StatCategory', 'ContentType', 'ContentRarity', 'UIElementType',
    'UIState', 'RenderQuality', 'RenderLayer', 'WorldObjectType', 'ObjectCategory',
    'ObjectState', 'CreatorMode', 'ToolType', 'SystemPriority', 'SystemState',
    'ItemCategory', 'ItemSlot', 'SKILL_GENERATION_TEMPLATES', 'SKILL_POWER_MULTIPLIERS',
    'STAT_CALCULATION_FORMULAS', 'WORLD_SETTINGS', 'CAMERA_SETTINGS', 'UI_SETTINGS',
    'UI_COLORS', 'DEFAULT_OBJECT_TEMPLATES'
]
