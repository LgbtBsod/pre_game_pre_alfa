"""
Система процедурной генерации контента с использованием seed для воспроизводимости.
Генерирует уникальные миры, врагов, оружие и предметы для каждого игрового цикла.
"""

import random
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib

logger = logging.getLogger(__name__)


class BiomeType(Enum):
    """Типы биомов"""
    FOREST = "forest"
    DESERT = "desert"
    MOUNTAIN = "mountain"
    OCEAN = "ocean"
    ARCTIC = "arctic"
    VOLCANO = "volcano"
    SWAMP = "swamp"
    CAVE = "cave"
    URBAN = "urban"
    SPACE = "space"


class EnemyType(Enum):
    """Типы врагов"""
    PREDATOR = "predator"
    PREY = "prey"
    NEUTRAL = "neutral"
    BOSS = "boss"
    ELITE = "elite"
    MINION = "minion"


class WeaponType(Enum):
    """Типы оружия"""
    SWORD = "sword"
    AXE = "axe"
    BOW = "bow"
    STAFF = "staff"
    DAGGER = "dagger"
    HAMMER = "hammer"
    SPEAR = "spear"
    WAND = "wand"


class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class GeneratedEnemy:
    """Сгенерированный враг"""
    id: str
    name: str
    enemy_type: str
    biome: str
    level: int
    stats: Dict[str, float]
    resistances: Dict[str, float]
    weaknesses: Dict[str, float]
    abilities: List[str]
    appearance: Dict[str, Any]
    behavior_pattern: str


@dataclass
class GeneratedWeapon:
    """Сгенерированное оружие"""
    id: str
    name: str
    weapon_type: str
    tier: int
    damage: float
    effects: List[str]
    requirements: Dict[str, float]
    appearance: Dict[str, Any]
    durability: int


@dataclass
class GeneratedItem:
    """Сгенерированный предмет"""
    id: str
    name: str
    item_type: str
    rarity: str
    effects: List[str]
    value: int
    weight: float
    appearance: Dict[str, Any]


@dataclass
class GeneratedWorld:
    """Сгенерированный мир"""
    id: str
    seed: int
    name: str
    biomes: List[Dict[str, Any]]
    landmarks: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    weather_patterns: List[str]
    time_cycle: Dict[str, Any]


class ContentGenerator:
    """Генератор контента"""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or random.randint(1, 999999)
        self.random_generator = random.Random(self.seed)
        
        # Шаблоны для генерации
        self.enemy_templates = self._init_enemy_templates()
        self.weapon_templates = self._init_weapon_templates()
        self.item_templates = self._init_item_templates()
        self.biome_templates = self._init_biome_templates()
        
        # Словари для генерации имён
        self.name_prefixes = ["Dark", "Light", "Ancient", "Modern", "Mystic", "Tech", "Wild", "Tame"]
        self.name_suffixes = ["Beast", "Spirit", "Guardian", "Hunter", "Wanderer", "Defender", "Seeker"]
        
        # Флаг инициализации контента
        self.content_initialized = False
        
        logger.info(f"Генератор контента инициализирован с seed: {self.seed}")
    
    def initialize_session_content(self, session_uuid: str, level: int = 1) -> Dict[str, Any]:
        """Инициализация контента для новой сессии"""
        try:
            if self.content_initialized:
                logger.warning("Контент уже инициализирован для этой сессии")
                return {}
            
            # Генерируем seed на основе UUID сессии и уровня
            session_seed = hash(session_uuid) % 999999
            level_seed = session_seed + level * 1000
            self.set_seed(level_seed)
            
            # Генерируем начальный контент
            initial_content = {
                "items": [],
                "enemies": [],
                "weapons": [],
                "skills": [],
                "world_seed": level_seed
            }
            
            # Генерируем начальные предметы
            for i in range(5):  # 5 начальных предметов
                item = self.generate_item(
                    item_type=self.random_generator.choice(["potion", "weapon", "armor"]),
                    rarity="common"
                )
                initial_content["items"].append(item.__dict__)
            
            # Генерируем начальное оружие
            for i in range(3):  # 3 начальных оружия
                weapon = self.generate_weapon(
                    weapon_type=self.random_generator.choice(list(WeaponType)).value,
                    tier=1
                )
                initial_content["weapons"].append(weapon.__dict__)
            
            # Генерируем начальных врагов
            for i in range(3):  # 3 начальных врага
                enemy = self.generate_enemy(
                    biome="forest",
                    level=level,
                    enemy_type="prey"
                )
                initial_content["enemies"].append(enemy.__dict__)
            
            # Генерируем начальные навыки
            for i in range(2):  # 2 начальных навыка
                skill = self._generate_basic_skill()
                initial_content["skills"].append(skill)
            
            self.content_initialized = True
            logger.info(f"Контент инициализирован для сессии {session_uuid}")
            return initial_content
            
        except Exception as e:
            logger.error(f"Ошибка инициализации контента сессии: {e}")
            return {}
    
    def _generate_basic_skill(self) -> Dict[str, Any]:
        """Генерация базового навыка"""
        skill_types = ["attack", "defense", "utility"]
        skill_type = self.random_generator.choice(skill_types)
        
        return {
            "id": f"skill_{self.random_generator.randint(1000, 9999)}",
            "name": f"Basic {skill_type.title()}",
            "type": skill_type,
            "level": 1,
            "description": f"A basic {skill_type} skill",
            "effect": f"Provides basic {skill_type} capabilities"
        }
    
    def _init_enemy_templates(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация шаблонов врагов"""
        return {
            "predator": {
                "base_stats": {"hp": 80, "damage": 25, "speed": 1.2, "defense": 15},
                "stat_variance": 0.3,
                "abilities": ["hunt", "stealth", "pack_tactics"],
                "behavior": "aggressive"
            },
            "prey": {
                "base_stats": {"hp": 40, "damage": 8, "speed": 1.8, "defense": 8},
                "stat_variance": 0.4,
                "abilities": ["flee", "alert", "group_defense"],
                "behavior": "defensive"
            },
            "neutral": {
                "base_stats": {"hp": 60, "damage": 15, "speed": 1.0, "defense": 12},
                "stat_variance": 0.25,
                "abilities": ["observe", "retreat", "negotiate"],
                "behavior": "cautious"
            },
            "boss": {
                "base_stats": {"hp": 200, "damage": 50, "speed": 0.8, "defense": 30},
                "stat_variance": 0.2,
                "abilities": ["special_attack", "summon_minions", "phase_shift"],
                "behavior": "aggressive"
            },
            "elite": {
                "base_stats": {"hp": 120, "damage": 35, "speed": 1.1, "defense": 20},
                "stat_variance": 0.15,
                "abilities": ["enhanced_attack", "defensive_stance", "tactical_retreat"],
                "behavior": "balanced"
            }
        }
    
    def _init_weapon_templates(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация шаблонов оружия"""
        return {
            "sword": {
                "base_damage": 20,
                "damage_variance": 0.3,
                "speed": 1.0,
                "effects": ["sharp", "balanced"],
                "tier_multipliers": [1.0, 1.2, 1.5, 2.0, 3.0]
            },
            "axe": {
                "base_damage": 30,
                "damage_variance": 0.4,
                "speed": 0.7,
                "effects": ["heavy", "armor_piercing"],
                "tier_multipliers": [1.0, 1.3, 1.6, 2.2, 3.5]
            },
            "bow": {
                "base_damage": 18,
                "damage_variance": 0.25,
                "speed": 1.3,
                "effects": ["ranged", "precise"],
                "tier_multipliers": [1.0, 1.15, 1.4, 1.8, 2.5]
            },
            "staff": {
                "base_damage": 15,
                "damage_variance": 0.5,
                "speed": 1.1,
                "effects": ["magical", "elemental"],
                "tier_multipliers": [1.0, 1.25, 1.6, 2.1, 3.2]
            }
        }
    
    def _init_item_templates(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация шаблонов предметов"""
        return {
            "consumable": {
                "effects": ["heal", "boost", "cure"],
                "rarity_weights": [0.5, 0.3, 0.15, 0.04, 0.01]
            },
            "equipment": {
                "effects": ["defense", "speed", "damage", "utility"],
                "rarity_weights": [0.4, 0.35, 0.2, 0.04, 0.01]
            },
            "material": {
                "effects": ["crafting", "upgrade", "trade"],
                "rarity_weights": [0.6, 0.25, 0.1, 0.04, 0.01]
            }
        }
    
    def _init_biome_templates(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация шаблонов биомов"""
        return {
            BiomeType.FOREST.value: {
                "enemy_types": ["predator", "prey", "neutral"],
                "resources": ["wood", "herbs", "animals"],
                "weather": ["sunny", "rainy", "foggy"],
                "difficulty": 1.0
            },
            BiomeType.DESERT.value: {
                "enemy_types": ["predator", "neutral"],
                "resources": ["sand", "cactus", "minerals"],
                "weather": ["hot", "sandstorm", "cold_night"],
                "difficulty": 1.3
            },
            BiomeType.MOUNTAIN.value: {
                "enemy_types": ["elite", "neutral", "boss"],
                "resources": ["stone", "crystals", "precious_metals"],
                "weather": ["windy", "snowy", "stormy"],
                "difficulty": 1.8
            },
            BiomeType.OCEAN.value: {
                "enemy_types": ["predator", "prey"],
                "resources": ["fish", "coral", "pearls"],
                "weather": ["calm", "stormy", "foggy"],
                "difficulty": 1.5
            },
            BiomeType.VOLCANO.value: {
                "enemy_types": ["boss", "elite", "predator"],
                "resources": ["lava", "obsidian", "fire_crystals"],
                "weather": ["hot", "ash_rain", "fire_storm"],
                "difficulty": 2.2
            }
        }
    
    def generate_world(
        self,
        world_size: str = "medium",
        *,
        biome: Optional[str] = None,
        size: Optional[str] = None,
        difficulty: Optional[float] = None,
    ) -> GeneratedWorld:
        """Генерация мира"""
        try:
            # Определение размера мира
            size_multipliers = {
                "small": 0.5,
                "medium": 1.0,
                "large": 1.5,
                "huge": 2.0
            }
            # Параметр size (если передан) имеет приоритет над world_size
            effective_size = size or world_size
            size_mult = size_multipliers.get(effective_size, 1.0)
            difficulty_mult = difficulty if isinstance(difficulty, (int, float)) else 1.0
            
            # Генерация биомов
            num_biomes = max(3, int(5 * size_mult))
            biomes = self._generate_biomes(num_biomes, force_biome=biome, difficulty_mult=difficulty_mult)
            
            # Генерация достопримечательностей
            num_landmarks = max(2, int(8 * size_mult))
            landmarks = self._generate_landmarks(num_landmarks)
            
            # Генерация ресурсов
            num_resources = max(5, int(15 * size_mult))
            resources = self._generate_resources(num_resources)
            
            # Генерация погодных паттернов
            weather_patterns = self._generate_weather_patterns()
            
            # Генерация временного цикла
            time_cycle = self._generate_time_cycle()
            
            world = GeneratedWorld(
                id=f"WORLD_{uuid.uuid4().hex[:8]}",
                seed=self.seed,
                name=self._generate_world_name(),
                biomes=biomes,
                landmarks=landmarks,
                resources=resources,
                weather_patterns=weather_patterns,
                time_cycle=time_cycle
            )
            
            logger.info(f"Сгенерирован мир: {world.name} (seed: {self.seed})")
            return world
            
        except Exception as e:
            logger.error(f"Ошибка генерации мира: {e}")
            raise
    
    def _generate_biomes(
        self,
        num_biomes: int,
        *,
        force_biome: Optional[str] = None,
        difficulty_mult: float = 1.0,
    ) -> List[Dict[str, Any]]:
        """Генерация биомов"""
        biomes = []
        available_biomes = list(self.biome_templates.keys())
        
        # Выбор случайных биомов
        if force_biome and force_biome in available_biomes:
            remaining = [b for b in available_biomes if b != force_biome]
            count_remaining = max(0, min(num_biomes - 1, len(remaining)))
            selected_biomes = [force_biome] + self.random_generator.sample(remaining, count_remaining)
        else:
            selected_biomes = self.random_generator.sample(
                available_biomes,
                min(num_biomes, len(available_biomes))
            )
        
        for i, biome_type in enumerate(selected_biomes):
            template = self.biome_templates[biome_type]
            
            # Генерация размера и позиции биома
            biome_size = self.random_generator.uniform(0.8, 1.5)
            biome_position = {
                "x": self.random_generator.uniform(0, 100),
                "y": self.random_generator.uniform(0, 100),
                "size": biome_size,
                "difficulty": template["difficulty"] * biome_size * max(0.1, difficulty_mult)
            }
            
            biome = {
                "type": biome_type,
                "position": biome_position,
                "enemy_types": template["enemy_types"].copy(),
                "resources": template["resources"].copy(),
                "weather": template["weather"].copy(),
                "unique_features": self._generate_biome_features(biome_type)
            }
            
            biomes.append(biome)
        
        return biomes
    
    def _generate_biome_features(self, biome_type: str) -> List[str]:
        """Генерация уникальных особенностей биома"""
        features = []
        
        if biome_type == BiomeType.FOREST.value:
            features = ["ancient_trees", "mystical_clearings", "hidden_paths"]
        elif biome_type == BiomeType.DESERT.value:
            features = ["oasis", "sand_dunes", "ancient_ruins"]
        elif biome_type == BiomeType.MOUNTAIN.value:
            features = ["peaks", "valleys", "caves", "summit_temple"]
        elif biome_type == BiomeType.OCEAN.value:
            features = ["islands", "underwater_caves", "shipwrecks"]
        elif biome_type == BiomeType.VOLCANO.value:
            features = ["lava_rivers", "ash_fields", "fire_geysers"]
        
        # Случайный выбор особенностей
        num_features = self.random_generator.randint(1, len(features))
        return self.random_generator.sample(features, num_features)
    
    def _generate_landmarks(self, num_landmarks: int) -> List[Dict[str, Any]]:
        """Генерация достопримечательностей"""
        landmarks = []
        landmark_types = [
            "temple", "castle", "tower", "cave", "ruins", "monument",
            "bridge", "gate", "altar", "portal", "beacon", "sanctuary"
        ]
        
        for i in range(num_landmarks):
            landmark_type = self.random_generator.choice(landmark_types)
            
            landmark = {
                "id": f"LANDMARK_{uuid.uuid4().hex[:6]}",
                "type": landmark_type,
                "name": self._generate_landmark_name(landmark_type),
                "position": {
                    "x": self.random_generator.uniform(0, 100),
                    "y": self.random_generator.uniform(0, 100)
                },
                "size": self.random_generator.uniform(0.5, 2.0),
                "difficulty": self.random_generator.uniform(0.5, 3.0),
                "rewards": self._generate_landmark_rewards(landmark_type),
                "requirements": self._generate_landmark_requirements(landmark_type)
            }
            
            landmarks.append(landmark)
        
        return landmarks
    
    def _generate_landmark_name(self, landmark_type: str) -> str:
        """Генерация названия достопримечательности"""
        prefixes = ["Ancient", "Forgotten", "Sacred", "Cursed", "Mystical", "Hidden"]
        suffixes = ["Sanctuary", "Temple", "Tower", "Castle", "Ruins", "Monument"]
        
        prefix = self.random_generator.choice(prefixes)
        suffix = self.random_generator.choice(suffixes)
        
        return f"{prefix} {suffix}"
    
    def _generate_landmark_rewards(self, landmark_type: str) -> List[str]:
        """Генерация наград достопримечательности"""
        rewards = []
        
        if landmark_type in ["temple", "sanctuary"]:
            rewards.extend(["spiritual_insight", "divine_protection", "sacred_knowledge"])
        elif landmark_type in ["castle", "tower"]:
            rewards.extend(["military_tactics", "strategic_advantage", "royal_favor"])
        elif landmark_type in ["cave", "ruins"]:
            rewards.extend(["ancient_artifacts", "lost_technology", "forgotten_secrets"])
        
        # Случайный выбор наград
        num_rewards = self.random_generator.randint(1, 3)
        return self.random_generator.sample(rewards, min(num_rewards, len(rewards)))
    
    def _generate_landmark_requirements(self, landmark_type: str) -> Dict[str, Any]:
        """Генерация требований достопримечательности"""
        requirements = {}
        
        if landmark_type in ["temple", "sanctuary"]:
            requirements["spirituality"] = self.random_generator.uniform(0.3, 0.8)
        elif landmark_type in ["castle", "tower"]:
            requirements["combat_skill"] = self.random_generator.uniform(0.4, 0.9)
        elif landmark_type in ["cave", "ruins"]:
            requirements["exploration"] = self.random_generator.uniform(0.2, 0.7)
        
        return requirements
    
    def _generate_resources(self, num_resources: int) -> List[Dict[str, Any]]:
        """Генерация ресурсов"""
        resources = []
        resource_types = [
            "minerals", "herbs", "animals", "crystals", "metals", "plants",
            "water", "energy", "knowledge", "artifacts"
        ]
        
        for i in range(num_resources):
            resource_type = self.random_generator.choice(resource_types)
            
            resource = {
                "id": f"RESOURCE_{uuid.uuid4().hex[:6]}",
                "type": resource_type,
                "name": self._generate_resource_name(resource_type),
                "position": {
                    "x": self.random_generator.uniform(0, 100),
                    "y": self.random_generator.uniform(0, 100)
                },
                "abundance": self.random_generator.uniform(0.3, 1.0),
                "quality": self.random_generator.uniform(0.5, 1.0),
                "regeneration_rate": self.random_generator.uniform(0.1, 0.5)
            }
            
            resources.append(resource)
        
        return resources
    
    def _generate_resource_name(self, resource_type: str) -> str:
        """Генерация названия ресурса"""
        if resource_type == "minerals":
            return self.random_generator.choice(["Iron Ore", "Gold Vein", "Crystal Deposit"])
        elif resource_type == "herbs":
            return self.random_generator.choice(["Healing Herb", "Poison Plant", "Mystic Flower"])
        elif resource_type == "animals":
            return self.random_generator.choice(["Wild Deer", "Mystic Fox", "Ancient Bear"])
        
        return f"{resource_type.title()} Source"
    
    def _generate_weather_patterns(self) -> List[str]:
        """Генерация погодных паттернов"""
        base_patterns = ["clear", "cloudy", "rainy", "stormy", "foggy", "windy"]
        special_patterns = ["magical_storm", "time_distortion", "reality_shift", "elemental_chaos"]
        
        # Базовые паттерны всегда присутствуют
        weather = base_patterns.copy()
        
        # Случайные специальные паттерны
        if self.random_generator.random() < 0.3:
            num_special = self.random_generator.randint(1, 2)
            special_selected = self.random_generator.sample(special_patterns, num_special)
            weather.extend(special_selected)
        
        return weather
    
    def _generate_time_cycle(self) -> Dict[str, Any]:
        """Генерация временного цикла"""
        return {
            "day_length": self.random_generator.uniform(600, 1200),  # секунды
            "night_length": self.random_generator.uniform(300, 900),
            "season_length": self.random_generator.uniform(3600, 7200),
            "special_events": self._generate_special_events()
        }
    
    def _generate_special_events(self) -> List[Dict[str, Any]]:
        """Генерация специальных событий"""
        events = []
        event_types = [
            "eclipse", "meteor_shower", "aurora", "time_anomaly",
            "dimensional_rift", "cosmic_storm", "evolution_surge"
        ]
        
        for event_type in event_types:
            if self.random_generator.random() < 0.4:  # 40% шанс события
                event = {
                    "type": event_type,
                    "frequency": self.random_generator.uniform(0.1, 0.5),
                    "duration": self.random_generator.uniform(60, 300),
                    "effects": self._generate_event_effects(event_type)
                }
                events.append(event)
        
        return events
    
    def _generate_event_effects(self, event_type: str) -> List[str]:
        """Генерация эффектов события"""
        effects_map = {
            "eclipse": ["darkness", "magic_boost", "creature_behavior_change"],
            "meteor_shower": ["destruction", "rare_materials", "cosmic_energy"],
            "aurora": ["beauty", "spiritual_awakening", "elemental_balance"],
            "time_anomaly": ["age_acceleration", "time_slow", "temporal_paradox"],
            "dimensional_rift": ["reality_shift", "otherworldly_creatures", "space_distortion"],
            "cosmic_storm": ["radiation", "cosmic_power", "dimensional_tears"],
            "evolution_surge": ["rapid_mutation", "species_evolution", "genetic_chaos"]
        }
        
        return effects_map.get(event_type, ["unknown_effect"])
    
    def _generate_world_name(self) -> str:
        """Генерация названия мира"""
        world_prefixes = ["New", "Ancient", "Lost", "Hidden", "Mystic", "Forgotten"]
        world_suffixes = ["World", "Realm", "Dimension", "Plane", "Existence", "Reality"]
        
        prefix = self.random_generator.choice(world_prefixes)
        suffix = self.random_generator.choice(world_suffixes)
        
        return f"{prefix} {suffix}"
    
    def generate_enemy(self, biome: str = "forest", level: int = 1) -> GeneratedEnemy:
        """Генерация врага"""
        try:
            # Выбор типа врага на основе биома
            biome_template = self.biome_templates.get(biome, self.biome_templates[BiomeType.FOREST.value])
            enemy_type = self.random_generator.choice(biome_template["enemy_types"])
            
            # Получение шаблона врага
            enemy_template = self.enemy_templates.get(enemy_type, self.enemy_templates["neutral"])
            
            # Генерация характеристик
            stats = {}
            for stat_name, base_value in enemy_template["base_stats"].items():
                variance = enemy_template["stat_variance"]
                stat_value = base_value * (1 + self.random_generator.uniform(-variance, variance))
                stats[stat_name] = round(stat_value * level, 1)
            
            # Генерация сопротивлений и слабостей
            resistances = self._generate_resistances()
            weaknesses = self._generate_weaknesses()
            
            # Генерация способностей
            abilities = self._generate_abilities(enemy_template["abilities"])
            
            # Генерация внешнего вида
            appearance = self._generate_enemy_appearance(enemy_type, biome)
            
            # Генерация паттерна поведения
            behavior_pattern = self._generate_behavior_pattern(enemy_type)
            
            enemy = GeneratedEnemy(
                id=f"ENEMY_{uuid.uuid4().hex[:8]}",
                name=self._generate_enemy_name(enemy_type),
                enemy_type=enemy_type,
                biome=biome,
                level=level,
                stats=stats,
                resistances=resistances,
                weaknesses=weaknesses,
                abilities=abilities,
                appearance=appearance,
                behavior_pattern=behavior_pattern
            )
            
            logger.info(f"Сгенерирован враг: {enemy.name} (тип: {enemy_type}, уровень: {level})")
            return enemy
            
        except Exception as e:
            logger.error(f"Ошибка генерации врага: {e}")
            raise
    
    def _generate_resistances(self) -> Dict[str, float]:
        """Генерация сопротивлений"""
        resistances = {}
        damage_types = ["physical", "fire", "ice", "lightning", "poison", "magic"]
        
        for damage_type in damage_types:
            if self.random_generator.random() > 0.7:  # 30% шанс сопротивления
                resistance_value = self.random_generator.uniform(0.1, 0.5)
                resistances[damage_type] = round(resistance_value, 2)
        
        return resistances
    
    def _generate_weaknesses(self) -> Dict[str, float]:
        """Генерация слабостей"""
        weaknesses = {}
        damage_types = ["physical", "fire", "ice", "lightning", "poison", "magic"]
        
        for damage_type in damage_types:
            if self.random_generator.random() > 0.7:  # 30% шанс слабости
                weakness_value = self.random_generator.uniform(0.1, 0.5)
                weaknesses[damage_type] = round(weakness_value, 2)
        
        return weaknesses
    
    def _generate_abilities(self, base_abilities: List[str]) -> List[str]:
        """Генерация способностей"""
        abilities = base_abilities.copy()
        
        # Дополнительные случайные способности
        additional_abilities = [
            "stealth", "regeneration", "teleport", "summon", "transform",
            "elemental_attack", "heal", "buff", "debuff", "counter"
        ]
        
        num_additional = self.random_generator.randint(0, 2)
        if num_additional > 0:
            selected = self.random_generator.sample(additional_abilities, num_additional)
            abilities.extend(selected)
        
        return abilities
    
    def _generate_enemy_appearance(self, enemy_type: str, biome: str) -> Dict[str, Any]:
        """Генерация внешнего вида врага"""
        appearance = {
            "size": self.random_generator.uniform(0.8, 1.5),
            "color_scheme": self._generate_color_scheme(biome),
            "special_features": []
        }
        
        # Специальные особенности на основе типа
        if enemy_type == "boss":
            appearance["special_features"].extend(["aura", "crown", "wings"])
        elif enemy_type == "elite":
            appearance["special_features"].extend(["armor", "weapon", "markings"])
        
        return appearance
    
    def _generate_color_scheme(self, biome: str) -> List[str]:
        """Генерация цветовой схемы"""
        biome_colors = {
            "forest": ["green", "brown", "gold"],
            "desert": ["yellow", "orange", "red"],
            "mountain": ["gray", "white", "blue"],
            "ocean": ["blue", "teal", "purple"],
            "volcano": ["red", "black", "orange"]
        }
        
        base_colors = biome_colors.get(biome, ["gray", "brown", "black"])
        return self.random_generator.sample(base_colors, min(2, len(base_colors)))
    
    def _generate_behavior_pattern(self, enemy_type: str) -> str:
        """Генерация паттерна поведения"""
        behavior_patterns = {
            "predator": "hunt_and_chase",
            "prey": "flee_and_hide",
            "neutral": "observe_and_retreat",
            "boss": "aggressive_and_strategic",
            "elite": "tactical_and_adaptive"
        }
        
        return behavior_patterns.get(enemy_type, "basic_ai")
    
    def _generate_enemy_name(self, enemy_type: str) -> str:
        """Генерация имени врага"""
        prefix = self.random_generator.choice(self.name_prefixes)
        suffix = self.random_generator.choice(self.name_suffixes)
        
        return f"{prefix} {suffix}"
    
    def generate_weapon(self, weapon_type: str = None, tier: int = 1) -> GeneratedWeapon:
        """Генерация оружия"""
        try:
            # Выбор типа оружия
            if not weapon_type:
                weapon_type = self.random_generator.choice(list(self.weapon_templates.keys()))
            
            weapon_template = self.weapon_templates[weapon_type]
            
            # Расчёт урона с учётом тира
            base_damage = weapon_template["base_damage"]
            tier_multiplier = weapon_template["tier_multipliers"][min(tier - 1, len(weapon_template["tier_multipliers"]) - 1)]
            damage_variance = weapon_template["damage_variance"]
            
            final_damage = base_damage * tier_multiplier * (1 + self.random_generator.uniform(-damage_variance, damage_variance))
            
            # Генерация эффектов
            base_effects = weapon_template["effects"].copy()
            additional_effects = self._generate_weapon_effects(weapon_type, tier)
            all_effects = base_effects + additional_effects
            
            # Генерация требований
            requirements = self._generate_weapon_requirements(tier)
            
            # Генерация внешнего вида
            appearance = self._generate_weapon_appearance(weapon_type, tier)
            
            # Расчёт прочности
            durability = int(100 * tier * (1 + self.random_generator.uniform(0.1, 0.3)))
            
            weapon = GeneratedWeapon(
                id=f"WEAPON_{uuid.uuid4().hex[:8]}",
                name=self._generate_weapon_name(weapon_type, tier),
                weapon_type=weapon_type,
                tier=tier,
                damage=round(final_damage, 1),
                effects=all_effects,
                requirements=requirements,
                appearance=appearance,
                durability=durability
            )
            
            logger.info(f"Сгенерировано оружие: {weapon.name} (тип: {weapon_type}, тир: {tier})")
            return weapon
            
        except Exception as e:
            logger.error(f"Ошибка генерации оружия: {e}")
            raise
    
    def _generate_weapon_effects(self, weapon_type: str, tier: int) -> List[str]:
        """Генерация эффектов оружия"""
        effects = []
        
        # Базовые эффекты для всех оружий
        base_effects = ["durable", "balanced"]
        
        # Специальные эффекты на основе типа
        type_effects = {
            "sword": ["sharp", "precise", "versatile"],
            "axe": ["heavy", "armor_piercing", "brutal"],
            "bow": ["ranged", "fast", "silent"],
            "staff": ["magical", "elemental", "channeling"]
        }
        
        # Специальные эффекты на основе тира
        tier_effects = {
            1: [],
            2: ["enhanced"],
            3: ["superior", "enchanted"],
            4: ["masterwork", "legendary"],
            5: ["mythical", "divine"]
        }
        
        # Сбор всех эффектов
        effects.extend(base_effects)
        effects.extend(type_effects.get(weapon_type, []))
        effects.extend(tier_effects.get(tier, []))
        
        # Случайный выбор дополнительных эффектов
        num_additional = min(tier, 2)
        if len(effects) > num_additional:
            effects = self.random_generator.sample(effects, num_additional)
        
        return effects
    
    def _generate_weapon_requirements(self, tier: int) -> Dict[str, float]:
        """Генерация требований оружия"""
        requirements = {}
        
        # Базовые требования
        requirements["level"] = tier * 5
        requirements["strength"] = tier * 2
        requirements["dexterity"] = tier * 1.5
        
        # Случайные дополнительные требования
        if tier >= 3:
            requirements["intelligence"] = tier * 1.2
        if tier >= 4:
            requirements["charisma"] = tier * 0.8
        
        return requirements
    
    def _generate_weapon_appearance(self, weapon_type: str, tier: int) -> Dict[str, Any]:
        """Генерация внешнего вида оружия"""
        appearance = {
            "size": 1.0 + (tier - 1) * 0.1,
            "material": self._generate_weapon_material(tier),
            "decorations": []
        }
        
        # Украшения на основе тира
        if tier >= 3:
            appearance["decorations"].append("engravings")
        if tier >= 4:
            appearance["decorations"].append("gems")
        if tier >= 5:
            appearance["decorations"].append("magical_runes")
        
        return appearance
    
    def _generate_weapon_material(self, tier: int) -> str:
        """Генерация материала оружия"""
        materials = {
            1: "iron",
            2: "steel",
            3: "mithril",
            4: "adamantium",
            5: "orichalcum"
        }
        
        return materials.get(tier, "iron")
    
    def _generate_weapon_name(self, weapon_type: str, tier: int) -> str:
        """Генерация названия оружия"""
        tier_names = {
            1: "Basic",
            2: "Enhanced",
            3: "Superior",
            4: "Masterwork",
            5: "Legendary"
        }
        
        tier_name = tier_names.get(tier, "Basic")
        weapon_name = weapon_type.title()
        
        return f"{tier_name} {weapon_name}"
    
    def generate_item(self, item_type: str = None, rarity: str = None) -> GeneratedItem:
        """Генерация предмета"""
        try:
            # Выбор типа предмета
            if not item_type:
                item_type = self.random_generator.choice(list(self.item_templates.keys()))
            
            # Выбор редкости
            if not rarity:
                rarity_weights = self.item_templates[item_type]["rarity_weights"]
                rarity_values = list(ItemRarity)
                rarity = self.random_generator.choices(rarity_values, weights=rarity_weights)[0].value
            
            # Генерация эффектов
            base_effects = self.item_templates[item_type]["effects"].copy()
            additional_effects = self._generate_item_effects(item_type, rarity)
            all_effects = base_effects + additional_effects
            
            # Расчёт стоимости и веса
            rarity_multipliers = {
                "common": 1.0,
                "uncommon": 2.0,
                "rare": 5.0,
                "epic": 15.0,
                "legendary": 50.0
            }
            
            base_value = 10
            value = int(base_value * rarity_multipliers.get(rarity, 1.0))
            weight = self.random_generator.uniform(0.1, 2.0)
            
            # Генерация внешнего вида
            appearance = self._generate_item_appearance(item_type, rarity)
            
            item = GeneratedItem(
                id=f"ITEM_{uuid.uuid4().hex[:8]}",
                name=self._generate_item_name(item_type, rarity),
                item_type=item_type,
                rarity=rarity,
                effects=all_effects,
                value=value,
                weight=round(weight, 2),
                appearance=appearance
            )
            
            logger.info(f"Сгенерирован предмет: {item.name} (тип: {item_type}, редкость: {rarity})")
            return item
            
        except Exception as e:
            logger.error(f"Ошибка генерации предмета: {e}")
            raise
    
    def _generate_item_effects(self, item_type: str, rarity: str) -> List[str]:
        """Генерация эффектов предмета"""
        effects = []
        
        # Эффекты на основе редкости
        rarity_effects = {
            "common": [],
            "uncommon": ["minor_boost"],
            "rare": ["moderate_boost", "special_ability"],
            "epic": ["major_boost", "unique_ability", "set_bonus"],
            "legendary": ["legendary_boost", "mythical_ability", "reality_altering"]
        }
        
        effects.extend(rarity_effects.get(rarity, []))
        
        # Случайные дополнительные эффекты
        if rarity in ["rare", "epic", "legendary"]:
            additional_effects = ["elemental_resistance", "stat_boost", "special_effect"]
            num_additional = 1 if rarity == "rare" else 2
            selected = self.random_generator.sample(additional_effects, num_additional)
            effects.extend(selected)
        
        return effects
    
    def _generate_item_appearance(self, item_type: str, rarity: str) -> Dict[str, Any]:
        """Генерация внешнего вида предмета"""
        appearance = {
            "size": self.random_generator.uniform(0.5, 1.5),
            "material": self._generate_item_material(rarity),
            "glow": rarity in ["epic", "legendary"]
        }
        
        return appearance
    
    def _generate_item_material(self, rarity: str) -> str:
        """Генерация материала предмета"""
        materials = {
            "common": "basic",
            "uncommon": "enhanced",
            "rare": "precious",
            "epic": "exotic",
            "legendary": "mythical"
        }
        
        return materials.get(rarity, "basic")
    
    def _generate_item_name(self, item_type: str, rarity: str) -> str:
        """Генерация названия предмета"""
        rarity_names = {
            "common": "Basic",
            "uncommon": "Enhanced",
            "rare": "Rare",
            "epic": "Epic",
            "legendary": "Legendary"
        }
        
        rarity_name = rarity_names.get(rarity, "Basic")
        item_name = item_type.title()
        
        return f"{rarity_name} {item_name}"
    
    def set_seed(self, seed: int):
        """Установка нового seed"""
        self.seed = seed
        self.random_generator = random.Random(seed)
        logger.info(f"Seed изменён на: {seed}")
    
    def get_current_seed(self) -> int:
        """Получение текущего seed"""
        return self.seed
    
    def generate_hash_from_seed(self) -> str:
        """Генерация хеша из текущего seed"""
        return hashlib.md5(str(self.seed).encode()).hexdigest()[:8]
    
    def generate_level_content(self, level_config: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация контента для нового уровня"""
        try:
            level_number = level_config.get("level_number", 1)
            difficulty_multiplier = level_config.get("difficulty_multiplier", 1.0)
            world_size = level_config.get("world_size", 1000)
            enemy_count = level_config.get("enemy_count", 5)
            item_count = level_config.get("item_count", 10)
            obstacle_count = level_config.get("obstacle_count", 3)
            player_data = level_config.get("player_data", {})
            
            # Генерируем новый seed для уровня
            level_seed = self.seed + level_number * 1000
            self.set_seed(level_seed)
            
            # Генерируем мир
            world_config = {
                "biome": self.random_generator.choice(list(BiomeType)).value,
                "size": "large" if world_size > 1200 else "medium",
                "difficulty": difficulty_multiplier
            }
            
            # Генерируем врагов
            enemies = []
            for i in range(enemy_count):
                enemy = self.generate_enemy(
                    biome=world_config["biome"],
                    level=int(level_number * difficulty_multiplier),
                    enemy_type=self.random_generator.choice(list(EnemyType)).value
                )
                enemies.append(enemy)
            
            # Генерируем предметы
            items = []
            for i in range(item_count):
                item = self.generate_item(
                    item_type=self.random_generator.choice(["potion", "weapon", "armor", "tool", "artifact"]),
                    rarity=self.random_generator.choice(list(ItemRarity)).value
                )
                items.append(item)
            
            # Генерируем препятствия
            obstacles = []
            for i in range(obstacle_count):
                obstacle = {
                    "id": f"OBSTACLE_{uuid.uuid4().hex[:8]}",
                    "type": self.random_generator.choice(["trap", "barrier", "hazard"]),
                    "position": (
                        self.random_generator.randint(-world_size//2, world_size//2),
                        self.random_generator.randint(-world_size//2, world_size//2),
                        0
                    ),
                    "effect": self.random_generator.choice(["damage", "slow", "confuse", "teleport"])
                }
                obstacles.append(obstacle)
            
            # Создаем конфигурацию уровня
            level_content = {
                "level_number": level_number,
                "world_config": world_config,
                "enemies": [enemy.__dict__ for enemy in enemies],
                "items": [item.__dict__ for item in items],
                "obstacles": obstacles,
                "player_data": player_data,
                "world_size": world_size,
                "difficulty_multiplier": difficulty_multiplier
            }
            
            logger.info(f"Сгенерирован контент для уровня {level_number}")
            return level_content
            
        except Exception as e:
            logger.error(f"Ошибка генерации контента уровня: {e}")
            # Возвращаем базовую конфигурацию в случае ошибки
            return {
                "level_number": level_config.get("level_number", 1),
                "world_config": {"biome": "forest", "size": "medium", "difficulty": 1.0},
                "enemies": [],
                "items": [],
                "obstacles": [],
                "player_data": level_config.get("player_data", {}),
                "world_size": 1000,
                "difficulty_multiplier": 1.0
            }
