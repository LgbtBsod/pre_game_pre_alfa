#!/usr/bin/env python3
"""Система событий - централизованное управление событиями игры"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

# = ТИПЫ СОБЫТИЙ

class EventType(Enum):
    """Типы событий"""
    SYSTEM = "system"              # Системные события
    GAME = "game"                  # Игровые события
    UI = "ui"                      # События интерфейса
    AUDIO = "audio"                # Аудио события
    NETWORK = "network"            # Сетевые события
    DEBUG = "debug"                # Отладочные события

class EventPriority(Enum):
    """Приоритеты событий"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class EventState(Enum):
    """Состояния событий"""
    PENDING = "pending"            # Ожидает обработки
    PROCESSING = "processing"      # Обрабатывается
    COMPLETED = "completed"        # Завершено
    FAILED = "failed"              # Завершилось с ошибкой
    CANCELLED = "cancelled"        # Отменено

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class Event:
    """Событие"""
    event_id: str
    event_type: str
    event_data: Dict[str, Any]
    source: str
    timestamp: float = field(default_factory=time.time)
    priority: EventPriority = EventPriority.NORMAL
    state: EventState = EventState.PENDING
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None

@dataclass
class EventHandler:
    """Обработчик события"""
    handler_id: str
    handler_func: Callable
    event_types: List[str]
    priority: EventPriority = EventPriority.NORMAL
    is_active: bool = True
    last_called: float = 0.0
    call_count: int = 0
    error_count: int = 0

@dataclass
class EventSubscription:
    """Подписка на событие"""
    subscriber_id: str
    event_type: str
    handler: Callable
    priority: EventPriority = EventPriority.NORMAL
    is_active: bool = True
    created_at: float = field(default_factory=time.time)

class EventSystem:
    """Система событий"""
    
    def __init__(self):
        self.event_handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self.event_queue: deque = deque()
        self.subscriptions: Dict[str, List[EventSubscription]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history_size = 1000
        self.is_running = False
        self.processing_thread = None
        self.lock = threading.Lock()
        
        # Статистика
        self.stats = {
            'events_processed': 0,
            'events_failed': 0,
            'handlers_registered': 0,
            'subscriptions_active': 0
        }
        
        logger.info("EventSystem инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы событий"""
        try:
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._event_processing_loop, daemon=True)
            self.processing_thread.start()
            logger.info("EventSystem успешно инициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации EventSystem: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Завершение работы системы событий"""
        try:
            self.is_running = False
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=5.0)
            logger.info("EventSystem успешно завершена")
            return True
        except Exception as e:
            logger.error(f"Ошибка завершения EventSystem: {e}")
            return False
    
    def emit(self, event_type: str, event_data: Dict[str, Any], source: str = "system", 
             priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Отправка события"""
        try:
            event = Event(
                event_id=f"{event_type}_{int(time.time() * 1000)}",
                event_type=event_type,
                event_data=event_data,
                source=source,
                priority=priority
            )
            
            with self.lock:
                self.event_queue.append(event)
                self.event_history.append(event)
                
                # Ограничиваем размер истории
                if len(self.event_history) > self.max_history_size:
                    self.event_history.pop(0)
            
            logger.debug(f"Событие {event_type} добавлено в очередь от {source}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки события {event_type}: {e}")
            return False
    
    def on(self, event_type: str, handler: Callable, subscriber_id: str = "unknown", 
            priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Подписка на событие"""
        try:
            subscription = EventSubscription(
                subscriber_id=subscriber_id,
                event_type=event_type,
                handler=handler,
                priority=priority
            )
            
            with self.lock:
                self.subscriptions[event_type].append(subscription)
                self.stats['subscriptions_active'] += 1
            
            logger.debug(f"Подписка на {event_type} от {subscriber_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка подписки на {event_type}: {e}")
            return False
    
    def off(self, event_type: str, subscriber_id: str) -> bool:
        """Отписка от события"""
        try:
            with self.lock:
                if event_type in self.subscriptions:
                    self.subscriptions[event_type] = [
                        sub for sub in self.subscriptions[event_type]
                        if sub.subscriber_id != subscriber_id
                    ]
                    self.stats['subscriptions_active'] = len([
                        sub for subs in self.subscriptions.values()
                        for sub in subs if sub.is_active
                    ])
            
            logger.debug(f"Отписка от {event_type} для {subscriber_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отписки от {event_type}: {e}")
            return False
    
    def subscribe(self, event_type: str, handler: Callable, subscriber_id: str = "unknown", 
                  priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Alias compatible with EventBus.on(event_type, handler, priority)."""
        return self.on(event_type, handler, subscriber_id, priority)
    
    def unsubscribe(self, event_type: str, subscriber_id: str) -> bool:
        """Alias для отписки"""
        return self.off(event_type, subscriber_id)
    
    def emit_event(self, event_type: str, event_data: Dict[str, Any], source: str = "system", 
                   priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Alias для emit"""
        return self.emit(event_type, event_data, source, priority)
    
    def _event_processing_loop(self):
        """Основной цикл обработки событий"""
        while self.is_running:
            try:
                if self.event_queue:
                    with self.lock:
                        if self.event_queue:
                            # Обрабатываем событие с наивысшим приоритетом
                            highest_priority_event = max(self.event_queue,
                                                       key=lambda e: e.priority.value)
                            self.event_queue.remove(highest_priority_event)
                            
                            if self._process_single_event(highest_priority_event):
                                self.stats['events_processed'] += 1
                            else:
                                self.stats['events_failed'] += 1
                
                time.sleep(0.001)  # Небольшая пауза
                
            except Exception as e:
                logger.error(f"Ошибка в цикле обработки событий: {e}")
                time.sleep(0.1)
    
    def _process_single_event(self, event: Event) -> bool:
        """Обработка одного события"""
        try:
            event.state = EventState.PROCESSING
            
            # Находим все подписки на этот тип события
            subscriptions = self.subscriptions.get(event.event_type, [])
            
            if not subscriptions:
                event.state = EventState.COMPLETED
                return True
            
            # Сортируем по приоритету (высокий приоритет первым)
            subscriptions.sort(key=lambda s: s.priority.value, reverse=True)
            
            success_count = 0
            for subscription in subscriptions:
                if not subscription.is_active:
                    continue
                
                try:
                    # Вызываем обработчик
                    subscription.handler(event)
                    subscription.last_called = time.time()
                    subscription.call_count += 1
                    success_count += 1
                    
                except Exception as e:
                    subscription.error_count += 1
                    logger.error(f"Ошибка в обработчике {subscription.subscriber_id} для {event.event_type}: {e}")
            
            if success_count > 0:
                event.state = EventState.COMPLETED
                return True
            else:
                event.state = EventState.FAILED
                return False
                
        except Exception as e:
            event.state = EventState.FAILED
            event.error_message = str(e)
            logger.error(f"Ошибка обработки события {event.event_type}: {e}")
            return False
    
    def process_events(self, max_events: int = 100) -> int:
        """Обработка событий в текущем потоке (для тестов)"""
        processed = 0
        while self.event_queue and processed < max_events:
            with self.lock:
                if self.event_queue:
                    event = self.event_queue.popleft()
                    if self._process_single_event(event):
                        processed += 1
        
        return processed
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        with self.lock:
            return {
                'events_processed': self.stats['events_processed'],
                'events_failed': self.stats['events_failed'],
                'handlers_registered': self.stats['handlers_registered'],
                'subscriptions_active': self.stats['subscriptions_active'],
                'queue_size': len(self.event_queue),
                'history_size': len(self.event_history),
                'is_running': self.is_running
            }
    
    def clear_history(self):
        """Очистка истории событий"""
        with self.lock:
            self.event_history.clear()
            logger.info("История событий очищена")
    
    def get_event_history(self, event_type: Optional[str] = None, 
                         limit: int = 100) -> List[Event]:
        """Получение истории событий"""
        with self.lock:
            if event_type:
                filtered_events = [e for e in self.event_history if e.event_type == event_type]
            else:
                filtered_events = self.event_history.copy()
            
            return filtered_events[-limit:]
