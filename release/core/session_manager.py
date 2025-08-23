#!/usr/bin/env python3
"""
Система управления игровыми сессиями.
Управляет временными сессиями и сохранением контента в БД.
"""

import uuid
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """Данные игровой сессии"""
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


class SessionManager:
    """Менеджер игровых сессий"""
    
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
        
        # Инициализация БД
        self._init_database()
        
        logger.info("SessionManager инициализирован")
    
    def _init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_uuid TEXT PRIMARY KEY,
                        slot_id INTEGER,
                        save_name TEXT,
                        world_seed INTEGER,
                        player_data TEXT,
                        world_data TEXT,
                        inventory_data TEXT,
                        progress_data TEXT,
                        generation_seed INTEGER,
                        current_level INTEGER,
                        created_at TEXT,
                        last_saved TEXT,
                        state TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS session_content (
                        session_uuid TEXT,
                        content_type TEXT,
                        content_data TEXT,
                        FOREIGN KEY (session_uuid) REFERENCES sessions (session_uuid)
                    )
                """)
                
                conn.commit()
                logger.info("База данных сессий инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации БД сессий: {e}")
    
    def create_temporary_session(self, world_seed: int = None) -> SessionData:
        """Создает временную сессию (не сохраняется в БД)"""
        if world_seed is None:
            world_seed = int(time.time()) % 1000000
        
        session_uuid = str(uuid.uuid4())
        
        self.current_session = SessionData(
            session_uuid=session_uuid,
            world_seed=world_seed,
            generation_seed=world_seed,
            save_name=f"Временная сессия {datetime.now().strftime('%H:%M')}",
            state="temporary"
        )
        
        # Очищаем временное хранилище контента
        self.session_content = {
            "items": [],
            "enemies": [],
            "skills": [],
            "genes": [],
            "accessories": []
        }
        
        logger.info(f"Создана временная сессия: {session_uuid}")
        return self.current_session
    
    def add_session_content(self, content_type: str, content_data: Dict[str, Any]):
        """Добавляет контент в текущую сессию (временное хранилище)"""
        if content_type in self.session_content:
            self.session_content[content_type].append(content_data)
            logger.debug(f"Добавлен контент типа {content_type} в сессию")
        else:
            logger.warning(f"Неизвестный тип контента: {content_type}")
    
    def get_session_content(self, content_type: str) -> List[Dict[str, Any]]:
        """Получает контент текущей сессии"""
        return self.session_content.get(content_type, [])
    
    def save_session_to_slot(self, slot_id: int, save_name: str = None) -> bool:
        """Сохраняет текущую сессию в слот (записывает в БД)"""
        if not self.current_session:
            logger.error("Нет активной сессии для сохранения")
            return False
        
        try:
            # Обновляем данные сессии
            self.current_session.slot_id = slot_id
            if save_name:
                self.current_session.save_name = save_name
            self.current_session.state = "saved"
            self.current_session.last_saved = datetime.now().isoformat()
            
            # Сохраняем в БД
            with sqlite3.connect(self.db_path) as conn:
                # Сохраняем основную информацию о сессии
                conn.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (session_uuid, slot_id, save_name, world_seed, player_data, world_data, 
                     inventory_data, progress_data, generation_seed, current_level, 
                     created_at, last_saved, state)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.current_session.session_uuid,
                    self.current_session.slot_id,
                    self.current_session.save_name,
                    self.current_session.world_seed,
                    json.dumps(self.current_session.player_data),
                    json.dumps(self.current_session.world_data),
                    json.dumps(self.current_session.inventory_data),
                    json.dumps(self.current_session.progress_data),
                    self.current_session.generation_seed,
                    self.current_session.current_level,
                    self.current_session.created_at,
                    self.current_session.last_saved,
                    self.current_session.state
                ))
                
                # Сохраняем контент сессии в БД
                conn.execute("DELETE FROM session_content WHERE session_uuid = ?", 
                           (self.current_session.session_uuid,))
                
                for content_type, content_list in self.session_content.items():
                    for content_item in content_list:
                        conn.execute("""
                            INSERT INTO session_content (session_uuid, content_type, content_data)
                            VALUES (?, ?, ?)
                        """, (
                            self.current_session.session_uuid,
                            content_type,
                            json.dumps(content_item)
                        ))
                
                conn.commit()
                logger.info(f"Сессия сохранена в слот {slot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")
            return False
    
    def load_session_from_slot(self, slot_id: int) -> Optional[SessionData]:
        """Загружает сессию из слота"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Загружаем основную информацию о сессии
                cursor = conn.execute("""
                    SELECT session_uuid, save_name, world_seed, player_data, world_data,
                           inventory_data, progress_data, generation_seed, current_level,
                           created_at, last_saved, state
                    FROM sessions WHERE slot_id = ?
                """, (slot_id,))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"Слот {slot_id} не найден")
                    return None
                
                # Создаем объект сессии
                session_data = SessionData(
                    session_uuid=row[0],
                    slot_id=slot_id,
                    save_name=row[1],
                    world_seed=row[2],
                    player_data=json.loads(row[3]) if row[3] else {},
                    world_data=json.loads(row[4]) if row[4] else {},
                    inventory_data=json.loads(row[5]) if row[5] else {},
                    progress_data=json.loads(row[6]) if row[6] else {},
                    generation_seed=row[7],
                    current_level=row[8],
                    created_at=row[9],
                    last_saved=row[10],
                    state=row[11]
                )
                
                # Загружаем контент сессии
                cursor = conn.execute("""
                    SELECT content_type, content_data FROM session_content 
                    WHERE session_uuid = ?
                """, (session_data.session_uuid,))
                
                self.session_content = {
                    "items": [],
                    "enemies": [],
                    "skills": [],
                    "genes": [],
                    "accessories": []
                }
                
                for content_type, content_data in cursor.fetchall():
                    if content_type in self.session_content:
                        self.session_content[content_type].append(json.loads(content_data))
                
                self.current_session = session_data
                logger.info(f"Сессия загружена из слота {slot_id}")
                return session_data
            
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {e}")
            return None
    
    def get_save_slots_info(self) -> List[Dict[str, Any]]:
        """Получает информацию о слотах сохранения"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT slot_id, save_name, current_level, last_saved, state
                    FROM sessions WHERE slot_id IS NOT NULL
                    ORDER BY slot_id
            """)
            
            slots_info = []
            for row in cursor.fetchall():
                    slots_info.append({
                        "slot_id": row[0],
                        "save_name": row[1],
                        "level": row[2],
                        "last_saved": row[3],
                        "state": row[4]
                    })
                
            return slots_info
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о слотах: {e}")
            return []
    
    def delete_save_slot(self, slot_id: int) -> bool:
        """Удаляет слот сохранения"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Получаем session_uuid для удаления связанного контента
                cursor = conn.execute("SELECT session_uuid FROM sessions WHERE slot_id = ?", (slot_id,))
                row = cursor.fetchone()
                
                if row:
                    session_uuid = row[0]
                    # Удаляем контент сессии
                    conn.execute("DELETE FROM session_content WHERE session_uuid = ?", (session_uuid,))
                    # Удаляем сессию
                    conn.execute("DELETE FROM sessions WHERE slot_id = ?", (slot_id,))
                    conn.commit()
                    
                    logger.info(f"Слот {slot_id} удален")
                    return True
                else:
                    logger.warning(f"Слот {slot_id} не найден")
                    return False
            
        except Exception as e:
            logger.error(f"Ошибка удаления слота: {e}")
            return False
    
    def update_session_data(self, player_data: Dict[str, Any] = None, 
                          world_data: Dict[str, Any] = None,
                          inventory_data: Dict[str, Any] = None,
                          progress_data: Dict[str, Any] = None):
        """Обновляет данные текущей сессии"""
        if not self.current_session:
            logger.warning("Нет активной сессии для обновления")
            return
        
        if player_data:
            self.current_session.player_data.update(player_data)
        if world_data:
            self.current_session.world_data.update(world_data)
        if inventory_data:
            self.current_session.inventory_data.update(inventory_data)
        if progress_data:
            self.current_session.progress_data.update(progress_data)
        
        self.current_session.last_saved = datetime.now().isoformat()
        logger.debug("Данные сессии обновлены")
    
    def get_current_session(self) -> Optional[SessionData]:
        """Получает текущую активную сессию"""
        return self.current_session
    
    def clear_current_session(self):
        """Очищает текущую сессию"""
        self.current_session = None
        self.session_content = {
            "items": [],
            "enemies": [],
            "skills": [],
            "genes": [],
            "accessories": []
        }
        logger.info("Текущая сессия очищена")

    def create_save_slot(self, save_name: str = None) -> int:
        """Создает новый слот сохранения и возвращает его ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Находим следующий свободный slot_id
                cursor = conn.execute("SELECT MAX(slot_id) FROM save_slots")
                max_slot = cursor.fetchone()[0]
                new_slot_id = (max_slot or 0) + 1
                
                # Создаем новый слот
                session_uuid = str(uuid.uuid4())
                save_name = save_name or f"Сохранение {new_slot_id}"
                
                conn.execute("""
                    INSERT INTO save_slots 
                    (slot_id, session_uuid, save_name, created_at, last_played, player_level, world_seed, play_time, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    new_slot_id,
                    session_uuid,
                    save_name,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    1,  # player_level
                    0,  # world_seed
                    0.0,  # play_time
                    1   # is_active
                ))
                
                conn.commit()
                logger.info(f"Создан новый слот сохранения: {new_slot_id}")
                return new_slot_id
                
        except Exception as e:
            logger.error(f"Ошибка создания слота сохранения: {e}")
            return -1

    def get_available_save_slots(self) -> List[Dict[str, Any]]:
        """Получает список доступных слотов сохранения"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT slot_id, save_name, created_at, last_played, player_level, play_time, is_active
                    FROM save_slots 
                    WHERE is_active = 1
                    ORDER BY slot_id
                """)
                
                slots = []
                for row in cursor.fetchall():
                    slots.append({
                        "slot_id": row[0],
                        "save_name": row[1],
                        "created_at": row[2],
                        "last_played": row[3],
                        "player_level": row[4],
                        "play_time": row[5],
                        "is_active": bool(row[6])
                    })
                
                return slots
            
        except Exception as e:
            logger.error(f"Ошибка получения слотов сохранения: {e}")
            return []

    def initialize_default_slots(self):
        """Инициализирует 5 слотов сохранения по умолчанию"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Проверяем, есть ли уже слоты
                cursor = conn.execute("SELECT COUNT(*) FROM save_slots")
                slot_count = cursor.fetchone()[0]
                
                if slot_count == 0:
                    # Создаем 5 слотов по умолчанию
                    for i in range(1, 6):
                        session_uuid = str(uuid.uuid4())
                        conn.execute("""
                            INSERT INTO save_slots 
                            (slot_id, session_uuid, save_name, created_at, last_played, player_level, world_seed, play_time, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            i,
                            session_uuid,
                            f"Слот {i}",
                            datetime.now().isoformat(),
                            datetime.now().isoformat(),
                            1,
                            0,
                            0.0,
                            1
                        ))
                    
                    conn.commit()
                    logger.info("Создано 5 слотов сохранения по умолчанию")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации слотов по умолчанию: {e}")


# Глобальный экземпляр менеджера сессий
session_manager = SessionManager()
