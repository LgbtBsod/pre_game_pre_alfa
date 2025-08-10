import time
from collections import deque
import random
import math
import numpy as np

class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
    
    def add(self, state, action, reward, next_state):
        self.buffer.append((state, action, reward, next_state))
    
    def sample(self, batch_size):
        if len(self.buffer) < batch_size:
            return self.buffer
        return random.sample(self.buffer, batch_size)

class AIMemory:
    def __init__(self, capacity=10):
        self.memory = deque(maxlen=capacity)
        self.learned_patterns = {}
        self.success_count = 0
        self.failure_count = 0
        self.weights = {}  # Веса для каждого воспоминания
    
    def record_event(self, event_type, data):
        event = {
            "time": time.time(),
            "type": event_type,
            "data": data
        }
        self.memory.append(event)
        self.weights[len(self.memory)-1] = 1.0  # Начальный вес
    
    def count_successes(self, action_type=None):
        if action_type:
            return sum(1 for i, e in enumerate(self.memory) 
                      if e.get('result') == 'SUCCESS' and e.get('action') == action_type
                      and self.weights.get(i, 1.0) > 0.1)
        return sum(1 for i, e in enumerate(self.memory) 
                  if e.get('result') == 'SUCCESS' and self.weights.get(i, 1.0) > 0.1)
    
    def count_failures(self, action_type=None):
        if action_type:
            return sum(1 for i, e in enumerate(self.memory) 
                      if e.get('result') == 'FAILURE' and e.get('action') == action_type
                      and self.weights.get(i, 1.0) > 0.1)
        return sum(1 for i, e in enumerate(self.memory) 
                  if e.get('result') == 'FAILURE' and self.weights.get(i, 1.0) > 0.1)
    
    def recognize_pattern(self, current_situation, pattern_recognizer=None):
        if pattern_recognizer:
            return pattern_recognizer.recognize(current_situation)
        
        # Fallback to simple recognition
        for pattern, response in self.learned_patterns.items():
            if self._similarity(pattern, current_situation) > 0.7:
                return response
        return None
    
    def learn_from_experience(self, situation, action, outcome):
        self.learned_patterns[situation] = (action, outcome)
        
        if outcome == "SUCCESS":
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def decay_memories(self, decay_rate=0.05):
        for idx in self.weights:
            self.weights[idx] *= (1 - decay_rate)
    
    def _similarity(self, pattern, situation):
        common_keys = set(pattern.keys()) & set(situation.keys())
        if not common_keys:
            return 0.0
        
        similarity = 0
        for key in common_keys:
            if pattern[key] == situation[key]:
                similarity += 1
        return similarity / len(common_keys)

class LearningController:
    def __init__(self, entity):
        self.entity = entity
        self.memory = AIMemory()
        self.replay_buffer = ReplayBuffer(capacity=1000)
        self.q_table = {}
        self.LEARNING_RATE = 0.1
        self.DISCOUNT_FACTOR = 0.95
        self.last_state = None
        self.last_action = None
        self.exploration_rate = 0.2
    
    def _get_state_hash(self):
        # Безопасные вычисления признаков состояния
        try:
            health_val = round(float(self.entity.health), 1)
        except Exception:
            health_val = 0.0

        try:
            stamina_val = round(float(getattr(self.entity, "stamina", 0.0)), 1)
        except Exception:
            stamina_val = 0.0

        try:
            mana_val = round(float(getattr(self.entity, "mana", 0.0)), 1)
        except Exception:
            mana_val = 0.0

        try:
            pos = (int(self.entity.position[0] / 10), int(self.entity.position[1] / 10))
        except Exception:
            pos = (0, 0)

        # Определяем близость врага по доступным данным
        enemy_near = False
        if hasattr(self.entity, "nearby_enemies"):
            enemy_near = bool(getattr(self.entity, "nearby_enemies", False))
        elif hasattr(self.entity, "get_nearby_entities"):
            try:
                enemy_near = len(self.entity.get_nearby_entities(radius=15.0, enemy_only=True)) > 0
            except Exception:
                enemy_near = False

        state = {
            "health": health_val,
            "enemy_near": enemy_near,
            "emotion": getattr(self.entity, "emotion", "NEUTRAL"),
            "stamina": stamina_val,
            "mana": mana_val,
            "position": pos,
        }
        return str(state)
    
    def _choose_action(self, state_hash):
        if state_hash not in self.q_table:
            # Initialize with possible actions
            self.q_table[state_hash] = {
                "ATTACK": 0,
                "DEFEND": 0,
                "USE_ITEM": 0,
                "FLEE": 0,
                "CAST_SPELL": 0
            }
            # Add spell actions (используем skills вместо spells)
            if hasattr(self.entity, 'skills') and self.entity.skills:
                for skill_name in self.entity.skills.keys():
                    self.q_table[state_hash][f"CAST_{skill_name}"] = 0
        
        # Эпсилон-жадная стратегия
        if random.random() < self.exploration_rate:
            return random.choice(list(self.q_table[state_hash].keys()))
        
        return max(self.q_table[state_hash], key=self.q_table[state_hash].get)
    
    def update(self, delta_time):
        current_state = self._get_state_hash()
        
        if self.last_state and self.last_action:
            reward = self._calculate_reward()
            self.replay_buffer.add(self.last_state, self.last_action, reward, current_state)
            
            # Обновляем Q-значение
            current_q = self.q_table[self.last_state][self.last_action]
            max_next_q = max(self.q_table.get(current_state, {"ATTACK": 0}).values())
            
            new_q = (1 - self.LEARNING_RATE) * current_q + \
                    self.LEARNING_RATE * (reward + self.DISCOUNT_FACTOR * max_next_q)
            
            self.q_table[self.last_state][self.last_action] = new_q
        
        # Выбор и выполнение нового действия
        action = self._choose_action(current_state)
        self.last_action = action
        self.last_state = current_state
        
        # Выполняем действие
        self._perform_action(action)
        
        # Уменьшаем exploration_rate со временем
        self.exploration_rate = max(0.01, self.exploration_rate * 0.999)
    
    def _calculate_reward(self):
        reward = 0
        
        # Награда за выживание
        if self.entity.health > 0:
            reward += 0.1
        
        # Награда за успешную атаку/заклинание
        if hasattr(self.entity, 'last_action_success') and self.entity.last_action_success:
            reward += 1.0
        
        # Штраф за потерю здоровья
        if hasattr(self.entity, 'last_health') and self.entity.health < self.entity.last_health:
            reward -= 0.5 * (self.entity.last_health - self.entity.health)
        
        # Штраф за смерть
        if self.entity.health <= 0:
            reward -= 10.0
        
        # Награда за эффективное использование маны
        if hasattr(self.entity, 'last_mana_used'):
            efficiency = self.entity.last_mana_used / max(1, self.entity.last_damage_dealt)
            if efficiency < 0.5:
                reward += 0.3
        
        return reward
    
    def _perform_action(self, action):
        if action == "ATTACK":
            # Используем существующий метод attack если есть цель
            if hasattr(self.entity, 'target') and self.entity.target:
                self.entity.attack(self.entity.target)
        elif action == "DEFEND":
            # Простое действие защиты - увеличиваем защиту
            if hasattr(self.entity, 'combat_stats'):
                self.entity.combat_stats['defense'] = min(20, self.entity.combat_stats.get('defense', 5) + 1)
        elif action == "USE_ITEM":
            # Используем существующий метод
            if hasattr(self.entity, 'use_best_healing_item'):
                self.entity.use_best_healing_item()
        elif action == "FLEE":
            # Простое бегство - отдаляемся от угрозы
            if hasattr(self.entity, 'position') and hasattr(self.entity, 'movement_speed'):
                # Упрощенная логика бегства
                pass
        elif action.startswith("CAST_"):
            skill_name = action[5:]
            # Используем существующий метод use_skill
            if hasattr(self.entity, 'use_skill'):
                self.entity.use_skill(skill_name)
            
class EnhancedAIMemory(AIMemory):
    def __init__(self, short_term_capacity=10, long_term_capacity=100):
        super().__init__(short_term_capacity)
        self.long_term_memory = deque(maxlen=long_term_capacity)
        self.memory_decay_rate = 0.01
    
    def record_event(self, event_type, data, importance=1.0):
        super().record_event(event_type, data)
        # Важные события попадают в долговременную память
        if importance > 0.7:
            self.long_term_memory.append({
                "time": time.time(),
                "type": event_type,
                "data": data,
                "importance": importance
            })
    
    def forget_old_memories(self):
        # Уменьшение важности воспоминаний со временем
        current_time = time.time()
        for memory in list(self.long_term_memory):
            age = current_time - memory["time"]
            memory["importance"] *= math.exp(-self.memory_decay_rate * age)
            
            # Удаление неважных воспоминаний
            if memory["importance"] < 0.1:
                self.long_term_memory.remove(memory)