#!/usr/bin/env python3
"""
Enhanced AI System - Улучшенная система искусственного интеллекта
Отвечает за AI-управление персонажами с обучением и памятью поколений
"""

import logging
import random
import math
import time
import json
import pickle
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class AIState(Enum):
    """Состояния AI"""
    IDLE = "idle"           # Ожидание
    WANDER = "wander"       # Блуждание
    CHASE = "chase"         # Преследование
    ATTACK = "attack"       # Атака
    FLEE = "flee"           # Бегство
    HEAL = "heal"           # Лечение
    SOCIAL = "social"       # Социальное взаимодействие
    LEARN = "learn"         # Обучение
    EXPLORE = "explore"     # Исследование
    CRAFT = "craft"         # Крафтинг
    TRADE = "trade"         # Торговля

class AIPersonality(Enum):
    """Типы личности AI"""
    AGGRESSIVE = "aggressive"       # Агрессивный
    DEFENSIVE = "defensive"         # Защитный
    CAUTIOUS = "cautious"          # Осторожный
    CURIOUS = "curious"            # Любопытный
    SOCIAL = "social"              # Социальный
    SOLITARY = "solitary"          # Одиночный
    SCHOLAR = "scholar"            # Ученый
    MERCHANT = "merchant"          # Торговец
    CRAFTSMAN = "craftsman"        # Ремесленник

class ActionType(Enum):
    """Типы действий AI"""
    MOVE = "move"
    ATTACK = "attack"
    DEFEND = "defend"
    USE_ABILITY = "use_ability"
    INTERACT = "interact"
    FLEE = "flee"
    HEAL = "heal"
    LEARN = "learn"
    CRAFT = "craft"
    TRADE = "trade"
    EXPLORE = "explore"

class LearningType(Enum):
    """Типы обучения"""
    REINFORCEMENT = "reinforcement"  # Обучение с подкреплением
    OBSERVATION = "observation"      # Обучение через наблюдение
    EXPERIMENTATION = "experimentation"  # Экспериментальное обучение
    SOCIAL = "social"                # Социальное обучение

@dataclass
class MemoryEntry:
    """Запись в памяти AI"""
    timestamp: float
    action: str
    target: Optional[str]
    result: str
    reward: float
    context: Dict[str, Any]
    success: bool
    learning_type: LearningType
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует запись в словарь для сохранения"""
        return asdict(self)

@dataclass
class AIDecision:
    """Решение AI с учетом обучения"""
    action: ActionType
    target: Optional[Any] = None
    priority: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""
    learning_factor: float = 0.0
    memory_influence: float = 0.0

@dataclass
class LearningData:
    """Данные об обучении AI"""
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    total_reward: float = 0.0
    average_reward: float = 0.0
    learning_rate: float = 0.1
    exploration_rate: float = 0.3
    last_learning_update: float = 0.0

@dataclass
class AIPattern:
    """Паттерн поведения AI с учетом обучения"""
    state: AIState
    duration: float = 0.0
    conditions: List[str] = None
    actions: List[ActionType] = None
    learning_modifiers: Dict[str, float] = None
    success_threshold: float = 0.7
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.actions is None:
            self.actions = []
        if self.learning_modifiers is None:
            self.learning_modifiers = {}

class SharedMemory:
    """Общая память для групп AI (враги, боссы)"""
    
    def __init__(self, memory_id: str, max_size: int = 1000):
        self.memory_id = memory_id
        self.max_size = max_size
        self.memories: List[MemoryEntry] = deque(maxlen=max_size)
        self.shared_knowledge: Dict[str, Any] = {}
        self.generation_data: Dict[str, Any] = {}
        
        logger.debug(f"Создана общая память: {memory_id}")
    
    def add_memory(self, entry: MemoryEntry):
        """Добавляет запись в общую память"""
        self.memories.append(entry)
        
        # Обновляем общие знания
        self._update_shared_knowledge(entry)
    
    def _update_shared_knowledge(self, entry: MemoryEntry):
        """Обновляет общие знания на основе новой записи"""
        if entry.success:
            # Успешные действия увеличивают знания
            action_key = f"successful_{entry.action}"
            if action_key not in self.shared_knowledge:
                self.shared_knowledge[action_key] = 0
            self.shared_knowledge[action_key] += 1
        
        # Обновляем статистику по типам обучения
        learning_key = f"learning_{entry.learning_type.value}"
        if learning_key not in self.shared_knowledge:
            self.shared_knowledge[learning_key] = 0
        self.shared_knowledge[learning_key] += 1
    
    def get_relevant_memories(self, action: str, context: Dict[str, Any], limit: int = 10) -> List[MemoryEntry]:
        """Получает релевантные записи памяти"""
        relevant_memories = []
        
        for memory in self.memories:
            if memory.action == action:
                # Проверяем схожесть контекста
                context_similarity = self._calculate_context_similarity(memory.context, context)
                if context_similarity > 0.5:  # Порог схожести
                    relevant_memories.append((memory, context_similarity))
        
        # Сортируем по схожести и возвращаем топ результаты
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in relevant_memories[:limit]]
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Рассчитывает схожесть контекстов"""
        if not context1 or not context2:
            return 0.0
        
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0
        
        total_similarity = 0.0
        for key in common_keys:
            if isinstance(context1[key], (int, float)) and isinstance(context2[key], (int, float)):
                # Числовые значения - нормализованная разность
                max_val = max(abs(context1[key]), abs(context2[key]))
                if max_val > 0:
                    diff = abs(context1[key] - context2[key]) / max_val
                    total_similarity += 1.0 - diff
            elif context1[key] == context2[key]:
                # Точное совпадение
                total_similarity += 1.0
        
        return total_similarity / len(common_keys)
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Получает статистику поколений"""
        return self.generation_data.copy()
    
    def update_generation_data(self, generation: int, data: Dict[str, Any]):
        """Обновляет данные поколения"""
        self.generation_data[f"generation_{generation}"] = data

class EnhancedAISystem:
    """Улучшенная система искусственного интеллекта с обучением"""
    
    def __init__(self):
        self.ai_entities: Dict[str, Dict[str, Any]] = {}
        self.behavior_patterns: Dict[AIPersonality, List[AIPattern]] = {}
        self.decision_weights: Dict[str, float] = {}
        
        # Система памяти
        self.individual_memory: Dict[str, List[MemoryEntry]] = {}
        self.shared_memories: Dict[str, SharedMemory] = {}
        
        # Система обучения
        self.learning_data: Dict[str, LearningData] = {}
        
        # Q-learning таблица
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Генерационная память
        self.generation_memory: Dict[str, List[Dict[str, Any]]] = {}
        self.current_generation: int = 1
        
        logger.info("Улучшенная система AI инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация улучшенной системы AI"""
        try:
            self._setup_behavior_patterns()
            self._setup_decision_weights()
            self._setup_shared_memories()
            
            logger.info("Улучшенная система AI успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации улучшенной системы AI: {e}")
            return False
    
    def _setup_behavior_patterns(self):
        """Настройка паттернов поведения с учетом обучения"""
        self.behavior_patterns = {
            AIPersonality.AGGRESSIVE: [
                AIPattern(AIState.IDLE, 2.0, ["no_enemies"], [ActionType.MOVE], {"exploration": 0.1}),
                AIPattern(AIState.CHASE, 5.0, ["enemy_detected"], [ActionType.MOVE, ActionType.ATTACK], {"combat": 0.3}),
                AIPattern(AIState.ATTACK, 3.0, ["enemy_in_range"], [ActionType.ATTACK, ActionType.USE_ABILITY], {"combat": 0.4}),
                AIPattern(AIState.LEARN, 2.0, ["combat_experience"], [ActionType.LEARN], {"learning": 0.2})
            ],
            AIPersonality.DEFENSIVE: [
                AIPattern(AIState.IDLE, 3.0, ["no_threats"], [ActionType.MOVE], {"exploration": 0.2}),
                AIPattern(AIState.DEFEND, 4.0, ["threat_detected"], [ActionType.DEFEND, ActionType.MOVE], {"defense": 0.3}),
                AIPattern(AIState.FLEE, 2.0, ["low_health"], [ActionType.FLEE, ActionType.HEAL], {"survival": 0.4}),
                AIPattern(AIState.LEARN, 3.0, ["defense_experience"], [ActionType.LEARN], {"learning": 0.2})
            ],
            AIPersonality.CURIOUS: [
                AIPattern(AIState.WANDER, 8.0, ["exploring"], [ActionType.MOVE, ActionType.INTERACT], {"exploration": 0.4}),
                AIPattern(AIState.LEARN, 6.0, ["new_discovery"], [ActionType.LEARN, ActionType.EXPLORE], {"learning": 0.5}),
                AIPattern(AIState.SOCIAL, 5.0, ["other_entities"], [ActionType.INTERACT, ActionType.LEARN], {"social": 0.3})
            ],
            AIPersonality.SCHOLAR: [
                AIPattern(AIState.LEARN, 10.0, ["always"], [ActionType.LEARN, ActionType.EXPLORE], {"learning": 0.6}),
                AIPattern(AIState.CRAFT, 5.0, ["materials_available"], [ActionType.CRAFT, ActionType.LEARN], {"crafting": 0.4}),
                AIPattern(AIState.SOCIAL, 3.0, ["knowledge_share"], [ActionType.INTERACT, ActionType.LEARN], {"social": 0.3})
            ]
        }
    
    def _setup_decision_weights(self):
        """Настройка весов для принятия решений с учетом обучения"""
        self.decision_weights = {
            "health": 0.25,           # Здоровье
            "threat_level": 0.2,      # Уровень угрозы
            "distance_to_target": 0.15,  # Расстояние до цели
            "personality": 0.1,       # Личность
            "memory": 0.15,           # Память
            "learning": 0.15          # Обучение
        }
    
    def _setup_shared_memories(self):
        """Настройка общих воспоминаний для групп AI"""
        # Память для врагов
        self.shared_memories["enemies"] = SharedMemory("enemies", max_size=500)
        
        # Память для боссов
        self.shared_memories["bosses"] = SharedMemory("bosses", max_size=200)
        
        # Память для NPC
        self.shared_memories["npcs"] = SharedMemory("npcs", max_size=300)
    
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any], memory_group: str = "individual"):
        """Регистрация сущности в улучшенной системе AI"""
        if entity_id in self.ai_entities:
            logger.warning(f"Сущность {entity_id} уже зарегистрирована в AI системе")
            return False
        
        # Устанавливаем базовые AI параметры
        ai_data = {
            "id": entity_id,
            "state": AIState.IDLE,
            "personality": entity_data.get("ai_personality", AIPersonality.CAUTIOUS),
            "state_timer": 0.0,
            "target": None,
            "last_decision": None,
            "behavior_history": [],
            "memory_group": memory_group,
            "learning_enabled": True,
            "exploration_rate": 0.3,
            "last_learning_update": time.time()
        }
        
        self.ai_entities[entity_id] = ai_data
        
        # Инициализируем индивидуальную память
        self.individual_memory[entity_id] = []
        
        # Инициализируем данные обучения
        self.learning_data[entity_id] = LearningData()
        
        # Инициализируем Q-таблицу
        self.q_table[entity_id] = {}
        
        logger.info(f"Сущность {entity_id} зарегистрирована в улучшенной AI системе")
        return True
    
    def unregister_entity(self, entity_id: str):
        """Отмена регистрации сущности"""
        if entity_id in self.ai_entities:
            del self.ai_entities[entity_id]
        if entity_id in self.individual_memory:
            del self.individual_memory[entity_id]
        if entity_id in self.learning_data:
            del self.learning_data[entity_id]
        if entity_id in self.q_table:
            del self.q_table[entity_id]
        
        logger.info(f"Сущность {entity_id} удалена из улучшенной AI системы")
    
    def update_entity(self, entity_id: str, entity_data: Dict[str, Any], delta_time: float):
        """Обновление AI сущности с учетом обучения"""
        if entity_id not in self.ai_entities:
            return
        
        ai_data = self.ai_entities[entity_id]
        
        # Обновляем таймер состояния
        ai_data["state_timer"] += delta_time
        
        # Проверяем необходимость смены состояния
        if self._should_change_state(ai_data, entity_data):
            self._change_state(ai_data, entity_data)
        
        # Принимаем решение с учетом обучения
        decision = self._make_enhanced_decision(ai_data, entity_data)
        if decision:
            self._execute_decision(decision, ai_data, entity_data)
            ai_data["last_decision"] = decision
        
        # Обновляем память и обучение
        self._update_memory_and_learning(ai_data, entity_data)
        
        # Периодическое обновление обучения
        if time.time() - ai_data["last_learning_update"] > 5.0:  # Каждые 5 секунд
            self._update_learning(entity_id)
            ai_data["last_learning_update"] = time.time()
    
    def _should_change_state(self, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> bool:
        """Проверка необходимости смены состояния с учетом обучения"""
        current_pattern = self._get_current_pattern(ai_data)
        if not current_pattern:
            return True
        
        # Проверяем время в текущем состоянии
        if ai_data["state_timer"] > current_pattern.duration:
            return True
        
        # Проверяем условия для смены состояния
        for condition in current_pattern.conditions:
            if not self._check_enhanced_condition(condition, ai_data, entity_data):
                return True
        
        return False
    
    def _check_enhanced_condition(self, condition: str, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> bool:
        """Проверка условий с учетом обучения и памяти"""
        if condition == "combat_experience":
            # Проверяем опыт в бою
            learning_data = self.learning_data.get(ai_data["id"])
            if learning_data:
                return learning_data.successful_actions > 5
        elif condition == "defense_experience":
            # Проверяем опыт в защите
            learning_data = self.learning_data.get(ai_data["id"])
            if learning_data:
                return learning_data.total_actions > 10
        elif condition == "new_discovery":
            # Проверяем новые открытия
            return random.random() < 0.1  # 10% шанс
        elif condition == "materials_available":
            # Проверяем доступность материалов
            return random.random() < 0.3  # 30% шанс
        elif condition == "knowledge_share":
            # Проверяем возможность обмена знаниями
            return random.random() < 0.2  # 20% шанс
        
        # Используем базовые проверки
        return self._check_basic_condition(condition, ai_data, entity_data)
    
    def _check_basic_condition(self, condition: str, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> bool:
        """Базовая проверка условий"""
        if condition == "no_enemies":
            return not self._has_enemies(entity_data)
        elif condition == "enemy_detected":
            return self._has_enemies(entity_data)
        elif condition == "enemy_in_range":
            return self._enemy_in_attack_range(entity_data)
        elif condition == "no_threats":
            return not self._has_threats(entity_data)
        elif condition == "threat_detected":
            return self._has_threats(entity_data)
        elif condition == "low_health":
            return entity_data.get("health", 100) < entity_data.get("max_health", 100) * 0.3
        elif condition == "safe_environment":
            return self._is_environment_safe(entity_data)
        elif condition == "exploring":
            return True
        elif condition == "danger_detected":
            return self._has_danger(entity_data)
        elif condition == "other_entities":
            return self._has_nearby_entities(entity_data)
        elif condition == "resting":
            return True
        elif condition == "seeking_company":
            return not self._has_nearby_entities(entity_data)
        elif condition == "group_activity":
            return self._has_nearby_entities(entity_data)
        elif condition == "alone":
            return not self._has_nearby_entities(entity_data)
        elif condition == "others_approaching":
            return self._has_approaching_entities(entity_data)
        
        return True
    
    def _make_enhanced_decision(self, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> Optional[AIDecision]:
        """Принятие решения с учетом обучения и памяти"""
        current_pattern = self._get_current_pattern(ai_data)
        if not current_pattern or not current_pattern.actions:
            return None
        
        # Получаем доступные действия
        available_actions = current_pattern.actions.copy()
        
        # Применяем модификаторы обучения
        learning_modifiers = current_pattern.learning_modifiers
        for action in available_actions:
            if action.value in learning_modifiers:
                # Увеличиваем приоритет действий с высоким модификатором обучения
                pass
        
        # Выбираем действие с учетом Q-learning
        action = self._select_action_with_q_learning(ai_data["id"], available_actions, entity_data)
        
        # Определяем цель действия
        target = self._select_enhanced_target(action, ai_data, entity_data)
        
        # Рассчитываем приоритет и уверенность с учетом обучения
        priority = self._calculate_enhanced_priority(action, target, ai_data, entity_data)
        confidence = self._calculate_enhanced_confidence(action, target, ai_data, entity_data)
        
        # Рассчитываем влияние обучения
        learning_factor = self._calculate_learning_factor(ai_data["id"], action, target)
        memory_influence = self._calculate_memory_influence(ai_data["id"], action, target)
        
        # Формируем рассуждение
        reasoning = self._generate_enhanced_reasoning(action, target, ai_data, entity_data, learning_factor, memory_influence)
        
        return AIDecision(
            action=action,
            target=target,
            priority=priority,
            confidence=confidence,
            reasoning=reasoning,
            learning_factor=learning_factor,
            memory_influence=memory_influence
        )
    
    def _select_action_with_q_learning(self, entity_id: str, available_actions: List[ActionType], entity_data: Dict[str, Any]) -> ActionType:
        """Выбирает действие с использованием Q-learning"""
        if entity_id not in self.q_table:
            self.q_table[entity_id] = {}
        
        # Создаем ключ состояния
        state_key = self._create_state_key(entity_data)
        
        if state_key not in self.q_table[entity_id]:
            self.q_table[entity_id][state_key] = {}
        
        # Инициализируем Q-значения для действий
        for action in available_actions:
            if action.value not in self.q_table[entity_id][state_key]:
                self.q_table[entity_id][state_key][action.value] = 0.0
        
        # Выбираем действие с учетом exploration/exploitation
        learning_data = self.learning_data.get(entity_id)
        if learning_data and random.random() < learning_data.exploration_rate:
            # Исследование - случайное действие
            return random.choice(available_actions)
        else:
            # Эксплуатация - лучшее действие
            best_action = max(available_actions, key=lambda a: self.q_table[entity_id][state_key].get(a.value, 0.0))
            return best_action
    
    def _create_state_key(self, entity_data: Dict[str, Any]) -> str:
        """Создает ключ состояния для Q-learning"""
        health_ratio = entity_data.get("health", 100) / entity_data.get("max_health", 100)
        health_level = "high" if health_ratio > 0.7 else "medium" if health_ratio > 0.3 else "low"
        
        # Упрощенный ключ состояния
        return f"health_{health_level}"
    
    def _select_enhanced_target(self, action: ActionType, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> Optional[Any]:
        """Выбор цели с учетом обучения и памяти"""
        if action == ActionType.ATTACK:
            # Ищем врагов для атаки с учетом опыта
            return self._find_best_target_for_attack(entity_data)
        elif action == ActionType.INTERACT:
            # Ищем сущности для взаимодействия с учетом обучения
            return self._find_best_interaction_target(entity_data)
        elif action == ActionType.LEARN:
            # Ищем лучшие источники знаний
            return self._find_best_learning_target(entity_data)
        elif action == ActionType.MOVE:
            # Генерируем точку назначения с учетом исследования
            return self._generate_enhanced_move_target(entity_data)
        
        return None
    
    def _find_best_target_for_attack(self, entity_data: Dict[str, Any]) -> Optional[Any]:
        """Находит лучшую цель для атаки с учетом опыта"""
        # Упрощенная реализация - в реальной игре здесь была бы логика поиска целей
        return None
    
    def _find_best_interaction_target(self, entity_data: Dict[str, Any]) -> Optional[Any]:
        """Находит лучшую цель для взаимодействия с учетом обучения"""
        # Упрощенная реализация
        return None
    
    def _find_best_learning_target(self, entity_data: Dict[str, Any]) -> Optional[Any]:
        """Находит лучшую цель для обучения"""
        # Упрощенная реализация
        return None
    
    def _generate_enhanced_move_target(self, entity_data: Dict[str, Any]) -> Tuple[float, float]:
        """Генерирует цель для движения с учетом исследования"""
        # Базовое случайное движение
        x = random.uniform(0, 1600)
        y = random.uniform(0, 900)
        
        # В будущем здесь можно добавить логику исследования неизвестных областей
        return (x, y)
    
    def _calculate_enhanced_priority(self, action: ActionType, target: Any, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> float:
        """Рассчитывает приоритет с учетом обучения"""
        priority = super()._calculate_priority(action, target, ai_data, entity_data)
        
        # Модификаторы на основе обучения
        learning_data = self.learning_data.get(ai_data["id"])
        if learning_data:
            # Успешные действия получают бонус к приоритету
            if learning_data.successful_actions > 10:
                priority += 0.1
            
            # Действия с высоким средним вознаграждением получают бонус
            if learning_data.average_reward > 0.5:
                priority += 0.1
        
        return min(1.0, priority)
    
    def _calculate_enhanced_confidence(self, action: ActionType, target: Any, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> float:
        """Рассчитывает уверенность с учетом обучения"""
        confidence = super()._calculate_confidence(action, target, ai_data, entity_data)
        
        # Модификаторы на основе обучения
        learning_data = self.learning_data.get(ai_data["id"])
        if learning_data:
            # Действия, которые часто успешны, получают бонус к уверенности
            if learning_data.total_actions > 0:
                success_rate = learning_data.successful_actions / learning_data.total_actions
                confidence += success_rate * 0.2
        
        return min(1.0, confidence)
    
    def _calculate_learning_factor(self, entity_id: str, action: ActionType, target: Any) -> float:
        """Рассчитывает фактор обучения для действия"""
        learning_data = self.learning_data.get(entity_id)
        if not learning_data:
            return 0.0
        
        # Базовый фактор обучения
        learning_factor = learning_data.learning_rate
        
        # Модификаторы на основе опыта
        if learning_data.total_actions > 20:
            learning_factor *= 0.8  # Снижаем скорость обучения с опытом
        elif learning_data.total_actions < 5:
            learning_factor *= 1.5  # Увеличиваем скорость обучения для новичков
        
        return min(1.0, learning_factor)
    
    def _calculate_memory_influence(self, entity_id: str, action: ActionType, target: Any) -> float:
        """Рассчитывает влияние памяти на решение"""
        # Проверяем индивидуальную память
        individual_memories = self.individual_memory.get(entity_id, [])
        relevant_individual = [m for m in individual_memories if m.action == action.value]
        
        # Проверяем общую память
        shared_memory = None
        for memory in self.shared_memories.values():
            relevant_shared = memory.get_relevant_memories(action.value, {})
            if relevant_shared:
                shared_memory = memory
                break
        
        # Рассчитываем влияние
        individual_influence = len(relevant_individual) * 0.1
        shared_influence = len(relevant_shared) * 0.05 if shared_memory else 0.0
        
        return min(1.0, individual_influence + shared_influence)
    
    def _generate_enhanced_reasoning(self, action: ActionType, target: Any, ai_data: Dict[str, Any], entity_data: Dict[str, Any], learning_factor: float, memory_influence: float) -> str:
        """Генерирует расширенное рассуждение для решения"""
        reasoning = f"Выполняю действие {action.value}"
        
        if target:
            if isinstance(target, tuple):
                reasoning += f" в направлении {target}"
            else:
                reasoning += f" на цель {target}"
        
        # Добавляем контекст обучения
        if learning_factor > 0.5:
            reasoning += " (высокий фактор обучения)"
        elif learning_factor < 0.2:
            reasoning += " (низкий фактор обучения)"
        
        # Добавляем контекст памяти
        if memory_influence > 0.3:
            reasoning += " (сильное влияние памяти)"
        
        # Добавляем контекст состояния
        if entity_data.get("health", 100) < entity_data.get("max_health", 100) * 0.3:
            reasoning += " (низкое здоровье)"
        
        return reasoning
    
    def _execute_decision(self, decision: AIDecision, ai_data: Dict[str, Any], entity_data: Dict[str, Any]):
        """Выполнение решения AI с учетом обучения"""
        logger.debug(f"AI {ai_data['id']} выполняет решение: {decision.reasoning}")
        
        # Обновляем историю поведения
        if "behavior_history" not in ai_data:
            ai_data["behavior_history"] = []
        ai_data["behavior_history"].append(decision.action)
        
        # Ограничиваем историю
        if len(ai_data["behavior_history"]) > 10:
            ai_data["behavior_history"] = ai_data["behavior_history"][-10:]
    
    def _update_memory_and_learning(self, ai_data: Dict[str, Any], entity_data: Dict[str, Any]):
        """Обновляет память и обучение AI"""
        entity_id = ai_data["id"]
        
        # Создаем запись памяти
        memory_entry = MemoryEntry(
            timestamp=ai_data.get("state_timer", 0.0),
            action=ai_data.get("last_decision", {}).get("action", {}).value if ai_data.get("last_decision") else "unknown",
            target=str(ai_data.get("target", "none")),
            result="success",  # Упрощенно
            reward=0.5,  # Базовое вознаграждение
            context={
                "health": entity_data.get("health", 100),
                "position": (entity_data.get("x", 0), entity_data.get("y", 0)),
                "state": ai_data["state"].value
            },
            success=True,  # Упрощенно
            learning_type=LearningType.REINFORCEMENT
        )
        
        # Добавляем в индивидуальную память
        if entity_id in self.individual_memory:
            self.individual_memory[entity_id].append(memory_entry)
            
            # Ограничиваем память
            if len(self.individual_memory[entity_id]) > 100:
                self.individual_memory[entity_id] = self.individual_memory[entity_id][-100:]
        
        # Добавляем в общую память, если это группа
        memory_group = ai_data.get("memory_group", "individual")
        if memory_group in self.shared_memories:
            self.shared_memories[memory_group].add_memory(memory_entry)
    
    def _update_learning(self, entity_id: str):
        """Обновляет параметры обучения AI"""
        if entity_id not in self.learning_data:
            return
        
        learning_data = self.learning_data[entity_id]
        
        # Обновляем среднее вознаграждение
        if learning_data.total_actions > 0:
            learning_data.average_reward = learning_data.total_reward / learning_data.total_actions
        
        # Адаптируем скорость обучения
        if learning_data.total_actions > 50:
            learning_data.learning_rate = max(0.01, learning_data.learning_rate * 0.99)
        
        # Адаптируем скорость исследования
        if learning_data.successful_actions > 20:
            learning_data.exploration_rate = max(0.1, learning_data.exploration_rate * 0.95)
    
    def record_action_result(self, entity_id: str, action: str, success: bool, reward: float, context: Dict[str, Any]):
        """Записывает результат действия для обучения"""
        if entity_id not in self.learning_data:
            return
        
        learning_data = self.learning_data[entity_id]
        
        # Обновляем статистику
        learning_data.total_actions += 1
        if success:
            learning_data.successful_actions += 1
        else:
            learning_data.failed_actions += 1
        
        learning_data.total_reward += reward
        
        # Обновляем Q-таблицу
        self._update_q_table(entity_id, action, reward, context)
        
        # Создаем запись памяти
        memory_entry = MemoryEntry(
            timestamp=time.time(),
            action=action,
            target=context.get("target", "unknown"),
            result="success" if success else "failure",
            reward=reward,
            context=context,
            success=success,
            learning_type=LearningType.REINFORCEMENT
        )
        
        # Добавляем в память
        if entity_id in self.individual_memory:
            self.individual_memory[entity_id].append(memory_entry)
    
    def _update_q_table(self, entity_id: str, action: str, reward: float, context: Dict[str, Any]):
        """Обновляет Q-таблицу для Q-learning"""
        if entity_id not in self.q_table:
            self.q_table[entity_id] = {}
        
        state_key = self._create_state_key(context)
        if state_key not in self.q_table[entity_id]:
            self.q_table[entity_id][state_key] = {}
        
        if action not in self.q_table[entity_id][state_key]:
            self.q_table[entity_id][state_key][action] = 0.0
        
        # Простое обновление Q-значения
        learning_data = self.learning_data.get(entity_id)
        if learning_data:
            alpha = learning_data.learning_rate
            current_q = self.q_table[entity_id][state_key][action]
            self.q_table[entity_id][state_key][action] = current_q + alpha * (reward - current_q)
    
    def save_generation_memory(self, save_id: str):
        """Сохраняет память поколений"""
        generation_data = {
            "generation": self.current_generation,
            "timestamp": time.time(),
            "ai_entities": len(self.ai_entities),
            "total_memories": sum(len(memories) for memories in self.individual_memory.values()),
            "shared_memories": {name: len(memory.memories) for name, memory in self.shared_memories.items()},
            "learning_stats": {entity_id: asdict(data) for entity_id, data in self.learning_data.items()}
        }
        
        if save_id not in self.generation_memory:
            self.generation_memory[save_id] = []
        
        self.generation_memory[save_id].append(generation_data)
        
        # Обновляем данные в общих воспоминаниях
        for memory_name, shared_memory in self.shared_memories.items():
            shared_memory.update_generation_data(self.current_generation, generation_data)
        
        logger.info(f"Память поколения {self.current_generation} сохранена для {save_id}")
    
    def load_generation_memory(self, save_id: str):
        """Загружает память поколений"""
        if save_id in self.generation_memory:
            generations = self.generation_memory[save_id]
            if generations:
                latest_generation = max(generations, key=lambda g: g["generation"])
                self.current_generation = latest_generation["generation"] + 1
                
                logger.info(f"Память поколений загружена для {save_id}, текущее поколение: {self.current_generation}")
                return True
        
        return False
    
    def get_ai_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получает расширенную информацию об AI сущности"""
        if entity_id not in self.ai_entities:
            return None
        
        ai_data = self.ai_entities[entity_id]
        learning_data = self.learning_data.get(entity_id)
        
        info = {
            "id": ai_data["id"],
            "state": ai_data["state"].value,
            "personality": ai_data["personality"].value,
            "state_timer": ai_data["state_timer"],
            "target": ai_data["target"],
            "last_decision": ai_data["last_decision"],
            "behavior_history": ai_data["behavior_history"][-5:],
            "memory_size": len(self.individual_memory.get(entity_id, [])),
            "learning_enabled": ai_data.get("learning_enabled", False),
            "exploration_rate": ai_data.get("exploration_rate", 0.0)
        }
        
        if learning_data:
            info.update({
                "total_actions": learning_data.total_actions,
                "successful_actions": learning_data.successful_actions,
                "success_rate": learning_data.successful_actions / learning_data.total_actions if learning_data.total_actions > 0 else 0.0,
                "average_reward": learning_data.average_reward,
                "learning_rate": learning_data.learning_rate
            })
        
        return info
    
    def cleanup(self):
        """Очистка улучшенной системы AI"""
        logger.info("Очистка улучшенной системы AI...")
        self.ai_entities.clear()
        self.behavior_patterns.clear()
        self.decision_weights.clear()
        self.individual_memory.clear()
        self.shared_memories.clear()
        self.learning_data.clear()
        self.q_table.clear()
        self.generation_memory.clear()
