#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА СОБЫТИЙ
Централизованная система событий для связи между модулями
Соблюдает принцип единой ответственности
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import weakref

from utils.logging_system import get_logger, log_system_event

class EventPriority(Enum):
    """Приоритеты событий"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class EventType(Enum):
    """Типы событий"""
    GAME_STATE = "game_state"
    PLAYER = "player"
    COMBAT = "combat"
    INVENTORY = "inventory"
    UI = "ui"
    AUDIO = "audio"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"
    CUSTOM = "custom"

@dataclass
class Event:
    """Событие"""
    event_type: str
    event_id: str
    data: Dict[str, Any]
    timestamp: float
    priority: EventPriority = EventPriority.NORMAL
    source: str = ""
    target: Optional[str] = None
    processed: bool = False

@dataclass
class EventHandler:
    """Обработчик событий"""
    handler_id: str
    callback: Callable
    event_types: List[str]
    priority: EventPriority = EventPriority.NORMAL
    once: bool = False
    enabled: bool = True
    created_at: float = 0.0

class EventSystem:
    """Система событий"""
    
    def __init__(self, max_queue_size: int = 1000):
        self.max_queue_size = max_queue_size
        
        # Очереди событий по приоритету
        self.event_queues: Dict[EventPriority, deque] = {
            priority: deque(maxlen=max_queue_size)
            for priority in EventPriority
        }
        
        # Обработчики событий
        self.handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self.handler_registry: Dict[str, EventHandler] = {}
        
        # Статистика
        self.events_processed = 0
        self.events_dropped = 0
        self.handlers_executed = 0
        
        # Поток обработки событий
        self.processing_thread: Optional[threading.Thread] = None
        self.running = False
        self.processing_enabled = True
        
        # Настройки
        self.async_processing = True
        self.max_handlers_per_event = 10
        self.event_timeout = 5.0  # Таймаут обработки события
        
        self.logger = get_logger("event_system")
        
        # Инициализация
        self._initialize_system()
        
        log_system_event("event_system", "initialized")
    
    def _initialize_system(self):
        """Инициализация системы"""
        try:
            # Запускаем поток обработки событий
            if self.async_processing:
                self.running = True
                self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
                self.processing_thread.start()
            
            # Регистрируем системные обработчики
            self._register_system_handlers()
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации системы событий: {e}")
    
    def _register_system_handlers(self):
        """Регистрация системных обработчиков"""
        # Обработчик для логирования событий
        self.register_handler(
            "system_logger",
            self._log_event,
            ["*"],  # Все события
            EventPriority.LOW
        )
        
        # Обработчик для статистики
        self.register_handler(
            "system_stats",
            self._update_statistics,
            ["*"],  # Все события
            EventPriority.LOW
        )
    
    def emit_event(self, event_type: str, event_id: str, data: Dict[str, Any] = None,
                  priority: EventPriority = EventPriority.NORMAL, source: str = "",
                  target: Optional[str] = None) -> bool:
        """Отправка события"""
        try:
            if not self.processing_enabled:
                return False
            
            # Создаем событие
            event = Event(
                event_type=event_type,
                event_id=event_id,
                data=data or {},
                timestamp=time.time(),
                priority=priority,
                source=source,
                target=target
            )
            
            # Добавляем в очередь
            queue = self.event_queues[priority]
            if len(queue) >= queue.maxlen:
                # Удаляем самое старое событие
                queue.popleft()
                self.events_dropped += 1
            
            queue.append(event)
            
            # Синхронная обработка если отключена асинхронная
            if not self.async_processing:
                self._process_event(event)
            
            log_system_event("event_system", "event_emitted", {
                "event_type": event_type,
                "event_id": event_id,
                "priority": priority.value,
                "source": source
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки события: {e}")
            return False
    
    def register_handler(self, handler_id: str, callback: Callable, 
                        event_types: List[str], priority: EventPriority = EventPriority.NORMAL,
                        once: bool = False) -> bool:
        """Регистрация обработчика событий"""
        try:
            # Проверяем существование обработчика
            if handler_id in self.handler_registry:
                self.logger.warning(f"Обработчик уже зарегистрирован: {handler_id}")
                return False
            
            # Создаем обработчик
            handler = EventHandler(
                handler_id=handler_id,
                callback=callback,
                event_types=event_types,
                priority=priority,
                once=once,
                created_at=time.time()
            )
            
            # Регистрируем обработчик
            self.handler_registry[handler_id] = handler
            
            # Добавляем в списки по типам событий
            for event_type in event_types:
                self.handlers[event_type].append(handler)
            
            # Сортируем по приоритету
            self.handlers[event_type].sort(key=lambda h: h.priority.value, reverse=True)
            
            log_system_event("event_system", "handler_registered", {
                "handler_id": handler_id,
                "event_types": event_types,
                "priority": priority.value
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка регистрации обработчика {handler_id}: {e}")
            return False
    
    def unregister_handler(self, handler_id: str) -> bool:
        """Отмена регистрации обработчика"""
        try:
            if handler_id not in self.handler_registry:
                return False
            
            handler = self.handler_registry[handler_id]
            
            # Удаляем из списков по типам событий
            for event_type in handler.event_types:
                if event_type in self.handlers:
                    self.handlers[event_type] = [
                        h for h in self.handlers[event_type] 
                        if h.handler_id != handler_id
                    ]
            
            # Удаляем из реестра
            del self.handler_registry[handler_id]
            
            log_system_event("event_system", "handler_unregistered", {
                "handler_id": handler_id
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка отмены регистрации обработчика {handler_id}: {e}")
            return False
    
    def _processing_loop(self):
        """Основной цикл обработки событий"""
        while self.running:
            try:
                if not self.processing_enabled:
                    time.sleep(0.01)
                    continue
                
                # Обрабатываем события по приоритету
                events_processed = 0
                for priority in [EventPriority.CRITICAL, EventPriority.HIGH, 
                               EventPriority.NORMAL, EventPriority.LOW]:
                    queue = self.event_queues[priority]
                    
                    while queue and events_processed < 100:  # Лимит за итерацию
                        event = queue.popleft()
                        self._process_event(event)
                        events_processed += 1
                
                if events_processed == 0:
                    time.sleep(0.001)  # Небольшая пауза если нет событий
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле обработки событий: {e}")
                time.sleep(0.1)
    
    def _process_event(self, event: Event):
        """Обработка события"""
        try:
            if event.processed:
                return
            
            # Получаем обработчики для типа события
            handlers = self._get_handlers_for_event(event)
            
            if not handlers:
                return
            
            # Ограничиваем количество обработчиков
            handlers = handlers[:self.max_handlers_per_event]
            
            # Выполняем обработчики
            for handler in handlers:
                if not handler.enabled:
                    continue
                
                try:
                    # Проверяем таймаут
                    start_time = time.time()
                    
                    # Выполняем обработчик
                    handler.callback(event)
                    
                    # Проверяем время выполнения
                    execution_time = time.time() - start_time
                    if execution_time > self.event_timeout:
                        self.logger.warning(f"Обработчик {handler.handler_id} выполняется слишком долго: {execution_time:.2f}s")
                    
                    self.handlers_executed += 1
                    
                    # Удаляем одноразовый обработчик
                    if handler.once:
                        self.unregister_handler(handler.handler_id)
                    
                except Exception as e:
                    self.logger.error(f"Ошибка в обработчике {handler.handler_id}: {e}")
            
            event.processed = True
            self.events_processed += 1
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки события {event.event_id}: {e}")
    
    def _get_handlers_for_event(self, event: Event) -> List[EventHandler]:
        """Получение обработчиков для события"""
        handlers = []
        
        # Обработчики для конкретного типа
        if event.event_type in self.handlers:
            handlers.extend(self.handlers[event.event_type])
        
        # Обработчики для всех событий (*)
        if "*" in self.handlers:
            handlers.extend(self.handlers["*"])
        
        # Фильтруем по target если указан
        if event.target:
            handlers = [h for h in handlers if h.handler_id == event.target]
        
        return handlers
    
    def _log_event(self, event: Event):
        """Логирование события"""
        self.logger.debug(f"Событие: {event.event_type}.{event.event_id} от {event.source}")
    
    def _update_statistics(self, event: Event):
        """Обновление статистики"""
        # Статистика обновляется в _process_event
        pass
    
    def wait_for_event(self, event_type: str, timeout: float = 5.0) -> Optional[Event]:
        """Ожидание события"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Проверяем все очереди
                for priority in [EventPriority.CRITICAL, EventPriority.HIGH, 
                               EventPriority.NORMAL, EventPriority.LOW]:
                    queue = self.event_queues[priority]
                    
                    for event in queue:
                        if event.event_type == event_type and not event.processed:
                            return event
                
                time.sleep(0.01)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка ожидания события: {e}")
            return None
    
    def clear_events(self, event_type: Optional[str] = None):
        """Очистка событий"""
        try:
            if event_type:
                # Очищаем события конкретного типа
                for queue in self.event_queues.values():
                    queue[:] = [e for e in queue if e.event_type != event_type]
            else:
                # Очищаем все события
                for queue in self.event_queues.values():
                    queue.clear()
            
            log_system_event("event_system", "events_cleared", {
                "event_type": event_type or "all"
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки событий: {e}")
    
    def pause_processing(self):
        """Приостановка обработки событий"""
        self.processing_enabled = False
        log_system_event("event_system", "processing_paused")
    
    def resume_processing(self):
        """Возобновление обработки событий"""
        self.processing_enabled = True
        log_system_event("event_system", "processing_resumed")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Получение статуса очередей"""
        return {
            priority.value: len(queue)
            for priority, queue in self.event_queues.items()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return {
            "events_processed": self.events_processed,
            "events_dropped": self.events_dropped,
            "handlers_executed": self.handlers_executed,
            "total_handlers": len(self.handler_registry),
            "queue_status": self.get_queue_status(),
            "processing_enabled": self.processing_enabled,
            "async_processing": self.async_processing,
            "handlers_by_type": {
                event_type: len(handlers)
                for event_type, handlers in self.handlers.items()
            }
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.running = False
        
        # Ждем завершения потока
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)
        
        # Очищаем все события
        self.clear_events()
        
        # Очищаем обработчики
        self.handlers.clear()
        self.handler_registry.clear()
        
        log_system_event("event_system", "cleanup_completed")
