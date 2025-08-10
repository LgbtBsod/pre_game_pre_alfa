"""
Централизованный менеджер данных игры.
Управляет загрузкой и доступом к данным предметов, врагов, эффектов и других игровых объектов.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
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
    base_damage: float
    attack_speed: float
    damage_type: Optional[str]
    element: Optional[str]
    element_damage: float
    defense: float
    weight: float
    durability: int
    max_durability: int
    cost: int
    effects: List[str]
    modifiers: Dict[str, Any]
    tags: List[str]
    resist_mod: Dict[str, float]
    weakness_mod: Dict[str, float]


@dataclass
class EnemyData:
    """Данные врага"""
    id: str
    name: str
    description: str
    enemy_type: str
    level: int
    experience_reward: int
    attributes: Dict[str, float]
    combat_stats: Dict[str, float]
    ai_behavior: Optional[str]
    loot_table: List[str]
    skills: List[str]
    tags: List[str]
    phases: List[Dict[str, Any]]


@dataclass
class EffectData:
    """Данные эффекта"""
    id: str
    name: str
    description: str
    effect_type: str
    duration: float
    tick_rate: float
    magnitude: float
    target_type: Optional[str]
    conditions: Dict[str, Any]
    modifiers: Dict[str, Any]
    visual_effects: Dict[str, Any]
    sound_effects: Dict[str, Any]


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
        
        # Загрузка данных
        self._load_all_data()
    
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
        cursor.execute('''
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
        ''')
        
        # Таблица врагов
        cursor.execute('''
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
        ''')
        
        # Таблица эффектов
        cursor.execute('''
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
        ''')
        
        # Таблица способностей
        cursor.execute('''
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
        ''')
        
        conn.commit()
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Создание индексов для оптимизации."""
        cursor = conn.cursor()
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_type ON items(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enemies_type ON enemies(enemy_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enemies_level ON enemies(level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_effects_type ON effects(effect_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_abilities_type ON abilities(ability_type)')
        
        conn.commit()
    
    def _load_all_data(self):
        """Загружает все данные из JSON файлов и БД."""
        try:
            self._load_items_from_json()
            self._load_enemies_from_json()
            self._load_effects_from_json()
            self._load_abilities_from_json()
            
            # Импортируем данные в БД
            self._import_json_to_db()
            
            logger.info("Все данные загружены успешно")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
    
    def _load_items_from_json(self):
        """Загружает предметы из JSON файла."""
        try:
            items_file = self.data_dir / "items.json"
            if items_file.exists():
                with open(items_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item_id, item_data in data.get("items", {}).items():
                        item_data["id"] = item_id
                        self._items_cache[item_id] = ItemData(**item_data)
                logger.info(f"Загружено {len(self._items_cache)} предметов")
        except Exception as e:
            logger.error(f"Ошибка загрузки предметов: {e}")
    
    def _load_enemies_from_json(self):
        """Загружает врагов из JSON файла."""
        try:
            entities_file = self.data_dir / "entities.json"
            if entities_file.exists():
                with open(entities_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entity_id, entity_data in data.get("entities", {}).items():
                        if entity_data.get("type") in ["enemy", "boss"]:
                            entity_data["id"] = entity_id
                            self._enemies_cache[entity_id] = EnemyData(**entity_data)
                logger.info(f"Загружено {len(self._enemies_cache)} врагов")
        except Exception as e:
            logger.error(f"Ошибка загрузки врагов: {e}")
    
    def _load_effects_from_json(self):
        """Загружает эффекты из JSON файла."""
        try:
            effects_file = self.data_dir / "effects.json"
            if effects_file.exists():
                with open(effects_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for effect_id, effect_data in data.get("effects", {}).items():
                        effect_data["id"] = effect_id
                        self._effects_cache[effect_id] = EffectData(**effect_data)
                logger.info(f"Загружено {len(self._effects_cache)} эффектов")
        except Exception as e:
            logger.error(f"Ошибка загрузки эффектов: {e}")
    
    def _load_abilities_from_json(self):
        """Загружает способности из JSON файла."""
        try:
            abilities_file = self.data_dir / "abilities.json"
            if abilities_file.exists():
                with open(abilities_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ability_id, ability_data in data.get("abilities", {}).items():
                        ability_data["id"] = ability_id
                        self._abilities_cache[ability_id] = AbilityData(**ability_data)
                logger.info(f"Загружено {len(self._abilities_cache)} способностей")
        except Exception as e:
            logger.error(f"Ошибка загрузки способностей: {e}")
    
    def _import_json_to_db(self):
        """Импортирует данные из JSON в базу данных."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Импорт предметов
                for item_data in self._items_cache.values():
                    self._insert_item_to_db(conn, item_data)
                
                # Импорт врагов
                for enemy_data in self._enemies_cache.values():
                    self._insert_enemy_to_db(conn, enemy_data)
                
                # Импорт эффектов
                for effect_data in self._effects_cache.values():
                    self._insert_effect_to_db(conn, effect_data)
                
                # Импорт способностей
                for ability_data in self._abilities_cache.values():
                    self._insert_ability_to_db(conn, ability_data)
                
            logger.info("Данные импортированы в БД")
        except Exception as e:
            logger.error(f"Ошибка импорта в БД: {e}")
    
    def _insert_item_to_db(self, conn: sqlite3.Connection, item_data: ItemData):
        """Вставляет предмет в БД."""
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO items 
            (id, name, description, type, slot, rarity, level_requirement,
             base_damage, attack_speed, damage_type, element, element_damage,
             defense, weight, durability, max_durability, cost, effects,
             modifiers, tags, resist_mod, weakness_mod)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_data.id, item_data.name, item_data.description, item_data.type,
            item_data.slot, item_data.rarity, item_data.level_requirement,
            item_data.base_damage, item_data.attack_speed, item_data.damage_type,
            item_data.element, item_data.element_damage, item_data.defense,
            item_data.weight, item_data.durability, item_data.max_durability,
            item_data.cost, json.dumps(item_data.effects), json.dumps(item_data.modifiers),
            json.dumps(item_data.tags), json.dumps(item_data.resist_mod),
            json.dumps(item_data.weakness_mod)
        ))
    
    def _insert_enemy_to_db(self, conn: sqlite3.Connection, enemy_data: EnemyData):
        """Вставляет врага в БД."""
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO enemies 
            (id, name, description, enemy_type, level, experience_reward,
             attributes, combat_stats, ai_behavior, loot_table, skills, tags, phases)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            enemy_data.id, enemy_data.name, enemy_data.description, enemy_data.enemy_type,
            enemy_data.level, enemy_data.experience_reward, json.dumps(enemy_data.attributes),
            json.dumps(enemy_data.combat_stats), enemy_data.ai_behavior,
            json.dumps(enemy_data.loot_table), json.dumps(enemy_data.skills),
            json.dumps(enemy_data.tags), json.dumps(enemy_data.phases)
        ))
    
    def _insert_effect_to_db(self, conn: sqlite3.Connection, effect_data: EffectData):
        """Вставляет эффект в БД."""
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO effects 
            (id, name, description, effect_type, duration, tick_rate, magnitude,
             target_type, conditions, modifiers, visual_effects, sound_effects)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            effect_data.id, effect_data.name, effect_data.description, effect_data.effect_type,
            effect_data.duration, effect_data.tick_rate, effect_data.magnitude,
            effect_data.target_type, json.dumps(effect_data.conditions),
            json.dumps(effect_data.modifiers), json.dumps(effect_data.visual_effects),
            json.dumps(effect_data.sound_effects)
        ))
    
    def _insert_ability_to_db(self, conn: sqlite3.Connection, ability_data: AbilityData):
        """Вставляет способность в БД."""
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO abilities 
            (id, name, description, ability_type, cooldown, mana_cost, stamina_cost,
             health_cost, damage, damage_type, range, area_of_effect, effects,
             requirements, modifiers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ability_data.id, ability_data.name, ability_data.description, ability_data.ability_type,
            ability_data.cooldown, ability_data.mana_cost, ability_data.stamina_cost,
            ability_data.health_cost, ability_data.damage, ability_data.damage_type,
            ability_data.range, ability_data.area_of_effect, json.dumps(ability_data.effects),
            json.dumps(ability_data.requirements), json.dumps(ability_data.modifiers)
        ))
    
    # Методы доступа к данным
    def get_item(self, item_id: str) -> Optional[ItemData]:
        """Получает данные предмета."""
        with self._lock:
            return self._items_cache.get(item_id)
    
    def get_items_by_type(self, item_type: str) -> List[ItemData]:
        """Получает предметы по типу."""
        with self._lock:
            return [item for item in self._items_cache.values() if item.type == item_type]
    
    def get_items_by_rarity(self, rarity: str) -> List[ItemData]:
        """Получает предметы по редкости."""
        with self._lock:
            return [item for item in self._items_cache.values() if item.rarity == rarity]
    
    def get_enemy(self, enemy_id: str) -> Optional[EnemyData]:
        """Получает данные врага."""
        with self._lock:
            return self._enemies_cache.get(enemy_id)
    
    def get_enemies_by_type(self, enemy_type: str) -> List[EnemyData]:
        """Получает врагов по типу."""
        with self._lock:
            return [enemy for enemy in self._enemies_cache.values() if enemy.enemy_type == enemy_type]
    
    def get_enemies_by_level(self, level: int) -> List[EnemyData]:
        """Получает врагов по уровню."""
        with self._lock:
            return [enemy for enemy in self._enemies_cache.values() if enemy.level == level]
    
    def get_effect(self, effect_id: str) -> Optional[EffectData]:
        """Получает данные эффекта."""
        with self._lock:
            return self._effects_cache.get(effect_id)
    
    def get_effects_by_type(self, effect_type: str) -> List[EffectData]:
        """Получает эффекты по типу."""
        with self._lock:
            return [effect for effect in self._effects_cache.values() if effect.effect_type == effect_type]
    
    def get_ability(self, ability_id: str) -> Optional[AbilityData]:
        """Получает данные способности."""
        with self._lock:
            return self._abilities_cache.get(ability_id)
    
    def get_abilities_by_type(self, ability_type: str) -> List[AbilityData]:
        """Получает способности по типу."""
        with self._lock:
            return [ability for ability in self._abilities_cache.values() if ability.ability_type == ability_type]
    
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
            self._load_all_data()


# Глобальный экземпляр менеджера данных
data_manager = DataManager()
