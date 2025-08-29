#!/usr/bin/env python3
"""
Улучшенная архитектура для AI-EVOLVE
Модульная архитектура с принципом единой ответственности
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Callable
from dataclasses import dataclass, field
import logging
import time
import threading
from contextlib import contextmanager

# ============================================================================
# БАЗОВЫЕ ИНТЕРФЕЙСЫ АРХИТЕКТУРЫ
# ============================================================================

class ComponentType(Enum):
    """Типы компонентов архитектуры"""
    SYSTEM = "system"
    MANAGER = "manager"
    SERVICE = "service"
    REPOSITORY = "repository"
    FACTORY = "factory"
    CONTROLLER = "controller"
    UTILITY = "utility"
    ADAPTER = "adapter"

class LifecycleState(Enum):
    """Состояния жизненного цикла компонента"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"

class Priority(Enum):
    """Приоритеты компонентов"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

# ============================================================================
# БАЗОВЫЕ КЛАССЫ АРХИТЕКТУРЫ
# ============================================================================

class IComponent(ABC):
    """Базовый интерфейс для всех компонентов архитектуры"""
    
    @property
    @abstractmethod
    def component_id(self) -> str:
        """Уникальный идентификатор компонента"""
        pass
    
    @property
    @abstractmethod
    def component_type(self) -> ComponentType:
        """Тип компонента"""
        pass
    
    @property
    @abstractmethod
    def priority(self) -> Priority:
        """Приоритет компонента"""
        pass
    
    @property
    @abstractmethod
    def state(self) -> LifecycleState:
        """Текущее состояние компонента"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация компонента"""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Запуск компонента"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Остановка компонента"""
        pass
    
    @abstractmethod
    def destroy(self) -> bool:
        """Уничтожение компонента"""
        pass

# ============================================================================
# БАЗОВЫЕ РЕАЛИЗАЦИИ
# ============================================================================

class BaseComponent(IComponent):
    """Базовая реализация компонента"""
    
    def __init__(self, component_id: str, component_type: ComponentType, priority: Priority = Priority.NORMAL):
        self._component_id = component_id
        self._component_type = component_type
        self._priority = priority
        self._state = LifecycleState.UNINITIALIZED
        self._logger = logging.getLogger(f"{__name__}.{component_id}")
        
    @property
    def component_id(self) -> str:
        return self._component_id
    
    @property
    def component_type(self) -> ComponentType:
        return self._component_type
    
    @property
    def priority(self) -> Priority:
        return self._priority
    
    @property
    def state(self) -> LifecycleState:
        return self._state
    
    def initialize(self) -> bool:
        """Инициализация компонента"""
        try:
            self._state = LifecycleState.INITIALIZING
            if self._on_initialize():
                self._state = LifecycleState.READY
                self._logger.info(f"Компонент {self.component_id} успешно инициализирован")
                return True
            else:
                self._state = LifecycleState.ERROR
                self._logger.error(f"Ошибка инициализации компонента {self.component_id}")
                return False
        except Exception as e:
            self._state = LifecycleState.ERROR
            self._logger.error(f"Исключение при инициализации {self.component_id}: {e}")
            return False
    
    def start(self) -> bool:
        """Запуск компонента"""
        if self._state != LifecycleState.READY:
            self._logger.warning(f"Нельзя запустить компонент {self.component_id} в состоянии {self._state}")
            return False
        
        try:
            self._state = LifecycleState.RUNNING
            if self._on_start():
                self._logger.info(f"Компонент {self.component_id} запущен")
                return True
            else:
                self._state = LifecycleState.ERROR
                return False
        except Exception as e:
            self._state = LifecycleState.ERROR
            self._logger.error(f"Исключение при запуске {self.component_id}: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка компонента"""
        if self._state not in [LifecycleState.RUNNING, LifecycleState.PAUSED]:
            return True
        
        try:
            self._state = LifecycleState.STOPPING
            if self._on_stop():
                self._state = LifecycleState.READY
                self._logger.info(f"Компонент {self.component_id} остановлен")
                return True
            else:
                self._state = LifecycleState.ERROR
                return False
        except Exception as e:
            self._state = LifecycleState.ERROR
            self._logger.error(f"Исключение при остановке {self.component_id}: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение компонента"""
        try:
            self._state = LifecycleState.STOPPING
            if self._on_destroy():
                self._state = LifecycleState.DESTROYED
                self._logger.info(f"Компонент {self.component_id} уничтожен")
                return True
            else:
                return False
        except Exception as e:
            self._logger.error(f"Исключение при уничтожении {self.component_id}: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка компонента"""
        if self._state != LifecycleState.RUNNING:
            return False
        
        try:
            self._state = LifecycleState.PAUSED
            self._on_pause()
            return True
        except Exception as e:
            self._logger.error(f"Исключение при приостановке {self.component_id}: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление компонента"""
        if self._state != LifecycleState.PAUSED:
            return False
        
        try:
            self._state = LifecycleState.RUNNING
            self._on_resume()
            return True
        except Exception as e:
            self._logger.error(f"Исключение при возобновлении {self.component_id}: {e}")
            return False
    
    # Методы для переопределения в наследниках
    def _on_initialize(self) -> bool:
        """Переопределяется в наследниках для специфичной инициализации"""
        return True
    
    def _on_start(self) -> bool:
        """Переопределяется в наследниках для специфичного запуска"""
        return True
    
    def _on_stop(self) -> bool:
        """Переопределяется в наследниках для специфичной остановки"""
        return True
    
    def _on_destroy(self) -> bool:
        """Переопределяется в наследниках для специфичного уничтожения"""
        return True
    
    def _on_pause(self):
        """Переопределяется в наследниках для специфичной приостановки"""
        pass
    
    def _on_resume(self):
        """Переопределяется в наследниках для специфичного возобновления"""
        pass

# ============================================================================
# МЕНЕДЖЕР КОМПОНЕНТОВ
# ============================================================================

class ComponentManager:
    """Менеджер компонентов архитектуры"""
    
    def __init__(self):
        self._components: Dict[str, IComponent] = {}
        self._components_by_type: Dict[ComponentType, List[IComponent]] = {}
        self._components_by_priority: Dict[Priority, List[IComponent]] = {}
        self._logger = logging.getLogger(__name__)
        
        # Инициализация словарей по типам и приоритетам
        for component_type in ComponentType:
            self._components_by_type[component_type] = []
        for priority in Priority:
            self._components_by_priority[priority] = []
    
    def register_component(self, component: IComponent) -> bool:
        """Регистрация компонента"""
        try:
            if component.component_id in self._components:
                self._logger.warning(f"Компонент {component.component_id} уже зарегистрирован")
                return False
            
            # Регистрируем компонент
            self._components[component.component_id] = component
            self._components_by_type[component.component_type].append(component)
            self._components_by_priority[component.priority].append(component)
            
            self._logger.info(f"Компонент {component.component_id} зарегистрирован")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка регистрации компонента {component.component_id}: {e}")
            return False
    
    def unregister_component(self, component_id: str) -> bool:
        """Отмена регистрации компонента"""
        try:
            if component_id not in self._components:
                return False
            
            component = self._components[component_id]
            
            # Удаляем из всех словарей
            self._components_by_type[component.component_type].remove(component)
            self._components_by_priority[component.priority].remove(component)
            del self._components[component_id]
            
            self._logger.info(f"Компонент {component_id} отменен")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка отмены регистрации {component_id}: {e}")
            return False
    
    def get_component(self, component_id: str) -> Optional[IComponent]:
        """Получение компонента по ID"""
        return self._components.get(component_id)
    
    def get_components_by_type(self, component_type: ComponentType) -> List[IComponent]:
        """Получение компонентов по типу"""
        return self._components_by_type.get(component_type, []).copy()
    
    def get_components_by_priority(self, priority: Priority) -> List[IComponent]:
        """Получение компонентов по приоритету"""
        return self._components_by_priority.get(priority, []).copy()
    
    def initialize_all(self) -> bool:
        """Инициализация всех компонентов по приоритету"""
        try:
            for priority in Priority:
                components = self._components_by_priority[priority]
                for component in components:
                    if not component.initialize():
                        self._logger.error(f"Ошибка инициализации {component.component_id}")
                        return False
            return True
        except Exception as e:
            self._logger.error(f"Ошибка массовой инициализации: {e}")
            return False
    
    def start_all(self) -> bool:
        """Запуск всех компонентов по приоритету"""
        try:
            for priority in Priority:
                components = self._components_by_priority[priority]
                for component in components:
                    if not component.start():
                        self._logger.error(f"Ошибка запуска {component.component_id}")
                        return False
            return True
        except Exception as e:
            self._logger.error(f"Ошибка массового запуска: {e}")
            return False
    
    def stop_all(self) -> bool:
        """Остановка всех компонентов по приоритету (в обратном порядке)"""
        try:
            for priority in reversed(list(Priority)):
                components = self._components_by_priority[priority]
                for component in components:
                    if not component.stop():
                        self._logger.error(f"Ошибка остановки {component.component_id}")
                        return False
            return True
        except Exception as e:
            self._logger.error(f"Ошибка массовой остановки: {e}")
            return False
    
    def destroy_all(self) -> bool:
        """Уничтожение всех компонентов"""
        try:
            for priority in reversed(list(Priority)):
                components = self._components_by_priority[priority]
                for component in components:
                    if not component.destroy():
                        self._logger.error(f"Ошибка уничтожения {component.component_id}")
                        return False
            return True
        except Exception as e:
            self._logger.error(f"Ошибка массового уничтожения: {e}")
            return False

# ============================================================================
# ШИНА СОБЫТИЙ
# ============================================================================

class EventBus:
    """Шина событий для межкомпонентного взаимодействия"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 1000
        self._logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: str, callback: Callable) -> bool:
        """Подписка на событие"""
        try:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                self._logger.debug(f"Подписка на {event_type}: {callback}")
                return True
            
            return False
        except Exception as e:
            self._logger.error(f"Ошибка подписки на {event_type}: {e}")
            return False
    
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """Отписка от события"""
        try:
            if event_type in self._subscribers:
                if callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
                    self._logger.debug(f"Отписка от {event_type}: {callback}")
                    return True
            
            return False
        except Exception as e:
            self._logger.error(f"Ошибка отписки от {event_type}: {e}")
            return False
    
    def publish(self, event_type: str, data: Any = None) -> bool:
        """Публикация события"""
        try:
            event = {
                'type': event_type,
                'data': data,
                'timestamp': time.time()
            }
            
            # Добавляем в историю
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # Уведомляем подписчиков
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        self._logger.error(f"Ошибка в callback для {event_type}: {e}")
            
            self._logger.debug(f"Событие опубликовано: {event_type}")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка публикации события {event_type}: {e}")
            return False
    
    def get_event_history(self, event_type: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Получение истории событий"""
        try:
            if event_type:
                history = [e for e in self._event_history if e['type'] == event_type]
            else:
                history = self._event_history.copy()
            
            if limit:
                history = history[-limit:]
            
            return history
        except Exception as e:
            self._logger.error(f"Ошибка получения истории событий: {e}")
            return []

# ============================================================================
# СИСТЕМА СОБЫТИЙ
# ============================================================================

@dataclass
class Event:
    """Базовый класс для событий"""
    event_type: str
    data: Any = None
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    target: Optional[str] = None
    priority: Priority = Priority.NORMAL
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

def create_event(event_type: str, data: Any = None, source: str = None, 
                target: str = None, priority: Priority = Priority.NORMAL) -> Event:
    """Создание события"""
    return Event(
        event_type=event_type,
        data=data,
        source=source,
        target=target,
        priority=priority
    )

# ============================================================================
# УТИЛИТЫ
# ============================================================================

@contextmanager
def component_lifecycle(component: IComponent):
    """Контекстный менеджер для жизненного цикла компонента"""
    try:
        if not component.initialize():
            raise RuntimeError(f"Ошибка инициализации {component.component_id}")
        
        if not component.start():
            raise RuntimeError(f"Ошибка запуска {component.component_id}")
        
        yield component
        
    finally:
        component.stop()
        component.destroy()

def validate_component(component: IComponent) -> bool:
    """Валидация компонента"""
    try:
        # Проверяем обязательные атрибуты
        required_attrs = ['component_id', 'component_type', 'priority', 'state']
        for attr in required_attrs:
            if not hasattr(component, attr):
                return False
        
        # Проверяем обязательные методы
        required_methods = ['initialize', 'start', 'stop', 'destroy']
        for method in required_methods:
            if not hasattr(component, method) or not callable(getattr(component, method)):
                return False
        
        return True
    except Exception:
        return False
