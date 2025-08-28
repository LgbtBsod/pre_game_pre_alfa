#!/usr/bin/env python3
"""
AI Interface - Единый интерфейс для всех AI систем
Обеспечивает принцип единой ответственности и модульность
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import importlib.util
from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import AIState, AIBehavior as AIPersonality, AIState as ActionType

logger = logging.getLogger(__name__)

@dataclass
class AIDecision:
    """Решение AI"""
    action_type: ActionType
    target: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    confidence: float = 0.5
    priority: int = 1

@dataclass
class AIEntity:
    """Сущность под управлением AI"""
    entity_id: str
    entity_type: str
    position: Tuple[float, float, float]
    personality: AIPersonality
    state: AIState
    memory_group: str
    data: Dict[str, Any]

class AISystemInterface(ABC):
    """
    Абстрактный интерфейс для всех AI систем
    Обеспечивает единообразный API
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация AI системы"""
        pass
    
    @abstractmethod
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any], memory_group: str = "default") -> bool:
        """Регистрация сущности в AI системе"""
        pass
    
    @abstractmethod
    def unregister_entity(self, entity_id: str) -> bool:
        """Удаление сущности из AI системы"""
        pass
    
    @abstractmethod
    def update_entity_state(self, entity_id: str, new_state: Dict[str, Any]) -> bool:
        """Обновление состояния сущности"""
        pass
    
    @abstractmethod
    def get_decision(self, entity_id: str, context: Dict[str, Any]) -> Optional[AIDecision]:
        """Получение решения AI для сущности"""
        pass
    
    @abstractmethod
    def learn_from_experience(self, entity_id: str, experience: Dict[str, Any]) -> bool:
        """Обучение на основе опыта"""
        pass
    
    @abstractmethod
    def get_entity_memory(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение памяти сущности"""
        pass
    
    @abstractmethod
    def save_memory(self, entity_id: str) -> bool:
        """Сохранение памяти сущности"""
        pass
    
    @abstractmethod
    def load_memory(self, entity_id: str) -> bool:
        """Загрузка памяти сущности"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Очистка ресурсов AI системы"""
        pass

class AISystemFactory:
    """
    Фабрика для создания AI систем
    Обеспечивает выбор оптимальной AI системы
    """
    
    @staticmethod
    def create_ai_system(system_type: str = "auto") -> AISystemInterface:
        """
        Создание AI системы
        
        Args:
            system_type: Тип системы ("pytorch", "enhanced", "basic", "auto")
        
        Returns:
            Экземпляр AI системы
        """
        if system_type == "auto":
            # Автоматический выбор лучшей доступной системы
            try:
                from .pytorch_ai_system import PyTorchAISystem
                logger.info("Создана PyTorch AI система")
                return PyTorchAISystem()
            except Exception as e:
                logger.warning(f"PyTorch AI недоступна: {e}")
                # Пробуем enhanced, если модуль существует
                if importlib.util.find_spec(__package__ + '.enhanced_ai_system') is not None:
                    try:
                        module = importlib.import_module(__package__ + '.enhanced_ai_system')
                        EnhancedAISystem = getattr(module, 'EnhancedAISystem')
                        logger.info("Создана Enhanced AI система")
                        return EnhancedAISystem()
                    except Exception as e2:
                        logger.warning(f"Enhanced AI недоступна: {e2}")
                from .ai_system import AISystem
                logger.info("Создана базовая AI система")
                return AISystem()
        
        elif system_type == "pytorch":
            try:
                from .pytorch_ai_system import PyTorchAISystem
                return PyTorchAISystem()
            except Exception as e:
                logger.warning(f"PyTorch AI недоступна: {e}; откат к базовой системе")
                from .ai_system import AISystem
                return AISystem()
        
        elif system_type == "enhanced":
            if importlib.util.find_spec(__package__ + '.enhanced_ai_system') is not None:
                try:
                    module = importlib.import_module(__package__ + '.enhanced_ai_system')
                    EnhancedAISystem = getattr(module, 'EnhancedAISystem')
                    return EnhancedAISystem()
                except Exception as e:
                    logger.warning(f"Enhanced AI недоступна: {e}; откат к базовой системе")
            from .ai_system import AISystem
            return AISystem()
        
        elif system_type == "basic":
            from .ai_system import AISystem
            return AISystem()
        
        else:
            raise ValueError(f"Неизвестный тип AI системы: {system_type}")

class AISystemManager(ISystem):
    """
    Менеджер AI систем
    Координирует работу различных AI систем
    """
    
    def __init__(self):
        # Свойства для интерфейса ISystem
        self._system_name = "ai_system_manager"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        self.ai_systems: Dict[str, AISystemInterface] = {}
        self.entity_mappings: Dict[str, str] = {}  # entity_id -> system_name
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
    
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
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self._system_name,
            'priority': self._system_priority.value,
            'state': self._system_state.value,
            'ai_systems_count': len(self.ai_systems),
            'entities_count': len(self.entity_mappings),
            'is_initialized': self.is_initialized
        }
    
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Обработка событий"""
        try:
            # Передаем событие всем AI системам
            for system in self.ai_systems.values():
                if hasattr(system, 'handle_event'):
                    system.handle_event(event_type, event_data)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы"""
        try:
            self._system_state = SystemState.PAUSED
            return True
        except Exception as e:
            self.logger.error(f"Ошибка приостановки системы: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы"""
        try:
            self._system_state = SystemState.READY
            return True
        except Exception as e:
            self.logger.error(f"Ошибка возобновления системы: {e}")
            return False
    
    def initialize(self) -> bool:
        """Инициализация AI системы"""
        try:
            self.is_initialized = True
            self._system_state = SystemState.READY
            self.logger.info("AI система успешно инициализирована")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации AI системы: {e}")
            return False
    
    def update(self, delta_time: float) -> None:
        """Обновление AI системы"""
        if not self.is_initialized:
            return
        
        try:
            self.update_all_systems(delta_time)
        except Exception as e:
            self.logger.error(f"Ошибка обновления AI системы: {e}")
    
    def cleanup(self) -> None:
        """Очистка AI системы"""
        try:
            # Очистка внутренних подсистем без рекурсии
            for name, system in list(self.ai_systems.items()):
                try:
                    system.cleanup()
                except Exception as e:
                    self.logger.error(f"Ошибка очистки AI подсистемы '{name}': {e}")
            self.ai_systems.clear()
            self.entity_mappings.clear()
            self.is_initialized = False
            self._system_state = SystemState.DESTROYED
            self.logger.info("AI система очищена")
        except Exception as e:
            self.logger.error(f"Ошибка очистки AI системы: {e}")
    
    def add_system(self, name: str, ai_system: AISystemInterface) -> bool:
        """Добавление AI системы"""
        try:
            if ai_system.initialize():
                self.ai_systems[name] = ai_system
                self.logger.info(f"AI система '{name}' добавлена")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка добавления AI системы '{name}': {e}")
            return False
    
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any], 
                       system_name: str = "default", memory_group: str = "default") -> bool:
        """Регистрация сущности в указанной AI системе"""
        if system_name not in self.ai_systems:
            self.logger.error(f"AI система '{system_name}' не найдена")
            return False
        
        try:
            if self.ai_systems[system_name].register_entity(entity_id, entity_data, memory_group):
                self.entity_mappings[entity_id] = system_name
                self.logger.debug(f"Сущность '{entity_id}' зарегистрирована в системе '{system_name}'")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка регистрации сущности '{entity_id}': {e}")
            return False
    
    def get_decision(self, entity_id: str, context: Dict[str, Any]) -> Optional[AIDecision]:
        """Получение решения AI для сущности"""
        if entity_id not in self.entity_mappings:
            self.logger.warning(f"Сущность '{entity_id}' не зарегистрирована")
            return None
        
        system_name = self.entity_mappings[entity_id]
        try:
            return self.ai_systems[system_name].get_decision(entity_id, context)
        except Exception as e:
            self.logger.error(f"Ошибка получения решения для '{entity_id}': {e}")
            return None
    
    def update_all_systems(self, delta_time: float) -> None:
        """Обновление всех AI систем"""
        for name, system in self.ai_systems.items():
            try:
                if hasattr(system, 'update'):
                    system.update(delta_time)
            except Exception as e:
                self.logger.error(f"Ошибка обновления AI системы '{name}': {e}")
    
    def cleanup(self) -> None:
        """Очистка всех AI систем"""
        for name, system in self.ai_systems.items():
            try:
                system.cleanup()
                self.logger.info(f"AI система '{name}' очищена")
            except Exception as e:
                self.logger.error(f"Ошибка очистки AI системы '{name}': {e}")
        
        self.ai_systems.clear()
        self.entity_mappings.clear()
