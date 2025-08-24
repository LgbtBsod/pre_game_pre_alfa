#!/usr/bin/env python3
"""
Performance Manager - Менеджер производительности
Отвечает только за мониторинг и оптимизацию производительности игры
"""

import time
import logging
import psutil
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque
import pygame

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    fps: float = 0.0
    frame_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    draw_calls: int = 0
    entities_count: int = 0
    particles_count: int = 0

class PerformanceManager:
    """Менеджер производительности"""
    
    def __init__(self):
        # Метрики производительности
        self.current_metrics = PerformanceMetrics()
        self.history: deque = deque(maxlen=1000)  # История метрик
        
        # Мониторинг
        self.monitoring_enabled = True
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = 0.1  # секунды
        
        # Пороги производительности
        self.fps_threshold = 30.0
        self.memory_threshold = 80.0  # процент
        self.cpu_threshold = 90.0     # процент
        
        # Статистика
        self.start_time = time.time()
        self.frame_count = 0
        self.last_frame_time = time.time()
        
        # Оптимизации
        self.auto_optimization_enabled = True
        self.quality_level = "high"  # high, medium, low
        
        # Pygame специфичные метрики
        self.pygame_info = {}
        
        logger.info("Менеджер производительности инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация менеджера производительности"""
        try:
            logger.info("Инициализация менеджера производительности...")
            
            # Получение информации о системе
            self._gather_system_info()
            
            # Запуск мониторинга
            if self.monitoring_enabled:
                self._start_monitoring()
            
            # Инициализация Pygame метрик
            self._initialize_pygame_metrics()
            
            logger.info("Менеджер производительности успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера производительности: {e}")
            return False
    
    def _gather_system_info(self):
        """Сбор информации о системе"""
        try:
            # CPU информация
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Память
            memory = psutil.virtual_memory()
            
            # Диск
            disk = psutil.disk_usage('/')
            
            system_info = {
                'cpu_count': cpu_count,
                'cpu_freq': cpu_freq.current if cpu_freq else 0,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'disk_total': disk.total,
                'disk_free': disk.free
            }
            
            logger.info(f"Системная информация: {system_info}")
            
        except Exception as e:
            logger.warning(f"Не удалось собрать системную информацию: {e}")
    
    def _initialize_pygame_metrics(self):
        """Инициализация Pygame метрик"""
        try:
            # Получение информации о дисплее
            display_info = pygame.display.Info()
            
            self.pygame_info = {
                'display_width': display_info.current_w,
                'display_height': display_info.current_h,
                'display_depth': display_info.bitsize,
                'display_flags': display_info.flags
            }
            
            logger.info(f"Pygame информация: {self.pygame_info}")
            
        except Exception as e:
            logger.warning(f"Не удалось получить Pygame информацию: {e}")
    
    def _start_monitoring(self):
        """Запуск мониторинга производительности"""
        def monitor_loop():
            while self.monitoring_enabled:
                try:
                    self._update_system_metrics()
                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    logger.error(f"Ошибка в цикле мониторинга: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Мониторинг производительности запущен")
    
    def _update_system_metrics(self):
        """Обновление системных метрик"""
        try:
            # CPU использование
            self.current_metrics.cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # Использование памяти
            memory = psutil.virtual_memory()
            self.current_metrics.memory_usage = memory.percent
            
            # GPU использование (если доступно)
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    self.current_metrics.gpu_usage = gpus[0].load * 100
            except ImportError:
                pass  # GPUtil не установлен
            
        except Exception as e:
            logger.debug(f"Ошибка обновления системных метрик: {e}")
    
    def update(self, delta_time: float):
        """Обновление метрик производительности"""
        current_time = time.time()
        
        # Обновление FPS
        if delta_time > 0:
            self.current_metrics.fps = 1.0 / delta_time
        else:
            self.current_metrics.fps = 0.0
        
        # Обновление времени кадра
        self.current_metrics.frame_time = delta_time * 1000  # в миллисекундах
        
        # Обновление счетчика кадров
        self.frame_count += 1
        
        # Сохранение метрик в историю
        self.history.append(PerformanceMetrics(
            fps=self.current_metrics.fps,
            frame_time=self.current_metrics.frame_time,
            cpu_usage=self.current_metrics.cpu_usage,
            memory_usage=self.current_metrics.memory_usage,
            gpu_usage=self.current_metrics.gpu_usage,
            draw_calls=self.current_metrics.draw_calls,
            entities_count=self.current_metrics.entities_count,
            particles_count=self.current_metrics.particles_count
        ))
        
        # Проверка порогов производительности
        self._check_performance_thresholds()
        
        # Автоматическая оптимизация
        if self.auto_optimization_enabled:
            self._auto_optimize()
    
    def _check_performance_thresholds(self):
        """Проверка порогов производительности"""
        # Проверка FPS
        if self.current_metrics.fps < self.fps_threshold:
            logger.warning(f"FPS ниже порога: {self.current_metrics.fps:.1f} < {self.fps_threshold}")
        
        # Проверка памяти
        if self.current_metrics.memory_usage > self.memory_threshold:
            logger.warning(f"Использование памяти выше порога: {self.current_metrics.memory_usage:.1f}% > {self.memory_threshold}%")
        
        # Проверка CPU
        if self.current_metrics.cpu_usage > self.cpu_threshold:
            logger.warning(f"Использование CPU выше порога: {self.current_metrics.cpu_usage:.1f}% > {self.cpu_threshold}%")
    
    def _auto_optimize(self):
        """Автоматическая оптимизация"""
        # Снижение качества при низком FPS
        if self.current_metrics.fps < 20.0 and self.quality_level == "high":
            self.set_quality_level("medium")
            logger.info("Автоматическое снижение качества до medium")
        
        elif self.current_metrics.fps < 15.0 and self.quality_level == "medium":
            self.set_quality_level("low")
            logger.info("Автоматическое снижение качества до low")
        
        # Повышение качества при хорошей производительности
        elif (self.current_metrics.fps > 50.0 and 
              self.current_metrics.memory_usage < 60.0 and 
              self.current_metrics.cpu_usage < 70.0):
            
            if self.quality_level == "low":
                self.set_quality_level("medium")
                logger.info("Автоматическое повышение качества до medium")
            elif self.quality_level == "medium":
                self.set_quality_level("high")
                logger.info("Автоматическое повышение качества до high")
    
    def set_quality_level(self, level: str):
        """Установка уровня качества"""
        if level in ["low", "medium", "high"]:
            old_level = self.quality_level
            self.quality_level = level
            
            # Применение настроек качества
            self._apply_quality_settings(level)
            
            logger.info(f"Уровень качества изменен: {old_level} -> {level}")
        else:
            logger.warning(f"Неизвестный уровень качества: {level}")
    
    def _apply_quality_settings(self, level: str):
        """Применение настроек качества"""
        settings = {
            "high": {
                "particle_limit": 1000,
                "shadow_quality": "high",
                "texture_quality": "high",
                "anti_aliasing": True
            },
            "medium": {
                "particle_limit": 500,
                "shadow_quality": "medium",
                "texture_quality": "medium",
                "anti_aliasing": False
            },
            "low": {
                "particle_limit": 200,
                "shadow_quality": "low",
                "texture_quality": "low",
                "anti_aliasing": False
            }
        }
        
        if level in settings:
            # Здесь можно применить настройки к игровым системам
            logger.debug(f"Применены настройки качества: {settings[level]}")
    
    def update_entity_count(self, count: int):
        """Обновление количества сущностей"""
        self.current_metrics.entities_count = count
    
    def update_particle_count(self, count: int):
        """Обновление количества частиц"""
        self.current_metrics.particles_count = count
    
    def update_draw_calls(self, count: int):
        """Обновление количества вызовов отрисовки"""
        self.current_metrics.draw_calls = count
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Получение текущих метрик"""
        return self.current_metrics
    
    def get_average_metrics(self, samples: int = 100) -> PerformanceMetrics:
        """Получение средних метрик за последние N сэмплов"""
        if not self.history:
            return PerformanceMetrics()
        
        recent_metrics = list(self.history)[-samples:]
        
        avg_fps = sum(m.fps for m in recent_metrics) / len(recent_metrics)
        avg_frame_time = sum(m.frame_time for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        
        return PerformanceMetrics(
            fps=avg_fps,
            frame_time=avg_frame_time,
            cpu_usage=avg_cpu,
            memory_usage=avg_memory
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Получение отчета о производительности"""
        avg_metrics = self.get_average_metrics()
        
        return {
            'current_metrics': {
                'fps': round(self.current_metrics.fps, 1),
                'frame_time': round(self.current_metrics.frame_time, 2),
                'cpu_usage': round(self.current_metrics.cpu_usage, 1),
                'memory_usage': round(self.current_metrics.memory_usage, 1),
                'gpu_usage': round(self.current_metrics.gpu_usage, 1),
                'entities_count': self.current_metrics.entities_count,
                'particles_count': self.current_metrics.particles_count,
                'draw_calls': self.current_metrics.draw_calls
            },
            'average_metrics': {
                'fps': round(avg_metrics.fps, 1),
                'frame_time': round(avg_metrics.frame_time, 2),
                'cpu_usage': round(avg_metrics.cpu_usage, 1),
                'memory_usage': round(avg_metrics.memory_usage, 1)
            },
            'system_info': {
                'quality_level': self.quality_level,
                'auto_optimization': self.auto_optimization_enabled,
                'monitoring_enabled': self.monitoring_enabled,
                'uptime': time.time() - self.start_time,
                'total_frames': self.frame_count
            }
        }
    
    def cleanup(self):
        """Очистка менеджера производительности"""
        logger.info("Очистка менеджера производительности...")
        
        # Остановка мониторинга
        self.monitoring_enabled = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
        
        # Очистка истории
        self.history.clear()
        
        logger.info("Менеджер производительности очищен")
