"""
Централизованный менеджер данных игры.
Управляет загрузкой и доступом к данным предметов, врагов, эффектов и других игровых объектов.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
import threading

from core.database_manager import database_manager

logger = logging.getLogger(__name__)


@dataclass
class ItemData:
    """Данные предмета"""

    id: str
    name: str
    description: str
    type: str
    slot: Optional[str]
    rarity: str
    level_requirement: int
    base_damage: float = 0.0
    attack_speed: float = 1.0
    damage_type: Optional[str] = None
    element: Optional[str] = None
    element_damage: float = 0.0
    defense: float = 0.0
    weight: float = 0.0
    durability: int = 100
    max_durability: int = 100
    cost: int = 0
    attack_range: float = 0.0
    effects: List[str] = field(default_factory=list)
    modifiers: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    resist_mod: Dict[str, float] = field(default_factory=dict)
    weakness_mod: Dict[str, float] = field(default_factory=dict)
    hex_id: Optional[str] = None


@dataclass
class EntityData:
    """Данные сущности"""

    id: str
    name: str
    description: str
    type: str
    level: int
    experience: int
    base_health: float
    base_mana: float
    base_damage: float
    base_armor: float
    base_speed: float
    attack_range: float
    ai_type: Optional[str] = None
    behavior_pattern: Optional[str] = None
    difficulty_rating: float = 1.0
    loot_table: List[str] = field(default_factory=list)
    hex_id: Optional[str] = None


@dataclass
class EffectData:
    """Данные эффекта"""

    id: str
    name: str
    description: str
    type: str
    category: str
    duration: float = 10.0
    tick_rate: float = 1.0
    magnitude: float = 1.0
    target_type: Optional[str] = None
    max_stacks: int = 1
    stackable: bool = False
    conditions: Dict[str, Any] = field(default_factory=dict)
    modifiers: Dict[str, Any] = field(default_factory=dict)
    visual_effects: Dict[str, Any] = field(default_factory=dict)
    sound_effects: Dict[str, Any] = field(default_factory=dict)
    hex_id: Optional[str] = None


@dataclass
class AbilityData:
    """Данные способности"""

    id: str
    name: str
    description: str
    type: str
    category: str
    level_requirement: int = 1
    mana_cost: int = 0
    cooldown: float = 0.0
    duration: float = 0.0
    range: float = 0.0
    area_of_effect: float = 0.0
    base_damage: float = 0.0
    damage_type: Optional[str] = None
    element: Optional[str] = None
    effects: List[str] = field(default_factory=list)
    modifiers: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    hex_id: Optional[str] = None


@dataclass
class AttributeData:
    """Данные атрибута"""

    id: str
    name: str
    description: str
    base_value: float = 0.0
    max_value: float = 100.0
    growth_rate: float = 1.0
    category: Optional[str] = None
    effects: List[str] = field(default_factory=list)
    hex_id: Optional[str] = None


class DataManager:
    """Централизованный менеджер данных игры"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()
        
        # Кэш данных
        self._items_cache: Dict[str, ItemData] = {}
        self._entities_cache: Dict[str, EntityData] = {}
        self._effects_cache: Dict[str, EffectData] = {}
        self._abilities_cache: Dict[str, AbilityData] = {}
        self._attributes_cache: Dict[str, AttributeData] = {}
        
        # Инициализация
        self._load_all_data_from_db()

    def _load_all_data_from_db(self):
        """Загружает все данные из базы данных"""
        try:
            logger.info("Загрузка данных из БД...")
            
            # Загружаем данные из БД через DatabaseManager
            self._load_items_from_db()
            self._load_entities_from_db()
            self._load_effects_from_db()
            self._load_abilities_from_db()
            self._load_attributes_from_db()
            
            logger.info("Все данные загружены из БД")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных из БД: {e}")

    def _load_items_from_db(self):
        """Загружает предметы из БД"""
        try:
            items_data = database_manager.get_items()
            self._items_cache.clear()
            
            for item_id, item_data in items_data.items():
                self._items_cache[item_id] = ItemData(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    type=item_data["type"],
                    slot=item_data["slot"],
                    rarity=item_data["rarity"],
                    level_requirement=item_data["level_requirement"],
                    base_damage=item_data["base_damage"] or 0.0,
                    attack_speed=item_data["attack_speed"] or 1.0,
                    damage_type=item_data["damage_type"],
                    element=item_data["element"],
                    element_damage=item_data["element_damage"] or 0.0,
                    defense=item_data["defense"] or 0.0,
                    weight=item_data["weight"] or 0.0,
                    durability=item_data["durability"] or 100,
                    max_durability=item_data["max_durability"] or 100,
                    cost=item_data["cost"] or 0,
                    attack_range=item_data["range"] or 0.0,
                    effects=item_data["effects"] or [],
                    modifiers=item_data["modifiers"] or {},
                    tags=item_data["tags"] or [],
                    resist_mod=item_data["resist_mod"] or {},
                    weakness_mod=item_data["weakness_mod"] or {},
                    hex_id=item_data["hex_id"]
                )
            
            logger.info(f"Загружено {len(self._items_cache)} предметов")
        except Exception as e:
            logger.error(f"Ошибка загрузки предметов: {e}")

    def _load_entities_from_db(self):
        """Загружает сущности из БД"""
        try:
            entities_data = database_manager.get_entities()
            self._entities_cache.clear()
            
            for entity_id, entity_data in entities_data.items():
                self._entities_cache[entity_id] = EntityData(
                    id=entity_data["id"],
                    name=entity_data["name"],
                    description=entity_data["description"],
                    type=entity_data["type"],
                    level=entity_data["level"],
                    experience=entity_data["experience"],
                    base_health=entity_data["base_health"] or 100.0,
                    base_mana=entity_data["base_mana"] or 50.0,
                    base_damage=entity_data["base_damage"] or 10.0,
                    base_armor=entity_data["base_armor"] or 0.0,
                    base_speed=entity_data["base_speed"] or 2.0,
                    attack_range=entity_data["attack_range"] or 50.0,
                    ai_type=entity_data["ai_type"],
                    behavior_pattern=entity_data["behavior_pattern"],
                    difficulty_rating=entity_data["difficulty_rating"] or 1.0,
                    loot_table=entity_data["loot_table"] or [],
                    hex_id=entity_data["hex_id"]
                )
            
            logger.info(f"Загружено {len(self._entities_cache)} сущностей")
        except Exception as e:
            logger.error(f"Ошибка загрузки сущностей: {e}")

    def _load_effects_from_db(self):
        """Загружает эффекты из БД"""
        try:
            effects_data = database_manager.get_effects()
            self._effects_cache.clear()
            
            for effect_id, effect_data in effects_data.items():
                self._effects_cache[effect_id] = EffectData(
                    id=effect_data["id"],
                    name=effect_data["name"],
                    description=effect_data["description"],
                    type=effect_data["type"],
                    category=effect_data["category"],
                    duration=effect_data["duration"] or 10.0,
                    tick_rate=effect_data["tick_interval"] or 1.0,
                    magnitude=1.0,  # Базовое значение
                    target_type=None,  # Базовое значение
                    max_stacks=effect_data["max_stacks"] or 1,
                    stackable=effect_data["stackable"] or False,
                    conditions={},  # Базовое значение
                    modifiers=effect_data["modifiers"] or {},
                    visual_effects={},  # Базовое значение
                    sound_effects={},  # Базовое значение
                    hex_id=effect_data["hex_id"]
                )
            
            logger.info(f"Загружено {len(self._effects_cache)} эффектов")
        except Exception as e:
            logger.error(f"Ошибка загрузки эффектов: {e}")

    def _load_abilities_from_db(self):
        """Загружает способности из БД"""
        try:
            # Пока используем пустой кэш, так как таблица abilities еще не создана
            self._abilities_cache.clear()
            logger.info("Кэш способностей очищен (таблица abilities не создана)")
        except Exception as e:
            logger.error(f"Ошибка загрузки способностей: {e}")

    def _load_attributes_from_db(self):
        """Загружает атрибуты из БД"""
        try:
            attributes_data = database_manager.get_attributes()
            self._attributes_cache.clear()
            
            for attr_id, attr_data in attributes_data.items():
                self._attributes_cache[attr_id] = AttributeData(
                    id=attr_data["id"],
                    name=attr_data["name"],
                    description=attr_data["description"],
                    base_value=attr_data["base_value"] or 0.0,
                    max_value=attr_data["max_value"] or 100.0,
                    growth_rate=attr_data["growth_rate"] or 1.0,
                    category=attr_data["category"],
                    effects=attr_data["effects"] or [],
                    hex_id=attr_data["hex_id"]
                )
            
            logger.info(f"Загружено {len(self._attributes_cache)} атрибутов")
        except Exception as e:
            logger.error(f"Ошибка загрузки атрибутов: {e}")

    def get_item(self, item_id: str) -> Optional[ItemData]:
        """Получает предмет по ID"""
        with self._lock:
            return self._items_cache.get(item_id)

    def get_items_by_type(self, item_type: str) -> List[ItemData]:
        """Получает предметы определенного типа"""
        with self._lock:
            return [item for item in self._items_cache.values() if item.type == item_type]

    def get_items_by_rarity(self, rarity: str) -> List[ItemData]:
        """Получает предметы определенной редкости"""
        with self._lock:
            return [item for item in self._items_cache.values() if item.rarity == rarity]

    def get_entity(self, entity_id: str) -> Optional[EntityData]:
        """Получает сущность по ID"""
        with self._lock:
            return self._entities_cache.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[EntityData]:
        """Получает сущности определенного типа"""
        with self._lock:
            return [entity for entity in self._entities_cache.values() if entity.type == entity_type]

    def get_enemies(self) -> List[EntityData]:
        """Получает всех врагов"""
        with self._lock:
            return [entity for entity in self._entities_cache.values() if entity.type == "enemy"]

    def get_effect(self, effect_id: str) -> Optional[EffectData]:
        """Получает эффект по ID"""
        with self._lock:
            return self._effects_cache.get(effect_id)

    def get_effects_by_type(self, effect_type: str) -> List[EffectData]:
        """Получает эффекты определенного типа"""
        with self._lock:
            return [effect for effect in self._effects_cache.values() if effect.type == effect_type]

    def get_ability(self, ability_id: str) -> Optional[AbilityData]:
        """Получает способность по ID"""
        with self._lock:
            return self._abilities_cache.get(ability_id)

    def get_abilities_by_type(self, ability_type: str) -> List[AbilityData]:
        """Получает способности определенного типа"""
        with self._lock:
            return [ability for ability in self._abilities_cache.values() if ability.type == ability_type]

    def get_attribute(self, attribute_id: str) -> Optional[AttributeData]:
        """Получает атрибут по ID"""
        with self._lock:
            return self._attributes_cache.get(attribute_id)

    def get_all_items(self) -> List[ItemData]:
        """Получает все предметы"""
        with self._lock:
            return list(self._items_cache.values())

    def get_all_entities(self) -> List[EntityData]:
        """Получает все сущности"""
        with self._lock:
            return list(self._entities_cache.values())

    def get_all_effects(self) -> List[EffectData]:
        """Получает все эффекты"""
        with self._lock:
            return list(self._effects_cache.values())

    def get_all_abilities(self) -> List[AbilityData]:
        """Получает все способности"""
        with self._lock:
            return list(self._abilities_cache.values())

    def get_all_attributes(self) -> List[AttributeData]:
        """Получает все атрибуты"""
        with self._lock:
            return list(self._attributes_cache.values())

    def add_item(self, item_data: ItemData) -> bool:
        """Добавляет новый предмет"""
        try:
            with self._lock:
                # Добавляем в БД
                item_dict = asdict(item_data)
                if database_manager.add_item(item_dict):
                    # Обновляем кэш
                    self._items_cache[item_data.id] = item_data
                    logger.info(f"Предмет {item_data.name} добавлен")
                    return True
                return False
        except Exception as e:
            logger.error(f"Ошибка добавления предмета: {e}")
            return False

    def add_entity(self, entity_data: EntityData) -> bool:
        """Добавляет новую сущность"""
        try:
            with self._lock:
                # Добавляем в БД
                entity_dict = asdict(entity_data)
                # TODO: Добавить метод add_entity в DatabaseManager
                # if database_manager.add_entity(entity_dict):
                #     # Обновляем кэш
                #     self._entities_cache[entity_data.id] = entity_data
                #     logger.info(f"Сущность {entity_data.name} добавлена")
                #     return True
                # return False
                logger.warning("Метод add_entity не реализован в DatabaseManager")
                return False
        except Exception as e:
            logger.error(f"Ошибка добавления сущности: {e}")
            return False

    def reload_data(self):
        """Перезагружает все данные из БД"""
        with self._lock:
            self._load_all_data_from_db()

    def search_items(self, query: str, limit: int = 10) -> List[ItemData]:
        """Ищет предметы по запросу"""
        try:
            items_data = database_manager.search_items(query, limit)
            items = []
            
            for item_data in items_data:
                items.append(ItemData(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    type=item_data["type"],
                    slot=item_data["slot"],
                    rarity=item_data["rarity"],
                    level_requirement=item_data["level_requirement"],
                    base_damage=item_data["base_damage"] or 0.0,
                    attack_speed=item_data["attack_speed"] or 1.0,
                    damage_type=item_data["damage_type"],
                    element=item_data["element"],
                    element_damage=item_data["element_damage"] or 0.0,
                    defense=item_data["defense"] or 0.0,
                    weight=item_data["weight"] or 0.0,
                    durability=item_data["durability"] or 100,
                    max_durability=item_data["max_durability"] or 100,
                    cost=item_data["cost"] or 0,
                    attack_range=item_data["range"] or 0.0,
                    effects=item_data["effects"] or [],
                    modifiers=item_data["modifiers"] or {},
                    tags=item_data["tags"] or [],
                    resist_mod=item_data["resist_mod"] or {},
                    weakness_mod=item_data["weakness_mod"] or {},
                    hex_id=item_data["hex_id"]
                ))
            
            return items
        except Exception as e:
            logger.error(f"Ошибка поиска предметов: {e}")
            return []

    def get_cache_stats(self) -> Dict[str, int]:
        """Получает статистику кэша"""
        with self._lock:
            return {
                "items": len(self._items_cache),
                "entities": len(self._entities_cache),
                "effects": len(self._effects_cache),
                "abilities": len(self._abilities_cache),
                "attributes": len(self._attributes_cache)
            }


# Глобальный экземпляр менеджера данных
data_manager = DataManager()
