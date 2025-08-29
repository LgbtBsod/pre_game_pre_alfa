#!/usr/bin/env python3
"""
Улучшенная архитектура для AI-EVOLVE
Модульная архитектура с принципом единой ответственности
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic
from dataclasses import dataclass, field
import logging
import time

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
    
    @abstractmethod
    def update(self, delta_time: float) -> bool:
        """Обновление компонента"""
        pass

class BaseComponent(IComponent):
    """Базовая реализация компонента"""
    
    def __init__(self, component_id: str, component_type: ComponentType, priority: Priority = Priority.NORMAL):
        self._component_id = component_id
        self._component_type = component_type
        self._priority = priority
        self._state = LifecycleState.UNINITIALIZED
        self._logger = logging.getLogger(f"{self.__class__.__name__}.{component_id}")
        self._dependencies: List[str] = []
        self._dependents: List[str] = []
        self._last_update = 0.0
        self._update_count = 0
        
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
    
    @state.setter
    def state(self, value: LifecycleState) -> None:
        self._state = value
    
    def add_dependency(self, component_id: str) -> None:
        """Добавление зависимости"""
        if component_id not in self._dependencies:
            self._dependencies.append(component_id)
    
    def add_dependent(self, component_id: str) -> None:
        """Добавление зависимого компонента"""
        if component_id not in self._dependents:
            self._dependents.append(component_id)
    
    def can_start(self) -> bool:
        """Проверка возможности запуска"""
        return self._state in [LifecycleState.READY, LifecycleState.STOPPED]
    
    def can_stop(self) -> bool:
        """Проверка возможности остановки"""
        return self._state in [LifecycleState.RUNNING, LifecycleState.PAUSED]
    
    def initialize(self) -> bool:
        """Базовая инициализация"""
        try:
            if self._state != LifecycleState.UNINITIALIZED:
                self._logger.warning(f"Попытка инициализации в состоянии {self._state}")
                return False
            
            self._state = LifecycleState.INITIALIZING
            self._logger.info("Начало инициализации")
            
            if self._initialize_impl():
                self._state = LifecycleState.READY
                self._logger.info("Инициализация завершена успешно")
                return True
            else:
                self._state = LifecycleState.ERROR
                self._logger.error("Ошибка инициализации")
                return False
                
        except Exception as e:
            self._state = LifecycleState.ERROR
            self._logger.error(f"Исключение при инициализации: {e}")
            return False
    
    def start(self) -> bool:
        """Базовый запуск"""
        try:
            if not self.can_start():
                self._logger.warning(f"Невозможно запустить в состоянии {self._state}")
                return False
            
            self._logger.info("Запуск компонента")
            
            if self._start_impl():
                self._state = LifecycleState.RUNNING
                self._logger.info("Компонент запущен")
                return True
            else:
                self._state = LifecycleState.ERROR
                self._logger.error("Ошибка запуска")
                return False
                
        except Exception as e:
            self._state = LifecycleState.ERROR
            self._logger.error(f"Исключение при запуске: {e}")
            return False
    
    def stop(self) -> bool:
        """Базовая остановка"""
        try:
            if not self.can_stop():
                self._logger.warning(f"Невозможно остановить в состоянии {self._state}")
                return False
            
            self._state = LifecycleState.STOPPING
            self._logger.info("Остановка компонента")
            
            if self._stop_impl():
                self._state = LifecycleState.STOPPED
                self._logger.info("Компонент остановлен")
                return True
            else:
                self._state = LifecycleState.ERROR
                self._logger.error("Ошибка остановки")
                return False
                
        except Exception as e:
            self._state = LifecycleState.ERROR
            self._logger.error(f"Исключение при остановке: {e}")
            return False
    
    def destroy(self) -> bool:
        """Базовое уничтожение"""
        try:
            self._logger.info("Уничтожение компонента")
            
            if self._state in [LifecycleState.RUNNING, LifecycleState.PAUSED]:
                self.stop()
            
            if self._destroy_impl():
                self._state = LifecycleState.DESTROYED
                self._logger.info("Компонент уничтожен")
                return True
            else:
                self._logger.error("Ошибка уничтожения")
                return False
                
        except Exception as e:
            self._logger.error(f"Исключение при уничтожении: {e}")
            return False
    
    def update(self, delta_time: float) -> bool:
        """Базовое обновление"""
        try:
            if self._state != LifecycleState.RUNNING:
                return True
            
            current_time = time.time()
            if self._update_impl(delta_time):
                self._last_update = current_time
                self._update_count += 1
                return True
            else:
                self._logger.warning("Ошибка обновления")
                return False
                
        except Exception as e:
            self._logger.error(f"Исключение при обновлении: {e}")
            return False
    
    # Методы для переопределения в наследниках
    def _initialize_impl(self) -> bool:
        """Реализация инициализации"""
        return True
    
    def _start_impl(self) -> bool:
        """Реализация запуска"""
        return True
    
    def _stop_impl(self) -> bool:
        """Реализация остановки"""
        return True
    
    def _destroy_impl(self) -> bool:
        """Реализация уничтожения"""
        return True
    
    def _update_impl(self, delta_time: float) -> bool:
        """Реализация обновления"""
        return True

# ============================================================================
# СИСТЕМА СОБЫТИЙ
# ============================================================================

@dataclass
class Event:
    """Событие системы"""
    event_id: str
    event_type: str
    source_id: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.NORMAL

class IEventBus(ABC):
    """Интерфейс шины событий"""
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: callable, priority: Priority = Priority.NORMAL) -> bool:
        """Подписка на событие"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: callable) -> bool:
        """Отписка от события"""
        pass
    
    @abstractmethod
    def publish(self, event: Event) -> bool:
        """Публикация события"""
        pass
    
    @abstractmethod
    def process_events(self) -> int:
        """Обработка событий в очереди"""
        pass

class EventBus(BaseComponent, IEventBus):
    """Реализация шины событий"""
    
    def __init__(self):
        super().__init__("event_bus", ComponentType.SERVICE, Priority.CRITICAL)
        self._subscribers: Dict[str, List[tuple]] = {}  # event_type -> [(handler, priority)]
        self._event_queue: List[Event] = []
        self._max_queue_size = 10000
        self._processed_events = 0
    
    def subscribe(self, event_type: str, handler: callable, priority: Priority = Priority.NORMAL) -> bool:
        """Подписка на событие"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        # Проверяем, что обработчик еще не подписан
        for existing_handler, _ in self._subscribers[event_type]:
            if existing_handler == handler:
                return True
        
        self._subscribers[event_type].append((handler, priority))
        # Сортируем по приоритету
        self._subscribers[event_type].sort(key=lambda x: x[1].value)
        return True
    
    def unsubscribe(self, event_type: str, handler: callable) -> bool:
        """Отписка от события"""
        if event_type not in self._subscribers:
            return False
        
        self._subscribers[event_type] = [
            (h, p) for h, p in self._subscribers[event_type] if h != handler
        ]
        return True
    
    def publish(self, event: Event) -> bool:
        """Публикация события"""
        if len(self._event_queue) >= self._max_queue_size:
            self._logger.warning("Очередь событий переполнена")
            return False
        
        self._event_queue.append(event)
        return True

    # --- Aliases for convenience ---
    def on(self, event_type: str, handler: callable, priority: Priority = Priority.NORMAL) -> bool:
        return self.subscribe(event_type, handler, priority)

    def emit(self, event_type: str, data: Dict[str, Any] = None, priority: Priority = Priority.NORMAL) -> bool:
        return self.publish(create_event(event_type, self.component_id, data, priority))
    
    def process_events(self) -> int:
        """Обработка событий в очереди"""
        processed = 0
        
        while self._event_queue and processed < 100:  # Ограничиваем количество событий за раз
            event = self._event_queue.pop(0)
            
            if event.event_type in self._subscribers:
                for handler, _ in self._subscribers[event.event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        self._logger.error(f"Ошибка обработки события {event.event_type}: {e}")
            
            processed += 1
            self._processed_events += 1
        
        return processed
    
    def _update_impl(self, delta_time: float) -> bool:
        """Обновление - обработка событий"""
        self.process_events()
        return True

# ============================================================================
# МЕНЕДЖЕР КОМПОНЕНТОВ
# ============================================================================

class ComponentManager(BaseComponent):
    """Менеджер компонентов архитектуры"""
    
    def __init__(self):
        super().__init__("component_manager", ComponentType.MANAGER, Priority.CRITICAL)
        self._components: Dict[str, IComponent] = {}
        self._component_order: List[str] = []
        self._dependency_graph: Dict[str, List[str]] = {}
        self._event_bus: Optional[EventBus] = None
    
    def register_component(self, component: IComponent) -> bool:
        """Регистрация компонента"""
        if component.component_id in self._components:
            self._logger.warning(f"Компонент {component.component_id} уже зарегистрирован")
            return False
        
        self._components[component.component_id] = component
        self._dependency_graph[component.component_id] = []
        
        # Обновляем порядок инициализации
        self._update_component_order()
        
        self._logger.info(f"Компонент {component.component_id} зарегистрирован")
        return True
    
    def unregister_component(self, component_id: str) -> bool:
        """Отмена регистрации компонента"""
        if component_id not in self._components:
            return False
        
        component = self._components[component_id]
        
        # Останавливаем и уничтожаем компонент
        if component.state in [LifecycleState.RUNNING, LifecycleState.PAUSED]:
            component.stop()
        
        if component.state != LifecycleState.DESTROYED:
            component.destroy()
        
        # Удаляем из всех структур
        del self._components[component_id]
        if component_id in self._dependency_graph:
            del self._dependency_graph[component_id]
        
        self._component_order = [cid for cid in self._component_order if cid != component_id]
        
        self._logger.info(f"Компонент {component_id} отменен")
        return True
    
    def add_dependency(self, component_id: str, dependency_id: str) -> bool:
        """Добавление зависимости между компонентами"""
        if component_id not in self._components or dependency_id not in self._components:
            return False
        
        if dependency_id not in self._dependency_graph[component_id]:
            self._dependency_graph[component_id].append(dependency_id)
            self._update_component_order()
        
        return True
    
    def get_component(self, component_id: str) -> Optional[IComponent]:
        """Получение компонента по ID"""
        return self._components.get(component_id)
    
    def get_components_by_type(self, component_type: ComponentType) -> List[IComponent]:
        """Получение компонентов по типу"""
        return [c for c in self._components.values() if c.component_type == component_type]
    
    def initialize_all(self) -> bool:
        """Инициализация всех компонентов в правильном порядке"""
        self._logger.info("Начало инициализации всех компонентов")
        
        for component_id in self._component_order:
            component = self._components[component_id]
            
            if component.state != LifecycleState.UNINITIALIZED:
                continue
            
            self._logger.info(f"Инициализация компонента {component_id}")
            
            if not component.initialize():
                self._logger.error(f"Ошибка инициализации компонента {component_id}")
                return False
        
        self._logger.info("Все компоненты инициализированы")
        return True
    
    def start_all(self) -> bool:
        """Запуск всех компонентов"""
        self._logger.info("Начало запуска всех компонентов")
        
        for component_id in self._component_order:
            component = self._components[component_id]
            
            if not component.can_start():
                continue
            
            self._logger.info(f"Запуск компонента {component_id}")
            
            if not component.start():
                self._logger.error(f"Ошибка запуска компонента {component_id}")
                return False
        
        self._logger.info("Все компоненты запущены")
        return True
    
    def stop_all(self) -> bool:
        """Остановка всех компонентов"""
        self._logger.info("Начало остановки всех компонентов")
        
        # Останавливаем в обратном порядке
        for component_id in reversed(self._component_order):
            component = self._components[component_id]
            
            if not component.can_stop():
                continue
            
            self._logger.info(f"Остановка компонента {component_id}")
            
            if not component.stop():
                self._logger.error(f"Ошибка остановки компонента {component_id}")
                return False
        
        self._logger.info("Все компоненты остановлены")
        return True
    
    def update_all(self, delta_time: float) -> bool:
        """Обновление всех компонентов"""
        for component_id in self._component_order:
            component = self._components[component_id]
            
            if component.state == LifecycleState.RUNNING:
                if not component.update(delta_time):
                    self._logger.warning(f"Ошибка обновления компонента {component_id}")
        
        return True
    
    def _update_component_order(self) -> None:
        """Обновление порядка инициализации компонентов"""
        # Топологическая сортировка для правильного порядка инициализации
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(component_id: str):
            if component_id in temp_visited:
                raise ValueError(f"Циклическая зависимость обнаружена: {component_id}")
            
            if component_id in visited:
                return
            
            temp_visited.add(component_id)
            
            for dependency_id in self._dependency_graph.get(component_id, []):
                if dependency_id in self._components:
                    visit(dependency_id)
            
            temp_visited.remove(component_id)
            visited.add(component_id)
            order.append(component_id)
        
        for component_id in self._components:
            if component_id not in visited:
                visit(component_id)
        
        self._component_order = order

# ============================================================================
# УТИЛИТЫ АРХИТЕКТУРЫ
# ============================================================================

def create_event(event_type: str, source_id: str, data: Dict[str, Any] = None, priority: Priority = Priority.NORMAL) -> Event:
    """Создание события"""
    return Event(
        event_id=f"{event_type}_{int(time.time() * 1000)}",
        event_type=event_type,
        source_id=source_id,
        timestamp=time.time(),
        data=data or {},
        priority=priority
    )

def validate_component_dependencies(component: IComponent, manager: ComponentManager) -> bool:
    """Валидация зависимостей компонента"""
    for dependency_id in component._dependencies:
        if not manager.get_component(dependency_id):
            return False
    return True
