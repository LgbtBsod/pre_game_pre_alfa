"""Менеджер базы данных для хранения игровых данных."""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер базы данных для хранения игровых данных."""
    
    def __init__(self, db_path: str = "data/game_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных и создание таблиц."""
        try:
            with self._get_connection() as conn:
                self._create_tables(conn)
                self._create_indexes(conn)
            logger.info("База данных инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
    
    def _get_connection(self):
        """Получает соединение с базой данных."""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Создает таблицы в базе данных."""
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
                effects TEXT,  -- JSON
                modifiers TEXT,  -- JSON
                tags TEXT,  -- JSON
                resist_mod TEXT,  -- JSON
                weakness_mod TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                attributes TEXT,  -- JSON
                combat_stats TEXT,  -- JSON
                ai_behavior TEXT,
                loot_table TEXT,  -- JSON
                skills TEXT,  -- JSON
                tags TEXT,  -- JSON
                phases TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                target_type TEXT,  -- self, enemy, area
                conditions TEXT,  -- JSON
                modifiers TEXT,  -- JSON
                visual_effects TEXT,  -- JSON
                sound_effects TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                effects TEXT,  -- JSON
                requirements TEXT,  -- JSON
                modifiers TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица атрибутов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attributes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                attribute_type TEXT NOT NULL,
                base_value REAL DEFAULT 0,
                max_value REAL DEFAULT 100,
                scaling_factor REAL DEFAULT 1.0,
                effects TEXT,  -- JSON
                modifiers TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица игровых сессий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                player_data TEXT,  -- JSON
                game_state TEXT,  -- JSON
                difficulty TEXT DEFAULT 'normal',
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER,
                score INTEGER DEFAULT 0,
                achievements TEXT  -- JSON
            )
        ''')
        
        # Таблица статистики
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                stat_type TEXT NOT NULL,
                stat_name TEXT NOT NULL,
                stat_value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES game_sessions (id)
            )
        ''')
        
        conn.commit()
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Создает индексы для оптимизации запросов."""
        cursor = conn.cursor()
        
        # Индексы для предметов
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_type ON items(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_level ON items(level_requirement)')
        
        # Индексы для врагов
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enemies_type ON enemies(enemy_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enemies_level ON enemies(level)')
        
        # Индексы для эффектов
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_effects_type ON effects(effect_type)')
        
        # Индексы для способностей
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_abilities_type ON abilities(ability_type)')
        
        # Индексы для статистики
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_session ON statistics(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_type ON statistics(stat_type)')
        
        conn.commit()
    
    def insert_item(self, item_data: Dict[str, Any]) -> bool:
        """Добавляет предмет в базу данных."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Подготовка данных
                    item_data['effects'] = json.dumps(item_data.get('effects', []))
                    item_data['modifiers'] = json.dumps(item_data.get('modifiers', {}))
                    item_data['tags'] = json.dumps(item_data.get('tags', []))
                    item_data['resist_mod'] = json.dumps(item_data.get('resist_mod', {}))
                    item_data['weakness_mod'] = json.dumps(item_data.get('weakness_mod', {}))
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO items 
                        (id, name, description, type, slot, rarity, level_requirement,
                         base_damage, attack_speed, damage_type, element, element_damage,
                         defense, weight, durability, max_durability, cost, effects,
                         modifiers, tags, resist_mod, weakness_mod, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (
                        item_data['id'], item_data['name'], item_data.get('description', ''),
                        item_data['type'], item_data.get('slot'), item_data['rarity'],
                        item_data.get('level_requirement', 1), item_data.get('base_damage', 0),
                        item_data.get('attack_speed', 1.0), item_data.get('damage_type'),
                        item_data.get('element'), item_data.get('element_damage', 0),
                        item_data.get('defense', 0), item_data.get('weight', 0),
                        item_data.get('durability', 100), item_data.get('max_durability', 100),
                        item_data.get('cost', 0), item_data['effects'], item_data['modifiers'],
                        item_data['tags'], item_data['resist_mod'], item_data['weakness_mod']
                    ))
                    
                    conn.commit()
                    logger.debug(f"Предмет {item_data['id']} добавлен в БД")
                    return True
                    
        except Exception as e:
            logger.error(f"Ошибка добавления предмета: {e}")
            return False
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Получает предмет из базы данных."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        columns = [description[0] for description in cursor.description]
                        item_data = dict(zip(columns, row))
                        
                        # Преобразование JSON полей обратно в Python объекты
                        item_data['effects'] = json.loads(item_data['effects'])
                        item_data['modifiers'] = json.loads(item_data['modifiers'])
                        item_data['tags'] = json.loads(item_data['tags'])
                        item_data['resist_mod'] = json.loads(item_data['resist_mod'])
                        item_data['weakness_mod'] = json.loads(item_data['weakness_mod'])
                        
                        return item_data
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка получения предмета: {e}")
            return None
    
    def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Получает все предметы определенного типа."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM items WHERE type = ?', (item_type,))
                    rows = cursor.fetchall()
                    
                    items = []
                    columns = [description[0] for description in cursor.description]
                    
                    for row in rows:
                        item_data = dict(zip(columns, row))
                        item_data['effects'] = json.loads(item_data['effects'])
                        item_data['modifiers'] = json.loads(item_data['modifiers'])
                        item_data['tags'] = json.loads(item_data['tags'])
                        item_data['resist_mod'] = json.loads(item_data['resist_mod'])
                        item_data['weakness_mod'] = json.loads(item_data['weakness_mod'])
                        items.append(item_data)
                    
                    return items
                    
        except Exception as e:
            logger.error(f"Ошибка получения предметов по типу: {e}")
            return []
    
    def insert_enemy(self, enemy_data: Dict[str, Any]) -> bool:
        """Добавляет врага в базу данных."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Подготовка данных
                    enemy_data['attributes'] = json.dumps(enemy_data.get('attributes', {}))
                    enemy_data['combat_stats'] = json.dumps(enemy_data.get('combat_stats', {}))
                    enemy_data['loot_table'] = json.dumps(enemy_data.get('loot_table', []))
                    enemy_data['skills'] = json.dumps(enemy_data.get('skills', []))
                    enemy_data['tags'] = json.dumps(enemy_data.get('tags', []))
                    enemy_data['phases'] = json.dumps(enemy_data.get('phases', []))
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO enemies 
                        (id, name, description, enemy_type, level, experience_reward,
                         attributes, combat_stats, ai_behavior, loot_table, skills,
                         tags, phases, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (
                        enemy_data['id'], enemy_data['name'], enemy_data.get('description', ''),
                        enemy_data['enemy_type'], enemy_data.get('level', 1),
                        enemy_data.get('experience_reward', 10), enemy_data['attributes'],
                        enemy_data['combat_stats'], enemy_data.get('ai_behavior'),
                        enemy_data['loot_table'], enemy_data['skills'], enemy_data['tags'],
                        enemy_data['phases']
                    ))
                    
                    conn.commit()
                    logger.debug(f"Враг {enemy_data['id']} добавлен в БД")
                    return True
                    
        except Exception as e:
            logger.error(f"Ошибка добавления врага: {e}")
            return False
    
    def get_enemy(self, enemy_id: str) -> Optional[Dict[str, Any]]:
        """Получает врага из базы данных."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM enemies WHERE id = ?', (enemy_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        columns = [description[0] for description in cursor.description]
                        enemy_data = dict(zip(columns, row))
                        
                        # Преобразование JSON полей
                        enemy_data['attributes'] = json.loads(enemy_data['attributes'])
                        enemy_data['combat_stats'] = json.loads(enemy_data['combat_stats'])
                        enemy_data['loot_table'] = json.loads(enemy_data['loot_table'])
                        enemy_data['skills'] = json.loads(enemy_data['skills'])
                        enemy_data['tags'] = json.loads(enemy_data['tags'])
                        enemy_data['phases'] = json.loads(enemy_data['phases'])
                        
                        return enemy_data
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка получения врага: {e}")
            return None
    
    def get_enemies_by_type(self, enemy_type: str) -> List[Dict[str, Any]]:
        """Получает всех врагов определенного типа."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM enemies WHERE enemy_type = ?', (enemy_type,))
                    rows = cursor.fetchall()
                    
                    enemies = []
                    columns = [description[0] for description in cursor.description]
                    
                    for row in rows:
                        enemy_data = dict(zip(columns, row))
                        enemy_data['attributes'] = json.loads(enemy_data['attributes'])
                        enemy_data['combat_stats'] = json.loads(enemy_data['combat_stats'])
                        enemy_data['loot_table'] = json.loads(enemy_data['loot_table'])
                        enemy_data['skills'] = json.loads(enemy_data['skills'])
                        enemy_data['tags'] = json.loads(enemy_data['tags'])
                        enemy_data['phases'] = json.loads(enemy_data['phases'])
                        enemies.append(enemy_data)
                    
                    return enemies
                    
        except Exception as e:
            logger.error(f"Ошибка получения врагов по типу: {e}")
            return []
    
    def save_game_session(self, session_data: Dict[str, Any]) -> int:
        """Сохраняет игровую сессию."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO game_sessions 
                        (session_name, player_data, game_state, difficulty, score, achievements)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        session_data['session_name'],
                        json.dumps(session_data.get('player_data', {})),
                        json.dumps(session_data.get('game_state', {})),
                        session_data.get('difficulty', 'normal'),
                        session_data.get('score', 0),
                        json.dumps(session_data.get('achievements', []))
                    ))
                    
                    session_id = cursor.lastrowid
                    conn.commit()
                    logger.info(f"Игровая сессия {session_id} сохранена")
                    return session_id
                    
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")
            return -1
    
    def load_game_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Загружает игровую сессию."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM game_sessions WHERE id = ?', (session_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        columns = [description[0] for description in cursor.description]
                        session_data = dict(zip(columns, row))
                        
                        session_data['player_data'] = json.loads(session_data['player_data'])
                        session_data['game_state'] = json.loads(session_data['game_state'])
                        session_data['achievements'] = json.loads(session_data['achievements'])
                        
                        return session_data
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {e}")
            return None
    
    def add_statistic(self, session_id: int, stat_type: str, stat_name: str, stat_value: float):
        """Добавляет статистику."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO statistics (session_id, stat_type, stat_name, stat_value)
                        VALUES (?, ?, ?, ?)
                    ''', (session_id, stat_type, stat_name, stat_value))
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Ошибка добавления статистики: {e}")
    
    def get_statistics(self, session_id: int, stat_type: str = None) -> List[Dict[str, Any]]:
        """Получает статистику для сессии."""
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    if stat_type:
                        cursor.execute('''
                            SELECT * FROM statistics 
                            WHERE session_id = ? AND stat_type = ?
                            ORDER BY timestamp
                        ''', (session_id, stat_type))
                    else:
                        cursor.execute('''
                            SELECT * FROM statistics 
                            WHERE session_id = ?
                            ORDER BY timestamp
                        ''', (session_id,))
                    
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    
                    return [dict(zip(columns, row)) for row in rows]
                    
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return []
    
    def import_from_json(self, json_file: str, table_name: str):
        """Импортирует данные из JSON файла в базу данных."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if table_name == 'items' and 'items' in data:
                for item_id, item_data in data['items'].items():
                    item_data['id'] = item_id
                    self.insert_item(item_data)
            
            elif table_name == 'enemies' and 'entities' in data:
                for entity_id, entity_data in data['entities'].items():
                    if entity_data.get('type') in ['enemy', 'boss']:
                        entity_data['id'] = entity_id
                        self.insert_enemy(entity_data)
            
            logger.info(f"Данные из {json_file} импортированы в таблицу {table_name}")
            
        except Exception as e:
            logger.error(f"Ошибка импорта из {json_file}: {e}")
    
    def export_to_json(self, table_name: str, output_file: str):
        """Экспортирует данные из базы данных в JSON файл."""
        try:
            data = {}
            
            if table_name == 'items':
                items = self.get_items_by_type('weapon') + self.get_items_by_type('armor') + \
                       self.get_items_by_type('consumable') + self.get_items_by_type('accessory')
                data['items'] = {item['id']: item for item in items}
            
            elif table_name == 'enemies':
                enemies = self.get_enemies_by_type('warrior') + self.get_enemies_by_type('archer') + \
                         self.get_enemies_by_type('mage')
                data['entities'] = {enemy['id']: enemy for enemy in enemies}
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Данные из таблицы {table_name} экспортированы в {output_file}")
            
        except Exception as e:
            logger.error(f"Ошибка экспорта в {output_file}: {e}")


# Глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager()
