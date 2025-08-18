#!/usr/bin/env python3
"""
Расширенная система оружия для эволюционной адаптации.
Включает различные типы оружия, их характеристики и эффективность против врагов.
"""

import random
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WeaponType(Enum):
    """Типы оружия"""
    SWORD = "sword"
    AXE = "axe"
    SPEAR = "spear"
    BOW = "bow"
    CROSSBOW = "crossbow"
    STAFF = "staff"
    WAND = "wand"
    DAGGER = "dagger"
    HAMMER = "hammer"
    SCYTHE = "scythe"
    GUN = "gun"
    LASER = "laser"
    PLASMA = "plasma"
    NANOBOT = "nanobot"
    QUANTUM = "quantum"


class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    MAGIC = "magic"
    RADIATION = "radiation"
    COSMIC = "cosmic"
    VOID = "void"
    CHAOS = "chaos"


class WeaponRarity(Enum):
    """Редкость оружия"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    DIVINE = "divine"


@dataclass
class WeaponStats:
    """Характеристики оружия"""
    base_damage: float
    damage_variance: float  # ±% от базового урона
    attack_speed: float     # Ударов в секунду
    range: float           # Дальность атаки
    accuracy: float        # Точность (0.0 - 1.0)
    critical_chance: float # Шанс критического удара
    critical_multiplier: float
    durability: float      # Прочность
    max_durability: float
    
    def get_damage(self) -> float:
        """Получение случайного урона"""
        variance = self.base_damage * (self.damage_variance / 100.0)
        return self.base_damage + random.uniform(-variance, variance)
    
    def get_effective_damage(self, target_resistance: float = 0.0) -> float:
        """Получение эффективного урона с учётом сопротивления"""
        base_damage = self.get_damage()
        resistance_multiplier = max(0.1, 1.0 - target_resistance)
        return base_damage * resistance_multiplier
    
    def is_critical_hit(self) -> bool:
        """Проверка критического удара"""
        return random.random() < self.critical_chance
    
    def take_durability_damage(self, amount: float = 1.0):
        """Получение урона по прочности"""
        self.durability = max(0.0, self.durability - amount)
    
    def can_use(self) -> bool:
        """Проверка возможности использования"""
        return self.durability > 0.0


@dataclass
class WeaponEnhancement:
    """Улучшение оружия"""
    enhancement_type: str
    value: float
    description: str
    cost: int
    level: int = 1
    
    def upgrade(self) -> bool:
        """Улучшение уровня"""
        if self.level < 10:  # Максимум 10 уровней
            self.level += 1
            self.value *= 1.2  # +20% к значению
            return True
        return False


@dataclass
class AdvancedWeapon:
    """Продвинутое оружие с характеристиками и улучшениями"""
    weapon_id: str
    name: str
    weapon_type: WeaponType
    damage_type: DamageType
    rarity: WeaponRarity
    stats: WeaponStats
    enhancements: List[WeaponEnhancement] = field(default_factory=list)
    
    # Эффективность против типов врагов
    enemy_effectiveness: Dict[str, float] = field(default_factory=dict)
    
    # Требования для использования
    level_requirement: int = 1
    strength_requirement: int = 0
    dexterity_requirement: int = 0
    intelligence_requirement: int = 0
    
    # Специальные способности
    special_abilities: List[str] = field(default_factory=list)
    
    def __init__(self, weapon_id: str, name: str, weapon_type: WeaponType, 
                 damage_type: DamageType, rarity: WeaponRarity, stats: WeaponStats):
        self.weapon_id = weapon_id
        self.name = name
        self.weapon_type = weapon_type
        self.damage_type = damage_type
        self.rarity = rarity
        self.stats = stats
        
        # Инициализация базовой эффективности
        self._init_base_effectiveness()
    
    def _init_base_effectiveness(self):
        """Инициализация базовой эффективности против врагов"""
        # Базовые множители эффективности
        base_multipliers = {
            "goblin": 1.2,      # Гоблины слабы к физическому урону
            "orc": 0.8,         # Орки устойчивы к физическому урону
            "troll": 0.6,       # Тролли очень устойчивы к физическому урону
            "dragon": 0.4,      # Драконы устойчивы ко всему
            "undead": 1.5,      # Нежить слаба к огню
            "demon": 0.7,       # Демоны устойчивы к огню
            "angel": 0.9,       # Ангелы нейтральны
            "beast": 1.1,       # Звери слабы к физическому урону
            "construct": 0.5,   # Конструкты устойчивы к физическому урону
            "elemental": 0.3    # Элементали устойчивы к своему типу урона
        }
        
        # Модификация на основе типа урона
        for enemy_type, base_mult in base_multipliers.items():
            if self.damage_type == DamageType.FIRE and enemy_type == "undead":
                self.enemy_effectiveness[enemy_type] = base_mult * 2.0
            elif self.damage_type == DamageType.ICE and enemy_type == "dragon":
                self.enemy_effectiveness[enemy_type] = base_mult * 1.5
            elif self.damage_type == DamageType.LIGHTNING and enemy_type == "construct":
                self.enemy_effectiveness[enemy_type] = base_mult * 1.8
            else:
                self.enemy_effectiveness[enemy_type] = base_mult
    
    def get_effectiveness_against(self, enemy_type: str) -> float:
        """Получение эффективности против конкретного врага"""
        return self.enemy_effectiveness.get(enemy_type, 1.0)
    
    def attack(self, target_resistance: float = 0.0, enemy_type: str = "unknown") -> Dict[str, Any]:
        """Выполнение атаки"""
        if not self.can_use():
            return {"damage": 0, "critical": False, "effective": False, "message": "Оружие сломано"}
        
        # Расчёт урона
        base_damage = self.stats.get_effective_damage(target_resistance)
        
        # Применение эффективности против врага
        effectiveness = self.get_effectiveness_against(enemy_type)
        final_damage = base_damage * effectiveness
        
        # Проверка критического удара
        is_critical = self.stats.is_critical_hit()
        if is_critical:
            final_damage *= self.stats.critical_multiplier
        
        # Урон по прочности
        self.stats.take_durability_damage(0.1)
        
        return {
            "damage": final_damage,
            "critical": is_critical,
            "effective": effectiveness > 1.0,
            "enemy_type": enemy_type,
            "weapon_type": self.weapon_type.value,
            "damage_type": self.damage_type.value
        }
    
    def add_enhancement(self, enhancement: WeaponEnhancement):
        """Добавление улучшения"""
        self.enhancements.append(enhancement)
        self._apply_enhancement(enhancement)
    
    def _apply_enhancement(self, enhancement: WeaponEnhancement):
        """Применение улучшения к характеристикам"""
        if enhancement.enhancement_type == "damage_boost":
            self.stats.base_damage *= (1.0 + enhancement.value)
        elif enhancement.enhancement_type == "speed_boost":
            self.stats.attack_speed *= (1.0 + enhancement.value)
        elif enhancement.enhancement_type == "critical_boost":
            self.stats.critical_chance = min(1.0, self.stats.critical_chance + enhancement.value)
        elif enhancement.enhancement_type == "durability_boost":
            self.stats.max_durability *= (1.0 + enhancement.value)
            self.stats.durability = self.stats.max_durability
    
    def can_equip(self, entity_stats: Dict[str, int]) -> bool:
        """Проверка возможности экипировки"""
        return (entity_stats.get("level", 0) >= self.level_requirement and
                entity_stats.get("strength", 0) >= self.strength_requirement and
                entity_stats.get("dexterity", 0) >= self.dexterity_requirement and
                entity_stats.get("intelligence", 0) >= self.intelligence_requirement)
    
    def get_weapon_info(self) -> Dict[str, Any]:
        """Получение информации об оружии"""
        return {
            "id": self.weapon_id,
            "name": self.name,
            "type": self.weapon_type.value,
            "damage_type": self.damage_type.value,
            "rarity": self.rarity.value,
            "stats": {
                "base_damage": self.stats.base_damage,
                "attack_speed": self.stats.attack_speed,
                "range": self.stats.range,
                "accuracy": self.stats.accuracy,
                "critical_chance": self.stats.critical_chance,
                "durability": f"{self.stats.durability:.1f}/{self.stats.max_durability:.1f}"
            },
            "enhancements": [enh.__dict__ for enh in self.enhancements],
            "requirements": {
                "level": self.level_requirement,
                "strength": self.strength_requirement,
                "dexterity": self.dexterity_requirement,
                "intelligence": self.intelligence_requirement
            }
        }


class WeaponFactory:
    """Фабрика создания оружия"""
    
    @staticmethod
    def create_weapon(weapon_type: WeaponType, rarity: WeaponRarity = WeaponRarity.COMMON) -> AdvancedWeapon:
        """Создание оружия заданного типа и редкости"""
        
        # Базовые характеристики для каждого типа оружия
        weapon_templates = {
            WeaponType.SWORD: {
                "damage": 25, "speed": 1.5, "range": 1.5, "accuracy": 0.9,
                "critical": 0.1, "durability": 100
            },
            WeaponType.AXE: {
                "damage": 35, "speed": 1.0, "range": 1.2, "accuracy": 0.8,
                "critical": 0.15, "durability": 80
            },
            WeaponType.SPEAR: {
                "damage": 30, "speed": 1.8, "range": 3.0, "accuracy": 0.95,
                "critical": 0.08, "durability": 90
            },
            WeaponType.BOW: {
                "damage": 20, "speed": 2.0, "range": 15.0, "accuracy": 0.85,
                "critical": 0.12, "durability": 70
            },
            WeaponType.STAFF: {
                "damage": 15, "speed": 1.2, "range": 2.5, "accuracy": 0.9,
                "critical": 0.05, "durability": 60
            },
            WeaponType.DAGGER: {
                "damage": 18, "speed": 3.0, "range": 1.0, "accuracy": 0.95,
                "critical": 0.25, "durability": 50
            }
        }
        
        template = weapon_templates.get(weapon_type, weapon_templates[WeaponType.SWORD])
        
        # Модификация характеристик на основе редкости
        rarity_multipliers = {
            WeaponRarity.COMMON: 1.0,
            WeaponRarity.UNCOMMON: 1.2,
            WeaponRarity.RARE: 1.5,
            WeaponRarity.EPIC: 2.0,
            WeaponRarity.LEGENDARY: 3.0,
            WeaponRarity.MYTHIC: 4.0,
            WeaponRarity.DIVINE: 5.0
        }
        
        multiplier = rarity_multipliers[rarity]
        
        # Создание характеристик
        stats = WeaponStats(
            base_damage=template["damage"] * multiplier,
            damage_variance=10.0,
            attack_speed=template["speed"],
            range=template["range"],
            accuracy=min(1.0, template["accuracy"] * (1.0 + (multiplier - 1.0) * 0.1)),
            critical_chance=min(0.5, template["critical"] * (1.0 + (multiplier - 1.0) * 0.2)),
            critical_multiplier=2.0,
            durability=template["durability"] * multiplier,
            max_durability=template["durability"] * multiplier
        )
        
        # Определение типа урона
        damage_type = WeaponFactory._get_damage_type_for_weapon(weapon_type)
        
        # Создание оружия
        weapon = AdvancedWeapon(
            weapon_id=f"{weapon_type.value}_{rarity.value}_{random.randint(1000, 9999)}",
            name=f"{rarity.value.title()} {weapon_type.value.title()}",
            weapon_type=weapon_type,
            damage_type=damage_type,
            rarity=rarity,
            stats=stats
        )
        
        # Добавление улучшений для редкого оружия
        if rarity in [WeaponRarity.RARE, WeaponRarity.EPIC, WeaponRarity.LEGENDARY]:
            WeaponFactory._add_random_enhancements(weapon, rarity)
        
        return weapon
    
    @staticmethod
    def _get_damage_type_for_weapon(weapon_type: WeaponType) -> DamageType:
        """Определение типа урона для оружия"""
        damage_mapping = {
            WeaponType.SWORD: DamageType.PHYSICAL,
            WeaponType.AXE: DamageType.PHYSICAL,
            WeaponType.SPEAR: DamageType.PHYSICAL,
            WeaponType.BOW: DamageType.PHYSICAL,
            WeaponType.STAFF: DamageType.MAGIC,
            WeaponType.WAND: DamageType.MAGIC,
            WeaponType.DAGGER: DamageType.PHYSICAL,
            WeaponType.HAMMER: DamageType.PHYSICAL,
            WeaponType.SCYTHE: DamageType.PHYSICAL,
            WeaponType.GUN: DamageType.PHYSICAL,
            WeaponType.LASER: DamageType.RADIATION,
            WeaponType.PLASMA: DamageType.FIRE,
            WeaponType.NANOBOT: DamageType.POISON,
            WeaponType.QUANTUM: DamageType.COSMIC
        }
        return damage_mapping.get(weapon_type, DamageType.PHYSICAL)
    
    @staticmethod
    def _add_random_enhancements(weapon: AdvancedWeapon, rarity: WeaponRarity):
        """Добавление случайных улучшений"""
        enhancement_types = [
            ("damage_boost", 0.2, "Увеличение урона"),
            ("speed_boost", 0.15, "Увеличение скорости атаки"),
            ("critical_boost", 0.1, "Увеличение шанса критического удара"),
            ("durability_boost", 0.3, "Увеличение прочности")
        ]
        
        num_enhancements = {
            WeaponRarity.RARE: 1,
            WeaponRarity.EPIC: 2,
            WeaponRarity.LEGENDARY: 3
        }.get(rarity, 1)
        
        for _ in range(num_enhancements):
            enh_type, enh_value, enh_desc = random.choice(enhancement_types)
            enhancement = WeaponEnhancement(
                enhancement_type=enh_type,
                value=enh_value,
                description=enh_desc,
                cost=100 * (rarity.value + 1)
            )
            weapon.add_enhancement(enhancement)


class WeaponManager:
    """Менеджер оружия для управления коллекцией"""
    
    def __init__(self):
        self.weapons: Dict[str, AdvancedWeapon] = {}
        self.weapon_types: Dict[WeaponType, List[str]] = {wt: [] for wt in WeaponType}
        self.rarity_distribution: Dict[WeaponRarity, int] = {r: 0 for r in WeaponRarity}
    
    def add_weapon(self, weapon: AdvancedWeapon):
        """Добавление оружия в коллекцию"""
        self.weapons[weapon.weapon_id] = weapon
        self.weapon_types[weapon.weapon_type].append(weapon.weapon_id)
        self.rarity_distribution[weapon.rarity] += 1
        
        logger.info(f"Оружие {weapon.name} добавлено в коллекцию")
    
    def remove_weapon(self, weapon_id: str) -> Optional[AdvancedWeapon]:
        """Удаление оружия из коллекции"""
        if weapon_id in self.weapons:
            weapon = self.weapons.pop(weapon_id)
            self.weapon_types[weapon.weapon_type].remove(weapon_id)
            self.rarity_distribution[weapon.rarity] -= 1
            return weapon
        return None
    
    def get_weapon(self, weapon_id: str) -> Optional[AdvancedWeapon]:
        """Получение оружия по ID"""
        return self.weapons.get(weapon_id)
    
    def get_weapons_by_type(self, weapon_type: WeaponType) -> List[AdvancedWeapon]:
        """Получение оружия по типу"""
        weapon_ids = self.weapon_types.get(weapon_type, [])
        return [self.weapons[wid] for wid in weapon_ids if wid in self.weapons]
    
    def get_weapons_by_rarity(self, rarity: WeaponRarity) -> List[AdvancedWeapon]:
        """Получение оружия по редкости"""
        return [w for w in self.weapons.values() if w.rarity == rarity]
    
    def get_best_weapon_against(self, enemy_type: str) -> Optional[AdvancedWeapon]:
        """Получение лучшего оружия против конкретного врага"""
        best_weapon = None
        best_score = 0.0
        
        for weapon in self.weapons.values():
            effectiveness = weapon.get_effectiveness_against(enemy_type)
            if effectiveness > best_score:
                best_score = effectiveness
                best_weapon = weapon
        
        return best_weapon
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Получение статистики коллекции"""
        return {
            "total_weapons": len(self.weapons),
            "weapons_by_type": {wt.value: len(weapon_ids) for wt, weapon_ids in self.weapon_types.items()},
            "weapons_by_rarity": {r.value: count for r, count in self.rarity_distribution.items()},
            "average_damage": sum(w.stats.base_damage for w in self.weapons.values()) / len(self.weapons) if self.weapons else 0
        }
