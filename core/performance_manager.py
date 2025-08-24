#!/usr/bin/env python3
"""
Оптимизированная система управления производительностью
Включает мониторинг, профилирование и автоматическую оптимизацию
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import gc
import psutil
import os

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    fps: float = 0.0
    frame_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_available: float = 0.0
    gpu_usage: float = 0.0
    disk_io: float = 0.0
    network_io: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class PerformanceThreshold:
    """Пороги производительности"""
    min_fps: float = 30.0
    max_frame_time: float = 33.0  # 30 FPS = 33ms
    max_cpu_usage: float = 80.0
    max_memory_usage: float = 85.0
    max_gpu_usage: float = 90.0


class PerformanceProfiler:
    """Профилировщик производительности"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.samples: deque = deque(maxlen=max_samples)
        self.profiling_active = False
        self.profile_data: Dict[str, List[float]] = defaultdict(list)
        
    def start_profiling(self):
        """Начало профилирования"""
        self.profiling_active = True
        self.profile_data.clear()
        logger.info("Профилирование производительности запущено")
    
    def stop_profiling(self):
        """Остановка профилирования"""
        self.profiling_active = False
        logger.info("Профилирование производительности остановлено")
    
    def add_sample(self, metrics: PerformanceMetrics):
        """Добавление образца метрик"""
        self.samples.append(metrics)
        
        if self.profiling_active:
            self.profile_data['fps'].append(metrics.fps)
            self.profile_data['frame_time'].append(metrics.frame_time)
            self.profile_data['cpu_usage'].append(metrics.cpu_usage)
            self.profile_data['memory_usage'].append(metrics.memory_usage)
    
    def get_average_metrics(self, window_size: int = 60) -> PerformanceMetrics:
        """Получение средних метрик за окно"""
        if not self.samples:
            return PerformanceMetrics()
        
        recent_samples = list(self.samples)[-window_size:]
        
        return PerformanceMetrics(
            fps=sum(s.fps for s in recent_samples) / len(recent_samples),
            frame_time=sum(s.frame_time for s in recent_samples) / len(recent_samples),
            cpu_usage=sum(s.cpu_usage for s in recent_samples) / len(recent_samples),
            memory_usage=sum(s.memory_usage for s in recent_samples) / len(recent_samples),
            memory_available=sum(s.memory_available for s in recent_samples) / len(recent_samples),
            gpu_usage=sum(s.gpu_usage for s in recent_samples) / len(recent_samples),
            disk_io=sum(s.disk_io for s in recent_samples) / len(recent_samples),
            network_io=sum(s.network_io for s in recent_samples) / len(recent_samples),
            timestamp=time.time()
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Получение отчета о производительности"""
        if not self.samples:
            return {}
        
        all_fps = [s.fps for s in self.samples]
        all_frame_times = [s.frame_time for s in self.samples]
        all_cpu = [s.cpu_usage for s in self.samples]
        all_memory = [s.memory_usage for s in self.samples]
        
        return {
            'fps': {
                'current': all_fps[-1] if all_fps else 0,
                'average': sum(all_fps) / len(all_fps) if all_fps else 0,
                'min': min(all_fps) if all_fps else 0,
                'max': max(all_fps) if all_fps else 0
            },
            'frame_time': {
                'current': all_frame_times[-1] if all_frame_times else 0,
                'average': sum(all_frame_times) / len(all_frame_times) if all_frame_times else 0,
                'min': min(all_frame_times) if all_frame_times else 0,
                'max': max(all_frame_times) if all_frame_times else 0
            },
            'cpu_usage': {
                'current': all_cpu[-1] if all_cpu else 0,
                'average': sum(all_cpu) / len(all_cpu) if all_cpu else 0,
                'max': max(all_cpu) if all_cpu else 0
            },
            'memory_usage': {
                'current': all_memory[-1] if all_memory else 0,
                'average': sum(all_memory) / len(all_memory) if all_memory else 0,
                'max': max(all_memory) if all_memory else 0
            },
            'samples_count': len(self.samples),
            'profiling_active': self.profiling_active
        }


class PerformanceOptimizer:
    """Оптимизатор производительности"""
    
    def __init__(self):
        self.thresholds = PerformanceThreshold()
        self.optimization_level = 0  # 0-3, где 0 - без оптимизации, 3 - максимальная
        self.optimization_history: List[Dict[str, Any]] = []
        self.auto_optimize = True
        
        # Обработчики оптимизации
        self.optimization_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
        
        logger.info("Оптимизатор производительности инициализирован")
    
    def _register_default_handlers(self):
        """Регистрация стандартных обработчиков оптимизации"""
        self.optimization_handlers['memory'] = self._optimize_memory
        self.optimization_handlers['graphics'] = self._optimize_graphics
        self.optimization_handlers['audio'] = self._optimize_audio
        self.optimization_handlers['ai'] = self._optimize_ai
        self.optimization_handlers['physics'] = self._optimize_physics
    
    def check_performance(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Проверка производительности на соответствие порогам"""
        issues = {}
        
        issues['low_fps'] = metrics.fps < self.thresholds.min_fps
        issues['high_frame_time'] = metrics.frame_time > self.thresholds.max_frame_time
        issues['high_cpu'] = metrics.cpu_usage > self.thresholds.max_cpu_usage
        issues['high_memory'] = metrics.memory_usage > self.thresholds.max_memory_usage
        issues['high_gpu'] = metrics.gpu_usage > self.thresholds.max_gpu_usage
        
        return issues
    
    def optimize_performance(self, metrics: PerformanceMetrics, issues: Dict[str, bool]) -> Dict[str, Any]:
        """Оптимизация производительности"""
        if not self.auto_optimize:
            return {}
        
        optimizations = {}
        
        # Оптимизация памяти
        if issues.get('high_memory', False):
            memory_opt = self._optimize_memory(metrics)
            if memory_opt:
                optimizations['memory'] = memory_opt
        
        # Оптимизация графики
        if issues.get('high_gpu', False) or issues.get('low_fps', False):
            graphics_opt = self._optimize_graphics(metrics)
            if graphics_opt:
                optimizations['graphics'] = graphics_opt
        
        # Оптимизация CPU
        if issues.get('high_cpu', False):
            cpu_opt = self._optimize_cpu(metrics)
            if cpu_opt:
                optimizations['cpu'] = cpu_opt
        
        # Оптимизация AI
        if issues.get('high_cpu', False):
            ai_opt = self._optimize_ai(metrics)
            if ai_opt:
                optimizations['ai'] = ai_opt
        
        # Записываем оптимизацию в историю
        if optimizations:
            self.optimization_history.append({
                'timestamp': time.time(),
                'metrics': metrics,
                'issues': issues,
                'optimizations': optimizations
            })
            
            # Ограничиваем размер истории
            if len(self.optimization_history) > 100:
                self.optimization_history.pop(0)
        
        return optimizations
    
    def _optimize_memory(self, metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
        """Оптимизация памяти"""
        try:
            # Принудительная сборка мусора
            collected = gc.collect()
            
            # Очистка кэша ресурсов
            from core.resource_manager import resource_manager
            resource_manager.clear_cache()
            
            logger.info(f"Оптимизация памяти: собрано {collected} объектов")
            
            return {
                'type': 'memory_cleanup',
                'objects_collected': collected,
                'cache_cleared': True
            }
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации памяти: {e}")
            return None
    
    def _optimize_graphics(self, metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
        """Оптимизация графики"""
        try:
            # Уменьшение качества графики
            if self.optimization_level < 3:
                self.optimization_level += 1
            
            # Настройки графики в зависимости от уровня оптимизации
            graphics_settings = {
                1: {'texture_quality': 'medium', 'shadow_quality': 'low'},
                2: {'texture_quality': 'low', 'shadow_quality': 'off', 'particle_count': 50},
                3: {'texture_quality': 'low', 'shadow_quality': 'off', 'particle_count': 25, 'view_distance': 0.5}
            }
            
            current_settings = graphics_settings.get(self.optimization_level, {})
            
            logger.info(f"Оптимизация графики: уровень {self.optimization_level}")
            
            return {
                'type': 'graphics_optimization',
                'level': self.optimization_level,
                'settings': current_settings
            }
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации графики: {e}")
            return None
    
    def _optimize_cpu(self, metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
        """Оптимизация CPU"""
        try:
            # Уменьшение частоты обновления AI
            ai_update_rate = max(0.5, 1.0 - (self.optimization_level * 0.2))
            
            # Уменьшение сложности физики
            physics_steps = max(1, 4 - self.optimization_level)
            
            logger.info(f"Оптимизация CPU: AI rate {ai_update_rate}, physics steps {physics_steps}")
            
            return {
                'type': 'cpu_optimization',
                'ai_update_rate': ai_update_rate,
                'physics_steps': physics_steps
            }
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации CPU: {e}")
            return None
    
    def _optimize_ai(self, metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
        """Оптимизация AI"""
        try:
            # Уменьшение количества активных AI
            max_ai_entities = max(5, 20 - (self.optimization_level * 5))
            
            # Упрощение алгоритмов AI
            ai_complexity = max(0.3, 1.0 - (self.optimization_level * 0.2))
            
            logger.info(f"Оптимизация AI: max entities {max_ai_entities}, complexity {ai_complexity}")
            
            return {
                'type': 'ai_optimization',
                'max_entities': max_ai_entities,
                'complexity': ai_complexity
            }
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации AI: {e}")
            return None
    
    def _optimize_audio(self, metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
        """Оптимизация аудио"""
        try:
            # Уменьшение качества аудио
            audio_quality = max(0.5, 1.0 - (self.optimization_level * 0.2))
            
            # Уменьшение количества одновременных звуков
            max_sounds = max(5, 15 - (self.optimization_level * 3))
            
            logger.info(f"Оптимизация аудио: quality {audio_quality}, max sounds {max_sounds}")
            
            return {
                'type': 'audio_optimization',
                'quality': audio_quality,
                'max_sounds': max_sounds
            }
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации аудио: {e}")
            return None
    
    def _optimize_physics(self, metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
        """Оптимизация физики"""
        try:
            # Уменьшение точности физики
            physics_accuracy = max(0.5, 1.0 - (self.optimization_level * 0.2))
            
            # Уменьшение количества физических объектов
            max_physics_objects = max(10, 50 - (self.optimization_level * 10))
            
            logger.info(f"Оптимизация физики: accuracy {physics_accuracy}, max objects {max_physics_objects}")
            
            return {
                'type': 'physics_optimization',
                'accuracy': physics_accuracy,
                'max_objects': max_physics_objects
            }
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации физики: {e}")
            return None
    
    def reset_optimization(self):
        """Сброс оптимизации"""
        self.optimization_level = 0
        logger.info("Оптимизация сброшена")
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Получение отчета об оптимизации"""
        return {
            'current_level': self.optimization_level,
            'auto_optimize': self.auto_optimize,
            'optimization_count': len(self.optimization_history),
            'recent_optimizations': self.optimization_history[-10:] if self.optimization_history else []
        }


class PerformanceMonitor:
    """Монитор производительности"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.optimizer = PerformanceOptimizer()
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitor_interval = 1.0  # секунды
        
        # Системная информация
        self.system_info = self._get_system_info()
        
        logger.info("Монитор производительности инициализирован")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'platform': os.name,
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}"
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о системе: {e}")
            return {}
    
    def start_monitoring(self):
        """Запуск мониторинга"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Мониторинг производительности запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Мониторинг производительности остановлен")
    
    def _monitor_loop(self):
        """Цикл мониторинга"""
        while self.monitoring_active:
            try:
                metrics = self._collect_metrics()
                self.profiler.add_sample(metrics)
                
                # Проверка производительности
                issues = self.optimizer.check_performance(metrics)
                
                # Оптимизация при необходимости
                if any(issues.values()):
                    optimizations = self.optimizer.optimize_performance(metrics, issues)
                    if optimizations:
                        logger.info(f"Применены оптимизации: {list(optimizations.keys())}")
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(self.monitor_interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Сбор метрик производительности"""
        try:
            # CPU
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # Память
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_available = memory.available / (1024 * 1024 * 1024)  # GB
            
            # GPU (упрощенная реализация)
            gpu_usage = 0.0  # Требует специальных библиотек
            
            # Диск и сеть
            disk_io = 0.0
            network_io = 0.0
            
            return PerformanceMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_available=memory_available,
                gpu_usage=gpu_usage,
                disk_io=disk_io,
                network_io=network_io,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Ошибка сбора метрик: {e}")
            return PerformanceMetrics()
    
    def update_frame_metrics(self, fps: float, frame_time: float):
        """Обновление метрик кадров"""
        if self.profiler.samples:
            current_metrics = self.profiler.samples[-1]
            current_metrics.fps = fps
            current_metrics.frame_time = frame_time
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Получение полного отчета о производительности"""
        profiler_report = self.profiler.get_performance_report()
        optimizer_report = self.optimizer.get_optimization_report()
        
        return {
            'system_info': self.system_info,
            'profiler': profiler_report,
            'optimizer': optimizer_report,
            'monitoring_active': self.monitoring_active
        }


# Глобальные экземпляры
performance_monitor = PerformanceMonitor()
performance_optimizer = PerformanceOptimizer()


def initialize_performance_monitoring():
    """Инициализация мониторинга производительности"""
    try:
        performance_monitor.start_monitoring()
        logger.info("Мониторинг производительности инициализирован")
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации мониторинга производительности: {e}")
        return False


def get_performance_stats() -> Dict[str, Any]:
    """Получение статистики производительности"""
    return performance_monitor.get_performance_report()
