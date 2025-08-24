#!/usr/bin/env python3
"""
AI System - Система искусственного интеллекта
Отвечает только за поведение и принятие решений NPC
"""

import logging
import random
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

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

class AIPersonality(Enum):
    """Типы личности AI"""
    AGGRESSIVE = "aggressive"       # Агрессивный
    DEFENSIVE = "defensive"         # Защитный
    CAUTIOUS = "cautious"          # Осторожный
    CURIOUS = "curious"            # Любопытный
    SOCIAL = "social"              # Социальный
    SOLITARY = "solitary"          # Одиночный

class ActionType(Enum):
    """Типы действий AI"""
    MOVE = "move"
    ATTACK = "attack"
    DEFEND = "defend"
    USE_ABILITY = "use_ability"
    INTERACT = "interact"
    FLEE = "flee"
    HEAL = "heal"

@dataclass
class AIDecision:
    """Решение AI"""
    action: ActionType
    target: Optional[Any] = None
    priority: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""

@dataclass
class AIPattern:
    """Паттерн поведения AI"""
    state: AIState
    duration: float = 0.0
    conditions: List[str] = None
    actions: List[ActionType] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.actions is None:
            self.actions = []

class AISystem:
    """Система искусственного интеллекта"""
    
    def __init__(self):
        self.ai_entities: Dict[str, Dict[str, Any]] = {}
        self.behavior_patterns: Dict[AIPersonality, List[AIPattern]] = {}
        self.decision_weights: Dict[str, float] = {}
        self.memory: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info("Система AI инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы AI"""
        try:
            self._setup_behavior_patterns()
            self._setup_decision_weights()
            
            logger.info("Система AI успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы AI: {e}")
            return False
    
    def _setup_behavior_patterns(self):
        """Настройка паттернов поведения"""
        self.behavior_patterns = {
            AIPersonality.AGGRESSIVE: [
                AIPattern(AIState.IDLE, 2.0, ["no_enemies"], [ActionType.MOVE]),
                AIPattern(AIState.CHASE, 5.0, ["enemy_detected"], [ActionType.MOVE, ActionType.ATTACK]),
                AIPattern(AIState.ATTACK, 3.0, ["enemy_in_range"], [ActionType.ATTACK, ActionType.USE_ABILITY])
            ],
            AIPersonality.DEFENSIVE: [
                AIPattern(AIState.IDLE, 3.0, ["no_threats"], [ActionType.MOVE]),
                AIPattern(AIState.DEFEND, 4.0, ["threat_detected"], [ActionType.DEFEND, ActionType.MOVE]),
                AIPattern(AIState.FLEE, 2.0, ["low_health"], [ActionType.FLEE, ActionType.HEAL])
            ],
            AIPersonality.CAUTIOUS: [
                AIPattern(AIState.IDLE, 4.0, ["safe_environment"], [ActionType.MOVE]),
                AIPattern(AIState.WANDER, 6.0, ["exploring"], [ActionType.MOVE, ActionType.INTERACT]),
                AIPattern(AIState.FLEE, 1.0, ["danger_detected"], [ActionType.FLEE])
            ],
            AIPersonality.CURIOUS: [
                AIPattern(AIState.WANDER, 8.0, ["exploring"], [ActionType.MOVE, ActionType.INTERACT]),
                AIPattern(AIState.SOCIAL, 5.0, ["other_entities"], [ActionType.INTERACT, ActionType.MOVE]),
                AIPattern(AIState.IDLE, 2.0, ["resting"], [ActionType.INTERACT])
            ],
            AIPersonality.SOCIAL: [
                AIPattern(AIState.SOCIAL, 10.0, ["other_entities"], [ActionType.INTERACT, ActionType.MOVE]),
                AIPattern(AIState.WANDER, 5.0, ["seeking_company"], [ActionType.MOVE, ActionType.INTERACT]),
                AIPattern(AIState.IDLE, 3.0, ["group_activity"], [ActionType.INTERACT])
            ],
            AIPersonality.SOLITARY: [
                AIPattern(AIState.IDLE, 6.0, ["alone"], [ActionType.MOVE]),
                AIPattern(AIState.WANDER, 4.0, ["exploring"], [ActionType.MOVE]),
                AIPattern(AIState.FLEE, 2.0, ["others_approaching"], [ActionType.FLEE])
            ]
        }
    
    def _setup_decision_weights(self):
        """Настройка весов для принятия решений"""
        self.decision_weights = {
            "health": 0.3,           # Здоровье
            "threat_level": 0.25,    # Уровень угрозы
            "distance_to_target": 0.2,  # Расстояние до цели
            "personality": 0.15,     # Личность
            "memory": 0.1            # Память
        }
    
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any]):
        """Регистрация сущности в системе AI"""
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
            "memory": []
        }
        
        self.ai_entities[entity_id] = ai_data
        self.memory[entity_id] = []
        
        logger.info(f"Сущность {entity_id} зарегистрирована в AI системе")
        return True
    
    def unregister_entity(self, entity_id: str):
        """Отмена регистрации сущности"""
        if entity_id in self.ai_entities:
            del self.ai_entities[entity_id]
        if entity_id in self.memory:
            del self.memory[entity_id]
        
        logger.info(f"Сущность {entity_id} удалена из AI системы")
    
    def update_entity(self, entity_id: str, entity_data: Dict[str, Any], delta_time: float):
        """Обновление AI сущности"""
        if entity_id not in self.ai_entities:
            return
        
        ai_data = self.ai_entities[entity_id]
        
        # Обновляем таймер состояния
        ai_data["state_timer"] += delta_time
        
        # Проверяем необходимость смены состояния
        if self._should_change_state(ai_data, entity_data):
            self._change_state(ai_data, entity_data)
        
        # Принимаем решение
        decision = self._make_decision(ai_data, entity_data)
        if decision:
            self._execute_decision(decision, ai_data, entity_data)
            ai_data["last_decision"] = decision
        
        # Обновляем память
        self._update_memory(ai_data, entity_data)
    
    def _should_change_state(self, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> bool:
        """Проверка необходимости смены состояния"""
        current_pattern = self._get_current_pattern(ai_data)
        if not current_pattern:
            return True
        
        # Проверяем время в текущем состоянии
        if ai_data["state_timer"] > current_pattern.duration:
            return True
        
        # Проверяем условия для смены состояния
        for condition in current_pattern.conditions:
            if not self._check_condition(condition, ai_data, entity_data):
                return True
        
        return False
    
    def _get_current_pattern(self, ai_data: Dict[str, Any]) -> Optional[AIPattern]:
        """Получение текущего паттерна поведения"""
        personality = ai_data["personality"]
        current_state = ai_data["state"]
        
        if personality in self.behavior_patterns:
            for pattern in self.behavior_patterns[personality]:
                if pattern.state == current_state:
                    return pattern
        
        return None
    
    def _check_condition(self, condition: str, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> bool:
        """Проверка условия"""
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
            return True  # Всегда можно исследовать
        elif condition == "danger_detected":
            return self._has_danger(entity_data)
        elif condition == "other_entities":
            return self._has_nearby_entities(entity_data)
        elif condition == "resting":
            return True  # Всегда можно отдыхать
        elif condition == "seeking_company":
            return not self._has_nearby_entities(entity_data)
        elif condition == "group_activity":
            return self._has_nearby_entities(entity_data)
        elif condition == "alone":
            return not self._has_nearby_entities(entity_data)
        elif condition == "others_approaching":
            return self._has_approaching_entities(entity_data)
        
        return True
    
    def _has_enemies(self, entity_data: Dict[str, Any]) -> bool:
        """Проверка наличия врагов"""
        # Простая проверка - если есть другие сущности с другим типом
        return False  # Упрощенная реализация
    
    def _has_threats(self, entity_data: Dict[str, Any]) -> bool:
        """Проверка наличия угроз"""
        return self._has_enemies(entity_data)
    
    def _enemy_in_attack_range(self, entity_data: Dict[str, Any]) -> bool:
        """Проверка врага в зоне атаки"""
        return False  # Упрощенная реализация
    
    def _is_environment_safe(self, entity_data: Dict[str, Any]) -> bool:
        """Проверка безопасности окружения"""
        return True  # Упрощенная реализация
    
    def _has_danger(self, entity_data: Dict[str, Any]) -> bool:
        """Проверка наличия опасности"""
        return self._has_threats(entity_data)
    
    def _has_nearby_entities(self, entity_data: Dict[str, Any]) -> bool:
        """Проверка наличия ближайших сущностей"""
        return False  # Упрощенная реализация
    
    def _has_approaching_entities(self, entity_data: Dict[str, Any]) -> bool:
        """Проверка приближающихся сущностей"""
        return False  # Упрощенная реализация
    
    def _change_state(self, ai_data: Dict[str, Any], entity_data: Dict[str, Any]):
        """Смена состояния AI"""
        personality = ai_data["personality"]
        old_state = ai_data["state"]
        
        # Выбираем новое состояние на основе личности
        available_patterns = self.behavior_patterns.get(personality, [])
        if available_patterns:
            # Выбираем случайный паттерн, отличный от текущего
            new_patterns = [p for p in available_patterns if p.state != old_state]
            if new_patterns:
                new_pattern = random.choice(new_patterns)
                ai_data["state"] = new_pattern.state
                ai_data["state_timer"] = 0.0
                
                logger.debug(f"AI {ai_data['id']} сменил состояние с {old_state.value} на {new_pattern.state.value}")
    
    def _make_decision(self, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> Optional[AIDecision]:
        """Принятие решения AI"""
        current_pattern = self._get_current_pattern(ai_data)
        if not current_pattern or not current_pattern.actions:
            return None
        
        # Выбираем действие на основе паттерна
        action = random.choice(current_pattern.actions)
        
        # Определяем цель действия
        target = self._select_target(action, ai_data, entity_data)
        
        # Рассчитываем приоритет и уверенность
        priority = self._calculate_priority(action, target, ai_data, entity_data)
        confidence = self._calculate_confidence(action, target, ai_data, entity_data)
        
        # Формируем рассуждение
        reasoning = self._generate_reasoning(action, target, ai_data, entity_data)
        
        return AIDecision(
            action=action,
            target=target,
            priority=priority,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _select_target(self, action: ActionType, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> Optional[Any]:
        """Выбор цели для действия"""
        if action == ActionType.ATTACK:
            # Ищем врагов для атаки
            return self._find_nearest_enemy(entity_data)
        elif action == ActionType.INTERACT:
            # Ищем сущности для взаимодействия
            return self._find_interaction_target(entity_data)
        elif action == ActionType.MOVE:
            # Генерируем случайную точку назначения
            return self._generate_move_target(entity_data)
        
        return None
    
    def _find_nearest_enemy(self, entity_data: Dict[str, Any]) -> Optional[Any]:
        """Поиск ближайшего врага"""
        # Упрощенная реализация
        return None
    
    def _find_interaction_target(self, entity_data: Dict[str, Any]) -> Optional[Any]:
        """Поиск цели для взаимодействия"""
        # Упрощенная реализация
        return None
    
    def _generate_move_target(self, entity_data: Dict[str, Any]) -> Tuple[float, float]:
        """Генерация цели для движения"""
        # Генерируем случайную точку в пределах игрового мира
        x = random.uniform(0, 1600)
        y = random.uniform(0, 900)
        return (x, y)
    
    def _calculate_priority(self, action: ActionType, target: Any, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> float:
        """Расчет приоритета действия"""
        priority = 0.0
        
        # Базовый приоритет действия
        base_priorities = {
            ActionType.ATTACK: 0.8,
            ActionType.DEFEND: 0.7,
            ActionType.FLEE: 0.9,
            ActionType.HEAL: 0.6,
            ActionType.MOVE: 0.3,
            ActionType.INTERACT: 0.4,
            ActionType.USE_ABILITY: 0.5
        }
        
        priority += base_priorities.get(action, 0.5)
        
        # Модификаторы на основе состояния
        if entity_data.get("health", 100) < entity_data.get("max_health", 100) * 0.3:
            if action == ActionType.HEAL or action == ActionType.FLEE:
                priority += 0.3
        
        # Модификаторы на основе личности
        personality_modifiers = {
            AIPersonality.AGGRESSIVE: {"attack": 0.2, "chase": 0.2},
            AIPersonality.DEFENSIVE: {"defend": 0.2, "flee": 0.2},
            AIPersonality.CAUTIOUS: {"move": 0.2, "flee": 0.2},
            AIPersonality.CURIOUS: {"interact": 0.2, "move": 0.2},
            AIPersonality.SOCIAL: {"interact": 0.3, "move": 0.1},
            AIPersonality.SOLITARY: {"move": 0.2, "flee": 0.2}
        }
        
        modifier = personality_modifiers.get(ai_data["personality"], {})
        if action.value in modifier:
            priority += modifier[action.value]
        
        return min(1.0, priority)
    
    def _calculate_confidence(self, action: ActionType, target: Any, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> float:
        """Расчет уверенности в решении"""
        confidence = 0.5  # Базовая уверенность
        
        # Модификаторы на основе опыта
        if action in ai_data.get("behavior_history", []):
            confidence += 0.2
        
        # Модификаторы на основе состояния
        if entity_data.get("health", 100) > entity_data.get("max_health", 100) * 0.7:
            confidence += 0.1
        
        # Модификаторы на основе наличия цели
        if target is not None:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, action: ActionType, target: Any, ai_data: Dict[str, Any], entity_data: Dict[str, Any]) -> str:
        """Генерация рассуждения для решения"""
        reasoning = f"Выполняю действие {action.value}"
        
        if target:
            if isinstance(target, tuple):
                reasoning += f" в направлении {target}"
            else:
                reasoning += f" на цель {target}"
        
        # Добавляем контекст
        if entity_data.get("health", 100) < entity_data.get("max_health", 100) * 0.3:
            reasoning += " (низкое здоровье)"
        
        return reasoning
    
    def _execute_decision(self, decision: AIDecision, ai_data: Dict[str, Any], entity_data: Dict[str, Any]):
        """Выполнение решения AI"""
        logger.debug(f"AI {ai_data['id']} выполняет решение: {decision.reasoning}")
        
        # Обновляем историю поведения
        if "behavior_history" not in ai_data:
            ai_data["behavior_history"] = []
        ai_data["behavior_history"].append(decision.action)
        
        # Ограничиваем историю
        if len(ai_data["behavior_history"]) > 10:
            ai_data["behavior_history"] = ai_data["behavior_history"][-10:]
    
    def _update_memory(self, ai_data: Dict[str, Any], entity_data: Dict[str, Any]):
        """Обновление памяти AI"""
        memory_entry = {
            "timestamp": ai_data.get("state_timer", 0.0),
            "state": ai_data["state"].value,
            "health": entity_data.get("health", 100),
            "position": (entity_data.get("x", 0), entity_data.get("y", 0)),
            "last_action": ai_data.get("last_decision", {}).get("action", {}).value if ai_data.get("last_decision") else None
        }
        
        self.memory[ai_data["id"]].append(memory_entry)
        
        # Ограничиваем память
        if len(self.memory[ai_data["id"]]) > 50:
            self.memory[ai_data["id"]] = self.memory[ai_data["id"]][-50:]
    
    def get_ai_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об AI сущности"""
        if entity_id not in self.ai_entities:
            return None
        
        ai_data = self.ai_entities[entity_id]
        
        return {
            "id": ai_data["id"],
            "state": ai_data["state"].value,
            "personality": ai_data["personality"].value,
            "state_timer": ai_data["state_timer"],
            "target": ai_data["target"],
            "last_decision": ai_data["last_decision"],
            "behavior_history": ai_data["behavior_history"][-5:],  # Последние 5 действий
            "memory_size": len(self.memory.get(entity_id, []))
        }
    
    def cleanup(self):
        """Очистка системы AI"""
        logger.info("Очистка системы AI...")
        self.ai_entities.clear()
        self.behavior_patterns.clear()
        self.decision_weights.clear()
        self.memory.clear()
