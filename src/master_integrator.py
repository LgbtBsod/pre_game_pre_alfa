#!/usr/bin/env python3
"""Мастер-интегратор - центральный координатор всех систем проекта
Обеспечивает интеграцию, синхронизацию и управление жизненным циклом всех компонентов"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Callable, Tuple
import logging
import os
import sys
import time
import threading
import json
import pickle
from concurrent.futures import ThreadPoolExecutor

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from src.systems.ai.ai_system import AISystem
from src.systems.evolution.evolution_system import EvolutionSystem
from src.systems.world.world_manager import WorldManager
from src.systems.quest.dynamic_quest_system import DynamicQuestSystem
from src.systems.dialogue.dialogue_system import DialogueSystem
from src.systems.crafting.crafting_system import CraftingSystem
from src.systems.trading.trading_system import TradingSystem
from src.systems.social.social_system import SocialSystem
from src.systems.content.content_system import ContentSystem
from src.systems.visualization.isometric_visualization_system import IsometricVisualizationSystem

logger = logging.getLogger(__name__)

# = ТИПЫ ИНТЕГРАЦИИ

class IntegrationType(Enum):
    """Типы интеграции"""
    FULL = "full"              # Полная интеграция
    PARTIAL = "partial"        # Частичная интеграция
    LOOSE = "loose"            # Слабая интеграция
    INDEPENDENT = "independent" # Независимая работа

class SystemStatus(Enum):
    """Статусы систем"""
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class SystemInfo:
    """Информация о системе"""
    system_id: str
    system_name: str
    system_type: ComponentType
    priority: Priority
    status: SystemStatus
    integration_type: IntegrationType
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    last_update: float = field(default_factory=time.time)
    error_count: int = 0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationEvent:
    """Событие интеграции"""
    event_id: str
    event_type: str
    source_system: str
    target_system: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    priority: Priority = Priority.NORMAL

class MasterIntegrator(BaseComponent):
    """Мастер-интегратор - центральный координатор всех систем"""
    
    def __init__(self):
        super().__init__(
            component_id="master_integrator",
            component_type=ComponentType.MANAGER,
            priority=Priority.CRITICAL
        )
        
        # Системы проекта
        self.systems: Dict[str, BaseComponent] = {}
        self.system_info: Dict[str, SystemInfo] = {}
        
        # Интеграция и события
        self.integration_events: List[IntegrationEvent] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Производительность и мониторинг
        self.performance_metrics: Dict[str, Any] = {}
        self.error_log: List[Dict[str, Any]] = []
        self.start_time: float = time.time()
        
        # Потоки и синхронизация
        self.update_thread: Optional[threading.Thread] = None
        self.is_running: bool = False
        self.update_interval: float = 0.016  # 60 FPS
        
        # Конфигурация
        self.config: Dict[str, Any] = {
            "max_events": 1000,
            "max_errors": 100,
            "performance_monitoring": True,
            "auto_recovery": True,
            "event_logging": True
        }
        
        logger.info("Мастер-интегратор инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация мастер-интегратора"""
        try:
            logger.info("Начало инициализации мастер-интегратора...")
            
            # Создание и регистрация систем
            if not self._create_systems():
                return False
            
            # Настройка зависимостей
            if not self._setup_dependencies():
                return False
            
            # Инициализация систем
            if not self._initialize_systems():
                return False
            
            # Настройка обработчиков событий
            self._setup_event_handlers()
            
            # Запуск мониторинга
            if self.config["performance_monitoring"]:
                self._start_performance_monitoring()
            
            self.state = LifecycleState.READY
            logger.info("Мастер-интегратор успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации мастер-интегратора: {e}")
            self.state = LifecycleState.ERROR
            return False
    
    def _create_systems(self) -> bool:
        """Создание всех систем проекта"""
        try:
            # Создание систем
            systems_to_create = [
                ("ai_system", AISystem, ComponentType.SYSTEM, Priority.HIGH),
                ("evolution_system", EvolutionSystem, ComponentType.SYSTEM, Priority.HIGH),
                ("world_manager", WorldManager, ComponentType.MANAGER, Priority.CRITICAL),
                ("quest_system", DynamicQuestSystem, ComponentType.SYSTEM, Priority.NORMAL),
                ("dialogue_system", DialogueSystem, ComponentType.SYSTEM, Priority.NORMAL),
                ("crafting_system", CraftingSystem, ComponentType.SYSTEM, Priority.NORMAL),
                ("trading_system", TradingSystem, ComponentType.SYSTEM, Priority.NORMAL),
                ("social_system", SocialSystem, ComponentType.SYSTEM, Priority.NORMAL),
                ("content_system", ContentSystem, ComponentType.SYSTEM, Priority.HIGH),
                ("isometric_visualization_system", IsometricVisualizationSystem, ComponentType.SYSTEM, Priority.HIGH)
            ]
            
            for system_id, system_class, system_type, priority in systems_to_create:
                try:
                    system = system_class()
                    self.systems[system_id] = system
                    
                    # Создание информации о системе
                    system_info = SystemInfo(
                        system_id=system_id,
                        system_name=system.component_id,
                        system_type=system_type,
                        priority=priority,
                        status=SystemStatus.UNKNOWN,
                        integration_type=IntegrationType.FULL
                    )
                    self.system_info[system_id] = system_info
                    
                    logger.debug(f"Система {system_id} создана")
                    
                except Exception as e:
                    logger.error(f"Ошибка создания системы {system_id}: {e}")
                    return False
            
            logger.info(f"Создано {len(self.systems)} систем")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания систем: {e}")
            return False
    
    def _setup_dependencies(self) -> bool:
        """Настройка зависимостей между системами"""
        try:
            # Определение зависимостей
            dependencies = {
                "ai_system": ["evolution_system"],
                "evolution_system": [],
                "content_system": ["world_manager"],
                "isometric_visualization_system": ["world_manager"],
                "world_manager": [],
                "quest_system": ["world_manager", "ai_system"],
                "dialogue_system": ["ai_system", "social_system"],
                "crafting_system": ["world_manager"],
                "trading_system": ["world_manager", "social_system"],
                "social_system": ["ai_system"]
            }
            
            # Установка зависимостей
            for system_id, deps in dependencies.items():
                if system_id in self.system_info:
                    self.system_info[system_id].dependencies = deps
                    
                    # Установка обратных зависимостей
                    for dep in deps:
                        if dep in self.system_info:
                            self.system_info[dep].dependents.append(system_id)
            
            logger.info("Зависимости между системами настроены")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки зависимостей: {e}")
            return False
    
    def _initialize_systems(self) -> bool:
        """Инициализация всех систем в правильном порядке"""
        try:
            # Определение порядка инициализации на основе зависимостей
            initialization_order = self._get_initialization_order()
            
            for system_id in initialization_order:
                if system_id not in self.systems:
                    continue
                
                system = self.systems[system_id]
                system_info = self.system_info[system_id]
                
                try:
                    logger.info(f"Инициализация системы {system_id}...")
                    system_info.status = SystemStatus.INITIALIZING
                    
                    if system.initialize():
                        system_info.status = SystemStatus.READY
                        logger.info(f"Система {system_id} успешно инициализирована")
                    else:
                        system_info.status = SystemStatus.ERROR
                        logger.error(f"Ошибка инициализации системы {system_id}")
                        if not self.config["auto_recovery"]:
                            return False
                        
                except Exception as e:
                    system_info.status = SystemStatus.ERROR
                    system_info.error_count += 1
                    logger.error(f"Исключение при инициализации системы {system_id}: {e}")
                    
                    if not self.config["auto_recovery"]:
                        return False
            
            logger.info("Все системы инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации систем: {e}")
            return False
    
    def _get_initialization_order(self) -> List[str]:
        """Получение порядка инициализации систем"""
        try:
            # Топологическая сортировка для определения порядка
            visited = set()
            temp_visited = set()
            order = []
            
            def dfs(system_id: str):
                if system_id in temp_visited:
                    raise Exception(f"Циклическая зависимость обнаружена: {system_id}")
                
                if system_id in visited:
                    return
                
                temp_visited.add(system_id)
                
                # Обработка зависимостей
                if system_id in self.system_info:
                    for dep in self.system_info[system_id].dependencies:
                        if dep in self.systems:
                            dfs(dep)
                
                temp_visited.remove(system_id)
                visited.add(system_id)
                order.append(system_id)
            
            # Обход всех систем
            for system_id in self.systems.keys():
                if system_id not in visited:
                    dfs(system_id)
            
            return order
            
        except Exception as e:
            logger.error(f"Ошибка определения порядка инициализации: {e}")
            return list(self.systems.keys())
    
    def _setup_event_handlers(self):
        """Настройка обработчиков событий"""
        try:
            # Регистрация обработчиков событий
            event_handlers = {
                "system_error": [self._handle_system_error],
                "system_status_change": [self._handle_status_change],
                "performance_alert": [self._handle_performance_alert],
                "integration_event": [self._handle_integration_event]
            }
            
            for event_type, handlers in event_handlers.items():
                self.event_handlers[event_type] = handlers
            
            logger.info("Обработчики событий настроены")
            
        except Exception as e:
            logger.error(f"Ошибка настройки обработчиков событий: {e}")
    
    def start(self) -> bool:
        """Запуск мастер-интегратора"""
        try:
            if self.state != LifecycleState.READY:
                logger.error("Мастер-интегратор не готов к запуску")
                return False
            
            logger.info("Запуск мастер-интегратора...")
            
            # Запуск систем
            for system_id, system in self.systems.items():
                if system.state == LifecycleState.READY:
                    try:
                        if system.start():
                            self.system_info[system_id].status = SystemStatus.RUNNING
                            logger.debug(f"Система {system_id} запущена")
                        else:
                            self.system_info[system_id].status = SystemStatus.ERROR
                            logger.error(f"Ошибка запуска системы {system_id}")
                    except Exception as e:
                        self.system_info[system_id].status = SystemStatus.ERROR
                        logger.error(f"Исключение при запуске системы {system_id}: {e}")
            
            # Запуск основного цикла обновления
            self.is_running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            self.state = LifecycleState.RUNNING
            logger.info("Мастер-интегратор запущен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска мастер-интегратора: {e}")
            return False
    
    def _update_loop(self):
        """Основной цикл обновления"""
        try:
            last_update = time.time()
            
            while self.is_running:
                current_time = time.time()
                delta_time = current_time - last_update
                
                # Обновление систем
                self._update_systems(delta_time)
                
                # Обработка событий
                self._process_events()
                
                # Обновление метрик производительности
                if self.config["performance_monitoring"]:
                    self._update_performance_metrics(delta_time)
                
                # Ограничение частоты обновления
                sleep_time = max(0, self.update_interval - (time.time() - current_time))
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                last_update = current_time
                
        except Exception as e:
            logger.error(f"Ошибка в цикле обновления: {e}")
            self.is_running = False
    
    def _update_systems(self, delta_time: float):
        """Обновление всех систем"""
        try:
            for system_id, system in self.systems.items():
                if system.state == LifecycleState.RUNNING:
                    try:
                        system.update(delta_time)
                        self.system_info[system_id].last_update = time.time()
                    except Exception as e:
                        self._handle_system_error(system_id, e)
                        
        except Exception as e:
            logger.error(f"Ошибка обновления систем: {e}")
    
    def _process_events(self):
        """Обработка событий интеграции"""
        try:
            # Обработка событий в порядке приоритета
            events_by_priority = {}
            for event in self.integration_events:
                priority_value = event.priority.value
                if priority_value not in events_by_priority:
                    events_by_priority[priority_value] = []
                events_by_priority[priority_value].append(event)
            
            # Обработка событий от высшего приоритета к низшему
            for priority_value in sorted(events_by_priority.keys()):
                for event in events_by_priority[priority_value]:
                    self._handle_integration_event(event)
            
            # Очистка обработанных событий
            self.integration_events.clear()
            
        except Exception as e:
            logger.error(f"Ошибка обработки событий: {e}")
    
    def _handle_system_error(self, system_id: str, error: Exception):
        """Обработка ошибки системы"""
        try:
            system_info = self.system_info.get(system_id)
            if system_info:
                system_info.error_count += 1
                system_info.status = SystemStatus.ERROR
            
            # Запись ошибки в лог
            error_record = {
                "timestamp": time.time(),
                "system_id": system_id,
                "error": str(error),
                "error_type": type(error).__name__
            }
            self.error_log.append(error_record)
            
            # Ограничение размера лога ошибок
            if len(self.error_log) > self.config["max_errors"]:
                self.error_log.pop(0)
            
            logger.error(f"Ошибка системы {system_id}: {error}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки ошибки системы: {e}")
    
    def _handle_status_change(self, system_id: str, old_status: SystemStatus, new_status: SystemStatus):
        """Обработка изменения статуса системы"""
        try:
            logger.info(f"Изменение статуса системы {system_id}: {old_status.value} -> {new_status.value}")
            
            # Обновление информации о системе
            if system_id in self.system_info:
                self.system_info[system_id].status = new_status
            
        except Exception as e:
            logger.error(f"Ошибка обработки изменения статуса: {e}")
    
    def _handle_performance_alert(self, system_id: str, metrics: Dict[str, Any]):
        """Обработка предупреждения о производительности"""
        try:
            logger.warning(f"Предупреждение производительности системы {system_id}: {metrics}")
            
            # Обновление метрик производительности
            if system_id in self.system_info:
                self.system_info[system_id].performance_metrics.update(metrics)
            
        except Exception as e:
            logger.error(f"Ошибка обработки предупреждения производительности: {e}")
    
    def _handle_integration_event(self, event: IntegrationEvent):
        """Обработка события интеграции"""
        try:
            if self.config["event_logging"]:
                logger.debug(f"Обработка события интеграции: {event.event_type} от {event.source_system}")
            
            # Здесь можно добавить специфичную логику обработки событий
            
        except Exception as e:
            logger.error(f"Ошибка обработки события интеграции: {e}")
    
    def _start_performance_monitoring(self):
        """Запуск мониторинга производительности"""
        try:
            # Инициализация метрик производительности
            self.performance_metrics = {
                "start_time": time.time(),
                "total_updates": 0,
                "average_update_time": 0.0,
                "system_performance": {}
            }
            
            logger.info("Мониторинг производительности запущен")
            
        except Exception as e:
            logger.error(f"Ошибка запуска мониторинга производительности: {e}")
    
    def _update_performance_metrics(self, delta_time: float):
        """Обновление метрик производительности"""
        try:
            self.performance_metrics["total_updates"] += 1
            
            # Обновление среднего времени обновления
            total_updates = self.performance_metrics["total_updates"]
            current_avg = self.performance_metrics["average_update_time"]
            self.performance_metrics["average_update_time"] = (
                (current_avg * (total_updates - 1) + delta_time) / total_updates
            )
            
            # Обновление метрик систем
            for system_id, system_info in self.system_info.items():
                if system_id not in self.performance_metrics["system_performance"]:
                    self.performance_metrics["system_performance"][system_id] = {}
                
                self.performance_metrics["system_performance"][system_id].update({
                    "status": system_info.status.value,
                    "error_count": system_info.error_count,
                    "last_update": system_info.last_update
                })
            
        except Exception as e:
            logger.error(f"Ошибка обновления метрик производительности: {e}")
    
    def pause(self) -> bool:
        """Приостановка мастер-интегратора"""
        try:
            logger.info("Приостановка мастер-интегратора...")
            
            # Приостановка систем
            for system_id, system in self.systems.items():
                if system.state == LifecycleState.RUNNING:
                    try:
                        if system.pause():
                            self.system_info[system_id].status = SystemStatus.PAUSED
                    except Exception as e:
                        logger.error(f"Ошибка приостановки системы {system_id}: {e}")
            
            self.state = LifecycleState.PAUSED
            logger.info("Мастер-интегратор приостановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка приостановки мастер-интегратора: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление мастер-интегратора"""
        try:
            logger.info("Возобновление мастер-интегратора...")
            
            # Возобновление систем
            for system_id, system in self.systems.items():
                if system.state == LifecycleState.PAUSED:
                    try:
                        if system.resume():
                            self.system_info[system_id].status = SystemStatus.RUNNING
                    except Exception as e:
                        logger.error(f"Ошибка возобновления системы {system_id}: {e}")
            
            self.state = LifecycleState.RUNNING
            logger.info("Мастер-интегратор возобновлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка возобновления мастер-интегратора: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка мастер-интегратора"""
        try:
            logger.info("Остановка мастер-интегратора...")
            
            # Остановка основного цикла
            self.is_running = False
            
            # Остановка систем
            for system_id, system in self.systems.items():
                try:
                    if system.state in [LifecycleState.RUNNING, LifecycleState.PAUSED]:
                        if system.stop():
                            self.system_info[system_id].status = SystemStatus.STOPPED
                except Exception as e:
                    logger.error(f"Ошибка остановки системы {system_id}: {e}")
            
            self.state = LifecycleState.STOPPED
            logger.info("Мастер-интегратор остановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки мастер-интегратора: {e}")
            return False
    
    def cleanup(self):
        """Очистка мастер-интегратора"""
        try:
            logger.info("Очистка мастер-интегратора...")
            
            # Остановка
            self.stop()
            
            # Очистка систем
            for system_id, system in self.systems.items():
                try:
                    system.cleanup()
                except Exception as e:
                    logger.error(f"Ошибка очистки системы {system_id}: {e}")
            
            # Очистка данных
            self.systems.clear()
            self.system_info.clear()
            self.integration_events.clear()
            self.event_handlers.clear()
            self.performance_metrics.clear()
            self.error_log.clear()
            
            self.state = LifecycleState.DESTROYED
            logger.info("Мастер-интегратор очищен")
            
        except Exception as e:
            logger.error(f"Ошибка очистки мастер-интегратора: {e}")
    
    def get_system(self, system_id: str) -> Optional[BaseComponent]:
        """Получение системы по ID"""
        return self.systems.get(system_id)
    
    def get_system_status(self, system_id: str) -> Optional[SystemStatus]:
        """Получение статуса системы"""
        system_info = self.system_info.get(system_id)
        return system_info.status if system_info else None
    
    def get_all_systems_status(self) -> Dict[str, SystemStatus]:
        """Получение статуса всех систем"""
        return {system_id: info.status for system_id, info in self.system_info.items()}
    
    def add_integration_event(self, event: IntegrationEvent):
        """Добавление события интеграции"""
        try:
            self.integration_events.append(event)
            
            # Ограничение количества событий
            if len(self.integration_events) > self.config["max_events"]:
                self.integration_events.pop(0)
                
        except Exception as e:
            logger.error(f"Ошибка добавления события интеграции: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Получение отчета о производительности"""
        try:
            uptime = time.time() - self.start_time
            
            return {
                "uptime": uptime,
                "total_systems": len(self.systems),
                "running_systems": sum(1 for info in self.system_info.values() 
                                     if info.status == SystemStatus.RUNNING),
                "error_count": sum(info.error_count for info in self.system_info.values()),
                "performance_metrics": self.performance_metrics,
                "system_status": self.get_all_systems_status()
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения отчета о производительности: {e}")
            return {}
    
    def get_error_log(self) -> List[Dict[str, Any]]:
        """Получение лога ошибок"""
        return self.error_log.copy()
    
    def update(self, delta_time: float):
        """Обновление мастер-интегратора"""
        # Обновление происходит в отдельном потоке
        pass
