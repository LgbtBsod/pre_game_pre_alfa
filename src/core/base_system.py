#!/usr/bin/env python3
"""
Базовый класс для всех систем игры
Устраняет дублирование кода между системами
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import time
import logging

from .interfaces import ISystem, SystemPriority, SystemState
from .constants import constants_manager, SYSTEM_LIMITS, TIME_CONSTANTS_RO, get_float


@dataclass
class SystemStats:
    """Статистика системы"""
    update_count: int = 0
    total_update_time: float = 0.0
    last_update_time: float = 0.0
    average_update_time: float = 0.0
    max_update_time: float = 0.0
    min_update_time: float = float('inf')
    error_count: int = 0
    last_error_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0


class BaseSystem(ISystem, ABC):
    """
    Базовый класс для всех систем игры
    Предоставляет общую функциональность и устраняет дублирование кода
    """
    
    def __init__(self, name: str, priority: SystemPriority = SystemPriority.NORMAL):
        self.name = name
        self.priority = priority
        self.state = SystemState.UNINITIALIZED
        self.enabled = True
        self.initialized = False
        self.destroyed = False
        
        # Статистика системы
        self.stats = SystemStats()
        
        # Логгер для системы
        self.logger = logging.getLogger(f"system.{name}")
        
        # Время последнего обновления
        self._last_update = 0.0
        self._update_interval = get_float(TIME_CONSTANTS_RO, "update_interval", 1.0/60.0)
        
        # Кэш для оптимизации
        self._cache: Dict[str, Any] = {}
        self._cache_timeout = 5.0  # 5 секунд
        
        # Метрики производительности
        self._performance_metrics = {
            "update_calls": 0,
            "total_time": 0.0,
            "peak_memory": 0.0,
            "errors": 0
        }
    
    def initialize(self) -> bool:
        """Инициализация системы"""
        if self.initialized:
            self.logger.warning(f"Система {self.name} уже инициализирована")
            return True
        
        try:
            self.state = SystemState.INITIALIZING
            self.logger.info(f"Инициализация системы {self.name}")
            
            # Вызов абстрактного метода для специфичной инициализации
            if not self._initialize_impl():
                self.logger.error(f"Ошибка инициализации системы {self.name}")
                self.state = SystemState.ERROR
                return False
            
            self.initialized = True
            self.state = SystemState.READY
            self.logger.info(f"Система {self.name} успешно инициализирована")
            return True
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка при инициализации системы {self.name}: {e}")
            self.state = SystemState.ERROR
            self._performance_metrics["errors"] += 1
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы"""
        if not self.enabled or not self.initialized or self.destroyed:
            return True
        
        # Проверка интервала обновления
        current_time = time.time()
        if current_time - self._last_update < self._update_interval:
            return True
        
        self._last_update = current_time
        start_time = time.time()
        
        try:
            # Обновление статистики
            self.stats.update_count += 1
            self._performance_metrics["update_calls"] += 1
            
            # Вызов абстрактного метода для специфичного обновления
            success = self._update_impl(delta_time)
            
            # Обновление метрик производительности
            update_time = time.time() - start_time
            self.stats.total_update_time += update_time
            self.stats.last_update_time = update_time
            self.stats.average_update_time = self.stats.total_update_time / self.stats.update_count
            self.stats.max_update_time = max(self.stats.max_update_time, update_time)
            self.stats.min_update_time = min(self.stats.min_update_time, update_time)
            
            self._performance_metrics["total_time"] += update_time
            
            # Обновление статистики системы
            self._update_system_stats()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления системы {self.name}: {e}")
            self.stats.error_count += 1
            self.stats.last_error_time = time.time()
            self._performance_metrics["errors"] += 1
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы"""
        if self.destroyed:
            return True
        
        try:
            self.logger.info(f"Уничтожение системы {self.name}")
            self.state = SystemState.DESTROYED
            
            # Вызов абстрактного метода для специфичного уничтожения
            self._destroy_impl()
            
            self.destroyed = True
            self.enabled = False
            self.initialized = False
            
            self.logger.info(f"Система {self.name} успешно уничтожена")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при уничтожении системы {self.name}: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы"""
        if self.state == SystemState.READY:
            self.state = SystemState.PAUSED
            self.logger.info(f"Система {self.name} приостановлена")
            return True
        return False
    
    def resume(self) -> bool:
        """Возобновление системы"""
        if self.state == SystemState.PAUSED:
            self.state = SystemState.READY
            self.logger.info(f"Система {self.name} возобновлена")
            return True
        return False
    
    def get_state(self) -> SystemState:
        """Получение состояния системы"""
        return self.state
    
    def get_priority(self) -> SystemPriority:
        """Получение приоритета системы"""
        return self.priority
    
    def is_enabled(self) -> bool:
        """Проверка активности системы"""
        return self.enabled
    
    def set_enabled(self, enabled: bool) -> None:
        """Установка активности системы"""
        self.enabled = enabled
        if enabled:
            self.logger.info(f"Система {self.name} включена")
        else:
            self.logger.info(f"Система {self.name} отключена")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return {
            "name": self.name,
            "state": self.state.value,
            "priority": self.priority.value,
            "enabled": self.enabled,
            "initialized": self.initialized,
            "destroyed": self.destroyed,
            "update_count": self.stats.update_count,
            "total_update_time": self.stats.total_update_time,
            "average_update_time": self.stats.average_update_time,
            "max_update_time": self.stats.max_update_time,
            "min_update_time": self.stats.min_update_time,
            "error_count": self.stats.error_count,
            "last_error_time": self.stats.last_error_time,
            "memory_usage": self.stats.memory_usage,
            "cpu_usage": self.stats.cpu_usage,
            "performance_metrics": self._performance_metrics.copy()
        }
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы (общий метод для всех систем)"""
        # Базовая реализация - может быть переопределена в наследниках
        try:
            # Обновление использования памяти (примерная оценка)
            import sys
            self.stats.memory_usage = sys.getsizeof(self) / 1024  # KB
            
            # Обновление использования CPU (примерная оценка)
            if self.stats.update_count > 0:
                self.stats.cpu_usage = (self.stats.total_update_time / 
                                      (time.time() - self._last_update + 1)) * 100
                
        except Exception as e:
            self.logger.warning(f"Ошибка обновления статистики системы {self.name}: {e}")
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        if key in self._cache:
            cache_entry = self._cache[key]
            if time.time() - cache_entry["timestamp"] < self._cache_timeout:
                return cache_entry["value"]
            else:
                del self._cache[key]
        return None
    
    def set_cache(self, key: str, value: Any) -> None:
        """Установка значения в кэш"""
        self._cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def clear_cache(self) -> None:
        """Очистка кэша"""
        self._cache.clear()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        return self._performance_metrics.copy()
    
    # Абстрактные методы, которые должны быть реализованы в наследниках
    @abstractmethod
    def _initialize_impl(self) -> bool:
        """Реализация инициализации системы"""
        pass
    
    @abstractmethod
    def _update_impl(self, delta_time: float) -> bool:
        """Реализация обновления системы"""
        pass
    
    @abstractmethod
    def _destroy_impl(self) -> None:
        """Реализация уничтожения системы"""
        pass
