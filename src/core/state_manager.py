#!/usr/bin/env python3
"""
Система управления состоянием - централизованное управление игровым состоянием
"""

import logging
import time
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import copy
from abc import abstractmethod

from .architecture import BaseComponent, ComponentType, Priority, Event, create_event

logger = logging.getLogger(__name__)

# ============================================================================
# ТИПЫ СОСТОЯНИЙ
# ============================================================================

class StateType(Enum):
    """Типы состояний"""
    GLOBAL = "global"
    ENTITY = "entity"
    SYSTEM = "system"
    UI = "ui"
    TEMPORARY = "temporary"

class StateScope(Enum):
    """Области видимости состояний"""
    PRIVATE = "private"
    PROTECTED = "protected"
    PUBLIC = "public"

# ============================================================================
# БАЗОВЫЕ КЛАССЫ СОСТОЯНИЙ
# ============================================================================

@dataclass
class StateChange:
    """Изменение состояния"""
    state_id: str
    old_value: Any
    new_value: Any
    timestamp: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StateSnapshot:
    """Снимок состояния"""
    state_id: str
    value: Any
    timestamp: float
    version: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class IStateContainer(Generic[TypeVar('T')]):
    """Интерфейс контейнера состояния"""
    
    @property
    @abstractmethod
    def state_id(self) -> str:
        """Идентификатор состояния"""
        pass
    
    @property
    @abstractmethod
    def value(self) -> TypeVar('T'):
        """Значение состояния"""
        pass
    
    @value.setter
    @abstractmethod
    def value(self, new_value: TypeVar('T')) -> None:
        """Установка значения состояния"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> int:
        """Версия состояния"""
        pass
    
    @property
    @abstractmethod
    def last_modified(self) -> float:
        """Время последнего изменения"""
        pass
    
    @abstractmethod
    def subscribe(self, callback: Callable[[StateChange], None]) -> bool:
        """Подписка на изменения"""
        pass
    
    @abstractmethod
    def unsubscribe(self, callback: Callable[[StateChange], None]) -> bool:
        """Отписка от изменений"""
        pass

class StateContainer(IStateContainer[TypeVar('T')]):
    """Реализация контейнера состояния"""
    
    def __init__(self, state_id: str, initial_value: TypeVar('T'), state_type: StateType = StateType.GLOBAL, scope: StateScope = StateScope.PUBLIC):
        self._state_id = state_id
        self._value = initial_value
        self._state_type = state_type
        self._scope = scope
        self._version = 0
        self._last_modified = time.time()
        self._subscribers: List[Callable[[StateChange], None]] = []
        self._metadata: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    @property
    def state_id(self) -> str:
        return self._state_id
    
    @property
    def value(self) -> TypeVar('T'):
        with self._lock:
            return copy.deepcopy(self._value)
    
    @value.setter
    def value(self, new_value: TypeVar('T')) -> None:
        with self._lock:
            old_value = self._value
            self._value = copy.deepcopy(new_value)
            self._version += 1
            self._last_modified = time.time()
            
            # Уведомляем подписчиков
            change = StateChange(
                state_id=self._state_id,
                old_value=old_value,
                new_value=self._value,
                timestamp=self._last_modified,
                source="state_container"
            )
            
            for callback in self._subscribers:
                try:
                    callback(change)
                except Exception as e:
                    logger.error(f"Ошибка в обработчике изменения состояния {self._state_id}: {e}")
    
    @property
    def version(self) -> int:
        return self._version
    
    @property
    def last_modified(self) -> float:
        return self._last_modified
    
    def subscribe(self, callback: Callable[[StateChange], None]) -> bool:
        """Подписка на изменения"""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)
                return True
        return False
    
    def unsubscribe(self, callback: Callable[[StateChange], None]) -> bool:
        """Отписка от изменений"""
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)
                return True
        return False
    
    def get_snapshot(self) -> StateSnapshot:
        """Получение снимка состояния"""
        with self._lock:
            return StateSnapshot(
                state_id=self._state_id,
                value=copy.deepcopy(self._value),
                timestamp=self._last_modified,
                version=self._version,
                metadata=copy.deepcopy(self._metadata)
            )
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Установка метаданных"""
        with self._lock:
            self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Получение метаданных"""
        with self._lock:
            return self._metadata.get(key, default)

# ============================================================================
# МЕНЕДЖЕР СОСТОЯНИЙ
# ============================================================================

class StateManager(BaseComponent):
    """Менеджер состояний"""
    
    def __init__(self):
        super().__init__("state_manager", ComponentType.MANAGER, Priority.CRITICAL)
        self._states: Dict[str, StateContainer] = {}
        self._state_groups: Dict[str, List[str]] = {}
        self._change_history: List[StateChange] = []
        self._max_history_size = 10000
        self._event_bus = None
        self._lock = threading.RLock()
    
    def register_state(self, state_id: str, initial_value: Any, state_type: StateType = StateType.GLOBAL, scope: StateScope = StateScope.PUBLIC) -> StateContainer:
        """Регистрация нового состояния"""
        with self._lock:
            if state_id in self._states:
                logger.warning(f"Состояние {state_id} уже зарегистрировано")
                return self._states[state_id]
            
            container = StateContainer(state_id, initial_value, state_type, scope)
            self._states[state_id] = container
            
            # Подписываемся на изменения для логирования
            container.subscribe(self._on_state_change)
            
            logger.info(f"Состояние {state_id} зарегистрировано")
            return container
    
    def unregister_state(self, state_id: str) -> bool:
        """Отмена регистрации состояния"""
        with self._lock:
            if state_id not in self._states:
                return False
            
            # Удаляем из групп
            for group_name, state_ids in self._state_groups.items():
                if state_id in state_ids:
                    state_ids.remove(state_id)
            
            del self._states[state_id]
            logger.info(f"Состояние {state_id} отменено")
            return True
    
    def get_state(self, state_id: str) -> Optional[StateContainer]:
        """Получение состояния по ID"""
        with self._lock:
            return self._states.get(state_id)
    
    def get_state_value(self, state_id: str, default: Any = None) -> Any:
        """Получение значения состояния"""
        container = self.get_state(state_id)
        if container:
            return container.value
        return default
    
    def set_state_value(self, state_id: str, value: Any) -> bool:
        """Установка значения состояния"""
        container = self.get_state(state_id)
        if container:
            container.value = value
            return True
        return False
    
    def create_state_group(self, group_name: str, state_ids: List[str]) -> bool:
        """Создание группы состояний"""
        with self._lock:
            if group_name in self._state_groups:
                logger.warning(f"Группа состояний {group_name} уже существует")
                return False
            
            # Проверяем, что все состояния существуют
            valid_state_ids = []
            for state_id in state_ids:
                if state_id in self._states:
                    valid_state_ids.append(state_id)
                else:
                    logger.warning(f"Состояние {state_id} не найдено для группы {group_name}")
            
            self._state_groups[group_name] = valid_state_ids
            logger.info(f"Группа состояний {group_name} создана с {len(valid_state_ids)} состояниями")
            return True
    
    def get_state_group(self, group_name: str) -> List[StateContainer]:
        """Получение группы состояний"""
        with self._lock:
            if group_name not in self._state_groups:
                return []
            
            containers = []
            for state_id in self._state_groups[group_name]:
                if state_id in self._states:
                    containers.append(self._states[state_id])
            
            return containers
    
    def get_states_by_type(self, state_type: StateType) -> List[StateContainer]:
        """Получение состояний по типу"""
        with self._lock:
            return [container for container in self._states.values() 
                   if hasattr(container, '_state_type') and container._state_type == state_type]
    
    def get_states_by_scope(self, scope: StateScope) -> List[StateContainer]:
        """Получение состояний по области видимости"""
        with self._lock:
            return [container for container in self._states.values() 
                   if hasattr(container, '_scope') and container._scope == scope]
    
    def create_snapshot(self, state_ids: Optional[List[str]] = None) -> Dict[str, StateSnapshot]:
        """Создание снимка состояний"""
        with self._lock:
            snapshots = {}
            
            if state_ids:
                # Снимок конкретных состояний
                for state_id in state_ids:
                    if state_id in self._states:
                        snapshots[state_id] = self._states[state_id].get_snapshot()
            else:
                # Снимок всех состояний
                for state_id, container in self._states.items():
                    snapshots[state_id] = container.get_snapshot()
            
            return snapshots
    
    def restore_snapshot(self, snapshots: Dict[str, StateSnapshot]) -> bool:
        """Восстановление из снимка"""
        with self._lock:
            try:
                for state_id, snapshot in snapshots.items():
                    if state_id in self._states:
                        self._states[state_id].value = snapshot.value
                        # Восстанавливаем метаданные
                        for key, value in snapshot.metadata.items():
                            self._states[state_id].set_metadata(key, value)
                
                logger.info(f"Восстановлено {len(snapshots)} состояний из снимка")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка восстановления из снимка: {e}")
                return False
    
    def get_change_history(self, state_id: Optional[str] = None, limit: int = 100) -> List[StateChange]:
        """Получение истории изменений"""
        with self._lock:
            if state_id:
                # История конкретного состояния
                history = [change for change in self._change_history if change.state_id == state_id]
            else:
                # Вся история
                history = self._change_history.copy()
            
            # Ограничиваем количество записей
            return history[-limit:] if limit > 0 else history
    
    def clear_history(self) -> None:
        """Очистка истории изменений"""
        with self._lock:
            self._change_history.clear()
            logger.info("История изменений очищена")
    
    def _on_state_change(self, change: StateChange) -> None:
        """Обработчик изменения состояния"""
        with self._lock:
            # Добавляем в историю
            self._change_history.append(change)
            
            # Ограничиваем размер истории
            if len(self._change_history) > self._max_history_size:
                self._change_history = self._change_history[-self._max_history_size:]
            
            # Публикуем событие
            if self._event_bus:
                event = create_event(
                    event_type="state_changed",
                    source_id=self.component_id,
                    data={
                        "state_id": change.state_id,
                        "old_value": change.old_value,
                        "new_value": change.new_value,
                        "timestamp": change.timestamp
                    }
                )
                self._event_bus.publish(event)
    
    def _initialize_impl(self) -> bool:
        """Инициализация менеджера состояний"""
        try:
            # Создаем базовые состояния
            self._create_base_states()
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера состояний: {e}")
            return False
    
    def _create_base_states(self) -> None:
        """Создание базовых состояний"""
        # Глобальные состояния
        self.register_state("game_time", 0.0, StateType.GLOBAL)
        self.register_state("game_paused", False, StateType.GLOBAL)
        self.register_state("game_speed", 1.0, StateType.GLOBAL)
        self.register_state("current_scene", "menu", StateType.GLOBAL)
        
        # Системные состояния
        self.register_state("fps", 0.0, StateType.SYSTEM)
        self.register_state("memory_usage", 0.0, StateType.SYSTEM)
        self.register_state("active_entities", 0, StateType.SYSTEM)
        
        # UI состояния
        self.register_state("ui_visible", True, StateType.UI)
        self.register_state("ui_scale", 1.0, StateType.UI)
        self.register_state("ui_theme", "dark", StateType.UI)
        
        logger.info("Базовые состояния созданы")

# ============================================================================
# УТИЛИТЫ ДЛЯ РАБОТЫ С СОСТОЯНИЯМИ
# ============================================================================

def create_entity_state(entity_id: str, initial_data: Dict[str, Any]) -> Dict[str, StateContainer]:
    """Создание состояний для сущности"""
    states = {}
    
    for key, value in initial_data.items():
        state_id = f"entity_{entity_id}_{key}"
        states[key] = StateContainer(state_id, value, StateType.ENTITY)
    
    return states

def create_system_state(system_id: str, initial_data: Dict[str, Any]) -> Dict[str, StateContainer]:
    """Создание состояний для системы"""
    states = {}
    
    for key, value in initial_data.items():
        state_id = f"system_{system_id}_{key}"
        states[key] = StateContainer(state_id, value, StateType.SYSTEM)
    
    return states

def create_ui_state(ui_id: str, initial_data: Dict[str, Any]) -> Dict[str, StateContainer]:
    """Создание состояний для UI"""
    states = {}
    
    for key, value in initial_data.items():
        state_id = f"ui_{ui_id}_{key}"
        states[key] = StateContainer(state_id, value, StateType.UI)
    
    return states
