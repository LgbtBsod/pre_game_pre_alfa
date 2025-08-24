#!/usr/bin/env python3
"""
Core Interfaces - Интерфейсы для всех систем
Обеспечивают принцип единой ответственности и модульность
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum

class GameState(Enum):
    """Состояния игры"""
    INITIALIZING = "initializing"
    MAIN_MENU = "main_menu"
    LOADING = "loading"
    PLAYING = "playing"
    PAUSED = "paused"
    SETTINGS = "settings"
    QUITTING = "quitting"

class ISystem(ABC):
    """Базовый интерфейс для всех систем"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация системы"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Обновление системы"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Очистка системы"""
        pass

class IRenderable(ABC):
    """Интерфейс для рендерируемых объектов"""
    
    @abstractmethod
    def render(self, render_node) -> None:
        """Отрисовка объекта"""
        pass
    
    @abstractmethod
    def set_visible(self, visible: bool) -> None:
        """Установка видимости"""
        pass

class IUpdatable(ABC):
    """Интерфейс для обновляемых объектов"""
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Обновление объекта"""
        pass

class IEventEmitter(ABC):
    """Интерфейс для эмиттеров событий"""
    
    @abstractmethod
    def emit_event(self, event_type: str, data: Any) -> None:
        """Эмиссия события"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, callback) -> None:
        """Подписка на событие"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, callback) -> None:
        """Отписка от события"""
        pass

class IEventSubscriber(ABC):
    """Интерфейс для подписчиков на события"""
    
    @abstractmethod
    def on_event(self, event_type: str, data: Any) -> None:
        """Обработка события"""
        pass

class IResourceManager(ISystem):
    """Интерфейс менеджера ресурсов"""
    
    @abstractmethod
    def load_resource(self, resource_path: str, resource_type: str) -> Any:
        """Загрузка ресурса"""
        pass
    
    @abstractmethod
    def unload_resource(self, resource_path: str) -> bool:
        """Выгрузка ресурса"""
        pass
    
    @abstractmethod
    def get_resource(self, resource_path: str) -> Optional[Any]:
        """Получение ресурса"""
        pass
    
    @abstractmethod
    def is_resource_loaded(self, resource_path: str) -> bool:
        """Проверка загрузки ресурса"""
        pass

class ISceneManager(ISystem):
    """Интерфейс менеджера сцен"""
    
    @abstractmethod
    def register_scene(self, name: str, scene) -> bool:
        """Регистрация сцены"""
        pass
    
    @abstractmethod
    def set_active_scene(self, name: str) -> bool:
        """Установка активной сцены"""
        pass
    
    @abstractmethod
    def get_active_scene(self):
        """Получение активной сцены"""
        pass
    
    @abstractmethod
    def switch_to_scene(self, name: str, transition_type: str = "instant") -> bool:
        """Переключение на сцену"""
        pass

class IPerformanceManager(ISystem):
    """Интерфейс менеджера производительности"""
    
    @abstractmethod
    def get_fps(self) -> float:
        """Получение FPS"""
        pass
    
    @abstractmethod
    def get_frame_time(self) -> float:
        """Получение времени кадра"""
        pass
    
    @abstractmethod
    def get_memory_usage(self) -> Dict[str, Any]:
        """Получение использования памяти"""
        pass
    
    @abstractmethod
    def start_profiling(self, name: str) -> None:
        """Начало профилирования"""
        pass
    
    @abstractmethod
    def end_profiling(self, name: str) -> None:
        """Завершение профилирования"""
        pass

class IConfigManager(ISystem):
    """Интерфейс менеджера конфигурации"""
    
    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        pass
    
    @abstractmethod
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Сохранение конфигурации"""
        pass
    
    @abstractmethod
    def get_value(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        pass
    
    @abstractmethod
    def set_value(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        pass

class IGameEngine(ISystem):
    """Интерфейс игрового движка"""
    
    @abstractmethod
    def run(self) -> None:
        """Запуск игрового цикла"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Остановка игрового цикла"""
        pass
    
    @abstractmethod
    def pause(self) -> None:
        """Пауза игры"""
        pass
    
    @abstractmethod
    def resume(self) -> None:
        """Возобновление игры"""
        pass
    
    @abstractmethod
    def change_state(self, new_state: GameState) -> None:
        """Изменение состояния игры"""
        pass
    
    @abstractmethod
    def get_state(self) -> GameState:
        """Получение текущего состояния"""
        pass

class IEntity(ISystem, IRenderable, IUpdatable):
    """Интерфейс игровой сущности"""
    
    @abstractmethod
    def get_id(self) -> str:
        """Получение ID сущности"""
        pass
    
    @abstractmethod
    def get_position(self) -> tuple:
        """Получение позиции"""
        pass
    
    @abstractmethod
    def set_position(self, position: tuple) -> None:
        """Установка позиции"""
        pass
    
    @abstractmethod
    def get_rotation(self) -> tuple:
        """Получение поворота"""
        pass
    
    @abstractmethod
    def set_rotation(self, rotation: tuple) -> None:
        """Установка поворота"""
        pass
    
    @abstractmethod
    def get_scale(self) -> tuple:
        """Получение масштаба"""
        pass
    
    @abstractmethod
    def set_scale(self, scale: tuple) -> None:
        """Установка масштаба"""
        pass

class IComponent(ISystem):
    """Интерфейс компонента сущности"""
    
    @abstractmethod
    def get_entity(self) -> IEntity:
        """Получение родительской сущности"""
        pass
    
    @abstractmethod
    def set_entity(self, entity: IEntity) -> None:
        """Установка родительской сущности"""
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """Получение типа компонента"""
        pass

class ISystemManager(ISystem):
    """Интерфейс менеджера систем"""
    
    @abstractmethod
    def add_system(self, name: str, system: ISystem) -> bool:
        """Добавление системы"""
        pass
    
    @abstractmethod
    def remove_system(self, name: str) -> bool:
        """Удаление системы"""
        pass
    
    @abstractmethod
    def get_system(self, name: str) -> Optional[ISystem]:
        """Получение системы"""
        pass
    
    @abstractmethod
    def update_all_systems(self, delta_time: float) -> None:
        """Обновление всех систем"""
        pass
