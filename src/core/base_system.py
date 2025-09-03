#!/usr/bin/env python3
"""Базовая система - основа для всех игровых систем"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable

from .interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)

# = БАЗОВЫЕ ТИПЫ

class SystemType(Enum):
    """Типы систем"""
    CORE = "core"                  # Основные системы
    GAME = "game"                  # Игровые системы
    UI = "ui"                      # Системы интерфейса
    AUDIO = "audio"                # Аудио системы
    NETWORK = "network"            # Сетевые системы
    DEBUG = "debug"                # Отладочные системы

class SystemCategory(Enum):
    """Категории систем"""
    ESSENTIAL = "essential"        # Обязательные системы
    OPTIONAL = "optional"          # Опциональные системы
    PLUGIN = "plugin"              # Плагин системы

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class SystemDependency:
    """Зависимость системы"""
    system_name: str
    is_required: bool = True
    version: str = "1.0.0"
    description: str = ""

@dataclass
class SystemConfig:
    """Конфигурация системы"""
    auto_start: bool = False
    auto_pause: bool = False
    update_interval: float = 0.016  # 60 FPS по умолчанию
    max_update_time: float = 0.033  # Максимум 30 FPS
    enable_logging: bool = True
    enable_metrics: bool = False

@dataclass
class SystemMetrics:
    """Метрики системы"""
    total_updates: int = 0
    total_update_time: float = 0.0
    average_update_time: float = 0.0
    max_update_time: float = 0.0
    min_update_time: float = float('inf')
    last_update_time: float = 0.0
    error_count: int = 0
    warning_count: int = 0

class BaseSystem(ISystem):
    """Базовая система - основа для всех игровых систем"""
    
    def __init__(self, system_id: str, system_name: str, system_type: SystemType = SystemType.GAME,
                 priority: SystemPriority = SystemPriority.NORMAL):
        """Инициализация базовой системы"""
        self._system_id = system_id
        self._system_name = system_name
        self._system_type = system_type
        self._priority = priority
        self._state = SystemState.UNINITIALIZED
        
        # Конфигурация и метрики
        self.config = SystemConfig()
        self.metrics = SystemMetrics()
        
        # Зависимости и компоненты
        self.dependencies: List[SystemDependency] = []
        self.managed_components: Dict[str, Any] = {}
        
        # Обработчики событий
        self.event_handlers: Dict[str, Callable] = {}
        
        # Время последнего обновления
        self._last_update_time = 0.0
        
        logger.debug(f"Базовая система {system_name} создана")
    
    # = СВОЙСТВА
    
    @property
    def system_id(self) -> str:
        """Уникальный идентификатор системы"""
        return self._system_id
    
    @property
    def system_name(self) -> str:
        """Название системы"""
        return self._system_name
    
    @property
    def system_type(self) -> SystemType:
        """Тип системы"""
        return self._system_type
    
    @property
    def system_priority(self) -> SystemPriority:
        """Приоритет системы"""
        return self._priority
    
    @property
    def system_state(self) -> SystemState:
        """Текущее состояние системы"""
        return self._state
    
    @property
    def is_initialized(self) -> bool:
        """Проверка инициализации системы"""
        return self._state in [SystemState.READY, SystemState.RUNNING, SystemState.PAUSED]
    
    @property
    def is_running(self) -> bool:
        """Проверка работы системы"""
        return self._state == SystemState.RUNNING
    
    @property
    def is_paused(self) -> bool:
        """Проверка приостановки системы"""
        return self._state == SystemState.PAUSED
    
    # = ЖИЗНЕННЫЙ ЦИКЛ
    
    def initialize(self) -> bool:
        """Инициализация системы"""
        try:
            if self._state != SystemState.UNINITIALIZED:
                logger.warning(f"Система {self._system_name} уже инициализирована")
                return False
            
            self._state = SystemState.INITIALIZING
            logger.info(f"Инициализация системы {self._system_name}")
            
            # Проверяем зависимости
            if not self._check_dependencies():
                self._state = SystemState.ERROR
                logger.error(f"Не удалось проверить зависимости для {self._system_name}")
                return False
            
            # Вызываем пользовательскую инициализацию
            if not self._on_initialize():
                self._state = SystemState.ERROR
                logger.error(f"Пользовательская инициализация {self._system_name} не удалась")
                return False
            
            self._state = SystemState.READY
            logger.info(f"Система {self._system_name} успешно инициализирована")
            return True
            
        except Exception as e:
            self._state = SystemState.ERROR
            logger.error(f"Ошибка инициализации {self._system_name}: {e}")
            return False
    
    def start(self) -> bool:
        """Запуск системы"""
        try:
            if not self.is_initialized:
                logger.error(f"Система {self._system_name} не инициализирована")
                return False
            
            if self.is_running:
                logger.warning(f"Система {self._system_name} уже запущена")
                return True
            
            logger.info(f"Запуск системы {self._system_name}")
            
            # Вызываем пользовательский запуск
            if not self._on_start():
                logger.error(f"Пользовательский запуск {self._system_name} не удался")
                return False
            
            self._state = SystemState.RUNNING
            self._last_update_time = time.time()
            logger.info(f"Система {self._system_name} запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска {self._system_name}: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы"""
        try:
            if not self.is_running:
                logger.warning(f"Система {self._system_name} не запущена")
                return False
            
            logger.info(f"Приостановка системы {self._system_name}")
            
            # Вызываем пользовательскую приостановку
            if not self._on_pause():
                logger.error(f"Пользовательская приостановка {self._system_name} не удалась")
                return False
            
            self._state = SystemState.PAUSED
            logger.info(f"Система {self._system_name} приостановлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка приостановки {self._system_name}: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы"""
        try:
            if not self.is_paused:
                logger.warning(f"Система {self._system_name} не приостановлена")
                return False
            
            logger.info(f"Возобновление системы {self._system_name}")
            
            # Вызываем пользовательское возобновление
            if not self._on_resume():
                logger.error(f"Пользовательское возобновление {self._system_name} не удалось")
                return False
            
            self._state = SystemState.RUNNING
            logger.info(f"Система {self._system_name} возобновлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка возобновления {self._system_name}: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка системы"""
        try:
            if self._state in [SystemState.STOPPED, SystemState.DESTROYED]:
                logger.warning(f"Система {self._system_name} уже остановлена")
                return True
            
            logger.info(f"Остановка системы {self._system_name}")
            
            # Вызываем пользовательскую остановку
            if not self._on_stop():
                logger.error(f"Пользовательская остановка {self._system_name} не удалась")
                return False
            
            self._state = SystemState.STOPPED
            logger.info(f"Система {self._system_name} остановлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки {self._system_name}: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы"""
        try:
            if self._state == SystemState.DESTROYED:
                logger.warning(f"Система {self._system_name} уже уничтожена")
                return True
            
            logger.info(f"Уничтожение системы {self._system_name}")
            
            # Сначала останавливаем
            if self.is_running or self.is_paused:
                self.stop()
            
            # Вызываем пользовательское уничтожение
            if not self._on_destroy():
                logger.error(f"Пользовательское уничтожение {self._system_name} не удалось")
                return False
            
            self._state = SystemState.DESTROYED
            logger.info(f"Система {self._system_name} уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения {self._system_name}: {e}")
            return False
    
    # = ОБНОВЛЕНИЕ
    
    def update(self, delta_time: float) -> None:
        """Обновление системы"""
        try:
            if not self.is_running:
                return
            
            # Проверяем интервал обновления
            current_time = time.time()
            if current_time - self._last_update_time < self.config.update_interval:
                return
            
            # Измеряем время обновления
            update_start_time = time.time()
            
            # Вызываем пользовательское обновление
            self._on_update(delta_time)
            
            # Обновляем метрики
            update_time = time.time() - update_start_time
            self._update_metrics(update_time)
            
            self._last_update_time = current_time
            
        except Exception as e:
            logger.error(f"Ошибка обновления {self._system_name}: {e}")
            self.metrics.error_count += 1
    
    def _update_metrics(self, update_time: float):
        """Обновление метрик системы"""
        self.metrics.total_updates += 1
        self.metrics.total_update_time += update_time
        self.metrics.average_update_time = self.metrics.total_update_time / self.metrics.total_updates
        self.metrics.max_update_time = max(self.metrics.max_update_time, update_time)
        self.metrics.min_update_time = min(self.metrics.min_update_time, update_time)
        self.metrics.last_update_time = update_time
    
    # = ЗАВИСИМОСТИ
    
    def add_dependency(self, system_name: str, is_required: bool = True, 
                      version: str = "1.0.0", description: str = ""):
        """Добавление зависимости"""
        dependency = SystemDependency(
            system_name=system_name,
            is_required=is_required,
            version=version,
            description=description
        )
        self.dependencies.append(dependency)
        logger.debug(f"Добавлена зависимость {system_name} для {self._system_name}")
    
    def _check_dependencies(self) -> bool:
        """Проверка зависимостей"""
        # В базовой реализации просто возвращаем True
        # В реальных системах здесь должна быть проверка доступности зависимостей
        return True
    
    # = КОМПОНЕНТЫ
    
    def register_component(self, component_id: str, component: Any) -> bool:
        """Регистрация компонента"""
        try:
            self.managed_components[component_id] = component
            logger.debug(f"Зарегистрирован компонент {component_id} в {self._system_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка регистрации компонента {component_id}: {e}")
            return False
    
    def unregister_component(self, component_id: str) -> bool:
        """Отмена регистрации компонента"""
        try:
            if component_id in self.managed_components:
                del self.managed_components[component_id]
                logger.debug(f"Отменена регистрация компонента {component_id} в {self._system_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка отмены регистрации компонента {component_id}: {e}")
            return False
    
    def get_component(self, component_id: str) -> Optional[Any]:
        """Получение компонента"""
        return self.managed_components.get(component_id)
    
    # = СОБЫТИЯ
    
    def register_event_handler(self, event_type: str, handler: Callable) -> bool:
        """Регистрация обработчика событий"""
        try:
            self.event_handlers[event_type] = handler
            logger.debug(f"Зарегистрирован обработчик событий {event_type} в {self._system_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка регистрации обработчика событий {event_type}: {e}")
            return False
    
    def unregister_event_handler(self, event_type: str) -> bool:
        """Отмена регистрации обработчика событий"""
        try:
            if event_type in self.event_handlers:
                del self.event_handlers[event_type]
                logger.debug(f"Отменена регистрация обработчика событий {event_type} в {self._system_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка отмены регистрации обработчика событий {event_type}: {e}")
            return False
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка события"""
        try:
            if event_type in self.event_handlers:
                handler = self.event_handlers[event_type]
                return handler(event_data)
            return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type} в {self._system_name}: {e}")
            return False
    
    # = ИНФОРМАЦИЯ О СИСТЕМЕ
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение диагностической информации о системе"""
        return {
            "name": self._system_name,
            "id": self._system_id,
            "type": self._system_type.value,
            "state": self._state.value,
            "priority": self._priority.value,
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "dependencies_count": len(self.dependencies),
            "components_count": len(self.managed_components),
            "event_handlers_count": len(self.event_handlers),
            "metrics": {
                "total_updates": self.metrics.total_updates,
                "average_update_time": self.metrics.average_update_time,
                "max_update_time": self.metrics.max_update_time,
                "error_count": self.metrics.error_count,
                "warning_count": self.metrics.warning_count
            },
            "config": {
                "auto_start": self.config.auto_start,
                "auto_pause": self.config.auto_pause,
                "update_interval": self.config.update_interval,
                "max_update_time": self.config.max_update_time
            }
        }
    
    # = ПОЛЬЗОВАТЕЛЬСКИЕ МЕТОДЫ (переопределяются в наследниках)
    
    def _on_initialize(self) -> bool:
        """Пользовательская инициализация (переопределяется)"""
        return True
    
    def _on_start(self) -> bool:
        """Пользовательский запуск (переопределяется)"""
        return True
    
    def _on_pause(self) -> bool:
        """Пользовательская приостановка (переопределяется)"""
        return True
    
    def _on_resume(self) -> bool:
        """Пользовательское возобновление (переопределяется)"""
        return True
    
    def _on_stop(self) -> bool:
        """Пользовательская остановка (переопределяется)"""
        return True
    
    def _on_destroy(self) -> bool:
        """Пользовательское уничтожение (переопределяется)"""
        return True
    
    def _on_update(self, delta_time: float) -> None:
        """Пользовательское обновление (переопределяется)"""
        pass
    
    # = УТИЛИТЫ
    
    def reset_metrics(self):
        """Сброс метрик системы"""
        self.metrics = SystemMetrics()
        logger.debug(f"Метрики системы {self._system_name} сброшены")
    
    def get_priority(self) -> SystemPriority:
        """Получение приоритета системы"""
        return self._priority
    
    def set_priority(self, priority: SystemPriority):
        """Установка приоритета системы"""
        self._priority = priority
        logger.debug(f"Приоритет системы {self._system_name} изменен на {priority.value}")
    
    def get_config(self) -> SystemConfig:
        """Получение конфигурации системы"""
        return self.config
    
    def set_config(self, config: SystemConfig):
        """Установка конфигурации системы"""
        self.config = config
        logger.debug(f"Конфигурация системы {self._system_name} обновлена")
    
    def get_metrics(self) -> SystemMetrics:
        """Получение метрик системы"""
        return self.metrics
    
    def __str__(self) -> str:
        """Строковое представление системы"""
        return f"{self._system_name}({self._system_id}) - {self._state.value}"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"<{self.__class__.__name__} {self._system_name} at {id(self)}>"
