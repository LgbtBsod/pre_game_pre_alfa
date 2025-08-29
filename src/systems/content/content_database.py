#!/usr/bin/env python3
"""
Система контента - база данных для процедурно сгенерированного контента
"""

import sqlite3
import logging
import uuid
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import constants_manager, ContentType, ContentRarity, EnemyType, BossType, DamageType, ItemType, ItemRarity, ItemCategory, StatType, BASE_STATS, PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS

logger = logging.getLogger(__name__)

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
class ContentSlot:
    """Слот для сохранения контента"""
    slot_id: str
    slot_name: str
    slot_type: str
    is_occupied: bool = False
    content_item: Optional[ContentItem] = None
    save_timestamp: float = 0.0

@dataclass
class ContentSession:
    """Сессия генерации контента"""
    session_id: str
    session_name: str
    start_timestamp: float
    end_timestamp: Optional[float] = None
    content_generated: int = 0
    content_saved: int = 0
    generation_config: Dict[str, Any] = None

class ContentDatabase(ISystem):
    """Система базы данных контента с использованием централизованных констант"""
    
    def __init__(self, db_path: str = "content.db"):
        self._system_name = "content_database"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        self.db_path = Path(db_path)
        self.connection = None
        self.cursor = None
        
        # Управление слотами и сессиями
        self.content_slots: Dict[str, ContentSlot] = {}
        self.content_sessions: Dict[str, ContentSession] = {}
        
        # Статистика системы
        self.system_stats = {
            'total_items': 0,
            'saved_items': 0,
            'deleted_items': 0,
            'sessions_created': 0,
            'sessions_completed': 0,
            'database_operations': 0,
            'update_time': 0.0
        }
        
        logger.info("Система базы данных контента инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы базы данных контента"""
        try:
            logger.info("Инициализация системы базы данных контента...")
            
            # Создаем подключение к базе данных
            self._create_database_connection()
            
            # Инициализируем таблицы
            self._initialize_database_tables()
            
            # Загружаем существующие данные
            self._load_existing_data()
            
            self._system_state = SystemState.READY
            logger.info("Система базы данных контента успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы базы данных контента: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы базы данных контента"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы базы данных контента: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы базы данных контента"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система базы данных контента приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы базы данных контента: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы базы данных контента"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система базы данных контента возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы базы данных контента: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы базы данных контента"""
        try:
            logger.info("Очистка системы базы данных контента...")
            
            # Закрываем подключение к базе данных
            if self.connection:
                self.connection.close()
            
            # Очищаем данные
            self.content_slots.clear()
            self.content_sessions.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'total_items': 0,
                'saved_items': 0,
                'deleted_items': 0,
                'sessions_created': 0,
                'sessions_completed': 0,
                'database_operations': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система базы данных контента очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы базы данных контента: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'database_path': str(self.db_path),
            'slots_count': len(self.content_slots),
            'sessions_count': len(self.content_sessions),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "content_item_created":
                return self._handle_content_item_created(event_data)
            elif event_type == "content_item_saved":
                return self._handle_content_item_saved(event_data)
            elif event_type == "content_item_deleted":
                return self._handle_content_item_deleted(event_data)
            elif event_type == "session_started":
                return self._handle_session_started(event_data)
            elif event_type == "session_completed":
                return self._handle_session_completed(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _create_database_connection(self) -> None:
        """Создание подключения к базе данных"""
        try:
            # Создаем директорию, если она не существует
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Создаем подключение
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            
            logger.debug(f"Подключение к базе данных создано: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Ошибка создания подключения к базе данных: {e}")
            raise
    
    def _initialize_database_tables(self) -> None:
        """Инициализация таблиц базы данных"""
        try:
            # Таблица контента
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_items (
                    uuid TEXT PRIMARY KEY,
                    content_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    rarity TEXT NOT NULL,
                    level_requirement INTEGER DEFAULT 1,
                    session_id TEXT NOT NULL,
                    generation_timestamp REAL NOT NULL,
                    data TEXT NOT NULL,
                    is_saved BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Таблица слотов
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_slots (
                    slot_id TEXT PRIMARY KEY,
                    slot_name TEXT NOT NULL,
                    slot_type TEXT NOT NULL,
                    is_occupied BOOLEAN DEFAULT FALSE,
                    content_uuid TEXT,
                    save_timestamp REAL DEFAULT 0.0,
                    FOREIGN KEY (content_uuid) REFERENCES content_items (uuid)
                )
            """)
            
            # Таблица сессий
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_sessions (
                    session_id TEXT PRIMARY KEY,
                    session_name TEXT NOT NULL,
                    start_timestamp REAL NOT NULL,
                    end_timestamp REAL,
                    content_generated INTEGER DEFAULT 0,
                    content_saved INTEGER DEFAULT 0,
                    generation_config TEXT
                )
            """)
            
            # Создаем индексы для улучшения производительности
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON content_items (content_type)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_rarity ON content_items (rarity)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_session ON content_items (session_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_slot_type ON content_slots (slot_type)")
            
            # Сохраняем изменения
            self.connection.commit()
            
            logger.debug("Таблицы базы данных инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации таблиц базы данных: {e}")
            raise
    
    def _load_existing_data(self) -> None:
        """Загрузка существующих данных из базы данных"""
        try:
            # Загружаем слоты
            self.cursor.execute("SELECT * FROM content_slots")
            for row in self.cursor.fetchall():
                slot = ContentSlot(
                    slot_id=row['slot_id'],
                    slot_name=row['slot_name'],
                    slot_type=row['slot_type'],
                    is_occupied=bool(row['is_occupied']),
                    save_timestamp=row['save_timestamp']
                )
                
                # Загружаем связанный контент, если есть
                if row['content_uuid']:
                    content_item = self.get_content_item(row['content_uuid'])
                    if content_item:
                        slot.content_item = content_item
                        slot.is_occupied = True
                
                self.content_slots[slot.slot_id] = slot
            
            # Загружаем сессии
            self.cursor.execute("SELECT * FROM content_sessions")
            for row in self.cursor.fetchall():
                session = ContentSession(
                    session_id=row['session_id'],
                    session_name=row['session_name'],
                    start_timestamp=row['start_timestamp'],
                    end_timestamp=row['end_timestamp'],
                    content_generated=row['content_generated'],
                    content_saved=row['content_saved'],
                    generation_config=json.loads(row['generation_config']) if row['generation_config'] else None
                )
                self.content_sessions[session.session_id] = session
            
            # Обновляем статистику
            self.cursor.execute("SELECT COUNT(*) as total FROM content_items")
            self.system_stats['total_items'] = self.cursor.fetchone()['total']
            
            self.cursor.execute("SELECT COUNT(*) as saved FROM content_items WHERE is_saved = 1")
            self.system_stats['saved_items'] = self.cursor.fetchone()['saved']
            
            logger.info(f"Загружено {len(self.content_slots)} слотов и {len(self.content_sessions)} сессий")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки существующих данных: {e}")
            raise
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            # Обновляем статистику из базы данных
            if self.cursor:
                self.cursor.execute("SELECT COUNT(*) as total FROM content_items")
                self.system_stats['total_items'] = self.cursor.fetchone()['total']
                
                self.cursor.execute("SELECT COUNT(*) as saved FROM content_items WHERE is_saved = 1")
                self.system_stats['saved_items'] = self.system_stats['saved_items'] = self.cursor.fetchone()['saved']
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_content_item_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания элемента контента"""
        try:
            content_item = event_data.get('content_item')
            if content_item:
                # Сохраняем элемент в базу данных
                self.save_content_item(content_item)
                
                # Обновляем статистику
                self.system_stats['total_items'] += 1
                
                logger.debug(f"Обработано событие создания элемента контента: {content_item.uuid}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания элемента контента: {e}")
            return False
    
    def _handle_content_item_saved(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события сохранения элемента контента"""
        try:
            content_item = event_data.get('content_item')
            slot_id = event_data.get('slot_id')
            
            if content_item and slot_id:
                # Сохраняем элемент в слот
                self.save_content_to_slot(content_item, slot_id)
                
                # Обновляем статистику
                self.system_stats['saved_items'] += 1
                
                logger.debug(f"Обработано событие сохранения элемента контента: {content_item.uuid} в слот {slot_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события сохранения элемента контента: {e}")
            return False
    
    def _handle_content_item_deleted(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события удаления элемента контента"""
        try:
            content_uuid = event_data.get('content_uuid')
            
            if content_uuid:
                # Удаляем элемент из базы данных
                self.delete_content_item(content_uuid)
                
                # Обновляем статистику
                self.system_stats['deleted_items'] += 1
                
                logger.debug(f"Обработано событие удаления элемента контента: {content_uuid}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события удаления элемента контента: {e}")
            return False
    
    def _handle_session_started(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события начала сессии"""
        try:
            session_data = event_data.get('session_data')
            
            if session_data:
                # Создаем новую сессию
                session = ContentSession(
                    session_id=session_data.get('session_id', str(uuid.uuid4())),
                    session_name=session_data.get('session_name', 'Unnamed Session'),
                    start_timestamp=time.time(),
                    generation_config=session_data.get('generation_config')
                )
                
                # Сохраняем сессию в базу данных
                self.save_session(session)
                
                # Добавляем в локальный словарь
                self.content_sessions[session.session_id] = session
                
                # Обновляем статистику
                self.system_stats['sessions_created'] += 1
                
                logger.debug(f"Обработано событие начала сессии: {session.session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события начала сессии: {e}")
            return False
    
    def _handle_session_completed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события завершения сессии"""
        try:
            session_id = event_data.get('session_id')
            
            if session_id and session_id in self.content_sessions:
                # Завершаем сессию
                session = self.content_sessions[session_id]
                session.end_timestamp = time.time()
                
                # Обновляем в базе данных
                self.update_session(session)
                
                # Обновляем статистику
                self.system_stats['sessions_completed'] += 1
                
                logger.debug(f"Обработано событие завершения сессии: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события завершения сессии: {e}")
            return False
    
    def save_content_item(self, content_item: ContentItem) -> bool:
        """Сохранение элемента контента в базу данных"""
        try:
            # Проверяем, существует ли уже элемент
            self.cursor.execute("SELECT uuid FROM content_items WHERE uuid = ?", (content_item.uuid,))
            if self.cursor.fetchone():
                # Обновляем существующий элемент
                self.cursor.execute("""
                    UPDATE content_items SET
                        content_type = ?, name = ?, description = ?, rarity = ?,
                        level_requirement = ?, session_id = ?, generation_timestamp = ?,
                        data = ?, is_saved = ?
                    WHERE uuid = ?
                """, (
                    content_item.content_type.value,
                    content_item.name,
                    content_item.description,
                    content_item.rarity.value,
                    content_item.level_requirement,
                    content_item.session_id,
                    content_item.generation_timestamp,
                    json.dumps(content_item.data),
                    content_item.is_saved,
                    content_item.uuid
                ))
            else:
                # Создаем новый элемент
                self.cursor.execute("""
                    INSERT INTO content_items (
                        uuid, content_type, name, description, rarity,
                        level_requirement, session_id, generation_timestamp,
                        data, is_saved
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content_item.uuid,
                    content_item.content_type.value,
                    content_item.name,
                    content_item.description,
                    content_item.rarity.value,
                    content_item.level_requirement,
                    content_item.session_id,
                    content_item.generation_timestamp,
                    json.dumps(content_item.data),
                    content_item.is_saved
                ))
            
            # Сохраняем изменения
            self.connection.commit()
            
            # Обновляем статистику
            self.system_stats['database_operations'] += 1
            
            logger.debug(f"Элемент контента сохранен: {content_item.uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения элемента контента: {e}")
            return False
    
    def get_content_item(self, content_uuid: str) -> Optional[ContentItem]:
        """Получение элемента контента по UUID"""
        try:
            self.cursor.execute("SELECT * FROM content_items WHERE uuid = ?", (content_uuid,))
            row = self.cursor.fetchone()
            
            if row:
                # Создаем объект ContentItem
                content_item = ContentItem(
                    uuid=row['uuid'],
                    content_type=ContentType(row['content_type']),
                    name=row['name'],
                    description=row['description'],
                    rarity=ContentRarity(row['rarity']),
                    level_requirement=row['level_requirement'],
                    session_id=row['session_id'],
                    generation_timestamp=row['generation_timestamp'],
                    data=json.loads(row['data']),
                    is_saved=bool(row['is_saved'])
                )
                
                return content_item
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения элемента контента: {e}")
            return None
    
    def delete_content_item(self, content_uuid: str) -> bool:
        """Удаление элемента контента"""
        try:
            # Удаляем из базы данных
            self.cursor.execute("DELETE FROM content_items WHERE uuid = ?", (content_uuid,))
            
            # Удаляем из слотов, если есть
            self.cursor.execute("UPDATE content_slots SET content_uuid = NULL, is_occupied = FALSE WHERE content_uuid = ?", (content_uuid,))
            
            # Сохраняем изменения
            self.connection.commit()
            
            # Обновляем статистику
            self.system_stats['database_operations'] += 1
            
            logger.debug(f"Элемент контента удален: {content_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления элемента контента: {e}")
            return False
    
    def save_content_to_slot(self, content_item: ContentItem, slot_id: str) -> bool:
        """Сохранение элемента контента в слот"""
        try:
            # Проверяем, существует ли слот
            if slot_id not in self.content_slots:
                logger.warning(f"Слот {slot_id} не найден")
                return False
            
            slot = self.content_slots[slot_id]
            
            # Освобождаем слот, если он занят
            if slot.is_occupied and slot.content_item:
                slot.content_item.is_saved = False
                self.save_content_item(slot.content_item)
            
            # Сохраняем новый элемент в слот
            slot.content_item = content_item
            slot.is_occupied = True
            slot.save_timestamp = time.time()
            
            # Обновляем элемент контента
            content_item.is_saved = True
            self.save_content_item(content_item)
            
            # Обновляем слот в базе данных
            self.cursor.execute("""
                UPDATE content_slots SET
                    is_occupied = ?, content_uuid = ?, save_timestamp = ?
                WHERE slot_id = ?
            """, (True, content_item.uuid, slot.save_timestamp, slot_id))
            
            # Сохраняем изменения
            self.connection.commit()
            
            logger.debug(f"Элемент контента {content_item.uuid} сохранен в слот {slot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения элемента контента в слот: {e}")
            return False
    
    def get_content_from_slot(self, slot_id: str) -> Optional[ContentItem]:
        """Получение элемента контента из слота"""
        try:
            if slot_id in self.content_slots:
                slot = self.content_slots[slot_id]
                if slot.is_occupied and slot.content_item:
                    return slot.content_item
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения элемента контента из слота: {e}")
            return None
    
    def create_slot(self, slot_id: str, slot_name: str, slot_type: str) -> bool:
        """Создание нового слота"""
        try:
            if slot_id in self.content_slots:
                logger.warning(f"Слот {slot_id} уже существует")
                return False
            
            # Создаем слот в базе данных
            self.cursor.execute("""
                INSERT INTO content_slots (slot_id, slot_name, slot_type)
                VALUES (?, ?, ?)
            """, (slot_id, slot_name, slot_type))
            
            # Создаем локальный объект
            slot = ContentSlot(
                slot_id=slot_id,
                slot_name=slot_name,
                slot_type=slot_type
            )
            self.content_slots[slot_id] = slot
            
            # Сохраняем изменения
            self.connection.commit()
            
            logger.debug(f"Создан новый слот: {slot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания слота: {e}")
            return False
    
    def delete_slot(self, slot_id: str) -> bool:
        """Удаление слота"""
        try:
            if slot_id not in self.content_slots:
                logger.warning(f"Слот {slot_id} не найден")
                return False
            
            slot = self.content_slots[slot_id]
            
            # Освобождаем слот, если он занят
            if slot.is_occupied and slot.content_item:
                slot.content_item.is_saved = False
                self.save_content_item(slot.content_item)
            
            # Удаляем слот из базы данных
            self.cursor.execute("DELETE FROM content_slots WHERE slot_id = ?", (slot_id,))
            
            # Удаляем из локального словаря
            del self.content_slots[slot_id]
            
            # Сохраняем изменения
            self.connection.commit()
            
            logger.debug(f"Слот удален: {slot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления слота: {e}")
            return False
    
    def save_session(self, session: ContentSession) -> bool:
        """Сохранение сессии в базу данных"""
        try:
            # Проверяем, существует ли уже сессия
            self.cursor.execute("SELECT session_id FROM content_sessions WHERE session_id = ?", (session.session_id,))
            if self.cursor.fetchone():
                # Обновляем существующую сессию
                self.cursor.execute("""
                    UPDATE content_sessions SET
                        session_name = ?, start_timestamp = ?, end_timestamp = ?,
                        content_generated = ?, content_saved = ?, generation_config = ?
                    WHERE session_id = ?
                """, (
                    session.session_name,
                    session.start_timestamp,
                    session.end_timestamp,
                    session.content_generated,
                    session.content_saved,
                    json.dumps(session.generation_config) if session.generation_config else None,
                    session.session_id
                ))
            else:
                # Создаем новую сессию
                self.cursor.execute("""
                    INSERT INTO content_sessions (
                        session_id, session_name, start_timestamp, end_timestamp,
                        content_generated, content_saved, generation_config
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.session_name,
                    session.start_timestamp,
                    session.end_timestamp,
                    session.content_generated,
                    session.content_saved,
                    json.dumps(session.generation_config) if session.generation_config else None
                ))
            
            # Сохраняем изменения
            self.connection.commit()
            
            # Обновляем статистику
            self.system_stats['database_operations'] += 1
            
            logger.debug(f"Сессия сохранена: {session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")
            return False
    
    def update_session(self, session: ContentSession) -> bool:
        """Обновление сессии"""
        try:
            return self.save_session(session)
        except Exception as e:
            logger.error(f"Ошибка обновления сессии: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[ContentSession]:
        """Получение сессии по ID"""
        try:
            if session_id in self.content_sessions:
                return self.content_sessions[session_id]
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения сессии: {e}")
            return None
    
    def get_all_sessions(self) -> List[ContentSession]:
        """Получение всех сессий"""
        try:
            return list(self.content_sessions.values())
        except Exception as e:
            logger.error(f"Ошибка получения всех сессий: {e}")
            return []
    
    def search_content_items(self, 
                           content_type: Optional[ContentType] = None,
                           rarity: Optional[ContentRarity] = None,
                           min_level: Optional[int] = None,
                           max_level: Optional[int] = None,
                           session_id: Optional[str] = None) -> List[ContentItem]:
        """Поиск элементов контента по критериям"""
        try:
            query = "SELECT * FROM content_items WHERE 1=1"
            params = []
            
            if content_type:
                query += " AND content_type = ?"
                params.append(content_type.value)
            
            if rarity:
                query += " AND rarity = ?"
                params.append(rarity.value)
            
            if min_level is not None:
                query += " AND level_requirement >= ?"
                params.append(min_level)
            
            if max_level is not None:
                query += " AND level_requirement <= ?"
                params.append(max_level)
            
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            
            query += " ORDER BY generation_timestamp DESC"
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            content_items = []
            for row in rows:
                content_item = ContentItem(
                    uuid=row['uuid'],
                    content_type=ContentType(row['content_type']),
                    name=row['name'],
                    description=row['description'],
                    rarity=ContentRarity(row['rarity']),
                    level_requirement=row['level_requirement'],
                    session_id=row['session_id'],
                    generation_timestamp=row['generation_timestamp'],
                    data=json.loads(row['data']),
                    is_saved=bool(row['is_saved'])
                )
                content_items.append(content_item)
            
            return content_items
            
        except Exception as e:
            logger.error(f"Ошибка поиска элементов контента: {e}")
            return []
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """Получение статистики контента"""
        try:
            stats = {}
            
            # Статистика по типам контента
            self.cursor.execute("""
                SELECT content_type, COUNT(*) as count
                FROM content_items
                GROUP BY content_type
            """)
            
            for row in self.cursor.fetchall():
                stats[f"{row['content_type']}_count"] = row['count']
            
            # Статистика по редкости
            self.cursor.execute("""
                SELECT rarity, COUNT(*) as count
                FROM content_items
                GROUP BY rarity
            """)
            
            for row in self.cursor.fetchall():
                stats[f"{row['rarity']}_count"] = row['count']
            
            # Статистика по уровням
            self.cursor.execute("""
                SELECT 
                    CASE 
                        WHEN level_requirement <= 5 THEN '1-5'
                        WHEN level_requirement <= 10 THEN '6-10'
                        WHEN level_requirement <= 20 THEN '11-20'
                        ELSE '21+'
                    END as level_range,
                    COUNT(*) as count
                FROM content_items
                GROUP BY level_range
            """)
            
            for row in self.cursor.fetchall():
                stats[f"level_{row['level_range']}_count"] = row['count']
            
            # Общая статистика
            stats['total_items'] = self.system_stats['total_items']
            stats['saved_items'] = self.system_stats['saved_items']
            stats['sessions_count'] = len(self.content_sessions)
            stats['slots_count'] = len(self.content_slots)
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики контента: {e}")
            return {}
    
    def backup_database(self, backup_path: str) -> bool:
        """Создание резервной копии базы данных"""
        try:
            import shutil
            
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Создаем резервную копию
            shutil.copy2(self.db_path, backup_file)
            
            logger.info(f"Резервная копия создана: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Восстановление базы данных из резервной копии"""
        try:
            import shutil
            
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"Файл резервной копии не найден: {backup_path}")
                return False
            
            # Закрываем текущее подключение
            if self.connection:
                self.connection.close()
            
            # Восстанавливаем из резервной копии
            shutil.copy2(backup_file, self.db_path)
            
            # Пересоздаем подключение
            self._create_database_connection()
            
            # Перезагружаем данные
            self._load_existing_data()
            
            logger.info(f"База данных восстановлена из резервной копии: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка восстановления базы данных: {e}")
            return False
