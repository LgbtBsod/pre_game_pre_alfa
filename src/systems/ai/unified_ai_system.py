#!/usr/bin/env python3
"""
Unified AI System - Объединенная система искусственного интеллекта
Консолидирует все AI системы в единую архитектуру без потери функциональности
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from ...core.constants import constants_manager, AIState, AIBehavior, AIDifficulty

logger = logging.getLogger(__name__)

@dataclass
class AISystemAdapter:
    """Адаптер для AI подсистемы"""
    system_name: str
    system_instance: Any
    priority: int
    is_active: bool = True
    last_update: float = 0.0
    update_count: int = 0
    error_count: int = 0
    capabilities: List[str] = field(default_factory=list)

@dataclass
class AIEntityData:
    """Данные AI сущности"""
    entity_id: str
    entity_type: str
    behavior: AIBehavior
    difficulty: AIDifficulty
    current_state: AIState
    position: tuple
    target: Optional[str] = None
    memory: Dict[str, Any] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    stats: Dict[str, float] = field(default_factory=dict)
    last_decision: float = 0.0
    decision_cooldown: float = 0.0

@dataclass
class AIDecision:
    """Решение AI"""
    entity_id: str
    decision_type: str
    target_id: Optional[str]
    action_data: Dict[str, Any]
    priority: float
    confidence: float
    timestamp: float
    executed: bool = False

class UnifiedAISystem(BaseComponent):
    """Объединенная система искусственного интеллекта с консолидированной архитектурой"""
    
    def __init__(self):
        super().__init__("unified_ai", ComponentType.SYSTEM, Priority.HIGH)
        
        # Адаптеры для AI подсистем
        self.ai_adapters: Dict[str, AISystemAdapter] = {}
        
        # AI сущности
        self.ai_entities: Dict[str, AIEntityData] = {}
        
        # Решения AI
        self.ai_decisions: Dict[str, List[AIDecision]] = {}
        
        # Группы AI
        self.ai_groups: Dict[str, List[str]] = {}
        
        # Память и опыт
        self.global_memory: Dict[str, Any] = {}
        self.experience_pool: Dict[str, float] = {}
        
        # Конфигурация
        self.max_ai_entities = 1000
        self.update_frequency = 0.1  # 10 раз в секунду
        self.decision_timeout = 1.0
        self.memory_cleanup_interval = 60.0
        
        # Состояние системы
        self.last_update = 0.0
        self.update_count = 0
        self.error_count = 0
        
        logger.info("Unified AI System инициализирован")
    
    def _on_initialize(self) -> bool:
        """Инициализация системы"""
        try:
            # Создаем адаптеры для существующих AI систем
            self._create_system_adapters()
            
            # Проверяем доступность систем
            if not self._validate_systems():
                logger.warning("Некоторые AI системы недоступны")
                self._setup_fallback_system()
            
            # Инициализируем глобальную память
            self._initialize_global_memory()
            
            logger.info("Unified AI System готов к работе")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Unified AI System: {e}")
            return False
    
    def _on_start(self) -> bool:
        """Запуск системы"""
        try:
            # Запускаем все активные адаптеры
            for adapter in self.ai_adapters.values():
                if adapter.is_active:
                    self._start_system_adapter(adapter)
            
            logger.info("Unified AI System запущен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска Unified AI System: {e}")
            return False
    
    def _on_stop(self) -> bool:
        """Остановка системы"""
        try:
            # Останавливаем все адаптеры
            for adapter in self.ai_adapters.values():
                self._stop_system_adapter(adapter)
            
            logger.info("Unified AI System остановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки Unified AI System: {e}")
            return False
    
    def _on_destroy(self) -> bool:
        """Уничтожение системы"""
        try:
            # Очищаем все адаптеры
            self.ai_adapters.clear()
            
            # Очищаем данные
            self.ai_entities.clear()
            self.ai_decisions.clear()
            self.ai_groups.clear()
            self.global_memory.clear()
            self.experience_pool.clear()
            
            logger.info("Unified AI System уничтожен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения Unified AI System: {e}")
            return False
    
    def _create_system_adapters(self):
        """Создание адаптеров для существующих AI систем"""
        try:
            # Адаптер для AISystem (основная система)
            try:
                from .ai_system import AISystem
                ai_system = AISystem()
                self.ai_adapters["ai_system"] = AISystemAdapter(
                    system_name="ai_system",
                    system_instance=ai_system,
                    priority=1,
                    capabilities=["behavior_trees", "rule_based", "basic_learning"]
                )
                logger.info("Адаптер для AISystem создан")
            except ImportError as e:
                logger.warning(f"AISystem недоступен: {e}")
            
            # Адаптер для PyTorchAISystem (нейронные сети)
            try:
                from .pytorch_ai_system import PyTorchAISystem
                pytorch_system = PyTorchAISystem()
                self.ai_adapters["pytorch"] = AISystemAdapter(
                    system_name="pytorch",
                    system_instance=pytorch_system,
                    priority=2,
                    capabilities=["neural_networks", "deep_learning", "reinforcement_learning"]
                )
                logger.info("Адаптер для PyTorchAISystem создан")
            except ImportError as e:
                logger.warning(f"PyTorchAISystem недоступен: {e}")
            
            # Адаптер для AIIntegrationSystem (если доступен)
            try:
                from .ai_integration_system import AIIntegrationSystem
                integration_system = AIIntegrationSystem()
                self.ai_adapters["integration"] = AISystemAdapter(
                    system_name="integration",
                    system_instance=integration_system,
                    priority=3,
                    capabilities=["integration", "fallback", "coordination"]
                )
                logger.info("Адаптер для AIIntegrationSystem создан")
            except ImportError as e:
                logger.warning(f"AIIntegrationSystem недоступен: {e}")
            
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
    
    def _initialize_global_memory(self):
        """Инициализация глобальной памяти"""
        try:
            # Базовые типы памяти
            self.global_memory = {
                "player_patterns": {},
                "combat_tactics": {},
                "environment_knowledge": {},
                "npc_relationships": {},
                "quest_progress": {},
                "world_events": {}
            }
            
            # Пул опыта
            self.experience_pool = {
                "combat": 0.0,
                "exploration": 0.0,
                "social": 0.0,
                "survival": 0.0
            }
            
            logger.info("Глобальная память инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации глобальной памяти: {e}")
    
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
    
    def get_ai_system(self, system_name: str = None, capability: str = None) -> Optional[Any]:
        """Получение AI системы по имени или возможностям"""
        if system_name and system_name in self.ai_adapters:
            adapter = self.ai_adapters[system_name]
            if adapter.is_active:
                return adapter.system_instance
        
        # Возвращаем систему с нужными возможностями
        if capability:
            for adapter in self.ai_adapters.values():
                if adapter.is_active and capability in adapter.capabilities:
                    return adapter.system_instance
        
        # Возвращаем систему с наивысшим приоритетом
        active_adapters = [a for a in self.ai_adapters.values() if a.is_active]
        if active_adapters:
            return min(active_adapters, key=lambda x: x.priority).system_instance
        
        # Возвращаем резервную систему
        return getattr(self, 'fallback_system', None)
    
    def register_ai_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        """Регистрация AI сущности во всех доступных системах"""
        try:
            success_count = 0
            
            # Регистрируем в основной системе
            primary_system = self.get_ai_system()
            if primary_system and hasattr(primary_system, 'register_entity'):
                try:
                    if primary_system.register_entity(entity_id, entity_data):
                        success_count += 1
                except Exception as e:
                    logger.error(f"Ошибка регистрации в основной системе: {e}")
            
            # Регистрируем в специализированных системах
            for adapter in self.ai_adapters.values():
                if adapter.is_active and adapter.system_name != "ai_system":
                    if hasattr(adapter.system_instance, 'register_entity'):
                        try:
                            if adapter.system_instance.register_entity(entity_id, entity_data):
                                success_count += 1
                        except Exception as e:
                            logger.error(f"Ошибка регистрации в {adapter.system_name}: {e}")
            
            if success_count > 0:
                # Создаем локальную копию данных
                self.ai_entities[entity_id] = AIEntityData(
                    entity_id=entity_id,
                    entity_type=entity_data.get('type', 'unknown'),
                    behavior=entity_data.get('behavior', AIBehavior.NEUTRAL),
                    difficulty=entity_data.get('difficulty', AIDifficulty.NORMAL),
                    current_state=AIState.IDLE,
                    position=entity_data.get('position', (0, 0, 0)),
                    memory=entity_data.get('memory', {}),
                    skills=entity_data.get('skills', []),
                    stats=entity_data.get('stats', {})
                )
                
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
            
            # Обновляем в основной системе
            primary_system = self.get_ai_system()
            if primary_system and hasattr(primary_system, 'update_entity'):
                try:
                    if primary_system.update_entity(entity_id, update_data):
                        success_count += 1
                except Exception as e:
                    logger.error(f"Ошибка обновления в основной системе: {e}")
            
            # Обновляем в специализированных системах
            for adapter in self.ai_adapters.values():
                if adapter.is_active and adapter.system_name != "ai_system":
                    if hasattr(adapter.system_instance, 'update_entity'):
                        try:
                            if adapter.system_instance.update_entity(entity_id, update_data):
                                success_count += 1
                        except Exception as e:
                            logger.error(f"Ошибка обновления в {adapter.system_name}: {e}")
            
            # Обновляем локальные данные
            if entity_id in self.ai_entities:
                entity = self.ai_entities[entity_id]
                for key, value in update_data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Ошибка обновления AI сущности {entity_id}: {e}")
            return False
    
    def remove_ai_entity(self, entity_id: str) -> bool:
        """Удаление AI сущности"""
        try:
            success_count = 0
            
            # Удаляем из основной системы
            primary_system = self.get_ai_system()
            if primary_system and hasattr(primary_system, 'remove_entity'):
                try:
                    if primary_system.remove_entity(entity_id):
                        success_count += 1
                except Exception as e:
                    logger.error(f"Ошибка удаления из основной системы: {e}")
            
            # Удаляем из специализированных систем
            for adapter in self.ai_adapters.values():
                if adapter.is_active and adapter.system_name != "ai_system":
                    if hasattr(adapter.system_instance, 'remove_entity'):
                        try:
                            if adapter.system_instance.remove_entity(entity_id):
                                success_count += 1
        except Exception as e:
                            logger.error(f"Ошибка удаления из {adapter.system_name}: {e}")
            
            # Удаляем локальные данные
            if entity_id in self.ai_entities:
                del self.ai_entities[entity_id]
            
            if success_count > 0:
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
            # Пытаемся получить состояние из основной системы
            primary_system = self.get_ai_system()
            if primary_system and hasattr(primary_system, 'get_entity_state'):
                try:
                    state = primary_system.get_entity_state(entity_id)
                    if state:
                        return state
                except Exception as e:
                    logger.error(f"Ошибка получения состояния из основной системы: {e}")
            
            # Возвращаем локальные данные
            if entity_id in self.ai_entities:
                entity = self.ai_entities[entity_id]
                return {
                    'entity_id': entity.entity_id,
                    'entity_type': entity.entity_type,
                    'behavior': entity.behavior,
                    'difficulty': entity.difficulty,
                    'current_state': entity.current_state,
                    'position': entity.position,
                    'target': entity.target,
                    'memory': entity.memory,
                    'skills': entity.skills,
                    'stats': entity.stats
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения состояния AI сущности {entity_id}: {e}")
            return None
    
    def add_experience(self, experience_type: str, amount: float, source: str = None):
        """Добавление опыта в глобальный пул"""
        try:
            if experience_type in self.experience_pool:
                self.experience_pool[experience_type] += amount
                
                # Обновляем глобальную память на основе опыта
                self._update_global_memory(experience_type, amount, source)
                
                logger.debug(f"Добавлен опыт {experience_type}: {amount}")
            else:
                logger.warning(f"Неизвестный тип опыта: {experience_type}")
            
        except Exception as e:
            logger.error(f"Ошибка добавления опыта: {e}")
    
    def _update_global_memory(self, experience_type: str, amount: float, source: str = None):
        """Обновление глобальной памяти на основе опыта"""
        try:
            if experience_type == "combat":
                # Обновляем тактики боя
                if "combat_tactics" not in self.global_memory:
                    self.global_memory["combat_tactics"] = {}
                
                if source:
                    if source not in self.global_memory["combat_tactics"]:
                        self.global_memory["combat_tactics"][source] = 0.0
                    self.global_memory["combat_tactics"][source] += amount
                    
            elif experience_type == "exploration":
                # Обновляем знания об окружении
                if "environment_knowledge" not in self.global_memory:
                    self.global_memory["environment_knowledge"] = {}
                    
            elif experience_type == "social":
                # Обновляем отношения с NPC
                if "npc_relationships" not in self.global_memory:
                    self.global_memory["npc_relationships"] = {}
            
        except Exception as e:
            logger.error(f"Ошибка обновления глобальной памяти: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        metrics = {
            'total_ai_entities': len(self.ai_entities),
            'available_systems': len([a for a in self.ai_adapters.values() if a.is_active]),
            'last_update': self.last_update,
            'update_count': self.update_count,
            'error_count': self.error_count
        }
        
        # Метрики по системам
        system_metrics = {}
        for adapter in self.ai_adapters.values():
            if adapter.is_active:
                system_metrics[adapter.system_name] = {
                    'priority': adapter.priority,
                    'update_count': adapter.update_count,
                    'error_count': adapter.error_count,
                    'last_update': adapter.last_update,
                    'capabilities': adapter.capabilities
                }
        
        metrics['system_metrics'] = system_metrics
        metrics['global_memory_size'] = len(self.global_memory)
        metrics['experience_pool'] = self.experience_pool.copy()
        
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
