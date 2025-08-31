#!/usr/bin/env python3
"""Система управления состоянием - централизованное управление игровым состоянием
Улучшенная версия с поддержкой групп, валидации и производительности"""

from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Callable
import copy
import logging
import os
import sys
import threading
import time
import weakref

from .architecture import BaseComponent, ComponentType, Priority

logger = logging.getLogger(__name__)

# = ТИПЫ СОСТОЯНИЙ

class StateType(Enum):
    """Типы состояний"""
    GLOBAL = "global"
    ENTITY = "entity"
    SYSTEM = "system"
    UI = "ui"
    TEMPORARY = "temporary"
    CONFIGURATION = "configuration"
    STATISTICS = "statistics"
    DATA = "data"

class StateScope(Enum):
    """Области видимости состояний"""
    PRIVATE = "private"
    PROTECTED = "protected"
    PUBLIC = "public"

class StateValidation(Enum):
    """Типы валидации состояний"""
    NONE = "none"
    TYPE = "type"
    RANGE = "range"
    ENUM = "enum"
    CUSTOM = "custom"

# = БАЗОВЫЕ КЛАССЫ СОСТОЯНИЙ

@dataclass
class StateChange:
    """Изменение состояния с улучшенной структурой"""
    state_id: str
    old_value: Any
    new_value: Any
    timestamp: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    change_type: str = "update"  # update, reset, restore, clear

@dataclass
class StateSnapshot:
    """Снимок состояния с версионированием"""
    state_id: str
    value: Any
    timestamp: float
    version: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None

@dataclass
class StateValidationRule:
    """Правило валидации состояния"""
    validation_type: StateValidation
    rule_data: Dict[str, Any]
    error_message: str = "Валидация не пройдена"
    custom_validator: Optional[Callable[[Any], bool]] = None

class IStateContainer(Generic[TypeVar('T')]):
    """Интерфейс для контейнера состояний"""
    
    @abstractmethod
    def get_state(self, state_id: str) -> Optional[TypeVar('T')]:
        """Получение состояния"""
        pass
    
    @abstractmethod
    def set_state(self, state_id: str, value: TypeVar('T')) -> bool:
        """Установка состояния"""
        pass
    
    @abstractmethod
    def has_state(self, state_id: str) -> bool:
        """Проверка наличия состояния"""
        pass
    
    @abstractmethod
    def remove_state(self, state_id: str) -> bool:
        """Удаление состояния"""
        pass
    
    @abstractmethod
    def get_all_states(self) -> Dict[str, TypeVar('T')]:
        """Получение всех состояний"""
        pass

# = РЕАЛИЗАЦИЯ МЕНЕДЖЕРА СОСТОЯНИЙ

class StateManager(BaseComponent):
    """Централизованный менеджер состояний"""
    
    def __init__(self):
        super().__init__(
            component_id="state_manager",
            component_type=ComponentType.MANAGER,
            priority=Priority.CRITICAL
        )
        
        # Хранилище состояний
        self._states: Dict[str, Any] = {}
        self._state_metadata: Dict[str, Dict[str, Any]] = {}
        self._state_history: Dict[str, List[StateChange]] = {}
        self._state_snapshots: Dict[str, List[StateSnapshot]] = {}
        self._validation_rules: Dict[str, StateValidationRule] = {}
        
        # Группы состояний
        self._state_groups: Dict[str, List[str]] = {}
        self._group_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Подписчики на изменения
        self._subscribers: Dict[str, List[Callable]] = {}
        self._global_subscribers: List[Callable] = []
        
        # Производительность и мониторинг
        self._change_count = 0
        self._validation_failures = 0
        self._last_cleanup = time.time()
        self._cleanup_interval = 300.0  # 5 минут
        
        # Потокобезопасность
        self._lock = threading.RLock()
        
        logger.info("StateManager инициализирован")
    
    def _on_initialize(self) -> bool:
        """Инициализация менеджера состояний"""
        try:
            # Создание базовых групп состояний
            self._create_default_groups()
            
            # Инициализация базовых состояний
            self._initialize_default_states()
            
            logger.info("StateManager успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации StateManager: {e}")
            return False
    
    def _create_default_groups(self):
        """Создание базовых групп состояний"""
        default_groups = {
            "game": {
                "description": "Игровые состояния",
                "scope": StateScope.PUBLIC,
                "auto_cleanup": False
            },
            "ui": {
                "description": "Состояния интерфейса",
                "scope": StateScope.PROTECTED,
                "auto_cleanup": True
            },
            "system": {
                "description": "Системные состояния",
                "scope": StateScope.PRIVATE,
                "auto_cleanup": False
            },
            "temporary": {
                "description": "Временные состояния",
                "scope": StateScope.PRIVATE,
                "auto_cleanup": True
            }
        }
        
        for group_name, metadata in default_groups.items():
            self.create_state_group(group_name, metadata)
    
    def _initialize_default_states(self):
        """Инициализация базовых состояний"""
        default_states = {
            "game.running": False,
            "game.paused": False,
            "game.current_level": 1,
            "system.initialized": False,
            "system.version": "1.0.0",
            "ui.main_menu_active": True,
            "ui.current_screen": "main_menu"
        }
        
        for state_id, value in default_states.items():
            self.set_state(state_id, value, source="system")
    
    def set_state(self, state_id: str, value: Any, source: str = "unknown", 
                  metadata: Dict[str, Any] = None) -> bool:
        """Установка состояния с валидацией и историей"""
        try:
            with self._lock:
                # Валидация
                if not self._validate_state(state_id, value):
                    return False
                
                # Получение старого значения
                old_value = self._states.get(state_id)
                
                # Проверка на реальное изменение
                if old_value == value:
                    return True  # Нет изменений
                
                # Установка нового значения
                self._states[state_id] = value
                
                # Обновление метаданных
                if metadata:
                    self._state_metadata[state_id] = metadata
                elif state_id not in self._state_metadata:
                    self._state_metadata[state_id] = {}
                
                # Запись в историю
                self._record_state_change(state_id, old_value, value, source)
                
                # Уведомление подписчиков
                self._notify_subscribers(state_id, old_value, value, source)
                
                self._change_count += 1
                logger.debug(f"Состояние {state_id} изменено: {old_value} -> {value}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка установки состояния {state_id}: {e}")
            return False
    
    def get_state(self, state_id: str, default: Any = None) -> Any:
        """Получение состояния"""
        try:
            with self._lock:
                return self._states.get(state_id, default)
        except Exception as e:
            logger.error(f"Ошибка получения состояния {state_id}: {e}")
            return default
    
    def has_state(self, state_id: str) -> bool:
        """Проверка наличия состояния"""
        try:
            with self._lock:
                return state_id in self._states
        except Exception as e:
            logger.error(f"Ошибка проверки состояния {state_id}: {e}")
            return False
    
    def remove_state(self, state_id: str) -> bool:
        """Удаление состояния"""
        try:
            with self._lock:
                if state_id in self._states:
                    old_value = self._states[state_id]
                    del self._states[state_id]
                    
                    # Очистка связанных данных
                    if state_id in self._state_metadata:
                        del self._state_metadata[state_id]
                    if state_id in self._state_history:
                        del self._state_history[state_id]
                    if state_id in self._validation_rules:
                        del self._validation_rules[state_id]
                    
                    # Уведомление подписчиков
                    self._notify_subscribers(state_id, old_value, None, "system")
                    
                    logger.debug(f"Состояние {state_id} удалено")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Ошибка удаления состояния {state_id}: {e}")
            return False
    
    def get_all_states(self) -> Dict[str, Any]:
        """Получение всех состояний"""
        try:
            with self._lock:
                return self._states.copy()
        except Exception as e:
            logger.error(f"Ошибка получения всех состояний: {e}")
            return {}
    
    def create_state_group(self, group_name: str, metadata: Dict[str, Any] = None) -> bool:
        """Создание группы состояний"""
        try:
            with self._lock:
                if group_name in self._state_groups:
                    logger.warning(f"Группа состояний {group_name} уже существует")
                    return False
                
                self._state_groups[group_name] = []
                self._group_metadata[group_name] = metadata or {}
                
                logger.debug(f"Создана группа состояний {group_name}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка создания группы состояний {group_name}: {e}")
            return False
    
    def add_state_to_group(self, group_name: str, state_id: str) -> bool:
        """Добавление состояния в группу"""
        try:
            with self._lock:
                if group_name not in self._state_groups:
                    logger.error(f"Группа состояний {group_name} не существует")
                    return False
                
                if state_id not in self._state_groups[group_name]:
                    self._state_groups[group_name].append(state_id)
                    logger.debug(f"Состояние {state_id} добавлено в группу {group_name}")
                
                return True
                
        except Exception as e:
            logger.error(f"Ошибка добавления состояния {state_id} в группу {group_name}: {e}")
            return False
    
    def get_group_states(self, group_name: str) -> Dict[str, Any]:
        """Получение всех состояний группы"""
        try:
            with self._lock:
                if group_name not in self._state_groups:
                    return {}
                
                group_states = {}
                for state_id in self._state_groups[group_name]:
                    if state_id in self._states:
                        group_states[state_id] = self._states[state_id]
                
                return group_states
                
        except Exception as e:
            logger.error(f"Ошибка получения состояний группы {group_name}: {e}")
            return {}
    
    def subscribe_to_state(self, state_id: str, callback: Callable) -> bool:
        """Подписка на изменения состояния"""
        try:
            with self._lock:
                if state_id not in self._subscribers:
                    self._subscribers[state_id] = []
                
                if callback not in self._subscribers[state_id]:
                    self._subscribers[state_id].append(callback)
                    logger.debug(f"Подписка на состояние {state_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"Ошибка подписки на состояние {state_id}: {e}")
            return False
    
    def unsubscribe_from_state(self, state_id: str, callback: Callable) -> bool:
        """Отписка от изменений состояния"""
        try:
            with self._lock:
                if state_id in self._subscribers and callback in self._subscribers[state_id]:
                    self._subscribers[state_id].remove(callback)
                    logger.debug(f"Отписка от состояния {state_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отписки от состояния {state_id}: {e}")
            return False
    
    def subscribe_to_all_states(self, callback: Callable) -> bool:
        """Подписка на все изменения состояний"""
        try:
            with self._lock:
                if callback not in self._global_subscribers:
                    self._global_subscribers.append(callback)
                    logger.debug("Подписка на все изменения состояний")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка подписки на все состояния: {e}")
            return False
    
    def unsubscribe_from_all_states(self, callback: Callable) -> bool:
        """Отписка от всех изменений состояний"""
        try:
            with self._lock:
                if callback in self._global_subscribers:
                    self._global_subscribers.remove(callback)
                    logger.debug("Отписка от всех изменений состояний")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отписки от всех состояний: {e}")
            return False
    
    def _validate_state(self, state_id: str, value: Any) -> bool:
        """Валидация состояния"""
        try:
            if state_id not in self._validation_rules:
                return True  # Нет правил валидации
            
            rule = self._validation_rules[state_id]
            
            if rule.validation_type == StateValidation.NONE:
                return True
            elif rule.validation_type == StateValidation.TYPE:
                expected_type = rule.rule_data.get("type")
                if expected_type and not isinstance(value, expected_type):
                    logger.warning(f"Валидация типа не пройдена для {state_id}: ожидается {expected_type}, получено {type(value)}")
                    self._validation_failures += 1
                    return False
            elif rule.validation_type == StateValidation.RANGE:
                min_val = rule.rule_data.get("min")
                max_val = rule.rule_data.get("max")
                if min_val is not None and value < min_val:
                    logger.warning(f"Валидация диапазона не пройдена для {state_id}: значение {value} меньше минимума {min_val}")
                    self._validation_failures += 1
                    return False
                if max_val is not None and value > max_val:
                    logger.warning(f"Валидация диапазона не пройдена для {state_id}: значение {value} больше максимума {max_val}")
                    self._validation_failures += 1
                    return False
            elif rule.validation_type == StateValidation.ENUM:
                allowed_values = rule.rule_data.get("values", [])
                if value not in allowed_values:
                    logger.warning(f"Валидация enum не пройдена для {state_id}: значение {value} не в списке {allowed_values}")
                    self._validation_failures += 1
                    return False
            elif rule.validation_type == StateValidation.CUSTOM:
                if rule.custom_validator and not rule.custom_validator(value):
                    logger.warning(f"Пользовательская валидация не пройдена для {state_id}")
                    self._validation_failures += 1
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации состояния {state_id}: {e}")
            return False
    
    def _record_state_change(self, state_id: str, old_value: Any, new_value: Any, source: str):
        """Запись изменения состояния в историю"""
        try:
            if state_id not in self._state_history:
                self._state_history[state_id] = []
            
            change = StateChange(
                state_id=state_id,
                old_value=old_value,
                new_value=new_value,
                timestamp=time.time(),
                source=source
            )
            
            self._state_history[state_id].append(change)
            
            # Ограничение размера истории
            if len(self._state_history[state_id]) > 100:
                self._state_history[state_id] = self._state_history[state_id][-50:]
                
        except Exception as e:
            logger.error(f"Ошибка записи изменения состояния {state_id}: {e}")
    
    def _notify_subscribers(self, state_id: str, old_value: Any, new_value: Any, source: str):
        """Уведомление подписчиков об изменении состояния"""
        try:
            # Уведомление подписчиков конкретного состояния
            if state_id in self._subscribers:
                for callback in self._subscribers[state_id]:
                    try:
                        callback(state_id, old_value, new_value, source)
                    except Exception as e:
                        logger.error(f"Ошибка в обработчике состояния {state_id}: {e}")
            
            # Уведомление глобальных подписчиков
            for callback in self._global_subscribers:
                try:
                    callback(state_id, old_value, new_value, source)
                except Exception as e:
                    logger.error(f"Ошибка в глобальном обработчике состояний: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка уведомления подписчиков для состояния {state_id}: {e}")
    
    def create_snapshot(self, state_id: str = None) -> str:
        """Создание снимка состояния или всех состояний"""
        try:
            with self._lock:
                snapshot_id = f"snapshot_{int(time.time())}"
                
                if state_id:
                    # Снимок конкретного состояния
                    if state_id in self._states:
                        snapshot = StateSnapshot(
                            state_id=state_id,
                            value=self._states[state_id],
                            timestamp=time.time(),
                            version=len(self._state_snapshots.get(state_id, [])) + 1,
                            metadata=self._state_metadata.get(state_id, {}).copy()
                        )
                        
                        if state_id not in self._state_snapshots:
                            self._state_snapshots[state_id] = []
                        
                        self._state_snapshots[state_id].append(snapshot)
                        logger.debug(f"Создан снимок состояния {state_id}")
                else:
                    # Снимок всех состояний
                    for sid in self._states:
                        snapshot = StateSnapshot(
                            state_id=sid,
                            value=self._states[sid],
                            timestamp=time.time(),
                            version=len(self._state_snapshots.get(sid, [])) + 1,
                            metadata=self._state_metadata.get(sid, {}).copy()
                        )
                        
                        if sid not in self._state_snapshots:
                            self._state_snapshots[sid] = []
                        
                        self._state_snapshots[sid].append(snapshot)
                    
                    logger.debug("Создан снимок всех состояний")
                
                return snapshot_id
                
        except Exception as e:
            logger.error(f"Ошибка создания снимка: {e}")
            return ""
    
    def restore_snapshot(self, state_id: str, version: int = None) -> bool:
        """Восстановление состояния из снимка"""
        try:
            with self._lock:
                if state_id not in self._state_snapshots:
                    logger.error(f"Снимки для состояния {state_id} не найдены")
                    return False
                
                snapshots = self._state_snapshots[state_id]
                if not snapshots:
                    logger.error(f"Снимки для состояния {state_id} пусты")
                    return False
                
                # Выбор снимка
                if version is None:
                    # Последний снимок
                    snapshot = snapshots[-1]
                else:
                    # Конкретная версия
                    snapshot = next((s for s in snapshots if s.version == version), None)
                    if not snapshot:
                        logger.error(f"Снимок версии {version} для состояния {state_id} не найден")
                        return False
                
                # Восстановление состояния
                old_value = self._states.get(state_id)
                self._states[state_id] = snapshot.value
                
                # Восстановление метаданных
                if snapshot.metadata:
                    self._state_metadata[state_id] = snapshot.metadata.copy()
                
                # Запись в историю
                self._record_state_change(state_id, old_value, snapshot.value, "snapshot_restore")
                
                # Уведомление подписчиков
                self._notify_subscribers(state_id, old_value, snapshot.value, "snapshot_restore")
                
                logger.debug(f"Восстановлено состояние {state_id} из снимка версии {snapshot.version}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка восстановления снимка для состояния {state_id}: {e}")
            return False
    
    def _on_update(self, delta_time: float) -> bool:
        """Обновление менеджера состояний"""
        try:
            # Периодическая очистка
            current_time = time.time()
            if current_time - self._last_cleanup > self._cleanup_interval:
                self._cleanup_old_data()
                self._last_cleanup = current_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления StateManager: {e}")
            return False
    
    def _cleanup_old_data(self):
        """Очистка старых данных"""
        try:
            with self._lock:
                # Очистка временных состояний
                temp_states = [state_id for state_id, metadata in self._state_metadata.items()
                             if metadata.get("auto_cleanup", False)]
                
                for state_id in temp_states:
                    if state_id in self._states:
                        del self._states[state_id]
                        logger.debug(f"Очищено временное состояние {state_id}")
                
                # Очистка старых снимков
                for state_id in list(self._state_snapshots.keys()):
                    snapshots = self._state_snapshots[state_id]
                    if len(snapshots) > 10:  # Оставляем только 10 последних снимков
                        self._state_snapshots[state_id] = snapshots[-10:]
                
                logger.debug("Выполнена очистка старых данных")
                
        except Exception as e:
            logger.error(f"Ошибка очистки старых данных: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики менеджера состояний"""
        try:
            with self._lock:
                return {
                    "total_states": len(self._states),
                    "total_groups": len(self._state_groups),
                    "total_subscribers": sum(len(subscribers) for subscribers in self._subscribers.values()),
                    "global_subscribers": len(self._global_subscribers),
                    "change_count": self._change_count,
                    "validation_failures": self._validation_failures,
                    "total_snapshots": sum(len(snapshots) for snapshots in self._state_snapshots.values()),
                    "state_history_size": sum(len(history) for history in self._state_history.values())
                }
        except Exception as e:
            logger.error(f"Ошибка получения статистики StateManager: {e}")
            return {}
    
    def cleanup(self):
        """Очистка менеджера состояний"""
        try:
            with self._lock:
                self._states.clear()
                self._state_metadata.clear()
                self._state_history.clear()
                self._state_snapshots.clear()
                self._validation_rules.clear()
                self._state_groups.clear()
                self._group_metadata.clear()
                self._subscribers.clear()
                self._global_subscribers.clear()
                
                logger.info("StateManager очищен")
                
        except Exception as e:
            logger.error(f"Ошибка очистки StateManager: {e}")

# = УТИЛИТЫ ДЛЯ РАБОТЫ С СОСТОЯНИЯМИ

def create_state_group(state_manager: StateManager, group_name: str, 
                      description: str = "", scope: StateScope = StateScope.PUBLIC,
                      auto_cleanup: bool = False) -> bool:
    """Утилита для создания группы состояний"""
    metadata = {
        "description": description,
        "scope": scope,
        "auto_cleanup": auto_cleanup,
        "created_at": time.time()
    }
    return state_manager.create_state_group(group_name, metadata)

def add_state_validation(state_manager: StateManager, state_id: str,
                        validation_type: StateValidation, rule_data: Dict[str, Any],
                        error_message: str = "Валидация не пройдена",
                        custom_validator: Callable[[Any], bool] = None) -> bool:
    """Утилита для добавления валидации состояния"""
    try:
        rule = StateValidationRule(
            validation_type=validation_type,
            rule_data=rule_data,
            error_message=error_message,
            custom_validator=custom_validator
        )
        state_manager._validation_rules[state_id] = rule
        return True
    except Exception as e:
        logger.error(f"Ошибка добавления валидации для состояния {state_id}: {e}")
        return False

logger.info("StateManager загружен")
