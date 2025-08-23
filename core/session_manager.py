#!/usr/bin/env python3
"""
Оптимизированная система управления игровыми сессиями.
Управляет временными сессиями и сохранением контента в БД с оптимизацией производительности.
"""

import uuid
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import sqlite3
from pathlib import Path
import threading
import pickle
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


@dataclass  
class UserSession:
    """Пользовательская сессия с оптимизацией"""
    session_id: str
    user_id: str = "default"
    start_time: float = 0.0
    last_activity: float = 0.0
    is_active: bool = True
    session_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.session_data is None:
            self.session_data = {}
        if self.start_time == 0.0:
            self.start_time = time.time()
        if self.last_activity == 0.0:
            self.last_activity = time.time()
    
    def update_activity(self):
        """Обновление времени последней активности"""
        self.last_activity = time.time()
    
    def get_duration(self) -> float:
        """Получение длительности сессии"""
        return time.time() - self.start_time
    
    def is_expired(self, max_idle_time: float = 3600) -> bool:
        """Проверка истечения сессии"""
        return time.time() - self.last_activity > max_idle_time


@dataclass
class SessionData:
    """Данные игровой сессии с оптимизацией"""
    session_uuid: str
    slot_id: Optional[int] = None
    save_name: str = ""
    world_seed: int = 0
    player_data: Dict[str, Any] = None
    world_data: Dict[str, Any] = None
    inventory_data: Dict[str, Any] = None
    progress_data: Dict[str, Any] = None
    generation_seed: int = 0
    current_level: int = 1
    created_at: str = ""
    last_saved: str = ""
    state: str = "active"
    version: str = "1.0.0"
    checksum: str = ""
    
    def __post_init__(self):
        if self.player_data is None:
            self.player_data = {}
        if self.world_data is None:
            self.world_data = {}
        if self.inventory_data is None:
            self.inventory_data = {}
        if self.progress_data is None:
            self.progress_data = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_saved:
            self.last_saved = datetime.now().isoformat()
    
    def calculate_checksum(self) -> str:
        """Вычисление контрольной суммы данных"""
        try:
            data_str = json.dumps(self.to_dict(), sort_keys=True)
            return str(hash(data_str))[:16]
        except Exception:
            return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сериализации"""
        return asdict(self)
    
    def validate(self) -> bool:
        """Валидация данных сессии"""
        required_fields = ['session_uuid', 'save_name', 'world_seed']
        return all(hasattr(self, field) and getattr(self, field) for field in required_fields)


class SessionManager:
    """Оптимизированный менеджер игровых сессий"""
    
    def __init__(self, db_path: str = "data/game_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Текущая активная сессия
        self.current_session: Optional[SessionData] = None
        
        # Временное хранилище контента сессии (не в БД)
        self.session_content: Dict[str, List[Dict]] = {
            "items": [],
            "enemies": [],
            "skills": [],
            "genes": [],
            "accessories": []
        }
        
        # Кэш для оптимизации
        self._cache = {}
        self._cache_lock = threading.RLock()
        
        # Пул потоков для асинхронных операций
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Инициализация БД
        self._init_database()
        
        # Автоочистка устаревших сессий
        self._cleanup_timer = time.time()
        self._cleanup_interval = 300  # 5 минут
        
        logger.info("SessionManager инициализирован")
    
    def _init_database(self):
        """Инициализация базы данных с оптимизацией"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging для производительности
                conn.execute("PRAGMA synchronous=NORMAL")  # Оптимизация синхронизации
                conn.execute("PRAGMA cache_size=10000")  # Увеличение кэша
                conn.execute("PRAGMA temp_store=MEMORY")  # Временные таблицы в памяти
                
                # Создаем таблицы если их нет
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_uuid TEXT PRIMARY KEY,
                        slot_id INTEGER,
                        save_name TEXT NOT NULL,
                        world_seed INTEGER NOT NULL,
                        player_data BLOB,
                        world_data BLOB,
                        inventory_data BLOB,
                        progress_data BLOB,
                        generation_seed INTEGER,
                        current_level INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL,
                        last_saved TEXT NOT NULL,
                        state TEXT DEFAULT 'active',
                        version TEXT DEFAULT '1.0.0',
                        checksum TEXT,
                        UNIQUE(slot_id, save_name)
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_sessions_slot_name ON sessions(slot_id, save_name);
                    CREATE INDEX IF NOT EXISTS idx_sessions_state ON sessions(state);
                    CREATE INDEX IF NOT EXISTS idx_sessions_last_saved ON sessions(last_saved);
                """)
                
                conn.commit()
                logger.info("База данных сессий инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации БД сессий: {e}")
            raise
    
    def get_session_content(self, content_type: str) -> List[Dict[str, Any]]:
        """Получение контента сессии по типу"""
        try:
            if not self.current_session:
                logger.warning("Нет активной сессии")
                return []
            
            # Для временных сессий возвращаем базовый контент
            if content_type == "enemies":
                return [
                    {"name": "Гоблин", "type": "goblin", "level": 1},
                    {"name": "Орк", "type": "orc", "level": 2},
                    {"name": "Тролль", "type": "troll", "level": 3}
                ]
            elif content_type == "items":
                return [
                    {"name": "Зелье здоровья", "type": "potion", "effect": "heal"},
                    {"name": "Меч", "type": "weapon", "damage": 10}
                ]
            else:
                logger.warning(f"Неизвестный тип контента: {content_type}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка получения контента сессии: {e}")
            return []
    
    def create_temporary_session(self) -> Optional[SessionData]:
        """Создание временной сессии для новой игры"""
        try:
            # Создаем временную сессию с автоматическим именем
            temp_name = f"temp_session_{int(time.time())}"
            session_data = self.create_session(temp_name, slot_id=0)
            
            if session_data:
                logger.info("Временная сессия создана успешно")
                return session_data
            else:
                logger.error("Ошибка создания временной сессии")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка создания временной сессии: {e}")
            return None
    
    def create_session(self, save_name: str, slot_id: int = None, world_seed: int = None) -> Optional[SessionData]:
        """Создание новой игровой сессии с оптимизацией"""
        try:
            if world_seed is None:
                world_seed = int(time.time()) % 1000000
            
            session_data = SessionData(
                session_uuid=str(uuid.uuid4()),
                slot_id=slot_id,
                save_name=save_name,
                world_seed=world_seed,
                generation_seed=int(time.time())
            )
            
            # Вычисляем контрольную сумму
            session_data.checksum = session_data.calculate_checksum()
            
            # Валидируем данные
            if not session_data.validate():
                logger.error("Ошибка валидации данных сессии")
                return None
            
            # Сохраняем в БД
            if self._save_session_to_db(session_data):
                self.current_session = session_data
                logger.info(f"Создана новая сессия: {save_name} (slot: {slot_id})")
                return session_data
            else:
                logger.error("Ошибка сохранения сессии в БД")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка создания сессии: {e}")
            return None
    
    def load_session(self, save_name: str, slot_id: int = None) -> Optional[SessionData]:
        """Загрузка существующей сессии с оптимизацией"""
        try:
            # Проверяем кэш
            cache_key = f"{slot_id}_{save_name}"
            with self._cache_lock:
                if cache_key in self._cache:
                    cached_data = self._cache[cache_key]
                    if time.time() - cached_data.get('timestamp', 0) < 300:  # 5 минут
                        logger.info(f"Сессия загружена из кэша: {save_name}")
                        return cached_data['data']
            
            # Загружаем из БД
            session_data = self._load_session_from_db(save_name, slot_id)
            if session_data:
                # Проверяем контрольную сумму
                current_checksum = session_data.calculate_checksum()
                if session_data.checksum and session_data.checksum != current_checksum:
                    logger.warning(f"Контрольная сумма сессии не совпадает: {save_name}")
                
                # Кэшируем данные
                with self._cache_lock:
                    self._cache[cache_key] = {
                        'data': session_data,
                        'timestamp': time.time()
                    }
                
                self.current_session = session_data
                logger.info(f"Сессия загружена: {save_name}")
                return session_data
            else:
                logger.warning(f"Сессия не найдена: {save_name}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {e}")
            return None
    
    def save_session(self, session_data: SessionData = None) -> bool:
        """Сохранение сессии с оптимизацией"""
        try:
            if session_data is None:
                session_data = self.current_session
            
            if not session_data:
                logger.error("Нет данных сессии для сохранения")
                return False
            
            # Обновляем время последнего сохранения
            session_data.last_saved = datetime.now().isoformat()
            session_data.checksum = session_data.calculate_checksum()
            
            # Валидируем данные
            if not session_data.validate():
                logger.error("Ошибка валидации данных сессии")
                return False
            
            # Сохраняем в БД
            if self._save_session_to_db(session_data):
                # Обновляем кэш
                cache_key = f"{session_data.slot_id}_{session_data.save_name}"
                with self._cache_lock:
                    self._cache[cache_key] = {
                        'data': session_data,
                        'timestamp': time.time()
                    }
                
                logger.info(f"Сессия сохранена: {session_data.save_name}")
                return True
            else:
                logger.error("Ошибка сохранения сессии в БД")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")
            return False
    
    def _save_session_to_db(self, session_data: SessionData) -> bool:
        """Сохранение сессии в БД с оптимизацией"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Сжимаем и сериализуем данные
                compressed_data = self._compress_session_data(session_data)
                
                conn.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (session_uuid, slot_id, save_name, world_seed, player_data, world_data, 
                     inventory_data, progress_data, generation_seed, current_level, 
                     created_at, last_saved, state, version, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_data.session_uuid,
                    session_data.slot_id,
                    session_data.save_name,
                    session_data.world_seed,
                    compressed_data.get('player_data'),
                    compressed_data.get('world_data'),
                    compressed_data.get('inventory_data'),
                    compressed_data.get('progress_data'),
                    session_data.generation_seed,
                    session_data.current_level,
                    session_data.created_at,
                    session_data.last_saved,
                    session_data.state,
                    session_data.version,
                    session_data.checksum
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии в БД: {e}")
            return False
    
    def _load_session_from_db(self, save_name: str, slot_id: int = None) -> Optional[SessionData]:
        """Загрузка сессии из БД с оптимизацией"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                if slot_id is not None:
                    cursor = conn.execute("""
                        SELECT * FROM sessions 
                        WHERE save_name = ? AND slot_id = ?
                    """, (save_name, slot_id))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM sessions 
                        WHERE save_name = ?
                    """, (save_name,))
                
                row = cursor.fetchone()
                if row:
                    # Распаковываем данные
                    session_data = SessionData(
                        session_uuid=row[0],
                        slot_id=row[1],
                        save_name=row[2],
                        world_seed=row[3],
                        player_data=self._decompress_data(row[4]),
                        world_data=self._decompress_data(row[5]),
                        inventory_data=self._decompress_data(row[6]),
                        progress_data=self._decompress_data(row[7]),
                        generation_seed=row[8],
                        current_level=row[9],
                        created_at=row[10],
                        last_saved=row[11],
                        state=row[12],
                        version=row[13],
                        checksum=row[14]
                    )
                    return session_data
                
                return None
                
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии из БД: {e}")
            return None
    
    def _compress_session_data(self, session_data: SessionData) -> Dict[str, bytes]:
        """Сжатие данных сессии для оптимизации хранения"""
        try:
            compressed_data = {}
            
            # Сжимаем и сериализуем данные
            for data_type in ['player_data', 'world_data', 'inventory_data', 'progress_data']:
                data = getattr(session_data, data_type)
                if data:
                    # Сериализуем в pickle и сжимаем
                    serialized = pickle.dumps(data)
                    compressed = zlib.compress(serialized, level=6)  # Оптимальный уровень сжатия
                    compressed_data[data_type] = compressed
                else:
                    compressed_data[data_type] = None
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"Ошибка сжатия данных сессии: {e}")
            return {}
    
    def _decompress_data(self, compressed_data: bytes) -> Optional[Dict[str, Any]]:
        """Распаковка сжатых данных сессии"""
        try:
            if compressed_data is None:
                return None
            
            # Распаковываем и десериализуем
            decompressed = zlib.decompress(compressed_data)
            data = pickle.loads(decompressed)
            return data
            
        except Exception as e:
            logger.error(f"Ошибка распаковки данных: {e}")
            return None
    
    def get_save_slots(self) -> List[Dict[str, Any]]:
        """Получение списка слотов сохранений с оптимизацией"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("""
                    SELECT slot_id, save_name, last_saved, current_level, world_seed
                    FROM sessions 
                    WHERE state = 'active'
                    ORDER BY slot_id, last_saved DESC
                """)
                
                slots = []
                for row in cursor.fetchall():
                    slots.append({
                        'slot_id': row[0],
                        'save_name': row[1],
                        'last_saved': row[2],
                        'current_level': row[3],
                        'world_seed': row[4]
                    })
                
                return slots
                
        except Exception as e:
            logger.error(f"Ошибка получения слотов сохранений: {e}")
            return []
    
    def delete_session(self, save_name: str, slot_id: int = None) -> bool:
        """Удаление сессии с оптимизацией"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                if slot_id is not None:
                    conn.execute("""
                        DELETE FROM sessions 
                        WHERE save_name = ? AND slot_id = ?
                    """, (save_name, slot_id))
                else:
                    conn.execute("""
                        DELETE FROM sessions 
                        WHERE save_name = ?
                    """, (save_name,))
                
                conn.commit()
                
                # Удаляем из кэша
                cache_key = f"{slot_id}_{save_name}"
                with self._cache_lock:
                    if cache_key in self._cache:
                        del self._cache[cache_key]
                
                logger.info(f"Сессия удалена: {save_name}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка удаления сессии: {e}")
            return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Очистка устаревших сессий"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            with sqlite3.connect(str(self.db_path)) as conn:
                # Находим устаревшие сессии
                cursor = conn.execute("""
                    SELECT session_uuid, save_name, slot_id FROM sessions 
                    WHERE (julianday('now') - julianday(last_saved)) * 24 > ?
                """, (max_age_hours,))
                
                expired_sessions = cursor.fetchall()
                deleted_count = 0
                
                for session in expired_sessions:
                    session_uuid, save_name, slot_id = session
                    
                    # Удаляем сессию
                    conn.execute("DELETE FROM sessions WHERE session_uuid = ?", (session_uuid,))
                    
                    # Удаляем из кэша
                    cache_key = f"{slot_id}_{save_name}"
                    with self._cache_lock:
                        if cache_key in self._cache:
                            del self._cache[cache_key]
                    
                    deleted_count += 1
                
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Удалено {deleted_count} устаревших сессий")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Ошибка очистки устаревших сессий: {e}")
            return 0
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Получение статистики сессий"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Общее количество сессий
                total_sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
                
                # Активные сессии
                active_sessions = conn.execute("SELECT COUNT(*) FROM sessions WHERE state = 'active'").fetchone()[0]
                
                # Размер БД
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                # Статистика кэша
                with self._cache_lock:
                    cache_size = len(self._cache)
                    cache_hits = sum(1 for v in self._cache.values() if time.time() - v.get('timestamp', 0) < 300)
                
                return {
                    'total_sessions': total_sessions,
                    'active_sessions': active_sessions,
                    'db_size_mb': round(db_size / (1024 * 1024), 2),
                    'cache_size': cache_size,
                    'cache_hits': cache_hits,
                    'current_session': self.current_session.save_name if self.current_session else None
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики сессий: {e}")
            return {}
    
    def update(self, delta_time: float):
        """Обновление менеджера сессий"""
        current_time = time.time()
        
        # Автоочистка устаревших сессий
        if current_time - self._cleanup_timer >= self._cleanup_interval:
            self.cleanup_expired_sessions()
            self._cleanup_timer = current_time
        
        # Очистка устаревшего кэша
        with self._cache_lock:
            current_time = time.time()
            expired_keys = [
                k for k, v in self._cache.items() 
                if current_time - v.get('timestamp', 0) > 600  # 10 минут
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            # Закрываем пул потоков
            self._executor.shutdown(wait=True)
            
            # Очищаем кэш
            with self._cache_lock:
                self._cache.clear()
            
            logger.info("SessionManager очищен")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке SessionManager: {e}")
    
    def __del__(self):
        """Деструктор для автоматической очистки"""
        self.cleanup()
