#!/usr/bin/env python3
"""
AI Integration System - Адаптер для интеграции существующих AI систем
Обеспечивает совместимость со старой архитектурой
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from ...core.constants import constants_manager, AIState, AIBehavior, AIDifficulty

logger = logging.getLogger(__name__)

@dataclass
class AISystemAdapter:
    """Адаптер для AI системы"""
    system_name: str
    system_instance: Any
    priority: int
    is_active: bool = True
    last_update: float = 0.0
    update_count: int = 0
    error_count: int = 0

class AIIntegrationSystem(BaseComponent):
    """
    Система интеграции AI - объединяет все существующие AI системы
    в единую архитектуру без потери функциональности
    """
    
    def __init__(self):
        super().__init__("ai_integration", ComponentType.SYSTEM, Priority.HIGH)
        
        # Адаптеры для существующих систем
        self.ai_adapters: Dict[str, AISystemAdapter] = {}
        
        # Состояние интеграции
        self.integration_state = "initializing"
        self.fallback_system = None
        
        # Метрики производительности
        self.total_ai_entities = 0
        self.active_ai_entities = 0
        self.last_performance_check = 0.0
        
        # Конфигурация
        self.max_ai_entities = 1000
        self.update_frequency = 0.1  # 10 раз в секунду
        self.performance_threshold = 0.016  # 16ms max per update
        
        logger.info("AI Integration System инициализирован")
    
    def _on_initialize(self) -> bool:
        """Инициализация системы интеграции"""
        try:
            # Создаем адаптеры для существующих систем
            self._create_system_adapters()
            
            # Проверяем доступность систем
            if not self._validate_systems():
                logger.warning("Некоторые AI системы недоступны, используется fallback")
                self._setup_fallback_system()
            
            self.integration_state = "ready"
            logger.info("AI Integration System готов к работе")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации AI Integration System: {e}")
            return False
    
    def _on_start(self) -> bool:
        """Запуск системы интеграции"""
        try:
            # Запускаем все активные адаптеры
            for adapter in self.ai_adapters.values():
                if adapter.is_active:
                    self._start_system_adapter(adapter)
            
            self.integration_state = "running"
            logger.info("AI Integration System запущен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска AI Integration System: {e}")
            return False
    
    def _on_stop(self) -> bool:
        """Остановка системы интеграции"""
        try:
            # Останавливаем все адаптеры
            for adapter in self.ai_adapters.values():
                self._stop_system_adapter(adapter)
            
            self.integration_state = "stopped"
            logger.info("AI Integration System остановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки AI Integration System: {e}")
            return False
    
    def _on_destroy(self) -> bool:
        """Уничтожение системы интеграции"""
        try:
            # Очищаем все адаптеры
            self.ai_adapters.clear()
            self.fallback_system = None
            
            logger.info("AI Integration System уничтожен")
            return True
                
        except Exception as e:
            logger.error(f"Ошибка уничтожения AI Integration System: {e}")
            return False
    
    def _create_system_adapters(self):
        """Создание адаптеров для существующих AI систем"""
        try:
            # Адаптер для UnifiedAISystem
            try:
                from .unified_ai_system import UnifiedAISystem
                unified_system = UnifiedAISystem()
                self.ai_adapters["unified"] = AISystemAdapter(
                    system_name="unified",
                    system_instance=unified_system,
                    priority=1
                )
                logger.info("Адаптер для UnifiedAISystem создан")
            except ImportError as e:
                logger.warning(f"UnifiedAISystem недоступен: {e}")
            
            # Адаптер для AISystem
            try:
                from .ai_system import AISystem
                ai_system = AISystem()
                self.ai_adapters["ai_system"] = AISystemAdapter(
                    system_name="ai_system",
                    system_instance=ai_system,
                    priority=2
                )
                logger.info("Адаптер для AISystem создан")
            except ImportError as e:
                logger.warning(f"AISystem недоступен: {e}")
            
            # Адаптер для PyTorchAISystem
            try:
                from .pytorch_ai_system import PyTorchAISystem
                pytorch_system = PyTorchAISystem()
                self.ai_adapters["pytorch"] = AISystemAdapter(
                    system_name="pytorch",
                    system_instance=pytorch_system,
                    priority=3
                )
                logger.info("Адаптер для PyTorchAISystem создан")
            except ImportError as e:
                logger.warning(f"PyTorchAISystem недоступен: {e}")
            
        except Exception as e:
            logger.error(f"Ошибка создания адаптеров: {e}")
    
    def _validate_systems(self) -> bool:
        """Проверка доступности AI систем"""
        available_systems = 0
        
        for adapter in self.ai_adapters.values():
            try:
                # Проверяем базовую функциональность
                if hasattr(adapter.system_instance, 'initialize'):
                    if adapter.system_instance.initialize():
                        available_systems += 1
                        logger.info(f"Система {adapter.system_name} доступна")
                    else:
                        adapter.is_active = False
                        logger.warning(f"Система {adapter.system_name} не инициализирована")
                else:
                    adapter.is_active = False
                    logger.warning(f"Система {adapter.system_name} не имеет метода initialize")
            except Exception as e:
                adapter.is_active = False
                logger.error(f"Ошибка валидации {adapter.system_name}: {e}")
        
        logger.info(f"Доступно AI систем: {available_systems}")
        return available_systems > 0
    
    def _setup_fallback_system(self):
        """Настройка резервной AI системы"""
        try:
            # Создаем простую резервную систему
            self.fallback_system = FallbackAISystem()
            if self.fallback_system.initialize():
                logger.info("Резервная AI система настроена")
            else:
                logger.error("Не удалось настроить резервную AI систему")
        except Exception as e:
            logger.error(f"Ошибка настройки резервной системы: {e}")
    
    def _start_system_adapter(self, adapter: AISystemAdapter):
        """Запуск адаптера системы"""
        try:
            if hasattr(adapter.system_instance, 'start'):
                if adapter.system_instance.start():
                    adapter.is_active = True
                    logger.info(f"Адаптер {adapter.system_name} запущен")
                else:
                    adapter.is_active = False
                    logger.error(f"Не удалось запустить {adapter.system_name}")
            else:
                adapter.is_active = True
                logger.info(f"Адаптер {adapter.system_name} активирован (без start)")
        except Exception as e:
            adapter.is_active = False
            logger.error(f"Ошибка запуска {adapter.system_name}: {e}")
    
    def _stop_system_adapter(self, adapter: AISystemAdapter):
        """Остановка адаптера системы"""
        try:
            if hasattr(adapter.system_instance, 'stop'):
                adapter.system_instance.stop()
                logger.info(f"Адаптер {adapter.system_name} остановлен")
        except Exception as e:
            logger.error(f"Ошибка остановки {adapter.system_name}: {e}")
        finally:
            adapter.is_active = False
    
    def get_ai_system(self, system_name: str = None) -> Optional[Any]:
        """Получение AI системы по имени или приоритету"""
        if system_name and system_name in self.ai_adapters:
            adapter = self.ai_adapters[system_name]
            if adapter.is_active:
                return adapter.system_instance
        
        # Возвращаем систему с наивысшим приоритетом
        active_adapters = [a for a in self.ai_adapters.values() if a.is_active]
        if active_adapters:
            return min(active_adapters, key=lambda x: x.priority).system_instance
        
        # Возвращаем резервную систему
        return self.fallback_system
    
    def register_ai_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        """Регистрация AI сущности во всех доступных системах"""
        try:
            success_count = 0
            
            for adapter in self.ai_adapters.values():
                if adapter.is_active and hasattr(adapter.system_instance, 'register_entity'):
                    try:
                        if adapter.system_instance.register_entity(entity_id, entity_data):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Ошибка регистрации в {adapter.system_name}: {e}")
            
            if success_count > 0:
                self.total_ai_entities += 1
                self.active_ai_entities += 1
                logger.debug(f"AI сущность {entity_id} зарегистрирована в {success_count} системах")
            return True
            else:
                logger.warning(f"AI сущность {entity_id} не зарегистрирована ни в одной системе")
                return False
            
        except Exception as e:
            logger.error(f"Ошибка регистрации AI сущности {entity_id}: {e}")
            return False
    
    def update_ai_entity(self, entity_id: str, update_data: Dict[str, Any]) -> bool:
        """Обновление AI сущности"""
        try:
            success_count = 0
            
            for adapter in self.ai_adapters.values():
                if adapter.is_active and hasattr(adapter.system_instance, 'update_entity'):
                    try:
                        if adapter.system_instance.update_entity(entity_id, update_data):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Ошибка обновления в {adapter.system_name}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Ошибка обновления AI сущности {entity_id}: {e}")
            return False
    
    def remove_ai_entity(self, entity_id: str) -> bool:
        """Удаление AI сущности"""
        try:
            success_count = 0
            
            for adapter in self.ai_adapters.values():
                if adapter.is_active and hasattr(adapter.system_instance, 'remove_entity'):
                    try:
                        if adapter.system_instance.remove_entity(entity_id):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Ошибка удаления из {adapter.system_name}: {e}")
            
            if success_count > 0:
                self.active_ai_entities = max(0, self.active_ai_entities - 1)
                logger.debug(f"AI сущность {entity_id} удалена из {success_count} систем")
                return True
            else:
                logger.warning(f"AI сущность {entity_id} не удалена ни из одной системы")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка удаления AI сущности {entity_id}: {e}")
            return False
    
    def get_ai_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение состояния AI сущности"""
        try:
            # Пытаемся получить состояние из активной системы
            for adapter in self.ai_adapters.values():
                if adapter.is_active and hasattr(adapter.system_instance, 'get_entity_state'):
                    try:
                        state = adapter.system_instance.get_entity_state(entity_id)
                        if state:
                            return state
                    except Exception as e:
                        logger.error(f"Ошибка получения состояния из {adapter.system_name}: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения состояния AI сущности {entity_id}: {e}")
            return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        current_time = time.time()
        
        # Обновляем метрики не чаще чем раз в секунду
        if current_time - self.last_performance_check < 1.0:
            return self._cached_metrics
        
        metrics = {
            'total_ai_entities': self.total_ai_entities,
            'active_ai_entities': self.active_ai_entities,
            'available_systems': len([a for a in self.ai_adapters.values() if a.is_active]),
            'integration_state': self.integration_state,
            'last_update': current_time
        }
        
        # Метрики по системам
        system_metrics = {}
        for adapter in self.ai_adapters.values():
            if adapter.is_active:
                system_metrics[adapter.system_name] = {
                    'priority': adapter.priority,
                    'update_count': adapter.update_count,
                    'error_count': adapter.error_count,
                    'last_update': adapter.last_update
                }
        
        metrics['system_metrics'] = system_metrics
        self._cached_metrics = metrics
        self.last_performance_check = current_time
        
        return metrics

# ============================================================================
# РЕЗЕРВНАЯ AI СИСТЕМА
# ============================================================================

class FallbackAISystem:
    """Простая резервная AI система для случаев недоступности основных систем"""
    
    def __init__(self):
        self.entities = {}
        self.initialized = False
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """Инициализация резервной системы"""
        try:
            self.initialized = True
            self.logger.info("Резервная AI система инициализирована")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации резервной AI системы: {e}")
            return False
    
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        """Регистрация сущности"""
        try:
            self.entities[entity_id] = {
                'data': entity_data,
                'state': 'idle',
                'last_update': time.time()
            }
            return True
        except Exception as e:
            self.logger.error(f"Ошибка регистрации сущности {entity_id}: {e}")
            return False
    
    def update_entity(self, entity_id: str, update_data: Dict[str, Any]) -> bool:
        """Обновление сущности"""
        try:
            if entity_id in self.entities:
                self.entities[entity_id].update(update_data)
                self.entities[entity_id]['last_update'] = time.time()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка обновления сущности {entity_id}: {e}")
            return False
    
    def remove_entity(self, entity_id: str) -> bool:
        """Удаление сущности"""
        try:
            if entity_id in self.entities:
                del self.entities[entity_id]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления сущности {entity_id}: {e}")
            return False
    
    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение состояния сущности"""
        return self.entities.get(entity_id)
