#!/usr/bin/env python3
"""
Performance Manager - Менеджер производительности
Мониторинг и оптимизация производительности игры
"""

import time
import logging
import threading
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
from dataclasses import dataclass, field
from enum import Enum

from .interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """Метрики производительности"""
    FPS = "fps"
    FRAME_TIME = "frame_time"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    GPU_USAGE = "gpu_usage"
    SYSTEM_UPDATE_TIME = "system_update_time"
    RENDER_TIME = "render_time"
    AI_UPDATE_TIME = "ai_update_time"
    EVENT_PROCESSING_TIME = "event_processing_time"

@dataclass
class PerformanceData:
    """Данные производительности"""
    metric: PerformanceMetric
    value: float
    timestamp: float
    source: str = "unknown"

@dataclass
class SystemPerformance:
    """Производительность системы"""
    system_name: str
    update_time: float = 0.0
    update_count: int = 0
    avg_update_time: float = 0.0
    max_update_time: float = 0.0
    min_update_time: float = float('inf')
    last_update: float = 0.0

class PerformanceManager(ISystem):
    """Менеджер производительности с расширенным мониторингом"""
    
    def __init__(self):
        # Свойства для интерфейса ISystem
        self._system_name = "performance_manager"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Метрики производительности
        self.metrics: Dict[PerformanceMetric, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        
        # Производительность систем
        self.system_performance: Dict[str, SystemPerformance] = {}
        
        # Настройки мониторинга
        self.monitoring_config = {
            'enabled': True,
            'sample_interval': 0.1,  # 10 раз в секунду
            'history_size': 1000,
            'alert_thresholds': {
                'fps_min': 30.0,
                'frame_time_max': 33.0,  # 30 FPS
                'cpu_usage_max': 80.0,
                'memory_usage_max': 85.0,
                'system_update_time_max': 16.0  # 60 FPS
            }
        }
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация менеджера производительности"""
        try:
            logger.info("Инициализация менеджера производительности...")
            
            # Статистика
            self.performance_stats = {
                'total_frames': 0,
                'total_update_time': 0.0,
                'avg_fps': 0.0,
                'avg_frame_time': 0.0,
                'performance_alerts': 0,
                'optimizations_applied': 0
            }
            
            # Поток мониторинга
            self.monitoring_thread: Optional[threading.Thread] = None
            self.monitoring_active = False
            
            # Кэш для оптимизации
            self.performance_cache = {}
            
            # Запускаем поток мониторинга
            self._start_monitoring()
            
            self._system_state = SystemState.READY
            logger.info("Менеджер производительности успешно инициализирован")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера производительности: {e}")
            return False
    

    
    def update(self, delta_time: float) -> bool:
        """Обновление менеджера производительности"""
        try:
            # Обновляем статистику
            self._update_performance_stats(delta_time)
            
            # Проверяем производительность систем
            self._check_system_performance()
            
            # Применяем оптимизации при необходимости
            self._apply_optimizations()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления менеджера производительности: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка мониторинга"""
        try:
            self.monitoring_active = False
            self._system_state = SystemState.PAUSED
            logger.info("Мониторинг производительности приостановлен")
            return True
        except Exception as e:
            logger.error(f"Ошибка приостановки мониторинга: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление мониторинга"""
        try:
            self.monitoring_active = True
            self._system_state = SystemState.READY
            logger.info("Мониторинг производительности возобновлен")
            return True
        except Exception as e:
            logger.error(f"Ошибка возобновления мониторинга: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка менеджера производительности"""
        try:
            logger.info("Очистка менеджера производительности...")
            
            # Останавливаем мониторинг
            self._stop_monitoring()
            
            # Очищаем данные
            self.metrics.clear()
            self.system_performance.clear()
            self.performance_cache.clear()
            
            self._system_state = SystemState.DESTROYED
            logger.info("Менеджер производительности очищен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки менеджера производительности: {e}")
            return False
    
    def record_metric(self, metric: PerformanceMetric, value: float, source: str = "unknown"):
        """Запись метрики производительности"""
        try:
            data = PerformanceData(
                metric=metric,
                value=value,
                timestamp=time.time(),
                source=source
            )
            
            self.metrics[metric].append(data)
            
            # Проверяем пороги предупреждений
            self._check_alert_thresholds(metric, value, source)
            
        except Exception as e:
            logger.error(f"Ошибка записи метрики {metric.value}: {e}")
    
    def record_system_performance(self, system_name: str, update_time: float):
        """Запись производительности системы"""
        try:
            if system_name not in self.system_performance:
                self.system_performance[system_name] = SystemPerformance(system_name)
            
            perf = self.system_performance[system_name]
            perf.update_time = update_time
            perf.update_count += 1
            perf.last_update = time.time()
            
            # Обновляем статистику
            total_time = perf.avg_update_time * (perf.update_count - 1) + update_time
            perf.avg_update_time = total_time / perf.update_count
            perf.max_update_time = max(perf.max_update_time, update_time)
            perf.min_update_time = min(perf.min_update_time, update_time)
            
        except Exception as e:
            logger.error(f"Ошибка записи производительности системы {system_name}: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Получение отчета о производительности"""
        try:
            report = {
                'current_metrics': {},
                'system_performance': {},
                'statistics': self.performance_stats.copy(),
                'alerts': self._get_active_alerts()
            }
            
            # Текущие метрики
            for metric in PerformanceMetric:
                if self.metrics[metric]:
                    latest = self.metrics[metric][-1]
                    report['current_metrics'][metric.value] = {
                        'value': latest.value,
                        'timestamp': latest.timestamp,
                        'source': latest.source
                    }
            
            # Производительность систем
            for system_name, perf in self.system_performance.items():
                report['system_performance'][system_name] = {
                    'avg_update_time': perf.avg_update_time,
                    'max_update_time': perf.max_update_time,
                    'min_update_time': perf.min_update_time,
                    'update_count': perf.update_count,
                    'last_update': perf.last_update
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Ошибка получения отчета о производительности: {e}")
            return {}
    
    def _start_monitoring(self):
        """Запуск потока мониторинга"""
        try:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("Поток мониторинга производительности запущен")
            
        except Exception as e:
            logger.error(f"Ошибка запуска мониторинга: {e}")
    
    def _stop_monitoring(self):
        """Остановка потока мониторинга"""
        try:
            self.monitoring_active = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=1.0)
            logger.info("Поток мониторинга производительности остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка остановки мониторинга: {e}")
    
    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.monitoring_active:
            try:
                # Собираем системные метрики
                self._collect_system_metrics()
                
                # Пауза между сборами
                time.sleep(self.monitoring_config['sample_interval'])
                
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(1.0)
    
    def _collect_system_metrics(self):
        """Сбор системных метрик"""
        try:
            import psutil
            
            # CPU использование
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.record_metric(PerformanceMetric.CPU_USAGE, cpu_percent, "system")
            
            # Использование памяти
            memory = psutil.virtual_memory()
            self.record_metric(PerformanceMetric.MEMORY_USAGE, memory.percent, "system")
            
        except ImportError:
            logger.warning("psutil не установлен, системные метрики недоступны")
        except Exception as e:
            logger.error(f"Ошибка сбора системных метрик: {e}")
    
    def _update_performance_stats(self, delta_time: float):
        """Обновление статистики производительности"""
        try:
            self.performance_stats['total_frames'] += 1
            self.performance_stats['total_update_time'] += delta_time
            
            # Обновляем средние значения
            if self.performance_stats['total_frames'] > 0:
                self.performance_stats['avg_frame_time'] = (
                    self.performance_stats['total_update_time'] / 
                    self.performance_stats['total_frames']
                )
                
                if self.performance_stats['avg_frame_time'] > 0:
                    self.performance_stats['avg_fps'] = 1.0 / self.performance_stats['avg_frame_time']
            
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
    
    def _check_system_performance(self):
        """Проверка производительности систем"""
        try:
            for system_name, perf in self.system_performance.items():
                if perf.avg_update_time > self.monitoring_config['alert_thresholds']['system_update_time_max']:
                    logger.warning(f"Система {system_name} работает медленно: {perf.avg_update_time:.2f}ms")
                    
        except Exception as e:
            logger.error(f"Ошибка проверки производительности систем: {e}")
    
    def _check_alert_thresholds(self, metric: PerformanceMetric, value: float, source: str):
        """Проверка порогов предупреждений"""
        try:
            thresholds = self.monitoring_config['alert_thresholds']
            
            if metric == PerformanceMetric.FPS and value < thresholds['fps_min']:
                logger.warning(f"Низкий FPS: {value:.1f} (источник: {source})")
                self.performance_stats['performance_alerts'] += 1
                
            elif metric == PerformanceMetric.FRAME_TIME and value > thresholds['frame_time_max']:
                logger.warning(f"Высокое время кадра: {value:.2f}ms (источник: {source})")
                self.performance_stats['performance_alerts'] += 1
                
            elif metric == PerformanceMetric.CPU_USAGE and value > thresholds['cpu_usage_max']:
                logger.warning(f"Высокое использование CPU: {value:.1f}% (источник: {source})")
                self.performance_stats['performance_alerts'] += 1
                
            elif metric == PerformanceMetric.MEMORY_USAGE and value > thresholds['memory_usage_max']:
                logger.warning(f"Высокое использование памяти: {value:.1f}% (источник: {source})")
                self.performance_stats['performance_alerts'] += 1
                
        except Exception as e:
            logger.error(f"Ошибка проверки порогов предупреждений: {e}")
    
    def _apply_optimizations(self):
        """Применение оптимизаций"""
        try:
            # Получаем текущие метрики
            current_fps = self._get_current_metric(PerformanceMetric.FPS)
            current_cpu = self._get_current_metric(PerformanceMetric.CPU_USAGE)
            current_memory = self._get_current_metric(PerformanceMetric.MEMORY_USAGE)
            
            # Применяем оптимизации на основе метрик
            optimizations_applied = 0
            
            if current_fps and current_fps < 30:
                # Снижаем качество рендеринга
                self._apply_render_optimizations()
                optimizations_applied += 1
                
            if current_cpu and current_cpu > 80:
                # Снижаем частоту обновления AI
                self._apply_ai_optimizations()
                optimizations_applied += 1
                
            if current_memory and current_memory > 85:
                # Очищаем кэш
                self._apply_memory_optimizations()
                optimizations_applied += 1
            
            if optimizations_applied > 0:
                self.performance_stats['optimizations_applied'] += optimizations_applied
                logger.info(f"Применено {optimizations_applied} оптимизаций")
                
        except Exception as e:
            logger.error(f"Ошибка применения оптимизаций: {e}")
    
    def _get_current_metric(self, metric: PerformanceMetric) -> Optional[float]:
        """Получение текущего значения метрики"""
        try:
            if self.metrics[metric]:
                return self.metrics[metric][-1].value
            return None
        except Exception:
            return None
    
    def _apply_render_optimizations(self):
        """Применение оптимизаций рендеринга"""
        # Здесь можно добавить логику снижения качества рендеринга
        pass
    
    def _apply_ai_optimizations(self):
        """Применение оптимизаций AI"""
        # Здесь можно добавить логику снижения частоты обновления AI
        pass
    
    def _apply_memory_optimizations(self):
        """Применение оптимизаций памяти"""
        # Очищаем кэш
        self.performance_cache.clear()
    
    def _get_active_alerts(self) -> List[str]:
        """Получение активных предупреждений"""
        alerts = []
        try:
            current_fps = self._get_current_metric(PerformanceMetric.FPS)
            current_cpu = self._get_current_metric(PerformanceMetric.CPU_USAGE)
            current_memory = self._get_current_metric(PerformanceMetric.MEMORY_USAGE)
            
            if current_fps and current_fps < 30:
                alerts.append(f"Низкий FPS: {current_fps:.1f}")
                
            if current_cpu and current_cpu > 80:
                alerts.append(f"Высокое использование CPU: {current_cpu:.1f}%")
                
            if current_memory and current_memory > 85:
                alerts.append(f"Высокое использование памяти: {current_memory:.1f}%")
                
        except Exception as e:
            logger.error(f"Ошибка получения предупреждений: {e}")
            
        return alerts
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'monitoring_enabled': self.monitoring_config['enabled'],
            'metrics_count': sum(len(metrics) for metrics in self.metrics.values()),
            'systems_monitored': len(self.system_performance),
            'stats': self.performance_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "performance_metric_recorded":
                metric, value, source = event_data
                self.record_metric(metric, value, source)
                return True
            elif event_type == "system_performance_recorded":
                system_name, update_time = event_data
                self.record_system_performance(system_name, update_time)
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
