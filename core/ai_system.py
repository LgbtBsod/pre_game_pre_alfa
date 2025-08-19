"""
Система обучения ИИ с Q-learning и адаптивным поведением.
Управляет поведением NPC и их адаптацией к стилю игры игрока.
"""

import random
import math
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Типы действий ИИ"""
    MOVE = "move"
    ATTACK = "attack"
    DEFEND = "defend"
    HEAL = "heal"
    RETREAT = "retreat"
    EXPLORE = "explore"
    INTERACT = "interact"
    WAIT = "wait"


class AIState(Enum):
    """Состояния ИИ"""
    IDLE = "idle"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    CAUTIOUS = "cautious"
    EXPLORATIVE = "explorative"
    SOCIAL = "social"


@dataclass
class AIAction:
    """Действие ИИ"""
    action_type: str
    target: Optional[str] = None
    priority: float = 1.0
    cooldown: float = 0.0
    last_used: float = 0.0
    
    def can_use(self, current_time: float) -> bool:
        """Проверка возможности использования действия"""
        return current_time - self.last_used >= self.cooldown


@dataclass
class AIPersonality:
    """Личность ИИ"""
    aggression: float = 0.5      # Агрессивность (0.0 - 1.0)
    curiosity: float = 0.5       # Любопытство (0.0 - 1.0)
    caution: float = 0.5         # Осторожность (0.0 - 1.0)
    social: float = 0.5          # Социальность (0.0 - 1.0)
    adaptability: float = 0.5    # Адаптивность (0.0 - 1.0)
    
    def get_behavior_tendency(self) -> str:
        """Получение тенденции поведения"""
        if self.aggression > 0.7:
            return "aggressive"
        elif self.caution > 0.7:
            return "defensive"
        elif self.curiosity > 0.7:
            return "explorative"
        elif self.social > 0.7:
            return "social"
        else:
            return "balanced"


class QLearningAgent:
    """Агент Q-learning для обучения ИИ"""
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.1, 
                 discount_factor: float = 0.95, epsilon: float = 0.1):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q-таблица
        self.q_table = np.zeros((state_size, action_size))
        
        # История обучения
        self.learning_history: List[Dict[str, Any]] = []
        
        # Адаптивные параметры
        self.adaptive_learning_rate = learning_rate
        self.adaptive_epsilon = epsilon
    
    def choose_action(self, state: int, available_actions: List[int]) -> int:
        """Выбор действия с использованием ε-greedy стратегии"""
        if random.random() < self.adaptive_epsilon:
            # Случайное действие (исследование)
            return random.choice(available_actions)
        else:
            # Жадное действие (эксплуатация)
            q_values = [self.q_table[state][action] for action in available_actions]
            max_q = max(q_values)
            best_actions = [action for action, q in zip(available_actions, q_values) if q == max_q]
            return random.choice(best_actions)
    
    def update_q_value(self, state: int, action: int, reward: float, next_state: int):
        """Обновление Q-значения"""
        current_q = self.q_table[state][action]
        max_next_q = np.max(self.q_table[next_state])
        
        # Q-learning формула
        new_q = current_q + self.adaptive_learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
        
        # Запись в историю обучения
        self.learning_history.append({
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state,
            "old_q": current_q,
            "new_q": new_q,
            "timestamp": 0.0  # Здесь будет время игры
        })
    
    def adapt_to_performance(self, performance_metric: float):
        """Адаптация параметров обучения на основе производительности"""
        if performance_metric > 0.7:  # Хорошая производительность
            # Уменьшаем исследование, увеличиваем эксплуатацию
            self.adaptive_epsilon = max(0.05, self.adaptive_epsilon * 0.95)
            self.adaptive_learning_rate = min(0.2, self.adaptive_learning_rate * 1.05)
        elif performance_metric < 0.3:  # Плохая производительность
            # Увеличиваем исследование, уменьшаем эксплуатацию
            self.adaptive_epsilon = min(0.3, self.adaptive_epsilon * 1.05)
            self.adaptive_learning_rate = max(0.05, self.adaptive_learning_rate * 0.95)
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Получение статистики обучения"""
        if not self.learning_history:
            return {"total_updates": 0, "avg_reward": 0.0}
        
        total_updates = len(self.learning_history)
        avg_reward = sum(update["reward"] for update in self.learning_history) / total_updates
        
        return {
            "total_updates": total_updates,
            "avg_reward": avg_reward,
            "learning_rate": self.adaptive_learning_rate,
            "epsilon": self.adaptive_epsilon
        }
    
    def save_q_table(self, filepath: str) -> bool:
        """Сохранение Q-таблицы"""
        try:
            np.save(filepath, self.q_table)
            logger.info(f"Q-таблица сохранена в {filepath}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения Q-таблицы: {e}")
            return False
    
    def load_q_table(self, filepath: str) -> bool:
        """Загрузка Q-таблицы"""
        try:
            self.q_table = np.load(filepath)
            logger.info(f"Q-таблица загружена из {filepath}")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки Q-таблицы: {e}")
            return False


class AdaptiveAISystem:
    """Адаптивная система ИИ"""
    
    def __init__(self, entity_id: str, effect_db=None):
        self.entity_id = entity_id
        self.effect_db = effect_db
        
        # Состояние ИИ
        self.current_state = AIState.IDLE.value
        self.target_entity = None
        self.path_to_target = []
        self.last_action_time = 0.0
        
        # Личность ИИ
        self.personality = AIPersonality()
        
        # Q-learning агент
        self.q_agent = QLearningAgent(
            state_size=100,  # Размер пространства состояний
            action_size=len(ActionType)
        )
        
        # Доступные действия
        self.available_actions = self._init_actions()
        
        # Память и опыт
        self.memory: Dict[str, Any] = {}
        self.experience_points = 0
        self.level = 1
        self.learning_level = 1  # Уровень обучения ИИ
        self.learning_history = []  # История обучения
        
        # Адаптация к игроку
        self.player_adaptation: Dict[str, float] = {}
        self.player_patterns: Dict[str, int] = {}
        
        # Экологическое обучение
        self.ecological_knowledge: Dict[str, float] = {}
        self.species_interactions: Dict[str, List[str]] = {}
        
        # Инициализация
        self._init_ecological_knowledge()
    
    def _init_actions(self) -> List[AIAction]:
        """Инициализация доступных действий"""
        return [
            AIAction(ActionType.MOVE.value, priority=1.0, cooldown=0.1),
            AIAction(ActionType.ATTACK.value, priority=2.0, cooldown=1.0),
            AIAction(ActionType.DEFEND.value, priority=1.5, cooldown=0.5),
            AIAction(ActionType.HEAL.value, priority=3.0, cooldown=5.0),
            AIAction(ActionType.RETREAT.value, priority=2.5, cooldown=2.0),
            AIAction(ActionType.EXPLORE.value, priority=0.8, cooldown=0.2),
            AIAction(ActionType.INTERACT.value, priority=1.2, cooldown=1.5),
            AIAction(ActionType.WAIT.value, priority=0.5, cooldown=0.0)
        ]
    
    def _init_ecological_knowledge(self):
        """Инициализация экологических знаний"""
        # Базовые знания о видах
        self.ecological_knowledge = {
            "predator": 0.5,
            "prey": 0.5,
            "neutral": 0.5,
            "dangerous": 0.3,
            "safe": 0.7
        }
        
        # Взаимодействия между видами
        self.species_interactions = {
            "predator": ["prey", "neutral"],
            "prey": ["predator"],
            "neutral": ["predator", "prey"],
            "dangerous": ["all"],
            "safe": ["neutral", "prey"]
        }
    
    def update(self, entity, world, delta_time: float):
        """Обновление ИИ системы"""
        try:
            # Получение текущего состояния
            current_state = self._get_current_state(entity, world)
            
            # Выбор действия
            action = self._choose_action(current_state, delta_time)
            
            # Выполнение действия
            reward = self._execute_action(entity, action, world)
            
            # Получение следующего состояния
            next_state = self._get_current_state(entity, world)
            
            # Обновление Q-таблицы
            self._update_learning(current_state, action, reward, next_state)
            
            # Адаптация к стилю игрока
            self._adapt_to_player(world.player if hasattr(world, 'player') else None)
            
            # Обновление экологических знаний
            self._update_ecological_knowledge(world)
            
            # Обновление времени
            self.last_action_time += delta_time
            
            # Обновление уровня обучения
            self._update_learning_level()
            
        except Exception as e:
            logger.error(f"Ошибка обновления ИИ системы: {e}")
    
    def _get_current_state(self, entity, world) -> int:
        """Получение текущего состояния для Q-learning"""
        # Упрощённое представление состояния
        state_features = []
        
        # Здоровье
        health_percent = getattr(entity, 'health', 100) / getattr(entity, 'max_health', 100)
        state_features.append(int(health_percent * 10))
        
        # Расстояние до ближайшего врага
        nearest_enemy_distance = self._get_nearest_enemy_distance(entity, world)
        state_features.append(min(9, int(nearest_enemy_distance / 10)))
        
        # Количество врагов поблизости
        nearby_enemies = self._count_nearby_enemies(entity, world)
        state_features.append(min(9, nearby_enemies))
        
        # Эмоциональное состояние
        emotional_state = getattr(entity, 'emotional_state', 'neutral')
        emotion_mapping = {'fear': 0, 'calm': 5, 'aggressive': 9}
        state_features.append(emotion_mapping.get(emotional_state, 5))
        
        # Преобразование в числовое состояние
        state = sum(feature * (10 ** i) for i, feature in enumerate(state_features))
        return state % 100  # Ограничение размера состояния
    
    def _get_nearest_enemy_distance(self, entity, world) -> float:
        """Получение расстояния до ближайшего врага"""
        try:
            if not hasattr(world, 'entities'):
                return 100.0
            
            min_distance = float('inf')
            for other_entity in world.entities:
                if other_entity != entity and hasattr(other_entity, 'position'):
                    distance = self._calculate_distance(entity.position, other_entity.position)
                    min_distance = min(min_distance, distance)
            
            return min_distance if min_distance != float('inf') else 100.0
        except:
            return 100.0
    
    def _count_nearby_enemies(self, entity, world) -> int:
        """Подсчёт врагов поблизости"""
        try:
            if not hasattr(world, 'entities'):
                return 0
            
            nearby_count = 0
            for other_entity in world.entities:
                if other_entity != entity and hasattr(other_entity, 'position'):
                    distance = self._calculate_distance(entity.position, other_entity.position)
                    if distance < 50:  # Радиус 50 единиц
                        nearby_count += 1
            
            return nearby_count
        except:
            return 0
    
    def _calculate_distance(self, pos1, pos2) -> float:
        """Расчёт расстояния между позициями"""
        try:
            # Проверяем, является ли позиция EntityPosition или tuple/list
            if hasattr(pos1, 'x') and hasattr(pos1, 'y'):
                # EntityPosition dataclass
                x1, y1 = pos1.x, pos1.y
            else:
                # tuple/list
                x1, y1 = pos1[0], pos1[1]
            
            if hasattr(pos2, 'x') and hasattr(pos2, 'y'):
                # EntityPosition dataclass
                x2, y2 = pos2.x, pos2.y
            else:
                # tuple/list
                x2, y2 = pos2[0], pos2[1]
            
            return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        except Exception as e:
            logger.error(f"Ошибка расчета расстояния: {e}")
            return 100.0
    
    def _choose_action(self, current_state: int, delta_time: float) -> AIAction:
        """Выбор действия"""
        # Фильтрация доступных действий по времени
        available_actions = [
            action for action in self.available_actions 
            if action.can_use(self.last_action_time)
        ]
        
        if not available_actions:
            return AIAction(ActionType.WAIT.value)
        
        # Получение индексов доступных действий
        action_indices = [i for i, action in enumerate(self.available_actions) 
                         if action in available_actions]
        
        # Выбор действия через Q-learning
        chosen_index = self.q_agent.choose_action(current_state, action_indices)
        chosen_action = self.available_actions[chosen_index]
        
        # Обновление времени последнего использования
        chosen_action.last_used = self.last_action_time
        
        return chosen_action
    
    def _execute_action(self, entity, action: AIAction, world) -> float:
        """Выполнение действия ИИ"""
        try:
            reward = 0.0
            current_time = self.last_action_time
            
            if not action.can_use(current_time):
                return 0.0
            
            if action.action_type == ActionType.MOVE.value:
                reward = self._execute_movement(entity, world)
            elif action.action_type == ActionType.ATTACK.value:
                reward = self._execute_attack(entity, world)
            elif action.action_type == ActionType.DEFEND.value:
                reward = self._execute_defend(entity, world)
            elif action.action_type == ActionType.HEAL.value:
                reward = self._execute_heal(entity, world)
            elif action.action_type == ActionType.RETREAT.value:
                reward = self._execute_retreat(entity, world)
            elif action.action_type == ActionType.EXPLORE.value:
                reward = self._execute_explore(entity, world)
            elif action.action_type == ActionType.INTERACT.value:
                reward = self._execute_interact(entity, world)
            elif action.action_type == ActionType.WAIT.value:
                reward = self._execute_wait(entity, world)
            
            # Обновление времени последнего использования
            action.last_used = current_time
            
            return reward
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия ИИ: {e}")
            return 0.0
    
    def get_autonomous_movement(self, entity, world) -> Tuple[float, float]:
        """Получение автономного движения для сущности"""
        try:
            # Проверка навигации к маяку (только если маяк уже обнаружен)
            if hasattr(world, 'beacon_system') and hasattr(entity, 'position'):
                # Проверяем, есть ли обнаруженные маяки
                discovered_beacons = [b for b in world.beacon_system.beacons.values() if b.discovered]
                
                if discovered_beacons and world.beacon_system.active_target:
                    beacon_direction = world.beacon_system.get_navigation_direction(
                        (entity.position.x, entity.position.y, entity.position.z)
                    )
                    if beacon_direction:
                        # Движение к маяку с небольшой случайностью для естественности
                        dx, dy = beacon_direction
                        dx += random.uniform(-0.1, 0.1)
                        dy += random.uniform(-0.1, 0.1)
                        
                        # Ограничение скорости движения
                        speed = getattr(entity.stats, 'speed', 1.0) if hasattr(entity, 'stats') else 1.0
                        return dx * speed, dy * speed
            
            # Анализ окружения (стандартное поведение)
            nearest_enemy = self._get_nearest_enemy(entity, world)
            nearest_item = self._get_nearest_item(entity, world)
            nearest_obstacle = self._get_nearest_obstacle(entity, world)
            
            # Определение направления движения на основе личности и состояния
            dx, dy = 0.0, 0.0
            
            if self.personality.aggression > 0.7 and nearest_enemy:
                # Агрессивное поведение - движение к врагу
                dx, dy = self._calculate_direction_to_target(entity, nearest_enemy)
            elif self.personality.curiosity > 0.7 and nearest_item:
                # Любопытное поведение - движение к предмету
                dx, dy = self._calculate_direction_to_target(entity, nearest_item)
            elif self.personality.caution > 0.7 and nearest_enemy:
                # Осторожное поведение - движение от врага
                dx, dy = self._calculate_direction_away_from_target(entity, nearest_enemy)
            else:
                # Случайное исследование - гарантируем движение
                dx, dy = self._get_random_movement_direction()
                
                # Если движение слишком слабое, усиливаем его
                if abs(dx) < 0.3 and abs(dy) < 0.3:
                    dx *= 2.0
                    dy *= 2.0
            
            # Избегание препятствий
            if nearest_obstacle and self._is_collision_imminent(entity, nearest_obstacle, dx, dy):
                dx, dy = self._calculate_avoidance_direction(entity, nearest_obstacle, dx, dy)
            
            # Ограничение скорости движения
            speed = getattr(entity.stats, 'speed', 1.0) if hasattr(entity, 'stats') else 1.0
            dx *= speed
            dy *= speed
            
            # Гарантируем минимальное движение для предотвращения "застревания"
            min_movement = 0.5
            if abs(dx) < min_movement and abs(dy) < min_movement:
                # Если движение слишком слабое, добавляем случайное направление
                angle = random.uniform(0, 2 * math.pi)
                dx += math.cos(angle) * min_movement
                dy += math.sin(angle) * min_movement
            
            return dx, dy
            
        except Exception as e:
            logger.error(f"Ошибка получения автономного движения: {e}")
            # Возвращаем случайное движение в случае ошибки
            return random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)
    
    def _get_nearest_enemy(self, entity, world) -> Optional[Any]:
        """Получение ближайшего врага"""
        try:
            if not hasattr(world, 'entities') or not world.entities:
                return None
            
            nearest_enemy = None
            min_distance = float('inf')
            
            for other_entity in world.entities:
                if other_entity != entity and hasattr(other_entity, 'type') and other_entity.type == 'enemy':
                    distance = self._calculate_distance(entity, other_entity)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_enemy = other_entity
            
            return nearest_enemy
        except Exception as e:
            logger.error(f"Ошибка поиска ближайшего врага: {e}")
            return None
    
    def _get_nearest_item(self, entity, world) -> Optional[Any]:
        """Получение ближайшего предмета"""
        try:
            if not hasattr(world, 'items') or not world.items:
                return None
            
            nearest_item = None
            min_distance = float('inf')
            
            for item in world.items:
                distance = self._calculate_distance(entity, item)
                if distance < min_distance:
                    min_distance = distance
                    nearest_item = item
            
            return nearest_item
        except Exception as e:
            logger.error(f"Ошибка поиска ближайшего предмета: {e}")
            return None
    
    def _get_nearest_obstacle(self, entity, world) -> Optional[Any]:
        """Получение ближайшего препятствия"""
        try:
            if not hasattr(world, 'obstacles') or not world.obstacles:
                return None
            
            nearest_obstacle = None
            min_distance = float('inf')
            
            for obstacle in world.obstacles:
                distance = self._calculate_distance(entity, obstacle)
                if distance < min_distance:
                    min_distance = distance
                    nearest_obstacle = obstacle
            
            return nearest_obstacle
        except Exception as e:
            logger.error(f"Ошибка поиска ближайшего препятствия: {e}")
            return None
    
    def _calculate_direction_to_target(self, entity, target) -> Tuple[float, float]:
        """Расчет направления к цели"""
        try:
            if not hasattr(entity, 'position') or not hasattr(target, 'position'):
                return 0.0, 0.0
            
            dx = target.position.x - entity.position.x
            dy = target.position.y - entity.position.y
            
            # Нормализация вектора
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length
            
            return dx, dy
        except Exception as e:
            logger.error(f"Ошибка расчета направления к цели: {e}")
            return 0.0, 0.0
    
    def _calculate_direction_away_from_target(self, entity, target) -> Tuple[float, float]:
        """Расчет направления от цели"""
        try:
            dx, dy = self._calculate_direction_to_target(entity, target)
            return -dx, -dy
        except Exception as e:
            logger.error(f"Ошибка расчета направления от цели: {e}")
            return 0.0, 0.0
    
    def _get_random_movement_direction(self) -> Tuple[float, float]:
        """Получение случайного направления движения"""
        try:
            angle = random.uniform(0, 2 * math.pi)
            dx = math.cos(angle)
            dy = math.sin(angle)
            return dx, dy
        except Exception as e:
            logger.error(f"Ошибка получения случайного направления: {e}")
            return 0.0, 0.0
    
    def _is_collision_imminent(self, entity, obstacle, dx, dy) -> bool:
        """Проверка приближающейся коллизии"""
        try:
            if not hasattr(entity, 'position') or not hasattr(obstacle, 'position'):
                return False
            
            # Простая проверка расстояния
            distance = self._calculate_distance(entity, obstacle)
            return distance < 50  # Порог коллизии
        except Exception as e:
            logger.error(f"Ошибка проверки коллизии: {e}")
            return False
    
    def _calculate_avoidance_direction(self, entity, obstacle, current_dx, current_dy) -> Tuple[float, float]:
        """Расчет направления избегания препятствия"""
        try:
            # Перпендикулярное направление
            avoid_dx = -current_dy
            avoid_dy = current_dx
            
            # Нормализация
            length = math.sqrt(avoid_dx * avoid_dx + avoid_dy * avoid_dy)
            if length > 0:
                avoid_dx /= length
                avoid_dy /= length
            
            return avoid_dx, avoid_dy
        except Exception as e:
            logger.error(f"Ошибка расчета направления избегания: {e}")
            return current_dx, current_dy
    
    def _calculate_distance(self, entity1, entity2) -> float:
        """Расчет расстояния между сущностями"""
        try:
            if not hasattr(entity1, 'position') or not hasattr(entity2, 'position'):
                return float('inf')
            
            dx = entity1.position[0] - entity2.position[0]
            dy = entity1.position[1] - entity2.position[1]
            return math.sqrt(dx * dx + dy * dy)
        except Exception as e:
            logger.error(f"Ошибка расчета расстояния: {e}")
            return float('inf')
    
    def _execute_movement(self, entity, world) -> float:
        """Выполнение движения"""
        try:
            # Получение автономного движения
            dx, dy = self.get_autonomous_movement(entity, world)
            
            # Применение движения к сущности
            if hasattr(entity, 'move_pygame'):
                entity.move_pygame(dx, dy)
                return 1.0  # Положительная награда за движение
            else:
                # Альтернативный способ движения
                if hasattr(entity, 'position'):
                    entity.position = (
                        entity.position[0] + dx,
                        entity.position[1] + dy,
                        entity.position[2]
                    )
                    return 1.0
            
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка выполнения движения: {e}")
            return 0.0
    
    def _execute_attack(self, entity, world) -> float:
        """Выполнение атаки"""
        try:
            # Поиск ближайшего врага
            nearest_enemy = self._get_nearest_enemy(entity, world)
            if nearest_enemy:
                # Простая атака
                if hasattr(nearest_enemy, 'health'):
                    nearest_enemy.health = max(0, nearest_enemy.health - 10)
                    return 5.0  # Награда за успешную атаку
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка выполнения атаки: {e}")
            return 0.0
    
    def _execute_defend(self, entity, world) -> float:
        """Выполнение защиты"""
        try:
            # Увеличение защиты на короткое время
            if hasattr(entity, 'defense'):
                entity.defense = min(100, entity.defense + 10)
                return 2.0  # Награда за защиту
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка выполнения защиты: {e}")
            return 0.0
    
    def _execute_heal(self, entity, world) -> float:
        """Выполнение лечения"""
        try:
            if hasattr(entity, 'health') and hasattr(entity, 'max_health'):
                if entity.health < entity.max_health:
                    entity.health = min(entity.max_health, entity.health + 20)
                    return 3.0  # Награда за лечение
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка выполнения лечения: {e}")
            return 0.0
    
    def _execute_retreat(self, entity, world) -> float:
        """Выполнение отступления"""
        try:
            # Движение от ближайшего врага
            nearest_enemy = self._get_nearest_enemy(entity, world)
            if nearest_enemy:
                dx, dy = self._calculate_direction_away_from_target(entity, nearest_enemy)
                if hasattr(entity, 'move_pygame'):
                    entity.move_pygame(dx, dy)
                    return 1.0  # Награда за отступление
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка выполнения отступления: {e}")
            return 0.0
    
    def _execute_explore(self, entity, world) -> float:
        """Выполнение исследования"""
        try:
            # Случайное движение для исследования
            dx, dy = self._get_random_movement_direction()
            if hasattr(entity, 'move_pygame'):
                entity.move_pygame(dx, dy)
                return 0.5  # Небольшая награда за исследование
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка выполнения исследования: {e}")
            return 0.0
    
    def _execute_interact(self, entity, world) -> float:
        """Выполнение взаимодействия"""
        try:
            # Поиск ближайшего предмета для взаимодействия
            nearest_item = self._get_nearest_item(entity, world)
            if nearest_item and self._calculate_distance(entity, nearest_item) < 30:
                # Взаимодействие с предметом
                return 2.0  # Награда за взаимодействие
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка выполнения взаимодействия: {e}")
            return 0.0
    
    def _execute_wait(self, entity, world) -> float:
        """Выполнение ожидания"""
        try:
            # Простое ожидание - восстановление ресурсов
            if hasattr(entity, 'stamina'):
                entity.stamina = min(100, entity.stamina + 5)
                return 0.1  # Небольшая награда за ожидание
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка выполнения ожидания: {e}")
            return 0.0
    
    def _modify_reward_by_personality(self, base_reward: float, action: AIAction) -> float:
        """Модификация награды на основе личности"""
        modified_reward = base_reward
        
        if action.action_type == ActionType.ATTACK.value:
            modified_reward *= (1.0 + self.personality.aggression)
        elif action.action_type == ActionType.EXPLORE.value:
            modified_reward *= (1.0 + self.personality.curiosity)
        elif action.action_type == ActionType.DEFEND.value:
            modified_reward *= (1.0 + self.personality.caution)
        elif action.action_type == ActionType.INTERACT.value:
            modified_reward *= (1.0 + self.personality.social)
        
        return modified_reward
    
    def _update_learning(self, current_state: int, action: AIAction, 
                        reward: float, next_state: int):
        """Обновление обучения"""
        action_index = self.available_actions.index(action)
        self.q_agent.update_q_value(current_state, action_index, reward, next_state)
        
        # Увеличение опыта
        self.experience_points += 1
        
        # Проверка повышения уровня
        if self.experience_points >= self.level * 100:
            self._level_up()
    
    def _level_up(self):
        """Повышение уровня ИИ"""
        self.level += 1
        self.experience_points = 0
        
        # Улучшение параметров
        self.personality.adaptability = min(1.0, self.personality.adaptability + 0.1)
        
        logger.info(f"ИИ {self.entity_id} достиг уровня {self.level}")
    
    def _adapt_to_player(self, player):
        """Адаптация к стилю игры игрока"""
        if not player:
            return
        
        try:
            # Анализ действий игрока
            player_actions = getattr(player, 'recent_actions', [])
            
            for action in player_actions:
                action_type = action.get('type', 'unknown')
                self.player_patterns[action_type] = self.player_patterns.get(action_type, 0) + 1
            
            # Адаптация на основе паттернов
            if self.player_patterns.get('attack', 0) > 10:
                self.personality.aggression = min(1.0, self.personality.aggression + 0.1)
            elif self.player_patterns.get('defend', 0) > 10:
                self.personality.caution = min(1.0, self.personality.caution + 0.1)
            
            # Адаптация параметров Q-learning
            performance = self._calculate_performance()
            self.q_agent.adapt_to_performance(performance)
            
        except Exception as e:
            logger.error(f"Ошибка адаптации к игроку: {e}")
    
    def _calculate_performance(self) -> float:
        """Расчёт производительности ИИ"""
        stats = self.q_agent.get_learning_stats()
        if stats["total_updates"] == 0:
            return 0.5
        
        # Простая метрика производительности
        return min(1.0, max(0.0, (stats["avg_reward"] + 1.0) / 2.0))
    
    def _update_ecological_knowledge(self, world):
        """Обновление экологических знаний"""
        try:
            # Обновление знаний о видах на основе опыта
            for entity in getattr(world, 'entities', []):
                if hasattr(entity, 'species'):
                    species = entity.species
                    interaction_result = self._evaluate_interaction(entity)
                    
                    # Обновление знаний
                    if species in self.ecological_knowledge:
                        current_knowledge = self.ecological_knowledge[species]
                        new_knowledge = current_knowledge * 0.9 + interaction_result * 0.1
                        self.ecological_knowledge[species] = max(0.0, min(1.0, new_knowledge))
            
        except Exception as e:
            logger.error(f"Ошибка обновления экологических знаний: {e}")
    
    def _evaluate_interaction(self, entity) -> float:
        """Оценка взаимодействия с сущностью"""
        # Простая оценка на основе типа сущности
        if hasattr(entity, 'is_hostile') and entity.is_hostile:
            return 0.2  # Отрицательный опыт
        elif hasattr(entity, 'is_friendly') and entity.is_friendly:
            return 0.8  # Положительный опыт
        else:
            return 0.5  # Нейтральный опыт
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Получение статистики ИИ"""
        q_stats = self.q_agent.get_learning_stats()
        
        return {
            "entity_id": self.entity_id,
            "level": self.level,
            "experience_points": self.experience_points,
            "current_state": self.current_state,
            "personality": {
                "aggression": self.personality.aggression,
                "curiosity": self.personality.curiosity,
                "caution": self.personality.caution,
                "social": self.personality.social,
                "adaptability": self.personality.adaptability
            },
            "learning_stats": q_stats,
            "ecological_knowledge": self.ecological_knowledge.copy(),
            "player_patterns": self.player_patterns.copy()
        }
    
    def set_personality(self, personality_data: Dict[str, float]):
        """Установка личности ИИ"""
        for key, value in personality_data.items():
            if hasattr(self.personality, key):
                setattr(self.personality, key, max(0.0, min(1.0, value)))
        
        logger.info(f"Личность ИИ {self.entity_id} обновлена")
    
    def reset_learning(self):
        """Сброс обучения"""
        self.q_agent.q_table.fill(0)
        self.experience_points = 0
        self.level = 1
        self.learning_level = 1
        self.learning_history = []
        
        logger.info(f"Обучение ИИ {self.entity_id} сброшено")
    
    def save_ai_state(self, filepath: str) -> bool:
        """Сохранение состояния ИИ"""
        try:
            ai_state = {
                "q_table": self.q_agent.q_table.tolist(),
                "personality": {
                    "aggression": self.personality.aggression,
                    "curiosity": self.personality.curiosity,
                    "caution": self.personality.caution,
                    "social": self.personality.social,
                    "adaptability": self.personality.adaptability
                },
                "level": self.level,
                "experience_points": self.experience_points,
                "ecological_knowledge": self.ecological_knowledge,
                "player_patterns": self.player_patterns
            }
            
            with open(filepath, 'w') as f:
                json.dump(ai_state, f, indent=2)
            
            logger.info(f"Состояние ИИ сохранено в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния ИИ: {e}")
            return False
    
    def load_ai_state(self, filepath: str) -> bool:
        """Загрузка состояния ИИ"""
        try:
            with open(filepath, 'r') as f:
                ai_state = json.load(f)
            
            # Восстановление Q-таблицы
            self.q_agent.q_table = np.array(ai_state["q_table"])
            
            # Восстановление личности
            personality_data = ai_state["personality"]
            for key, value in personality_data.items():
                if hasattr(self.personality, key):
                    setattr(self.personality, key, value)
            
            # Восстановление других параметров
            self.level = ai_state.get("level", 1)
            self.experience_points = ai_state.get("experience_points", 0)
            self.ecological_knowledge = ai_state.get("ecological_knowledge", {})
            self.player_patterns = ai_state.get("player_patterns", {})
            
            logger.info(f"Состояние ИИ загружено из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки состояния ИИ: {e}")
            return False
    
    def _update_learning_level(self):
        """Обновление уровня обучения ИИ"""
        try:
            # Увеличиваем опыт на основе успешных действий
            if self.experience_points > self.level * 100:
                self.level += 1
                self.learning_level = self.level
                self.experience_points = 0
                logger.info(f"ИИ {self.entity_id} достиг уровня {self.level}")
        except Exception as e:
            logger.error(f"Ошибка обновления уровня обучения: {e}")

    def update_environment_info(self, entity, world):
        """Обновление информации об окружении для ИИ"""
        try:
            # Обновляем информацию о ближайших объектах
            self._update_nearest_targets(entity, world)
            
            # Обновляем состояние личности на основе окружения
            self._adapt_personality_to_environment(entity, world)
            
        except Exception as e:
            logger.error(f"Ошибка обновления информации об окружении: {e}")
    
    def _update_nearest_targets(self, entity, world):
        """Обновление информации о ближайших целях"""
        try:
            # Кэшируем информацию о ближайших объектах
            self._cached_nearest_enemy = self._get_nearest_enemy(entity, world)
            self._cached_nearest_item = self._get_nearest_item(entity, world)
            self._cached_nearest_obstacle = self._get_nearest_obstacle(entity, world)
            
        except Exception as e:
            logger.error(f"Ошибка обновления ближайших целей: {e}")
    
    def _adapt_personality_to_environment(self, entity, world):
        """Адаптация личности к окружению"""
        try:
            if not hasattr(self, 'personality'):
                return
            
            # Адаптация на основе количества врагов
            enemy_count = len(getattr(world, 'entities', []))
            if enemy_count > 3:
                # Много врагов - увеличиваем осторожность
                self.personality.caution = min(0.9, self.personality.caution + 0.1)
                self.personality.aggression = max(0.1, self.personality.aggression - 0.05)
            elif enemy_count == 0:
                # Нет врагов - увеличиваем любопытство
                self.personality.curiosity = min(0.9, self.personality.curiosity + 0.1)
                self.personality.caution = max(0.1, self.personality.caution - 0.05)
            
            # Адаптация на основе препятствий
            obstacle_count = len(getattr(world, 'obstacles', []))
            if obstacle_count > 2:
                # Много препятствий - увеличиваем осторожность
                self.personality.caution = min(0.9, self.personality.caution + 0.05)
            
        except Exception as e:
            logger.error(f"Ошибка адаптации личности: {e}")
