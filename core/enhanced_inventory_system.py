#!/usr/bin/env python3
"""
Расширенная система инвентаря и предметов.
Вдохновлено Hades, Risk of Rain 2, Binding of Isaac, Enter the Gungeon.
Включает синергии предметов, эволюцию снаряжения и адаптивные эффекты.
"""

import random
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

from .generational_memory_system import GenerationalMemorySystem, MemoryType

logger = logging.getLogger(__name__)


class ItemType(Enum):
    """Типы предметов"""
    # Оружие (Hades)
    WEAPON = "weapon"
    WEAPON_ASPECT = "weapon_aspect"
    WEAPON_UPGRADE = "weapon_upgrade"
    
    # Пассивные предметы (Risk of Rain 2)
    PASSIVE_COMMON = "passive_common"
    PASSIVE_UNCOMMON = "passive_uncommon"
    PASSIVE_LEGENDARY = "passive_legendary"
    PASSIVE_VOID = "passive_void"
    
    # Активные предметы (Binding of Isaac)
    ACTIVE_SPACEBAR = "active_spacebar"
    ACTIVE_PILL = "active_pill"
    ACTIVE_CARD = "active_card"
    ACTIVE_TRINKET = "active_trinket"
    
    # Боеприпасы (Enter the Gungeon)
    AMMUNITION = "ammunition"
    SPECIAL_AMMO = "special_ammo"
    
    # Эволюционные предметы
    EVOLUTION_CATALYST = "evolution_catalyst"
    GENETIC_MODIFIER = "genetic_modifier"
    MEMORY_CRYSTAL = "memory_crystal"
    
    # Божественные дары (Hades)
    DIVINE_BOON = "divine_boon"
    OLYMPIAN_GIFT = "olympian_gift"
    
    # Проклятые предметы
    CURSED_ITEM = "cursed_item"
    CORRUPTED_ARTIFACT = "corrupted_artifact"


class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"           # Обычный (белый)
    UNCOMMON = "uncommon"       # Необычный (зелёный)
    RARE = "rare"               # Редкий (синий)
    EPIC = "epic"               # Эпический (фиолетовый)
    LEGENDARY = "legendary"     # Легендарный (оранжевый)
    MYTHIC = "mythic"           # Мифический (красный)
    VOID = "void"               # Пустотный (чёрный)
    DIVINE = "divine"           # Божественный (золотой)
    CORRUPTED = "corrupted"     # Искажённый (тёмно-красный)
    TRANSCENDENT = "transcendent" # Трансцендентный (радужный)


class ItemTag(Enum):
    """Теги предметов для синергий"""
    DAMAGE = "damage"
    DEFENSE = "defense"
    SPEED = "speed"
    HEALING = "healing"
    ELEMENTAL = "elemental"
    UTILITY = "utility"
    CURSED = "cursed"
    DIVINE = "divine"
    EVOLUTION = "evolution"
    MEMORY = "memory"
    TEMPORAL = "temporal"
    DIMENSIONAL = "dimensional"


@dataclass
class ItemEffect:
    """Эффект предмета"""
    effect_type: str
    value: float
    duration: float
    stacks: bool
    conditions: List[str] = field(default_factory=list)
    
    def apply_effect(self, target: Any, context: Dict[str, Any]) -> bool:
        """Применение эффекта"""
        # Здесь будет логика применения эффекта
        return True


@dataclass 
class ItemSynergy:
    """Синергия между предметами"""
    id: str
    name: str
    description: str
    required_items: List[str]
    required_tags: List[str]
    bonus_effects: List[ItemEffect]
    evolution_unlock: Optional[str] = None


@dataclass
class Item:
    """Предмет"""
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    tags: List[ItemTag]
    
    # Эффекты
    base_effects: List[ItemEffect] = field(default_factory=list)
    evolved_effects: List[ItemEffect] = field(default_factory=list)
    
    # Эволюция
    evolution_level: int = 0
    max_evolution_level: int = 3
    evolution_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Синергии
    synergy_partners: List[str] = field(default_factory=list)
    
    # Метаданные
    stack_count: int = 1
    max_stacks: int = 1
    acquisition_time: float = 0.0
    usage_count: int = 0
    
    def can_evolve(self, context: Dict[str, Any]) -> bool:
        """Проверка возможности эволюции"""
        if self.evolution_level >= self.max_evolution_level:
            return False
        
        for requirement, value in self.evolution_requirements.items():
            if context.get(requirement, 0) < value:
                return False
        
        return True
    
    def evolve(self, context: Dict[str, Any]) -> bool:
        """Эволюция предмета"""
        if not self.can_evolve(context):
            return False
        
        self.evolution_level += 1
        
        # Добавляем эволюционные эффекты
        if self.evolved_effects:
            self.base_effects.extend(self.evolved_effects)
        
        logger.info(f"Предмет {self.name} эволюционировал до уровня {self.evolution_level}")
        return True
    
    def get_effective_value(self, effect_type: str) -> float:
        """Получение эффективного значения эффекта"""
        total_value = 0.0
        
        for effect in self.base_effects:
            if effect.effect_type == effect_type:
                multiplier = 1.0 + (self.evolution_level * 0.2)  # 20% за уровень эволюции
                total_value += effect.value * multiplier
        
        return total_value


class EnhancedInventorySystem:
    """Расширенная система инвентаря"""
    
    def __init__(self, memory_system: GenerationalMemorySystem):
        self.memory_system = memory_system
        
        # Инвентарь
        self.inventory: Dict[str, Item] = {}
        self.equipped_items: Dict[str, str] = {}  # slot -> item_id
        
        # Синергии
        self.item_synergies: Dict[str, ItemSynergy] = {}
        self.active_synergies: List[str] = []
        
        # Система эволюции предметов
        self.evolution_system = ItemEvolutionSystem()
        
        # Система синергий (Risk of Rain 2 style)
        self.synergy_system = ItemSynergySystem()
        
        # Система божественных даров (Hades style)
        self.divine_boon_system = DivineBoonSystem()
        
        # Инициализация
        self._init_base_items()
        self._init_item_synergies()
        
        logger.info("Расширенная система инвентаря инициализирована")
    
    def add_item(self, item_id: str, context: Dict[str, Any] = None) -> bool:
        """Добавление предмета в инвентарь"""
        if context is None:
            context = {}
        
        # Создание предмета из шаблона
        item = self._create_item_from_template(item_id, context)
        if not item:
            logger.warning(f"Не удалось создать предмет: {item_id}")
            return False
        
        # Проверка на стакование
        existing_item = self._find_stackable_item(item)
        if existing_item and existing_item.stack_count < existing_item.max_stacks:
            existing_item.stack_count += 1
            logger.info(f"Предмет {item.name} добавлен в стак (стаков: {existing_item.stack_count})")
        else:
            # Добавление нового предмета
            item.acquisition_time = time.time()
            self.inventory[item.id] = item
            logger.info(f"Добавлен предмет: {item.name} ({item.rarity.value})")
        
        # Проверка синергий
        self._check_new_synergies(item)
        
        # Запись в память
        self._record_item_acquisition(item, context)
        
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Удаление предмета из инвентаря"""
        if item_id not in self.inventory:
            return False
        
        item = self.inventory[item_id]
        
        if item.stack_count > quantity:
            item.stack_count -= quantity
            logger.info(f"Удалено {quantity} из стака {item.name} (осталось: {item.stack_count})")
        else:
            del self.inventory[item_id]
            # Удаление из экипированных предметов
            for slot, equipped_id in list(self.equipped_items.items()):
                if equipped_id == item_id:
                    del self.equipped_items[slot]
            logger.info(f"Предмет {item.name} полностью удалён из инвентаря")
            
            # Обновление синергий
            self._update_synergies()
        
        return True
    
    def use_item(self, item_id: str, target: Optional[str] = None,
                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Использование предмета"""
        if item_id not in self.inventory:
            return {"success": False, "reason": "Item not found"}
        
        item = self.inventory[item_id]
        
        # Применение эффектов предмета
        result = self._apply_item_effects(item, target, context or {})
        
        # Увеличение счётчика использования
        item.usage_count += 1
        
        # Запись использования в память
        self._record_item_usage(item, result, context or {})
        
        return result
    
    def evolve_item(self, item_id: str, context: Dict[str, Any] = None) -> bool:
        """Эволюция предмета"""
        if item_id not in self.inventory:
            return False
        
        item = self.inventory[item_id]
        
        if item.evolve(context or {}):
            # Проверка новых синергий после эволюции
            self._check_new_synergies(item)
            
            # Запись эволюции в память
            self._record_item_evolution(item, context or {})
            
            return True
        
        return False
    
    def get_inventory_bonuses(self) -> Dict[str, float]:
        """Получение бонусов от всех предметов в инвентаре"""
        bonuses = {}
        
        for item in self.inventory.values():
            for effect in item.base_effects:
                if effect.effect_type not in bonuses:
                    bonuses[effect.effect_type] = 0.0
                
                # Учитываем стаки и эволюцию
                effective_value = item.get_effective_value(effect.effect_type)
                bonuses[effect.effect_type] += effective_value * item.stack_count
        
        # Добавляем бонусы от синергий
        synergy_bonuses = self.synergy_system.get_synergy_bonuses(self.active_synergies)
        for bonus_type, value in synergy_bonuses.items():
            if bonus_type not in bonuses:
                bonuses[bonus_type] = 0.0
            bonuses[bonus_type] += value
        
        return bonuses
    
    def suggest_item_combinations(self) -> List[Dict[str, Any]]:
        """Предложение комбинаций предметов"""
        suggestions = []
        
        # Поиск возможных синергий
        for synergy in self.item_synergies.values():
            if synergy.id in self.active_synergies:
                continue
            
            owned_items = set(self.inventory.keys())
            required_items = set(synergy.required_items)
            
            missing_items = required_items - owned_items
            
            if len(missing_items) <= 2:  # Близко к синергии
                suggestions.append({
                    "type": "synergy",
                    "synergy_name": synergy.name,
                    "description": synergy.description,
                    "missing_items": list(missing_items),
                    "priority": len(synergy.bonus_effects)
                })
        
        # Предложения по эволюции
        for item in self.inventory.values():
            if item.can_evolve({}):
                suggestions.append({
                    "type": "evolution",
                    "item_name": item.name,
                    "description": f"Эволюционировать {item.name} до уровня {item.evolution_level + 1}",
                    "requirements": item.evolution_requirements,
                    "priority": item.evolution_level + 1
                })
        
        # Сортировка по приоритету
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        return suggestions[:5]  # Топ-5 предложений
    
    def _init_base_items(self):
        """Инициализация базовых предметов"""
        self.item_templates = {
            # Оружие (Hades style)
            "stygius_sword": {
                "name": "Меч Стигий",
                "description": "Надёжный меч подземного мира",
                "type": ItemType.WEAPON,
                "rarity": ItemRarity.COMMON,
                "tags": [ItemTag.DAMAGE],
                "effects": [
                    ItemEffect("weapon_damage", 25.0, -1, False),
                    ItemEffect("attack_speed", 1.0, -1, False)
                ],
                "max_stacks": 1,
                "evolution_requirements": {"kills": 50, "weapon_mastery": 10}
            },
            
            # Пассивные предметы (Risk of Rain 2 style)
            "crowbar": {
                "name": "Лом",
                "description": "+75% урона врагам с полным здоровьем",
                "type": ItemType.PASSIVE_COMMON,
                "rarity": ItemRarity.COMMON,
                "tags": [ItemTag.DAMAGE],
                "effects": [
                    ItemEffect("full_health_damage", 0.75, -1, True, ["target_full_health"])
                ],
                "max_stacks": 10
            },
            
            "ceremonial_dagger": {
                "name": "Церемониальный кинжал",
                "description": "Убийство врага призывает кинжалы",
                "type": ItemType.PASSIVE_UNCOMMON,
                "rarity": ItemRarity.UNCOMMON,
                "tags": [ItemTag.DAMAGE, ItemTag.UTILITY],
                "effects": [
                    ItemEffect("on_kill_daggers", 3.0, -1, True, ["enemy_killed"])
                ],
                "max_stacks": 5
            },
            
            # Активные предметы (Binding of Isaac style)
            "d6_dice": {
                "name": "Кубик D6",
                "description": "Перебрасывает все пассивные предметы в комнате",
                "type": ItemType.ACTIVE_SPACEBAR,
                "rarity": ItemRarity.RARE,
                "tags": [ItemTag.UTILITY],
                "effects": [
                    ItemEffect("reroll_items", 1.0, 0, False)
                ],
                "max_stacks": 1
            },
            
            # Божественные дары (Hades style)
            "zeus_lightning": {
                "name": "Молния Зевса",
                "description": "Атаки поражают молнией ближайших врагов",
                "type": ItemType.DIVINE_BOON,
                "rarity": ItemRarity.DIVINE,
                "tags": [ItemTag.DAMAGE, ItemTag.ELEMENTAL],
                "effects": [
                    ItemEffect("lightning_chain", 40.0, -1, False)
                ],
                "max_stacks": 1,
                "synergy_partners": ["poseidon_wave", "ares_doom"]
            },
            
            # Эволюционные предметы
            "evolution_crystal": {
                "name": "Кристалл эволюции",
                "description": "Ускоряет эволюционные процессы на 50%",
                "type": ItemType.EVOLUTION_CATALYST,
                "rarity": ItemRarity.EPIC,
                "tags": [ItemTag.EVOLUTION],
                "effects": [
                    ItemEffect("evolution_speed", 0.5, -1, True)
                ],
                "max_stacks": 3
            },
            
            # Проклятые предметы
            "cursed_eye": {
                "name": "Проклятый глаз",
                "description": "+2 урона, но телепортирует в случайную комнату при получении урона",
                "type": ItemType.CURSED_ITEM,
                "rarity": ItemRarity.CORRUPTED,
                "tags": [ItemTag.DAMAGE, ItemTag.CURSED],
                "effects": [
                    ItemEffect("damage_bonus", 2.0, -1, False),
                    ItemEffect("random_teleport", 1.0, -1, False, ["take_damage"])
                ],
                "max_stacks": 1
            }
        }
    
    def _init_item_synergies(self):
        """Инициализация синергий предметов"""
        self.item_synergies = {
            "divine_duo_zeus_poseidon": ItemSynergy(
                id="divine_duo_zeus_poseidon",
                name="Морская буря",
                description="Молнии Зевса создают волны Посейдона",
                required_items=["zeus_lightning", "poseidon_wave"],
                required_tags=[],
                bonus_effects=[
                    ItemEffect("storm_combo", 100.0, -1, False)
                ]
            ),
            
            "evolution_mastery": ItemSynergy(
                id="evolution_mastery",
                name="Мастерство эволюции",
                description="Несколько эволюционных предметов дают экспоненциальный бонус",
                required_items=[],
                required_tags=["evolution", "evolution", "evolution"],
                bonus_effects=[
                    ItemEffect("evolution_mastery", 2.0, -1, False)
                ]
            ),
            
            "cursed_power": ItemSynergy(
                id="cursed_power",
                name="Проклятая мощь",
                description="Проклятые предметы дают бонус к урону за каждое проклятие",
                required_items=[],
                required_tags=["cursed", "cursed"],
                bonus_effects=[
                    ItemEffect("curse_damage_per_curse", 0.25, -1, True)
                ]
            )
        }
    
    def _create_item_from_template(self, item_id: str, context: Dict[str, Any]) -> Optional[Item]:
        """Создание предмета из шаблона"""
        if item_id not in self.item_templates:
            return None
        
        template = self.item_templates[item_id]
        
        item = Item(
            id=str(uuid.uuid4()),
            name=template["name"],
            description=template["description"],
            item_type=template["type"],
            rarity=template["rarity"],
            tags=template["tags"],
            base_effects=template["effects"].copy(),
            max_stacks=template.get("max_stacks", 1),
            evolution_requirements=template.get("evolution_requirements", {}),
            synergy_partners=template.get("synergy_partners", [])
        )
        
        return item
    
    def _find_stackable_item(self, new_item: Item) -> Optional[Item]:
        """Поиск предмета для стакования"""
        for item in self.inventory.values():
            if (item.name == new_item.name and 
                item.rarity == new_item.rarity and
                item.max_stacks > 1):
                return item
        return None
    
    def _check_new_synergies(self, new_item: Item):
        """Проверка новых синергий"""
        for synergy in self.item_synergies.values():
            if synergy.id in self.active_synergies:
                continue
            
            if self._check_synergy_requirements(synergy):
                self.active_synergies.append(synergy.id)
                logger.info(f"Активирована синергия: {synergy.name}")
    
    def _check_synergy_requirements(self, synergy: ItemSynergy) -> bool:
        """Проверка требований синергии"""
        # Проверка требуемых предметов
        owned_items = set(item.name.lower().replace(" ", "_") for item in self.inventory.values())
        required_items = set(synergy.required_items)
        
        if not required_items.issubset(owned_items):
            return False
        
        # Проверка требуемых тегов
        owned_tags = []
        for item in self.inventory.values():
            owned_tags.extend([tag.value for tag in item.tags])
        
        for required_tag in synergy.required_tags:
            if owned_tags.count(required_tag) < synergy.required_tags.count(required_tag):
                return False
        
        return True
    
    def _update_synergies(self):
        """Обновление активных синергий"""
        self.active_synergies = []
        
        for synergy in self.item_synergies.values():
            if self._check_synergy_requirements(synergy):
                self.active_synergies.append(synergy.id)
    
    def _apply_item_effects(self, item: Item, target: Optional[str], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Применение эффектов предмета"""
        results = []
        
        for effect in item.base_effects:
            # Проверка условий
            if effect.conditions:
                if not self._check_effect_conditions(effect.conditions, context):
                    continue
            
            # Применение эффекта
            if effect.apply_effect(target, context):
                results.append({
                    "effect_type": effect.effect_type,
                    "value": effect.value,
                    "applied": True
                })
        
        return {
            "success": True,
            "item_name": item.name,
            "effects_applied": results,
            "usage_count": item.usage_count + 1
        }
    
    def _check_effect_conditions(self, conditions: List[str], context: Dict[str, Any]) -> bool:
        """Проверка условий эффекта"""
        for condition in conditions:
            if condition == "target_full_health":
                if context.get("target_health_percent", 0.0) < 1.0:
                    return False
            elif condition == "enemy_killed":
                if not context.get("enemy_killed", False):
                    return False
            elif condition == "take_damage":
                if not context.get("damage_taken", False):
                    return False
        
        return True
    
    def _record_item_acquisition(self, item: Item, context: Dict[str, Any]):
        """Запись получения предмета в память"""
        try:
            memory_content = {
                "item_name": item.name,
                "item_type": item.item_type.value,
                "item_rarity": item.rarity.value,
                "context": context,
                "timestamp": time.time()
            }
            
            self.memory_system.add_memory(
                memory_type=MemoryType.ITEM_USAGE,
                content=memory_content,
                intensity=0.5,
                emotional_impact=0.3
            )
            
        except Exception as e:
            logger.error(f"Ошибка записи получения предмета: {e}")
    
    def _record_item_usage(self, item: Item, result: Dict[str, Any], context: Dict[str, Any]):
        """Запись использования предмета в память"""
        try:
            memory_content = {
                "item_name": item.name,
                "usage_result": result,
                "context": context,
                "timestamp": time.time()
            }
            
            self.memory_system.add_memory(
                memory_type=MemoryType.ITEM_USAGE,
                content=memory_content,
                intensity=0.4,
                emotional_impact=0.2
            )
            
        except Exception as e:
            logger.error(f"Ошибка записи использования предмета: {e}")
    
    def _record_item_evolution(self, item: Item, context: Dict[str, Any]):
        """Запись эволюции предмета в память"""
        try:
            memory_content = {
                "item_name": item.name,
                "evolution_level": item.evolution_level,
                "context": context,
                "timestamp": time.time()
            }
            
            self.memory_system.add_memory(
                memory_type=MemoryType.EVOLUTIONARY_SUCCESS,
                content=memory_content,
                intensity=0.7,
                emotional_impact=0.4
            )
            
        except Exception as e:
            logger.error(f"Ошибка записи эволюции предмета: {e}")


class ItemEvolutionSystem:
    """Система эволюции предметов"""
    
    def __init__(self):
        self.evolution_paths: Dict[str, List[str]] = {}
        self.evolution_requirements: Dict[str, Dict[str, Any]] = {}
    
    def register_evolution_path(self, item_name: str, evolution_stages: List[str]):
        """Регистрация пути эволюции"""
        self.evolution_paths[item_name] = evolution_stages


class ItemSynergySystem:
    """Система синергий предметов"""
    
    def __init__(self):
        self.synergy_bonuses: Dict[str, Dict[str, float]] = {}
    
    def get_synergy_bonuses(self, active_synergies: List[str]) -> Dict[str, float]:
        """Получение бонусов от синергий"""
        bonuses = {}
        
        for synergy_id in active_synergies:
            if synergy_id in self.synergy_bonuses:
                for bonus_type, value in self.synergy_bonuses[synergy_id].items():
                    if bonus_type not in bonuses:
                        bonuses[bonus_type] = 0.0
                    bonuses[bonus_type] += value
        
        return bonuses


class DivineBoonSystem:
    """Система божественных даров (Hades)"""
    
    def __init__(self):
        self.olympian_gods = [
            "zeus", "poseidon", "ares", "artemis", "athena", 
            "dionysus", "demeter", "aphrodite", "hermes"
        ]
        self.god_favor_levels: Dict[str, int] = {god: 0 for god in self.olympian_gods}
    
    def offer_divine_boon(self, god: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Предложение божественного дара"""
        favor_level = self.god_favor_levels.get(god, 0)
        
        # Генерация дара на основе уровня благосклонности
        boon_power = 1.0 + (favor_level * 0.2)
        
        return {
            "god": god,
            "boon_power": boon_power,
            "special_effects": self._get_god_special_effects(god)
        }
    
    def _get_god_special_effects(self, god: str) -> List[str]:
        """Получение специальных эффектов бога"""
        god_effects = {
            "zeus": ["lightning_chain", "static_discharge"],
            "poseidon": ["tidal_wave", "water_knockback"],
            "ares": ["doom_curse", "blade_rift"],
            "artemis": ["critical_strike", "seeking_arrow"],
            "athena": ["deflect_attacks", "divine_protection"]
        }
        
        return god_effects.get(god, [])
