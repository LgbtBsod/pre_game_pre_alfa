#!/usr/bin/env python3
"""Менеджер систем - управление всеми системами игры"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Type, Callable
from collections import defaultdict

from .event_system import EventPriority
from .interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)

# = ТИПЫ УПРАВЛЕНИЯ

class SystemOperation(Enum):
    """Операции с системами"""
    REGISTER = "register"
    UNREGISTER = "unregister"
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    RESTART = "restart"
    UPDATE = "update"

class SystemStatus(Enum):
    """Статусы систем"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    WARNING = "warning"
    MAINTENANCE = "maintenance"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class SystemInfo:
    """Информация о системе"""
    system_id: str
    system_name: str
    system_type: str
    priority: SystemPriority
    state: SystemState
    status: SystemStatus
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    last_update: float = 0.0
    error_count: int = 0
    warning_count: int = 0

@dataclass
class SystemOperationResult:
    """Результат операции с системой"""
    success: bool
    operation: SystemOperation
    system_id: str
    message: str
    timestamp: float = field(default_factory=time.time)
    error_details: Optional[str] = None

class SystemManager:
    """Менеджер систем - управление всеми системами игры"""
    
    def __init__(self):
        self.systems: Dict[str, ISystem] = {}
        self.system_info: Dict[str, SystemInfo] = {}
        self.system_dependencies: Dict[str, List[str]] = defaultdict(list)
        self.system_dependents: Dict[str, List[str]] = defaultdict(list)
        self.event_system = None
        self.is_initialized = False
        
        # Статистика
        self.stats = {
            'total_systems': 0,
            'active_systems': 0,
            'error_systems': 0,
            'operations_performed': 0,
            'last_operation_time': 0.0
        }
        
        logger.info("SystemManager создан")
    
    def initialize(self, event_system=None) -> bool:
        """Инициализация менеджера систем"""
        try:
            self.event_system = event_system
            
            # Подписываемся на события систем
            if self.event_system:
                self.event_system.subscribe("system_ready", self._handle_system_ready, "system_manager", EventPriority.HIGH)
                self.event_system.subscribe("system_error", self._handle_system_error, "system_manager", EventPriority.CRITICAL)
            
            self.is_initialized = True
            logger.info("SystemManager успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации SystemManager: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Завершение работы менеджера систем"""
        try:
            # Останавливаем все системы
            for system_id in list(self.systems.keys()):
                self.stop_system(system_id)
            
            self.is_initialized = False
            logger.info("SystemManager успешно завершен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка завершения SystemManager: {e}")
            return False
    
    # = УПРАВЛЕНИЕ СИСТЕМАМИ
    
    def register_system(self, system: ISystem) -> SystemOperationResult:
        """Регистрация системы"""
        try:
            system_id = system.system_id
            system_name = system.system_name
            
            if system_id in self.systems:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.REGISTER,
                    system_id=system_id,
                    message=f"Система {system_name} уже зарегистрирована"
                )
            
            # Регистрируем систему
            self.systems[system_id] = system
            self.system_info[system_id] = SystemInfo(
                system_id=system_id,
                system_name=system_name,
                system_type=getattr(system, 'system_type', 'unknown').value if hasattr(system, 'system_type') else 'unknown',
                priority=system.system_priority,
                state=system.system_state,
                status=SystemStatus.INACTIVE
            )
            
            # Обновляем статистику
            self.stats['total_systems'] += 1
            self.stats['operations_performed'] += 1
            self.stats['last_operation_time'] = time.time()
            
            logger.info(f"Система {system_name} зарегистрирована")
            
            # Отправляем событие
            if self.event_system:
                self.event_system.emit("system_registered", {
                    "system_id": system_id,
                    "system_name": system_name
                }, "system_manager")
            
            return SystemOperationResult(
                success=True,
                operation=SystemOperation.REGISTER,
                system_id=system_id,
                message=f"Система {system_name} успешно зарегистрирована"
            )
            
        except Exception as e:
            logger.error(f"Ошибка регистрации системы {system_id}: {e}")
            return SystemOperationResult(
                success=False,
                operation=SystemOperation.REGISTER,
                system_id=system_id,
                message=f"Ошибка регистрации: {str(e)}",
                error_details=str(e)
            )
    
    def unregister_system(self, system_id: str) -> SystemOperationResult:
        """Отмена регистрации системы"""
        try:
            if system_id not in self.systems:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.UNREGISTER,
                    system_id=system_id,
                    message=f"Система {system_id} не найдена"
                )
            
            system = self.systems[system_id]
            system_name = system.system_name
            
            # Останавливаем систему перед удалением
            if system.system_state in [SystemState.RUNNING, SystemState.PAUSED]:
                system.stop()
            
            # Удаляем систему
            del self.systems[system_id]
            del self.system_info[system_id]
            
            # Обновляем статистику
            self.stats['total_systems'] -= 1
            if system_id in [sid for sid, info in self.system_info.items() if info.status == SystemStatus.ACTIVE]:
                self.stats['active_systems'] -= 1
            self.stats['operations_performed'] += 1
            self.stats['last_operation_time'] = time.time()
            
            logger.info(f"Система {system_name} отменена регистрация")
            
            # Отправляем событие
            if self.event_system:
                self.event_system.emit("system_unregistered", {
                    "system_id": system_id,
                    "system_name": system_name
                }, "system_manager")
            
            return SystemOperationResult(
                success=True,
                operation=SystemOperation.UNREGISTER,
                system_id=system_id,
                message=f"Система {system_name} успешно отменена регистрация"
            )
            
        except Exception as e:
            logger.error(f"Ошибка отмены регистрации системы {system_id}: {e}")
            return SystemOperationResult(
                success=False,
                operation=SystemOperation.UNREGISTER,
                system_id=system_id,
                message=f"Ошибка отмены регистрации: {str(e)}",
                error_details=str(e)
            )
    
    def start_system(self, system_id: str) -> SystemOperationResult:
        """Запуск системы"""
        try:
            if system_id not in self.systems:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.START,
                    system_id=system_id,
                    message=f"Система {system_id} не найдена"
                )
            
            system = self.systems[system_id]
            system_name = system.system_name
            
            # Проверяем зависимости
            if not self._check_system_dependencies(system_id):
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.START,
                    system_id=system_id,
                    message=f"Не выполнены зависимости для {system_name}"
                )
            
            # Запускаем систему
            if system.start():
                self.system_info[system_id].state = SystemState.RUNNING
                self.system_info[system_id].status = SystemStatus.ACTIVE
                self.system_info[system_id].last_update = time.time()
                
                # Обновляем статистику
                self.stats['active_systems'] += 1
                self.stats['operations_performed'] += 1
                self.stats['last_operation_time'] = time.time()
                
                logger.info(f"Система {system_name} запущена")
                
                # Отправляем событие
                if self.event_system:
                    self.event_system.emit("system_started", {
                        "system_id": system_id,
                        "system_name": system_name
                    }, "system_manager")
                
                return SystemOperationResult(
                    success=True,
                    operation=SystemOperation.START,
                    system_id=system_id,
                    message=f"Система {system_name} успешно запущена"
                )
            else:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.START,
                    system_id=system_id,
                    message=f"Не удалось запустить систему {system_name}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка запуска системы {system_id}: {e}")
            return SystemOperationResult(
                success=False,
                operation=SystemOperation.START,
                system_id=system_id,
                message=f"Ошибка запуска: {str(e)}",
                error_details=str(e)
            )
    
    def stop_system(self, system_id: str) -> SystemOperationResult:
        """Остановка системы"""
        try:
            if system_id not in self.systems:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.STOP,
                    system_id=system_id,
                    message=f"Система {system_id} не найдена"
                )
            
            system = self.systems[system_id]
            system_name = system.system_name
            
            # Останавливаем систему
            if system.stop():
                self.system_info[system_id].state = SystemState.STOPPED
                self.system_info[system_id].status = SystemStatus.INACTIVE
                
                # Обновляем статистику
                if self.system_info[system_id].status == SystemStatus.ACTIVE:
                    self.stats['active_systems'] -= 1
                self.stats['operations_performed'] += 1
                self.stats['last_operation_time'] = time.time()
                
                logger.info(f"Система {system_name} остановлена")
                
                # Отправляем событие
                if self.event_system:
                    self.event_system.emit("system_stopped", {
                        "system_id": system_id,
                        "system_name": system_name
                    }, "system_manager")
                
                return SystemOperationResult(
                    success=True,
                    operation=SystemOperation.STOP,
                    system_id=system_id,
                    message=f"Система {system_name} успешно остановлена"
                )
            else:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.STOP,
                    system_id=system_id,
                    message=f"Не удалось остановить систему {system_name}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка остановки системы {system_id}: {e}")
            return SystemOperationResult(
                success=False,
                operation=SystemOperation.STOP,
                system_id=system_id,
                message=f"Ошибка остановки: {str(e)}",
                error_details=str(e)
            )
    
    def pause_system(self, system_id: str) -> SystemOperationResult:
        """Приостановка системы"""
        try:
            if system_id not in self.systems:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.PAUSE,
                    system_id=system_id,
                    message=f"Система {system_id} не найдена"
                )
            
            system = self.systems[system_id]
            system_name = system.system_name
            
            # Приостанавливаем систему
            if system.pause():
                self.system_info[system_id].state = SystemState.PAUSED
                self.system_info[system_id].status = SystemStatus.INACTIVE
                
                # Обновляем статистику
                if self.system_info[system_id].status == SystemStatus.ACTIVE:
                    self.stats['active_systems'] -= 1
                self.stats['operations_performed'] += 1
                self.stats['last_operation_time'] = time.time()
                
                logger.info(f"Система {system_name} приостановлена")
                
                return SystemOperationResult(
                    success=True,
                    operation=SystemOperation.PAUSE,
                    system_id=system_id,
                    message=f"Система {system_name} успешно приостановлена"
                )
            else:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.PAUSE,
                    system_id=system_id,
                    message=f"Не удалось приостановить систему {system_name}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка приостановки системы {system_id}: {e}")
            return SystemOperationResult(
                success=False,
                operation=SystemOperation.PAUSE,
                system_id=system_id,
                message=f"Ошибка приостановки: {str(e)}",
                error_details=str(e)
            )
    
    def resume_system(self, system_id: str) -> SystemOperationResult:
        """Возобновление системы"""
        try:
            if system_id not in self.systems:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.RESUME,
                    system_id=system_id,
                    message=f"Система {system_id} не найдена"
                )
            
            system = self.systems[system_id]
            system_name = system.system_name
            
            # Возобновляем систему
            if system.resume():
                self.system_info[system_id].state = SystemState.RUNNING
                self.system_info[system_id].status = SystemStatus.ACTIVE
                
                # Обновляем статистику
                self.stats['active_systems'] += 1
                self.stats['operations_performed'] += 1
                self.stats['last_operation_time'] = time.time()
                
                logger.info(f"Система {system_name} возобновлена")
                
                return SystemOperationResult(
                    success=True,
                    operation=SystemOperation.RESUME,
                    system_id=system_id,
                    message=f"Система {system_name} успешно возобновлена"
                )
            else:
                return SystemOperationResult(
                    success=False,
                    operation=SystemOperation.RESUME,
                    system_id=system_id,
                    message=f"Не удалось возобновить систему {system_name}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка возобновления системы {system_id}: {e}")
            return SystemOperationResult(
                success=False,
                operation=SystemOperation.RESUME,
                system_id=system_id,
                message=f"Ошибка возобновления: {str(e)}",
                error_details=str(e)
            )
    
    def restart_system(self, system_id: str) -> SystemOperationResult:
        """Перезапуск системы"""
        try:
            # Останавливаем систему
            stop_result = self.stop_system(system_id)
            if not stop_result.success:
                return stop_result
            
            # Запускаем систему
            start_result = self.start_system(system_id)
            if not start_result.success:
                return start_result
            
            logger.info(f"Система {system_id} успешно перезапущена")
            
            return SystemOperationResult(
                success=True,
                operation=SystemOperation.RESTART,
                system_id=system_id,
                message=f"Система {system_id} успешно перезапущена"
            )
            
        except Exception as e:
            logger.error(f"Ошибка перезапуска системы {system_id}: {e}")
            return SystemOperationResult(
                success=False,
                operation=SystemOperation.RESTART,
                system_id=system_id,
                message=f"Ошибка перезапуска: {str(e)}",
                error_details=str(e)
            )
    
    # = ОБНОВЛЕНИЕ СИСТЕМ
    
    def update_systems(self, delta_time: float) -> None:
        """Обновление всех активных систем"""
        try:
            for system_id, system in self.systems.items():
                if system.system_state == SystemState.RUNNING:
                    try:
                        system.update(delta_time)
                        self.system_info[system_id].last_update = time.time()
                    except Exception as e:
                        logger.error(f"Ошибка обновления системы {system_id}: {e}")
                        self.system_info[system_id].error_count += 1
                        self.system_info[system_id].status = SystemStatus.ERROR
                        
                        # Отправляем событие об ошибке
                        if self.event_system:
                            self.event_system.emit("system_update_error", {
                                "system_id": system_id,
                                "error": str(e)
                            }, "system_manager")
        except Exception as e:
            logger.error(f"Ошибка обновления систем: {e}")
    
    # = ЗАВИСИМОСТИ
    
    def add_system_dependency(self, system_id: str, dependency_id: str) -> bool:
        """Добавление зависимости между системами"""
        try:
            if system_id not in self.systems or dependency_id not in self.systems:
                return False
            
            self.system_dependencies[system_id].append(dependency_id)
            self.system_dependents[dependency_id].append(system_id)
            
            # Обновляем информацию о системе
            if system_id in self.system_info:
                self.system_info[system_id].dependencies.append(dependency_id)
            if dependency_id in self.system_info:
                self.system_info[dependency_id].dependents.append(system_id)
            
            logger.debug(f"Добавлена зависимость {system_id} -> {dependency_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления зависимости {system_id} -> {dependency_id}: {e}")
            return False
    
    def remove_system_dependency(self, system_id: str, dependency_id: str) -> bool:
        """Удаление зависимости между системами"""
        try:
            if system_id in self.system_dependencies:
                if dependency_id in self.system_dependencies[system_id]:
                    self.system_dependencies[system_id].remove(dependency_id)
            
            if dependency_id in self.system_dependents:
                if system_id in self.system_dependents[dependency_id]:
                    self.system_dependents[dependency_id].remove(system_id)
            
            # Обновляем информацию о системе
            if system_id in self.system_info:
                if dependency_id in self.system_info[system_id].dependencies:
                    self.system_info[system_id].dependencies.remove(dependency_id)
            if dependency_id in self.system_info:
                if system_id in self.system_info[dependency_id].dependents:
                    self.system_info[dependency_id].dependents.remove(system_id)
            
            logger.debug(f"Удалена зависимость {system_id} -> {dependency_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления зависимости {system_id} -> {dependency_id}: {e}")
            return False
    
    def _check_system_dependencies(self, system_id: str) -> bool:
        """Проверка зависимостей системы"""
        try:
            if system_id not in self.system_dependencies:
                return True
            
            for dependency_id in self.system_dependencies[system_id]:
                if dependency_id not in self.systems:
                    logger.warning(f"Зависимость {dependency_id} для {system_id} не найдена")
                    return False
                
                dependency = self.systems[dependency_id]
                if dependency.system_state != SystemState.RUNNING:
                    logger.warning(f"Зависимость {dependency_id} для {system_id} не запущена")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки зависимостей для {system_id}: {e}")
            return False
    
    # = ПОЛУЧЕНИЕ ИНФОРМАЦИИ
    
    def get_system(self, system_id: str) -> Optional[ISystem]:
        """Получение системы по ID"""
        return self.systems.get(system_id)
    
    def get_system_info(self, system_id: str) -> Optional[SystemInfo]:
        """Получение информации о системе"""
        return self.system_info.get(system_id)
    
    def get_all_systems(self) -> Dict[str, ISystem]:
        """Получение всех систем"""
        return self.systems.copy()
    
    def get_all_system_info(self) -> Dict[str, SystemInfo]:
        """Получение информации о всех системах"""
        return {name: self.get_system_info(name) for name in self.systems}
    
    def get_systems_by_type(self, system_type: str) -> List[ISystem]:
        """Получение систем по типу"""
        return [system for system in self.systems.values() 
                if getattr(system, 'system_type', None) and system.system_type.value == system_type]
    
    def get_active_systems(self) -> List[ISystem]:
        """Получение активных систем"""
        return [system for system in self.systems.values() 
                if system.system_state == SystemState.RUNNING]
    
    def get_system_count(self) -> int:
        """Получение количества систем"""
        return len(self.systems)
    
    def get_active_system_count(self) -> int:
        """Получение количества активных систем"""
        return len([s for s in self.systems.values() if s.system_state == SystemState.RUNNING])
    
    # = СТАТИСТИКА
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики менеджера систем"""
        return {
            'total_systems': self.stats['total_systems'],
            'active_systems': self.stats['active_systems'],
            'error_systems': self.stats['error_systems'],
            'operations_performed': self.stats['operations_performed'],
            'last_operation_time': self.stats['last_operation_time'],
            'system_types': list(set(info.system_type for info in self.system_info.values())),
            'system_states': {state.value: len([s for s in self.systems.values() if s.system_state == state]) 
                             for state in SystemState}
        }
    
    # = ОБРАБОТЧИКИ СОБЫТИЙ
    
    def _handle_system_ready(self, event_data: Dict[str, Any]) -> None:
        """Обработка события готовности системы"""
        try:
            system_id = event_data.get('system_id')
            if system_id and system_id in self.system_info:
                self.system_info[system_id].status = SystemStatus.ACTIVE
                logger.debug(f"Система {system_id} готова")
        except Exception as e:
            logger.error(f"Ошибка обработки события готовности системы: {e}")
    
    def _handle_system_error(self, event_data: Dict[str, Any]) -> None:
        """Обработка события ошибки системы"""
        try:
            system_id = event_data.get('system_id')
            if system_id and system_id in self.system_info:
                self.system_info[system_id].status = SystemStatus.ERROR
                self.system_info[system_id].error_count += 1
                self.stats['error_systems'] += 1
                logger.warning(f"Система {system_id} в состоянии ошибки")
        except Exception as e:
            logger.error(f"Ошибка обработки события ошибки системы: {e}")
    
    # = УТИЛИТЫ
    
    def clear_error_systems(self) -> int:
        """Очистка систем в состоянии ошибки"""
        cleared_count = 0
        for system_id, info in self.system_info.items():
            if info.status == SystemStatus.ERROR:
                try:
                    system = self.systems[system_id]
                    if system.system_state == SystemState.ERROR:
                        system.stop()
                        info.status = SystemStatus.INACTIVE
                        info.state = SystemState.STOPPED
                        cleared_count += 1
                        logger.info(f"Система {system_id} очищена от ошибок")
                except Exception as e:
                    logger.error(f"Ошибка очистки системы {system_id}: {e}")
        
        self.stats['error_systems'] = max(0, self.stats['error_systems'] - cleared_count)
        return cleared_count
    
    def get_system_dependencies(self, system_id: str) -> List[str]:
        """Получение зависимостей системы"""
        return self.system_dependencies.get(system_id, []).copy()
    
    def get_system_dependents(self, system_id: str) -> List[str]:
        """Получение зависимых систем"""
        return self.system_dependents.get(system_id, []).copy()
    
    def __str__(self) -> str:
        """Строковое представление менеджера систем"""
        return f"SystemManager({len(self.systems)} systems, {self.stats['active_systems']} active)"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"<{self.__class__.__name__} at {id(self)}>"
