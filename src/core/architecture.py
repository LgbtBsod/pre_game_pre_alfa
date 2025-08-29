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
    
    @abstractmethod
    def update(self, delta_time: float) -> bool:
        """Обновление компонента"""
        pass

class BaseComponent(IComponent):
    """Базовая реализация компонента с улучшенным управлением зависимостями"""
    
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
        self._lock = threading.RLock()
        self._error_count = 0
        self._warning_count = 0
        
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
        with self._lock:
            return self._state
    
    @state.setter
    def state(self, value: LifecycleState) -> None:
        with self._lock:
            self._state = value
    
    def add_dependency(self, component_id: str) -> None:
        """Добавление зависимости"""
        with self._lock:
            if component_id not in self._dependencies:
                self._dependencies.append(component_id)
    
    def add_dependent(self, component_id: str) -> None:
        """Добавление зависимого компонента"""
        with self._lock:
            if component_id not in self._dependents:
                self._dependents.append(component_id)
    
    def can_start(self) -> bool:
        """Проверка возможности запуска"""
        return self._state in [LifecycleState.READY, LifecycleState.STOPPED]
    
    def can_stop(self) -> bool:
        """Проверка возможности остановки"""
        return self._state in [LifecycleState.RUNNING, LifecycleState.PAUSED]
    
    def initialize(self) -> bool:
        """Базовая инициализация с улучшенной обработкой ошибок"""
        try:
            with self._lock:
                if self._state != LifecycleState.UNINITIALIZED:
                    self._logger.warning(f"Попытка инициализации в состоянии {self._state}")
                    return False
                
                self._state = LifecycleState.INITIALIZING
                self._logger.info("Начало инициализации")
            
            if self._initialize_impl():
                with self._lock:
                    self._state = LifecycleState.READY
                self._logger.info("Инициализация завершена успешно")
                return True
            else:
                with self._lock:
                    self._state = LifecycleState.ERROR
                self._logger.error("Ошибка инициализации")
                return False
                
        except Exception as e:
            with self._lock:
                self._state = LifecycleState.ERROR
                self._error_count += 1
            self._logger.error(f"Исключение при инициализации: {e}")
            return False
    
    def start(self) -> bool:
        """Базовый запуск с улучшенной обработкой ошибок"""
        try:
            with self._lock:
                if not self.can_start():
                    self._logger.warning(f"Невозможно запустить в состоянии {self._state}")
                    return False
                
                self._logger.info("Запуск компонента")
            
            if self._start_impl():
                with self._lock:
                    self._state = LifecycleState.RUNNING
                self._logger.info("Компонент запущен")
                return True
            else:
                with self._lock:
                    self._state = LifecycleState.ERROR
                self._logger.error("Ошибка запуска")
                return False
                
        except Exception as e:
            with self._lock:
                self._state = LifecycleState.ERROR
                self._error_count += 1
            self._logger.error(f"Исключение при запуске: {e}")
            return False
    
    def stop(self) -> bool:
        """Базовая остановка с улучшенной обработкой ошибок"""
        try:
            with self._lock:
                if not self.can_stop():
                    self._logger.warning(f"Невозможно остановить в состоянии {self._state}")
                    return False
                
                self._state = LifecycleState.STOPPING
                self._logger.info("Остановка компонента")
            
            if self._stop_impl():
                with self._lock:
                    self._state = LifecycleState.STOPPED
                self._logger.info("Компонент остановлен")
                return True
            else:
                with self._lock:
                    self._state = LifecycleState.ERROR
                self._logger.error("Ошибка остановки")
                return False
                
        except Exception as e:
            with self._lock:
                self._state = LifecycleState.ERROR
                self._error_count += 1
            self._logger.error(f"Исключение при остановке: {e}")
            return False
    
    def destroy(self) -> bool:
        """Базовое уничтожение с улучшенной обработкой ошибок"""
        try:
            self._logger.info("Уничтожение компонента")
            
            with self._lock:
                if self._state in [LifecycleState.RUNNING, LifecycleState.PAUSED]:
                    self.stop()
            
            if self._destroy_impl():
                with self._lock:
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
        """Базовое обновление с улучшенной обработкой ошибок"""
        try:
            with self._lock:
                if self._state != LifecycleState.RUNNING:
                    return True
                
                current_time = time.time()
            
            if self._update_impl(delta_time):
                with self._lock:
                    self._last_update = current_time
                    self._update_count += 1
                return True
            else:
                self._logger.warning("Ошибка обновления")
                return False
                
        except Exception as e:
            with self._lock:
                self._error_count += 1
            self._logger.error(f"Исключение при обновлении: {e}")
            return False
    
    def get_error_count(self) -> int:
        """Получение количества ошибок"""
        with self._lock:
            return self._error_count
    
    def get_warning_count(self) -> int:
        """Получение количества предупреждений"""
        with self._lock:
            return self._warning_count
    
    def reset_error_counters(self) -> None:
        """Сброс счетчиков ошибок"""
        with self._lock:
            self._error_count = 0
            self._warning_count = 0
    
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
    """Событие системы с улучшенной структурой"""
    event_id: str
    event_type: str
    source_id: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)

class IEventBus(ABC):
    """Интерфейс шины событий с улучшенным API"""
    
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
    
    @abstractmethod
    def get_subscriber_count(self, event_type: str) -> int:
        """Получение количества подписчиков на событие"""
        pass

class EventBus(BaseComponent, IEventBus):
    """Реализация шины событий с улучшенной производительностью"""
    
    def __init__(self):
        super().__init__("event_bus", ComponentType.SERVICE, Priority.CRITICAL)
        self._subscribers: Dict[str, List[tuple]] = {}  # event_type -> [(handler, priority)]
        self._event_queue: List[Event] = []
        self._max_queue_size = 10000
        self._processed_events = 0
        self._dropped_events = 0
        self._event_stats: Dict[str, int] = {}
    
    def subscribe(self, event_type: str, handler: callable, priority: Priority = Priority.NORMAL) -> bool:
        """Подписка на событие с проверкой дублирования"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        # Проверяем, что обработчик еще не подписан
        for existing_handler, _ in self._subscribers[event_type]:
            if existing_handler == handler:
                return True
        
        self._subscribers[event_type].append((handler, priority))
        # Сортируем по приоритету
        self._subscribers[event_type].sort(key=lambda x: x[1].value)
        
        # Обновляем статистику
        self._event_stats[event_type] = self._event_stats.get(event_type, 0) + 1
        
        return True
    
    def unsubscribe(self, event_type: str, handler: callable) -> bool:
        """Отписка от события с обновлением статистики"""
        if event_type not in self._subscribers:
            return False
        
        original_count = len(self._subscribers[event_type])
        self._subscribers[event_type] = [
            (h, p) for h, p in self._subscribers[event_type] if h != handler
        ]
        
        if len(self._subscribers[event_type]) < original_count:
            self._event_stats[event_type] = max(0, self._event_stats.get(event_type, 1) - 1)
            return True
        
        return False
    
    def publish(self, event: Event) -> bool:
        """Публикация события с проверкой переполнения"""
        if len(self._event_queue) >= self._max_queue_size:
            self._dropped_events += 1
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
        """Обработка событий в очереди с ограничением по времени"""
        processed = 0
        start_time = time.time()
        max_processing_time = 0.016  # 16ms max
        
        while (self._event_queue and processed < 100 and 
               time.time() - start_time < max_processing_time):
            event = self._event_queue.pop(0)
            
            if event.event_type in self._subscribers:
                for handler, _ in self._subscribers[event.event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        self._logger.error(f"Ошибка обработки события {event.event_type}: {e}")
                        self._error_count += 1
            
            processed += 1
            self._processed_events += 1
        
        return processed
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Получение количества подписчиков на событие"""
        return len(self._subscribers.get(event_type, []))
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Получение статистики событий"""
        return {
            'processed_events': self._processed_events,
            'dropped_events': self._dropped_events,
            'queue_size': len(self._event_queue),
            'subscriber_counts': self._event_stats.copy()
        }
    
    def _update_impl(self, delta_time: float) -> bool:
        """Обновление - обработка событий"""
        self.process_events()
        return True

# ============================================================================
# МЕНЕДЖЕР КОМПОНЕНТОВ
# ============================================================================

class ComponentManager(BaseComponent):
    """Менеджер компонентов архитектуры с улучшенным управлением зависимостями"""
    
    def __init__(self):
        super().__init__("component_manager", ComponentType.MANAGER, Priority.CRITICAL)
        self._components: Dict[str, IComponent] = {}
        self._component_order: List[str] = []
        self._dependency_graph: Dict[str, List[str]] = {}
        self._event_bus: Optional[EventBus] = None
        self._component_stats: Dict[str, Dict[str, Any]] = {}
    
    def register_component(self, component: IComponent) -> bool:
        """Регистрация компонента с проверкой зависимостей"""
        if component.component_id in self._components:
            self._logger.warning(f"Компонент {component.component_id} уже зарегистрирован")
            return False
        
        self._components[component.component_id] = component
        self._dependency_graph[component.component_id] = []
        self._component_stats[component.component_id] = {
            'registration_time': time.time(),
            'update_count': 0,
            'error_count': 0,
            'last_update': 0.0
        }
        
        # Обновляем порядок инициализации
        self._update_component_order()
        
        self._logger.info(f"Компонент {component.component_id} зарегистрирован")
        return True
    
    def unregister_component(self, component_id: str) -> bool:
        """Отмена регистрации компонента с проверкой зависимостей"""
        if component_id not in self._components:
            return False
        
        # Проверяем, не зависит ли от этого компонента кто-то другой
        dependents = [cid for cid, deps in self._dependency_graph.items() 
                     if component_id in deps]
        if dependents:
            self._logger.warning(f"Нельзя удалить компонент {component_id}, от него зависят: {dependents}")
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
        if component_id in self._component_stats:
            del self._component_stats[component_id]
        
        self._component_order = [cid for cid in self._component_order if cid != component_id]
        
        self._logger.info(f"Компонент {component_id} отменен")
        return True
    
    def add_dependency(self, component_id: str, dependency_id: str) -> bool:
        """Добавление зависимости между компонентами с проверкой циклов"""
        if component_id not in self._components or dependency_id not in self._components:
            return False
        
        # Проверяем, не создаст ли это циклическую зависимость
        if self._would_create_cycle(component_id, dependency_id):
            self._logger.error(f"Добавление зависимости {component_id} -> {dependency_id} создаст цикл")
            return False
        
        if dependency_id not in self._dependency_graph[component_id]:
            self._dependency_graph[component_id].append(dependency_id)
            self._update_component_order()
        
        return True
    
    def _would_create_cycle(self, component_id: str, dependency_id: str) -> bool:
        """Проверка, создаст ли зависимость цикл"""
        visited = set()
        temp_visited = set()
        
        def has_cycle(node: str) -> bool:
            if node in temp_visited:
                return True
            if node in visited:
                return False
            
            temp_visited.add(node)
            
            for dep in self._dependency_graph.get(node, []):
                if has_cycle(dep):
                    return True
            
            temp_visited.remove(node)
            visited.add(node)
            return False
        
        # Временно добавляем зависимость
        self._dependency_graph[component_id].append(dependency_id)
        
        # Проверяем на циклы
        has_cycle_result = has_cycle(component_id)
        
        # Убираем временную зависимость
        self._dependency_graph[component_id].remove(dependency_id)
        
        return has_cycle_result
    
    def get_component(self, component_id: str) -> Optional[IComponent]:
        """Получение компонента по ID"""
        return self._components.get(component_id)
    
    def get_components_by_type(self, component_type: ComponentType) -> List[IComponent]:
        """Получение компонентов по типу"""
        return [c for c in self._components.values() if c.component_type == component_type]
    
    def get_component_stats(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Получение статистики компонента"""
        return self._component_stats.get(component_id)
    
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
        """Обновление всех компонентов с обновлением статистики"""
        for component_id in self._component_order:
            component = self._components[component_id]
            
            if component.state == LifecycleState.RUNNING:
                update_start = time.time()
                
                if not component.update(delta_time):
                    self._logger.warning(f"Ошибка обновления компонента {component_id}")
                    self._component_stats[component_id]['error_count'] += 1
                else:
                    # Обновляем статистику
                    self._component_stats[component_id]['update_count'] += 1
                    self._component_stats[component_id]['last_update'] = time.time()
                    self._component_stats[component_id]['error_count'] = component.get_error_count()
        
        return True
    
    def _update_component_order(self) -> None:
        """Обновление порядка инициализации компонентов с улучшенной топологической сортировкой"""
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
# ЦЕНТРАЛИЗОВАННЫЙ МЕНЕДЖЕР ЗАВИСИМОСТЕЙ
# ============================================================================

class DependencyManager(BaseComponent):
    """Централизованный менеджер зависимостей для всей архитектуры"""
    
    def __init__(self):
        super().__init__("dependency_manager", ComponentType.MANAGER, Priority.CRITICAL)
        self._dependency_registry: Dict[str, Dict[str, Any]] = {}
        self._component_registry: Dict[str, Dict[str, Any]] = {}
        self._service_registry: Dict[str, Any] = {}
    
    def register_service(self, service_name: str, service_instance: Any, 
                        service_type: str = "core") -> bool:
        """Регистрация сервиса в глобальном реестре"""
        if service_name in self._service_registry:
            self._logger.warning(f"Сервис {service_name} уже зарегистрирован")
            return False
        
        self._service_registry[service_name] = {
            'instance': service_instance,
            'type': service_type,
            'registration_time': time.time()
        }
        
        self._logger.info(f"Сервис {service_name} зарегистрирован")
        return True
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Получение сервиса по имени"""
        service_info = self._service_registry.get(service_name)
        return service_info['instance'] if service_info else None
    
    def register_component_dependency(self, component_id: str, dependency_name: str, 
                                   dependency_type: str, required: bool = True) -> bool:
        """Регистрация зависимости компонента"""
        if component_id not in self._dependency_registry:
            self._dependency_registry[component_id] = {}
        
        self._dependency_registry[component_id][dependency_name] = {
            'type': dependency_type,
            'required': required,
            'resolved': False,
            'resolved_time': None
        }
        
        return True
    
    def resolve_dependency(self, component_id: str, dependency_name: str, 
                          dependency_instance: Any) -> bool:
        """Разрешение зависимости компонента"""
        if (component_id in self._dependency_registry and 
            dependency_name in self._dependency_registry[component_id]):
            
            self._dependency_registry[component_id][dependency_name].update({
                'resolved': True,
                'resolved_time': time.time(),
                'instance': dependency_instance
            })
            
            return True
        
        return False
    
    def get_component_dependencies(self, component_id: str) -> Dict[str, Any]:
        """Получение зависимостей компонента"""
        return self._dependency_registry.get(component_id, {})
    
    def check_component_ready(self, component_id: str) -> bool:
        """Проверка готовности компонента (все зависимости разрешены)"""
        if component_id not in self._dependency_registry:
            return True
        
        for dep_name, dep_info in self._dependency_registry[component_id].items():
            if dep_info['required'] and not dep_info['resolved']:
                return False
        
        return True
    
    def get_unresolved_dependencies(self, component_id: str) -> List[str]:
        """Получение списка неразрешенных зависимостей"""
        unresolved = []
        if component_id in self._dependency_registry:
            for dep_name, dep_info in self._dependency_registry[component_id].items():
                if dep_info['required'] and not dep_info['resolved']:
                    unresolved.append(dep_name)
        
        return unresolved

# ============================================================================
# УТИЛИТЫ АРХИТЕКТУРЫ
# ============================================================================

def create_event(event_type: str, source_id: str, data: Dict[str, Any] = None, 
                priority: Priority = Priority.NORMAL, metadata: Dict[str, Any] = None) -> Event:
    """Создание события с улучшенной структурой"""
    return Event(
        event_id=f"{event_type}_{int(time.time() * 1000)}",
        event_type=event_type,
        source_id=source_id,
        timestamp=time.time(),
        data=data or {},
        priority=priority,
        metadata=metadata or {}
    )

def validate_component_dependencies(component: IComponent, manager: ComponentManager) -> bool:
    """Валидация зависимостей компонента"""
    for dependency_id in component._dependencies:
        if not manager.get_component(dependency_id):
            return False
    return True

@contextmanager
def component_lifecycle_context(component: IComponent, operation: str):
    """Контекстный менеджер для управления жизненным циклом компонента"""
    try:
        component._logger.info(f"Начало операции: {operation}")
        yield component
        component._logger.info(f"Операция завершена успешно: {operation}")
    except Exception as e:
        component._logger.error(f"Ошибка в операции {operation}: {e}")
        component.state = LifecycleState.ERROR
        raise
