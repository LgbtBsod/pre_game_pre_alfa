#!/usr/bin/env python3
"""
Генератор контента для эволюционной адаптации.
Создает миры, врагов, оружие и предметы на основе данных из БД.
"""

import random
import math
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Импортируем менеджер данных для загрузки контента из БД
try:
    from .data_manager import data_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logging.warning("DataManager недоступен, используется локальный контент")

logger = logging.getLogger(__name__)


class BiomeType(Enum):
    """Типы биомов"""
    FOREST = "forest"
    DESERT = "desert"
    MOUNTAIN = "mountain"
    SWAMP = "swamp"
    TUNDRA = "tundra"
    VOLCANO = "volcano"
    CRYSTAL_CAVE = "crystal_cave"
    FLOATING_ISLANDS = "floating_islands"
    UNDERWATER = "underwater"
    SPACE_STATION = "space_station"


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
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"
    EXPLOSIVE = "explosive"
    ENERGY = "energy"
    BIOLOGICAL = "biological"


class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


@dataclass
class GeneratedEnemy:
    """Сгенерированный враг"""
    enemy_id: str
    name: str
    enemy_type: str
    level: int
    health: float
    damage: float
    speed: float
    defense: float
    behavior: str
    abilities: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    resistances: List[str] = field(default_factory=list)
    loot_table: List[str] = field(default_factory=list)
    experience_reward: int = 0
    ai_personality: str = "balanced"


@dataclass
class GeneratedWeapon:
    """Сгенерированное оружие"""
    weapon_id: str
    name: str
    weapon_type: str
    damage_type: str
    rarity: str
    base_damage: float
    attack_speed: float
    special_effects: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    durability: float = 100.0


@dataclass
class GeneratedItem:
    """Сгенерированный предмет"""
    item_id: str
    name: str
    item_type: str
    rarity: str
    value: int
    weight: float
    effects: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedWorld:
    """Сгенерированный мир"""
    world_id: str
    name: str
    biome: str
    size: str
    difficulty: float
    width: int
    height: int
    layers: int
    features: List[str] = field(default_factory=list)
    enemies: List[GeneratedEnemy] = field(default_factory=list)
    items: List[GeneratedItem] = field(default_factory=list)
    weather_patterns: List[str] = field(default_factory=list)
    time_cycle: str = "normal"
    gravity: float = 1.0
    atmosphere: str = "breathable"


class ContentGenerator:
    """Генератор контента"""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or random.randint(1, 999999)
        random.seed(self.seed)
        
        # Инициализация шаблонов
        self.enemy_templates = self._init_enemy_templates()
        self.weapon_templates = self._init_weapon_templates()
        self.item_templates = self._init_item_templates()
        self.biome_templates = self._init_biome_templates()
        
        # Попытка загрузить данные из БД
        self.db_enemy_types = {}
        self.db_weapons = {}
        self.db_items = {}
        if DB_AVAILABLE:
            self._load_database_content()
        
        logger.info(f"Генератор контента инициализирован с seed: {self.seed}")
    
    def _load_database_content(self):
        """Загружает контент из базы данных"""
        try:
            # Загружаем типы врагов
            entities = data_manager.get_all_entities()
            for entity in entities:
                if entity.type == "enemy":
                    self.db_enemy_types[entity.id] = {
                        "name": entity.name,
                        "base_health": entity.base_health,
                        "base_damage": entity.base_damage,
                        "base_speed": entity.base_speed,
                        "base_armor": entity.base_armor,
                        "behavior": entity.behavior_pattern or "balanced"
                    }
            
            # Загружаем оружие
            weapons = data_manager.get_all_items()
            for weapon in weapons:
                if weapon.type == "weapon":
                    self.db_weapons[weapon.id] = {
                        "name": weapon.name,
                        "base_damage": weapon.base_damage,
                        "attack_speed": weapon.attack_speed,
                        "rarity": weapon.rarity
                    }
            
            # Загружаем предметы
            items = data_manager.get_all_items()
            for item in items:
                self.db_items[item.id] = {
                    "name": item.name,
                    "type": item.type,
                    "rarity": item.rarity,
                    "value": item.cost,
                    "weight": item.weight
                }
            
            logger.info(f"Загружено из БД: {len(self.db_enemy_types)} врагов, {len(self.db_weapons)} оружия, {len(self.db_items)} предметов")
            
        except Exception as e:
            logger.warning(f"Не удалось загрузить данные из БД: {e}")
    
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
            "melee": {
                "base_stats": {"damage": 20, "speed": 1.0, "range": 1.5, "accuracy": 0.9},
                "stat_variance": 0.25,
                "special_effects": ["bleeding", "armor_penetration", "critical_strike"]
            },
            "ranged": {
                "base_stats": {"damage": 15, "speed": 1.5, "range": 10.0, "accuracy": 0.8},
                "stat_variance": 0.3,
                "special_effects": ["piercing", "explosive", "rapid_fire"]
            },
            "magic": {
                "base_stats": {"damage": 30, "speed": 0.8, "range": 5.0, "accuracy": 0.95},
                "stat_variance": 0.2,
                "special_effects": ["elemental_damage", "area_effect", "mana_burn"]
            }
        }
    
    def _init_item_templates(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация шаблонов предметов"""
        return {
            "weapon": {
                "base_stats": {"value": 100, "weight": 3.0},
                "stat_variance": 0.4,
                "effects": ["damage_boost", "speed_boost", "critical_boost"]
            },
            "armor": {
                "base_stats": {"value": 80, "weight": 5.0},
                "stat_variance": 0.3,
                "effects": ["defense_boost", "resistance_boost", "mobility_boost"]
            },
            "consumable": {
                "base_stats": {"value": 25, "weight": 0.5},
                "stat_variance": 0.5,
                "effects": ["healing", "mana_restore", "buff_temporary"]
            }
        }
    
    def _init_biome_templates(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация шаблонов биомов"""
        return {
            "forest": {
                "features": ["trees", "undergrowth", "water_bodies"],
                "enemy_types": ["predator", "prey", "neutral"],
                "weather": ["rain", "fog", "sunny"],
                "difficulty_modifier": 1.0
            },
            "desert": {
                "features": ["sand_dunes", "oasis", "ruins"],
                "enemy_types": ["predator", "boss"],
                "weather": ["heat_wave", "sandstorm", "clear"],
                "difficulty_modifier": 1.3
            },
            "mountain": {
                "features": ["peaks", "caves", "cliffs"],
                "enemy_types": ["elite", "boss", "neutral"],
                "weather": ["snow", "wind", "clear"],
                "difficulty_modifier": 1.5
            },
            "swamp": {
                "features": ["marsh", "trees", "water"],
                "enemy_types": ["predator", "neutral", "boss"],
                "weather": ["rain", "fog", "humid"],
                "difficulty_modifier": 1.2
            }
        }
    
    def generate_world(self, world_size: str = "medium", biome: Optional[str] = None, difficulty: float = 1.0) -> GeneratedWorld:
        """Генерирует новый мир"""
        world_id = f"WORLD_{random.randint(10000, 99999)}"
        
        # Выбор биома
        if biome is None:
            biome = random.choice(list(BiomeType)).value
        
        # Размеры мира
        size_map = {
            "small": (50, 50, 3),
            "medium": (100, 100, 5),
            "large": (200, 200, 8),
            "huge": (400, 400, 12)
        }
        width, height, layers = size_map.get(world_size, (100, 100, 5))
        
        # Генерация особенностей
        features = self._generate_world_features(biome, world_size)
        
        # Генерация врагов
        enemies = self._generate_enemies_for_world(biome, difficulty, world_size)
        
        # Генерация предметов
        items = self._generate_items_for_world(biome, difficulty, world_size)
        
        # Генерация погоды
        weather_patterns = self._generate_weather_patterns(biome)
        
        world = GeneratedWorld(
            world_id=world_id,
            name=f"Мир {biome.title()} #{world_id[-5:]}",
            biome=biome,
            size=world_size,
            difficulty=difficulty,
            width=width,
            height=height,
            layers=layers,
            features=features,
            enemies=enemies,
            items=items,
            weather_patterns=weather_patterns,
            time_cycle="normal",
            gravity=1.0,
            atmosphere="breathable"
        )
        
        logger.info(f"Сгенерирован мир: {world.name} (биом: {biome}, размер: {world_size}, сложность: {difficulty:.2f})")
        return world
    
    def _generate_world_features(self, biome: str, world_size: str) -> List[str]:
        """Генерирует особенности мира"""
        features = []
        biome_template = self.biome_templates.get(biome, self.biome_templates["forest"])
        
        # Базовые особенности биома
        features.extend(biome_template["features"])
        
        # Дополнительные особенности на основе размера
        if world_size in ["large", "huge"]:
            features.extend(["ancient_ruins", "hidden_caves", "treasure_hoards"])
        
        if world_size == "huge":
            features.extend(["floating_islands", "time_anomalies", "dimensional_portals"])
        
        # Случайные особенности
        random_features = [
            "crystal_deposits", "magical_springs", "ancient_trees",
            "underground_cities", "floating_rocks", "energy_fields"
        ]
        features.extend(random.sample(random_features, random.randint(2, 4)))
        
        return features
    
    def _generate_enemies_for_world(self, biome: str, difficulty: float, world_size: str) -> List[GeneratedEnemy]:
        """Генерирует врагов для мира"""
        enemies = []
        biome_template = self.biome_templates.get(biome, self.biome_templates["forest"])
        
        # Определяем количество врагов на основе размера мира
        size_enemy_counts = {"small": 5, "medium": 12, "large": 25, "huge": 50}
        enemy_count = size_enemy_counts.get(world_size, 12)
        
        # Используем данные из БД если доступны
        if self.db_enemy_types:
            enemy_types = list(self.db_enemy_types.keys())
            for i in range(enemy_count):
                enemy_type_id = random.choice(enemy_types)
                enemy_data = self.db_enemy_types[enemy_type_id]
                
                # Модифицируем характеристики на основе сложности
                level = max(1, int(difficulty * random.randint(1, 10)))
                health = enemy_data["base_health"] * difficulty * (0.8 + random.random() * 0.4)
                damage = enemy_data["base_damage"] * difficulty * (0.8 + random.random() * 0.4)
                
                enemy = GeneratedEnemy(
                    enemy_id=f"{enemy_type_id}_{i:03d}",
                    name=f"{enemy_data['name']} #{i+1}",
                    enemy_type=enemy_type_id,
                    level=level,
                    health=health,
                    damage=damage,
                    speed=enemy_data["base_speed"],
                    defense=enemy_data["base_armor"],
                    behavior=enemy_data["behavior"],
                    abilities=["basic_attack"],
                    weaknesses=[],
                    resistances=[],
                    loot_table=[],
                    experience_reward=level * 10,
                    ai_personality="balanced"
                )
                enemies.append(enemy)
        else:
            # Fallback на локальные шаблоны
            for i in range(enemy_count):
                enemy_type = random.choice(biome_template["enemy_types"])
                template = self.enemy_templates[enemy_type]
                
                enemy = self._generate_enemy_from_template(template, difficulty, i)
                enemies.append(enemy)
        
        return enemies
    
    def _generate_enemy_from_template(self, template: Dict[str, Any], difficulty: float, index: int) -> GeneratedEnemy:
        """Генерирует врага из шаблона"""
        stats = template["base_stats"]
        variance = template["stat_variance"]
        
        # Применяем вариацию и сложность
        health = stats["hp"] * difficulty * (1.0 + random.uniform(-variance, variance))
        damage = stats["damage"] * difficulty * (1.0 + random.uniform(-variance, variance))
        speed = stats["speed"] * (1.0 + random.uniform(-variance, variance))
        defense = stats["defense"] * (1.0 + random.uniform(-variance, variance))
        
        enemy = GeneratedEnemy(
            enemy_id=f"enemy_{index:03d}",
            name=f"Враг {index+1}",
            enemy_type=template["behavior"],
            level=max(1, int(difficulty * random.randint(1, 10))),
            health=health,
            damage=damage,
            speed=speed,
            defense=defense,
            behavior=template["behavior"],
            abilities=template["abilities"].copy(),
            weaknesses=[],
            resistances=[],
            loot_table=[],
            experience_reward=int(difficulty * random.randint(10, 50)),
            ai_personality="balanced"
        )
        
        return enemy
    
    def _generate_items_for_world(self, biome: str, difficulty: float, world_size: str) -> List[GeneratedItem]:
        """Генерирует предметы для мира"""
        items = []
        size_item_counts = {"small": 8, "medium": 20, "large": 45, "huge": 100}
        item_count = size_item_counts.get(world_size, 20)
        
        # Используем данные из БД если доступны
        if self.db_items:
            item_types = list(self.db_items.keys())
            for i in range(item_count):
                item_type_id = random.choice(item_types)
                item_data = self.db_items[item_type_id]
                
                item = GeneratedItem(
                    item_id=f"{item_type_id}_{i:03d}",
                    name=f"{item_data['name']} #{i+1}",
                    item_type=item_data["type"],
                    rarity=item_data["rarity"],
                    value=int(item_data["value"] * difficulty * (0.8 + random.random() * 0.4)),
                    weight=item_data["weight"],
                    effects=[],
                    requirements={}
                )
                items.append(item)
        else:
            # Fallback на локальные шаблоны
            for i in range(item_count):
                item_type = random.choice(list(self.item_templates.keys()))
                template = self.item_templates[item_type]
                
                item = self._generate_item_from_template(template, difficulty, i)
                items.append(item)
        
        return items
    
    def _generate_item_from_template(self, template: Dict[str, Any], difficulty: float, index: int) -> GeneratedItem:
        """Генерирует предмет из шаблона"""
        stats = template["base_stats"]
        variance = template["stat_variance"]
        
        value = int(stats["value"] * difficulty * (1.0 + random.uniform(-variance, variance)))
        weight = stats["weight"] * (1.0 + random.uniform(-variance, variance))
        
        item = GeneratedItem(
            item_id=f"item_{index:03d}",
            name=f"Предмет {index+1}",
            item_type=template.get("type", "generic"),
            rarity=random.choice(list(ItemRarity)).value,
            value=value,
            weight=weight,
            effects=random.sample(template["effects"], random.randint(1, 2)),
            requirements={}
        )
        
        return item
    
    def _generate_weather_patterns(self, biome: str) -> List[str]:
        """Генерирует паттерны погоды"""
        biome_template = self.biome_templates.get(biome, self.biome_templates["forest"])
        base_weather = biome_template["weather"]
        
        # Добавляем случайные погодные явления
        special_weather = [
            "aurora_borealis", "meteor_shower", "time_dilation",
            "reality_shift", "dimensional_storm", "magical_rain"
        ]
        
        weather_patterns = base_weather.copy()
        if random.random() < 0.3:  # 30% шанс особой погоды
            weather_patterns.extend(random.sample(special_weather, random.randint(1, 2)))
        
        return weather_patterns
    
    def generate_enemy(self, enemy_type: str, level: int, difficulty: float = 1.0) -> GeneratedEnemy:
        """Генерирует конкретного врага"""
        if enemy_type in self.enemy_templates:
            template = self.enemy_templates[enemy_type]
            return self._generate_enemy_from_template(template, difficulty, 0)
        else:
            # Создаем врага с базовыми характеристиками
            return GeneratedEnemy(
                enemy_id=f"enemy_{random.randint(1000, 9999)}",
                name=f"Неизвестный враг",
                enemy_type=enemy_type,
                level=level,
                health=50.0 * difficulty,
                damage=10.0 * difficulty,
                speed=1.0,
                defense=5.0,
                behavior="balanced",
                abilities=["basic_attack"],
                weaknesses=[],
                resistances=[],
                loot_table=[],
                experience_reward=level * 10,
                ai_personality="balanced"
            )
    
    def generate_weapon(self, weapon_type: str, rarity: str, level: int) -> GeneratedWeapon:
        """Генерирует оружие"""
        if weapon_type in self.weapon_templates:
            template = self.weapon_templates[weapon_type]
            stats = template["base_stats"]
            
            # Модифицируем характеристики на основе уровня и редкости
            rarity_multipliers = {
                "common": 1.0, "uncommon": 1.2, "rare": 1.5,
                "epic": 2.0, "legendary": 3.0, "mythic": 4.0
            }
            multiplier = rarity_multipliers.get(rarity, 1.0)
            
            weapon = GeneratedWeapon(
                weapon_id=f"weapon_{random.randint(1000, 9999)}",
                name=f"{weapon_type.title()} оружие",
                weapon_type=weapon_type,
                damage_type="physical",
                rarity=rarity,
                base_damage=stats["damage"] * multiplier * (1.0 + level * 0.1),
                attack_speed=stats["speed"],
                special_effects=random.sample(template["special_effects"], random.randint(1, 2)),
                requirements={"level": level},
                durability=100.0 * multiplier
            )
            return weapon
        else:
            # Создаем базовое оружие
            return GeneratedWeapon(
                weapon_id=f"weapon_{random.randint(1000, 9999)}",
                name="Базовое оружие",
                weapon_type="generic",
                damage_type="physical",
                rarity="common",
                base_damage=10.0 + level * 2,
                attack_speed=1.0,
                special_effects=[],
                requirements={"level": level},
                durability=100.0
            )
    
    def get_available_enemy_types(self) -> List[str]:
        """Возвращает доступные типы врагов"""
        if self.db_enemy_types:
            return list(self.db_enemy_types.keys())
        else:
            return list(self.enemy_templates.keys())
    
    def get_available_weapon_types(self) -> List[str]:
        """Возвращает доступные типы оружия"""
        if self.db_weapons:
            return list(self.db_weapons.keys())
        else:
            return list(self.weapon_templates.keys())
    
    def get_available_item_types(self) -> List[str]:
        """Возвращает доступные типы предметов"""
        if self.db_items:
            return list(self.db_items.keys())
        else:
            return list(self.item_templates.keys())


# Глобальный экземпляр генератора
content_generator = ContentGenerator()
