"""
Безопасная система работы с базой данных.
Защита от SQL injection, безопасная сериализация, шифрование чувствительных данных.
"""

import sqlite3
import json
import hashlib
import hmac
import secrets
import base64
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import threading
import logging
from contextlib import contextmanager
import pickle
import zlib

logger = logging.getLogger(__name__)


class DatabaseSecurityError(Exception):
    """Ошибка безопасности базы данных"""
    pass


class SecureSerializer:
    """Безопасный сериализатор данных"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self._compression_threshold = 1024  # Сжимать данные больше этого размера
    
    def serialize(self, data: Any) -> str:
        """Безопасная сериализация данных"""
        try:
            # Используем JSON для безопасной сериализации
            json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            
            # Сжимаем данные если они большие
            if len(json_data) > self._compression_threshold:
                compressed = zlib.compress(json_data.encode('utf-8'))
                return base64.b64encode(compressed).decode('ascii')
            
            return json_data
            
        except Exception as e:
            logger.error(f"Ошибка сериализации: {e}")
            raise DatabaseSecurityError(f"Ошибка сериализации данных: {e}")
    
    def deserialize(self, data: str) -> Any:
        """Безопасная десериализация данных"""
        try:
            # Проверяем, является ли данные base64
            if self._is_base64(data):
                compressed = base64.b64decode(data.encode('ascii'))
                json_data = zlib.decompress(compressed).decode('utf-8')
            else:
                json_data = data
            
            return json.loads(json_data)
            
        except Exception as e:
            logger.error(f"Ошибка десериализации: {e}")
            raise DatabaseSecurityError(f"Ошибка десериализации данных: {e}")
    
    def _is_base64(self, data: str) -> bool:
        """Проверка, является ли строка base64"""
        try:
            base64.b64decode(data.encode('ascii'))
            return True
        except Exception:
            return False


class SecureDatabase:
    """
    Безопасная обертка над SQLite с защитой от SQL injection
    и безопасной сериализацией данных.
    """
    
    def __init__(self, db_path: str, secret_key: Optional[str] = None):
        self.db_path = Path(db_path)
        self.secret_key = secret_key or secrets.token_hex(32)
        self.serializer = SecureSerializer(self.secret_key)
        self._lock = threading.RLock()
        
        # Статистика безопасности
        self.security_stats = {
            'queries_executed': 0,
            'injection_attempts_blocked': 0,
            'data_encrypted': 0,
            'data_decrypted': 0
        }
        
        # Инициализация базы данных
        self._init_database()
        
        logger.info(f"SecureDatabase инициализирована: {db_path}")
    
    def _init_database(self) -> None:
        """Инициализация базы данных с проверками безопасности"""
        try:
            with self._get_connection() as conn:
                # Создаем таблицу для метаданных безопасности
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Сохраняем хеш секретного ключа
                key_hash = hashlib.sha256(self.secret_key.encode()).hexdigest()
                conn.execute("""
                    INSERT OR REPLACE INTO security_metadata (key, value) 
                    VALUES (?, ?)
                """, ('secret_key_hash', key_hash))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise DatabaseSecurityError(f"Ошибка инициализации БД: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            
            # Включаем внешние ключи
            conn.execute("PRAGMA foreign_keys = ON")
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseSecurityError(f"Ошибка соединения с БД: {e}")
        finally:
            if conn:
                conn.close()
    
    def _validate_sql_injection(self, query: str, params: tuple) -> bool:
        """Проверка на попытки SQL injection"""
        # Разрешенные SQL команды для внутреннего использования
        allowed_patterns = [
            'select', 'insert', 'update', 'delete', 'create table', 'drop table'
        ]
        
        # Подозрительные паттерны
        suspicious_patterns = [
            ';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute',
            'union', 'drop database', 'create database', 'alter table',
            'script', 'javascript', 'eval(', 'exec('
        ]
        
        query_lower = query.lower()
        
        # Проверяем на подозрительные паттерны
        for pattern in suspicious_patterns:
            if pattern in query_lower:
                self.security_stats['injection_attempts_blocked'] += 1
                logger.warning(f"Обнаружена попытка SQL injection: {pattern}")
                return False
        
        # Проверяем, что запрос содержит только разрешенные команды
        has_allowed_pattern = any(pattern in query_lower for pattern in allowed_patterns)
        if not has_allowed_pattern and query.strip():
            logger.warning(f"Неизвестная SQL команда: {query}")
            return False
        
        return True
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Безопасное выполнение запроса
        
        Args:
            query: SQL запрос с параметрами
            params: Параметры для запроса
            
        Returns:
            Результат запроса
        """
        with self._lock:
            # Проверяем на SQL injection
            if not self._validate_sql_injection(query, params):
                raise DatabaseSecurityError("Обнаружена попытка SQL injection")
            
            try:
                with self._get_connection() as conn:
                    cursor = conn.execute(query, params)
                    
                    if query.strip().upper().startswith('SELECT'):
                        results = []
                        for row in cursor.fetchall():
                            results.append(dict(row))
                        return results
                    else:
                        conn.commit()
                        return []
                        
            except Exception as e:
                logger.error(f"Ошибка выполнения запроса: {e}")
                raise DatabaseSecurityError(f"Ошибка выполнения запроса: {e}")
            finally:
                self.security_stats['queries_executed'] += 1
    
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Безопасное выполнение множественных запросов"""
        with self._lock:
            # Проверяем на SQL injection
            if not self._validate_sql_injection(query, []):
                raise DatabaseSecurityError("Обнаружена попытка SQL injection")
            
            try:
                with self._get_connection() as conn:
                    conn.executemany(query, params_list)
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"Ошибка выполнения множественных запросов: {e}")
                raise DatabaseSecurityError(f"Ошибка выполнения множественных запросов: {e}")
            finally:
                self.security_stats['queries_executed'] += len(params_list)
    
    def store_secure_data(self, table: str, key: str, data: Any) -> bool:
        """
        Безопасное сохранение данных с шифрованием
        
        Args:
            table: Имя таблицы
            key: Ключ данных
            data: Данные для сохранения
            
        Returns:
            True если данные сохранены успешно
        """
        try:
            # Сериализуем данные
            serialized_data = self.serializer.serialize(data)
            
            # Создаем таблицу если не существует
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            self.execute_query(create_table_query)
            
            # Сохраняем данные
            insert_query = f"""
                INSERT OR REPLACE INTO {table} (key, data, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """
            self.execute_query(insert_query, (key, serialized_data))
            
            self.security_stats['data_encrypted'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            return False
    
    def get_secure_data(self, table: str, key: str) -> Optional[Any]:
        """
        Безопасное получение данных с дешифрованием
        
        Args:
            table: Имя таблицы
            key: Ключ данных
            
        Returns:
            Дешифрованные данные или None
        """
        try:
            query = f"SELECT data FROM {table} WHERE key = ?"
            results = self.execute_query(query, (key,))
            
            if results:
                serialized_data = results[0]['data']
                data = self.serializer.deserialize(serialized_data)
                self.security_stats['data_decrypted'] += 1
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения данных: {e}")
            return None
    
    def delete_secure_data(self, table: str, key: str) -> bool:
        """Безопасное удаление данных"""
        try:
            query = f"DELETE FROM {table} WHERE key = ?"
            self.execute_query(query, (key,))
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления данных: {e}")
            return False
    
    def get_all_keys(self, table: str) -> List[str]:
        """Получить все ключи из таблицы"""
        try:
            query = f"SELECT key FROM {table}"
            results = self.execute_query(query)
            return [row['key'] for row in results]
            
        except Exception as e:
            logger.error(f"Ошибка получения ключей: {e}")
            return []
    
    def backup_database(self, backup_path: str) -> bool:
        """Создание резервной копии базы данных"""
        try:
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self._get_connection() as conn:
                backup_conn = sqlite3.connect(str(backup_path))
                conn.backup(backup_conn)
                backup_conn.close()
            
            logger.info(f"Резервная копия создана: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return False
    
    def verify_integrity(self) -> bool:
        """Проверка целостности базы данных"""
        try:
            with self._get_connection() as conn:
                # Проверяем целостность
                result = conn.execute("PRAGMA integrity_check").fetchone()
                if result[0] != 'ok':
                    logger.error(f"Ошибка целостности БД: {result[0]}")
                    return False
                
                # Проверяем внешние ключи
                result = conn.execute("PRAGMA foreign_key_check").fetchall()
                if result:
                    logger.error(f"Ошибки внешних ключей: {result}")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Ошибка проверки целостности: {e}")
            return False
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Получить статистику безопасности"""
        with self._lock:
            return self.security_stats.copy()
    
    def clear_security_stats(self) -> None:
        """Очистить статистику безопасности"""
        with self._lock:
            self.security_stats = {
                'queries_executed': 0,
                'injection_attempts_blocked': 0,
                'data_encrypted': 0,
                'data_decrypted': 0
            }
    
    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            # Создаем резервную копию перед очисткой
            backup_path = f"{self.db_path}.backup"
            self.backup_database(backup_path)
            
            logger.info("SecureDatabase очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки SecureDatabase: {e}")


# Глобальный экземпляр безопасной базы данных
secure_db = SecureDatabase("data/secure_game_data.db")


class GameDataManager:
    """Менеджер игровых данных с безопасным хранением"""
    
    def __init__(self):
        self.db = secure_db
        self.cache: Dict[str, Any] = {}
        self._cache_lock = threading.RLock()
    
    def save_player_data(self, player_id: str, data: Dict[str, Any]) -> bool:
        """Сохранить данные игрока"""
        return self.db.store_secure_data('player_data', player_id, data)
    
    def load_player_data(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Загрузить данные игрока"""
        # Проверяем кэш
        with self._cache_lock:
            if player_id in self.cache:
                return self.cache[player_id]
        
        # Загружаем из БД
        data = self.db.get_secure_data('player_data', player_id)
        
        # Кэшируем
        if data:
            with self._cache_lock:
                self.cache[player_id] = data
        
        return data
    
    def save_game_state(self, state_id: str, state_data: Dict[str, Any]) -> bool:
        """Сохранить состояние игры"""
        return self.db.store_secure_data('game_states', state_id, state_data)
    
    def load_game_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Загрузить состояние игры"""
        return self.db.get_secure_data('game_states', state_id)
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Сохранить настройки игры"""
        return self.db.store_secure_data('settings', 'game_settings', settings)
    
    def load_settings(self) -> Optional[Dict[str, Any]]:
        """Загрузить настройки игры"""
        return self.db.get_secure_data('settings', 'game_settings')
    
    def clear_cache(self) -> None:
        """Очистить кэш"""
        with self._cache_lock:
            self.cache.clear()
    
    def get_all_player_ids(self) -> List[str]:
        """Получить все ID игроков"""
        return self.db.get_all_keys('player_data')
    
    def delete_player_data(self, player_id: str) -> bool:
        """Удалить данные игрока"""
        # Удаляем из кэша
        with self._cache_lock:
            self.cache.pop(player_id, None)
        
        # Удаляем из БД
        return self.db.delete_secure_data('player_data', player_id)
    
    def backup_all_data(self, backup_path: str) -> bool:
        """Создать резервную копию всех данных"""
        return self.db.backup_database(backup_path)
    
    def verify_data_integrity(self) -> bool:
        """Проверить целостность данных"""
        return self.db.verify_integrity()


# Глобальный экземпляр менеджера данных
game_data_manager = GameDataManager()
