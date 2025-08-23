"""
Оптимизированный менеджер доступа к SQLite БД контента игры.
Обеспечивает минимально необходимые методы для DataManager с оптимизацией производительности.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import threading
import logging
import time
from contextlib import contextmanager
import json

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Оптимизированная обёртка над SQLite для чтения данных игры."""

    def __init__(self, db_path: str = "data/game_data.db"):
        self.db_path = Path(db_path)
        self._lock = threading.RLock()
        self._connection_pool = {}
        self._max_connections = 5
        self._connection_timeout = 30  # секунды
        
        # Кэш для оптимизации
        self._cache = {}
        self._cache_lock = threading.RLock()
        self._cache_ttl = 300  # 5 минут
        
        # Статистика производительности
        self._stats = {
            'queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0
        }
        
        # Инициализация БД
        self._init_database()
        
        logger.info(f"DatabaseManager инициализирован: {self.db_path}")

    def _init_database(self):
        """Инициализация базы данных с оптимизацией"""
        try:
            with self._get_connection() as conn:
                # Оптимизация SQLite
                conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                conn.execute("PRAGMA synchronous=NORMAL")  # Оптимизация синхронизации
                conn.execute("PRAGMA cache_size=10000")  # Увеличение кэша
                conn.execute("PRAGMA temp_store=MEMORY")  # Временные таблицы в памяти
                conn.execute("PRAGMA mmap_size=268435456")  # 256MB для mmap
                conn.execute("PRAGMA optimize")  # Автооптимизация
                
                # Создаем индексы для производительности
                self._create_indexes(conn)
                
                logger.info("База данных оптимизирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise

    def _create_indexes(self, conn: sqlite3.Connection):
        """Создание индексов для оптимизации запросов"""
        try:
            # Индексы для таблицы effects
            conn.execute("CREATE INDEX IF NOT EXISTS idx_effects_type ON effects(effect_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_effects_category ON effects(attribute)")
            
            # Индексы для таблицы items
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_level ON items(level_requirement)")
            
            # Индексы для таблицы enemies
            conn.execute("CREATE INDEX IF NOT EXISTS idx_enemies_type ON enemies(enemy_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_enemies_biome ON enemies(biome)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_enemies_level ON enemies(level)")
            
            # Индексы для таблицы skills
            conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_type ON skills(skill_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_element ON skills(element)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_level ON skills(level_requirement)")
            
            conn.commit()
            logger.info("Индексы созданы")
            
        except Exception as e:
            logger.warning(f"Ошибка создания индексов: {e}")

    @contextmanager
    def _get_connection(self):
        """Получение соединения с БД с пулом соединений"""
        conn = None
        try:
            conn = self._get_cached_connection()
            if not conn:
                conn = sqlite3.connect(str(self.db_path), timeout=20.0)
                conn.row_factory = sqlite3.Row
                
                # Применяем оптимизации для нового соединения
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA cache_size=10000")
                conn.execute("PRAGMA temp_store=MEMORY")
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Ошибка работы с БД: {e}")
            raise
        finally:
            if conn:
                self._return_connection(conn)

    def _get_cached_connection(self) -> Optional[sqlite3.Connection]:
        """Получение соединения из пула"""
        current_time = time.time()
        
        with self._lock:
            # Очищаем устаревшие соединения
            expired_keys = [
                k for k, v in self._connection_pool.items()
                if current_time - v['last_used'] > self._connection_timeout
            ]
            for key in expired_keys:
                try:
                    self._connection_pool[key]['connection'].close()
                except Exception:
                    pass
                del self._connection_pool[key]
            
            # Ищем свободное соединение
            for conn_data in self._connection_pool.values():
                if not conn_data['in_use']:
                    conn_data['in_use'] = True
                    conn_data['last_used'] = current_time
                    return conn_data['connection']
            
            # Создаем новое соединение если есть место
            if len(self._connection_pool) < self._max_connections:
                conn = sqlite3.connect(str(self.db_path), timeout=20.0)
                conn.row_factory = sqlite3.Row
                
                conn_id = id(conn)
                self._connection_pool[conn_id] = {
                    'connection': conn,
                    'in_use': True,
                    'last_used': current_time
                }
                
                return conn
        
        return None

    def _return_connection(self, conn: sqlite3.Connection):
        """Возврат соединения в пул"""
        with self._lock:
            for conn_data in self._connection_pool.values():
                if conn_data['connection'] == conn:
                    conn_data['in_use'] = False
                    break

    def _get_cache_key(self, table: str, params: Dict[str, Any] = None) -> str:
        """Генерация ключа кэша"""
        if params:
            param_str = json.dumps(params, sort_keys=True)
            return f"{table}:{param_str}"
        return table

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        with self._cache_lock:
            if cache_key in self._cache:
                cache_data = self._cache[cache_key]
                if time.time() - cache_data['timestamp'] < self._cache_ttl:
                    self._stats['cache_hits'] += 1
                    return cache_data['data']
                else:
                    del self._cache[cache_key]
        
        self._stats['cache_misses'] += 1
        return None

    def _set_cache(self, cache_key: str, data: Any):
        """Установка данных в кэш"""
        with self._cache_lock:
            self._cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }

    def _execute_query(self, query: str, params: Tuple = None, cache_key: str = None) -> List[sqlite3.Row]:
        """Выполнение запроса с оптимизацией"""
        start_time = time.time()
        
        try:
            # Проверяем кэш
            if cache_key:
                cached_result = self._get_from_cache(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Выполняем запрос
            with self._get_connection() as conn:
                cursor = conn.execute(query, params or ())
                result = cursor.fetchall()
                
                # Кэшируем результат
                if cache_key and result:
                    self._set_cache(cache_key, result)
                
                # Обновляем статистику
                self._stats['queries'] += 1
                self._stats['total_time'] += time.time() - start_time
                
                return result
                
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    # ---- Effects ----
    def get_effects(self, effect_type: str = None, category: str = None) -> Dict[str, Dict[str, Any]]:
        """Получение эффектов с фильтрацией и кэшированием"""
        try:
            cache_key = f"effects:{effect_type or 'all'}:{category or 'all'}"
            
            if effect_type and category:
                query = "SELECT * FROM effects WHERE effect_type = ? AND attribute = ?"
                params = (effect_type, category)
            elif effect_type:
                query = "SELECT * FROM effects WHERE effect_type = ?"
                params = (effect_type,)
            elif category:
                query = "SELECT * FROM effects WHERE attribute = ?"
                params = (category,)
            else:
                query = "SELECT * FROM effects"
                params = ()
            
            rows = self._execute_query(query, params, cache_key)
            
            result = {}
            for row in rows:
                effect_id = row["code"]
                result[effect_id] = {
                    "id": effect_id,
                    "name": row["name"],
                    "description": row["description"],
                    "type": row["effect_type"],
                    "category": row["attribute"],
                    "duration": row["duration"],
                    "tick_interval": row["tick_interval"],
                    "max_stacks": row["max_stacks"],
                    "stackable": (row["max_stacks"] or 1) > 1,
                    "modifiers": {},
                    "hex_id": row["guid"],
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка чтения effects: {e}")
            return {}

    # ---- Items ----
    def get_items(self, item_type: str = None, rarity: str = None, level_min: int = None) -> Dict[str, Dict[str, Any]]:
        """Получение предметов с фильтрацией и кэшированием"""
        try:
            cache_key = f"items:{item_type or 'all'}:{rarity or 'all'}:{level_min or 'all'}"
            
            query_parts = ["SELECT * FROM items"]
            params = []
            
            if item_type or rarity or level_min:
                query_parts.append("WHERE")
                conditions = []
                
                if item_type:
                    conditions.append("item_type = ?")
                    params.append(item_type)
                
                if rarity:
                    conditions.append("rarity = ?")
                    params.append(rarity)
                
                if level_min:
                    conditions.append("level_requirement >= ?")
                    params.append(level_min)
                
                query_parts.append(" AND ".join(conditions))
            
            query = " ".join(query_parts)
            rows = self._execute_query(query, tuple(params), cache_key)
            
            result = {}
            for row in rows:
                item_id = row["item_id"]
                result[item_id] = {
                    "id": item_id,
                    "name": row["name"],
                    "description": row["description"],
                    "type": row["item_type"],
                    "slot": None,
                    "rarity": row["rarity"],
                    "level_requirement": 1,
                    "base_damage": 0.0,
                    "attack_speed": 1.0,
                    "damage_type": None,
                    "element": None,
                    "element_damage": 0.0,
                    "defense": 0.0,
                    "weight": row["weight"],
                    "durability": 100,
                    "max_durability": 100,
                    "cost": row["value"],
                    "range": 0.0,
                    "effects": [],
                    "modifiers": {},
                    "tags": [],
                    "resist_mod": {},
                    "weakness_mod": {},
                    "hex_id": None,
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка чтения items: {e}")
            return {}

    # ---- Enemies ----
    def get_enemies(self, enemy_type: str = None, biome: str = None, level_min: int = None, level_max: int = None) -> Dict[str, Dict[str, Any]]:
        """Получение врагов с фильтрацией и кэшированием"""
        try:
            cache_key = f"enemies:{enemy_type or 'all'}:{biome or 'all'}:{level_min or 'all'}:{level_max or 'all'}"
            
            query_parts = ["SELECT * FROM enemies"]
            params = []
            
            if enemy_type or biome or level_min or level_max:
                query_parts.append("WHERE")
                conditions = []
                
                if enemy_type:
                    conditions.append("enemy_type = ?")
                    params.append(enemy_type)
                
                if biome:
                    conditions.append("biome = ?")
                    params.append(biome)
                
                if level_min:
                    conditions.append("level >= ?")
                    params.append(level_min)
                
                if level_max:
                    conditions.append("level <= ?")
                    params.append(level_max)
                
                query_parts.append(" AND ".join(conditions))
            
            query = " ".join(query_parts)
            rows = self._execute_query(query, tuple(params), cache_key)
            
            result = {}
            for row in rows:
                enemy_id = row["enemy_id"]
                result[enemy_id] = {
                    "id": enemy_id,
                    "name": row["name"],
                    "type": row["enemy_type"],
                    "biome": row["biome"],
                    "level": row["level"],
                    "health": row["health"],
                    "damage": row["damage"],
                    "defense": row["defense"],
                    "speed": row["speed"],
                    "abilities": [],
                    "drops": [],
                    "experience": row["experience"],
                    "hex_id": row["guid"],
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка чтения enemies: {e}")
            return {}

    # ---- Skills ----
    def get_skills(self, skill_type: str = None, element: str = None, level_min: int = None) -> Dict[str, Dict[str, Any]]:
        """Получение навыков с фильтрацией и кэшированием"""
        try:
            cache_key = f"skills:{skill_type or 'all'}:{element or 'all'}:{level_min or 'all'}"
            
            query_parts = ["SELECT * FROM skills"]
            params = []
            
            if skill_type or element or level_min:
                query_parts.append("WHERE")
                conditions = []
                
                if skill_type:
                    conditions.append("skill_type = ?")
                    params.append(skill_type)
                
                if element:
                    conditions.append("element = ?")
                    params.append(element)
                
                if level_min:
                    conditions.append("level_requirement >= ?")
                    params.append(level_min)
                
                query_parts.append(" AND ".join(conditions))
            
            query = " ".join(query_parts)
            rows = self._execute_query(query, tuple(params), cache_key)
            
            result = {}
            for row in rows:
                skill_id = row["skill_id"]
                result[skill_id] = {
                    "id": skill_id,
                    "name": row["name"],
                    "description": row["description"],
                    "type": row["skill_type"],
                    "element": row["element"],
                    "level_requirement": row["level_requirement"],
                    "mana_cost": row["mana_cost"],
                    "cooldown": row["cooldown"],
                    "damage": row["damage"],
                    "range": row["range"],
                    "effects": [],
                    "modifiers": {},
                    "hex_id": row["guid"],
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка чтения skills: {e}")
            return {}

    # ---- Genes ----
    def get_genes(self, gene_type: str = None, rarity: str = None) -> Dict[str, Dict[str, Any]]:
        """Получение генов с фильтрацией и кэшированием"""
        try:
            cache_key = f"genes:{gene_type or 'all'}:{rarity or 'all'}"
            
            query_parts = ["SELECT * FROM genes"]
            params = []
            
            if gene_type or rarity:
                query_parts.append("WHERE")
                conditions = []
                
                if gene_type:
                    conditions.append("gene_type = ?")
                    params.append(gene_type)
                
                if rarity:
                    conditions.append("rarity = ?")
                    params.append(rarity)
                
                query_parts.append(" AND ".join(conditions))
            
            query = " ".join(query_parts)
            rows = self._execute_query(query, tuple(params), cache_key)
            
            result = {}
            for row in rows:
                gene_id = row["gene_id"]
                result[gene_id] = {
                    "id": gene_id,
                    "name": row["name"],
                    "description": row["description"],
                    "type": row["gene_type"],
                    "rarity": row["rarity"],
                    "effects": [],
                    "modifiers": {},
                    "hex_id": row["guid"],
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка чтения genes: {e}")
            return {}

    # ---- Accessories ----
    def get_accessories(self, accessory_type: str = None, rarity: str = None) -> Dict[str, Dict[str, Any]]:
        """Получение аксессуаров с фильтрацией и кэшированием"""
        try:
            cache_key = f"accessories:{accessory_type or 'all'}:{rarity or 'all'}"
            
            query_parts = ["SELECT * FROM accessories"]
            params = []
            
            if accessory_type or rarity:
                query_parts.append("WHERE")
                conditions = []
                
                if accessory_type:
                    conditions.append("accessory_type = ?")
                    params.append(accessory_type)
                
                if rarity:
                    conditions.append("rarity = ?")
                    params.append(rarity)
                
                query_parts.append(" AND ".join(conditions))
            
            query = " ".join(query_parts)
            rows = self._execute_query(query, tuple(params), cache_key)
            
            result = {}
            for row in rows:
                accessory_id = row["accessory_id"]
                result[accessory_id] = {
                    "id": accessory_id,
                    "name": row["name"],
                    "description": row["description"],
                    "type": row["accessory_type"],
                    "rarity": row["rarity"],
                    "effects": [],
                    "modifiers": {},
                    "hex_id": row["guid"],
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка чтения accessories: {e}")
            return {}

    def get_database_info(self) -> Dict[str, Any]:
        """Получение информации о базе данных"""
        try:
            with self._get_connection() as conn:
                # Размер БД
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                # Количество записей в таблицах
                tables = ['effects', 'items', 'enemies', 'skills', 'genes', 'accessories']
                table_counts = {}
                
                for table in tables:
                    try:
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        table_counts[table] = count
                    except Exception:
                        table_counts[table] = 0
                
                # Статистика кэша
                with self._cache_lock:
                    cache_size = len(self._cache)
                    cache_keys = list(self._cache.keys())
                
                return {
                    'db_path': str(self.db_path),
                    'db_size_mb': round(db_size / (1024 * 1024), 2),
                    'table_counts': table_counts,
                    'cache_size': cache_size,
                    'cache_keys': cache_keys[:10],  # Первые 10 ключей
                    'performance_stats': self._stats.copy(),
                    'connection_pool_size': len(self._connection_pool)
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о БД: {e}")
            return {}

    def clear_cache(self):
        """Очистка кэша"""
        with self._cache_lock:
            self._cache.clear()
        logger.info("Кэш базы данных очищен")

    def optimize_database(self):
        """Оптимизация базы данных"""
        try:
            with self._get_connection() as conn:
                # Анализируем таблицы
                conn.execute("ANALYZE")
                
                # Оптимизируем
                conn.execute("PRAGMA optimize")
                
                # Перестраиваем индексы
                conn.execute("REINDEX")
                
                conn.commit()
                logger.info("База данных оптимизирована")
                
        except Exception as e:
            logger.error(f"Ошибка оптимизации БД: {e}")

    def cleanup(self):
        """Очистка ресурсов"""
        try:
            # Закрываем все соединения
            with self._lock:
                for conn_data in self._connection_pool.values():
                    try:
                        conn_data['connection'].close()
                    except Exception:
                        pass
                self._connection_pool.clear()
            
            # Очищаем кэш
            self.clear_cache()
            
            logger.info("DatabaseManager очищен")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке DatabaseManager: {e}")

    def __del__(self):
        """Деструктор для автоматической очистки"""
        self.cleanup()


# Глобальный экземпляр
database_manager = DatabaseManager()


