#!/usr/bin/env python3
"""
Оптимизированная система событий.
Включает асинхронную обработку, приоритеты и автоматическую очистку.
"""

import time
import threading
import queue
import weakref
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum, auto
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Приоритеты обработки событий"""
    CRITICAL = auto()    # Критические события (ввод, сеть)
    HIGH = auto()        # Высокий приоритет (физика, анимация)
    NORMAL = auto()      # Обычный приоритет (логика игры)
    LOW = auto()         # Низкий приоритет (UI, эффекты)
    BACKGROUND = auto()  # Фоновые задачи


class GameEvents(Enum):
    """Типы игровых событий"""
    # Системные события
    GAME_START = "game_start"
    GAME_PAUSE = "game_pause"
    GAME_RESUME = "game_resume"
    GAME_QUIT = "game_quit"
    
    # События игрока
    PLAYER_MOVE = "player_move"
    PLAYER_ATTACK = "player_attack"
    PLAYER_DAMAGE = "player_damage"
    PLAYER_HEAL = "player_heal"
    PLAYER_LEVEL_UP = "player_level_up"
    PLAYER_DEATH = "player_death"
    
    # События мира
    WORLD_UPDATE = "world_update"
    WEATHER_CHANGE = "weather_change"
    TIME_CHANGE = "time_change"
    
    # События боя
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"
    ENEMY_SPAWN = "enemy_spawn"
    ENEMY_DEATH = "enemy_death"
    
    # События предметов
    ITEM_PICKUP = "item_pickup"
    ITEM_USE = "item_use"
    INVENTORY_CHANGE = "inventory_change"
    
    # События квестов
    QUEST_START = "quest_start"
    QUEST_COMPLETE = "quest_complete"
    QUEST_FAIL = "quest_fail"
    
    # События UI
    UI_OPEN = "ui_open"
    UI_CLOSE = "ui_close"
    UI_UPDATE = "ui_update"
    
    # События звука
    SOUND_PLAY = "sound_play"
    MUSIC_CHANGE = "music_change"
    
    # События сохранения
    SAVE_GAME = "save_game"
    LOAD_GAME = "load_game"
    
    # Тестовые события
    TEST_EVENT = "test_event"


@dataclass
class Event:
    """Событие игры"""
    event_type: GameEvents
    data: Dict[str, Any]
    timestamp: float = None
    priority: EventPriority = EventPriority.NORMAL
    source: str = "system"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class EventHandler:
    """Обработчик события"""
    
    def __init__(self, handler_id: str, callback: Callable, priority: EventPriority = EventPriority.NORMAL):
        self.handler_id = handler_id
        self.callback = callback
        self.priority = priority
        self.is_active = True
        self.call_count = 0
        self.last_called = 0.0
    
    def call(self, event: Event) -> bool:
        """Вызвать обработчик"""
        if not self.is_active:
            return False
        
        try:
            start_time = time.time()
            self.callback(event)
            self.call_count += 1
            self.last_called = start_time
            return True
        except Exception as e:
            logger.error(f"Ошибка в обработчике событий {self.handler_id}: {e}")
            return False


class EventQueue:
    """Очередь событий с приоритетами"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queues: Dict[EventPriority, queue.Queue] = {
            priority: queue.Queue(maxsize=max_size // len(EventPriority))
            for priority in EventPriority
        }
        self._lock = threading.RLock()
    
    def put(self, event: Event) -> bool:
        """Добавить событие в очередь"""
        try:
            self._queues[event.priority].put_nowait(event)
            return True
        except queue.Full:
            logger.warning(f"Очередь событий переполнена для приоритета {event.priority}")
            return False
    
    def get(self, timeout: float = 0.1) -> Optional[Event]:
        """Получить событие из очереди"""
        # Обрабатываем события по приоритету
        for priority in EventPriority:
            try:
                return self._queues[priority].get_nowait()
            except queue.Empty:
                continue
        
        return None
    
    def get_nowait(self) -> Optional[Event]:
        """Получить событие из очереди без ожидания (для совместимости)"""
        return self.get(timeout=0.0)
    
    def clear(self) -> None:
        """Очистить все очереди"""
        with self._lock:
            for q in self._queues.values():
                while not q.empty():
                    try:
                        q.get_nowait()
                    except queue.Empty:
                        break
    
    def size(self) -> int:
        """Получить общий размер очередей"""
        return sum(q.qsize() for q in self._queues.values())


class EventSystem:
    """Оптимизированная система событий"""
    
    def __init__(self, max_handlers_per_event: int = 50):
        self.max_handlers_per_event = max_handlers_per_event
        
        # Обработчики событий
        self._handlers: Dict[GameEvents, Dict[str, EventHandler]] = defaultdict(dict)
        
        # Очередь событий
        self._event_queue = EventQueue()
        
        # Статистика
        self._stats = {
            'events_processed': 0,
            'events_dropped': 0,
            'handlers_called': 0,
            'errors': 0
        }
        
        # Состояние системы
        self._running = False
        self._processing_thread = None
        self._stop_event = threading.Event()
        
        # Блокировки
        self._handlers_lock = threading.RLock()
        self._stats_lock = threading.RLock()
    
    def start_processing(self) -> bool:
        """Запустить обработку событий"""
        if self._running:
            logger.warning("Система событий уже запущена")
            return False
        
        try:
            self._running = True
            self._stop_event.clear()
            
            # Запускаем поток обработки
            self._processing_thread = threading.Thread(
                target=self._process_events_loop,
                daemon=True,
                name="EventProcessor"
            )
            self._processing_thread.start()
            
            logger.info("Система событий запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска системы событий: {e}")
            self._running = False
            return False
    
    def stop_processing(self) -> None:
        """Остановить обработку событий"""
        if not self._running:
            return
        
        logger.info("Остановка системы событий...")
        
        self._running = False
        self._stop_event.set()
        
        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join(timeout=5)
        
        # Обрабатываем оставшиеся события
        self._process_remaining_events()
        
        logger.info("Система событий остановлена")
    
    def _process_events_loop(self) -> None:
        """Основной цикл обработки событий"""
        while self._running and not self._stop_event.is_set():
            try:
                event = self._event_queue.get(timeout=0.1)
                if event:
                    self._process_event(event)
            except Exception as e:
                logger.error(f"Ошибка в цикле обработки событий: {e}")
                with self._stats_lock:
                    self._stats['errors'] += 1
    
    def _process_remaining_events(self) -> None:
        """Обработать оставшиеся события"""
        processed = 0
        while True:
            event = self._event_queue.get()
            if event is None:
                break
            
            self._process_event(event)
            processed += 1
        
        if processed > 0:
            logger.info(f"Обработано {processed} оставшихся событий")
    
    def _process_event(self, event: Event) -> None:
        """Обработать одно событие"""
        with self._handlers_lock:
            handlers = self._handlers.get(event.event_type, {})
        
        if not handlers:
            return
        
        # Сортируем обработчики по приоритету
        sorted_handlers = sorted(
            handlers.values(),
            key=lambda h: h.priority.value
        )
        
        # Вызываем обработчики
        for handler in sorted_handlers:
            if handler.call(event):
                with self._stats_lock:
                    self._stats['handlers_called'] += 1
            else:
                with self._stats_lock:
                    self._stats['errors'] += 1
        
        with self._stats_lock:
            self._stats['events_processed'] += 1
    
    def subscribe(self, event_type: GameEvents, callback: Callable, 
                 handler_id: str = None, priority: EventPriority = EventPriority.NORMAL) -> str:
        """
        Подписаться на событие
        
        Args:
            event_type: Тип события
            callback: Функция обработчик
            handler_id: ID обработчика (генерируется автоматически если не указан)
            priority: Приоритет обработчика
            
        Returns:
            ID обработчика
        """
        if handler_id is None:
            handler_id = f"{event_type.value}_{id(callback)}_{time.time()}"
        
        with self._handlers_lock:
            if len(self._handlers[event_type]) >= self.max_handlers_per_event:
                logger.warning(f"Достигнут лимит обработчиков для события {event_type}")
                return None
            
            handler = EventHandler(handler_id, callback, priority)
            self._handlers[event_type][handler_id] = handler
        
        logger.debug(f"Подписка на событие {event_type} с ID {handler_id}")
        return handler_id
    
    def unsubscribe(self, event_type: GameEvents, handler_id: str) -> bool:
        """
        Отписаться от события
        
        Args:
            event_type: Тип события
            handler_id: ID обработчика
            
        Returns:
            True если отписка прошла успешно
        """
        with self._handlers_lock:
            if event_type in self._handlers and handler_id in self._handlers[event_type]:
                del self._handlers[event_type][handler_id]
                logger.debug(f"Отписка от события {event_type} с ID {handler_id}")
                return True
        
        return False
    
    def emit(self, event: Event) -> bool:
        """
        Отправить событие в очередь
        
        Args:
            event: Событие для отправки
            
        Returns:
            True если событие добавлено в очередь
        """
        if not self._running:
            logger.warning("Попытка отправить событие в остановленную систему")
            return False
        
        success = self._event_queue.put(event)
        if not success:
            with self._stats_lock:
                self._stats['events_dropped'] += 1
        
        return success
    
    def emit_immediate(self, event: Event) -> None:
        """
        Немедленно обработать событие (синхронно)
        
        Args:
            event: Событие для обработки
        """
        self._process_event(event)
    
    def register_handler(self, event_type: GameEvents, handler: Callable) -> None:
        """Регистрация обработчика события (для совместимости)"""
        handler_id = f"handler_{len(self._handlers.get(event_type, {}))}"
        self.subscribe(event_type, handler, handler_id)
    
    def emit_event(self, event_type: GameEvents, data: Dict[str, Any] = None, 
                  priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Отправка события (для совместимости)"""
        return self.emit_simple(event_type, data, priority)
    
    def process_events(self) -> None:
        """Обработка событий в очереди (для совместимости)"""
        # Обрабатываем несколько событий из очереди
        for _ in range(10):  # Ограничиваем количество обрабатываемых событий
            try:
                event = self._event_queue.get_nowait()
                self._process_event(event)
            except queue.Empty:
                break
    
    def emit_simple(self, event_type: GameEvents, data: Dict[str, Any] = None, 
                   priority: EventPriority = EventPriority.NORMAL, source: str = "system") -> bool:
        """
        Отправить простое событие
        
        Args:
            event_type: Тип события
            data: Данные события
            priority: Приоритет
            source: Источник события
            
        Returns:
            True если событие отправлено
        """
        if data is None:
            data = {}
        
        event = Event(
            event_type=event_type,
            data=data,
            priority=priority,
            source=source
        )
        
        return self.emit(event)
    
    def get_handlers_count(self, event_type: GameEvents = None) -> int:
        """Получить количество обработчиков"""
        with self._handlers_lock:
            if event_type:
                return len(self._handlers.get(event_type, {}))
            else:
                return sum(len(handlers) for handlers in self._handlers.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику системы событий"""
        with self._stats_lock:
            stats = self._stats.copy()
            stats.update({
                'queue_size': self._event_queue.size(),
                'handlers_count': self.get_handlers_count(),
                'running': self._running
            })
            return stats
    
    def clear_handlers(self, event_type: GameEvents = None) -> None:
        """Очистить обработчики событий"""
        with self._handlers_lock:
            if event_type:
                if event_type in self._handlers:
                    del self._handlers[event_type]
            else:
                self._handlers.clear()
        
        logger.info(f"Очищены обработчики для события {event_type if event_type else 'всех событий'}")
    
    def cleanup_inactive_handlers(self) -> int:
        """Очистить неактивные обработчики"""
        cleaned = 0
        
        with self._handlers_lock:
            for event_type in list(self._handlers.keys()):
                handlers = self._handlers[event_type]
                inactive_handlers = [
                    handler_id for handler_id, handler in handlers.items()
                    if not handler.is_active
                ]
                
                for handler_id in inactive_handlers:
                    del handlers[handler_id]
                    cleaned += 1
        
        if cleaned > 0:
            logger.info(f"Очищено {cleaned} неактивных обработчиков")
        
        return cleaned
    
    def shutdown(self) -> None:
        """Завершение работы системы событий"""
        self.stop_processing()
        self.clear_handlers()
        self._event_queue.clear()
        logger.info("Система событий завершена")
    
    def __del__(self):
        """Деструктор"""
        self.shutdown()


# Глобальный экземпляр системы событий
event_system = EventSystem()
# Запускаем систему событий
event_system.start_processing()
