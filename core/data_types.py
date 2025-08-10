"""
Система кортежей данных для игры
Вместо парсинга по имени используются структурированные данные
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


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

    def to_tuple(
        self,
    ) -> Tuple[str, str, str, float, float, float, str, Dict[str, float]]:
        """Преобразовать в кортеж для быстрого доступа"""
        return (
            self.id,
            self.name,
            self.description,
            self.base_value,
            self.max_value,
            self.growth_rate,
            self.category,
            self.effects,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttributeData":
        """Создать из словаря"""
        # Удаляем hex_id из данных, если он есть, так как это поле уже определено в классе
        data_copy = data.copy()
        if "hex_id" in data_copy:
            del data_copy["hex_id"]
        return cls(**data_copy)


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

    def to_tuple(
        self,
    ) -> Tuple[
        str,
        str,
        str,
        str,
        str,
        List[str],
        Dict[str, Any],
        int,
        Optional[float],
        Optional[float],
        Optional[float],
        bool,
    ]:
        """Преобразовать в кортеж для быстрого доступа"""
        return (
            self.id,
            self.name,
            self.description,
            self.type,
            self.category,
            self.tags,
            self.modifiers,
            self.max_stacks,
            self.duration,
            self.interval,
            self.tick_interval,
            self.stackable,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EffectData":
        """Создать из словаря"""
        # Удаляем hex_id из данных, если он есть, так как это поле уже определено в классе
        data_copy = data.copy()
        if "hex_id" in data_copy:
            del data_copy["hex_id"]
        # Поле type уже определено в классе, поэтому не нужно его удалять
        return cls(**data_copy)


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

    def to_tuple(
        self,
    ) -> Tuple[
        str,
        str,
        str,
        str,
        Optional[str],
        str,
        int,
        Optional[float],
        Optional[float],
        Optional[float],
        Optional[str],
        Optional[str],
        Optional[float],
        Optional[float],
        Optional[int],
        Optional[int],
        Optional[float],
        Optional[float],
        Optional[float],
        Optional[float],
        Optional[float],
        Optional[float],
        Optional[float],
        Optional[float],
        Optional[float],
        Optional[int],
        Optional[int],
        List[str],
        Dict[str, Any],
        List[str],
        Dict[str, float],
        Dict[str, float],
        Dict[str, float],
    ]:
        """Преобразовать в кортеж для быстрого доступа"""
        return (
            self.id,
            self.name,
            self.description,
            self.type,
            self.slot,
            self.rarity,
            self.level_requirement,
            self.base_damage,
            self.attack_speed,
            self.defense,
            self.damage_type,
            self.element,
            self.element_damage,
            self.range,
            self.cost,
            self.mana_cost,
            self.critical_chance,
            self.weight,
            self.block_chance,
            self.heal_amount,
            self.heal_percent,
            self.mana_amount,
            self.mana_percent,
            self.duration,
            self.cooldown,
            self.durability,
            self.max_durability,
            self.effects,
            self.modifiers,
            self.tags,
            self.resist_mod,
            self.weakness_mod,
            self.elemental_resistance,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ItemData":
        """Создать из словаря"""
        # Удаляем hex_id из данных, если он есть, так как это поле уже определено в классе
        data_copy = data.copy()
        if "hex_id" in data_copy:
            del data_copy["hex_id"]
        # Поле type уже определено в классе, поэтому не нужно его удалять
        return cls(**data_copy)


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

    def to_tuple(
        self,
    ) -> Tuple[
        str,
        str,
        str,
        str,
        int,
        int,
        int,
        Dict[str, float],
        Dict[str, float],
        List[str],
        int,
        List[str],
        List[str],
        Optional[str],
        Optional[int],
        Optional[str],
        Optional[List[str]],
        Optional[List[Dict[str, Any]]],
    ]:
        """Преобразовать в кортеж для быстрого доступа"""
        return (
            self.id,
            self.name,
            self.description,
            self.type,
            self.level,
            self.experience,
            self.experience_to_next,
            self.attributes,
            self.combat_stats,
            self.equipment_slots,
            self.inventory_size,
            self.skills,
            self.tags,
            self.enemy_type,
            self.experience_reward,
            self.ai_behavior,
            self.loot_table,
            self.phases,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityData":
        """Создать из словаря"""
        # Удаляем hex_id из данных, если он есть, так как это поле уже определено в классе
        data_copy = data.copy()
        if "hex_id" in data_copy:
            del data_copy["hex_id"]
        # Поле type уже определено в классе, поэтому не нужно его удалять
        return cls(**data_copy)


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
        cursor.execute(
            """
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
        """
        )

        cursor.execute(
            """
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
        """
        )

        cursor.execute(
            """
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
        """
        )

        cursor.execute(
            """
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
        """
        )

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
        """Загрузить атрибуты из базы данных"""
        try:
            import sqlite3

            db_path = Path("data/game_data.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM attributes")
                    rows = cursor.fetchall()

                    for row in rows:
                        try:
                            attr_data = {
                                "id": row[0],
                                "name": row[1],
                                "description": row[2] or "",
                                "base_value": row[3] or 10.0,
                                "max_value": row[4] or 100.0,
                                "growth_rate": row[5] or 1.0,
                                "category": row[6] or "physical",
                                "effects": json.loads(row[7]) if row[7] else {},
                                "hex_id": row[8] if len(row) > 8 else None,
                            }
                            self.attributes[attr_data["id"]] = AttributeData.from_dict(
                                attr_data
                            )
                        except Exception as e:
                            logger.warning(f"Ошибка загрузки атрибута {row[0]}: {e}")
                            continue
            else:
                logger.warning("База данных не найдена")
        except Exception as e:
            logger.error(f"Ошибка загрузки атрибутов: {e}")

    def load_effects(self):
        """Загрузить эффекты из базы данных"""
        try:
            import sqlite3

            db_path = Path("data/game_data.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM effects")
                    rows = cursor.fetchall()

                    for row in rows:
                        try:
                            effect_data = {
                                "id": row[0],
                                "name": row[1],
                                "description": row[2] or "",
                                "type": row[3],
                                "category": row[4] if len(row) > 4 else "general",
                                "tags": (
                                    json.loads(row[5])
                                    if len(row) > 5 and row[5]
                                    else []
                                ),
                                "modifiers": (
                                    json.loads(row[6])
                                    if len(row) > 6 and row[6]
                                    else {}
                                ),
                                "max_stacks": row[7] if len(row) > 7 else 1,
                                "duration": row[8] if len(row) > 8 else None,
                                "interval": row[9] if len(row) > 9 else None,
                                "tick_interval": row[10] if len(row) > 10 else None,
                                "stackable": row[11] if len(row) > 11 else False,
                                "hex_id": row[12] if len(row) > 12 else None,
                            }
                            self.effects[effect_data["id"]] = EffectData.from_dict(
                                effect_data
                            )
                        except Exception as e:
                            logger.warning(f"Ошибка загрузки эффекта {row[0]}: {e}")
                            continue
            else:
                logger.warning("База данных не найдена")
        except Exception as e:
            logger.error(f"Ошибка загрузки эффектов: {e}")

    def load_items(self):
        """Загрузить предметы из базы данных"""
        try:
            import sqlite3

            db_path = Path("data/game_data.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM items")
                    rows = cursor.fetchall()

                    for row in rows:
                        try:
                            item_data = {
                                "id": row[0],
                                "name": row[1],
                                "description": row[2] or "",
                                "type": row[3],
                                "slot": row[4],
                                "rarity": row[5],
                                "level_requirement": row[6] or 1,
                                "base_damage": row[7],
                                "attack_speed": row[8],
                                "defense": row[9],
                                "damage_type": row[10],
                                "element": row[11],
                                "element_damage": row[12],
                                "range": row[13] if len(row) > 13 else None,
                                "cost": row[14] if len(row) > 14 else 0,
                                "mana_cost": row[15] if len(row) > 15 else None,
                                "critical_chance": row[16] if len(row) > 16 else None,
                                "weight": row[17] if len(row) > 17 else None,
                                "block_chance": row[18] if len(row) > 18 else None,
                                "heal_amount": row[19] if len(row) > 19 else None,
                                "heal_percent": row[20] if len(row) > 20 else None,
                                "mana_amount": row[21] if len(row) > 21 else None,
                                "mana_percent": row[22] if len(row) > 22 else None,
                                "duration": row[23] if len(row) > 23 else None,
                                "cooldown": row[24] if len(row) > 24 else None,
                                "durability": row[25] if len(row) > 25 else None,
                                "max_durability": row[26] if len(row) > 26 else None,
                                "effects": (
                                    json.loads(row[27])
                                    if len(row) > 27 and row[27]
                                    else []
                                ),
                                "modifiers": (
                                    json.loads(row[28])
                                    if len(row) > 28 and row[28]
                                    else {}
                                ),
                                "tags": (
                                    json.loads(row[29])
                                    if len(row) > 29 and row[29]
                                    else []
                                ),
                                "resist_mod": (
                                    json.loads(row[30])
                                    if len(row) > 30 and row[30]
                                    else {}
                                ),
                                "weakness_mod": (
                                    json.loads(row[31])
                                    if len(row) > 31 and row[31]
                                    else {}
                                ),
                                "elemental_resistance": (
                                    json.loads(row[32])
                                    if len(row) > 32 and row[32]
                                    else {}
                                ),
                                "hex_id": row[33] if len(row) > 33 else None,
                            }
                            self.items[item_data["id"]] = ItemData.from_dict(item_data)
                        except Exception as e:
                            logger.warning(f"Ошибка загрузки предмета {row[0]}: {e}")
                            continue
            else:
                logger.warning("База данных не найдена")
        except Exception as e:
            logger.error(f"Ошибка загрузки предметов: {e}")

    def load_entities(self):
        """Загрузить сущности из базы данных"""
        try:
            import sqlite3

            db_path = Path("data/game_data.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM entities")
                    rows = cursor.fetchall()

                    for row in rows:
                        try:
                            entity_data = {
                                "id": row[0],
                                "name": row[1],
                                "description": row[2] or "",
                                "type": row[3],
                                "level": row[4] or 1,
                                "experience": row[5] or 0,
                                "experience_to_next": row[6] or 100,
                                "attributes": (
                                    json.loads(row[7])
                                    if len(row) > 7 and row[7]
                                    else {}
                                ),
                                "combat_stats": (
                                    json.loads(row[8])
                                    if len(row) > 8 and row[8]
                                    else {}
                                ),
                                "equipment_slots": (
                                    json.loads(row[9])
                                    if len(row) > 9 and row[9]
                                    else []
                                ),
                                "inventory_size": row[10] if len(row) > 10 else 0,
                                "skills": (
                                    json.loads(row[11])
                                    if len(row) > 11 and row[11]
                                    else []
                                ),
                                "tags": (
                                    json.loads(row[12])
                                    if len(row) > 12 and row[12]
                                    else []
                                ),
                                "enemy_type": row[13] if len(row) > 13 else None,
                                "experience_reward": row[14] if len(row) > 14 else None,
                                "ai_behavior": row[15] if len(row) > 15 else None,
                                "loot_table": (
                                    json.loads(row[16])
                                    if len(row) > 16 and row[16]
                                    else None
                                ),
                                "phases": (
                                    json.loads(row[17])
                                    if len(row) > 17 and row[17]
                                    else None
                                ),
                                "hex_id": row[18] if len(row) > 18 else None,
                            }
                            self.entities[entity_data["id"]] = EntityData.from_dict(
                                entity_data
                            )
                        except Exception as e:
                            logger.warning(f"Ошибка загрузки сущности {row[0]}: {e}")
                            continue
            else:
                logger.warning("База данных не найдена")
        except Exception as e:
            logger.error(f"Ошибка загрузки сущностей: {e}")

    def load_settings(self):
        """Загрузить настройки игры"""
        file_path = self.data_path / "game_settings.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
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
            cursor.execute(
                """
                INSERT INTO attributes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    attr.id,
                    attr.name,
                    attr.description,
                    attr.base_value,
                    attr.max_value,
                    attr.growth_rate,
                    attr.category,
                    json.dumps(attr.effects),
                    attr.hex_id,
                ),
            )

        # Добавляем эффекты
        for effect in self.effects.values():
            cursor.execute(
                """
                INSERT INTO effects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    effect.id,
                    effect.name,
                    effect.description,
                    effect.type,
                    effect.category,
                    json.dumps(effect.tags),
                    json.dumps(effect.modifiers),
                    effect.max_stacks,
                    effect.duration,
                    effect.interval,
                    effect.tick_interval,
                    effect.stackable,
                    effect.type,
                    effect.hex_id,
                ),
            )

        # Добавляем предметы
        for item in self.items.values():
            cursor.execute(
                """
                INSERT INTO items (
                    id, name, description, type, slot, rarity, level_requirement,
                    base_damage, attack_speed, defense, damage_type, element,
                    element_damage, range, cost, mana_cost, critical_chance,
                    weight, block_chance, heal_amount, heal_percent, mana_amount,
                    mana_percent, duration, cooldown, durability, max_durability,
                    effects, modifiers, tags, resist_mod, weakness_mod, elemental_resistance, hex_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item.id,
                    item.name,
                    item.description,
                    item.type,
                    item.slot,
                    item.rarity,
                    item.level_requirement,
                    item.base_damage,
                    item.attack_speed,
                    item.defense,
                    item.damage_type,
                    item.element,
                    item.element_damage,
                    item.range,
                    item.cost,
                    item.mana_cost,
                    item.critical_chance,
                    item.weight,
                    item.block_chance,
                    item.heal_amount,
                    item.heal_percent,
                    item.mana_amount,
                    item.mana_percent,
                    item.duration,
                    item.cooldown,
                    item.durability,
                    item.max_durability,
                    json.dumps(item.effects),
                    json.dumps(item.modifiers),
                    json.dumps(item.tags),
                    json.dumps(item.resist_mod),
                    json.dumps(item.weakness_mod),
                    json.dumps(item.elemental_resistance),
                    item.hex_id,
                ),
            )

        # Добавляем сущности
        for entity in self.entities.values():
            cursor.execute(
                """
                INSERT INTO entities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entity.id,
                    entity.name,
                    entity.description,
                    entity.type,
                    entity.level,
                    entity.experience,
                    entity.experience_to_next,
                    json.dumps(entity.attributes),
                    json.dumps(entity.combat_stats),
                    json.dumps(entity.equipment_slots),
                    entity.inventory_size,
                    json.dumps(entity.skills),
                    json.dumps(entity.tags),
                    entity.enemy_type,
                    entity.experience_reward,
                    entity.ai_behavior,
                    json.dumps(entity.loot_table),
                    json.dumps(entity.phases),
                    entity.hex_id,
                ),
            )

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

    def insert_item(self, item_data: Dict[str, Any]) -> bool:
        """Добавить предмет в базу данных"""
        try:
            # Создаем объект ItemData из словаря
            item = ItemData.from_dict(item_data)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO items (
                    id, name, description, type, slot, rarity, level_requirement,
                    base_damage, attack_speed, defense, damage_type, element,
                    element_damage, range, cost, mana_cost, critical_chance,
                    weight, block_chance, heal_amount, heal_percent, mana_amount,
                    mana_percent, duration, cooldown, durability, max_durability,
                    effects, modifiers, tags, resist_mod, weakness_mod, elemental_resistance, hex_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item.id,
                    item.name,
                    item.description,
                    item.type,
                    item.slot,
                    item.rarity,
                    item.level_requirement,
                    item.base_damage,
                    item.attack_speed,
                    item.defense,
                    item.damage_type,
                    item.element,
                    item.element_damage,
                    item.range,
                    item.cost,
                    item.mana_cost,
                    item.critical_chance,
                    item.weight,
                    item.block_chance,
                    item.heal_amount,
                    item.heal_percent,
                    item.mana_amount,
                    item.mana_percent,
                    item.duration,
                    item.cooldown,
                    item.durability,
                    item.max_durability,
                    json.dumps(item.effects),
                    json.dumps(item.modifiers),
                    json.dumps(item.tags),
                    json.dumps(item.resist_mod),
                    json.dumps(item.weakness_mod),
                    json.dumps(item.elemental_resistance),
                    item.hex_id,
                ),
            )

            conn.commit()
            conn.close()

            # Добавляем в память
            self.items[item.id] = item
            return True

        except Exception as e:
            logger.error(f"Ошибка добавления предмета: {e}")
            return False

    def insert_enemy(self, enemy_data: Dict[str, Any]) -> bool:
        """Добавить врага в базу данных"""
        try:
            # Создаем объект EntityData из словаря
            enemy = EntityData.from_dict(enemy_data)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO entities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    enemy.id,
                    enemy.name,
                    enemy.description,
                    enemy.type,
                    enemy.level,
                    enemy.experience,
                    enemy.experience_to_next,
                    json.dumps(enemy.attributes),
                    json.dumps(enemy.combat_stats),
                    json.dumps(enemy.equipment_slots),
                    enemy.inventory_size,
                    json.dumps(enemy.skills),
                    json.dumps(enemy.tags),
                    enemy.enemy_type,
                    enemy.experience_reward,
                    enemy.ai_behavior,
                    json.dumps(enemy.loot_table),
                    json.dumps(enemy.phases),
                    enemy.hex_id,
                ),
            )

            conn.commit()
            conn.close()

            # Добавляем в память
            self.entities[enemy.id] = enemy
            return True

        except Exception as e:
            logger.error(f"Ошибка добавления врага: {e}")
            return False

    def get_items_by_type(self, item_type: str) -> List[ItemData]:
        """Получить предметы по типу"""
        return [item for item in self.items.values() if item.type == item_type]

    def get_enemies_by_type(self, enemy_type: str) -> List[EntityData]:
        """Получить врагов по типу"""
        return [
            entity
            for entity in self.entities.values()
            if entity.type in ["enemy", "boss"] and entity.enemy_type == enemy_type
        ]

    def get_enemy(self, enemy_id: str) -> Optional[EntityData]:
        """Получить врага по ID"""
        entity = self.entities.get(enemy_id)
        if entity and entity.type in ["enemy", "boss"]:
            return entity
        return None


# Глобальный экземпляр менеджера данных
data_manager = DataManager()
