#!/usr/bin/env python3
"""
Система генерации контента для игровых сессий.
Генерирует уникальный контент для каждой сессии с GUID в 16-ричной системе.
"""

import random
import uuid
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    ARTIFACT = "artifact"


class EnemyType(Enum):
    """Типы врагов"""
    PREDATOR = "predator"
    HERBIVORE = "herbivore"
    NEUTRAL = "neutral"
    BOSS = "boss"


class SkillType(Enum):
    """Типы навыков"""
    COMBAT = "combat"
    UTILITY = "utility"
    PASSIVE = "passive"
    ACTIVE = "active"


class GeneType(Enum):
    """Типы генов"""
    STRENGTH = "strength"
    AGILITY = "agility"
    INTELLIGENCE = "intelligence"
    ENDURANCE = "endurance"
    EVOLUTION = "evolution"


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
    MYTHIC = "mythic"


@dataclass
class GeneratedItem:
    """Сгенерированный предмет"""
    guid: str
    name: str
    item_type: ItemType
    rarity: str
    stats: Dict[str, Any]
    description: str
    position: tuple


@dataclass
class GeneratedEnemy:
    """Сгенерированный враг"""
    guid: str
    name: str
    enemy_type: EnemyType
    level: int
    stats: Dict[str, Any]
    abilities: List[str]
    position: tuple


@dataclass
class GeneratedSkill:
    """Сгенерированный навык"""
    guid: str
    name: str
    skill_type: SkillType
    level: int
    effects: Dict[str, Any]
    description: str


@dataclass
class GeneratedGene:
    """Сгенерированный ген"""
    guid: str
    name: str
    gene_type: GeneType
    level: int
    effects: Dict[str, Any]
    description: str


@dataclass
class GeneratedAccessory:
    """Сгенерированный аксессуар"""
    guid: str
    name: str
    slot: str
    stats: Dict[str, Any]
    effects: List[str]
    position: tuple


@dataclass
class GeneratedWeapon:
    """Сгенерированное оружие"""
    guid: str
    name: str
    weapon_type: WeaponType
    tier: int
    damage: float
    effects: List[str]
    requirements: Dict[str, Any]
    appearance: Dict[str, Any]
    durability: int
    position: tuple


@dataclass
class GeneratedWorld:
    """Сгенерированный мир"""
    guid: str
    name: str
    biome: BiomeType
    size: str
    width: int
    height: int
    difficulty: float
    seed: int
    features: List[str]
    weather: str


class ContentGenerator:
    """Генератор контента для сессий"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(1, 999999)
        self.rng = random.Random(self.seed)
        
        # Константы для генерации
        self.ITEM_NAMES = [
            "Меч", "Топор", "Лук", "Кинжал", "Молот", "Копье", "Щит", "Шлем",
            "Нагрудник", "Поножи", "Сапоги", "Перчатки", "Пояс", "Плащ",
            "Зелье", "Свиток", "Кристалл", "Руна", "Амулет", "Кольцо"
        ]
        
        self.ENEMY_NAMES = [
            "Волк", "Медведь", "Орк", "Гоблин", "Тролль", "Дракон", "Гигант",
            "Призрак", "Скелет", "Зомби", "Демон", "Ангел", "Элементаль",
            "Кентавр", "Минотавр", "Гарпия", "Василиск", "Феникс"
        ]
        
        self.SKILL_NAMES = [
            "Атака", "Защита", "Исцеление", "Магия", "Скрытность", "Выживание",
            "Крафтинг", "Торговля", "Дипломатия", "Тактика", "Лидерство",
            "Анализ", "Интуиция", "Рефлексы", "Выносливость", "Сила воли"
        ]
        
        self.GENE_NAMES = [
            "Сила", "Ловкость", "Интеллект", "Выносливость", "Эволюция",
            "Адаптация", "Мутация", "Регенерация", "Иммунитет", "Метаболизм",
            "Нейропластичность", "Эпигенетика", "Теломераза", "Апоптоз"
        ]
        
        self.ACCESSORY_NAMES = [
            "Ожерелье", "Браслет", "Серьги", "Корона", "Маска", "Плащ",
            "Пояс", "Перчатки", "Сапоги", "Шарф", "Шляпа", "Очки"
        ]
        
        # Префиксы и суффиксы для разнообразия
        self.PREFIXES = ["Древний", "Магический", "Эпический", "Легендарный", "Мистический", "Священный", "Проклятый", "Зачарованный"]
        self.SUFFIXES = ["Силы", "Мудрости", "Скорости", "Защиты", "Разрушения", "Исцеления", "Тьмы", "Света"]
        
        logger.info(f"ContentGenerator инициализирован с seed: {self.seed}")
    
    def generate_guid(self) -> str:
        """Генерирует GUID в 16-ричной системе"""
        # Создаем UUID и конвертируем в hex
        guid = uuid.uuid4()
        return guid.hex.upper()
    
    def generate_item(self, item_type: ItemType = None) -> GeneratedItem:
        """Генерирует предмет"""
        if item_type is None:
            item_type = self.rng.choice(list(ItemType))
        
        # Генерируем имя
        base_name = self.rng.choice(self.ITEM_NAMES)
        prefix = self.rng.choice(self.PREFIXES) if self.rng.random() < 0.3 else ""
        suffix = self.rng.choice(self.SUFFIXES) if self.rng.random() < 0.3 else ""
        
        name_parts = [part for part in [prefix, base_name, suffix] if part]
        name = " ".join(name_parts)
        
        # Генерируем характеристики
        stats = self._generate_item_stats(item_type)
        
        # Генерируем описание
        description = self._generate_item_description(name, item_type, stats)
        
        # Генерируем позицию в мире
        position = (
            self.rng.randint(-5000, 5000),
            self.rng.randint(-5000, 5000),
            0
        )
        
        return GeneratedItem(
            guid=self.generate_guid(),
            name=name,
            item_type=item_type,
            rarity=self._determine_rarity(stats),
            stats=stats,
            description=description,
            position=position
        )
    
    def generate_enemy(self, enemy_type: EnemyType = None) -> GeneratedEnemy:
        """Генерирует врага"""
        if enemy_type is None:
            enemy_type = self.rng.choice(list(EnemyType))
        
        # Генерируем имя
        base_name = self.rng.choice(self.ENEMY_NAMES)
        prefix = self.rng.choice(self.PREFIXES) if self.rng.random() < 0.2 else ""
        
        name_parts = [part for part in [prefix, base_name] if part]
        name = " ".join(name_parts)
        
        # Генерируем уровень
        level = self.rng.randint(1, 20)
        
        # Генерируем характеристики
        stats = self._generate_enemy_stats(enemy_type, level)
        
        # Генерируем способности
        abilities = self._generate_enemy_abilities(enemy_type, level)
        
        # Генерируем позицию в мире
        position = (
            self.rng.randint(-5000, 5000),
            self.rng.randint(-5000, 5000),
            0
        )
        
        return GeneratedEnemy(
            guid=self.generate_guid(),
            name=name,
            enemy_type=enemy_type,
                level=level,
                stats=stats,
                abilities=abilities,
            position=position
        )
    
    def generate_skill(self, skill_type: SkillType = None) -> GeneratedSkill:
        """Генерирует навык"""
        if skill_type is None:
            skill_type = self.rng.choice(list(SkillType))
        
        # Генерируем имя
        base_name = self.rng.choice(self.SKILL_NAMES)
        prefix = self.rng.choice(self.PREFIXES) if self.rng.random() < 0.3 else ""
        
        name_parts = [part for part in [prefix, base_name] if part]
        name = " ".join(name_parts)
        
        # Генерируем уровень
        level = self.rng.randint(1, 10)
        
        # Генерируем эффекты
        effects = self._generate_skill_effects(skill_type, level)
        
        # Генерируем описание
        description = self._generate_skill_description(name, skill_type, effects)
        
        return GeneratedSkill(
            guid=self.generate_guid(),
            name=name,
            skill_type=skill_type,
            level=level,
            effects=effects,
            description=description
        )
    
    def generate_gene(self, gene_type: GeneType = None) -> GeneratedGene:
        """Генерирует ген"""
        if gene_type is None:
            gene_type = self.rng.choice(list(GeneType))
        
        # Генерируем имя
        base_name = self.rng.choice(self.GENE_NAMES)
        prefix = self.rng.choice(self.PREFIXES) if self.rng.random() < 0.3 else ""
        
        name_parts = [part for part in [prefix, base_name] if part]
        name = " ".join(name_parts)
        
        # Генерируем уровень
        level = self.rng.randint(1, 5)
        
        # Генерируем эффекты
        effects = self._generate_gene_effects(gene_type, level)
        
        # Генерируем описание
        description = self._generate_gene_description(name, gene_type, effects)
        
        return GeneratedGene(
            guid=self.generate_guid(),
            name=name,
            gene_type=gene_type,
            level=level,
            effects=effects,
            description=description
        )
    
    def generate_accessory(self) -> GeneratedAccessory:
        """Генерирует аксессуар"""
        # Генерируем имя
        base_name = self.rng.choice(self.ACCESSORY_NAMES)
        prefix = self.rng.choice(self.PREFIXES) if self.rng.random() < 0.3 else ""
        suffix = self.rng.choice(self.SUFFIXES) if self.rng.random() < 0.3 else ""
        
        name_parts = [part for part in [prefix, base_name, suffix] if part]
        name = " ".join(name_parts)
        
        # Определяем слот
        slots = ["head", "neck", "shoulders", "chest", "waist", "legs", "feet", "hands", "finger", "trinket"]
        slot = self.rng.choice(slots)
        
        # Генерируем характеристики
        stats = self._generate_accessory_stats(slot)
        
        # Генерируем эффекты
        effects = self._generate_accessory_effects(slot)
        
        # Генерируем позицию в мире
        position = (
            self.rng.randint(-5000, 5000),
            self.rng.randint(-5000, 5000),
            0
        )
        
        return GeneratedAccessory(
            guid=self.generate_guid(),
            name=name,
            slot=slot,
            stats=stats,
            effects=effects,
            position=position
        )
    
    def initialize_session_content(self, session_uuid: str, level: int = 1) -> Dict[str, List[Dict]]:
        """Инициализирует контент для новой сессии"""
        logger.info(f"Инициализация контента для сессии {session_uuid}, уровень {level}")
        
        # Устанавливаем seed на основе session_uuid
        session_seed = int(hashlib.md5(session_uuid.encode()).hexdigest()[:8], 16)
        self.rng.seed(session_seed)
        
        # Генерируем количество объектов в зависимости от уровня
        item_count = max(5, level * 2)
        enemy_count = max(3, level * 3)
        skill_count = max(2, level)
        gene_count = max(1, level // 2)
        accessory_count = max(2, level)
        
        # Генерируем предметы
        items = []
        for _ in range(item_count):
            item = self.generate_item()
            items.append({
                "guid": item.guid,
                "name": item.name,
                "type": item.item_type.value,
                "rarity": item.rarity,
                "stats": item.stats,
                "description": item.description,
                "position": item.position
            })
        
        # Генерируем врагов
        enemies = []
        for _ in range(enemy_count):
            enemy = self.generate_enemy()
            enemies.append({
                "guid": enemy.guid,
                "name": enemy.name,
                "type": enemy.enemy_type.value,
                "level": enemy.level,
                "stats": enemy.stats,
                "abilities": enemy.abilities,
                "position": enemy.position
            })
        
        # Генерируем навыки
        skills = []
        for _ in range(skill_count):
            skill = self.generate_skill()
            skills.append({
                "guid": skill.guid,
                "name": skill.name,
                "type": skill.skill_type.value,
                "level": skill.level,
                "effects": skill.effects,
                "description": skill.description
            })
        
        # Генерируем гены
        genes = []
        for _ in range(gene_count):
            gene = self.generate_gene()
            genes.append({
                "guid": gene.guid,
                "name": gene.name,
                "type": gene.gene_type.value,
                "level": gene.level,
                "effects": gene.effects,
                "description": gene.description
            })
        
        # Генерируем аксессуары
        accessories = []
        for _ in range(accessory_count):
            accessory = self.generate_accessory()
            accessories.append({
                "guid": accessory.guid,
                "name": accessory.name,
                "slot": accessory.slot,
                "stats": accessory.stats,
                "effects": accessory.effects,
                "position": accessory.position
            })
        
        return {
            "items": items,
            "enemies": enemies,
            "skills": skills,
            "genes": genes,
            "accessories": accessories
        }
    
    def _generate_item_stats(self, item_type: ItemType) -> Dict[str, Any]:
        """Генерирует характеристики предмета"""
        stats = {}
        
        if item_type == ItemType.WEAPON:
            stats["damage"] = self.rng.randint(10, 100)
            stats["speed"] = self.rng.uniform(0.5, 2.0)
            stats["durability"] = self.rng.randint(50, 200)
        elif item_type == ItemType.ARMOR:
            stats["defense"] = self.rng.randint(5, 50)
            stats["weight"] = self.rng.uniform(1.0, 10.0)
            stats["durability"] = self.rng.randint(50, 200)
        elif item_type == ItemType.CONSUMABLE:
            stats["healing"] = self.rng.randint(20, 100)
            stats["duration"] = self.rng.randint(10, 60)
        elif item_type == ItemType.MATERIAL:
            stats["quality"] = self.rng.randint(1, 10)
            stats["quantity"] = self.rng.randint(1, 10)
        elif item_type == ItemType.ARTIFACT:
            stats["power"] = self.rng.randint(50, 200)
            stats["charges"] = self.rng.randint(1, 5)
        
        return stats
    
    def _generate_enemy_stats(self, enemy_type: EnemyType, level: int) -> Dict[str, Any]:
        """Генерирует характеристики врага"""
        base_health = 50 + (level * 20)
        base_damage = 10 + (level * 5)
        
        stats = {
            "health": base_health,
            "max_health": base_health,
            "damage": base_damage,
            "speed": self.rng.uniform(0.5, 2.0),
            "defense": self.rng.randint(0, level * 3)
        }
        
        if enemy_type == EnemyType.PREDATOR:
            stats["damage"] *= 1.5
            stats["speed"] *= 1.2
        elif enemy_type == EnemyType.BOSS:
            stats["health"] *= 3
            stats["damage"] *= 2
            stats["defense"] *= 2
        
        return stats
    
    def _generate_enemy_abilities(self, enemy_type: EnemyType, level: int) -> List[str]:
        """Генерирует способности врага"""
        abilities = []
        
        if enemy_type == EnemyType.PREDATOR:
            abilities.extend(["Охота", "Преследование"])
        elif enemy_type == EnemyType.BOSS:
            abilities.extend(["Особая атака", "Защита", "Регенерация"])
        elif enemy_type == EnemyType.NEUTRAL:
            abilities.append("Защита территории")
        
        if level > 5:
            abilities.append("Улучшенная атака")
        if level > 10:
            abilities.append("Особая способность")
        
        return abilities
    
    def _generate_skill_effects(self, skill_type: SkillType, level: int) -> Dict[str, Any]:
        """Генерирует эффекты навыка"""
        effects = {}
        
        if skill_type == SkillType.COMBAT:
            effects["damage_bonus"] = level * 5
            effects["critical_chance"] = level * 2
        elif skill_type == SkillType.UTILITY:
            effects["movement_speed"] = level * 0.1
            effects["resource_efficiency"] = level * 0.05
        elif skill_type == SkillType.PASSIVE:
            effects["stat_bonus"] = level * 3
        elif skill_type == SkillType.ACTIVE:
            effects["cooldown"] = max(1, 10 - level)
            effects["power"] = level * 10
        
        return effects
    
    def _generate_gene_effects(self, gene_type: GeneType, level: int) -> Dict[str, Any]:
        """Генерирует эффекты гена"""
        effects = {}
        
        if gene_type == GeneType.STRENGTH:
            effects["physical_power"] = level * 5
            effects["carry_capacity"] = level * 10
        elif gene_type == GeneType.AGILITY:
            effects["movement_speed"] = level * 0.1
            effects["dodge_chance"] = level * 2
        elif gene_type == GeneType.INTELLIGENCE:
            effects["magic_power"] = level * 5
            effects["learning_speed"] = level * 0.1
        elif gene_type == GeneType.ENDURANCE:
            effects["health_bonus"] = level * 20
            effects["stamina_bonus"] = level * 10
        elif gene_type == GeneType.EVOLUTION:
            effects["evolution_rate"] = level * 0.1
            effects["mutation_chance"] = level * 0.05
        
        return effects
    
    def _generate_accessory_stats(self, slot: str) -> Dict[str, Any]:
        """Генерирует характеристики аксессуара"""
        stats = {}
        
        if slot in ["head", "chest"]:
            stats["defense"] = self.rng.randint(5, 20)
        elif slot in ["hands", "feet"]:
            stats["speed"] = self.rng.uniform(0.1, 0.5)
        elif slot in ["finger", "trinket"]:
            stats["magic_power"] = self.rng.randint(5, 25)
        
        stats["durability"] = self.rng.randint(50, 150)
        return stats
    
    def _generate_accessory_effects(self, slot: str) -> List[str]:
        """Генерирует эффекты аксессуара"""
        effects = []
        
        if slot == "head":
            effects.append("Улучшенное зрение")
        elif slot == "neck":
            effects.append("Защита от магии")
        elif slot == "finger":
            effects.append("Увеличение маны")
        
        if self.rng.random() < 0.3:
            effects.append("Особый эффект")
        
        return effects
    
    def _determine_rarity(self, stats: Dict[str, Any]) -> str:
        """Определяет редкость предмета на основе характеристик"""
        total_power = sum(stats.values()) if isinstance(stats, dict) else 0
        
        if total_power > 150:
            return "legendary"
        elif total_power > 100:
            return "epic"
        elif total_power > 50:
            return "rare"
        else:
            return "common"
    
    def _generate_item_description(self, name: str, item_type: ItemType, stats: Dict[str, Any]) -> str:
        """Генерирует описание предмета"""
        descriptions = {
            ItemType.WEAPON: f"Мощное оружие {name.lower()} с характеристиками: {', '.join([f'{k}: {v}' for k, v in stats.items()])}",
            ItemType.ARMOR: f"Надежная броня {name.lower()} обеспечивает защиту: {', '.join([f'{k}: {v}' for k, v in stats.items()])}",
            ItemType.CONSUMABLE: f"Полезный предмет {name.lower()} для восстановления: {', '.join([f'{k}: {v}' for k, v in stats.items()])}",
            ItemType.MATERIAL: f"Ценный материал {name.lower()} для крафтинга: {', '.join([f'{k}: {v}' for k, v in stats.items()])}",
            ItemType.ARTIFACT: f"Древний артефакт {name.lower()} с магическими свойствами: {', '.join([f'{k}: {v}' for k, v in stats.items()])}"
        }
        return descriptions.get(item_type, f"Таинственный предмет {name.lower()}")
    
    def _generate_skill_description(self, name: str, skill_type: SkillType, effects: Dict[str, Any]) -> str:
        """Генерирует описание навыка"""
        return f"Навык {name.lower()} типа {skill_type.value} с эффектами: {', '.join([f'{k}: {v}' for k, v in effects.items()])}"
    
    def _generate_gene_description(self, name: str, gene_type: GeneType, effects: Dict[str, Any]) -> str:
        """Генерирует описание гена"""
        return f"Ген {name.lower()} типа {gene_type.value} с эффектами: {', '.join([f'{k}: {v}' for k, v in effects.items()])}"
    
    def generate_world(self, biome: str = "forest", size: str = "medium", difficulty: float = 1.0) -> Dict[str, Any]:
        """Генерирует игровой мир"""
        world_size_map = {
            "small": (1000, 1000),
            "medium": (5000, 5000),
            "large": (10000, 10000),
            "massive": (20000, 20000)
        }
        
        width, height = world_size_map.get(size, (5000, 5000))
        
        return {
            "biome": biome,
            "size": size,
            "width": width,
            "height": height,
            "difficulty": difficulty,
            "seed": self.seed
        }
