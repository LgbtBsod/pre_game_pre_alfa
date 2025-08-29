#!/usr/bin/env python3
"""
Улучшенные интерфейсы для систем - интеграция с новой архитектурой
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Protocol
from dataclasses import dataclass, field
import logging
import time

from .architecture import BaseComponent, ComponentType, Priority, LifecycleState
from .state_manager import StateManager, StateType
from .repository import RepositoryManager, DataType, StorageType

logger = logging.getLogger(__name__)

# ============================================================================
# БАЗОВЫЕ ИНТЕРФЕЙСЫ СИСТЕМ
# ============================================================================

class IGameSystem(ABC):
    """Базовый интерфейс для игровых систем"""
    
    @property
    @abstractmethod
    def system_name(self) -> str:
        """Название системы"""
        pass
    
    @property
    @abstractmethod
    def system_priority(self) -> Priority:
        """Приоритет системы"""
        pass
    
    @property
    @abstractmethod
    def system_state(self) -> LifecycleState:
        """Состояние системы"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация системы"""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Запуск системы"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Остановка системы"""
        pass
    
    @abstractmethod
    def destroy(self) -> bool:
        """Уничтожение системы"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> bool:
        """Обновление системы"""
        pass
    
    @abstractmethod
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        pass
    
    @abstractmethod
    def reset_stats(self) -> None:
        """Сброс статистики системы"""
        pass

class BaseGameSystem(BaseComponent, IGameSystem):
    """Базовая реализация игровой системы"""
    
    def __init__(self, system_name: str, system_priority: Priority = Priority.NORMAL):
        super().__init__(system_name, ComponentType.SYSTEM, system_priority)
        
        # Интеграция с новой архитектурой
        self.state_manager: Optional[StateManager] = None
        self.repository_manager: Optional[RepositoryManager] = None
        self.event_bus = None
        
        # Статистика системы
        self.system_stats: Dict[str, Any] = {
            'update_count': 0,
            'total_update_time': 0.0,
            'last_update_time': 0.0,
            'errors_count': 0,
            'warnings_count': 0
        }
        
        # Состояния системы
        self.system_states: Dict[str, str] = {}
        
        # Репозитории системы
        self.system_repositories: Dict[str, str] = {}
    
    @property
    def system_name(self) -> str:
        return self.component_id
    
    @property
    def system_priority(self) -> Priority:
        return self.priority
    
    @property
    def system_state(self) -> LifecycleState:
        return self.state
    
    def set_architecture_components(self, state_manager: StateManager, 
                                  repository_manager: RepositoryManager, 
                                  event_bus=None) -> None:
        """Установка компонентов архитектуры"""
        self.state_manager = state_manager
        self.repository_manager = repository_manager
        self.event_bus = event_bus
    
    def register_system_state(self, state_id: str, initial_value: Any, 
                            state_type: StateType = StateType.SYSTEM) -> bool:
        """Регистрация состояния системы"""
        if not self.state_manager:
            return False
        
        full_state_id = f"{self.system_name}_{state_id}"
        container = self.state_manager.register_state(full_state_id, initial_value, state_type)
        if container:
            self.system_states[state_id] = full_state_id
            return True
        return False
    
    def get_system_state(self, state_id: str, default: Any = None) -> Any:
        """Получение состояния системы"""
        if not self.state_manager or state_id not in self.system_states:
            return default
        
        return self.state_manager.get_state_value(self.system_states[state_id], default)
    
    def set_system_state(self, state_id: str, value: Any) -> bool:
        """Установка состояния системы"""
        if not self.state_manager or state_id not in self.system_states:
            return False
        
        return self.state_manager.set_state_value(self.system_states[state_id], value)
    
    def register_system_repository(self, repository_id: str, data_type: DataType, 
                                 storage_type: StorageType = StorageType.MEMORY) -> bool:
        """Регистрация репозитория системы"""
        if not self.repository_manager:
            return False
        
        full_repository_id = f"{self.system_name}_{repository_id}"
        repository = self.repository_manager.create_repository(full_repository_id, data_type, storage_type)
        if repository:
            self.system_repositories[repository_id] = full_repository_id
            return True
        return False
    
    def get_system_repository(self, repository_id: str):
        """Получение репозитория системы"""
        if not self.repository_manager or repository_id not in self.system_repositories:
            return None
        
        return self.repository_manager.get_repository(self.system_repositories[repository_id])
    
    def publish_system_event(self, event_type: str, data: Dict[str, Any] = None) -> bool:
        """Публикация события системы"""
        if not self.event_bus:
            return False
        
        from .architecture import create_event
        event = create_event(event_type, self.system_name, data)
        return self.event_bus.publish(event)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        stats = self.system_stats.copy()
        stats['system_name'] = self.system_name
        stats['system_state'] = self.system_state.value
        stats['system_priority'] = self.system_priority.value
        stats['update_count'] = self._update_count
        stats['last_update'] = self._last_update
        return stats
    
    def reset_stats(self) -> None:
        """Сброс статистики системы"""
        self.system_stats = {
            'update_count': 0,
            'total_update_time': 0.0,
            'last_update_time': 0.0,
            'errors_count': 0,
            'warnings_count': 0
        }
        self._update_count = 0
    
    def _initialize_impl(self) -> bool:
        """Реализация инициализации системы"""
        try:
            # Регистрируем базовые состояния системы
            self._register_base_states()
            
            # Регистрируем базовые репозитории системы
            self._register_base_repositories()
            
            # Вызываем специфичную инициализацию
            return self._initialize_system_impl()
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы {self.system_name}: {e}")
            return False
    
    def _start_impl(self) -> bool:
        """Реализация запуска системы"""
        try:
            return self._start_system_impl()
        except Exception as e:
            logger.error(f"Ошибка запуска системы {self.system_name}: {e}")
            return False
    
    def _stop_impl(self) -> bool:
        """Реализация остановки системы"""
        try:
            return self._stop_system_impl()
        except Exception as e:
            logger.error(f"Ошибка остановки системы {self.system_name}: {e}")
            return False
    
    def _destroy_impl(self) -> bool:
        """Реализация уничтожения системы"""
        try:
            return self._destroy_system_impl()
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы {self.system_name}: {e}")
            return False
    
    def _update_impl(self, delta_time: float) -> bool:
        """Реализация обновления системы"""
        try:
            update_start = time.time()
            
            # Обновляем статистику
            self.system_stats['update_count'] += 1
            self.system_stats['last_update_time'] = delta_time
            self.system_stats['total_update_time'] += delta_time
            
            # Вызываем специфичное обновление
            result = self._update_system_impl(delta_time)
            
            # Записываем время обновления
            update_time = time.time() - update_start
            self.system_stats['last_update_time'] = update_time
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы {self.system_name}: {e}")
            self.system_stats['errors_count'] += 1
            return False
    
    def _register_base_states(self) -> None:
        """Регистрация базовых состояний системы"""
        self.register_system_state("initialized", False)
        self.register_system_state("running", False)
        self.register_system_state("error_count", 0)
        self.register_system_state("warning_count", 0)
    
    def _register_base_repositories(self) -> None:
        """Регистрация базовых репозиториев системы"""
        # Каждая система может иметь репозиторий для своих данных
        self.register_system_repository("data", DataType.STATISTICS)
    
    # Методы для переопределения в наследниках
    def _initialize_system_impl(self) -> bool:
        """Специфичная инициализация системы"""
        return True
    
    def _start_system_impl(self) -> bool:
        """Специфичный запуск системы"""
        return True
    
    def _stop_system_impl(self) -> bool:
        """Специфичная остановка системы"""
        return True
    
    def _destroy_system_impl(self) -> bool:
        """Специфичное уничтожение системы"""
        return True
    
    def _update_system_impl(self, delta_time: float) -> bool:
        """Специфичное обновление системы"""
        return True

# ============================================================================
# СПЕЦИАЛИЗИРОВАННЫЕ ИНТЕРФЕЙСЫ
# ============================================================================

class ICombatSystem(IGameSystem):
    """Интерфейс боевой системы"""
    
    @abstractmethod
    def start_combat(self, participants: List[str]) -> str:
        """Начало боя"""
        pass
    
    @abstractmethod
    def end_combat(self, combat_id: str) -> bool:
        """Завершение боя"""
        pass
    
    @abstractmethod
    def perform_attack(self, attacker_id: str, target_id: str, attack_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение атаки"""
        pass
    
    @abstractmethod
    def get_combat_stats(self, entity_id: str) -> Dict[str, Any]:
        """Получение боевой статистики"""
        pass

class IRenderSystem(Protocol):
    def initialize(self, *args, **kwargs) -> bool: ...
    def add_object(self, object_id: str, render_data: Dict[str, Any]) -> bool: ...
    def remove_object(self, object_id: str) -> bool: ...
    def update(self, delta_time: float) -> None: ...

class IEffectSystem(Protocol):
    def initialize(self, *args, **kwargs) -> bool: ...
    def apply_effect(self, target_id: str, effect_id: str, params: Dict[str, Any]) -> bool: ...
    def remove_effect(self, target_id: str, effect_id: str) -> bool: ...
    def update(self, delta_time: float) -> None: ...

class IAISystem(IGameSystem):
    """Интерфейс системы ИИ"""
    
    @abstractmethod
    def register_ai_entity(self, entity_id: str, ai_data: Dict[str, Any]) -> bool:
        """Регистрация ИИ сущности"""
        pass
    
    @abstractmethod
    def make_decision(self, entity_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Принятие решения ИИ"""
        pass
    
    @abstractmethod
    def update_ai_behavior(self, entity_id: str, behavior_data: Dict[str, Any]) -> bool:
        """Обновление поведения ИИ"""
        pass
    
    @abstractmethod
    def get_ai_memory(self, entity_id: str) -> Dict[str, Any]:
        """Получение памяти ИИ"""
        pass

class IInventorySystem(IGameSystem):
    """Интерфейс системы инвентаря"""
    
    @abstractmethod
    def add_item(self, entity_id: str, item_data: Dict[str, Any]) -> bool:
        """Добавление предмета"""
        pass
    
    @abstractmethod
    def remove_item(self, entity_id: str, item_id: str) -> bool:
        """Удаление предмета"""
        pass
    
    @abstractmethod
    def get_inventory(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение инвентаря"""
        pass
    
    @abstractmethod
    def equip_item(self, entity_id: str, item_id: str, slot: str) -> bool:
        """Экипировка предмета"""
        pass

class ISkillSystem(IGameSystem):
    """Интерфейс системы навыков"""
    
    @abstractmethod
    def learn_skill(self, entity_id: str, skill_id: str) -> bool:
        """Изучение навыка"""
        pass
    
    @abstractmethod
    def use_skill(self, entity_id: str, skill_id: str, target_id: str = None) -> bool:
        """Использование навыка"""
        pass
    
    @abstractmethod
    def get_skills(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение навыков"""
        pass
    
    @abstractmethod
    def upgrade_skill(self, entity_id: str, skill_id: str) -> bool:
        """Улучшение навыка"""
        pass

class IQuestSystem(Protocol):
    def initialize(self, state_manager, repository_manager, event_bus=None) -> bool: ...
    def start_quest(self, entity_id: str, quest_id: str) -> bool: ...
    def update(self, delta_time: float) -> None: ...

class ITradingSystem(Protocol):
    def initialize(self, state_manager, repository_manager, event_bus=None) -> bool: ...
    def create_trade_offer(self, seller_id: str, items, price: float, currency_type=None, trade_type=None) -> Optional[str]: ...
    def accept_trade_offer(self, offer_id: str, buyer_id: str, quantity: int = None) -> bool: ...
    def update(self, delta_time: float) -> None: ...

class ISocialSystem(Protocol):
    def initialize(self, state_manager, repository_manager, event_bus=None) -> bool: ...
    def perform_interaction(self, initiator_id: str, target_id: str, interaction_type, success: bool = True, data: Dict[str, Any] = None) -> bool: ...
    def update(self, delta_time: float) -> None: ...

# ============================================================================
# УТИЛИТЫ ДЛЯ РАБОТЫ С СИСТЕМАМИ
# ============================================================================

def create_system_state_group(state_manager: StateManager, system_name: str, 
                            states: Dict[str, Any]) -> bool:
    """Создание группы состояний для системы"""
    try:
        state_ids = []
        for state_id, initial_value in states.items():
            full_state_id = f"{system_name}_{state_id}"
            state_manager.register_state(full_state_id, initial_value, StateType.SYSTEM)
            state_ids.append(full_state_id)
        
        return state_manager.create_state_group(f"{system_name}_states", state_ids)
        
    except Exception as e:
        logger.error(f"Ошибка создания группы состояний для системы {system_name}: {e}")
        return False

def create_system_repository_group(repository_manager: RepositoryManager, system_name: str,
                                 repositories: Dict[str, DataType]) -> bool:
    """Создание группы репозиториев для системы"""
    try:
        for repo_id, data_type in repositories.items():
            full_repo_id = f"{system_name}_{repo_id}"
            repository_manager.create_repository(full_repo_id, data_type)
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка создания группы репозиториев для системы {system_name}: {e}")
        return False

def validate_system_dependencies(system: BaseGameSystem, 
                               required_components: List[str]) -> bool:
    """Валидация зависимостей системы"""
    missing_components = []
    
    if "state_manager" in required_components and not system.state_manager:
        missing_components.append("state_manager")
    
    if "repository_manager" in required_components and not system.repository_manager:
        missing_components.append("repository_manager")
    
    if "event_bus" in required_components and not system.event_bus:
        missing_components.append("event_bus")
    
    if missing_components:
        logger.error(f"Система {system.system_name} не имеет необходимых компонентов: {missing_components}")
        return False
    
    return True
