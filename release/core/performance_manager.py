#!/usr/bin/env python3
"""
Менеджер производительности для оптимизации игры
Отслеживает и управляет ресурсами системы
"""

import gc
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Уровни производительности"""
    LOW = "low"
    MEDIUM = "medium"  
    HIGH = "high"
    ULTRA = "ultra"


@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    fps: float = 0.0
    frame_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    entities_count: int = 0
    active_particles: int = 0
    draw_calls: int = 0
    last_update: float = field(default_factory=time.time)


@dataclass
class PerformanceSettings:
    """Настройки производительности"""
    target_fps: int = 60
    max_entities: int = 100
    max_particles: int = 200
    memory_limit: int = 512  # MB
    auto_optimize: bool = True
    quality_level: PerformanceLevel = PerformanceLevel.MEDIUM


class PerformanceOptimizer:
    """
    Оптимизатор производительности.
    Автоматически адаптирует настройки игры под производительность системы.
    """
    
    def __init__(self, settings: PerformanceSettings = None):
        self.settings = settings or PerformanceSettings()
        self.metrics = PerformanceMetrics()
        
        # История метрик
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 60  # 60 секунд истории
        
        # Оптимизации
        self.optimizations: Dict[str, bool] = {
            'reduce_particles': False,
            'limit_entities': False,
            'lower_quality': False,
            'disable_effects': False,
            'reduce_audio': False
        }
        
        # Callbacks для оптимизаций
        self.optimization_callbacks: Dict[str, Callable] = {}
        
        # Мониторинг
        self._monitoring = False
        self._monitor_thread = None
        self._last_gc = time.time()
        
        logger.info("Оптимизатор производительности инициализирован")
    
    def start_monitoring(self):
        """Запуск мониторинга производительности"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Мониторинг производительности запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        logger.info("Мониторинг производительности остановлен")
    
    def _monitor_loop(self):
        """Цикл мониторинга"""
        while self._monitoring:
            try:
                self._update_metrics()
                self._check_performance()
                self._cleanup_if_needed()
                time.sleep(1.0)  # Обновление каждую секунду
            except Exception as e:
                logger.error(f"Ошибка мониторинга: {e}")
    
    def _update_metrics(self):
        """Обновление метрик производительности"""
        try:
            # Системные метрики
            process = psutil.Process()
            self.metrics.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            self.metrics.cpu_usage = process.cpu_percent()
            self.metrics.last_update = time.time()
            
            # Добавляем в историю
            self.metrics_history.append(self.metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления метрик: {e}")
    
    def _check_performance(self):
        """Проверка производительности и автооптимизация"""
        if not self.settings.auto_optimize:
            return
        
        # Проверяем FPS
        if self.metrics.fps < self.settings.target_fps * 0.8:
            self._apply_fps_optimizations()
        
        # Проверяем память
        if self.metrics.memory_usage > self.settings.memory_limit * 0.9:
            self._apply_memory_optimizations()
        
        # Проверяем количество сущностей
        if self.metrics.entities_count > self.settings.max_entities:
            self._apply_entity_optimizations()
    
    def _apply_fps_optimizations(self):
        """Применение оптимизаций для FPS"""
        if not self.optimizations['reduce_particles']:
            self.optimizations['reduce_particles'] = True
            self._call_optimization('reduce_particles')
            logger.info("Применена оптимизация: уменьшение частиц")
        
        elif not self.optimizations['lower_quality']:
            self.optimizations['lower_quality'] = True
            self._call_optimization('lower_quality')
            logger.info("Применена оптимизация: снижение качества")
        
        elif not self.optimizations['disable_effects']:
            self.optimizations['disable_effects'] = True
            self._call_optimization('disable_effects')
            logger.info("Применена оптимизация: отключение эффектов")
    
    def _apply_memory_optimizations(self):
        """Применение оптимизаций памяти"""
        if not self.optimizations['limit_entities']:
            self.optimizations['limit_entities'] = True
            self._call_optimization('limit_entities')
            logger.info("Применена оптимизация: ограничение сущностей")
        
        # Принудительная сборка мусора
        gc.collect()
        logger.info("Выполнена сборка мусора")
    
    def _apply_entity_optimizations(self):
        """Оптимизации для сущностей"""
        if not self.optimizations['limit_entities']:
            self.optimizations['limit_entities'] = True
            self._call_optimization('limit_entities')
            logger.info("Применена оптимизация: ограничение сущностей")
    
    def _call_optimization(self, optimization_name: str):
        """Вызов callback оптимизации"""
        callback = self.optimization_callbacks.get(optimization_name)
        if callback:
            try:
                callback()
            except Exception as e:
                logger.error(f"Ошибка применения оптимизации {optimization_name}: {e}")
    
    def _cleanup_if_needed(self):
        """Очистка при необходимости"""
        current_time = time.time()
        
        # Сборка мусора каждые 5 секунд
        if current_time - self._last_gc > 5.0:
            gc.collect()
            self._last_gc = current_time
    
    def register_optimization_callback(self, name: str, callback: Callable):
        """Регистрация callback для оптимизации"""
        self.optimization_callbacks[name] = callback
        logger.info(f"Зарегистрирован callback оптимизации: {name}")
    
    def update_fps(self, fps: float, frame_time: float):
        """Обновление FPS метрик"""
        self.metrics.fps = fps
        self.metrics.frame_time = frame_time
    
    def update_entities_count(self, count: int):
        """Обновление количества сущностей"""
        self.metrics.entities_count = count
    
    def update_particles_count(self, count: int):
        """Обновление количества частиц"""
        self.metrics.active_particles = count
    
    def update_draw_calls(self, count: int):
        """Обновление количества вызовов отрисовки"""
        self.metrics.draw_calls = count
    
    def get_metrics(self) -> PerformanceMetrics:
        """Получение текущих метрик"""
        return self.metrics
    
    def get_average_fps(self, seconds: int = 10) -> float:
        """Получение среднего FPS за период"""
        if not self.metrics_history:
            return 0.0
        
        recent_metrics = [m for m in self.metrics_history 
                         if time.time() - m.last_update <= seconds]
        
        if not recent_metrics:
            return 0.0
        
        return sum(m.fps for m in recent_metrics) / len(recent_metrics)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Получение отчета о производительности"""
        return {
            'current_metrics': {
                'fps': self.metrics.fps,
                'frame_time': self.metrics.frame_time,
                'memory_mb': self.metrics.memory_usage,
                'cpu_percent': self.metrics.cpu_usage,
                'entities': self.metrics.entities_count,
                'particles': self.metrics.active_particles,
                'draw_calls': self.metrics.draw_calls
            },
            'averages': {
                'fps_10s': self.get_average_fps(10),
                'fps_30s': self.get_average_fps(30),
                'fps_60s': self.get_average_fps(60)
            },
            'optimizations': self.optimizations.copy(),
            'settings': {
                'target_fps': self.settings.target_fps,
                'max_entities': self.settings.max_entities,
                'max_particles': self.settings.max_particles,
                'memory_limit': self.settings.memory_limit,
                'quality_level': self.settings.quality_level.value
            }
        }
    
    def reset_optimizations(self):
        """Сброс всех оптимизаций"""
        for key in self.optimizations:
            self.optimizations[key] = False
        logger.info("Все оптимизации сброшены")
    
    def set_quality_level(self, level: PerformanceLevel):
        """Установка уровня качества"""
        self.settings.quality_level = level
        
        # Применяем настройки в зависимости от уровня
        if level == PerformanceLevel.LOW:
            self.settings.max_entities = 50
            self.settings.max_particles = 100
        elif level == PerformanceLevel.MEDIUM:
            self.settings.max_entities = 100
            self.settings.max_particles = 200
        elif level == PerformanceLevel.HIGH:
            self.settings.max_entities = 200
            self.settings.max_particles = 500
        elif level == PerformanceLevel.ULTRA:
            self.settings.max_entities = 500
            self.settings.max_particles = 1000
        
        logger.info(f"Установлен уровень качества: {level.value}")


# Глобальный экземпляр оптимизатора
performance_optimizer = PerformanceOptimizer()


def initialize_performance_monitoring():
    """Инициализация мониторинга производительности"""
    try:
        performance_optimizer.start_monitoring()
        logger.info("Мониторинг производительности инициализирован")
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации мониторинга: {e}")
        return False


def cleanup_performance_monitoring():
    """Очистка мониторинга производительности"""
    try:
        performance_optimizer.stop_monitoring()
        logger.info("Мониторинг производительности остановлен")
    except Exception as e:
        logger.error(f"Ошибка остановки мониторинга: {e}")
