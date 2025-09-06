#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА ПОВЕДЕНИЯ ВРАГОВ
Управление поведением врагов для препятствования игроку в поиске маяка
"""

import time
import math
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from utils.logging_system import get_logger, log_system_event

class EnemyBehaviorState(Enum):
    """Состояния поведения врага"""
    PATROL = "patrol"           # Патрулирование
    HUNT_PLAYER = "hunt_player" # Охота на игрока
    GUARD_LIGHTHOUSE = "guard_lighthouse" # Охрана маяка
    INTERCEPT = "intercept"     # Перехват игрока
    ATTACK = "attack"          # Атака игрока
    RETREAT = "retreat"        # Отступление

class EnemyBehaviorType(Enum):
    """Типы поведения врагов"""
    AGGRESSIVE = "aggressive"   # Агрессивное поведение
    DEFENSIVE = "defensive"     # Защитное поведение
    TACTICAL = "tactical"       # Тактическое поведение
    PERSISTENT = "persistent"   # Упорное поведение

@dataclass
class BehaviorPattern:
    """Паттерн поведения"""
    behavior_type: EnemyBehaviorType
    priority: int  # Приоритет поведения (1-10)
    conditions: Dict[str, Any]  # Условия активации
    actions: List[str]  # Действия для выполнения
    duration: float  # Длительность поведения
    cooldown: float  # Время перезарядки

@dataclass
class EnemyBehavior:
    """Поведение врага"""
    entity_id: str
    current_state: EnemyBehaviorState
    behavior_type: EnemyBehaviorType
    target_position: Optional[Tuple[float, float, float]] = None
    last_action_time: float = field(default_factory=time.time)
    behavior_start_time: float = field(default_factory=time.time)
    memory_patterns: List[Dict[str, Any]] = field(default_factory=list)
    learning_rate: float = 0.05

class EnemyBehaviorSystem:
    """Система поведения врагов"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Кэш поведений врагов
        self.enemy_behaviors: Dict[str, EnemyBehavior] = {}
        
        # Паттерны поведения
        self.behavior_patterns: Dict[EnemyBehaviorType, BehaviorPattern] = {}
        
        # Инициализируем паттерны поведения
        self._initialize_behavior_patterns()
        
        log_system_event("enemy_behavior_system", "initialized")
    
    def _initialize_behavior_patterns(self):
        """Инициализация паттернов поведения"""
        # Агрессивное поведение
        self.behavior_patterns[EnemyBehaviorType.AGGRESSIVE] = BehaviorPattern(
            behavior_type=EnemyBehaviorType.AGGRESSIVE,
            priority=8,
            conditions={
                "player_distance": 100.0,
                "lighthouse_distance": 200.0,
                "health_percentage": 0.5
            },
            actions=["hunt_player", "attack_player", "block_lighthouse"],
            duration=30.0,
            cooldown=10.0
        )
        
        # Защитное поведение
        self.behavior_patterns[EnemyBehaviorType.DEFENSIVE] = BehaviorPattern(
            behavior_type=EnemyBehaviorType.DEFENSIVE,
            priority=6,
            conditions={
                "lighthouse_distance": 50.0,
                "player_distance": 150.0
            },
            actions=["guard_lighthouse", "block_access", "retreat_if_low_health"],
            duration=45.0,
            cooldown=15.0
        )
        
        # Тактическое поведение
        self.behavior_patterns[EnemyBehaviorType.TACTICAL] = BehaviorPattern(
            behavior_type=EnemyBehaviorType.TACTICAL,
            priority=7,
            conditions={
                "player_distance": 80.0,
                "lighthouse_distance": 120.0,
                "ai_memory_level": 20
            },
            actions=["intercept_player", "flank_player", "coordinate_with_allies"],
            duration=25.0,
            cooldown=8.0
        )
        
        # Упорное поведение
        self.behavior_patterns[EnemyBehaviorType.PERSISTENT] = BehaviorPattern(
            behavior_type=EnemyBehaviorType.PERSISTENT,
            priority=9,
            conditions={
                "player_distance": 60.0,
                "lighthouse_distance": 100.0,
                "health_percentage": 0.3
            },
            actions=["persistent_attack", "block_lighthouse", "call_reinforcements"],
            duration=40.0,
            cooldown=5.0
        )
    
    def initialize_enemy_behavior(self, entity_id: str, enemy_type: str, 
                                 position: Tuple[float, float, float]) -> EnemyBehavior:
        """Инициализация поведения врага"""
        # Определяем тип поведения на основе типа врага
        behavior_type = self._get_behavior_type_for_enemy(enemy_type)
        
        behavior = EnemyBehavior(
            entity_id=entity_id,
            current_state=EnemyBehaviorState.PATROL,
            behavior_type=behavior_type,
            target_position=position
        )
        
        self.enemy_behaviors[entity_id] = behavior
        
        self.logger.info(f"Initialized behavior for enemy {entity_id}: {behavior_type.value}")
        return behavior
    
    def update_enemy_behavior(self, entity_id: str, enemy, player_position: Tuple[float, float, float],
                             lighthouse_position: Optional[Tuple[float, float, float]] = None) -> List[str]:
        """Обновление поведения врага"""
        if entity_id not in self.enemy_behaviors:
            return []
        
        behavior = self.enemy_behaviors[entity_id]
        current_time = time.time()
        
        # Проверяем, нужно ли сменить поведение
        if self._should_change_behavior(behavior, enemy, player_position, lighthouse_position):
            new_behavior_type = self._select_optimal_behavior(behavior, enemy, player_position, lighthouse_position)
            if new_behavior_type != behavior.behavior_type:
                behavior.behavior_type = new_behavior_type
                behavior.behavior_start_time = current_time
                behavior.current_state = self._get_initial_state_for_behavior(new_behavior_type)
        
        # Выполняем действия в соответствии с текущим поведением
        actions = self._execute_behavior_actions(behavior, enemy, player_position, lighthouse_position)
        
        # Обновляем время последнего действия
        behavior.last_action_time = current_time
        
        return actions
    
    def _get_behavior_type_for_enemy(self, enemy_type: str) -> EnemyBehaviorType:
        """Получение типа поведения для типа врага"""
        behavior_mapping = {
            "basic": EnemyBehaviorType.AGGRESSIVE,
            "boss": EnemyBehaviorType.TACTICAL,
            "chimera": EnemyBehaviorType.PERSISTENT
        }
        return behavior_mapping.get(enemy_type, EnemyBehaviorType.DEFENSIVE)
    
    def _should_change_behavior(self, behavior: EnemyBehavior, enemy, 
                               player_position: Tuple[float, float, float],
                               lighthouse_position: Optional[Tuple[float, float, float]]) -> bool:
        """Проверка необходимости смены поведения"""
        current_time = time.time()
        
        # Проверяем время текущего поведения
        behavior_duration = current_time - behavior.behavior_start_time
        pattern = self.behavior_patterns[behavior.behavior_type]
        
        if behavior_duration > pattern.duration:
            return True
        
        # Проверяем условия для смены поведения
        player_distance = self._calculate_distance(
            (enemy.x, enemy.y, enemy.z), player_position
        )
        
        lighthouse_distance = 0.0
        if lighthouse_position:
            lighthouse_distance = self._calculate_distance(
                (enemy.x, enemy.y, enemy.z), lighthouse_position
            )
        
        # Проверяем критические условия
        if player_distance < 20.0:  # Игрок очень близко
            return True
        
        if lighthouse_distance < 30.0 and player_distance < 100.0:  # Игрок близко к маяку
            return True
        
        return False
    
    def _select_optimal_behavior(self, behavior: EnemyBehavior, enemy,
                                player_position: Tuple[float, float, float],
                                lighthouse_position: Optional[Tuple[float, float, float]]) -> EnemyBehaviorType:
        """Выбор оптимального поведения"""
        player_distance = self._calculate_distance(
            (enemy.x, enemy.y, enemy.z), player_position
        )
        
        lighthouse_distance = 0.0
        if lighthouse_position:
            lighthouse_distance = self._calculate_distance(
                (enemy.x, enemy.y, enemy.z), lighthouse_position
            )
        
        # Получаем уровень здоровья врага
        health_percentage = 1.0
        if hasattr(enemy, 'health') and hasattr(enemy, 'max_health'):
            health_percentage = enemy.health / enemy.max_health if enemy.max_health > 0 else 1.0
        
        # Оцениваем каждое поведение
        behavior_scores = {}
        for behavior_type, pattern in self.behavior_patterns.items():
            score = self._evaluate_behavior_pattern(
                pattern, player_distance, lighthouse_distance, health_percentage
            )
            behavior_scores[behavior_type] = score
        
        # Выбираем поведение с наивысшим баллом
        best_behavior = max(behavior_scores.items(), key=lambda x: x[1])[0]
        
        return best_behavior
    
    def _evaluate_behavior_pattern(self, pattern: BehaviorPattern, player_distance: float,
                                  lighthouse_distance: float, health_percentage: float) -> float:
        """Оценка паттерна поведения"""
        score = pattern.priority
        
        # Модификаторы на основе условий
        conditions = pattern.conditions
        
        # Проверяем расстояние до игрока
        if "player_distance" in conditions:
            target_distance = conditions["player_distance"]
            distance_score = 1.0 - abs(player_distance - target_distance) / target_distance
            score += distance_score * 2.0
        
        # Проверяем расстояние до маяка
        if "lighthouse_distance" in conditions:
            target_distance = conditions["lighthouse_distance"]
            distance_score = 1.0 - abs(lighthouse_distance - target_distance) / target_distance
            score += distance_score * 1.5
        
        # Проверяем уровень здоровья
        if "health_percentage" in conditions:
            target_health = conditions["health_percentage"]
            health_score = 1.0 - abs(health_percentage - target_health) / target_health
            score += health_score * 1.0
        
        return score
    
    def _get_initial_state_for_behavior(self, behavior_type: EnemyBehaviorType) -> EnemyBehaviorState:
        """Получение начального состояния для типа поведения"""
        state_mapping = {
            EnemyBehaviorType.AGGRESSIVE: EnemyBehaviorState.HUNT_PLAYER,
            EnemyBehaviorType.DEFENSIVE: EnemyBehaviorState.GUARD_LIGHTHOUSE,
            EnemyBehaviorType.TACTICAL: EnemyBehaviorState.INTERCEPT,
            EnemyBehaviorType.PERSISTENT: EnemyBehaviorState.ATTACK
        }
        return state_mapping.get(behavior_type, EnemyBehaviorState.PATROL)
    
    def _execute_behavior_actions(self, behavior: EnemyBehavior, enemy,
                                 player_position: Tuple[float, float, float],
                                 lighthouse_position: Optional[Tuple[float, float, float]]) -> List[str]:
        """Выполнение действий поведения"""
        pattern = self.behavior_patterns[behavior.behavior_type]
        actions = []
        
        for action in pattern.actions:
            if self._can_execute_action(action, behavior, enemy, player_position, lighthouse_position):
                result = self._execute_action(action, behavior, enemy, player_position, lighthouse_position)
                if result:
                    actions.append(action)
        
        return actions
    
    def _can_execute_action(self, action: str, behavior: EnemyBehavior, enemy,
                           player_position: Tuple[float, float, float],
                           lighthouse_position: Optional[Tuple[float, float, float]]) -> bool:
        """Проверка возможности выполнения действия"""
        current_time = time.time()
        
        # Проверяем перезарядку
        if current_time - behavior.last_action_time < 1.0:  # Минимальная задержка между действиями
            return False
        
        # Проверяем специфические условия для каждого действия
        if action == "hunt_player":
            player_distance = self._calculate_distance(
                (enemy.x, enemy.y, enemy.z), player_position
            )
            return player_distance > 20.0
        
        elif action == "attack_player":
            player_distance = self._calculate_distance(
                (enemy.x, enemy.y, enemy.z), player_position
            )
            return player_distance <= 20.0
        
        elif action == "guard_lighthouse":
            return lighthouse_position is not None
        
        elif action == "block_lighthouse":
            if lighthouse_position:
                lighthouse_distance = self._calculate_distance(
                    (enemy.x, enemy.y, enemy.z), lighthouse_position
                )
                player_distance = self._calculate_distance(
                    (enemy.x, enemy.y, enemy.z), player_position
                )
                return lighthouse_distance < 100.0 and player_distance < 150.0
            return False
        
        return True
    
    def _execute_action(self, action: str, behavior: EnemyBehavior, enemy,
                       player_position: Tuple[float, float, float],
                       lighthouse_position: Optional[Tuple[float, float, float]]) -> bool:
        """Выполнение действия"""
        try:
            if action == "hunt_player":
                return enemy.move_to_intercept_player(player_position)
            
            elif action == "attack_player":
                return enemy.attack_player_near_lighthouse(player_position)
            
            elif action == "guard_lighthouse":
                if lighthouse_position:
                    # Движение к маяку для охраны
                    dx = lighthouse_position[0] - enemy.x
                    dy = lighthouse_position[1] - enemy.y
                    distance = (dx*dx + dy*dy) ** 0.5
                    
                    if distance > 30.0:
                        move_speed = 1.5
                        enemy.x += (dx / distance) * move_speed
                        enemy.y += (dy / distance) * move_speed
                        return True
                return False
            
            elif action == "block_lighthouse":
                return enemy.block_lighthouse_access(player_position)
            
            elif action == "intercept_player":
                return enemy.move_to_intercept_player(player_position)
            
            elif action == "flank_player":
                # Фланговый маневр
                if lighthouse_position:
                    # Вычисляем позицию для флангового маневра
                    dx = player_position[0] - lighthouse_position[0]
                    dy = player_position[1] - lighthouse_position[1]
                    distance = (dx*dx + dy*dy) ** 0.5
                    
                    if distance > 0:
                        # Перпендикулярное направление для фланга
                        flank_x = -dy / distance * 50.0
                        flank_y = dx / distance * 50.0
                        
                        target_x = player_position[0] + flank_x
                        target_y = player_position[1] + flank_y
                        
                        # Движение к фланговой позиции
                        move_speed = 1.2
                        enemy.x += (target_x - enemy.x) * move_speed * 0.1
                        enemy.y += (target_y - enemy.y) * move_speed * 0.1
                        return True
                return False
            
            elif action == "persistent_attack":
                # Упорная атака
                if hasattr(enemy, 'attack_player_near_lighthouse'):
                    return enemy.attack_player_near_lighthouse(player_position)
                return False
            
            elif action == "retreat_if_low_health":
                # Отступление при низком здоровье
                if hasattr(enemy, 'health') and hasattr(enemy, 'max_health'):
                    health_percentage = enemy.health / enemy.max_health if enemy.max_health > 0 else 1.0
                    if health_percentage < 0.3:
                        # Отступление от игрока
                        dx = enemy.x - player_position[0]
                        dy = enemy.y - player_position[1]
                        distance = (dx*dx + dy*dy) ** 0.5
                        
                        if distance > 0:
                            retreat_speed = 2.0
                            enemy.x += (dx / distance) * retreat_speed
                            enemy.y += (dy / distance) * retreat_speed
                            return True
                return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error executing action {action}: {e}")
            return False
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                           pos2: Tuple[float, float, float]) -> float:
        """Вычисление расстояния между двумя точками"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def get_enemy_behavior_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о поведении врага"""
        if entity_id not in self.enemy_behaviors:
            return None
        
        behavior = self.enemy_behaviors[entity_id]
        current_time = time.time()
        
        return {
            "entity_id": entity_id,
            "current_state": behavior.current_state.value,
            "behavior_type": behavior.behavior_type.value,
            "target_position": behavior.target_position,
            "behavior_duration": current_time - behavior.behavior_start_time,
            "time_since_last_action": current_time - behavior.last_action_time,
            "learning_rate": behavior.learning_rate,
            "memory_patterns_count": len(behavior.memory_patterns)
        }
    
    def update_behavior_learning(self, entity_id: str, success: bool, action: str):
        """Обновление обучения поведения"""
        if entity_id not in self.enemy_behaviors:
            return
        
        behavior = self.enemy_behaviors[entity_id]
        
        # Добавляем паттерн в память
        pattern = {
            "action": action,
            "success": success,
            "timestamp": time.time(),
            "behavior_type": behavior.behavior_type.value,
            "state": behavior.current_state.value
        }
        
        behavior.memory_patterns.append(pattern)
        
        # Ограничиваем размер памяти
        if len(behavior.memory_patterns) > 50:
            behavior.memory_patterns = behavior.memory_patterns[-50:]
        
        # Обновляем скорость обучения на основе успеха
        if success:
            behavior.learning_rate = min(0.1, behavior.learning_rate + 0.01)
        else:
            behavior.learning_rate = max(0.01, behavior.learning_rate - 0.005)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы поведения"""
        total_enemies = len(self.enemy_behaviors)
        
        behavior_counts = {}
        for behavior in self.enemy_behaviors.values():
            behavior_type = behavior.behavior_type.value
            behavior_counts[behavior_type] = behavior_counts.get(behavior_type, 0) + 1
        
        return {
            "total_enemies": total_enemies,
            "behavior_distribution": behavior_counts,
            "active_patterns": len(self.behavior_patterns)
        }
