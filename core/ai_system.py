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
            return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        except:
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
        """Выполнение действия и получение награды"""
        try:
            reward = 0.0
            
            if action.action_type == ActionType.MOVE.value:
                reward = self._execute_move(entity, world)
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
            
            # Модификация награды на основе личности
            reward = self._modify_reward_by_personality(reward, action)
            
            return reward
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия {action.action_type}: {e}")
            return 0.0
    
    def _execute_move(self, entity, world) -> float:
        """Выполнение движения"""
        # Здесь будет логика движения
        return 0.1
    
    def _execute_attack(self, entity, world) -> float:
        """Выполнение атаки"""
        # Здесь будет логика атаки
        return 0.5
    
    def _execute_defend(self, entity, world) -> float:
        """Выполнение защиты"""
        # Здесь будет логика защиты
        return 0.3
    
    def _execute_heal(self, entity, world) -> float:
        """Выполнение лечения"""
        # Здесь будет логика лечения
        return 0.8
    
    def _execute_retreat(self, entity, world) -> float:
        """Выполнение отступления"""
        # Здесь будет логика отступления
        return -0.2
    
    def _execute_explore(self, entity, world) -> float:
        """Выполнение исследования"""
        # Здесь будет логика исследования
        return 0.2
    
    def _execute_interact(self, entity, world) -> float:
        """Выполнение взаимодействия"""
        # Здесь будет логика взаимодействия
        return 0.4
    
    def _execute_wait(self, entity, world) -> float:
        """Выполнение ожидания"""
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
        self.learning_history.clear()
        
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
