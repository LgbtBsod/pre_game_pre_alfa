"""
Система управления игровыми сессиями с поддержкой множественных слотов сохранения.
Обеспечивает изоляцию данных между сессиями и правильную генерацию контента.
"""

import uuid
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Состояния игровой сессии"""
    NEW = "new"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    SAVED = "saved"


@dataclass
class SaveSlot:
    """Слот сохранения"""
    slot_id: int
    session_uuid: str
    save_name: str
    created_at: datetime
    last_played: datetime
    player_level: int
    world_seed: int
    play_time: float
    is_active: bool = True


@dataclass
class SessionData:
    """Данные игровой сессии"""
    session_uuid: str
    slot_id: int
    state: SessionState
    created_at: datetime
    last_saved: datetime
    
    # Игровые данные
    player_data: Dict[str, Any] = field(default_factory=dict)
    world_data: Dict[str, Any] = field(default_factory=dict)
    inventory_data: Dict[str, Any] = field(default_factory=dict)
    progress_data: Dict[str, Any] = field(default_factory=dict)
    
    # Сгенерированный контент для этой сессии
    session_items: List[Dict[str, Any]] = field(default_factory=list)
    session_enemies: List[Dict[str, Any]] = field(default_factory=list)
    session_weapons: List[Dict[str, Any]] = field(default_factory=list)
    session_skills: List[Dict[str, Any]] = field(default_factory=list)
    
    # Настройки генерации
    generation_seed: int = 0
    current_level: int = 1


class SessionManager:
    """Менеджер игровых сессий"""
    
    def __init__(self, save_dir: str = "save", max_slots: int = 10):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.max_slots = max_slots
        
        # База данных сессий
        self.db_path = self.save_dir / "sessions.db"
        self._init_session_database()
        
        # Активная сессия
        self.active_session: Optional[SessionData] = None
        self.active_slot: Optional[SaveSlot] = None
        
        logger.info(f"Менеджер сессий инициализирован: {self.save_dir}")
    
    def _init_session_database(self):
        """Инициализация базы данных сессий"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Таблица слотов сохранения
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS save_slots (
                    slot_id INTEGER PRIMARY KEY,
                    session_uuid TEXT UNIQUE NOT NULL,
                    save_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_played TEXT NOT NULL,
                    player_level INTEGER DEFAULT 1,
                    world_seed INTEGER DEFAULT 0,
                    play_time REAL DEFAULT 0.0,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Таблица данных сессий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_data (
                    session_uuid TEXT PRIMARY KEY,
                    slot_id INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_saved TEXT NOT NULL,
                    player_data TEXT,
                    world_data TEXT,
                    inventory_data TEXT,
                    progress_data TEXT,
                    session_items TEXT,
                    session_enemies TEXT,
                    session_weapons TEXT,
                    session_skills TEXT,
                    generation_seed INTEGER DEFAULT 0,
                    current_level INTEGER DEFAULT 1,
                    FOREIGN KEY(slot_id) REFERENCES save_slots(slot_id)
                )
            """)
            
            # Индексы
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_save_slots_active ON save_slots(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_data_slot ON session_data(slot_id)")
            
            conn.commit()
            logger.info("База данных сессий инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации БД сессий: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def create_new_session(self, slot_id: int, save_name: str, world_seed: int = None) -> SessionData:
        """Создание новой игровой сессии"""
        try:
            # Проверяем доступность слота
            if not self._is_slot_available(slot_id):
                raise ValueError(f"Слот {slot_id} уже занят")
            
            # Генерируем UUID сессии
            session_uuid = str(uuid.uuid4())
            
            # Создаём слот сохранения
            save_slot = SaveSlot(
                slot_id=slot_id,
                session_uuid=session_uuid,
                save_name=save_name,
                created_at=datetime.now(),
                last_played=datetime.now(),
                player_level=1,
                world_seed=world_seed or 0,
                play_time=0.0,
                is_active=True
            )
            
            # Создаём данные сессии
            session_data = SessionData(
                session_uuid=session_uuid,
                slot_id=slot_id,
                state=SessionState.NEW,
                created_at=datetime.now(),
                last_saved=datetime.now(),
                generation_seed=world_seed or 0,
                current_level=1
            )
            
            # Сохраняем в БД
            self._save_slot_to_db(save_slot)
            self._save_session_to_db(session_data)
            
            # Активируем сессию
            self.active_session = session_data
            self.active_slot = save_slot
            
            logger.info(f"Создана новая сессия: {session_uuid} в слоте {slot_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Ошибка создания сессии: {e}")
            raise
    
    def load_session(self, slot_id: int) -> SessionData:
        """Загрузка существующей сессии"""
        try:
            # Загружаем слот
            save_slot = self._load_slot_from_db(slot_id)
            if not save_slot:
                raise ValueError(f"Слот {slot_id} не найден")
            
            # Загружаем данные сессии
            session_data = self._load_session_from_db(save_slot.session_uuid)
            if not session_data:
                raise ValueError(f"Данные сессии {save_slot.session_uuid} не найдены")
            
            # Активируем сессию
            self.active_session = session_data
            self.active_slot = save_slot
            
            # Обновляем время последней игры
            save_slot.last_played = datetime.now()
            self._save_slot_to_db(save_slot)
            
            logger.info(f"Загружена сессия: {session_data.session_uuid} из слота {slot_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {e}")
            raise
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """Сохранение текущей сессии"""
        try:
            if not self.active_session:
                raise ValueError("Нет активной сессии для сохранения")
            
            # Обновляем данные сессии
            self.active_session.player_data = session_data.get("player", {})
            self.active_session.world_data = session_data.get("world", {})
            self.active_session.inventory_data = session_data.get("inventory", {})
            self.active_session.progress_data = session_data.get("progress", {})
            self.active_session.last_saved = datetime.now()
            self.active_session.state = SessionState.SAVED
            
            # Обновляем слот
            if self.active_slot:
                self.active_slot.last_played = datetime.now()
                self.active_slot.play_time = session_data.get("play_time", 0.0)
                self.active_slot.player_level = session_data.get("player_level", 1)
                self._save_slot_to_db(self.active_slot)
            
            # Сохраняем в БД
            self._save_session_to_db(self.active_session)
            
            # Создаём резервную копию в JSON
            self._create_backup_save()
            
            logger.info(f"Сессия {self.active_session.session_uuid} сохранена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")
            return False
    
    def delete_session(self, slot_id: int) -> bool:
        """Удаление сессии"""
        try:
            # Загружаем слот
            save_slot = self._load_slot_from_db(slot_id)
            if not save_slot:
                return False
            
            # Удаляем из БД
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM session_data WHERE session_uuid = ?", (save_slot.session_uuid,))
            cursor.execute("DELETE FROM save_slots WHERE slot_id = ?", (slot_id,))
            
            conn.commit()
            conn.close()
            
            # Удаляем резервную копию
            backup_file = self.save_dir / f"save_{slot_id}.json"
            if backup_file.exists():
                backup_file.unlink()
            
            logger.info(f"Сессия в слоте {slot_id} удалена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления сессии: {e}")
            return False
    
    def get_available_slots(self) -> List[SaveSlot]:
        """Получение списка доступных слотов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT slot_id, session_uuid, save_name, created_at, last_played,
                       player_level, world_seed, play_time, is_active
                FROM save_slots
                WHERE is_active = 1
                ORDER BY slot_id
            """)
            
            slots = []
            for row in cursor.fetchall():
                slot = SaveSlot(
                    slot_id=row[0],
                    session_uuid=row[1],
                    save_name=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    last_played=datetime.fromisoformat(row[4]),
                    player_level=row[5],
                    world_seed=row[6],
                    play_time=row[7],
                    is_active=bool(row[8])
                )
                slots.append(slot)
            
            conn.close()
            return slots
            
        except Exception as e:
            logger.error(f"Ошибка получения слотов: {e}")
            return []
    
    def get_free_slot_id(self) -> Optional[int]:
        """Получение свободного ID слота"""
        used_slots = {slot.slot_id for slot in self.get_available_slots()}
        
        for slot_id in range(1, self.max_slots + 1):
            if slot_id not in used_slots:
                return slot_id
        
        return None
    
    def add_session_content(self, content_type: str, content_data: Dict[str, Any]):
        """Добавление контента в текущую сессию"""
        if not self.active_session:
            return
        
        if content_type == "items":
            self.active_session.session_items.append(content_data)
        elif content_type == "enemies":
            self.active_session.session_enemies.append(content_data)
        elif content_type == "weapons":
            self.active_session.session_weapons.append(content_data)
        elif content_type == "skills":
            self.active_session.session_skills.append(content_data)
        
        # Автосохранение
        self._save_session_to_db(self.active_session)
    
    def get_session_content(self, content_type: str) -> List[Dict[str, Any]]:
        """Получение контента текущей сессии"""
        if not self.active_session:
            return []
        
        if content_type == "items":
            return self.active_session.session_items
        elif content_type == "enemies":
            return self.active_session.session_enemies
        elif content_type == "weapons":
            return self.active_session.session_weapons
        elif content_type == "skills":
            return self.active_session.session_skills
        
        return []
    
    def _is_slot_available(self, slot_id: int) -> bool:
        """Проверка доступности слота"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM save_slots WHERE slot_id = ? AND is_active = 1", (slot_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count == 0
    
    def _save_slot_to_db(self, save_slot: SaveSlot):
        """Сохранение слота в БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO save_slots 
            (slot_id, session_uuid, save_name, created_at, last_played, 
             player_level, world_seed, play_time, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            save_slot.slot_id, save_slot.session_uuid, save_slot.save_name,
            save_slot.created_at.isoformat(), save_slot.last_played.isoformat(),
            save_slot.player_level, save_slot.world_seed, save_slot.play_time,
            1 if save_slot.is_active else 0
        ))
        
        conn.commit()
        conn.close()
    
    def _save_session_to_db(self, session_data: SessionData):
        """Сохранение данных сессии в БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO session_data 
            (session_uuid, slot_id, state, created_at, last_saved,
             player_data, world_data, inventory_data, progress_data,
             session_items, session_enemies, session_weapons, session_skills,
             generation_seed, current_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data.session_uuid, session_data.slot_id, session_data.state.value,
            session_data.created_at.isoformat(), session_data.last_saved.isoformat(),
            json.dumps(session_data.player_data), json.dumps(session_data.world_data),
            json.dumps(session_data.inventory_data), json.dumps(session_data.progress_data),
            json.dumps(session_data.session_items), json.dumps(session_data.session_enemies),
            json.dumps(session_data.session_weapons), json.dumps(session_data.session_skills),
            session_data.generation_seed, session_data.current_level
        ))
        
        conn.commit()
        conn.close()
    
    def _load_slot_from_db(self, slot_id: int) -> Optional[SaveSlot]:
        """Загрузка слота из БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT slot_id, session_uuid, save_name, created_at, last_played,
                   player_level, world_seed, play_time, is_active
            FROM save_slots
            WHERE slot_id = ? AND is_active = 1
        """, (slot_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return SaveSlot(
                slot_id=row[0],
                session_uuid=row[1],
                save_name=row[2],
                created_at=datetime.fromisoformat(row[3]),
                last_played=datetime.fromisoformat(row[4]),
                player_level=row[5],
                world_seed=row[6],
                play_time=row[7],
                is_active=bool(row[8])
            )
        
        return None
    
    def _load_session_from_db(self, session_uuid: str) -> Optional[SessionData]:
        """Загрузка данных сессии из БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_uuid, slot_id, state, created_at, last_saved,
                   player_data, world_data, inventory_data, progress_data,
                   session_items, session_enemies, session_weapons, session_skills,
                   generation_seed, current_level
            FROM session_data
            WHERE session_uuid = ?
        """, (session_uuid,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return SessionData(
                session_uuid=row[0],
                slot_id=row[1],
                state=SessionState(row[2]),
                created_at=datetime.fromisoformat(row[3]),
                last_saved=datetime.fromisoformat(row[4]),
                player_data=json.loads(row[5]) if row[5] else {},
                world_data=json.loads(row[6]) if row[6] else {},
                inventory_data=json.loads(row[7]) if row[7] else {},
                progress_data=json.loads(row[8]) if row[8] else {},
                session_items=json.loads(row[9]) if row[9] else [],
                session_enemies=json.loads(row[10]) if row[10] else [],
                session_weapons=json.loads(row[11]) if row[11] else [],
                session_skills=json.loads(row[12]) if row[12] else [],
                generation_seed=row[13],
                current_level=row[14]
            )
        
        return None
    
    def _create_backup_save(self):
        """Создание резервной копии сохранения в JSON"""
        if not self.active_session or not self.active_slot:
            return
        
        backup_data = {
            "session_uuid": self.active_session.session_uuid,
            "slot_id": self.active_slot.slot_id,
            "save_name": self.active_slot.save_name,
            "created_at": self.active_session.created_at.isoformat(),
            "last_saved": self.active_session.last_saved.isoformat(),
            "player_data": self.active_session.player_data,
            "world_data": self.active_session.world_data,
            "inventory_data": self.active_session.inventory_data,
            "progress_data": self.active_session.progress_data,
            "session_items": self.active_session.session_items,
            "session_enemies": self.active_session.session_enemies,
            "session_weapons": self.active_session.session_weapons,
            "session_skills": self.active_session.session_skills,
            "generation_seed": self.active_session.generation_seed,
            "current_level": self.active_session.current_level
        }
        
        backup_file = self.save_dir / f"save_{self.active_slot.slot_id}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)


# Глобальный экземпляр менеджера сессий
session_manager = SessionManager()
