#!/usr/bin/env python3
"""
Unified AI System - Объединенная система искусственного интеллекта
Интегрирует все AI системы в единую архитектуру
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.system_interfaces import BaseGameSystem, Priority
from ...core.constants import (
    AIState, AIBehavior, AIDifficulty, StatType,
    BASE_STATS, PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class UnifiedAIConfig:
    """Конфигурация объединенной AI системы"""
    # Основные настройки
    enable_behavior_trees: bool = True
    enable_neural_networks: bool = True
    enable_rule_based: bool = True
    enable_learning: bool = True
    
    # Настройки производительности
    max_ai_entities: int = SYSTEM_LIMITS["max_ai_entities"]
    update_frequency: float = 0.1  # 10 раз в секунду
    decision_timeout: float = 1.0
    memory_cleanup_interval: float = 60.0
    
    # Настройки обучения
    learning_rate: float = 0.01
    experience_decay: float = 0.95
    adaptation_speed: float = 0.1
    
    # Настройки поведения
    default_behavior: AIBehavior = AIBehavior.AGGRESSIVE
    default_difficulty: AIDifficulty = AIDifficulty.NORMAL
    group_coordination: bool = True
    retreat_threshold: float = 0.2

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

class UnifiedAISystem(BaseGameSystem):
    """Объединенная система искусственного интеллекта с улучшенной архитектурой"""
    
    def __init__(self, config_manager=None, event_system=None):
        super().__init__("unified_ai", Priority.HIGH)
        
        # Внешние зависимости
        self.config_manager = config_manager
        self.event_system = event_system
        self.event_bus = None
        
        # Конфигурация системы
        self.config = UnifiedAIConfig()
        
        # AI сущности
        self.ai_entities: Dict[str, AIEntityData] = {}
        
        # Решения AI
        self.ai_decisions: Dict[str, List[AIDecision]] = {}
        
        # Группы AI
        self.ai_groups: Dict[str, List[str]] = {}
        
        # Память и опыт
        self.global_memory: Dict[str, Any] = {}
        self.experience_pool: Dict[str, float] = {}
        
        # Подсистемы AI
        self.behavior_system = None
        self.neural_system = None
        self.rule_system = None
        self.learning_system = None
        
        # Статистика
        self.stats = {
            'total_entities': 0,
            'active_entities': 0,
            'decisions_made': 0,
            'learning_events': 0,
            'update_time': 0.0
        }
        
        logger.info("Unified AI System инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы"""
        try:
            if not super().initialize():
                return False
                
            logger.info("Инициализация Unified AI System...")
            
            # Загрузка конфигурации
            if self.config_manager:
                ai_config = self.config_manager.get_config('ai_config')
                if ai_config:
                    self._load_config(ai_config)
            
            # Инициализация подсистем
            if not self._initialize_subsystems():
                return False
            
            # Регистрация обработчиков событий через event_bus (fallback на event_system)
            try:
                if self.event_bus:
                    self.event_bus.on("entity_created", self._on_entity_created)
                    self.event_bus.on("entity_destroyed", self._on_entity_destroyed)
                    self.event_bus.on("combat_started", self._on_combat_started)
                    self.event_bus.on("combat_ended", self._on_combat_ended)
                    self.event_bus.on("damage_dealt", self._on_damage_dealt)
                    self.event_bus.on("damage_received", self._on_damage_received)
                elif self.event_system:
                    self._register_event_handlers()
            except Exception:
                if self.event_system:
                    self._register_event_handlers()
            
            # Регистрация состояний и репозиториев
            self._register_system_states()
            self._register_system_repositories()
            
            logger.info("Unified AI System успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Unified AI System: {e}")
            return False
    
    def start(self) -> bool:
        """Запуск системы"""
        try:
            if not super().start():
                return False
            
            # Восстановление данных из репозиториев
            self._restore_from_repositories()
            
            logger.info("Unified AI System запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска Unified AI System: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка системы"""
        try:
            # Сохранение данных в репозитории
            self._save_to_repositories()
            
            if not super().stop():
                return False
            
            logger.info("Unified AI System остановлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки Unified AI System: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы"""
        try:
            # Сохранение данных в репозитории
            self._save_to_repositories()
            
            if not super().destroy():
                return False
            
            logger.info("Unified AI System уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения Unified AI System: {e}")
            return False
    
    def update(self, delta_time: float) -> None:
        """Обновление системы"""
        try:
            super().update(delta_time)
            
            start_time = time.time()
            
            # Обновление AI сущностей
            self._update_ai_entities(delta_time)
            
            # Обработка решений
            self._process_decisions(delta_time)
            
            # Обновление подсистем
            self._update_subsystems(delta_time)
            
            # Очистка памяти
            self._cleanup_memory(delta_time)
            
            # Обновление статистики
            self.stats['update_time'] = time.time() - start_time
            
            # Обновление состояний
            self._update_states()
            
        except Exception as e:
            logger.error(f"Ошибка обновления Unified AI System: {e}")
    
    def _initialize_subsystems(self) -> bool:
        """Инициализация подсистем AI"""
        try:
            # Система поведения (поведенческие деревья)
            if self.config.enable_behavior_trees:
                self.behavior_system = BehaviorTreeSystem()
                if not self.behavior_system.initialize():
                    logger.warning("Не удалось инициализировать систему поведенческих деревьев")
            
            # Нейронная система (если доступна)
            if self.config.enable_neural_networks:
                try:
                    self.neural_system = NeuralNetworkSystem()
                    if not self.neural_system.initialize():
                        logger.warning("Не удалось инициализировать нейронную систему")
                except Exception as e:
                    logger.warning(f"Нейронная система недоступна: {e}")
            
            # Правила поведения
            if self.config.enable_rule_based:
                self.rule_system = RuleBasedSystem()
                if not self.rule_system.initialize():
                    logger.warning("Не удалось инициализировать систему правил")
            
            # Система обучения
            if self.config.enable_learning:
                self.learning_system = LearningSystem()
                if not self.learning_system.initialize():
                    logger.warning("Не удалось инициализировать систему обучения")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации подсистем AI: {e}")
            return False
    
    def _register_event_handlers(self):
        """Регистрация обработчиков событий"""
        if not self.event_system:
            return
        
        # Обработчики событий AI
        self.event_system.subscribe("entity_created", self._on_entity_created)
        self.event_system.subscribe("entity_destroyed", self._on_entity_destroyed)
        self.event_system.subscribe("combat_started", self._on_combat_started)
        self.event_system.subscribe("combat_ended", self._on_combat_ended)
        self.event_system.subscribe("damage_dealt", self._on_damage_dealt)
        self.event_system.subscribe("damage_received", self._on_damage_received)
    
    def _register_system_states(self):
        """Регистрация состояний системы (для совместимости с тестами)"""
        if not self.state_manager:
            return
            
        try:
            # Основные настройки AI системы
            self.state_manager.register_state(
                "ai_system_settings",
                {
                    "enable_behavior_trees": self.config.enable_behavior_trees,
                    "enable_neural_networks": self.config.enable_neural_networks,
                    "enable_rule_based": self.config.enable_rule_based,
                    "enable_learning": self.config.enable_learning,
                    "max_ai_entities": self.config.max_ai_entities,
                    "update_frequency": self.config.update_frequency,
                    "learning_rate": self.config.learning_rate,
                    "default_behavior": self.config.default_behavior.value,
                    "default_difficulty": self.config.default_difficulty.value
                }
            )
            
            # Статистика AI системы
            self.state_manager.register_state(
                "ai_system_stats",
                self.stats
            )
            
            # Активные AI сущности
            self.state_manager.register_state(
                "active_ai_entities",
                {entity_id: {
                    "entity_type": data.entity_type,
                    "behavior": data.behavior.value,
                    "difficulty": data.difficulty.value,
                    "current_state": data.current_state.value,
                    "position": data.position,
                    "target": data.target
                } for entity_id, data in self.ai_entities.items()}
            )
            
            logger.debug("Состояния AI системы зарегистрированы")
            
        except Exception as e:
            logger.warning(f"Ошибка регистрации состояний AI системы: {e}")
    
    def _register_states(self):
        """Регистрация состояний в StateManager"""
        if not self.state_manager:
            return
            
        try:
            # Основные настройки AI системы
            self.state_manager.register_state(
                "ai_system_settings",
                {
                    "enable_behavior_trees": self.config.enable_behavior_trees,
                    "enable_neural_networks": self.config.enable_neural_networks,
                    "enable_rule_based": self.config.enable_rule_based,
                    "enable_learning": self.config.enable_learning,
                    "max_ai_entities": self.config.max_ai_entities,
                    "update_frequency": self.config.update_frequency,
                    "learning_rate": self.config.learning_rate,
                    "default_behavior": self.config.default_behavior.value,
                    "default_difficulty": self.config.default_difficulty.value
                }
            )
            
            # Статистика AI системы
            self.state_manager.register_state(
                "ai_system_stats",
                self.stats
            )
            
            # Активные AI сущности
            self.state_manager.register_state(
                "active_ai_entities",
                {entity_id: {
                    "entity_id": data.entity_type,
                    "behavior": data.behavior.value,
                    "difficulty": data.difficulty.value,
                    "current_state": data.current_state.value,
                    "position": data.position,
                    "target": data.target
                } for entity_id, data in self.ai_entities.items()}
            )
            
            logger.debug("Состояния AI системы зарегистрированы")
            
        except Exception as e:
            logger.warning(f"Ошибка регистрации состояний AI системы: {e}")
    
    def _register_system_repositories(self):
        """Регистрация репозиториев системы (для совместимости с тестами)"""
        if not self.repository_manager:
            return
            
        try:
            # AI сущности
            self.repository_manager.register_repository(
                "ai_entities",
                "ai_entities",
                "memory"
            )
            
            # Решения AI
            self.repository_manager.register_repository(
                "ai_decisions",
                "ai_decisions",
                "memory"
            )
            
            # Группы AI
            self.repository_manager.register_repository(
                "ai_groups",
                "ai_groups",
                "memory"
            )
            
            # Глобальная память
            self.repository_manager.register_repository(
                "ai_global_memory",
                "global_memory",
                "memory"
            )
            
            # Пул опыта
            self.repository_manager.register_repository(
                "ai_experience_pool",
                "experience_pool",
                "memory"
            )
            
            logger.debug("Репозитории AI системы зарегистрированы")
            
        except Exception as e:
            logger.warning(f"Ошибка регистрации репозиториев AI системы: {e}")
    
    def _register_repositories(self):
        """Регистрация репозиториев в RepositoryManager"""
        if not self.repository_manager:
            return
            
        try:
            # AI сущности
            self.repository_manager.register_repository(
                "ai_entities",
                "ai_entities",
                "memory"
            )
            
            # Решения AI
            self.repository_manager.register_repository(
                "ai_decisions",
                "ai_decisions",
                "memory"
            )
            
            # Группы AI
            self.repository_manager.register_repository(
                "ai_groups",
                "ai_groups",
                "memory"
            )
            
            # Глобальная память
            self.repository_manager.register_repository(
                "ai_global_memory",
                "global_memory",
                "memory"
            )
            
            # Пул опыта
            self.repository_manager.register_repository(
                "ai_experience_pool",
                "experience_pool",
                "memory"
            )
            
            logger.debug("Репозитории AI системы зарегистрированы")
            
        except Exception as e:
            logger.warning(f"Ошибка регистрации репозиториев AI системы: {e}")
    
    def _restore_from_repositories(self):
        """Восстановление данных из репозиториев"""
        if not self.repository_manager:
            return
            
        try:
            # Восстанавливаем AI сущности
            ai_entities_data = self.repository_manager.get_repository("ai_entities").get_all()
            if ai_entities_data:
                for entity_data in ai_entities_data:
                    if entity_data.get("entity_id"):
                        self.ai_entities[entity_data["entity_id"]] = AIEntityData(**entity_data)
                        self.stats['total_entities'] += 1
                        self.stats['active_entities'] += 1
            
            # Восстанавливаем решения
            ai_decisions_data = self.repository_manager.get_repository("ai_decisions").get_all()
            if ai_decisions_data:
                for decision_data in ai_decisions_data:
                    if decision_data.get("entity_id"):
                        if decision_data["entity_id"] not in self.ai_decisions:
                            self.ai_decisions[decision_data["entity_id"]] = []
                        self.ai_decisions[decision_data["entity_id"]].append(AIDecision(**decision_data))
            
            # Восстанавливаем группы
            ai_groups_data = self.repository_manager.get_repository("ai_groups").get_all()
            if ai_groups_data:
                for group_data in ai_groups_data:
                    if group_data.get("group_id") and group_data.get("entity_ids"):
                        self.ai_groups[group_data["group_id"]] = group_data["entity_ids"]
            
            # Восстанавливаем глобальную память
            global_memory_data = self.repository_manager.get_repository("ai_global_memory").get_all()
            if global_memory_data:
                for memory_data in global_memory_data:
                    if memory_data.get("key") and memory_data.get("value"):
                        self.global_memory[memory_data["key"]] = memory_data["value"]
            
            # Восстанавливаем пул опыта
            experience_pool_data = self.repository_manager.get_repository("ai_experience_pool").get_all()
            if experience_pool_data:
                for experience_data in experience_pool_data:
                    if experience_data.get("skill") and experience_data.get("value"):
                        self.experience_pool[experience_data["skill"]] = experience_data["value"]
            
            logger.debug("Данные AI системы восстановлены из репозиториев")
            
        except Exception as e:
            logger.warning(f"Ошибка восстановления данных AI системы: {e}")
    
    def _save_to_repositories(self):
        """Сохранение данных в репозитории"""
        if not self.repository_manager:
            return
            
        try:
            # Сохраняем AI сущности
            ai_entities_repo = self.repository_manager.get_repository("ai_entities")
            ai_entities_repo.clear()
            for entity_id, entity_data in self.ai_entities.items():
                ai_entities_repo.create({
                    "entity_id": entity_id,
                    "entity_type": entity_data.entity_type,
                    "behavior": entity_data.behavior.value,
                    "difficulty": entity_data.difficulty.value,
                    "current_state": entity_data.current_state.value,
                    "position": entity_data.position,
                    "target": entity_data.target,
                    "memory": entity_data.memory,
                    "skills": entity_data.skills,
                    "stats": entity_data.stats,
                    "last_decision": entity_data.last_decision,
                    "decision_cooldown": entity_data.decision_cooldown
                })
            
            # Сохраняем решения
            ai_decisions_repo = self.repository_manager.get_repository("ai_decisions")
            ai_decisions_repo.clear()
            for entity_id, decisions in self.ai_decisions.items():
                for decision in decisions:
                    ai_decisions_repo.create({
                        "entity_id": decision.entity_id,
                        "decision_type": decision.decision_type,
                        "target_id": decision.target_id,
                        "action_data": decision.action_data,
                        "priority": decision.priority,
                        "confidence": decision.confidence,
                        "timestamp": decision.timestamp,
                        "executed": decision.executed
                    })
            
            # Сохраняем группы
            ai_groups_repo = self.repository_manager.get_repository("ai_groups")
            ai_groups_repo.clear()
            for group_id, entity_ids in self.ai_groups.items():
                ai_groups_repo.create({
                    "group_id": group_id,
                    "entity_ids": entity_ids
                })
            
            # Сохраняем глобальную память
            global_memory_repo = self.repository_manager.get_repository("ai_global_memory")
            global_memory_repo.clear()
            for key, value in self.global_memory.items():
                global_memory_repo.create({
                    "key": key,
                    "value": value
                })
            
            # Сохраняем пул опыта
            experience_pool_repo = self.repository_manager.get_repository("ai_experience_pool")
            experience_pool_repo.clear()
            for skill, value in self.experience_pool.items():
                experience_pool_repo.create({
                    "skill": skill,
                    "value": value
                })
            
            logger.debug("Данные AI системы сохранены в репозитории")
            
        except Exception as e:
            logger.warning(f"Ошибка сохранения данных AI системы: {e}")
    
    def _update_states(self):
        """Обновление состояний в StateManager"""
        if not self.state_manager:
            return
            
        try:
            # Обновляем статистику
            self.state_manager.set_state_value("ai_system_stats", self.stats)
            
            # Обновляем активные AI сущности
            self.state_manager.set_state_value("active_ai_entities", {
                entity_id: {
                    "entity_type": data.entity_type,
                    "behavior": data.behavior.value,
                    "difficulty": data.difficulty.value,
                    "current_state": data.current_state.value,
                    "position": data.position,
                    "target": data.target
                } for entity_id, data in self.ai_entities.items()
            })
            
        except Exception as e:
            logger.warning(f"Ошибка обновления состояний AI системы: {e}")
    
    def _update_ai_entities(self, delta_time: float):
        """Обновление AI сущностей"""
        current_time = time.time()
        
        for entity_id, entity_data in self.ai_entities.items():
            try:
                # Проверка времени принятия решения
                if current_time - entity_data.last_decision >= entity_data.decision_cooldown:
                    # Принятие решения
                    decision = self._make_decision(entity_data)
                    if decision:
                        self._add_decision(entity_id, decision)
                        entity_data.last_decision = current_time
                
                # Обновление состояния
                self._update_entity_state(entity_data, delta_time)
                
            except Exception as e:
                logger.error(f"Ошибка обновления AI сущности {entity_id}: {e}")
    
    def _make_decision(self, entity_data: AIEntityData) -> Optional[AIDecision]:
        """Принятие решения для AI сущности"""
        try:
            # Приоритет: нейронная сеть > поведенческое дерево > правила
            if self.neural_system and self.neural_system.can_make_decision(entity_data):
                return self.neural_system.make_decision(entity_data)
            
            elif self.behavior_system:
                return self.behavior_system.make_decision(entity_data)
            
            elif self.rule_system:
                return self.rule_system.make_decision(entity_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка принятия решения для {entity_data.entity_id}: {e}")
            return None
    
    def _add_decision(self, entity_id: str, decision: AIDecision):
        """Добавление решения в очередь"""
        if entity_id not in self.ai_decisions:
            self.ai_decisions[entity_id] = []
        
        self.ai_decisions[entity_id].append(decision)
        self.stats['decisions_made'] += 1
    
    def _process_decisions(self, delta_time: float):
        """Обработка решений AI"""
        for entity_id, decisions in self.ai_decisions.items():
            # Сортируем по приоритету
            decisions.sort(key=lambda d: d.priority, reverse=True)
            
            # Выполняем решения
            for decision in decisions[:3]:  # Максимум 3 решения за раз
                if not decision.executed:
                    self._execute_decision(decision)
                    decision.executed = True
            
            # Удаляем выполненные решения
            self.ai_decisions[entity_id] = [d for d in decisions if not d.executed]
    
    def _execute_decision(self, decision: AIDecision):
        """Выполнение решения AI"""
        try:
            # Эмиссия события о решении AI
            if self.event_system:
                self.event_system.emit("ai_decision_executed", {
                    'entity_id': decision.entity_id,
                    'decision_type': decision.decision_type,
                    'target_id': decision.target_id,
                    'action_data': decision.action_data,
                    'confidence': decision.confidence
                }, "unified_ai_system")
            
            # Обучение на основе результата
            if self.learning_system:
                self.learning_system.record_decision(decision)
            
        except Exception as e:
            logger.error(f"Ошибка выполнения решения AI: {e}")
    
    def _update_subsystems(self, delta_time: float):
        """Обновление подсистем"""
        if self.behavior_system:
            self.behavior_system.update(delta_time)
        
        if self.neural_system:
            self.neural_system.update(delta_time)
        
        if self.rule_system:
            self.rule_system.update(delta_time)
        
        if self.learning_system:
            self.learning_system.update(delta_time)
    
    def _load_config(self, config: Dict[str, Any]):
        """Загрузка конфигурации"""
        try:
            if 'enable_behavior_trees' in config:
                self.config.enable_behavior_trees = config['enable_behavior_trees']
            if 'enable_neural_networks' in config:
                self.config.enable_neural_networks = config['enable_neural_networks']
            if 'enable_rule_based' in config:
                self.config.enable_rule_based = config['enable_rule_based']
            if 'enable_learning' in config:
                self.config.enable_learning = config['enable_learning']
            if 'max_ai_entities' in config:
                self.config.max_ai_entities = config['max_ai_entities']
            if 'update_frequency' in config:
                self.config.update_frequency = config['update_frequency']
            if 'learning_rate' in config:
                self.config.learning_rate = config['learning_rate']
            if 'default_behavior' in config:
                self.config.default_behavior = AIBehavior(config['default_behavior'])
            if 'default_difficulty' in config:
                self.config.default_difficulty = AIDifficulty(config['default_difficulty'])
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации AI: {e}")
    
    def _update_entity_state(self, entity_data: AIEntityData, delta_time: float):
        """Обновление состояния AI сущности"""
        try:
            # Обновление времени перезарядки решений
            if entity_data.decision_cooldown > 0:
                entity_data.decision_cooldown -= delta_time
                entity_data.decision_cooldown = max(0, entity_data.decision_cooldown)
            
            # Обновление памяти сущности
            current_time = time.time()
            memory_keys = list(entity_data.memory.keys())
            for key in memory_keys:
                memory_item = entity_data.memory[key]
                if 'expiry_time' in memory_item and current_time > memory_item['expiry_time']:
                    del entity_data.memory[key]
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояния AI сущности {entity_data.entity_id}: {e}")
    
    def _cleanup_memory(self, delta_time: float):
        """Очистка памяти"""
        current_time = time.time()
        
        # Очистка старых решений
        for entity_id in list(self.ai_decisions.keys()):
            decisions = self.ai_decisions[entity_id]
            # Удаляем решения старше 10 секунд
            self.ai_decisions[entity_id] = [
                d for d in decisions 
                if current_time - d.timestamp < 10.0
            ]
    
    # Обработчики событий
    def _on_entity_created(self, event_data: Dict[str, Any]):
        """Обработчик создания сущности"""
        entity_id = event_data.get('entity_id')
        entity_type = event_data.get('entity_type')
        
        if entity_type in ['npc', 'enemy', 'boss', 'mutant']:
            self.add_ai_entity(entity_id, entity_type, event_data)
    
    def _on_entity_destroyed(self, event_data: Dict[str, Any]):
        """Обработчик уничтожения сущности"""
        entity_id = event_data.get('entity_id')
        self.remove_ai_entity(entity_id)
    
    def _on_combat_started(self, event_data: Dict[str, Any]):
        """Обработчик начала боя"""
        # Обновляем состояние AI сущностей
        pass
    
    def _on_combat_ended(self, event_data: Dict[str, Any]):
        """Обработчик окончания боя"""
        # Обновляем состояние AI сущностей
        pass
    
    def _on_damage_dealt(self, event_data: Dict[str, Any]):
        """Обработчик нанесения урона"""
        # Обновляем память AI
        pass
    
    def _on_damage_received(self, event_data: Dict[str, Any]):
        """Обработчик получения урона"""
        # Обновляем память AI
        pass
    
    # Публичные методы
    def add_ai_entity(self, entity_id: str, entity_type: str, data: Dict[str, Any]):
        """Добавление AI сущности"""
        try:
            entity_data = AIEntityData(
                entity_id=entity_id,
                entity_type=entity_type,
                behavior=data.get('behavior', self.config.default_behavior),
                difficulty=data.get('difficulty', self.config.default_difficulty),
                current_state=AIState.IDLE,
                position=data.get('position', (0, 0, 0)),
                stats=data.get('stats', {})
            )
            
            self.ai_entities[entity_id] = entity_data
            self.stats['total_entities'] += 1
            self.stats['active_entities'] += 1
            
            logger.debug(f"Добавлена AI сущность: {entity_id} ({entity_type})")
            
        except Exception as e:
            logger.error(f"Ошибка добавления AI сущности {entity_id}: {e}")
    
    def remove_ai_entity(self, entity_id: str):
        """Удаление AI сущности"""
        if entity_id in self.ai_entities:
            del self.ai_entities[entity_id]
            self.stats['active_entities'] -= 1
            
            # Удаляем решения
            if entity_id in self.ai_decisions:
                del self.ai_decisions[entity_id]
            
            logger.debug(f"Удалена AI сущность: {entity_id}")
    
    def get_ai_entity(self, entity_id: str) -> Optional[AIEntityData]:
        """Получение AI сущности"""
        return self.ai_entities.get(entity_id)
    
    def update_entity_position(self, entity_id: str, position: tuple):
        """Обновление позиции AI сущности"""
        if entity_id in self.ai_entities:
            self.ai_entities[entity_id].position = position
    
    def set_entity_target(self, entity_id: str, target_id: str):
        """Установка цели для AI сущности"""
        if entity_id in self.ai_entities:
            self.ai_entities[entity_id].target = target_id
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Сброс статистики системы"""
        self.stats = {
            'total_entities': 0,
            'active_entities': 0,
            'decisions_made': 0,
            'learning_events': 0,
            'update_time': 0.0
        }
    
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._on_entity_created(event_data)
            elif event_type == "entity_destroyed":
                return self._on_entity_destroyed(event_data)
            elif event_type == "combat_started":
                return self._on_combat_started(event_data)
            elif event_type == "combat_ended":
                return self._on_combat_ended(event_data)
            elif event_type == "damage_dealt":
                return self._on_damage_dealt(event_data)
            elif event_type == "damage_received":
                return self._on_damage_received(event_data)
            return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'system_name': self.system_name,
            'system_state': self.system_state.value,
            'total_entities': self.stats['total_entities'],
            'active_entities': self.stats['active_entities'],
            'decisions_made': self.stats['decisions_made'],
            'update_time': self.stats['update_time']
        }
    
    def cleanup(self) -> None:
        """Очистка системы"""
        try:
            logger.info("Очистка Unified AI System...")
            
            # Очистка подсистем
            if self.behavior_system:
                self.behavior_system.cleanup()
            
            if self.neural_system:
                self.neural_system.cleanup()
            
            if self.rule_system:
                self.rule_system.cleanup()
            
            if self.learning_system:
                self.learning_system.cleanup()
            
            # Очистка данных
            self.ai_entities.clear()
            self.ai_decisions.clear()
            self.ai_groups.clear()
            self.global_memory.clear()
            self.experience_pool.clear()
            
            self.system_state = self.LifecycleState.UNINITIALIZED
            logger.info("Unified AI System очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки Unified AI System: {e}")

# Заглушки для подсистем (будут реализованы отдельно)
class BehaviorTreeSystem:
    def initialize(self): return True
    def update(self, dt): pass
    def cleanup(self): pass
    def make_decision(self, entity_data): return None

class NeuralNetworkSystem:
    def initialize(self): return True
    def update(self, dt): pass
    def cleanup(self): pass
    def can_make_decision(self, entity_data): return False
    def make_decision(self, entity_data): return None

class RuleBasedSystem:
    def initialize(self): return True
    def update(self, dt): pass
    def cleanup(self): pass
    def make_decision(self, entity_data): return None

class LearningSystem:
    def initialize(self): return True
    def update(self, dt): pass
    def cleanup(self): pass
    def record_decision(self, decision): pass
