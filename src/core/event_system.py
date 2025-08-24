#!/usr/bin/env python3
"""
Event System - Система событий для улучшения модульности
Реализует паттерн Observer для снижения связанности между системами
"""

import logging
import time
from typing import Dict, List, Any, Callable, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from .interfaces import IEventEmitter, IEventSubscriber

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Приоритеты событий"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Event:
    """Событие"""
    event_type: str
    data: Any
    timestamp: float
    source: str
    priority: EventPriority = EventPriority.NORMAL

@dataclass
class EventSubscription:
    """Подписка на событие"""
    callback: Callable
    priority: EventPriority
    subscriber_id: str

class EventSystem(IEventEmitter):
    """
    Центральная система событий
    Обеспечивает связь между различными системами игры
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, List[EventSubscription]] = defaultdict(list)
        self.event_queue: deque = deque(maxlen=1000)
        self.is_initialized = False
        
        # Статистика
        self.events_processed = 0
        self.events_emitted = 0
        
        logger.info("Система событий инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы событий"""
        try:
            self.is_initialized = True
            logger.info("Система событий успешно инициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации системы событий: {e}")
            return False
    
    def emit_event(self, event_type: str, data: Any, source: str = "unknown", 
                   priority: EventPriority = EventPriority.NORMAL) -> None:
        """Эмиссия события"""
        if not self.is_initialized:
            logger.warning("Система событий не инициализирована")
            return
        
        try:
            event = Event(
                event_type=event_type,
                data=data,
                timestamp=time.time(),
                source=source,
                priority=priority
            )
            
            # Добавляем событие в очередь
            self.event_queue.append(event)
            self.events_emitted += 1
            
            logger.debug(f"Событие {event_type} добавлено в очередь от {source}")
            
        except Exception as e:
            logger.error(f"Ошибка эмиссии события {event_type}: {e}")
    
    def subscribe(self, event_type: str, callback: Callable, 
                  subscriber_id: str = "unknown", 
                  priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Подписка на событие"""
        try:
            subscription = EventSubscription(
                callback=callback,
                priority=priority,
                subscriber_id=subscriber_id
            )
            
            self.subscriptions[event_type].append(subscription)
            
            # Сортируем по приоритету (высокий приоритет первым)
            self.subscriptions[event_type].sort(
                key=lambda x: x.priority.value, reverse=True
            )
            
            logger.debug(f"Подписка на {event_type} от {subscriber_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка подписки на {event_type}: {e}")
            return False
    
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """Отписка от события"""
        try:
            if event_type in self.subscriptions:
                # Удаляем все подписки с данным callback
                original_length = len(self.subscriptions[event_type])
                self.subscriptions[event_type] = [
                    sub for sub in self.subscriptions[event_type]
                    if sub.callback != callback
                ]
                
                removed_count = original_length - len(self.subscriptions[event_type])
                if removed_count > 0:
                    logger.debug(f"Отписано {removed_count} подписок от {event_type}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка отписки от {event_type}: {e}")
            return False
    
    def unsubscribe_all(self, subscriber_id: str) -> int:
        """Отписка от всех событий для конкретного подписчика"""
        try:
            removed_count = 0
            
            for event_type in list(self.subscriptions.keys()):
                original_length = len(self.subscriptions[event_type])
                self.subscriptions[event_type] = [
                    sub for sub in self.subscriptions[event_type]
                    if sub.subscriber_id != subscriber_id
                ]
                
                removed_count += original_length - len(self.subscriptions[event_type])
                
                # Удаляем пустые списки подписок
                if not self.subscriptions[event_type]:
                    del self.subscriptions[event_type]
            
            if removed_count > 0:
                logger.debug(f"Отписано {removed_count} подписок для {subscriber_id}")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Ошибка массовой отписки для {subscriber_id}: {e}")
            return 0
    
    def process_events(self) -> int:
        """Обработка всех событий в очереди"""
        if not self.is_initialized:
            return 0
        
        try:
            processed_count = 0
            
            # Обрабатываем события по приоритету
            while self.event_queue:
                # Находим событие с наивысшим приоритетом
                highest_priority_event = max(self.event_queue, 
                                           key=lambda e: e.priority.value)
                
                # Удаляем его из очереди
                self.event_queue.remove(highest_priority_event)
                
                # Обрабатываем событие
                if self._process_single_event(highest_priority_event):
                    processed_count += 1
                    self.events_processed += 1
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Ошибка обработки событий: {e}")
            return 0
    
    def _process_single_event(self, event: Event) -> bool:
        """Обработка одного события"""
        try:
            if event.event_type not in self.subscriptions:
                return False
            
            # Вызываем все подписчики
            for subscription in self.subscriptions[event.event_type]:
                try:
                    subscription.callback(event)
                except Exception as e:
                    logger.error(f"Ошибка в callback {subscription.subscriber_id} "
                               f"для события {event.event_type}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обработки события {event.event_type}: {e}")
            return False
    
    def get_subscription_count(self, event_type: str = None) -> int:
        """Получение количества подписок"""
        if event_type:
            return len(self.subscriptions.get(event_type, []))
        else:
            return sum(len(subs) for subs in self.subscriptions.values())
    
    def get_queue_size(self) -> int:
        """Получение размера очереди событий"""
        return len(self.event_queue)
    
    def clear_queue(self) -> None:
        """Очистка очереди событий"""
        self.event_queue.clear()
        logger.debug("Очередь событий очищена")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики системы событий"""
        return {
            'events_processed': self.events_processed,
            'events_emitted': self.events_emitted,
            'queue_size': len(self.event_queue),
            'subscription_count': self.get_subscription_count(),
            'event_types': list(self.subscriptions.keys())
        }
    
    def update(self, delta_time: float) -> None:
        """Обновление системы событий"""
        # Обрабатываем события
        processed = self.process_events()
        if processed > 0:
            logger.debug(f"Обработано {processed} событий")
    
    def cleanup(self) -> None:
        """Очистка системы событий"""
        logger.info("Очистка системы событий...")
        
        try:
            # Отписываем всех подписчиков
            for event_type in list(self.subscriptions.keys()):
                self.subscriptions[event_type].clear()
            
            self.subscriptions.clear()
            self.event_queue.clear()
            self.is_initialized = False
            
            # Сбрасываем статистику
            self.events_processed = 0
            self.events_emitted = 0
            
            logger.info("Система событий очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы событий: {e}")

class EventSubscriber(IEventSubscriber):
    """
    Базовый класс для подписчиков на события
    Упрощает работу с системой событий
    """
    
    def __init__(self, event_system: EventSystem, subscriber_id: str):
        self.event_system = event_system
        self.subscriber_id = subscriber_id
        self.subscribed_events: List[str] = []
    
    def subscribe_to_event(self, event_type: str, callback: Callable = None, 
                          priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Подписка на событие"""
        if callback is None:
            callback = self.on_event
        
        if self.event_system.subscribe(event_type, callback, self.subscriber_id, priority):
            self.subscribed_events.append(event_type)
            return True
        return False
    
    def unsubscribe_from_event(self, event_type: str) -> bool:
        """Отписка от события"""
        if self.event_system.unsubscribe(event_type, self.on_event):
            if event_type in self.subscribed_events:
                self.subscribed_events.remove(event_type)
            return True
        return False
    
    def unsubscribe_from_all_events(self) -> int:
        """Отписка от всех событий"""
        removed_count = self.event_system.unsubscribe_all(self.subscriber_id)
        self.subscribed_events.clear()
        return removed_count
    
    def on_event(self, event: Event) -> None:
        """Обработка события (переопределяется в наследниках)"""
        logger.debug(f"Событие {event.event_type} получено подписчиком {self.subscriber_id}")
    
    def cleanup(self) -> None:
        """Очистка подписчика"""
        self.unsubscribe_from_all_events()

# Глобальный экземпляр системы событий
_global_event_system: Optional[EventSystem] = None

def get_global_event_system() -> EventSystem:
    """Получение глобального экземпляра системы событий"""
    global _global_event_system
    if _global_event_system is None:
        _global_event_system = EventSystem()
        _global_event_system.initialize()
    return _global_event_system

def set_global_event_system(event_system: EventSystem) -> None:
    """Установка глобального экземпляра системы событий"""
    global _global_event_system
    _global_event_system = event_system
