"""
Система кортежей данных для игры
Вместо парсинга по имени используются структурированные данные
"""
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
from pathlib import Path


class DataType(Enum):
    """Типы данных"""
    ATTRIBUTE = "attribute"
    EFFECT = "effect"
    ITEM = "item"
    ENTITY = "entity"
    SKILL = "skill"
    SETTING = "setting"


@dataclass
class AttributeData:
    """Кортеж данных атрибута"""
    id: str
    name: str
    description: str
    base_value: float
    max_value: float
    growth_rate: float
    category: str
    effects: Dict[str, float] = field(default_factory=dict)
    hex_id: Optional[str] = None
    
    def to_tuple(self) -> Tuple[str, str, str, float, float, float, str, Dict[str, float]]:
        """Преобразовать в кортеж для быстрого доступа"""
        return (self.id, self.name, self.description, self.base_value, 
                self.max_value, self.growth_rate, self.category, self.effects)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttributeData':
        """Создать из словаря"""
        return cls(**data)


@dataclass
class EffectData:
    """Кортеж данных эффекта"""
    id: str
    name: str
    description: str
    type: str
    category: str
    tags: List[str]
    modifiers: Dict[str, Any]
    max_stacks: int = 1
    duration: Optional[float] = None
    interval: Optional[float] = None
    tick_interval: Optional[float] = None
    stackable: bool = False
    hex_id: Optional[str] = None
    
    def to_tuple(self) -> Tuple[str, str, str, str, str, List[str], Dict[str, Any], int, Optional[float], Optional[float], Optional[float], bool]:
        """Преобразовать в кортеж для быстрого доступа"""
        return (self.id, self.name, self.description, self.type, self.category, self.tags, 
                self.modifiers, self.max_stacks, self.duration, self.interval, self.tick_interval, self.stackable)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EffectData':
        """Создать из словаря"""
        return cls(**data)


@dataclass
class ItemData:
    """Кортеж данных предмета"""
    id: str
    name: str
    description: str
    type: str
    slot: Optional[str]
    rarity: str
    level_requirement: int
    base_damage: Optional[float] = None
    attack_speed: Optional[float] = None
    defense: Optional[float] = None
    damage_type: Optional[str] = None
    element: Optional[str] = None
    element_damage: Optional[float] = None
    range: Optional[float] = None
    cost: Optional[int] = None
    mana_cost: Optional[int] = None
    critical_chance: Optional[float] = None
    weight: Optional[float] = None
    block_chance: Optional[float] = None
    heal_amount: Optional[float] = None
    heal_percent: Optional[float] = None
    mana_amount: Optional[float] = None
    mana_percent: Optional[float] = None
    duration: Optional[float] = None
    cooldown: Optional[float] = None
    durability: Optional[int] = None
    max_durability: Optional[int] = None
    effects: List[str] = field(default_factory=list)
    modifiers: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    resist_mod: Dict[str, float] = field(default_factory=dict)
    weakness_mod: Dict[str, float] = field(default_factory=dict)
    elemental_resistance: Dict[str, float] = field(default_factory=dict)
    hex_id: Optional[str] = None
    
    def to_tuple(self) -> Tuple[str, str, str, str, Optional[str], str, int, 
                                Optional[float], Optional[float], Optional[float], 
                                Optional[str], Optional[str], Optional[float], Optional[float], Optional[int],
                                Optional[int], Optional[float], Optional[float], Optional[float], Optional[float],
                                Optional[float], Optional[float], Optional[float], Optional[float], Optional[float],
                                Optional[int], Optional[int],
                                List[str], Dict[str, Any], List[str], Dict[str, float], Dict[str, float], Dict[str, float]]:
        """Преобразовать в кортеж для быстрого доступа"""
        return (self.id, self.name, self.description, self.type, self.slot,
                self.rarity, self.level_requirement, self.base_damage,
                self.attack_speed, self.defense, self.damage_type, self.element,
                self.element_damage, self.range, self.cost, self.mana_cost,
                self.critical_chance, self.weight, self.block_chance, self.heal_amount,
                self.heal_percent, self.mana_amount, self.mana_percent, self.duration,
                self.cooldown, self.durability,
                self.max_durability, self.effects, self.modifiers, self.tags,
                self.resist_mod, self.weakness_mod, self.elemental_resistance)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemData':
        """Создать из словаря"""
        return cls(**data)


@dataclass
class EntityData:
    """Кортеж данных сущности"""
    id: str
    name: str
    description: str
    type: str
    level: int
    experience: int = 0
    experience_to_next: int = 100
    attributes: Dict[str, float] = field(default_factory=dict)
    combat_stats: Dict[str, float] = field(default_factory=dict)
    equipment_slots: List[str] = field(default_factory=list)
    inventory_size: int = 0
    skills: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    enemy_type: Optional[str] = None
    experience_reward: Optional[int] = None
    ai_behavior: Optional[str] = None
    loot_table: Optional[List[str]] = None
    phases: Optional[List[Dict[str, Any]]] = None
    hex_id: Optional[str] = None
    
    def to_tuple(self) -> Tuple[str, str, str, str, int, int, int, 
                                Dict[str, float], Dict[str, float], List[str], 
                                int, List[str], List[str], Optional[str], 
                                Optional[int], Optional[str], Optional[List[str]], 
                                Optional[List[Dict[str, Any]]]]:
        """Преобразовать в кортеж для быстрого доступа"""
        return (self.id, self.name, self.description, self.type, self.level,
                self.experience, self.experience_to_next, self.attributes,
                self.combat_stats, self.equipment_slots, self.inventory_size,
                self.skills, self.tags, self.enemy_type, self.experience_reward,
                self.ai_behavior, self.loot_table, self.phases)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityData':
        """Создать из словаря"""
        return cls(**data)


class DataManager:
    """Менеджер данных для загрузки и управления кортежами данных"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.attributes: Dict[str, AttributeData] = {}
        self.effects: Dict[str, EffectData] = {}
        self.items: Dict[str, ItemData] = {}
        self.entities: Dict[str, EntityData] = {}
        self.settings: Dict[str, Any] = {}
        
        # SQLite база данных для быстрого поиска
        self.db_path = self.data_path / "game_data.db"
        self.init_database()
        
        # Загружаем все данные
        self.load_all_data()
    
    def init_database(self):
        """Инициализация SQLite базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Удаляем существующие таблицы для пересоздания схемы
        cursor.execute("DROP TABLE IF EXISTS attributes")
        cursor.execute("DROP TABLE IF EXISTS effects")
        cursor.execute("DROP TABLE IF EXISTS items")
        cursor.execute("DROP TABLE IF EXISTS entities")
        
        # Создаем таблицы
        cursor.execute('''
            CREATE TABLE attributes (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                base_value REAL,
                max_value REAL,
                growth_rate REAL,
                category TEXT,
                effects TEXT,
                hex_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE effects (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                type TEXT,
                category TEXT,
                tags TEXT,
                modifiers TEXT,
                max_stacks INTEGER,
                duration REAL,
                interval REAL,
                tick_interval REAL,
                stackable INTEGER,
                effect_type TEXT,
                hex_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE items (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                type TEXT,
                slot TEXT,
                rarity TEXT,
                level_requirement INTEGER,
                base_damage REAL,
                attack_speed REAL,
                defense REAL,
                damage_type TEXT,
                element TEXT,
                element_damage REAL,
                range REAL,
                cost INTEGER,
                mana_cost INTEGER,
                critical_chance REAL,
                weight REAL,
                block_chance REAL,
                heal_amount REAL,
                heal_percent REAL,
                mana_amount REAL,
                mana_percent REAL,
                duration REAL,
                cooldown REAL,
                durability INTEGER,
                max_durability INTEGER,
                effects TEXT,
                modifiers TEXT,
                tags TEXT,
                resist_mod TEXT,
                weakness_mod TEXT,
                elemental_resistance TEXT,
                hex_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE entities (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                type TEXT,
                level INTEGER,
                experience INTEGER,
                experience_to_next INTEGER,
                attributes TEXT,
                combat_stats TEXT,
                equipment_slots TEXT,
                inventory_size INTEGER,
                skills TEXT,
                tags TEXT,
                enemy_type TEXT,
                experience_reward INTEGER,
                ai_behavior TEXT,
                loot_table TEXT,
                phases TEXT,
                hex_id TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_all_data(self):
        """Загрузить все данные из JSON файлов"""
        self.load_attributes()
        self.load_effects()
        self.load_items()
        self.load_entities()
        self.load_settings()
        self.update_database()
    
    def load_attributes(self):
        """Загрузить атрибуты"""
        file_path = self.data_path / "attributes.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for attr_id, attr_data in data.get("attributes", {}).items():
                    self.attributes[attr_id] = AttributeData.from_dict(attr_data)
    
    def load_effects(self):
        """Загрузить эффекты"""
        file_path = self.data_path / "effects.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for effect_id, effect_data in data.get("effects", {}).items():
                    self.effects[effect_id] = EffectData.from_dict(effect_data)
    
    def load_items(self):
        """Загрузить предметы"""
        file_path = self.data_path / "items.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item_id, item_data in data.get("items", {}).items():
                    self.items[item_id] = ItemData.from_dict(item_data)
    
    def load_entities(self):
        """Загрузить сущности"""
        file_path = self.data_path / "entities.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entity_id, entity_data in data.get("entities", {}).items():
                    self.entities[entity_id] = EntityData.from_dict(entity_data)
    
    def load_settings(self):
        """Загрузить настройки игры"""
        file_path = self.data_path / "game_settings.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
    
    def update_database(self):
        """Обновить SQLite базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Очищаем таблицы
        cursor.execute("DELETE FROM attributes")
        cursor.execute("DELETE FROM effects")
        cursor.execute("DELETE FROM items")
        cursor.execute("DELETE FROM entities")
        
        # Добавляем атрибуты
        for attr in self.attributes.values():
            cursor.execute('''
                INSERT INTO attributes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (attr.id, attr.name, attr.description, attr.base_value,
                  attr.max_value, attr.growth_rate, attr.category, json.dumps(attr.effects), attr.hex_id))
        
        # Добавляем эффекты
        for effect in self.effects.values():
            cursor.execute('''
                INSERT INTO effects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (effect.id, effect.name, effect.description, effect.type, effect.category,
                  json.dumps(effect.tags), json.dumps(effect.modifiers), effect.max_stacks,
                  effect.duration, effect.interval, effect.tick_interval, effect.stackable, effect.type, effect.hex_id))
        
        # Добавляем предметы
        for item in self.items.values():
            cursor.execute('''
                INSERT INTO items (
                    id, name, description, type, slot, rarity, level_requirement,
                    base_damage, attack_speed, defense, damage_type, element,
                    element_damage, range, cost, mana_cost, critical_chance,
                    weight, block_chance, heal_amount, heal_percent, mana_amount,
                    mana_percent, duration, cooldown, durability, max_durability,
                    effects, modifiers, tags, resist_mod, weakness_mod, elemental_resistance, hex_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item.id, item.name, item.description, item.type, item.slot,
                  item.rarity, item.level_requirement, item.base_damage,
                  item.attack_speed, item.defense, item.damage_type, item.element,
                  item.element_damage, item.range, item.cost, item.mana_cost,
                  item.critical_chance, item.weight, item.block_chance, item.heal_amount,
                  item.heal_percent, item.mana_amount, item.mana_percent, item.duration,
                  item.cooldown, item.durability, item.max_durability, json.dumps(item.effects),
                  json.dumps(item.modifiers), json.dumps(item.tags),
                  json.dumps(item.resist_mod), json.dumps(item.weakness_mod),
                  json.dumps(item.elemental_resistance), item.hex_id))
        
        # Добавляем сущности
        for entity in self.entities.values():
            cursor.execute('''
                INSERT INTO entities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (entity.id, entity.name, entity.description, entity.type,
                  entity.level, entity.experience, entity.experience_to_next,
                  json.dumps(entity.attributes), json.dumps(entity.combat_stats),
                  json.dumps(entity.equipment_slots), entity.inventory_size,
                  json.dumps(entity.skills), json.dumps(entity.tags),
                  entity.enemy_type, entity.experience_reward,
                  entity.ai_behavior, json.dumps(entity.loot_table),
                  json.dumps(entity.phases), entity.hex_id))
        
        conn.commit()
        conn.close()
    
    def get_attribute(self, attr_id: str) -> Optional[AttributeData]:
        """Получить атрибут по ID"""
        return self.attributes.get(attr_id)
    
    def get_effect(self, effect_id: str) -> Optional[EffectData]:
        """Получить эффект по ID"""
        return self.effects.get(effect_id)
    
    def get_item(self, item_id: str) -> Optional[ItemData]:
        """Получить предмет по ID"""
        return self.items.get(item_id)
    
    def get_entity(self, entity_id: str) -> Optional[EntityData]:
        """Получить сущность по ID"""
        return self.entities.get(entity_id)
    
    def search_by_name(self, name: str, data_type: DataType) -> List[Any]:
        """Поиск по имени (для обратной совместимости)"""
        results = []
        
        if data_type == DataType.ATTRIBUTE:
            for attr in self.attributes.values():
                if name.lower() in attr.name.lower():
                    results.append(attr)
        elif data_type == DataType.EFFECT:
            for effect in self.effects.values():
                if name.lower() in effect.name.lower():
                    results.append(effect)
        elif data_type == DataType.ITEM:
            for item in self.items.values():
                if name.lower() in item.name.lower():
                    results.append(item)
        elif data_type == DataType.ENTITY:
            for entity in self.entities.values():
                if name.lower() in entity.name.lower():
                    results.append(entity)
        
        return results
    
    def get_by_tags(self, tags: List[str], data_type: DataType) -> List[Any]:
        """Получить объекты по тегам"""
        results = []
        
        if data_type == DataType.EFFECT:
            for effect in self.effects.values():
                if any(tag in effect.tags for tag in tags):
                    results.append(effect)
        elif data_type == DataType.ITEM:
            for item in self.items.values():
                if any(tag in item.tags for tag in tags):
                    results.append(item)
        elif data_type == DataType.ENTITY:
            for entity in self.entities.values():
                if any(tag in entity.tags for tag in tags):
                    results.append(entity)
        
        return results
    
    def insert_item(self, item: ItemData) -> bool:
        """Добавить предмет в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO items (
                    id, name, description, type, slot, rarity, level_requirement,
                    base_damage, attack_speed, defense, damage_type, element,
                    element_damage, range, cost, mana_cost, critical_chance,
                    weight, block_chance, heal_amount, heal_percent, mana_amount,
                    mana_percent, duration, cooldown, durability, max_durability,
                    effects, modifiers, tags, resist_mod, weakness_mod, elemental_resistance, hex_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item.id, item.name, item.description, item.type, item.slot,
                  item.rarity, item.level_requirement, item.base_damage,
                  item.attack_speed, item.defense, item.damage_type, item.element,
                  item.element_damage, item.range, item.cost, item.mana_cost,
                  item.critical_chance, item.weight, item.block_chance, item.heal_amount,
                  item.heal_percent, item.mana_amount, item.mana_percent, item.duration,
                  item.cooldown, item.durability, item.max_durability, json.dumps(item.effects),
                  json.dumps(item.modifiers), json.dumps(item.tags),
                  json.dumps(item.resist_mod), json.dumps(item.weakness_mod),
                  json.dumps(item.elemental_resistance), item.hex_id))
            
            conn.commit()
            conn.close()
            
            # Добавляем в память
            self.items[item.id] = item
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления предмета: {e}")
            return False


# Глобальный экземпляр менеджера данных
data_manager = DataManager()
