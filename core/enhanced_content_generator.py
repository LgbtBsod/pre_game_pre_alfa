#!/usr/bin/env python3
"""
Расширенная система процедурной генерации контента.
Вдохновлено Binding of Isaac, Risk of Rain 2, Loop Hero.
Включает генерацию врагов, боссов, ловушек, сундуков и процедурных уровней.
"""

import random
import uuid
import hashlib
import math
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

from .generational_memory_system import GenerationalMemorySystem, MemoryType

logger = logging.getLogger(__name__)


class BiomeType(Enum):
    """Типы биомов"""
    FOREST = "forest"
    DESERT = "desert"
    MOUNTAIN = "mountain"
    OCEAN = "ocean"
    ARCTIC = "arctic"
    SWAMP = "swamp"
    VOLCANO = "volcano"
    CRYSTAL = "crystal"
    UNDERWORLD = "underworld"
    SPACE = "space"
    CORRUPTED = "corrupted"
    SANCTUARY = "sanctuary"


class EnemyType(Enum):
    """Типы врагов"""
    PREDATOR = "predator"
    HERBIVORE = "herbivore"
    NEUTRAL = "neutral"
    BOSS = "boss"
    ELITE = "elite"
    MINION = "minion"
    SUMMONED = "summoned"
    CORRUPTED = "corrupted"
    EVOLVED = "evolved"
    LEGENDARY = "legendary"


class TrapType(Enum):
    """Типы ловушек"""
    SPIKE = "spike"
    PIT = "pit"
    ARROW = "arrow"
    EXPLOSIVE = "explosive"
    POISON = "poison"
    ELECTRIC = "electric"
    ICE = "ice"
    FIRE = "fire"
    PSYCHOLOGICAL = "psychological"
    TEMPORAL = "temporal"


class ChestType(Enum):
    """Типы сундуков"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    CORRUPTED = "corrupted"
    EVOLUTIONARY = "evolutionary"
    TEMPORAL = "temporal"
    DIMENSIONAL = "dimensional"


class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    CORRUPTED = "corrupted"
    EVOLUTIONARY = "evolutionary"
    TEMPORAL = "temporal"
    DIMENSIONAL = "dimensional"


@dataclass
class GeneratedEnemy:
    """Сгенерированный враг"""
    guid: str
    name: str
    enemy_type: EnemyType
    biome: BiomeType
    level: int
    stats: Dict[str, Any]
    abilities: List[str]
    ai_personality: Dict[str, float]
    loot_table: List[str]
    evolution_potential: float
    memory_capacity: int
    emotional_resistance: float
    position: Tuple[int, int]
    spawn_conditions: Dict[str, Any]
    
    def get_power_level(self) -> float:
        """Получение уровня силы врага"""
        base_power = self.level * 10
        stat_bonus = sum(self.stats.values()) * 0.1
        ability_bonus = len(self.abilities) * 5
        return base_power + stat_bonus + ability_bonus


@dataclass
class GeneratedBoss:
    """Сгенерированный босс"""
    guid: str
    name: str
    boss_type: str
    biome: BiomeType
    level: int
    phases: List[Dict[str, Any]]
    special_abilities: List[str]
    evolution_stages: List[Dict[str, Any]]
    memory_system: Dict[str, Any]
    emotional_triggers: List[str]
    loot_table: List[str]
    position: Tuple[int, int]
    arena_effects: List[str]
    
    def get_current_phase(self, health_percent: float) -> Dict[str, Any]:
        """Получение текущей фазы босса"""
        for phase in self.phases:
            if health_percent >= phase["health_threshold"]:
                return phase
        return self.phases[-1]


@dataclass
class GeneratedTrap:
    """Сгенерированная ловушка"""
    guid: str
    name: str
    trap_type: TrapType
    damage: float
    trigger_conditions: Dict[str, Any]
    disarm_difficulty: float
    visibility: float
    position: Tuple[int, int]
    effects: List[str]
    evolution_potential: float


@dataclass
class GeneratedChest:
    """Сгенерированный сундук"""
    guid: str
    name: str
    chest_type: ChestType
    rarity: ItemRarity
    contents: List[str]
    unlock_requirements: Dict[str, Any]
    trap_chance: float
    position: Tuple[int, int]
    evolution_requirements: Dict[str, Any]


@dataclass
class GeneratedLevel:
    """Сгенерированный уровень"""
    guid: str
    name: str
    biome: BiomeType
    difficulty: float
    size: Tuple[int, int]
    rooms: List[Dict[str, Any]]
    connections: List[Tuple[int, int]]
    hazards: List[str]
    resources: List[str]
    evolution_opportunities: List[str]
    memory_triggers: List[str]


class EnhancedContentGenerator:
    """Расширенный генератор контента"""
    
    def __init__(self, memory_system: GenerationalMemorySystem):
        self.memory_system = memory_system
        
        # Шаблоны генерации
        self.enemy_templates: Dict[str, Dict[str, Any]] = {}
        self.boss_templates: Dict[str, Dict[str, Any]] = {}
        self.trap_templates: Dict[str, Dict[str, Any]] = {}
        self.chest_templates: Dict[str, Dict[str, Any]] = {}
        
        # Система эволюции контента
        self.content_evolution_system = ContentEvolutionSystem()
        
        # Система памяти контента
        self.content_memory_system = ContentMemorySystem(memory_system)
        
        # Инициализация шаблонов
        self._init_generation_templates()
        
        logger.info("Расширенный генератор контента инициализирован")
    
    def generate_enemy(self, biome: BiomeType, level: int, 
                      context: Dict[str, Any]) -> GeneratedEnemy:
        """Генерация врага"""
        # Выбор типа врага
        enemy_type = self._select_enemy_type(biome, level, context)
        
        # Генерация характеристик
        stats = self._generate_enemy_stats(enemy_type, level, biome)
        abilities = self._generate_enemy_abilities(enemy_type, level, biome)
        personality = self._generate_enemy_personality(enemy_type, biome)
        
        # Генерация позиции
        position = self._generate_enemy_position(context)
        
        # Создание врага
        enemy = GeneratedEnemy(
            guid=str(uuid.uuid4()),
            name=self._generate_enemy_name(enemy_type, biome),
            enemy_type=enemy_type,
            biome=biome,
            level=level,
            stats=stats,
            abilities=abilities,
            ai_personality=personality,
            loot_table=self._generate_loot_table(enemy_type, level),
            evolution_potential=random.uniform(0.1, 0.9),
            memory_capacity=random.randint(5, 20),
            emotional_resistance=random.uniform(0.2, 0.8),
            position=position,
            spawn_conditions=context
        )
        
        # Запись в память
        self.content_memory_system.record_enemy_generation(enemy, context)
        
        return enemy
    
    def generate_boss(self, biome: BiomeType, level: int, 
                     context: Dict[str, Any]) -> GeneratedBoss:
        """Генерация босса"""
        # Выбор типа босса
        boss_type = self._select_boss_type(biome, level, context)
        
        # Генерация фаз
        phases = self._generate_boss_phases(boss_type, level, biome)
        
        # Генерация способностей
        special_abilities = self._generate_boss_abilities(boss_type, level, biome)
        
        # Генерация эволюционных стадий
        evolution_stages = self._generate_evolution_stages(boss_type, level)
        
        # Создание босса
        boss = GeneratedBoss(
            guid=str(uuid.uuid4()),
            name=self._generate_boss_name(boss_type, biome),
            boss_type=boss_type,
            biome=biome,
            level=level,
            phases=phases,
            special_abilities=special_abilities,
            evolution_stages=evolution_stages,
            memory_system=self._generate_boss_memory_system(boss_type, level),
            emotional_triggers=self._generate_emotional_triggers(boss_type, biome),
            loot_table=self._generate_boss_loot_table(boss_type, level),
            position=self._generate_boss_position(context),
            arena_effects=self._generate_arena_effects(boss_type, biome)
        )
        
        # Запись в память
        self.content_memory_system.record_boss_generation(boss, context)
        
        return boss
    
    def generate_trap(self, biome: BiomeType, level: int, 
                     context: Dict[str, Any]) -> GeneratedTrap:
        """Генерация ловушки"""
        # Выбор типа ловушки
        trap_type = self._select_trap_type(biome, level, context)
        
        # Генерация характеристик
        damage = self._calculate_trap_damage(trap_type, level, biome)
        trigger_conditions = self._generate_trigger_conditions(trap_type, context)
        
        # Создание ловушки
        trap = GeneratedTrap(
            guid=str(uuid.uuid4()),
            name=self._generate_trap_name(trap_type, biome),
            trap_type=trap_type,
            damage=damage,
            trigger_conditions=trigger_conditions,
            disarm_difficulty=random.uniform(0.3, 0.9),
            visibility=random.uniform(0.1, 0.8),
            position=self._generate_trap_position(context),
            effects=self._generate_trap_effects(trap_type, biome),
            evolution_potential=random.uniform(0.1, 0.7)
        )
        
        return trap
    
    def generate_chest(self, biome: BiomeType, level: int, 
                      context: Dict[str, Any]) -> GeneratedChest:
        """Генерация сундука"""
        # Выбор типа сундука
        chest_type = self._select_chest_type(biome, level, context)
        
        # Генерация содержимого
        contents = self._generate_chest_contents(chest_type, level, biome)
        
        # Генерация требований
        unlock_requirements = self._generate_unlock_requirements(chest_type, level)
        
        # Создание сундука
        chest = GeneratedChest(
            guid=str(uuid.uuid4()),
            name=self._generate_chest_name(chest_type, biome),
            chest_type=chest_type,
            rarity=self._determine_chest_rarity(chest_type, level),
            contents=contents,
            unlock_requirements=unlock_requirements,
            trap_chance=self._calculate_trap_chance(chest_type, level),
            position=self._generate_chest_position(context),
            evolution_requirements=self._generate_evolution_requirements(chest_type, level)
        )
        
        return chest
    
    def generate_level(self, biome: BiomeType, difficulty: float, 
                      size: Tuple[int, int], context: Dict[str, Any]) -> GeneratedLevel:
        """Генерация уровня"""
        # Генерация комнат
        rooms = self._generate_level_rooms(size, difficulty, biome)
        
        # Генерация соединений
        connections = self._generate_room_connections(rooms)
        
        # Генерация опасностей
        hazards = self._generate_level_hazards(difficulty, biome)
        
        # Создание уровня
        level = GeneratedLevel(
            guid=str(uuid.uuid4()),
            name=self._generate_level_name(biome, difficulty),
            biome=biome,
            difficulty=difficulty,
            size=size,
            rooms=rooms,
            connections=connections,
            hazards=hazards,
            resources=self._generate_level_resources(biome, difficulty),
            evolution_opportunities=self._generate_evolution_opportunities(difficulty, biome),
            memory_triggers=self._generate_memory_triggers(difficulty, biome)
        )
        
        return level
    
    def _select_enemy_type(self, biome: BiomeType, level: int, 
                          context: Dict[str, Any]) -> EnemyType:
        """Выбор типа врага"""
        biome_enemies = {
            BiomeType.FOREST: [EnemyType.PREDATOR, EnemyType.HERBIVORE, EnemyType.NEUTRAL],
            BiomeType.DESERT: [EnemyType.PREDATOR, EnemyType.CORRUPTED, EnemyType.EVOLVED],
            BiomeType.MOUNTAIN: [EnemyType.ELITE, EnemyType.BOSS, EnemyType.LEGENDARY],
            BiomeType.OCEAN: [EnemyType.PREDATOR, EnemyType.SUMMONED, EnemyType.CORRUPTED],
            BiomeType.ARCTIC: [EnemyType.ELITE, EnemyType.EVOLVED, EnemyType.LEGENDARY],
            BiomeType.SWAMP: [EnemyType.CORRUPTED, EnemyType.SUMMONED, EnemyType.MINION],
            BiomeType.VOLCANO: [EnemyType.BOSS, EnemyType.LEGENDARY, EnemyType.CORRUPTED],
            BiomeType.CRYSTAL: [EnemyType.EVOLVED, EnemyType.LEGENDARY],
            BiomeType.UNDERWORLD: [EnemyType.CORRUPTED, EnemyType.BOSS, EnemyType.LEGENDARY],
            BiomeType.SPACE: [EnemyType.EVOLVED, EnemyType.LEGENDARY],
            BiomeType.CORRUPTED: [EnemyType.CORRUPTED, EnemyType.EVOLVED, EnemyType.BOSS],
            BiomeType.SANCTUARY: [EnemyType.NEUTRAL, EnemyType.ELITE, EnemyType.EVOLVED]
        }
        
        available_types = biome_enemies.get(biome, [EnemyType.NEUTRAL])
        
        # Влияние уровня сложности
        if level > 20:
            available_types.extend([EnemyType.ELITE, EnemyType.BOSS])
        if level > 50:
            available_types.extend([EnemyType.LEGENDARY])
        
        # Влияние контекста
        if context.get("boss_room", False):
            available_types = [EnemyType.BOSS, EnemyType.LEGENDARY]
        elif context.get("elite_room", False):
            available_types = [EnemyType.ELITE, EnemyType.EVOLVED]
        
        return random.choice(available_types)
    
    def _select_trap_type(self, biome: BiomeType, level: int, 
                          context: Dict[str, Any]) -> TrapType:
        """Выбор типа ловушки на основе биома и уровня"""
        biome_traps = {
            BiomeType.FOREST: [TrapType.SPIKE, TrapType.PIT, TrapType.POISON],
            BiomeType.DESERT: [TrapType.SPIKE, TrapType.PIT, TrapType.EXPLOSIVE],
            BiomeType.MOUNTAIN: [TrapType.ARROW, TrapType.PIT, TrapType.ICE],
            BiomeType.OCEAN: [TrapType.PIT, TrapType.ELECTRIC, TrapType.PSYCHOLOGICAL],
            BiomeType.ARCTIC: [TrapType.ICE, TrapType.PIT, TrapType.TEMPORAL],
            BiomeType.SWAMP: [TrapType.POISON, TrapType.PIT, TrapType.PSYCHOLOGICAL],
            BiomeType.VOLCANO: [TrapType.FIRE, TrapType.EXPLOSIVE, TrapType.PIT],
            BiomeType.CRYSTAL: [TrapType.SPIKE, TrapType.ICE, TrapType.TEMPORAL],
            BiomeType.UNDERWORLD: [TrapType.PSYCHOLOGICAL, TrapType.POISON, TrapType.TEMPORAL],
            BiomeType.SPACE: [TrapType.TEMPORAL, TrapType.ELECTRIC, TrapType.PSYCHOLOGICAL],
            BiomeType.CORRUPTED: [TrapType.POISON, TrapType.PSYCHOLOGICAL, TrapType.TEMPORAL],
            BiomeType.SANCTUARY: [TrapType.SPIKE, TrapType.PIT, TrapType.ELECTRIC]
        }
        
        available_types = biome_traps.get(biome, [TrapType.SPIKE])
        
        # Влияние уровня сложности
        if level > 20:
            available_types.extend([TrapType.EXPLOSIVE, TrapType.PSYCHOLOGICAL])
        if level > 50:
            available_types.extend([TrapType.TEMPORAL])
        
        # Влияние контекста
        if context.get("boss_room", False):
            available_types = [TrapType.PSYCHOLOGICAL, TrapType.TEMPORAL]
        elif context.get("elite_room", False):
            available_types = [TrapType.EXPLOSIVE, TrapType.PSYCHOLOGICAL]
        
        return random.choice(available_types)
    
    def _generate_enemy_stats(self, enemy_type: EnemyType, level: int, 
                             biome: BiomeType) -> Dict[str, Any]:
        """Генерация характеристик врага"""
        base_stats = {
            "health": level * 10,
            "attack": level * 2,
            "defense": level * 1.5,
            "speed": random.uniform(0.8, 1.2),
            "stamina": level * 8,
            "intelligence": random.uniform(0.5, 1.5)
        }
        
        # Модификаторы по типу врага
        type_modifiers = {
            EnemyType.PREDATOR: {"attack": 1.3, "speed": 1.4, "intelligence": 1.2},
            EnemyType.HERBIVORE: {"defense": 1.3, "health": 1.2, "speed": 0.8},
            EnemyType.ELITE: {"health": 1.5, "attack": 1.4, "defense": 1.3},
            EnemyType.BOSS: {"health": 2.0, "attack": 1.8, "defense": 1.6},
            EnemyType.LEGENDARY: {"health": 3.0, "attack": 2.5, "defense": 2.0},
            EnemyType.CORRUPTED: {"attack": 1.6, "speed": 1.3, "health": 0.8},
            EnemyType.EVOLVED: {"health": 1.4, "attack": 1.5, "intelligence": 1.8}
        }
        
        modifiers = type_modifiers.get(enemy_type, {})
        for stat, modifier in modifiers.items():
            if stat in base_stats:
                base_stats[stat] *= modifier
        
        # Модификаторы по биому
        biome_modifiers = {
            BiomeType.VOLCANO: {"attack": 1.2, "health": 1.1},
            BiomeType.ARCTIC: {"defense": 1.3, "speed": 0.9},
            BiomeType.CRYSTAL: {"intelligence": 1.4, "attack": 1.1},
            BiomeType.UNDERWORLD: {"attack": 1.3, "health": 1.2}
        }
        
        modifiers = biome_modifiers.get(biome, {})
        for stat, modifier in modifiers.items():
            if stat in base_stats:
                base_stats[stat] *= modifier
        
        return base_stats
    
    def _generate_enemy_abilities(self, enemy_type: EnemyType, level: int, 
                                 biome: BiomeType) -> List[str]:
        """Генерация способностей врага"""
        base_abilities = ["basic_attack", "move"]
        
        # Способности по типу врага
        type_abilities = {
            EnemyType.PREDATOR: ["charge", "pounce", "track"],
            EnemyType.ELITE: ["combo_attack", "defensive_stance", "counter_attack"],
            EnemyType.BOSS: ["special_attack", "area_attack", "summon_minions"],
            EnemyType.LEGENDARY: ["ultimate_ability", "phase_shift", "reality_warp"],
            EnemyType.CORRUPTED: ["corruption_attack", "mind_control", "life_drain"],
            EnemyType.EVOLVED: ["adapt", "evolve", "learn"]
        }
        
        abilities = base_abilities.copy()
        type_specific = type_abilities.get(enemy_type, [])
        abilities.extend(type_specific)
        
        # Способности по биому
        biome_abilities = {
            BiomeType.VOLCANO: ["fire_attack", "lava_walk", "heat_wave"],
            BiomeType.ARCTIC: ["ice_attack", "freeze", "blizzard"],
            BiomeType.CRYSTAL: ["crystal_shard", "reflection", "prism"],
            BiomeType.UNDERWORLD: ["shadow_step", "void_attack", "corruption"]
        }
        
        biome_specific = biome_abilities.get(biome, [])
        if random.random() < 0.3:  # 30% шанс получить способность биома
            abilities.extend(random.sample(biome_specific, min(2, len(biome_specific))))
        
        # Уровневые способности
        if level > 15:
            abilities.append("advanced_combat")
        if level > 30:
            abilities.append("tactical_awareness")
        if level > 50:
            abilities.append("master_strategy")
        
        return abilities
    
    def _generate_enemy_personality(self, enemy_type: EnemyType, 
                                   biome: BiomeType) -> Dict[str, float]:
        """Генерация личности врага"""
        base_personality = {
            "aggression": 0.5,
            "curiosity": 0.5,
            "caution": 0.5,
            "social": 0.5,
            "adaptability": 0.5
        }
        
        # Модификаторы по типу врага
        type_modifiers = {
            EnemyType.PREDATOR: {"aggression": 0.8, "caution": 0.3, "social": 0.2},
            EnemyType.HERBIVORE: {"aggression": 0.2, "caution": 0.8, "social": 0.7},
            EnemyType.ELITE: {"aggression": 0.7, "caution": 0.6, "adaptability": 0.8},
            EnemyType.BOSS: {"aggression": 0.9, "caution": 0.4, "adaptability": 0.9},
            EnemyType.CORRUPTED: {"aggression": 0.9, "social": 0.1, "adaptability": 0.7},
            EnemyType.EVOLVED: {"curiosity": 0.8, "adaptability": 0.9, "social": 0.6}
        }
        
        modifiers = type_modifiers.get(enemy_type, {})
        for trait, modifier in modifiers.items():
            if trait in base_personality:
                base_personality[trait] = modifier
        
        # Модификаторы по биому
        biome_modifiers = {
            BiomeType.VOLCANO: {"aggression": 0.2, "caution": -0.1},
            BiomeType.ARCTIC: {"caution": 0.2, "social": -0.1},
            BiomeType.CRYSTAL: {"curiosity": 0.2, "intelligence": 0.2},
            BiomeType.UNDERWORLD: {"aggression": 0.3, "social": -0.2}
        }
        
        modifiers = biome_modifiers.get(biome, {})
        for trait, modifier in modifiers.items():
            if trait in base_personality:
                base_personality[trait] = max(0.0, min(1.0, base_personality[trait] + modifier))
        
        return base_personality
    
    def _generate_loot_table(self, enemy_type: EnemyType, level: int) -> List[str]:
        """Генерация таблицы лута"""
        loot_table = []
        
        # Базовый лут
        if random.random() < 0.8:  # 80% шанс базового лута
            loot_table.append("basic_material")
        
        # Лут по типу врага
        type_loot = {
            EnemyType.PREDATOR: ["predator_fang", "aggressive_gene"],
            EnemyType.ELITE: ["elite_core", "advanced_material"],
            EnemyType.BOSS: ["boss_essence", "legendary_material"],
            EnemyType.LEGENDARY: ["legendary_artifact", "mythic_gene"],
            EnemyType.CORRUPTED: ["corruption_shard", "dark_essence"],
            EnemyType.EVOLVED: ["evolution_crystal", "adaptive_gene"]
        }
        
        enemy_loot = type_loot.get(enemy_type, [])
        if random.random() < 0.6:  # 60% шанс специфичного лута
            loot_table.extend(random.sample(enemy_loot, min(2, len(enemy_loot))))
        
        # Уровневый лут
        if level > 20 and random.random() < 0.4:
            loot_table.append("advanced_weapon")
        if level > 40 and random.random() < 0.3:
            loot_table.append("legendary_item")
        
        return loot_table
    
    def _generate_enemy_name(self, enemy_type: EnemyType, biome: BiomeType) -> str:
        """Генерация имени врага"""
        prefixes = {
            EnemyType.PREDATOR: ["Savage", "Feral", "Bloodthirsty"],
            EnemyType.ELITE: ["Elite", "Veteran", "Master"],
            EnemyType.BOSS: ["Ancient", "Tyrant", "Overlord"],
            EnemyType.LEGENDARY: ["Legendary", "Mythic", "Eternal"],
            EnemyType.CORRUPTED: ["Corrupted", "Twisted", "Defiled"],
            EnemyType.EVOLVED: ["Evolved", "Advanced", "Transcended"]
        }
        
        suffixes = {
            BiomeType.FOREST: ["Stalker", "Hunter", "Guardian"],
            BiomeType.VOLCANO: ["Inferno", "Blaze", "Magma"],
            BiomeType.ARCTIC: ["Frost", "Blizzard", "Glacier"],
            BiomeType.CRYSTAL: ["Crystal", "Prism", "Gem"],
            BiomeType.UNDERWORLD: ["Shadow", "Void", "Abyss"]
        }
        
        prefix = random.choice(prefixes.get(enemy_type, ["Unknown"]))
        suffix = random.choice(suffixes.get(biome, ["Creature"]))
        
        return f"{prefix} {suffix}"
    
    def _generate_enemy_position(self, context: Dict[str, Any]) -> Tuple[int, int]:
        """Генерация позиции врага"""
        # Простая генерация позиции в пределах уровня
        level_width = context.get("level_width", 1000)
        level_height = context.get("level_height", 1000)
        
        x = random.randint(100, level_width - 100)
        y = random.randint(100, level_height - 100)
        
        return (x, y)
    
    def _init_generation_templates(self):
        """Инициализация шаблонов генерации"""
        # Шаблоны врагов
        self.enemy_templates = {
            "forest_predator": {
                "stats": {"speed": 1.3, "attack": 1.2},
                "abilities": ["stealth", "ambush", "track"],
                "personality": {"aggression": 0.8, "caution": 0.4}
            },
            "volcano_boss": {
                "stats": {"health": 2.0, "attack": 1.8, "defense": 1.5},
                "abilities": ["fire_breath", "lava_pool", "volcanic_eruption"],
                "personality": {"aggression": 0.9, "caution": 0.3}
            }
        }
        
        # Шаблоны боссов
        self.boss_templates = {
            "evolutionary_tyrant": {
                "phases": [
                    {"health_threshold": 1.0, "abilities": ["basic_attack", "evolve"]},
                    {"health_threshold": 0.7, "abilities": ["advanced_attack", "summon_minions"]},
                    {"health_threshold": 0.3, "abilities": ["ultimate_attack", "reality_warp"]}
                ],
                "evolution_stages": ["alpha", "beta", "omega"]
            }
        }
        
        # Шаблоны ловушек
        self.trap_templates = {
            "spike_trap": {
                "damage": 25,
                "trigger": "pressure_plate",
                "effects": ["bleeding", "stunned"]
            },
            "poison_trap": {
                "damage": 15,
                "trigger": "proximity",
                "effects": ["poisoned", "weakened"]
            }
        }
        
        # Шаблоны сундуков
        self.chest_templates = {
            "evolutionary_chest": {
                "contents": ["evolution_gene", "adaptive_weapon", "memory_crystal"],
                "requirements": {"evolution_level": 5, "memory_fragments": 10}
            }
        }


class ContentEvolutionSystem:
    """Система эволюции контента"""
    
    def __init__(self):
        self.evolution_tracks: Dict[str, List[str]] = {}
        self.mutation_chances: Dict[str, float] = {}
    
    def evolve_content(self, content_id: str, evolution_type: str, 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Эволюция контента"""
        if content_id not in self.evolution_tracks:
            self.evolution_tracks[content_id] = []
        
        evolution = {
            "type": evolution_type,
            "timestamp": time.time(),
            "context": context,
            "stage": len(self.evolution_tracks[content_id]) + 1
        }
        
        self.evolution_tracks[content_id].append(evolution)
        
        return evolution


class ContentMemorySystem:
    """Система памяти контента"""
    
    def __init__(self, memory_system: GenerationalMemorySystem):
        self.memory_system = memory_system
        self.content_memories: Dict[str, List[Dict[str, Any]]] = {}
    
    def record_enemy_generation(self, enemy: GeneratedEnemy, context: Dict[str, Any]):
        """Запись генерации врага в память"""
        memory_content = {
            "enemy_id": enemy.guid,
            "enemy_type": enemy.enemy_type.value,
            "biome": enemy.biome.value,
            "level": enemy.level,
            "stats": enemy.stats,
            "context": context,
            "timestamp": time.time()
        }
        
        self.memory_system.add_memory(
            memory_type=MemoryType.ENEMY_PATTERNS,
            content=memory_content,
            intensity=enemy.level / 100.0,
            emotional_impact=0.3
        )
    
    def record_boss_generation(self, boss: GeneratedBoss, context: Dict[str, Any]):
        """Запись генерации босса в память"""
        memory_content = {
            "boss_id": boss.guid,
            "boss_type": boss.boss_type,
            "biome": boss.biome.value,
            "level": boss.level,
            "phases": len(boss.phases),
            "context": context,
            "timestamp": time.time()
        }
        
        self.memory_system.add_memory(
            memory_type=MemoryType.ENEMY_PATTERNS,
            content=memory_content,
            intensity=boss.level / 50.0,
            emotional_impact=0.7
        )
