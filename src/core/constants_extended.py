#!/usr/bin/env python3
"""Расширенный модуль констант - дополнительные типы и константы
Расширяет базовый модуль констант"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import os
import time

from .constants import (
    DamageType,
    EmotionType, GeneType, EvolutionType, constants_manager
)

logger = logging.getLogger(__name__)

# = ДОПОЛНИТЕЛЬНЫЕ ТИПЫ

class BiomeType(Enum):
    """Типы биомов"""
    FOREST = "forest"
    DESERT = "desert"
    MOUNTAIN = "mountain"
    OCEAN = "ocean"
    TUNDRA = "tundra"
    SWAMP = "swamp"
    VOLCANO = "volcano"
    CRYSTAL = "crystal"
    EVOLUTIONARY = "evolutionary"
    MEMORY = "memory"

class StructureType(Enum):
    """Типы структур"""
    DUNGEON = "dungeon"
    SETTLEMENT = "settlement"
    TOWER = "tower"
    TEMPLE = "temple"
    LABORATORY = "laboratory"
    EVOLUTION_CHAMBER = "evolution_chamber"
    MEMORY_VAULT = "memory_vault"
    PORTAL = "portal"

class EnemyType(Enum):
    """Типы врагов"""
    WILD_ANIMAL = "wild_animal"
    MUTANT = "mutant"
    EVOLVED = "evolved"
    BOSS = "boss"
    ELITE = "elite"
    MINION = "minion"
    GUARDIAN = "guardian"
    EVOLUTIONARY = "evolutionary"

class BossPhase(Enum):
    """Фазы боссов"""
    NORMAL = "normal"
    ENRAGED = "enraged"
    EVOLVED = "evolved"
    FINAL = "final"
    TRANSCENDENT = "transcendent"

class QuestType(Enum):
    """Типы квестов"""
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    WEEKLY = "weekly"
    EVOLUTION = "evolution"
    MEMORY = "memory"
    SOCIAL = "social"
    EXPLORATION = "exploration"

class QuestStatus(Enum):
    """Статусы квестов"""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EVOLVED = "evolved"

class DialogueType(Enum):
    """Типы диалогов"""
    GREETING = "greeting"
    QUEST = "quest"
    TRADE = "trade"
    SOCIAL = "social"
    EVOLUTION = "evolution"
    MEMORY = "memory"
    EMOTIONAL = "emotional"

class TradeType(Enum):
    """Типы торговли"""
    BUY = "buy"
    SELL = "sell"
    EXCHANGE = "exchange"
    CRAFT = "craft"
    EVOLUTION = "evolution"
    MEMORY = "memory"

class CraftingType(Enum):
    """Типы крафтинга"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    TOOL = "tool"
    EVOLUTION = "evolution"
    MEMORY = "memory"

class MemoryType(Enum):
    """Типы памяти"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    EMOTIONAL = "emotional"
    GENETIC = "genetic"
    EVOLUTIONARY = "evolutionary"

class MemoryImportance(Enum):
    """Важность памяти"""
    TRIVIAL = 1
    MINOR = 2
    MODERATE = 3
    IMPORTANT = 4
    CRITICAL = 5
    EVOLUTIONARY = 6

class WorldEventType(Enum):
    """Типы мировых событий"""
    NATURAL_DISASTER = "natural_disaster"
    EVOLUTION_WAVE = "evolution_wave"
    MEMORY_STORM = "memory_storm"
    BOSS_SPAWN = "boss_spawn"
    PORTAL_OPENING = "portal_opening"
    MUTATION_OUTBREAK = "mutation_outbreak"

class WeatherType(Enum):
    """Типы погоды"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"
    EVOLUTIONARY = "evolutionary"
    MEMORY = "memory"

class TimeOfDay(Enum):
    """Время суток"""
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    NIGHT = "night"
    MIDNIGHT = "midnight"

class SeasonType(Enum):
    """Типы сезонов"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    EVOLUTIONARY = "evolutionary"

class CameraMode(Enum):
    """Режимы камеры"""
    ISOMETRIC = "isometric"
    THIRD_PERSON = "third_person"
    FIRST_PERSON = "first_person"
    TOP_DOWN = "top_down"
    FREE = "free"

class InputType(Enum):
    """Типы ввода"""
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    GAMEPAD = "gamepad"
    TOUCH = "touch"
    VOICE = "voice"

class AudioType(Enum):
    """Типы аудио"""
    MUSIC = "music"
    SFX = "sfx"
    VOICE = "voice"
    AMBIENT = "ambient"
    EVOLUTIONARY = "evolutionary"

class ParticleType(Enum):
    """Типы частиц"""
    FIRE = "fire"
    WATER = "water"
    LIGHTNING = "lightning"
    SMOKE = "smoke"
    SPARKLE = "sparkle"
    EVOLUTION = "evolution"
    MEMORY = "memory"

class AnimationType(Enum):
    """Типы анимации"""
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    ATTACK = "attack"
    DEFEND = "defend"
    EVOLVE = "evolve"
    EMOTE = "emote"

# = ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ

@dataclass
class BiomeData:
    """Данные биома"""
    name: str
    type: BiomeType
    temperature: float
    humidity: float
    elevation: float
    vegetation_density: float
    enemy_spawn_rate: float
    resource_abundance: float
    evolution_influence: float
    memory_influence: float

@dataclass
class StructureData:
    """Данные структуры"""
    name: str
    type: StructureType
    size: Tuple[int, int, int]
    complexity: int
    difficulty: int
    rewards: Dict[str, Any]
    evolution_requirements: List[str]
    memory_requirements: List[str]

@dataclass
class EnemyData:
    """Данные врага"""
    name: str
    type: EnemyType
    level: int
    health: int
    damage: int
    skills: List[str]
    evolution_stage: int
    memory_capacity: int
    behavior: str
    rewards: Dict[str, Any]

@dataclass
class BossData:
    """Данные босса"""
    name: str
    phases: List[BossPhase]
    health_per_phase: List[int]
    damage_per_phase: List[int]
    skills_per_phase: List[List[str]]
    evolution_requirements: List[str]
    memory_requirements: List[str]
    rewards: Dict[str, Any]

@dataclass
class QuestData:
    """Данные квеста"""
    name: str
    type: QuestType
    description: str
    objectives: List[str]
    rewards: Dict[str, Any]
    evolution_requirements: List[str]
    memory_requirements: List[str]
    time_limit: Optional[float]

@dataclass
class DialogueData:
    """Данные диалога"""
    id: str
    type: DialogueType
    speaker: str
    text: str
    responses: List[str]
    emotion_influence: Dict[EmotionType, float]
    memory_influence: Dict[MemoryType, float]
    evolution_influence: float

@dataclass
class MemoryData:
    """Данные памяти"""
    id: str
    type: MemoryType
    content: str
    importance: MemoryImportance
    emotion: EmotionType
    intensity: float
    creation_time: float
    decay_rate: float
    evolution_influence: float

# = ДОПОЛНИТЕЛЬНЫЕ КОНСТАНТЫ

# Константы для биомов
BIOME_CONSTANTS = {
    "forest": {
        "temperature": 0.6,
        "humidity": 0.8,
        "elevation": 0.3,
        "vegetation_density": 0.9,
        "enemy_spawn_rate": 0.1,
        "resource_abundance": 0.7,
        "evolution_influence": 0.3,
        "memory_influence": 0.4
    },
    "desert": {
        "temperature": 0.9,
        "humidity": 0.1,
        "elevation": 0.2,
        "vegetation_density": 0.1,
        "enemy_spawn_rate": 0.15,
        "resource_abundance": 0.3,
        "evolution_influence": 0.6,
        "memory_influence": 0.2
    },
    "mountain": {
        "temperature": 0.3,
        "humidity": 0.5,
        "elevation": 0.9,
        "vegetation_density": 0.4,
        "enemy_spawn_rate": 0.2,
        "resource_abundance": 0.6,
        "evolution_influence": 0.7,
        "memory_influence": 0.5
    },
    "evolutionary": {
        "temperature": 0.7,
        "humidity": 0.6,
        "elevation": 0.5,
        "vegetation_density": 0.8,
        "enemy_spawn_rate": 0.25,
        "resource_abundance": 0.9,
        "evolution_influence": 1.0,
        "memory_influence": 0.8
    }
}

# Константы для структур
STRUCTURE_CONSTANTS = {
    "dungeon": {
        "size_range": ((10, 10, 5), (50, 50, 20)),
        "complexity_range": (3, 8),
        "difficulty_range": (1, 10),
        "evolution_requirements": ["level_5", "memory_100"],
        "memory_requirements": ["exploration_skill_3"]
    },
    "evolution_chamber": {
        "size_range": ((20, 20, 10), (30, 30, 15)),
        "complexity_range": (7, 10),
        "difficulty_range": (8, 10),
        "evolution_requirements": ["level_10", "evolution_points_50"],
        "memory_requirements": ["evolution_memory_100"]
    },
    "memory_vault": {
        "size_range": ((15, 15, 8), (25, 25, 12)),
        "complexity_range": (5, 9),
        "difficulty_range": (6, 9),
        "evolution_requirements": ["level_7", "memory_capacity_200"],
        "memory_requirements": ["memory_skill_5"]
    }
}

# Константы для врагов
ENEMY_CONSTANTS = {
    "wild_animal": {
        "health_multiplier": 1.0,
        "damage_multiplier": 1.0,
        "skill_count_range": (1, 3),
        "evolution_chance": 0.01,
        "memory_capacity": 50
    },
    "mutant": {
        "health_multiplier": 1.5,
        "damage_multiplier": 1.3,
        "skill_count_range": (2, 4),
        "evolution_chance": 0.05,
        "memory_capacity": 100
    },
    "boss": {
        "health_multiplier": 5.0,
        "damage_multiplier": 2.0,
        "skill_count_range": (5, 8),
        "evolution_chance": 0.2,
        "memory_capacity": 500
    },
    "evolutionary": {
        "health_multiplier": 3.0,
        "damage_multiplier": 1.8,
        "skill_count_range": (4, 7),
        "evolution_chance": 0.15,
        "memory_capacity": 300
    }
}

# Константы для квестов
QUEST_CONSTANTS = {
    "main": {
        "reward_multiplier": 2.0,
        "experience_multiplier": 1.5,
        "evolution_points": 10,
        "memory_points": 50
    },
    "side": {
        "reward_multiplier": 1.0,
        "experience_multiplier": 1.0,
        "evolution_points": 5,
        "memory_points": 25
    },
    "evolution": {
        "reward_multiplier": 1.5,
        "experience_multiplier": 1.2,
        "evolution_points": 20,
        "memory_points": 75
    },
    "memory": {
        "reward_multiplier": 1.3,
        "experience_multiplier": 1.1,
        "evolution_points": 8,
        "memory_points": 100
    }
}

# Константы для диалогов
DIALOGUE_CONSTANTS = {
    "greeting": {
        "emotion_influence": 0.1,
        "memory_influence": 0.05,
        "evolution_influence": 0.0
    },
    "quest": {
        "emotion_influence": 0.3,
        "memory_influence": 0.2,
        "evolution_influence": 0.1
    },
    "evolution": {
        "emotion_influence": 0.5,
        "memory_influence": 0.4,
        "evolution_influence": 0.8
    },
    "memory": {
        "emotion_influence": 0.4,
        "memory_influence": 0.6,
        "evolution_influence": 0.2
    }
}

# Константы для памяти
MEMORY_CONSTANTS = {
    "short_term": {
        "decay_rate": 0.1,
        "capacity": 100,
        "importance_range": (1, 3)
    },
    "long_term": {
        "decay_rate": 0.01,
        "capacity": 1000,
        "importance_range": (2, 5)
    },
    "episodic": {
        "decay_rate": 0.05,
        "capacity": 500,
        "importance_range": (3, 6)
    },
    "evolutionary": {
        "decay_rate": 0.001,
        "capacity": 2000,
        "importance_range": (4, 6)
    }
}

# Константы для процедурной генерации контента
CONTENT_GENERATION_CONSTANTS = {
    "boss_skills_variation": 0.3,  # 30% вариация навыков боссов
    "weapon_stats_variation": 0.25,  # 25% вариация статов оружия
    "jewelry_stats_variation": 0.2,  # 20% вариация статов украшений
    "skill_stats_variation": 0.35,  # 35% вариация статов навыков
    "session_uniqueness_factor": 0.8,  # Фактор уникальности сессии
    "level_progression_factor": 1.2,  # Фактор прогрессии уровня
    "evolution_influence_factor": 1.5,  # Фактор влияния эволюции
    "memory_influence_factor": 1.3   # Фактор влияния памяти
}

# Константы для сессий
SESSION_GENERATION_CONSTANTS = {
    "content_generation_timeout": 30.0,  # Таймаут генерации контента
    "max_content_items_per_session": 1000,  # Максимум предметов контента на сессию
    "content_cache_size": 100,  # Размер кэша контента
    "session_data_compression": True,  # Сжатие данных сессии
    "backup_frequency": 300,  # Частота резервного копирования (5 минут)
    "session_cleanup_interval": 3600,  # Интервал очистки сессий (1 час)
    "max_session_age": 86400  # Максимальный возраст сессии (24 часа)
}

# Константы для визуализации эмоций
EMOTION_VISUALIZATION_CONSTANTS = {
    "disc_radius": 0.5,
    "disc_height": 2.0,
    "color_intensity_range": (0.3, 1.0),
    "pulse_frequency": 2.0,  # Гц
    "rotation_speed": 1.0,  # Радиан/сек
    "fade_duration": 0.5,  # Секунды
    "max_emotion_discs": 10  # Максимум дисков эмоций на экране
}

# Константы для геометрических фигур
GEOMETRIC_SHAPE_CONSTANTS = {
    "sphere": {
        "radius": 0.5,
        "segments": 16,
        "color": (0.8, 0.8, 0.8, 1.0)
    },
    "cube": {
        "size": 1.0,
        "color": (0.6, 0.6, 0.6, 1.0)
    },
    "cylinder": {
        "radius": 0.5,
        "height": 1.0,
        "segments": 12,
        "color": (0.7, 0.7, 0.7, 1.0)
    },
    "dodecahedron": {
        "radius": 0.5,
        "color": (0.9, 0.3, 0.3, 1.0)
    },
    "octahedron": {
        "radius": 0.5,
        "color": (0.3, 0.9, 0.3, 1.0)
    }
}

logger.info("Расширенный модуль констант загружен")
