#!/usr/bin/env python3
"""Интерфейсы для архитектуры системы"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Callable
from dataclasses import dataclass, field

# = БАЗОВЫЕ ТИПЫ

class SystemPriority(Enum):
    """Приоритеты систем"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

class SystemState(Enum):
    """Состояния систем"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"

class ComponentType(Enum):
    """Типы компонентов"""
    SYSTEM = "system"
    MANAGER = "manager"
    SERVICE = "service"
    REPOSITORY = "repository"
    FACTORY = "factory"
    CONTROLLER = "controller"
    UTILITY = "utility"
    ADAPTER = "adapter"

# = БАЗОВЫЕ ИНТЕРФЕЙСЫ

class ISystem(ABC):
    """Базовый интерфейс для всех систем"""
    
    @property
    @abstractmethod
    def system_id(self) -> str:
        """Уникальный идентификатор системы"""
        pass
    
    @property
    @abstractmethod
    def system_name(self) -> str:
        """Название системы"""
        pass
    
    @property
    @abstractmethod
    def system_priority(self) -> SystemPriority:
        """Приоритет системы"""
        pass
    
    @property
    @abstractmethod
    def system_state(self) -> SystemState:
        """Текущее состояние системы"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация системы"""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Запуск системы"""
        pass
    
    @abstractmethod
    def pause(self) -> bool:
        """Приостановка системы"""
        pass
    
    @abstractmethod
    def resume(self) -> bool:
        """Возобновление системы"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Остановка системы"""
        pass
    
    @abstractmethod
    def destroy(self) -> bool:
        """Уничтожение системы"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Обновление системы"""
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Получение диагностической информации о системе."""
        pass

class IManager(ABC):
    """Базовый интерфейс для всех менеджеров"""
    
    @property
    @abstractmethod
    def manager_id(self) -> str:
        """Уникальный идентификатор менеджера"""
        pass
    
    @property
    @abstractmethod
    def managed_components(self) -> List[str]:
        """Список управляемых компонентов"""
        pass
    
    @abstractmethod
    def register_component(self, component_id: str, component: Any) -> bool:
        """Регистрация компонента"""
        pass
    
    @abstractmethod
    def unregister_component(self, component_id: str) -> bool:
        """Отмена регистрации компонента"""
        pass
    
    @abstractmethod
    def get_component(self, component_id: str) -> Optional[Any]:
        """Получение компонента"""
        pass

class IService(ABC):
    """Базовый интерфейс для всех сервисов"""
    
    @property
    @abstractmethod
    def service_id(self) -> str:
        """Уникальный идентификатор сервиса"""
        pass
    
    @property
    @abstractmethod
    def service_type(self) -> str:
        """Тип сервиса"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """Получение информации о сервисе"""
        pass

class IRepository(ABC):
    """Базовый интерфейс для всех репозиториев"""
    
    @property
    @abstractmethod
    def repository_id(self) -> str:
        """Уникальный идентификатор репозитория"""
        pass
    
    @property
    @abstractmethod
    def data_type(self) -> str:
        """Тип данных"""
        pass
    
    @abstractmethod
    def store(self, key: str, data: Any) -> bool:
        """Сохранение данных"""
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Получение данных"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Удаление данных"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Проверка существования данных"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Очистка репозитория"""
        pass

class IFactory(ABC):
    """Базовый интерфейс для всех фабрик"""
    
    @property
    @abstractmethod
    def factory_id(self) -> str:
        """Уникальный идентификатор фабрики"""
        pass
    
    @property
    @abstractmethod
    def product_type(self) -> str:
        """Тип производимого продукта"""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> Any:
        """Создание продукта"""
        pass
    
    @abstractmethod
    def can_create(self, **kwargs) -> bool:
        """Проверка возможности создания"""
        pass

class IController(ABC):
    """Базовый интерфейс для всех контроллеров"""
    
    @property
    @abstractmethod
    def controller_id(self) -> str:
        """Уникальный идентификатор контроллера"""
        pass
    
    @property
    @abstractmethod
    def controlled_systems(self) -> List[str]:
        """Список управляемых систем"""
        pass
    
    @abstractmethod
    def control_system(self, system_id: str, command: str, **kwargs) -> bool:
        """Управление системой"""
        pass
    
    @abstractmethod
    def get_control_status(self, system_id: str) -> Dict[str, Any]:
        """Получение статуса управления"""
        pass

class IUtility(ABC):
    """Базовый интерфейс для всех утилит"""
    
    @property
    @abstractmethod
    def utility_id(self) -> str:
        """Уникальный идентификатор утилиты"""
        pass
    
    @property
    @abstractmethod
    def utility_type(self) -> str:
        """Тип утилиты"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Выполнение утилиты"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Проверка доступности утилиты"""
        pass

class IAdapter(ABC):
    """Базовый интерфейс для всех адаптеров"""
    
    @property
    @abstractmethod
    def adapter_id(self) -> str:
        """Уникальный идентификатор адаптера"""
        pass
    
    @property
    @abstractmethod
    def source_type(self) -> str:
        """Тип источника"""
        pass
    
    @property
    @abstractmethod
    def target_type(self) -> str:
        """Тип цели"""
        pass
    
    @abstractmethod
    def adapt(self, source: Any) -> Any:
        """Адаптация данных"""
        pass
    
    @abstractmethod
    def can_adapt(self, source: Any) -> bool:
        """Проверка возможности адаптации"""
        pass

# = СПЕЦИАЛИЗИРОВАННЫЕ ИНТЕРФЕЙСЫ

class IGameSystem(ISystem):
    """Интерфейс для игровых систем"""
    
    @abstractmethod
    def get_game_data(self) -> Dict[str, Any]:
        """Получение игровых данных"""
        pass
    
    @abstractmethod
    def set_game_data(self, data: Dict[str, Any]) -> bool:
        """Установка игровых данных"""
        pass

class IAudioSystem(ISystem):
    """Интерфейс для аудио систем"""
    
    @abstractmethod
    def play_sound(self, sound_id: str, volume: float = 1.0) -> bool:
        """Воспроизведение звука"""
        pass
    
    @abstractmethod
    def stop_sound(self, sound_id: str) -> bool:
        """Остановка звука"""
        pass
    
    @abstractmethod
    def set_volume(self, volume: float) -> bool:
        """Установка громкости"""
        pass

class IVisualSystem(ISystem):
    """Интерфейс для визуальных систем"""
    
    @abstractmethod
    def render(self, scene_data: Dict[str, Any]) -> bool:
        """Рендеринг сцены"""
        pass
    
    @abstractmethod
    def update_camera(self, camera_data: Dict[str, Any]) -> bool:
        """Обновление камеры"""
        pass
    
    @abstractmethod
    def add_visual_effect(self, effect_data: Dict[str, Any]) -> bool:
        """Добавление визуального эффекта"""
        pass

class IInputSystem(ISystem):
    """Интерфейс для систем ввода"""
    
    @abstractmethod
    def get_input_state(self) -> Dict[str, Any]:
        """Получение состояния ввода"""
        pass
    
    @abstractmethod
    def register_input_handler(self, input_type: str, handler: Callable) -> bool:
        """Регистрация обработчика ввода"""
        pass
    
    @abstractmethod
    def unregister_input_handler(self, input_type: str) -> bool:
        """Отмена регистрации обработчика ввода"""
        pass

class INetworkSystem(ISystem):
    """Интерфейс для сетевых систем"""
    
    @abstractmethod
    def connect(self, address: str, port: int) -> bool:
        """Подключение к серверу"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Отключение от сервера"""
        pass
    
    @abstractmethod
    def send_data(self, data: Any) -> bool:
        """Отправка данных"""
        pass
    
    @abstractmethod
    def receive_data(self) -> Optional[Any]:
        """Получение данных"""
        pass

# = ДЕКОРАТОРЫ И УТИЛИТЫ

def implements_interface(interface_class):
    """Декоратор для проверки реализации интерфейса"""
    def decorator(cls):
        if not issubclass(cls, interface_class):
            raise TypeError(f"Класс {cls.__name__} должен реализовывать интерфейс {interface_class.__name__}")
        return cls
    return decorator

def validate_interface_implementation(obj: Any, interface_class: Type) -> bool:
    """Проверка реализации интерфейса объектом"""
    if not isinstance(obj, interface_class):
        return False
    
    # Проверяем наличие всех абстрактных методов
    for method_name in interface_class.__abstractmethods__:
        if not hasattr(obj, method_name):
            return False
    
    return True
