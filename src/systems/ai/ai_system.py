#!/usr/bin/env python3
"""Единая система искусственного интеллекта
Объединяет все AI возможности в одной системе"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
import logging
import random
import time
import math
import threading
from concurrent.futures import ThreadPoolExecutor

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ AI
class AIType(Enum):
    """Типы искусственного интеллекта"""
    BEHAVIOR_TREE = "behavior_tree"
    STATE_MACHINE = "state_machine"
    NEURAL_NETWORK = "neural_network"
    FUZZY_LOGIC = "fuzzy_logic"
    GENETIC_ALGORITHM = "genetic_algorithm"
    REINFORCEMENT_LEARNING = "reinforcement_learning"

class AIState(Enum):
    """Состояния AI"""
    IDLE = "idle"
    PATROLLING = "patrolling"
    CHASING = "chasing"
    ATTACKING = "attacking"
    FLEEING = "fleeing"
    SEARCHING = "searching"
    RESTING = "resting"
    INTERACTING = "interacting"

class AIPriority(Enum):
    """Приоритеты AI"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class AIEntity:
    """AI сущность"""
    entity_id: str
    ai_type: AIType
    current_state: AIState
    priority: AIPriority
    position: Tuple[float, float, float]
    target_position: Optional[Tuple[float, float, float]] = None
    target_entity: Optional[str] = None
    health: float = 100.0
    max_health: float = 100.0
    speed: float = 1.0
    detection_range: float = 10.0
    attack_range: float = 2.0
    memory: Dict[str, Any] = field(default_factory=dict)
    behavior_data: Dict[str, Any] = field(default_factory=dict)
    last_update: float = field(default_factory=time.time)

@dataclass
class AIBehavior:
    """Поведение AI"""
    behavior_id: str
    name: str
    description: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    priority: int = 0
    cooldown: float = 0.0
    last_execution: float = 0.0

@dataclass
class AIDecision:
    """Решение AI"""
    entity_id: str
    behavior_id: str
    action: str
    target: Optional[str] = None
    position: Optional[Tuple[float, float, float]] = None
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)

# = НАСТРОЙКИ AI
@dataclass
class AISettings:
    """Настройки AI системы"""
    update_interval: float = 0.1
    max_entities: int = 1000
    max_threads: int = 4
    enable_multithreading: bool = True
    enable_learning: bool = True
    enable_memory: bool = True
    enable_adaptation: bool = True

# = ЕДИНАЯ AI СИСТЕМА
class AISystem(BaseComponent):
    """Единая система искусственного интеллекта"""
    
    def __init__(self):
        super().__init__(
            component_id="AISystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки системы
        self.settings = AISettings()
        
        # AI сущности
        self.ai_entities: Dict[str, AIEntity] = {}
        self.entity_behaviors: Dict[str, List[AIBehavior]] = {}
        
        # Поведения и решения
        self.behaviors: Dict[str, AIBehavior] = {}
        self.decisions: List[AIDecision] = []
        
        # Память и обучение
        self.global_memory: Dict[str, Any] = {}
        self.experience_pool: Dict[str, List[Dict[str, Any]]] = {}
        self.learning_data: Dict[str, Any] = {}
        
        # Многопоточность
        self.executor: Optional[ThreadPoolExecutor] = None
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Статистика
        self.stats = {
            "total_entities": 0,
            "active_entities": 0,
            "decisions_made": 0,
            "learning_events": 0,
            "update_time": 0.0
        }
        
        # Callbacks
        self.behavior_callbacks: Dict[str, Callable] = {}
        self.decision_callbacks: List[Callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация AI системы"""
        try:
            # Инициализация поведений
            self._initialize_behaviors()
            
            # Создание пула потоков
            if self.settings.enable_multithreading:
                self.executor = ThreadPoolExecutor(max_workers=self.settings.max_threads)
            
            # Инициализация памяти
            if self.settings.enable_memory:
                self._initialize_memory()
            
            self.logger.info("AISystem инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации AISystem: {e}")
            return False
    
    def _initialize_behaviors(self):
        """Инициализация базовых поведений"""
        # Поведение патрулирования
        self.behaviors["patrol"] = AIBehavior(
            behavior_id="patrol",
            name="Патрулирование",
            description="Патрулирование территории",
            conditions={"state": AIState.IDLE, "has_target": False},
            actions=["move_to_point", "look_around"],
            priority=1
        )
        
        # Поведение преследования
        self.behaviors["chase"] = AIBehavior(
            behavior_id="chase",
            name="Преследование",
            description="Преследование цели",
            conditions={"has_target": True, "target_in_range": True},
            actions=["move_to_target", "attack"],
            priority=5
        )
        
        # Поведение атаки
        self.behaviors["attack"] = AIBehavior(
            behavior_id="attack",
            name="Атака",
            description="Атака цели",
            conditions={"target_in_attack_range": True},
            actions=["perform_attack", "use_abilities"],
            priority=10
        )
        
        # Поведение бегства
        self.behaviors["flee"] = AIBehavior(
            behavior_id="flee",
            name="Бегство",
            description="Бегство от опасности",
            conditions={"health_low": True, "threat_detected": True},
            actions=["move_away", "find_cover"],
            priority=8
        )
        
        # Поведение поиска
        self.behaviors["search"] = AIBehavior(
            behavior_id="search",
            name="Поиск",
            description="Поиск целей или предметов",
            conditions={"lost_target": True, "has_search_area": True},
            actions=["explore_area", "investigate_sounds"],
            priority=3
        )
    
    def _initialize_memory(self):
        """Инициализация памяти"""
        self.global_memory = {
            "threats": {},
            "resources": {},
            "territories": {},
            "allies": {},
            "enemies": {}
        }
    
    def register_entity(self, entity_id: str, ai_type: AIType, 
                       position: Tuple[float, float, float], **kwargs) -> bool:
        """Регистрация AI сущности"""
        try:
            if len(self.ai_entities) >= self.settings.max_entities:
                self.logger.warning(f"Достигнут лимит AI сущностей: {self.settings.max_entities}")
                return False
            
            # Создание AI сущности
            entity = AIEntity(
                entity_id=entity_id,
                ai_type=ai_type,
                current_state=AIState.IDLE,
                priority=AIPriority.NORMAL,
                position=position,
                **kwargs
            )
            
            self.ai_entities[entity_id] = entity
            self.entity_behaviors[entity_id] = []
            
            # Добавление базовых поведений
            for behavior in self.behaviors.values():
                self.entity_behaviors[entity_id].append(behavior)
            
            self.stats["total_entities"] += 1
            self.stats["active_entities"] += 1
            
            self.logger.info(f"Зарегистрирована AI сущность {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка регистрации AI сущности {entity_id}: {e}")
            return False
    
    def unregister_entity(self, entity_id: str) -> bool:
        """Удаление AI сущности"""
        try:
            if entity_id in self.ai_entities:
                del self.ai_entities[entity_id]
                if entity_id in self.entity_behaviors:
                    del self.entity_behaviors[entity_id]
                
                self.stats["active_entities"] -= 1
                self.logger.info(f"Удалена AI сущность {entity_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления AI сущности {entity_id}: {e}")
            return False
    
    def update_entity(self, entity_id: str, **kwargs) -> bool:
        """Обновление AI сущности"""
        try:
            if entity_id not in self.ai_entities:
                return False
            
            entity = self.ai_entities[entity_id]
            
            # Обновление полей
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            entity.last_update = time.time()
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления AI сущности {entity_id}: {e}")
            return False
    
    def make_decision(self, entity_id: str) -> Optional[AIDecision]:
        """Принятие решения для AI сущности"""
        try:
            if entity_id not in self.ai_entities:
                return None
            
            entity = self.ai_entities[entity_id]
            behaviors = self.entity_behaviors.get(entity_id, [])
            
            # Фильтрация доступных поведений
            available_behaviors = []
            for behavior in behaviors:
                if self._check_behavior_conditions(entity, behavior):
                    available_behaviors.append(behavior)
            
            if not available_behaviors:
                return None
            
            # Выбор поведения с наивысшим приоритетом
            best_behavior = max(available_behaviors, key=lambda b: b.priority)
            
            # Создание решения
            decision = AIDecision(
                entity_id=entity_id,
                behavior_id=best_behavior.behavior_id,
                action=best_behavior.actions[0] if best_behavior.actions else "idle",
                confidence=1.0
            )
            
            # Обновление времени выполнения
            best_behavior.last_execution = time.time()
            
            # Добавление в список решений
            self.decisions.append(decision)
            self.stats["decisions_made"] += 1
            
            # Уведомление о решении
            self._notify_decision_made(decision)
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Ошибка принятия решения для {entity_id}: {e}")
            return None
    
    def _check_behavior_conditions(self, entity: AIEntity, behavior: AIBehavior) -> bool:
        """Проверка условий поведения"""
        try:
            for condition, value in behavior.conditions.items():
                if condition == "state" and entity.current_state != value:
                    return False
                elif condition == "has_target" and bool(entity.target_entity) != value:
                    return False
                elif condition == "target_in_range" and entity.target_position:
                    distance = self._calculate_distance(entity.position, entity.target_position)
                    if distance > entity.detection_range:
                        return False
                elif condition == "target_in_attack_range" and entity.target_position:
                    distance = self._calculate_distance(entity.position, entity.target_position)
                    if distance > entity.attack_range:
                        return False
                elif condition == "health_low" and entity.health > entity.max_health * 0.3:
                    return False
                elif condition == "threat_detected":
                    # Проверка наличия угроз в памяти
                    threats = self.global_memory.get("threats", {})
                    if not threats:
                        return False
                elif condition == "lost_target" and entity.target_entity:
                    return False
                elif condition == "has_search_area":
                    # Проверка наличия области поиска
                    return True  # Упрощенная проверка
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки условий поведения: {e}")
            return False
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                          pos2: Tuple[float, float, float]) -> float:
        """Расчет расстояния между точками"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))
    
    def add_behavior_callback(self, behavior_id: str, callback: Callable):
        """Добавление callback для поведения"""
        self.behavior_callbacks[behavior_id] = callback
    
    def add_decision_callback(self, callback: Callable):
        """Добавление callback для решений"""
        self.decision_callbacks.append(callback)
    
    def _notify_decision_made(self, decision: AIDecision):
        """Уведомление о принятом решении"""
        for callback in self.decision_callbacks:
            try:
                callback(decision)
            except Exception as e:
                self.logger.error(f"Ошибка в callback решения: {e}")
    
    def get_entity_state(self, entity_id: str) -> Optional[AIEntity]:
        """Получение состояния AI сущности"""
        return self.ai_entities.get(entity_id)
    
    def get_all_entities(self) -> Dict[str, AIEntity]:
        """Получение всех AI сущностей"""
        return self.ai_entities.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики AI системы"""
        return {
            "total_entities": self.stats["total_entities"],
            "active_entities": self.stats["active_entities"],
            "decisions_made": self.stats["decisions_made"],
            "learning_events": self.stats["learning_events"],
            "update_time": self.stats["update_time"],
            "behaviors_count": len(self.behaviors),
            "memory_size": len(self.global_memory)
        }
    
    def clear_memory(self):
        """Очистка памяти"""
        self.global_memory.clear()
        self.experience_pool.clear()
        self.learning_data.clear()
        self.logger.info("Память AI системы очищена")
    
    def _on_destroy(self):
        """Уничтожение AI системы"""
        self.running = False
        
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5.0)
        
        if self.executor:
            self.executor.shutdown(wait=True)
        
        self.ai_entities.clear()
        self.entity_behaviors.clear()
        self.behaviors.clear()
        self.decisions.clear()
        self.global_memory.clear()
        self.experience_pool.clear()
        self.learning_data.clear()
        
        self.logger.info("AISystem уничтожен")
