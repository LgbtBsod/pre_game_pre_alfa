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
    MAGICAL = "magical"
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
# Но добавляем обратно для совместимости с существующим кодом
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
    # Базовые атрибуты
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
    
    # Новые расширенные типы генов
    # Элементальные гены
    FIRE_AFFINITY = "fire_affinity"
    ICE_AFFINITY = "ice_affinity"
    LIGHTNING_AFFINITY = "lightning_affinity"
    EARTH_AFFINITY = "earth_affinity"
    WIND_AFFINITY = "wind_affinity"
    WATER_AFFINITY = "water_affinity"
    LIGHT_AFFINITY = "light_affinity"
    DARK_AFFINITY = "dark_affinity"
    
    # Специальные способности
    TELEPATHY = "telepathy"
    TELEKINESIS = "telekinesis"
    SHAPESHIFTING = "shapeshifting"
    REGENERATION = "regeneration"
    IMMORTALITY = "immortality"
    PHASING = "phasing"
    TIME_MANIPULATION = "time_manipulation"
    SPACE_MANIPULATION = "space_manipulation"
    
    # Эмоциональные гены
    EMOTIONAL_STABILITY = "emotional_stability"
    EMPATHY = "empathy"
    COURAGE = "courage"
    CALMNESS = "calmness"
    AGGRESSION = "aggression"
    FEAR_RESISTANCE = "fear_resistance"
    
    # Когнитивные гены
    MEMORY_ENHANCEMENT = "memory_enhancement"
    LEARNING_SPEED = "learning_speed"
    CREATIVITY = "creativity"
    LOGICAL_THINKING = "logical_thinking"
    INTUITION = "intuition"
    FOCUS = "focus"
    
    # Физические мутации
    WINGS = "wings"
    SCALES = "scales"
    FUR = "fur"
    CLAWS = "claws"
    FANGS = "fangs"
    HORNS = "horns"
    TAIL = "tail"
    EXTRA_LIMBS = "extra_limbs"
    
    # Метаболические гены
    FAST_METABOLISM = "fast_metabolism"
    SLOW_METABOLISM = "slow_metabolism"
    TOXIN_RESISTANCE = "toxin_resistance"
    DISEASE_RESISTANCE = "disease_resistance"
    HEALING_FACTOR = "healing_factor"
    AGING_RESISTANCE = "aging_resistance"
    
    # Социальные гены
    LEADERSHIP = "leadership"
    DIPLOMACY = "diplomacy"
    INTIMIDATION = "intimidation"
    PERSUASION = "persuasion"
    TEAMWORK = "teamwork"
    SOLITARY = "solitary"
    
    # Специализированные гены
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
    
    def __le__(self, other):
        if isinstance(other, EvolutionStage):
            return self < other or self == other
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, EvolutionStage):
            return not self <= other
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, EvolutionStage):
            return not self < other
        return NotImplemented

class EvolutionType(Enum):
    """Типы эволюции"""
    NATURAL = "natural"
    FORCED = "forced"
    MUTATION = "mutation"
    FUSION = "fusion"
    ABSORPTION = "absorption"
    TRANSFORMATION = "transformation"
    
    # Новые типы эволюции
    # Элементальная эволюция
    FIRE_EVOLUTION = "fire_evolution"
    ICE_EVOLUTION = "ice_evolution"
    LIGHTNING_EVOLUTION = "lightning_evolution"
    EARTH_EVOLUTION = "earth_evolution"
    WIND_EVOLUTION = "wind_evolution"
    WATER_EVOLUTION = "water_evolution"
    LIGHT_EVOLUTION = "light_evolution"
    DARK_EVOLUTION = "dark_evolution"
    
    # Специальная эволюция
    PSYCHIC_EVOLUTION = "psychic_evolution"
    TECHNOLOGICAL_EVOLUTION = "technological_evolution"
    SPIRITUAL_EVOLUTION = "spiritual_evolution"
    CHAOS_EVOLUTION = "chaos_evolution"
    ORDER_EVOLUTION = "order_evolution"
    VOID_EVOLUTION = "void_evolution"
    
    # Гибридная эволюция
    HYBRID_EVOLUTION = "hybrid_evolution"
    CHIMERA_EVOLUTION = "chimera_evolution"
    SYMBIOTIC_EVOLUTION = "symbiotic_evolution"
    PARASITIC_EVOLUTION = "parasitic_evolution"
    
    # Космическая эволюция
    COSMIC_EVOLUTION = "cosmic_evolution"
    DIMENSIONAL_EVOLUTION = "dimensional_evolution"
    TEMPORAL_EVOLUTION = "temporal_evolution"
    QUANTUM_EVOLUTION = "quantum_evolution"

class EvolutionTriggerType(Enum):
    """Типы триггеров эволюции"""
    LEVEL_UP = "level_up"
    COMBAT_VICTORY = "combat_victory"
    ENVIRONMENTAL_STRESS = "environmental_stress"
    EMOTIONAL_CRISIS = "emotional_crisis"
    GENETIC_MUTATION = "genetic_mutation"
    EXTERNAL_CATALYST = "external_catalyst"
    TIME_PASSAGE = "time_passage"
    SOCIAL_INTERACTION = "social_interaction"
    EXPLORATION_DISCOVERY = "exploration_discovery"
    CRAFTING_MASTERY = "crafting_mastery"
    MAGIC_MASTERY = "magic_mastery"
    SURVIVAL_CHALLENGE = "survival_challenge"

class EvolutionPath(Enum):
    """Пути эволюции"""
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    HEALER = "healer"
    SUMMONER = "summoner"
    ELEMENTALIST = "elementalist"
    PSYCHIC = "psychic"
    TECHNOMANCER = "technomancer"
    SHAPESHIFTER = "shapeshifter"
    NECROMANCER = "necromancer"
    PALADIN = "paladin"
    DRUID = "druid"
    MONK = "monk"
    BARD = "bard"
    RANGER = "ranger"
    BERSERKER = "berserker"
    ASSASSIN = "assassin"
    GUARDIAN = "guardian"
    SAGE = "sage"
    WANDERER = "wanderer"

# ============================================================================
# ТИПЫ ЭМОЦИЙ
# ============================================================================

class EmotionType(Enum):
    """Типы эмоций"""
    # Базовые эмоции
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
    
    # Новые расширенные эмоции
    # Позитивные эмоции
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
    
    # Негативные эмоции
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
    
    # Социальные эмоции
    EMPATHY = "empathy"
    COMPASSION = "compassion"
    CONTEMPT = "contempt"
    INDIGNATION = "indignation"
    SYMPATHY = "sympathy"
    PITY = "pity"
    RESPECT = "respect"
    DISRESPECT = "disrespect"
    LOYALTY = "loyalty"
    
    # Когнитивные эмоции
    CURIOSITY = "curiosity"
    INTEREST = "interest"
    BOREDOM = "boredom"
    FASCINATION = "fascination"
    PERPLEXITY = "perplexity"
    CERTAINTY = "certainty"
    DOUBT = "doubt"
    
    # Эстетические эмоции
    AWE = "awe"
    BEAUTY = "beauty"
    SUBLIME = "sublime"
    UGLINESS = "ugliness"
    HARMONY = "harmony"
    DISCORD = "discord"
    
    # Моральные эмоции
    RIGHTEOUSNESS = "righteousness"
    REMORSE = "remorse"
    INNOCENCE = "innocence"
    CORRUPTION = "corruption"
    HONOR = "honor"
    DISHONOR = "dishonor"
    
    # Экзистенциальные эмоции
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

# ============================================================================
# ТИПЫ СУЩНОСТЕЙ
# ============================================================================

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
    NORMAL = "normal"
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

# Базовые значения характеристик для всех сущностей
BASE_STATS = {
    # Основные характеристики
    "health": 100,
    "mana": 50,
    "stamina": 100,
    
    # Боевые характеристики
    "attack": 10,
    "defense": 5,
    "speed": 1.0,
    "range": 1.0,
    
    # Атрибуты
    "intelligence": 10,
    "strength": 10,
    "agility": 10,
    "constitution": 10,
    "wisdom": 10,
    "charisma": 10,
    "luck": 5,
    
    # Шансовые характеристики
    "critical_chance": 0.05,
    "critical_multiplier": 2.0,
    "dodge_chance": 0.1,
    "block_chance": 0.15,
    "parry_chance": 0.1,
    "evasion_chance": 0.1,
    "resist_chance": 0.1,
    
    # Механика стойкости
    "toughness": 100,
    "toughness_resistance": 0.0,
    "stun_resistance": 0.0,
    "break_efficiency": 1.0,
    
    # Стихийные сопротивления (автоматически заполняются)
    "resistance": {},
    
    # Стихийные множители (автоматически заполняются)
    "damage_multipliers": {},
}

# Характеристики для предметов (наследуют от BASE_STATS + дополнительные)
ITEM_STATS = {
    "weapon": {
        # Базовые характеристики (наследуются от BASE_STATS)
        "health": 0,
        "mana": 0,
        "stamina": 0,
        "attack": 0,
        "defense": 0,
        "speed": 0,
        "intelligence": 0,
        "strength": 0,
        "agility": 0,
        "constitution": 0,
        "wisdom": 0,
        "charisma": 0,
        "luck": 0,
        "toughness": 0,
        "toughness_resistance": 0,
        "stun_resistance": 0,
        "break_efficiency": 0,
        
        # Специфичные для оружия
        "critical_chance": 0,
        "critical_multiplier": 0,
        "damage_type": None,
        "toughness_damage": 0,
        "penetration": 0,
        "range": 0,
        "attack_speed": 0,
    },
    "armor": {
        # Базовые характеристики (наследуются от BASE_STATS)
        "health": 0,
        "mana": 0,
        "stamina": 0,
        "attack": 0,
        "defense": 0,
        "speed": 0,
        "intelligence": 0,
        "strength": 0,
        "agility": 0,
        "constitution": 0,
        "wisdom": 0,
        "charisma": 0,
        "luck": 0,
        "toughness": 0,
        "toughness_resistance": 0,
        "stun_resistance": 0,
        "break_efficiency": 0,
        
        # Специфичные для брони
        "resistance": {},  # Сопротивления по типам урона
        "weight": 0,
        "movement_penalty": 0,
        "durability": 0,
        "max_durability": 0,
    },
    "accessory": {
        # Базовые характеристики (наследуются от BASE_STATS)
        "health": 0,
        "mana": 0,
        "stamina": 0,
        "attack": 0,
        "defense": 0,
        "speed": 0,
        "intelligence": 0,
        "strength": 0,
        "agility": 0,
        "constitution": 0,
        "wisdom": 0,
        "charisma": 0,
        "luck": 0,
        "toughness": 0,
        "toughness_resistance": 0,
        "stun_resistance": 0,
        "break_efficiency": 0,
        
        # Специфичные для аксессуаров
        "special_effects": [],
        "set_bonus": None,
        "socket_count": 0,
    },
    "consumable": {
        # Базовые характеристики (наследуются от BASE_STATS)
        "health": 0,
        "mana": 0,
        "stamina": 0,
        "attack": 0,
        "defense": 0,
        "speed": 0,
        "intelligence": 0,
        "strength": 0,
        "agility": 0,
        "constitution": 0,
        "wisdom": 0,
        "charisma": 0,
        "luck": 0,
        "toughness": 0,
        "toughness_resistance": 0,
        "stun_resistance": 0,
        "break_efficiency": 0,
        
        # Специфичные для расходников
        "healing": 0,
        "mana_restore": 0,
        "stamina_restore": 0,
        "duration": 0,
        "effects": [],
        "cooldown": 0,
        "uses_remaining": 1,
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

# Шаблоны характеристик для разных типов врагов
ENEMY_TEMPLATES = {
    # Танк - высокая защита, низкая скорость
    "tank": {
        "name": "Танк",
        "description": "Медленный, но очень защищенный враг",
        "base_multipliers": {
            "health": 2.0,
            "defense": 2.5,
            "speed": 0.6,
            "attack": 0.8,
            "toughness": 1.5,
            "toughness_resistance": 1.5,
            "stun_resistance": 2.0,
        },
        "preferred_skills": ["defensive", "counter"],
        "ai_behavior": "defensive",
        "weakness_types": ["magic_weak", "arcane_weak"],
        "loot_quality": "rare",
    },
    
    # Ассасин - высокая скорость, низкая защита
    "assassin": {
        "name": "Ассасин",
        "description": "Быстрый и смертоносный, но хрупкий враг",
        "base_multipliers": {
            "health": 0.7,
            "defense": 0.5,
            "speed": 2.5,
            "attack": 2.0,
            "critical_chance": 2.0,
            "critical_multiplier": 1.5,
            "dodge_chance": 2.0,
            "evasion_chance": 2.0,
        },
        "preferred_skills": ["attack", "movement"],
        "ai_behavior": "aggressive",
        "weakness_types": ["physical_weak"],
        "loot_quality": "epic",
    },
    
    # Маг - высокая магия, низкая физическая защита
    "mage": {
        "name": "Маг",
        "description": "Мощный в магии, но слабый физически",
        "base_multipliers": {
            "health": 0.8,
            "mana": 3.0,
            "defense": 0.6,
            "intelligence": 2.5,
            "wisdom": 2.0,
            "attack": 0.5,
            "magic_resistance": 1.5,
        },
        "preferred_skills": ["magic", "support"],
        "ai_behavior": "tactical",
        "weakness_types": ["physical_weak", "piercing_weak"],
        "loot_quality": "rare",
    },
    
    # Брут - высокая сила, средняя защита
    "brute": {
        "name": "Брут",
        "description": "Сильный и выносливый враг",
        "base_multipliers": {
            "health": 1.8,
            "stamina": 2.0,
            "strength": 2.5,
            "constitution": 2.0,
            "attack": 1.8,
            "defense": 1.2,
            "toughness": 1.3,
            "break_efficiency": 1.5,
        },
        "preferred_skills": ["attack", "defensive"],
        "ai_behavior": "aggressive",
        "weakness_types": ["fire_weak", "lightning_weak"],
        "loot_quality": "uncommon",
    },
    
    # Стрелок - высокая дальность, средняя защита
    "archer": {
        "name": "Стрелок",
        "description": "Атакует с расстояния, избегает ближнего боя",
        "base_multipliers": {
            "health": 0.9,
            "speed": 1.8,
            "agility": 2.0,
            "attack": 1.5,
            "range": 3.0,
            "critical_chance": 1.5,
            "dodge_chance": 1.8,
        },
        "preferred_skills": ["ranged", "movement"],
        "ai_behavior": "cautious",
        "weakness_types": ["fire_weak", "ice_weak"],
        "loot_quality": "rare",
    },
    
    # Некромант - высокая магия, низкая физическая защита
    "necromancer": {
        "name": "Некромант",
        "description": "Владеет темной магией и некромантией",
        "base_multipliers": {
            "health": 0.7,
            "mana": 2.5,
            "intelligence": 2.0,
            "wisdom": 1.8,
            "dark_resistance": 2.0,
            "holy_weakness": 2.0,
        },
        "preferred_skills": ["magic", "debuff"],
        "ai_behavior": "tactical",
        "weakness_types": ["holy_weak", "radiant_weak"],
        "loot_quality": "epic",
    },
    
    # Элементаль - высокая стихийная сила, специфические слабости
    "elemental": {
        "name": "Элементаль",
        "description": "Существо чистой стихии",
        "base_multipliers": {
            "health": 1.2,
            "mana": 2.0,
            "intelligence": 1.5,
            "elemental_resistance": 2.0,
            "physical_weakness": 1.5,
        },
        "preferred_skills": ["magic", "elemental"],
        "ai_behavior": "aggressive",
        "weakness_types": ["opposite_element"],
        "loot_quality": "rare",
    },
    
    # Дракон - высокая сила во всех аспектах
    "dragon": {
        "name": "Дракон",
        "description": "Мощное мифическое существо",
        "base_multipliers": {
            "health": 5.0,
            "mana": 3.0,
            "stamina": 4.0,
            "attack": 3.0,
            "defense": 2.5,
            "speed": 1.5,
            "intelligence": 2.0,
            "strength": 3.0,
            "fire_resistance": 3.0,
            "toughness": 2.0,
        },
        "preferred_skills": ["ultimate", "magic", "attack"],
        "ai_behavior": "berserk",
        "weakness_types": ["ice_weak", "holy_weak"],
        "loot_quality": "legendary",
    },
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
    
    # Система квестов
    "max_active_quests": 10,
    "max_daily_quests": 5,
    "max_quest_chains": 5,
    "max_quest_objectives": 10,
    "max_quest_rewards": 10,
    
    # Система торговли
    "max_active_offers": 20,
    "max_trade_history": 100,
    "max_market_items": 1000,
    "max_contract_duration": 604800.0,  # 7 дней
    
    # Система социального взаимодействия
    "max_relationships": 100,
    "max_interactions_per_day": 50,
    "max_reputation_types": 20,
    "max_faction_members": 1000,
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
    "evolution_cooldown": 60.0,       # кулдаун эволюции (1 минута)
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
    "ui_event_delay": 0.1,             # задержка событий UI
    
    # Временные константы для системы квестов
    "quest_expiration_time": 86400.0,  # время истечения квеста (24 часа)
    "quest_chain_delay": 300.0,        # задержка между квестами в цепочке (5 минут)
    "daily_quest_reset": 86400.0,      # сброс ежедневных квестов (24 часа)
    "weekly_quest_reset": 604800.0,    # сброс еженедельных квестов (7 дней)
    
    # Временные константы для системы торговли
    "offer_expiration_time": 604800.0, # время истечения предложения (7 дней)
    "market_update_interval": 3600.0,  # интервал обновления рынка (1 час)
    "trade_cooldown": 60.0,            # кулдаун между сделками (1 минута)
    "contract_duration": 604800.0,     # длительность контракта (7 дней)
    
    # Временные константы для системы социального взаимодействия
    "interaction_cooldown": 300.0,     # кулдаун между взаимодействиями (5 минут)
    "reputation_decay_interval": 86400.0, # интервал затухания репутации (24 часа)
    "relationship_update_interval": 3600.0, # интервал обновления отношений (1 час)
    "faction_influence_update": 1800.0,    # интервал обновления влияния фракций (30 минут)
}

# Вероятности и шансы
PROBABILITY_CONSTANTS = {
    # Базовые шансы
    "base_critical_chance": 0.05,
    "base_dodge_chance": 0.1,
    "base_block_chance": 0.15,
    "base_mutation_chance": 0.01,
    "base_adaptation_chance": 0.05,
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
    "max_critical_multiplier": 10.0,
    
    # Система квестов
    "hidden_quest_chance": 0.1,
    "epic_quest_chance": 0.05,
    "quest_completion_bonus": 1.2,
    "quest_failure_penalty": 0.8,
    "quest_time_bonus": 1.1,
    
    # Система торговли
    "transaction_fee": 0.05,  # 5% комиссия
    "tax_rate": 0.02,  # 2% налог
    "reputation_impact": 0.1,
    "price_volatility": 0.1,
    "bulk_discount_rate": 0.1,
    
    # Система социального взаимодействия
    "relationship_decay_rate": 0.01,
    "reputation_decay_rate": 0.005,
    "faction_influence": 0.1,
    "interaction_success_rate": 0.8,
    "betrayal_chance": 0.05
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

def generate_base_stats_with_resistances():
    """Генерация базовых характеристик с автоматически заполненными сопротивлениями"""
    base_stats = BASE_STATS.copy()
    
    # Автоматически заполняем сопротивления и множители
    resistances, multipliers = generate_damage_constants()
    
    base_stats["resistance"] = resistances
    base_stats["damage_multipliers"] = multipliers
    
    return base_stats

def apply_enemy_template(base_stats: dict, template_name: str, level: int = 1) -> dict:
    """Применение шаблона врага к базовым характеристикам"""
    if template_name not in ENEMY_TEMPLATES:
        return base_stats
    
    template = ENEMY_TEMPLATES[template_name]
    modified_stats = base_stats.copy()
    
    # Применяем множители из шаблона
    for stat, multiplier in template["base_multipliers"].items():
        if stat in modified_stats:
            if isinstance(modified_stats[stat], (int, float)):
                modified_stats[stat] = int(modified_stats[stat] * multiplier * level)
            elif stat == "resistance" and isinstance(multiplier, dict):
                # Специальная обработка для сопротивлений
                for res_type, res_value in multiplier.items():
                    if res_type in modified_stats["resistance"]:
                        modified_stats["resistance"][res_type] = res_value
    
    # Добавляем информацию о шаблоне
    modified_stats["enemy_template"] = template_name
    modified_stats["preferred_skills"] = template["preferred_skills"]
    modified_stats["ai_behavior"] = template["ai_behavior"]
    modified_stats["weakness_types"] = template["weakness_types"]
    modified_stats["loot_quality"] = template["loot_quality"]
    
    return modified_stats

# Генерируем константы автоматически
DEFAULT_RESISTANCES, DAMAGE_MULTIPLIERS = generate_damage_constants()

# ============================================================================
# СЛОТЫ ЭКИПИРОВКИ
# ============================================================================

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
# ШАБЛОНЫ ГЕНЕРАЦИИ СКИЛЛОВ
# ============================================================================

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
    },
    "buff": {
        "name_patterns": ["Enhance", "Boost", "Empower", "Strengthen", "Fortify"],
        "duration": 30.0,
        "mana_cost": 15,
        "cooldown": 10.0,
        "range": 2.0,
        "effects": ["buff"],
        "requirements": ["charisma"],
        "animation": "buff"
    },
    "debuff": {
        "name_patterns": ["Weaken", "Slow", "Poison", "Curse", "Drain"],
        "duration": 20.0,
        "mana_cost": 18,
        "cooldown": 12.0,
        "range": 4.0,
        "effects": ["debuff"],
        "requirements": ["intelligence"],
        "animation": "debuff"
    },
    "movement": {
        "name_patterns": ["Dash", "Leap", "Teleport", "Rush", "Charge"],
        "distance": 5.0,
        "mana_cost": 12,
        "cooldown": 6.0,
        "effects": ["movement"],
        "requirements": ["agility"],
        "animation": "dash"
    },
    "defensive": {
        "name_patterns": ["Shield", "Block", "Parry", "Dodge", "Counter"],
        "defense_boost": 15,
        "mana_cost": 8,
        "cooldown": 4.0,
        "effects": ["defense"],
        "requirements": ["constitution"],
        "animation": "block"
    }
}

SKILL_POWER_MULTIPLIERS = {
    "common": 1.0,
    "uncommon": 1.2,
    "rare": 1.5,
    "epic": 2.0,
    "legendary": 3.0,
    "mythic": 4.0,
    "divine": 5.0
}

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

# Шаблоны для предметов
ITEM_TEMPLATES = {
    "weapon": {
        "sword": {
            "name": "Меч",
            "base_multipliers": {
                "attack": 1.2,
                "speed": 1.0,
                "critical_chance": 1.1,
                "toughness_damage": 0.8,
                "break_efficiency": 1.0,
            },
            "preferred_damage_types": [DamageType.PHYSICAL, DamageType.PIERCING],
            "skill_requirements": ["strength", "agility"],
        },
        "axe": {
            "name": "Топор",
            "base_multipliers": {
                "attack": 1.5,
                "speed": 0.8,
                "critical_multiplier": 1.3,
                "toughness_damage": 1.2,
                "break_efficiency": 1.5,
            },
            "preferred_damage_types": [DamageType.PHYSICAL],
            "skill_requirements": ["strength"],
        },
        "bow": {
            "name": "Лук",
            "base_multipliers": {
                "attack": 1.0,
                "speed": 1.5,
                "range": 3.0,
                "critical_chance": 1.3,
                "toughness_damage": 0.6,
                "break_efficiency": 0.8,
            },
            "preferred_damage_types": [DamageType.PHYSICAL, DamageType.PIERCING],
            "skill_requirements": ["agility", "dexterity"],
        },
        "staff": {
            "name": "Посох",
            "base_multipliers": {
                "attack": 0.8,
                "mana": 1.5,
                "intelligence": 1.2,
                "magic_resistance": 1.1,
                "toughness_damage": 0.5,
                "break_efficiency": 0.7,
            },
            "preferred_damage_types": [DamageType.MAGIC, DamageType.ARCANE],
            "skill_requirements": ["intelligence", "wisdom"],
        },
    },
    "armor": {
        "plate": {
            "name": "Пластинчатая броня",
            "base_multipliers": {
                "defense": 2.0,
                "health": 1.5,
                "weight": 2.0,
                "movement_penalty": 1.5,
                "toughness_resistance": 1.8,
                "stun_resistance": 1.5,
            },
            "preferred_resistances": [DamageType.PHYSICAL, DamageType.PIERCING],
            "skill_requirements": ["strength", "constitution"],
        },
        "leather": {
            "name": "Кожаная броня",
            "base_multipliers": {
                "defense": 0.8,
                "speed": 1.3,
                "agility": 1.2,
                "weight": 0.6,
                "movement_penalty": 0.8,
                "toughness_resistance": 0.7,
                "stun_resistance": 0.9,
            },
            "preferred_resistances": [DamageType.PHYSICAL],
            "skill_requirements": ["agility", "dexterity"],
        },
        "cloth": {
            "name": "Тканевая броня",
            "base_multipliers": {
                "defense": 0.5,
                "mana": 1.8,
                "intelligence": 1.3,
                "magic_resistance": 1.5,
                "weight": 0.3,
                "movement_penalty": 0.5,
                "toughness_resistance": 0.5,
                "stun_resistance": 0.7,
            },
            "preferred_resistances": [DamageType.MAGIC, DamageType.ARCANE],
            "skill_requirements": ["intelligence", "wisdom"],
        },
    },
    "accessory": {
        "ring": {
            "name": "Кольцо",
            "base_multipliers": {
                "intelligence": 1.2,
                "strength": 1.2,
                "agility": 1.2,
                "constitution": 1.2,
                "wisdom": 1.2,
                "charisma": 1.2,
                "luck": 1.3,
            },
            "socket_count": 1,
            "set_bonus": None,
        },
        "necklace": {
            "name": "Ожерелье",
            "base_multipliers": {
                "intelligence": 1.5,
                "wisdom": 1.3,
                "charisma": 1.4,
                "mana": 1.2,
            },
            "socket_count": 2,
            "set_bonus": None,
        },
        "amulet": {
            "name": "Амулет",
            "base_multipliers": {
                "strength": 1.5,
                "constitution": 1.3,
                "health": 1.2,
                "stamina": 1.2,
            },
            "socket_count": 1,
            "set_bonus": None,
        },
    },
}

def apply_item_template(item_type: str, template_name: str, level: int = 1, rarity: str = "common") -> dict:
    """Применение шаблона предмета к базовым характеристикам"""
    if item_type not in ITEM_TEMPLATES or template_name not in ITEM_TEMPLATES[item_type]:
        return ITEM_STATS[item_type].copy()
    
    template = ITEM_TEMPLATES[item_type][template_name]
    item_stats = ITEM_STATS[item_type].copy()
    
    # Применяем множители из шаблона
    for stat, multiplier in template["base_multipliers"].items():
        if stat in item_stats:
            if isinstance(item_stats[stat], (int, float)):
                item_stats[stat] = int(item_stats[stat] * multiplier * level)
    
    # Добавляем информацию о шаблоне
    item_stats["template_name"] = template_name
    item_stats["template_display_name"] = template["name"]
    item_stats["preferred_damage_types"] = template.get("preferred_damage_types", [])
    item_stats["preferred_resistances"] = template.get("preferred_resistances", [])
    item_stats["skill_requirements"] = template.get("skill_requirements", [])
    item_stats["socket_count"] = template.get("socket_count", 0)
    item_stats["set_bonus"] = template.get("set_bonus")
    
    # Применяем множитель редкости
    rarity_multipliers = {
        "common": 1.0,
        "uncommon": 1.2,
        "rare": 1.5,
        "epic": 2.0,
        "legendary": 3.0,
        "mythic": 4.0,
        "divine": 5.0,
    }
    
    rarity_mult = rarity_multipliers.get(rarity, 1.0)
    for stat in ["attack", "defense", "health", "mana", "stamina"]:
        if stat in item_stats and isinstance(item_stats[stat], (int, float)):
            item_stats[stat] = int(item_stats[stat] * rarity_mult)
    
    return item_stats

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

# ============================================================================
# КОНСТАНТЫ ДЛЯ НОВЫХ СИСТЕМ
# ============================================================================

# Константы для системы квестов
QUEST_CONSTANTS = {
    "max_active_quests": 10,
    "max_daily_quests": 5,
    "quest_expiration_time": 86400.0,  # 24 часа в секундах
    "quest_chain_bonus": 1.5,
    "hidden_quest_chance": 0.1,
    "epic_quest_chance": 0.05,
    "quest_completion_bonus": 1.2,
    "quest_failure_penalty": 0.8,
    "quest_time_bonus": 1.1,
    "quest_difficulty_multiplier": {
        "trivial": 0.5,
        "easy": 0.8,
        "normal": 1.0,
        "hard": 1.5,
        "expert": 2.0,
        "master": 3.0,
        "legendary": 5.0,
        "mythic": 10.0
    }
}

# Константы для системы торговли
TRADING_CONSTANTS = {
    "max_active_offers": 20,
    "offer_expiration_time": 604800.0,  # 7 дней в секундах
    "transaction_fee": 0.05,  # 5% комиссия
    "tax_rate": 0.02,  # 2% налог
    "reputation_impact": 0.1,
    "price_volatility": 0.1,
    "market_update_interval": 3600.0,  # 1 час
    "bulk_discount_threshold": 10,
    "bulk_discount_rate": 0.1,
    "quality_multiplier": {
        "poor": 0.5,
        "common": 1.0,
        "uncommon": 1.5,
        "rare": 3.0,
        "epic": 7.0,
        "legendary": 15.0,
        "mythic": 30.0,
        "divine": 100.0
    }
}

# Константы для социальной системы
SOCIAL_CONSTANTS = {
    "max_relationships": 100,
    "relationship_decay_rate": 0.01,
    "interaction_cooldown": 300.0,  # 5 минут
    "reputation_decay_rate": 0.005,
    "faction_influence": 0.1,
    "social_status_requirements": {
        "peasant": 0,
        "citizen": 100,
        "merchant": 500,
        "noble": 1000,
        "royal": 5000,
        "legendary": 10000,
        "mythic": 50000
    },
    "relationship_strength": {
        "stranger": 0,
        "acquaintance": 10,
        "friend": 50,
        "close_friend": 100,
        "best_friend": 200,
        "family": 300,
        "spouse": 500
    }
}

# Константы для системы эволюции (расширенные)
EVOLUTION_CONSTANTS = {
    "max_evolution_stage": 8,
    "evolution_points_per_level": 10,
    "mutation_chance_base": 0.05,
    "adaptation_chance_base": 0.03,
    "gene_expression_rate": 0.1,
    "evolution_cooldown": 3600.0,  # 1 час
    "stage_requirements": {
        "basic": 0,
        "intermediate": 100,
        "advanced": 300,
        "elite": 600,
        "master": 1000,
        "legendary": 2000,
        "mythic": 5000,
        "divine": 10000
    },
    "evolution_bonuses": {
        "basic": 1.0,
        "intermediate": 1.2,
        "advanced": 1.5,
        "elite": 2.0,
        "master": 3.0,
        "legendary": 5.0,
        "mythic": 10.0,
        "divine": 20.0
    }
}

# Константы для системы эмоций (расширенные)
EMOTION_CONSTANTS = {
    "max_emotion_intensity": 10,
    "emotion_decay_rate": 0.1,
    "emotion_influence_radius": 5.0,
    "emotional_stability_threshold": 0.5,
    "empathy_range": 3.0,
    "courage_boost_factor": 1.5,
    "fear_resistance_bonus": 0.2,
    "emotion_combination_bonus": 1.3,
    "emotional_exhaustion_threshold": 8.0,
    "emotion_recovery_rate": 0.05
}

# Константы для системы генома (расширенные)
GENOME_CONSTANTS = {
    "max_genes_per_entity": 50,
    "mutation_rate": 0.01,
    "recombination_rate": 0.02,
    "gene_expression_threshold": 0.5,
    "genome_complexity_limit": 1000,
    "trait_activation_chance": 0.7,
    "gene_stability_factor": 0.9,
    "mutation_stability": 0.8,
    "gene_combination_bonus": 1.2,
    "genome_evolution_rate": 0.1
}

# Константы для системы боя (расширенные)
COMBAT_CONSTANTS = {
    "base_attack_speed": 1.0,
    "base_defense": 10,
    "critical_hit_chance": 0.05,
    "critical_hit_multiplier": 2.0,
    "dodge_chance": 0.1,
    "block_chance": 0.15,
    "parry_chance": 0.1,
    "counter_attack_chance": 0.2,
    "stun_duration": 2.0,
    "bleed_damage": 5,
    "poison_damage": 3,
    "burn_damage": 4,
    "freeze_duration": 1.5,
    "shock_damage": 6,
    "combo_multiplier": 1.2,
    "chain_attack_bonus": 1.1
}

# Константы для системы навыков (расширенные)
SKILL_CONSTANTS = {
    "max_skill_level": 100,
    "skill_points_per_level": 5,
    "skill_learning_rate": 0.1,
    "skill_decay_rate": 0.01,
    "skill_specialization_bonus": 1.5,
    "skill_combination_bonus": 1.3,
    "skill_mastery_threshold": 90,
    "skill_evolution_chance": 0.05,
    "skill_synergy_bonus": 1.2,
    "skill_adaptation_rate": 0.1
}

# Константы для системы инвентаря (расширенные)
INVENTORY_CONSTANTS = {
    "max_inventory_slots": 50,
    "max_stack_size": 999,
    "weight_limit": 100.0,
    "encumbrance_threshold": 0.8,
    "item_durability_decay": 0.01,
    "repair_efficiency": 0.8,
    "enchantment_success_rate": 0.7,
    "disenchant_efficiency": 0.5,
    "item_quality_bonus": 1.2,
    "inventory_organization_bonus": 1.1
}

# Константы для системы крафтинга (расширенные)
CRAFTING_CONSTANTS = {
    "base_crafting_success": 0.8,
    "quality_material_bonus": 1.3,
    "skill_crafting_bonus": 1.2,
    "tool_quality_bonus": 1.1,
    "recipe_complexity_penalty": 0.9,
    "experimental_crafting_chance": 0.1,
    "masterwork_chance": 0.05,
    "critical_crafting_chance": 0.02,
    "crafting_failure_penalty": 0.5,
    "crafting_experience_gain": 10
}

# Константы для системы мира (расширенные)
WORLD_CONSTANTS = {
    "world_size": 1000,
    "chunk_size": 16,
    "render_distance": 8,
    "day_night_cycle": 1200.0,  # 20 минут
    "weather_change_interval": 300.0,  # 5 минут
    "season_duration": 7200.0,  # 2 часа
    "resource_respawn_time": 600.0,  # 10 минут
    "enemy_spawn_rate": 0.1,
    "loot_drop_rate": 0.3,
    "exploration_bonus": 1.2
}

# Константы для системы рендеринга (расширенные)
RENDERING_CONSTANTS = {
    "max_fps": 60,
    "vsync_enabled": True,
    "antialiasing_level": 4,
    "shadow_quality": "high",
    "texture_quality": "high",
    "particle_effects": True,
    "bloom_effect": True,
    "motion_blur": False,
    "depth_of_field": True,
    "ambient_occlusion": True
}

# Константы для системы UI (расширенные)
UI_CONSTANTS = {
    "ui_scale": 1.0,
    "font_size": 14,
    "button_padding": 5,
    "menu_transition_speed": 0.3,
    "tooltip_delay": 0.5,
    "notification_duration": 3.0,
    "progress_bar_smoothness": 0.1,
    "color_blind_mode": False,
    "high_contrast_mode": False,
    "accessibility_features": True
}

# Константы для системы звука (расширенные)
AUDIO_CONSTANTS = {
    "master_volume": 1.0,
    "music_volume": 0.7,
    "sfx_volume": 0.8,
    "voice_volume": 0.9,
    "ambient_volume": 0.5,
    "spatial_audio": True,
    "reverb_enabled": True,
    "echo_enabled": False,
    "audio_quality": "high",
    "sample_rate": 44100
}

# Константы для системы сети (расширенные)
NETWORK_CONSTANTS = {
    "max_players": 100,
    "tick_rate": 60,
    "interpolation_delay": 0.1,
    "prediction_enabled": True,
    "lag_compensation": True,
    "bandwidth_limit": 1000000,  # 1 MB/s
    "connection_timeout": 30.0,
    "reconnect_attempts": 3,
    "ping_update_interval": 1.0,
    "packet_loss_threshold": 0.1
}

# Константы для системы безопасности (расширенные)
SECURITY_CONSTANTS = {
    "encryption_enabled": True,
    "checksum_verification": True,
    "anti_cheat_enabled": True,
    "rate_limiting": True,
    "session_timeout": 3600.0,  # 1 час
    "max_login_attempts": 5,
    "password_min_length": 8,
    "two_factor_auth": False,
    "backup_frequency": 3600.0,  # 1 час
    "log_retention_days": 30
}

# Константы для системы аналитики (расширенные)
ANALYTICS_CONSTANTS = {
    "data_collection_enabled": True,
    "performance_monitoring": True,
    "error_reporting": True,
    "usage_statistics": True,
    "crash_reporting": True,
    "telemetry_enabled": False,
    "privacy_mode": True,
    "data_retention_days": 90,
    "anonymization_enabled": True,
    "opt_out_enabled": True
}

# ============================================================================
# ТИПЫ КВЕСТОВ
# ============================================================================

class QuestType(Enum):
    """Типы квестов"""
    # Основные типы
    MAIN_QUEST = "main_quest"
    SIDE_QUEST = "side_quest"
    DAILY_QUEST = "daily_quest"
    WEEKLY_QUEST = "weekly_quest"
    EVENT_QUEST = "event_quest"
    
    # Специализированные квесты
    EXPLORATION_QUEST = "exploration_quest"
    COMBAT_QUEST = "combat_quest"
    CRAFTING_QUEST = "crafting_quest"
    SOCIAL_QUEST = "social_quest"
    SURVIVAL_QUEST = "survival_quest"
    
    # Эволюционные квесты
    EVOLUTION_QUEST = "evolution_quest"
    MUTATION_QUEST = "mutation_quest"
    ADAPTATION_QUEST = "adaptation_quest"
    GENE_QUEST = "gene_quest"
    
    # Эмоциональные квесты
    EMOTIONAL_QUEST = "emotional_quest"
    THERAPY_QUEST = "therapy_quest"
    EMPATHY_QUEST = "empathy_quest"
    COURAGE_QUEST = "courage_quest"
    
    # Скрытые квесты
    HIDDEN_QUEST = "hidden_quest"
    SECRET_QUEST = "secret_quest"
    MYSTERY_QUEST = "mystery_quest"
    LEGENDARY_QUEST = "legendary_quest"

class QuestStatus(Enum):
    """Статусы квестов"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    EXPIRED = "expired"
    LOCKED = "locked"
    AVAILABLE = "available"

class QuestRewardType(Enum):
    """Типы наград за квесты"""
    # Материальные награды
    EXPERIENCE = "experience"
    GOLD = "gold"
    ITEMS = "items"
    MATERIALS = "materials"
    CURRENCY = "currency"
    
    # Эволюционные награды
    EVOLUTION_POINTS = "evolution_points"
    GENE_FRAGMENTS = "gene_fragments"
    MUTATION_CHANCES = "mutation_chances"
    ADAPTATION_BONUS = "adaptation_bonus"
    
    # Эмоциональные награды
    EMOTIONAL_STABILITY = "emotional_stability"
    EMPATHY_BOOST = "empathy_boost"
    COURAGE_BOOST = "courage_boost"
    CALMNESS_BOOST = "calmness_boost"
    
    # Способности и навыки
    SKILL_POINTS = "skill_points"
    ABILITY_UNLOCKS = "ability_unlocks"
    SPELL_LEARNING = "spell_learning"
    TECHNIQUE_MASTERY = "technique_mastery"
    
    # Социальные награды
    REPUTATION = "reputation"
    ALLIANCE_POINTS = "alliance_points"
    FACTION_STANDING = "faction_standing"
    RELATIONSHIP_BOOST = "relationship_boost"
    
    # Специальные награды
    TITLE = "title"
    ACHIEVEMENT = "achievement"
    COSMETIC_ITEM = "cosmetic_item"
    SPECIAL_ACCESS = "special_access"

class QuestDifficulty(Enum):
    """Сложность квестов"""
    TRIVIAL = "trivial"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class QuestCategory(Enum):
    """Категории квестов"""
    STORY = "story"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    CRAFTING = "crafting"
    SOCIAL = "social"
    SURVIVAL = "survival"
    EVOLUTION = "evolution"
    EMOTIONAL = "emotional"
    MYSTERY = "mystery"
    EVENT = "event"

# ============================================================================
# ТИПЫ ТОРГОВЛИ
# ============================================================================

class TradeType(Enum):
    """Типы торговли"""
    # Основные типы
    BUY = "buy"
    SELL = "sell"
    EXCHANGE = "exchange"
    AUCTION = "auction"
    BARTER = "barter"
    
    # Специализированные типы
    BULK_TRADE = "bulk_trade"
    CONTRACT_TRADE = "contract_trade"
    FUTURES_TRADE = "futures_trade"
    OPTIONS_TRADE = "options_trade"
    
    # Эволюционные типы
    GENE_TRADE = "gene_trade"
    EVOLUTION_TRADE = "evolution_trade"
    MUTATION_TRADE = "mutation_trade"
    ADAPTATION_TRADE = "adaptation_trade"
    
    # Эмоциональные типы
    EMOTION_TRADE = "emotion_trade"
    EXPERIENCE_TRADE = "experience_trade"
    MEMORY_TRADE = "memory_trade"
    WISDOM_TRADE = "wisdom_trade"

class TradeStatus(Enum):
    """Статусы торговли"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class CurrencyType(Enum):
    """Типы валют"""
    # Основные валюты
    GOLD = "gold"
    SILVER = "silver"
    COPPER = "copper"
    PLATINUM = "platinum"
    
    # Специальные валюты
    CREDITS = "credits"
    TOKENS = "tokens"
    POINTS = "points"
    FRAGMENTS = "fragments"
    
    # Эволюционные валюты
    EVOLUTION_POINTS = "evolution_points"
    GENE_FRAGMENTS = "gene_fragments"
    MUTATION_CHANCES = "mutation_chances"
    ADAPTATION_BONUS = "adaptation_bonus"
    
    # Эмоциональные валюты
    EMOTIONAL_STABILITY = "emotional_stability"
    EMPATHY_POINTS = "empathy_points"
    COURAGE_POINTS = "courage_points"
    WISDOM_POINTS = "wisdom_points"

class TradeCategory(Enum):
    """Категории торговли"""
    WEAPONS = "weapons"
    ARMOR = "armor"
    CONSUMABLES = "consumables"
    MATERIALS = "materials"
    CURRENCY = "currency"
    SERVICES = "services"
    INFORMATION = "information"
    SKILLS = "skills"
    GENES = "genes"
    EMOTIONS = "emotions"

class TradeRarity(Enum):
    """Редкость торговых предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    DIVINE = "divine"

class TradeLocation(Enum):
    """Места торговли"""
    MARKETPLACE = "marketplace"
    SHOP = "shop"
    AUCTION_HOUSE = "auction_house"
    BLACK_MARKET = "black_market"
    TRADING_POST = "trading_post"
    CARAVAN = "caravan"
    PORT = "port"
    GUILD_HALL = "guild_hall"
    TEMPLE = "temple"
    ACADEMY = "academy"

# ============================================================================
# ТИПЫ СОЦИАЛЬНОГО ВЗАИМОДЕЙСТВИЯ
# ============================================================================

class RelationshipType(Enum):
    """Типы отношений"""
    # Базовые отношения
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    BEST_FRIEND = "best_friend"
    ENEMY = "enemy"
    RIVAL = "rival"
    
    # Семейные отношения
    FAMILY = "family"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    SPOUSE = "spouse"
    MENTOR = "mentor"
    STUDENT = "student"
    
    # Профессиональные отношения
    COLLEAGUE = "colleague"
    BOSS = "boss"
    SUBORDINATE = "subordinate"
    PARTNER = "partner"
    ALLY = "ally"
    COMPETITOR = "competitor"
    
    # Эволюционные отношения
    EVOLUTION_PARTNER = "evolution_partner"
    GENE_DONOR = "gene_donor"
    MUTATION_BUDDY = "mutation_buddy"
    ADAPTATION_MENTOR = "adaptation_mentor"
    
    # Эмоциональные отношения
    EMOTIONAL_SUPPORT = "emotional_support"
    THERAPIST = "therapist"
    EMPATHY_PARTNER = "empathy_partner"
    COURAGE_INSPIRER = "courage_inspirer"

class InteractionType(Enum):
    """Типы взаимодействий"""
    # Базовые взаимодействия
    GREETING = "greeting"
    CONVERSATION = "conversation"
    GIFT_GIVING = "gift_giving"
    HELP_OFFERED = "help_offered"
    HELP_RECEIVED = "help_received"
    
    # Эмоциональные взаимодействия
    EMOTIONAL_SUPPORT = "emotional_support"
    EMPATHY_SHARED = "empathy_shared"
    COURAGE_GIVEN = "courage_given"
    COMFORT_PROVIDED = "comfort_provided"
    
    # Конфликтные взаимодействия
    ARGUMENT = "argument"
    INSULT = "insult"
    THREAT = "threat"
    VIOLENCE = "violence"
    BETRAYAL = "betrayal"
    
    # Эволюционные взаимодействия
    GENE_SHARING = "gene_sharing"
    MUTATION_HELP = "mutation_help"
    EVOLUTION_GUIDANCE = "evolution_guidance"
    ADAPTATION_TRAINING = "adaptation_training"
    
    # Торговые взаимодействия
    TRADE_FAIR = "trade_fair"
    TRADE_UNFAIR = "trade_unfair"
    SERVICE_PROVIDED = "service_provided"
    SERVICE_RECEIVED = "service_received"
    
    # Образовательные взаимодействия
    KNOWLEDGE_SHARED = "knowledge_shared"
    SKILL_TAUGHT = "skill_taught"
    WISDOM_IMPARTED = "wisdom_imparted"
    EXPERIENCE_SHARED = "experience_shared"

class ReputationType(Enum):
    """Типы репутации"""
    # Общая репутация
    GENERAL = "general"
    HONESTY = "honesty"
    RELIABILITY = "reliability"
    GENEROSITY = "generosity"
    INTELLIGENCE = "intelligence"
    
    # Боевая репутация
    COMBAT_SKILL = "combat_skill"
    BRAVERY = "bravery"
    STRATEGY = "strategy"
    LOYALTY = "loyalty"
    
    # Эволюционная репутация
    EVOLUTION_MASTERY = "evolution_mastery"
    GENE_EXPERTISE = "gene_expertise"
    MUTATION_CONTROL = "mutation_control"
    ADAPTATION_ABILITY = "adaptation_ability"
    
    # Эмоциональная репутация
    EMOTIONAL_STABILITY = "emotional_stability"
    EMPATHY_LEVEL = "empathy_level"
    COURAGE_LEVEL = "courage_level"
    WISDOM_LEVEL = "wisdom_level"
    
    # Торговая репутация
    TRADING_FAIRNESS = "trading_fairness"
    QUALITY_PROVIDER = "quality_provider"
    PRICE_REASONABLE = "price_reasonable"
    SERVICE_QUALITY = "service_quality"

class SocialStatus(Enum):
    """Социальный статус"""
    OUTCAST = "outcast"
    PEASANT = "peasant"
    CITIZEN = "citizen"
    MERCHANT = "merchant"
    NOBLE = "noble"
    ROYAL = "royal"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class FactionType(Enum):
    """Типы фракций"""
    NEUTRAL = "neutral"
    EVOLUTIONISTS = "evolutionists"
    TRADITIONALISTS = "traditionalists"
    EMOTIONALISTS = "emotionalists"
    TECHNOLOGISTS = "technologists"
    MYSTICS = "mystics"
    WARRIORS = "warriors"
    TRADERS = "traders"
    SCHOLARS = "scholars"
    OUTLAWS = "outlaws"

class CommunicationChannel(Enum):
    """Каналы коммуникации"""
    VERBAL = "verbal"
    NONVERBAL = "nonverbal"
    TELEPATHIC = "telepathic"
    EMOTIONAL = "emotional"
    GESTURAL = "gestural"
    WRITTEN = "written"
    DIGITAL = "digital"
    QUANTUM = "quantum"
