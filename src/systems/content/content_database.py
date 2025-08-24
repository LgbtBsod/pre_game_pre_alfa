#!/usr/bin/env python3
"""
Content Database - База данных для процедурно сгенерированного контента
"""

import sqlite3
import logging
import uuid
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Типы контента"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    GENE = "gene"
    SKILL = "skill"
    EFFECT = "effect"
    MATERIAL = "material"
    ENEMY = "enemy"
    BOSS = "boss"

class ContentRarity(Enum):
    """Редкость контента"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class EnemyType(Enum):
    """Типы врагов"""
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"
    FLYING = "flying"
    UNDEAD = "undead"
    BEAST = "beast"
    HUMAN = "human"
    DEMON = "demon"

class BossType(Enum):
    """Типы боссов"""
    MINI_BOSS = "mini_boss"
    AREA_BOSS = "area_boss"
    DUNGEON_BOSS = "dungeon_boss"
    WORLD_BOSS = "world_boss"
    FINAL_BOSS = "final_boss"

class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"
    ARCANE = "arcane"

@dataclass
class ContentItem:
    """Элемент контента"""
    uuid: str
    content_type: ContentType
    name: str
    description: str
    rarity: ContentRarity
    level_requirement: int
    session_id: str
    generation_timestamp: float
    data: Dict[str, Any]
    is_saved: bool = False  # Сохранен ли в слот

@dataclass
class EnemyData:
    """Данные врага"""
    enemy_type: EnemyType
    base_health: int
    base_mana: int
    base_attack: int
    base_defense: int
    base_speed: float
    base_intelligence: int
    weaknesses: List[DamageType]
    resistances: List[DamageType]
    immunities: List[DamageType]
    skills: List[str]  # UUID скиллов
    loot_table: List[str]  # UUID предметов в луте
    experience_reward: int
    gold_reward: int
    ai_behavior: str  # Тип поведения AI
    spawn_conditions: Dict[str, Any]  # Условия появления

@dataclass
class BossData:
    """Данные босса"""
    boss_type: BossType
    base_health: int
    base_mana: int
    base_attack: int
    base_defense: int
    base_speed: float
    base_intelligence: int
    weaknesses: List[DamageType]
    resistances: List[DamageType]
    immunities: List[DamageType]
    skills: List[str]  # UUID скиллов
    special_abilities: List[str]  # UUID специальных способностей
    phases: List[Dict[str, Any]]  # Фазы боя
    loot_table: List[str]  # UUID предметов в луте
    experience_reward: int
    gold_reward: int
    ai_behavior: str  # Тип поведения AI
    spawn_conditions: Dict[str, Any]  # Условия появления
    minion_spawns: List[Dict[str, Any]]  # Спавн миньонов

class ContentDatabase:
    """База данных для хранения процедурно сгенерированного контента"""
    
    def __init__(self, db_path: str = "content_database.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
        
    def _initialize_database(self):
        """Инициализация базы данных"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Создаем таблицы
            self._create_tables()
            logger.info("База данных контента инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def _create_tables(self):
        """Создание таблиц базы данных"""
        cursor = self.connection.cursor()
        
        # Таблица сессий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time REAL,
                current_level INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Таблица контента
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                uuid TEXT PRIMARY KEY,
                content_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                rarity TEXT NOT NULL,
                level_requirement INTEGER DEFAULT 1,
                session_id TEXT NOT NULL,
                generation_timestamp REAL NOT NULL,
                data TEXT NOT NULL,
                is_saved BOOLEAN DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Таблица врагов (расширенная)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enemies (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                enemy_type TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                session_id TEXT NOT NULL,
                base_health INTEGER DEFAULT 100,
                base_mana INTEGER DEFAULT 50,
                base_attack INTEGER DEFAULT 20,
                base_defense INTEGER DEFAULT 10,
                base_speed REAL DEFAULT 1.0,
                base_intelligence INTEGER DEFAULT 10,
                weaknesses TEXT,  -- JSON список
                resistances TEXT,  -- JSON список
                immunities TEXT,   -- JSON список
                skills TEXT,       -- JSON список UUID
                loot_table TEXT,   -- JSON список UUID
                experience_reward INTEGER DEFAULT 100,
                gold_reward INTEGER DEFAULT 50,
                ai_behavior TEXT DEFAULT 'aggressive',
                spawn_conditions TEXT,  -- JSON
                generation_timestamp REAL NOT NULL,
                is_saved BOOLEAN DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Таблица боссов (расширенная)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bosses (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                boss_type TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                session_id TEXT NOT NULL,
                base_health INTEGER DEFAULT 500,
                base_mana INTEGER DEFAULT 200,
                base_attack INTEGER DEFAULT 80,
                base_defense INTEGER DEFAULT 60,
                base_speed REAL DEFAULT 1.2,
                base_intelligence INTEGER DEFAULT 30,
                weaknesses TEXT,  -- JSON список
                resistances TEXT,  -- JSON список
                immunities TEXT,   -- JSON список
                skills TEXT,       -- JSON список UUID
                special_abilities TEXT,  -- JSON список UUID
                phases TEXT,       -- JSON список фаз
                loot_table TEXT,   -- JSON список UUID
                experience_reward INTEGER DEFAULT 1000,
                gold_reward INTEGER DEFAULT 500,
                ai_behavior TEXT DEFAULT 'boss',
                spawn_conditions TEXT,  -- JSON
                minion_spawns TEXT,    -- JSON список
                generation_timestamp REAL NOT NULL,
                is_saved BOOLEAN DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Индексы для быстрого поиска
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON content (content_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON content (session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_level_req ON content (level_requirement)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rarity ON content (rarity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enemy_type ON enemies (enemy_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enemy_level ON enemies (level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_boss_type ON bosses (boss_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_boss_level ON bosses (level)")
        
        self.connection.commit()
        logger.debug("Таблицы базы данных созданы")
    
    def create_session(self, session_id: str = None) -> str:
        """Создание новой игровой сессии"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sessions (session_id, start_time, current_level, is_active)
                VALUES (?, ?, ?, ?)
            """, (session_id, time.time(), 1, True))
            
            self.connection.commit()
            logger.info(f"Создана новая сессия: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Ошибка создания сессии: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о сессии"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM sessions WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения сессии: {e}")
            return None
    
    def update_session_level(self, session_id: str, new_level: int):
        """Обновление уровня сессии"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE sessions SET current_level = ? WHERE session_id = ?
            """, (new_level, session_id))
            
            self.connection.commit()
            logger.info(f"Уровень сессии {session_id} обновлен до {new_level}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления уровня сессии: {e}")
    
    def add_content_item(self, content_item: Union[ContentItem, Dict[str, Any]]) -> bool:
        """Добавление элемента контента в базу данных"""
        try:
            cursor = self.connection.cursor()
            
            # Поддерживаем как ContentItem, так и обычные словари
            if isinstance(content_item, dict):
                uuid_val = content_item['uuid']
                content_type_val = content_item['content_type'].value if hasattr(content_item['content_type'], 'value') else content_item['content_type']
                name_val = content_item['name']
                description_val = content_item['description']
                rarity_val = content_item['rarity'].value if hasattr(content_item['rarity'], 'value') else content_item['rarity']
                level_req_val = content_item['level_requirement']
                session_id_val = content_item['session_id']
                generation_timestamp_val = content_item['generation_timestamp']
                data_val = json.dumps(content_item['data'])
                is_saved_val = content_item.get('is_saved', False)
            else:
                uuid_val = content_item.uuid
                content_type_val = content_item.content_type.value
                name_val = content_item.name
                description_val = content_item.description
                rarity_val = content_item.rarity.value
                level_req_val = content_item.level_requirement
                session_id_val = content_item.session_id
                generation_timestamp_val = content_item.generation_timestamp
                data_val = json.dumps(content_item.data)
                is_saved_val = content_item.is_saved
            
            cursor.execute("""
                INSERT OR REPLACE INTO content 
                (uuid, content_type, name, description, rarity, level_requirement, 
                 session_id, generation_timestamp, data, is_saved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uuid_val,
                content_type_val,
                name_val,
                description_val,
                rarity_val,
                level_req_val,
                session_id_val,
                generation_timestamp_val,
                data_val,
                is_saved_val
            ))
            
            self.connection.commit()
            logger.debug(f"Добавлен элемент контента: {name_val}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления элемента контента: {e}")
            return False
    
    def add_enemy(self, enemy_uuid: str, name: str, enemy_type: EnemyType, level: int, 
                  session_id: str, enemy_data: EnemyData) -> bool:
        """Добавление врага в базу данных"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO enemies 
                (uuid, name, enemy_type, level, session_id, base_health, base_mana,
                 base_attack, base_defense, base_speed, base_intelligence,
                 weaknesses, resistances, immunities, skills, loot_table,
                 experience_reward, gold_reward, ai_behavior, spawn_conditions,
                 generation_timestamp, is_saved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                enemy_uuid, name, enemy_type.value, level, session_id,
                enemy_data.base_health, enemy_data.base_mana,
                enemy_data.base_attack, enemy_data.base_defense,
                enemy_data.base_speed, enemy_data.base_intelligence,
                json.dumps([w.value for w in enemy_data.weaknesses]),
                json.dumps([r.value for r in enemy_data.resistances]),
                json.dumps([i.value for i in enemy_data.immunities]),
                json.dumps(enemy_data.skills),
                json.dumps(enemy_data.loot_table),
                enemy_data.experience_reward, enemy_data.gold_reward,
                enemy_data.ai_behavior,
                json.dumps(enemy_data.spawn_conditions),
                time.time(), False
            ))
            
            self.connection.commit()
            logger.debug(f"Добавлен враг: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления врага: {e}")
            return False
    
    def add_boss(self, boss_uuid: str, name: str, boss_type: BossType, level: int,
                 session_id: str, boss_data: BossData) -> bool:
        """Добавление босса в базу данных"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO bosses 
                (uuid, name, boss_type, level, session_id, base_health, base_mana,
                 base_attack, base_defense, base_speed, base_intelligence,
                 weaknesses, resistances, immunities, skills, special_abilities,
                 phases, loot_table, experience_reward, gold_reward, ai_behavior,
                 spawn_conditions, minion_spawns, generation_timestamp, is_saved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                boss_uuid, name, boss_type.value, level, session_id,
                boss_data.base_health, boss_data.base_mana,
                boss_data.base_attack, boss_data.base_defense,
                boss_data.base_speed, boss_data.base_intelligence,
                json.dumps([w.value for w in boss_data.weaknesses]),
                json.dumps([r.value for r in boss_data.resistances]),
                json.dumps([i.value for i in boss_data.immunities]),
                json.dumps(boss_data.skills),
                json.dumps(boss_data.special_abilities),
                json.dumps(boss_data.phases),
                json.dumps(boss_data.loot_table),
                boss_data.experience_reward, boss_data.gold_reward,
                boss_data.ai_behavior,
                json.dumps(boss_data.spawn_conditions),
                json.dumps(boss_data.minion_spawns),
                time.time(), False
            ))
            
            self.connection.commit()
            logger.debug(f"Добавлен босс: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления босса: {e}")
            return False
    
    def get_enemies_by_level(self, session_id: str, level: int, enemy_type: Optional[EnemyType] = None) -> List[Dict[str, Any]]:
        """Получение врагов для определенного уровня"""
        try:
            cursor = self.connection.cursor()
            
            if enemy_type:
                cursor.execute("""
                    SELECT * FROM enemies 
                    WHERE session_id = ? AND level <= ? AND enemy_type = ?
                    ORDER BY level DESC, base_health DESC
                """, (session_id, level, enemy_type.value))
            else:
                cursor.execute("""
                    SELECT * FROM enemies 
                    WHERE session_id = ? AND level <= ?
                    ORDER BY level DESC, base_health DESC
                """, (session_id, level))
            
            enemies = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                # Парсим JSON поля
                row_dict['weaknesses'] = json.loads(row_dict['weaknesses'])
                row_dict['resistances'] = json.loads(row_dict['resistances'])
                row_dict['immunities'] = json.loads(row_dict['immunities'])
                row_dict['skills'] = json.loads(row_dict['skills'])
                row_dict['loot_table'] = json.loads(row_dict['loot_table'])
                row_dict['spawn_conditions'] = json.loads(row_dict['spawn_conditions'])
                enemies.append(row_dict)
            
            return enemies
            
        except Exception as e:
            logger.error(f"Ошибка получения врагов для уровня: {e}")
            return []
    
    def get_bosses_by_level(self, session_id: str, level: int, boss_type: Optional[BossType] = None) -> List[Dict[str, Any]]:
        """Получение боссов для определенного уровня"""
        try:
            cursor = self.connection.cursor()
            
            if boss_type:
                cursor.execute("""
                    SELECT * FROM bosses 
                    WHERE session_id = ? AND level <= ? AND boss_type = ?
                    ORDER BY level DESC, base_health DESC
                """, (session_id, level, boss_type.value))
            else:
                cursor.execute("""
                    SELECT * FROM bosses 
                    WHERE session_id = ? AND level <= ?
                    ORDER BY level DESC, base_health DESC
                """, (session_id, level))
            
            bosses = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                # Парсим JSON поля
                row_dict['weaknesses'] = json.loads(row_dict['weaknesses'])
                row_dict['resistances'] = json.loads(row_dict['resistances'])
                row_dict['immunities'] = json.loads(row_dict['immunities'])
                row_dict['skills'] = json.loads(row_dict['skills'])
                row_dict['special_abilities'] = json.loads(row_dict['special_abilities'])
                row_dict['phases'] = json.loads(row_dict['phases'])
                row_dict['loot_table'] = json.loads(row_dict['loot_table'])
                row_dict['spawn_conditions'] = json.loads(row_dict['spawn_conditions'])
                row_dict['minion_spawns'] = json.loads(row_dict['minion_spawns'])
                bosses.append(row_dict)
            
            return bosses
            
        except Exception as e:
            logger.error(f"Ошибка получения боссов для уровня: {e}")
            return []
    
    def get_content_by_session(self, session_id: str, content_type: Optional[ContentType] = None) -> List[ContentItem]:
        """Получение контента для определенной сессии"""
        try:
            cursor = self.connection.cursor()
            
            if content_type:
                cursor.execute("""
                    SELECT * FROM content 
                    WHERE session_id = ? AND content_type = ?
                    ORDER BY generation_timestamp DESC
                """, (session_id, content_type.value))
            else:
                cursor.execute("""
                    SELECT * FROM content 
                    WHERE session_id = ?
                    ORDER BY generation_timestamp DESC
                """, (session_id,))
            
            content_items = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                content_item = ContentItem(
                    uuid=row_dict['uuid'],
                    content_type=ContentType(row_dict['content_type']),
                    name=row_dict['name'],
                    description=row_dict['description'],
                    rarity=ContentRarity(row_dict['rarity']),
                    level_requirement=row_dict['level_requirement'],
                    session_id=row_dict['session_id'],
                    generation_timestamp=row_dict['generation_timestamp'],
                    data=json.loads(row_dict['data']),
                    is_saved=bool(row_dict['is_saved'])
                )
                content_items.append(content_item)
            
            return content_items
            
        except Exception as e:
            logger.error(f"Ошибка получения контента для сессии: {e}")
            return []
    
    def get_content_by_level(self, session_id: str, level: int, content_type: Optional[ContentType] = None) -> List[ContentItem]:
        """Получение контента для определенного уровня"""
        try:
            cursor = self.connection.cursor()
            
            if content_type:
                cursor.execute("""
                    SELECT * FROM content 
                    WHERE session_id = ? AND level_requirement <= ? AND content_type = ?
                    ORDER BY rarity DESC, generation_timestamp DESC
                """, (session_id, level, content_type.value))
            else:
                cursor.execute("""
                    SELECT * FROM content 
                    WHERE session_id = ? AND level_requirement <= ?
                    ORDER BY rarity DESC, generation_timestamp DESC
                """, (session_id, level))
            
            content_items = []
            for row in cursor.fetchall():
                row_dict = dict(row)
                content_item = ContentItem(
                    uuid=row_dict['uuid'],
                    content_type=ContentType(row_dict['content_type']),
                    name=row_dict['name'],
                    description=row_dict['description'],
                    rarity=ContentRarity(row_dict['rarity']),
                    level_requirement=row_dict['level_requirement'],
                    session_id=row_dict['session_id'],
                    generation_timestamp=row_dict['generation_timestamp'],
                    data=json.loads(row_dict['data']),
                    is_saved=bool(row_dict['is_saved'])
                )
                content_items.append(content_item)
            
            return content_items
            
        except Exception as e:
            logger.error(f"Ошибка получения контента для уровня: {e}")
            return []
    
    def mark_content_as_saved(self, content_uuid: str, session_id: str):
        """Отметка контента как сохраненного в слот"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE content SET is_saved = 1 
                WHERE uuid = ? AND session_id = ?
            """, (content_uuid, session_id))
            
            self.connection.commit()
            logger.debug(f"Контент {content_uuid} отмечен как сохраненный")
            
        except Exception as e:
            logger.error(f"Ошибка отметки контента как сохраненного: {e}")
    
    def cleanup_unsaved_content(self, session_id: str):
        """Очистка несохраненного контента для сессии"""
        try:
            cursor = self.connection.cursor()
            
            # Очищаем несохраненный контент
            cursor.execute("""
                DELETE FROM content 
                WHERE session_id = ? AND is_saved = 0
            """)
            content_deleted = cursor.rowcount
            
            # Очищаем несохраненных врагов
            cursor.execute("""
                DELETE FROM enemies 
                WHERE session_id = ? AND is_saved = 0
            """)
            enemies_deleted = cursor.rowcount
            
            # Очищаем несохраненных боссов
            cursor.execute("""
                DELETE FROM bosses 
                WHERE session_id = ? AND is_saved = 0
            """)
            bosses_deleted = cursor.rowcount
            
            self.connection.commit()
            logger.info(f"Удалено {content_deleted} элементов контента, {enemies_deleted} врагов, {bosses_deleted} боссов для сессии {session_id}")
            
        except Exception as e:
            logger.error(f"Ошибка очистки несохраненного контента: {e}")
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Получение статистики сессии"""
        try:
            cursor = self.connection.cursor()
            
            # Общее количество контента
            cursor.execute("""
                SELECT COUNT(*) as total FROM content WHERE session_id = ?
            """, (session_id,))
            total_content = cursor.fetchone()['total']
            
            # Контент по типам
            cursor.execute("""
                SELECT content_type, COUNT(*) as count 
                FROM content 
                WHERE session_id = ?
                GROUP BY content_type
            """, (session_id,))
            content_by_type = dict(cursor.fetchall())
            
            # Контент по редкости
            cursor.execute("""
                SELECT rarity, COUNT(*) as count 
                FROM content 
                WHERE session_id = ?
                GROUP BY rarity
            """, (session_id,))
            content_by_rarity = dict(cursor.fetchall())
            
            # Количество врагов
            cursor.execute("""
                SELECT COUNT(*) as total FROM enemies WHERE session_id = ?
            """, (session_id,))
            total_enemies = cursor.fetchone()['total']
            
            # Количество боссов
            cursor.execute("""
                SELECT COUNT(*) as total FROM bosses WHERE session_id = ?
            """, (session_id,))
            total_bosses = cursor.fetchone()['total']
            
            # Уровень сессии
            session_info = self.get_session(session_id)
            current_level = session_info['current_level'] if session_info else 1
            
            return {
                'session_id': session_id,
                'current_level': current_level,
                'total_content': total_content,
                'content_by_type': content_by_type,
                'content_by_rarity': content_by_rarity,
                'total_enemies': total_enemies,
                'total_bosses': total_bosses
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики сессии: {e}")
            return {}
    
    def get_content_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Получение контента по UUID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM content WHERE uuid = ?
            """, [uuid])
            
            row = cursor.fetchone()
            if row:
                return {
                    'uuid': row[0],
                    'content_type': row[1],
                    'name': row[2],
                    'description': row[3],
                    'rarity': row[4],
                    'level_requirement': row[5],
                    'session_id': row[6],
                    'generation_timestamp': row[7],
                    'data': json.loads(row[8]) if row[8] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения контента по UUID: {e}")
            return None
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
            logger.info("Соединение с базой данных закрыто")
