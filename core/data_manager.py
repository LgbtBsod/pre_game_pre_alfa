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
    attack_range: float = 0.0  # Переименовано с range для избежания конфликта
    effects: List[str] = field(default_factory=list)
    modifiers: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    resist_mod: Dict[str, float] = field(default_factory=dict)
    weakness_mod: Dict[str, float] = field(default_factory=dict)


@dataclass
class EnemyData:
    """Данные врага"""

    id: str
    name: str
    description: str
    enemy_type: str
    level: int
    experience_reward: int
    attributes: Dict[str, float] = field(default_factory=dict)
    combat_stats: Dict[str, float] = field(default_factory=dict)
    ai_behavior: Optional[str] = None
    loot_table: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    phases: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EffectData:
    """Данные эффекта"""

    id: str
    name: str
    description: str
    effect_type: str
    duration: float = 10.0
    tick_rate: float = 1.0
    magnitude: float = 1.0
    target_type: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    modifiers: Dict[str, Any] = field(default_factory=dict)
    visual_effects: Dict[str, Any] = field(default_factory=dict)
    sound_effects: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AbilityData:
    """Данные способности"""

    id: str
    name: str
    description: str
    ability_type: str
    cooldown: float
    mana_cost: int
    stamina_cost: int
    health_cost: int
    damage: float
    damage_type: Optional[str]
    range: float
    area_of_effect: float
    effects: List[str]
    requirements: Dict[str, Any]
    modifiers: Dict[str, Any]


class DataManager:
    """Централизованный менеджер данных игры."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()

        # Кэш данных
        self._items_cache: Dict[str, ItemData] = {}
        self._enemies_cache: Dict[str, EnemyData] = {}
        self._effects_cache: Dict[str, EffectData] = {}
        self._abilities_cache: Dict[str, AbilityData] = {}

        # База данных
        self.db_path = self.data_dir / "game_data.db"
        self._init_database()

        # Загрузка данных из базы данных
        self._load_all_data_from_db()

    def _init_database(self):
        """Инициализация базы данных."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                self._create_tables(conn)
                self._create_indexes(conn)
            logger.info("База данных инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")

    def _create_tables(self, conn: sqlite3.Connection):
        """Создание таблиц в базе данных."""
        cursor = conn.cursor()

        # Таблица предметов
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                slot TEXT,
                rarity TEXT NOT NULL,
                level_requirement INTEGER DEFAULT 1,
                base_damage REAL DEFAULT 0,
                attack_speed REAL DEFAULT 1.0,
                damage_type TEXT,
                element TEXT,
                element_damage REAL DEFAULT 0,
                defense REAL DEFAULT 0,
                range REAL DEFAULT 0,
                weight REAL DEFAULT 0,
                durability INTEGER DEFAULT 100,
                max_durability INTEGER DEFAULT 100,
                cost INTEGER DEFAULT 0,
                effects TEXT,
                modifiers TEXT,
                tags TEXT,
                resist_mod TEXT,
                weakness_mod TEXT
            )
        """
        )

        # Таблица врагов
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS enemies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                enemy_type TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                experience_reward INTEGER DEFAULT 10,
                attributes TEXT,
                combat_stats TEXT,
                ai_behavior TEXT,
                loot_table TEXT,
                skills TEXT,
                tags TEXT,
                phases TEXT
            )
        """
        )

        # Таблица эффектов
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS effects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                effect_type TEXT NOT NULL,
                duration REAL DEFAULT 10.0,
                tick_rate REAL DEFAULT 1.0,
                magnitude REAL DEFAULT 1.0,
                target_type TEXT,
                conditions TEXT,
                modifiers TEXT,
                visual_effects TEXT,
                sound_effects TEXT
            )
        """
        )

        # Таблица способностей
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS abilities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                ability_type TEXT NOT NULL,
                cooldown REAL DEFAULT 1.0,
                mana_cost INTEGER DEFAULT 0,
                stamina_cost INTEGER DEFAULT 0,
                health_cost INTEGER DEFAULT 0,
                damage REAL DEFAULT 0,
                damage_type TEXT,
                range REAL DEFAULT 0,
                area_of_effect REAL DEFAULT 0,
                effects TEXT,
                requirements TEXT,
                modifiers TEXT
            )
        """
        )

        conn.commit()

    def _create_indexes(self, conn: sqlite3.Connection):
        """Создание индексов для оптимизации."""
        cursor = conn.cursor()

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON items(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_enemies_type ON enemies(enemy_type)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enemies_level ON enemies(level)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_effects_type ON effects(effect_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_abilities_type ON abilities(ability_type)"
        )

        conn.commit()

    def _load_all_data_from_db(self):
        """Загружает все данные из базы данных."""
        try:
            self._load_items_from_db()
            self._load_enemies_from_db()
            self._load_effects_from_db()
            self._load_abilities_from_db()
            logger.info("Все данные загружены успешно")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")

    def _load_items_from_db(self):
        """Загружает предметы из базы данных."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM items")
                rows = cursor.fetchall()

                for row in rows:
                    try:
                        # Создаем словарь с данными из БД, учитывая порядок колонок
                        # id, name, description, type, slot, rarity, level_requirement,
                        # base_damage, attack_speed, defense, damage_type, element,
                        # element_damage, range, cost, mana_cost, critical_chance,
                        # weight, block_chance, heal_amount, heal_percent, mana_amount,
                        # mana_percent, duration, cooldown, durability, max_durability,
                        # effects, modifiers, tags, resist_mod, weakness_mod, elemental_resistance, hex_id

                        # Безопасно извлекаем значения с проверкой на None
                        effects_json = row[26] if len(row) > 26 and row[26] else "[]"
                        modifiers_json = row[27] if len(row) > 27 and row[27] else "{}"
                        tags_json = row[28] if len(row) > 28 and row[28] else "[]"
                        resist_mod_json = row[29] if len(row) > 29 and row[29] else "{}"
                        weakness_mod_json = (
                            row[30] if len(row) > 30 and row[30] else "{}"
                        )

                        # Безопасно парсим JSON
                        try:
                            effects = (
                                json.loads(effects_json)
                                if isinstance(effects_json, str)
                                else []
                            )
                        except (json.JSONDecodeError, TypeError):
                            effects = []

                        try:
                            modifiers = (
                                json.loads(modifiers_json)
                                if isinstance(modifiers_json, str)
                                else {}
                            )
                        except (json.JSONDecodeError, TypeError):
                            modifiers = {}

                        try:
                            tags = (
                                json.loads(tags_json)
                                if isinstance(tags_json, str)
                                else []
                            )
                        except (json.JSONDecodeError, TypeError):
                            tags = []

                        try:
                            resist_mod = (
                                json.loads(resist_mod_json)
                                if isinstance(resist_mod_json, str)
                                else {}
                            )
                        except (json.JSONDecodeError, TypeError):
                            resist_mod = {}

                        try:
                            weakness_mod = (
                                json.loads(weakness_mod_json)
                                if isinstance(weakness_mod_json, str)
                                else {}
                            )
                        except (json.JSONDecodeError, TypeError):
                            weakness_mod = {}

                        item_data = {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2] or "",
                            "type": row[3] or "item",
                            "slot": row[4],
                            "rarity": row[5] or "common",
                            "level_requirement": row[6] or 1,
                            "base_damage": float(row[7]) if row[7] is not None else 0.0,
                            "attack_speed": (
                                float(row[8]) if row[8] is not None else 1.0
                            ),
                            "damage_type": row[10] if len(row) > 10 else None,
                            "element": row[11] if len(row) > 11 else None,
                            "element_damage": (
                                float(row[12])
                                if len(row) > 12 and row[12] is not None
                                else 0.0
                            ),
                            "defense": (
                                float(row[9])
                                if len(row) > 9 and row[9] is not None
                                else 0.0
                            ),
                            "attack_range": (
                                float(row[13])
                                if len(row) > 13 and row[13] is not None
                                else 0.0
                            ),  # Добавлено поле attack_range
                            "weight": (
                                float(row[17])
                                if len(row) > 17 and row[17] is not None
                                else 0.0
                            ),
                            "durability": (
                                int(row[24])
                                if len(row) > 24 and row[24] is not None
                                else 100
                            ),
                            "max_durability": (
                                int(row[25])
                                if len(row) > 25 and row[25] is not None
                                else 100
                            ),
                            "cost": (
                                int(row[14])
                                if len(row) > 14 and row[14] is not None
                                else 0
                            ),
                            "effects": effects,
                            "modifiers": modifiers,
                            "tags": tags,
                            "resist_mod": resist_mod,
                            "weakness_mod": weakness_mod,
                        }

                        self._items_cache[item_data["id"]] = ItemData(**item_data)
                    except Exception as e:
                        logger.warning(f"Ошибка загрузки предмета {row[0]}: {e}")
                        continue

                logger.info(f"Загружено {len(self._items_cache)} предметов из БД")
        except Exception as e:
            logger.error(f"Ошибка загрузки предметов из БД: {e}")

    def _load_enemies_from_db(self):
        """Загружает врагов из базы данных."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM enemies")
                rows = cursor.fetchall()

                for row in rows:
                    try:
                        # Создаем словарь с данными из БД, учитывая порядок колонок
                        # id, name, description, enemy_type, level, experience_reward,
                        # attributes, combat_stats, ai_behavior, loot_table, skills, tags, phases

                        # Безопасно извлекаем JSON поля
                        attributes_json = row[6] if len(row) > 6 and row[6] else "{}"
                        combat_stats_json = row[7] if len(row) > 7 and row[7] else "{}"
                        loot_table_json = row[9] if len(row) > 9 and row[9] else "[]"
                        skills_json = row[10] if len(row) > 10 and row[10] else "[]"
                        tags_json = row[11] if len(row) > 11 and row[11] else "[]"
                        phases_json = row[12] if len(row) > 12 and row[12] else "[]"

                        # Безопасно парсим JSON
                        try:
                            attributes = (
                                json.loads(attributes_json)
                                if isinstance(attributes_json, str)
                                else {}
                            )
                        except (json.JSONDecodeError, TypeError):
                            attributes = {}

                        try:
                            combat_stats = (
                                json.loads(combat_stats_json)
                                if isinstance(combat_stats_json, str)
                                else {}
                            )
                        except (json.JSONDecodeError, TypeError):
                            combat_stats = {}

                        try:
                            loot_table = (
                                json.loads(loot_table_json)
                                if isinstance(loot_table_json, str)
                                else []
                            )
                        except (json.JSONDecodeError, TypeError):
                            loot_table = []

                        try:
                            skills = (
                                json.loads(skills_json)
                                if isinstance(skills_json, str)
                                else []
                            )
                        except (json.JSONDecodeError, TypeError):
                            skills = []

                        try:
                            tags = (
                                json.loads(tags_json)
                                if isinstance(tags_json, str)
                                else []
                            )
                        except (json.JSONDecodeError, TypeError):
                            tags = []

                        try:
                            phases = (
                                json.loads(phases_json)
                                if isinstance(phases_json, str)
                                else []
                            )
                        except (json.JSONDecodeError, TypeError):
                            phases = []

                        enemy_data = {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2] or "",
                            "enemy_type": row[3] or "enemy",
                            "level": int(row[4]) if row[4] is not None else 1,
                            "experience_reward": (
                                int(row[5]) if row[5] is not None else 0
                            ),
                            "attributes": attributes,
                            "combat_stats": combat_stats,
                            "ai_behavior": row[8] if len(row) > 8 else None,
                            "loot_table": loot_table,
                            "skills": skills,
                            "tags": tags,
                            "phases": phases,
                        }

                        self._enemies_cache[enemy_data["id"]] = EnemyData(**enemy_data)
                    except Exception as e:
                        logger.warning(f"Ошибка загрузки врага {row[0]}: {e}")
                        continue

                logger.info(f"Загружено {len(self._enemies_cache)} врагов из БД")
        except Exception as e:
            logger.error(f"Ошибка загрузки врагов из БД: {e}")

    def _load_effects_from_db(self):
        """Загружает эффекты из базы данных."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM effects")
                rows = cursor.fetchall()

                for row in rows:
                    try:
                        # Создаем словарь с данными из БД, учитывая порядок колонок
                        # id, name, description, type, category, tags, modifiers, max_stacks,
                        # duration, interval, tick_interval, stackable, effect_type, hex_id

                        # Безопасно извлекаем JSON поля
                        tags_json = row[5] if len(row) > 5 and row[5] else "[]"
                        modifiers_json = row[6] if len(row) > 6 and row[6] else "{}"

                        # Безопасно парсим JSON
                        try:
                            tags = (
                                json.loads(tags_json)
                                if isinstance(tags_json, str)
                                else []
                            )
                        except (json.JSONDecodeError, TypeError):
                            tags = []

                        try:
                            modifiers = (
                                json.loads(modifiers_json)
                                if isinstance(modifiers_json, str)
                                else {}
                            )
                        except (json.JSONDecodeError, TypeError):
                            modifiers = {}

                        effect_data = {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2] or "",
                            "effect_type": row[12] if len(row) > 12 else "buff",
                            "duration": (
                                float(row[8])
                                if len(row) > 8 and row[8] is not None
                                else 10.0
                            ),
                            "tick_rate": (
                                float(row[10])
                                if len(row) > 10 and row[10] is not None
                                else 1.0
                            ),
                            "magnitude": 1.0,  # Default value
                            "target_type": None,  # Default value
                            "conditions": {},  # Default value
                            "modifiers": modifiers,
                            "visual_effects": {},  # Default value
                            "sound_effects": {},  # Default value
                        }

                        self._effects_cache[effect_data["id"]] = EffectData(
                            **effect_data
                        )
                    except Exception as e:
                        logger.warning(f"Ошибка загрузки эффекта {row[0]}: {e}")
                        continue

                logger.info(f"Загружено {len(self._effects_cache)} эффектов из БД")
        except Exception as e:
            logger.error(f"Ошибка загрузки эффектов из БД: {e}")

    def _load_abilities_from_db(self):
        """Загружает способности из базы данных."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM abilities")
                rows = cursor.fetchall()

                for row in rows:
                    try:
                        # Создаем словарь с данными из БД, учитывая порядок колонок
                        # id, name, description, ability_type, cooldown, mana_cost, stamina_cost,
                        # health_cost, damage, damage_type, range, area_of_effect, effects, requirements, modifiers

                        # Безопасно извлекаем JSON поля
                        effects_json = row[12] if len(row) > 12 and row[12] else "[]"
                        requirements_json = (
                            row[13] if len(row) > 13 and row[13] else "{}"
                        )
                        modifiers_json = row[14] if len(row) > 14 and row[14] else "{}"

                        # Безопасно парсим JSON
                        try:
                            effects = (
                                json.loads(effects_json)
                                if isinstance(effects_json, str)
                                else []
                            )
                        except (json.JSONDecodeError, TypeError):
                            effects = []

                        try:
                            requirements = (
                                json.loads(requirements_json)
                                if isinstance(requirements_json, str)
                                else {}
                            )
                        except (json.JSONDecodeError, TypeError):
                            requirements = {}

                        try:
                            modifiers = (
                                json.loads(modifiers_json)
                                if isinstance(modifiers_json, str)
                                else {}
                            )
                        except (json.JSONDecodeError, TypeError):
                            modifiers = {}

                        ability_data = {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2] or "",
                            "ability_type": row[3] or "passive",
                            "cooldown": float(row[4]) if row[4] is not None else 0.0,
                            "mana_cost": int(row[5]) if row[5] is not None else 0,
                            "stamina_cost": int(row[6]) if row[6] is not None else 0,
                            "health_cost": int(row[7]) if row[7] is not None else 0,
                            "damage": float(row[8]) if row[8] is not None else 0.0,
                            "damage_type": row[9] if len(row) > 9 else None,
                            "range": (
                                float(row[10])
                                if len(row) > 10 and row[10] is not None
                                else 0.0
                            ),
                            "area_of_effect": (
                                float(row[11])
                                if len(row) > 11 and row[11] is not None
                                else 0.0
                            ),
                            "effects": effects,
                            "requirements": requirements,
                            "modifiers": modifiers,
                        }

                        self._abilities_cache[ability_data["id"]] = AbilityData(
                            **ability_data
                        )
                    except Exception as e:
                        logger.warning(f"Ошибка загрузки способности {row[0]}: {e}")
                        continue

                logger.info(
                    f"Загружено {len(self._abilities_cache)} способностей из БД"
                )
        except Exception as e:
            logger.error(f"Ошибка загрузки способностей из БД: {e}")

    def _insert_item_to_db(self, conn: sqlite3.Connection, item_data: ItemData):
        """Вставляет предмет в БД."""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO items 
            (id, name, description, type, slot, rarity, level_requirement,
             base_damage, attack_speed, damage_type, element, element_damage,
             defense, range, weight, durability, max_durability, cost, effects,
             modifiers, tags, resist_mod, weakness_mod)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item_data.id,
                item_data.name,
                item_data.description,
                item_data.type,
                item_data.slot,
                item_data.rarity,
                item_data.level_requirement,
                item_data.base_damage,
                item_data.attack_speed,
                item_data.damage_type,
                item_data.element,
                item_data.element_damage,
                item_data.defense,
                item_data.attack_range,
                item_data.weight,
                item_data.durability,
                item_data.max_durability,
                item_data.cost,
                json.dumps(item_data.effects),
                json.dumps(item_data.modifiers),
                json.dumps(item_data.tags),
                json.dumps(item_data.resist_mod),
                json.dumps(item_data.weakness_mod),
            ),
        )

    def _insert_enemy_to_db(self, conn: sqlite3.Connection, enemy_data: EnemyData):
        """Вставляет врага в БД."""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO enemies 
            (id, name, description, enemy_type, level, experience_reward,
             attributes, combat_stats, ai_behavior, loot_table, skills, tags, phases)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                enemy_data.id,
                enemy_data.name,
                enemy_data.description,
                enemy_data.enemy_type,
                enemy_data.level,
                enemy_data.experience_reward,
                json.dumps(enemy_data.attributes),
                json.dumps(enemy_data.combat_stats),
                enemy_data.ai_behavior,
                json.dumps(enemy_data.loot_table),
                json.dumps(enemy_data.skills),
                json.dumps(enemy_data.tags),
                json.dumps(enemy_data.phases),
            ),
        )

    def _insert_effect_to_db(self, conn: sqlite3.Connection, effect_data: EffectData):
        """Вставляет эффект в БД."""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO effects 
            (id, name, description, effect_type, duration, tick_rate, magnitude,
             target_type, conditions, modifiers, visual_effects, sound_effects)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                effect_data.id,
                effect_data.name,
                effect_data.description,
                effect_data.effect_type,
                effect_data.duration,
                effect_data.tick_rate,
                effect_data.magnitude,
                effect_data.target_type,
                json.dumps(effect_data.conditions),
                json.dumps(effect_data.modifiers),
                json.dumps(effect_data.visual_effects),
                json.dumps(effect_data.sound_effects),
            ),
        )

    def _insert_ability_to_db(
        self, conn: sqlite3.Connection, ability_data: AbilityData
    ):
        """Вставляет способность в БД."""
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO abilities 
            (id, name, description, ability_type, cooldown, mana_cost, stamina_cost,
             health_cost, damage, damage_type, range, area_of_effect, effects,
             requirements, modifiers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                ability_data.id,
                ability_data.name,
                ability_data.description,
                ability_data.ability_type,
                ability_data.cooldown,
                ability_data.mana_cost,
                ability_data.stamina_cost,
                ability_data.health_cost,
                ability_data.damage,
                ability_data.damage_type,
                ability_data.range,
                ability_data.area_of_effect,
                json.dumps(ability_data.effects),
                json.dumps(ability_data.requirements),
                json.dumps(ability_data.modifiers),
            ),
        )

    # Методы доступа к данным
    def get_item(self, item_id: str) -> Optional[ItemData]:
        """Получает данные предмета."""
        with self._lock:
            return self._items_cache.get(item_id)

    def get_items_by_type(self, item_type: str) -> List[ItemData]:
        """Получает предметы по типу."""
        with self._lock:
            return [
                item for item in self._items_cache.values() if item.type == item_type
            ]

    def get_items_by_rarity(self, rarity: str) -> List[ItemData]:
        """Получает предметы по редкости."""
        with self._lock:
            return [
                item for item in self._items_cache.values() if item.rarity == rarity
            ]

    def get_enemy(self, enemy_id: str) -> Optional[EnemyData]:
        """Получает данные врага."""
        with self._lock:
            return self._enemies_cache.get(enemy_id)

    def get_enemies_by_type(self, enemy_type: str) -> List[EnemyData]:
        """Получает врагов по типу."""
        with self._lock:
            return [
                enemy
                for enemy in self._enemies_cache.values()
                if enemy.enemy_type == enemy_type
            ]

    def get_enemies_by_level(self, level: int) -> List[EnemyData]:
        """Получает врагов по уровню."""
        with self._lock:
            return [
                enemy for enemy in self._enemies_cache.values() if enemy.level == level
            ]

    def get_effect(self, effect_id: str) -> Optional[EffectData]:
        """Получает данные эффекта."""
        with self._lock:
            return self._effects_cache.get(effect_id)

    def get_effects_by_type(self, effect_type: str) -> List[EffectData]:
        """Получает эффекты по типу."""
        with self._lock:
            return [
                effect
                for effect in self._effects_cache.values()
                if effect.effect_type == effect_type
            ]

    def get_ability(self, ability_id: str) -> Optional[AbilityData]:
        """Получает данные способности."""
        with self._lock:
            return self._abilities_cache.get(ability_id)

    def get_abilities_by_type(self, ability_type: str) -> List[AbilityData]:
        """Получает способности по типу."""
        with self._lock:
            return [
                ability
                for ability in self._abilities_cache.values()
                if ability.ability_type == ability_type
            ]

    def get_all_items(self) -> List[ItemData]:
        """Получает все предметы."""
        with self._lock:
            return list(self._items_cache.values())

    def get_all_enemies(self) -> List[EnemyData]:
        """Получает всех врагов."""
        with self._lock:
            return list(self._enemies_cache.values())

    def get_all_effects(self) -> List[EffectData]:
        """Получает все эффекты."""
        with self._lock:
            return list(self._effects_cache.values())

    def get_all_abilities(self) -> List[AbilityData]:
        """Получает все способности."""
        with self._lock:
            return list(self._abilities_cache.values())

    def add_item(self, item_data: ItemData) -> bool:
        """Добавляет новый предмет."""
        with self._lock:
            try:
                self._items_cache[item_data.id] = item_data
                with sqlite3.connect(self.db_path) as conn:
                    self._insert_item_to_db(conn, item_data)
                return True
            except Exception as e:
                logger.error(f"Ошибка добавления предмета: {e}")
                return False

    def add_enemy(self, enemy_data: EnemyData) -> bool:
        """Добавляет нового врага."""
        with self._lock:
            try:
                self._enemies_cache[enemy_data.id] = enemy_data
                with sqlite3.connect(self.db_path) as conn:
                    self._insert_enemy_to_db(conn, enemy_data)
                return True
            except Exception as e:
                logger.error(f"Ошибка добавления врага: {e}")
                return False

    def reload_data(self):
        """Перезагружает все данные."""
        with self._lock:
            self._items_cache.clear()
            self._enemies_cache.clear()
            self._effects_cache.clear()
            self._abilities_cache.clear()
            self._load_all_data_from_db()


# Глобальный экземпляр менеджера данных
data_manager = DataManager()
