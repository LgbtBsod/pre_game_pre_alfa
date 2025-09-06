#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
import math
import json
import pickle
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Попытка импорта ML фреймворков
TORCH_AVAILABLE = False
try:
    # Отложенная загрузка PyTorch
    torch = None
    nn = None
    optim = None
    TORCH_AVAILABLE = False
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class AIType(Enum):
    """Типы искусственного интеллекта"""
    BEHAVIOR_TREE = "behavior_tree"
    STATE_MACHINE = "state_machine"
    NEURAL_NETWORK = "neural_network"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    EVOLUTIONARY = "evolutionary"
    HYBRID = "hybrid"

class AIState(Enum):
    """Состояния ИИ"""
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"
    SEARCH = "search"
    GUARD = "guard"
    INTERACT = "interact"

class MemoryType(Enum):
    """Типы памяти"""
    COMBAT = "combat"
    MOVEMENT = "movement"
    SKILL_USAGE = "skill_usage"
    ITEM_USAGE = "item_usage"
    ENVIRONMENT = "environment"
    SOCIAL = "social"

@dataclass
class MemoryEntry:
    """Запись в памяти"""
    memory_id: str
    memory_type: MemoryType
    data: Dict[str, Any]
    importance: float = 1.0
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)

@dataclass
class AIBehavior:
    """Поведение ИИ"""
    behavior_id: str
    name: str
    description: str
    conditions: List[Callable] = field(default_factory=list)
    actions: List[Callable] = field(default_factory=list)
    priority: int = 1
    cooldown: float = 0.0
    last_used: float = 0.0

class AINeuralNetwork:
    """Упрощенная нейронная сеть для принятия решений"""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Простые веса (без PyTorch)
        self.weights_input_hidden = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.weights_hidden_output = [[random.uniform(-1, 1) for _ in range(output_size)] for _ in range(hidden_size)]
        self.bias_hidden = [random.uniform(-1, 1) for _ in range(hidden_size)]
        self.bias_output = [random.uniform(-1, 1) for _ in range(output_size)]
    
    def sigmoid(self, x):
        """Функция активации"""
        return 1 / (1 + math.exp(-max(-500, min(500, x))))
    
    def forward(self, inputs):
        """Прямой проход"""
        # Скрытый слой
        hidden = []
        for i in range(self.hidden_size):
            sum_val = self.bias_hidden[i]
            for j in range(self.input_size):
                sum_val += inputs[j] * self.weights_input_hidden[j][i]
            hidden.append(self.sigmoid(sum_val))
        
        # Выходной слой
        outputs = []
        for i in range(self.output_size):
            sum_val = self.bias_output[i]
            for j in range(self.hidden_size):
                sum_val += hidden[j] * self.weights_hidden_output[j][i]
            outputs.append(self.sigmoid(sum_val))
        
        return outputs
    
    def mutate(self, mutation_rate: float = 0.1):
        """Мутация весов"""
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                if random.random() < mutation_rate:
                    self.weights_input_hidden[i][j] += random.uniform(-0.5, 0.5)
        
        for i in range(self.hidden_size):
            for j in range(self.output_size):
                if random.random() < mutation_rate:
                    self.weights_hidden_output[i][j] += random.uniform(-0.5, 0.5)
        
        for i in range(self.hidden_size):
            if random.random() < mutation_rate:
                self.bias_hidden[i] += random.uniform(-0.5, 0.5)
        
        for i in range(self.output_size):
            if random.random() < mutation_rate:
                self.bias_output[i] += random.uniform(-0.5, 0.5)

class AdvancedAISystem:
    """Продвинутая система искусственного интеллекта"""
    
    def __init__(self, save_directory: str = "saves/ai_memory"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        # ИИ сущности
        self.ai_entities: Dict[str, Dict[str, Any]] = {}
        self.memories: Dict[str, List[MemoryEntry]] = {}
        self.behaviors: Dict[str, List[AIBehavior]] = {}
        self.neural_networks: Dict[str, AINeuralNetwork] = {}
        
        # Настройки
        self.max_memories_per_entity = 1000
        self.memory_decay_rate = 0.01
        self.learning_rate = 0.1
        self.mutation_rate = 0.05
        
        # Статистика
        self.decisions_made = 0
        self.learning_events = 0
        
    def create_ai_entity(self, entity_id: str, ai_type: AIType = AIType.STATE_MACHINE, 
                        initial_state: AIState = AIState.IDLE) -> bool:
        """Создание ИИ для сущности"""
        try:
            self.ai_entities[entity_id] = {
                'ai_type': ai_type,
                'current_state': initial_state,
                'target_entity': None,
                'last_decision_time': 0.0,
                'decision_cooldown': 0.1,
                'fitness_score': 0.0,
                'generation': 0,
                'learning_data': []
            }
            
            # Инициализация памяти
            self.memories[entity_id] = []
            
            # Инициализация поведения
            self.behaviors[entity_id] = self._create_default_behaviors()
            
            # Создание нейронной сети если нужно
            if ai_type in [AIType.NEURAL_NETWORK, AIType.REINFORCEMENT_LEARNING, AIType.EVOLUTIONARY]:
                self.neural_networks[entity_id] = AINeuralNetwork(
                    input_size=20,  # Размер входных данных
                    hidden_size=16,
                    output_size=8   # Количество возможных действий
                )
            
            return True
        except Exception as e:
            print(f"Ошибка создания ИИ для {entity_id}: {e}")
            return False
    
    def make_decision(self, entity_id: str, game_state: Dict[str, Any]) -> Optional[str]:
        """Принятие решения ИИ"""
        if entity_id not in self.ai_entities:
            return None
        
        ai_data = self.ai_entities[entity_id]
        current_time = time.time()
        
        # Проверяем кулдаун решений
        if current_time - ai_data['last_decision_time'] < ai_data['decision_cooldown']:
            return None
        
        decision = None
        
        try:
            if ai_data['ai_type'] == AIType.STATE_MACHINE:
                decision = self._state_machine_decision(entity_id, game_state)
            elif ai_data['ai_type'] == AIType.NEURAL_NETWORK:
                decision = self._neural_network_decision(entity_id, game_state)
            elif ai_data['ai_type'] == AIType.REINFORCEMENT_LEARNING:
                decision = self._reinforcement_learning_decision(entity_id, game_state)
            elif ai_data['ai_type'] == AIType.EVOLUTIONARY:
                decision = self._evolutionary_decision(entity_id, game_state)
            else:
                decision = self._behavior_tree_decision(entity_id, game_state)
            
            # Обновляем время последнего решения
            ai_data['last_decision_time'] = current_time
            self.decisions_made += 1
            
            # Сохраняем данные для обучения
            if ai_data['ai_type'] in [AIType.REINFORCEMENT_LEARNING, AIType.EVOLUTIONARY]:
                self._record_decision_data(entity_id, game_state, decision)
            
        except Exception as e:
            print(f"Ошибка принятия решения для {entity_id}: {e}")
        
        return decision
    
    def learn_from_experience(self, entity_id: str, experience_data: Dict[str, Any]):
        """Обучение на основе опыта"""
        if entity_id not in self.ai_entities:
            return
        
        ai_data = self.ai_entities[entity_id]
        
        try:
            if ai_data['ai_type'] == AIType.REINFORCEMENT_LEARNING:
                self._reinforcement_learning_update(entity_id, experience_data)
            elif ai_data['ai_type'] == AIType.EVOLUTIONARY:
                self._evolutionary_learning_update(entity_id, experience_data)
            
            self.learning_events += 1
            
        except Exception as e:
            print(f"Ошибка обучения для {entity_id}: {e}")
    
    def add_memory(self, entity_id: str, memory_type: MemoryType, data: Dict[str, Any], 
                   importance: float = 1.0):
        """Добавление памяти"""
        if entity_id not in self.memories:
            return
        
        memory = MemoryEntry(
            memory_id=f"{entity_id}_{int(time.time() * 1000)}",
            memory_type=memory_type,
            data=data,
            importance=importance
        )
        
        self.memories[entity_id].append(memory)
        
        # Ограничиваем количество воспоминаний
        if len(self.memories[entity_id]) > self.max_memories_per_entity:
            # Удаляем самые старые и менее важные воспоминания
            self.memories[entity_id].sort(key=lambda m: (m.importance, m.timestamp))
            self.memories[entity_id] = self.memories[entity_id][-self.max_memories_per_entity:]
    
    def get_relevant_memories(self, entity_id: str, memory_type: MemoryType, 
                            limit: int = 10) -> List[MemoryEntry]:
        """Получение релевантных воспоминаний"""
        if entity_id not in self.memories:
            return []
        
        relevant = [m for m in self.memories[entity_id] if m.memory_type == memory_type]
        relevant.sort(key=lambda m: (m.importance, m.last_access), reverse=True)
        
        # Обновляем счетчик доступа
        for memory in relevant[:limit]:
            memory.access_count += 1
            memory.last_access = time.time()
        
        return relevant[:limit]
    
    def evolve_ai(self, entity_id: str, fitness_score: float):
        """Эволюция ИИ"""
        if entity_id not in self.ai_entities or entity_id not in self.neural_networks:
            return
        
        ai_data = self.ai_entities[entity_id]
        ai_data['fitness_score'] = fitness_score
        
        # Если это эволюционный ИИ, мутируем нейронную сеть
        if ai_data['ai_type'] == AIType.EVOLUTIONARY:
            self.neural_networks[entity_id].mutate(self.mutation_rate)
            ai_data['generation'] += 1
    
    def save_ai_state(self, entity_id: str):
        """Сохранение состояния ИИ"""
        if entity_id not in self.ai_entities:
            return
        
        try:
            save_data = {
                'ai_entity': self.ai_entities[entity_id],
                'memories': [
                    {
                        'memory_id': m.memory_id,
                        'memory_type': m.memory_type.value,
                        'data': m.data,
                        'importance': m.importance,
                        'timestamp': m.timestamp,
                        'access_count': m.access_count,
                        'last_access': m.last_access
                    }
                    for m in self.memories.get(entity_id, [])
                ],
                'neural_network': None
            }
            
            # Сохраняем нейронную сеть если есть
            if entity_id in self.neural_networks:
                nn = self.neural_networks[entity_id]
                save_data['neural_network'] = {
                    'input_size': nn.input_size,
                    'hidden_size': nn.hidden_size,
                    'output_size': nn.output_size,
                    'weights_input_hidden': nn.weights_input_hidden,
                    'weights_hidden_output': nn.weights_hidden_output,
                    'bias_hidden': nn.bias_hidden,
                    'bias_output': nn.bias_output
                }
            
            save_file = self.save_directory / f"{entity_id}_ai_state.json"
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Ошибка сохранения ИИ для {entity_id}: {e}")
    
    def load_ai_state(self, entity_id: str) -> bool:
        """Загрузка состояния ИИ"""
        try:
            save_file = self.save_directory / f"{entity_id}_ai_state.json"
            if not save_file.exists():
                return False
            
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Восстанавливаем ИИ сущность
            self.ai_entities[entity_id] = save_data['ai_entity']
            
            # Восстанавливаем память
            self.memories[entity_id] = []
            for mem_data in save_data['memories']:
                memory = MemoryEntry(
                    memory_id=mem_data['memory_id'],
                    memory_type=MemoryType(mem_data['memory_type']),
                    data=mem_data['data'],
                    importance=mem_data['importance'],
                    timestamp=mem_data['timestamp'],
                    access_count=mem_data['access_count'],
                    last_access=mem_data['last_access']
                )
                self.memories[entity_id].append(memory)
            
            # Восстанавливаем нейронную сеть
            if save_data['neural_network']:
                nn_data = save_data['neural_network']
                nn = AINeuralNetwork(
                    nn_data['input_size'],
                    nn_data['hidden_size'],
                    nn_data['output_size']
                )
                nn.weights_input_hidden = nn_data['weights_input_hidden']
                nn.weights_hidden_output = nn_data['weights_hidden_output']
                nn.bias_hidden = nn_data['bias_hidden']
                nn.bias_output = nn_data['bias_output']
                self.neural_networks[entity_id] = nn
            
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки ИИ для {entity_id}: {e}")
            return False
    
    def _create_default_behaviors(self) -> List[AIBehavior]:
        """Создание поведения по умолчанию"""
        behaviors = []
        
        # Поведение атаки
        attack_behavior = AIBehavior(
            behavior_id="attack",
            name="Attack",
            description="Атака ближайшего врага",
            priority=3,
            cooldown=1.0
        )
        behaviors.append(attack_behavior)
        
        # Поведение преследования
        chase_behavior = AIBehavior(
            behavior_id="chase",
            name="Chase",
            description="Преследование цели",
            priority=2,
            cooldown=0.5
        )
        behaviors.append(chase_behavior)
        
        # Поведение патрулирования
        patrol_behavior = AIBehavior(
            behavior_id="patrol",
            name="Patrol",
            description="Патрулирование территории",
            priority=1,
            cooldown=2.0
        )
        behaviors.append(patrol_behavior)
        
        return behaviors
    
    def _state_machine_decision(self, entity_id: str, game_state: Dict[str, Any]) -> Optional[str]:
        """Принятие решения на основе конечного автомата"""
        ai_data = self.ai_entities[entity_id]
        current_state = ai_data['current_state']
        
        # Простая логика состояний
        if current_state == AIState.IDLE:
            # Ищем ближайшего врага
            if 'enemies' in game_state and game_state['enemies']:
                ai_data['current_state'] = AIState.CHASE
                ai_data['target_entity'] = game_state['enemies'][0]
                return "chase"
            else:
                ai_data['current_state'] = AIState.PATROL
                return "patrol"
        
        elif current_state == AIState.CHASE:
            if ai_data['target_entity'] and 'distance_to_target' in game_state:
                distance = game_state['distance_to_target']
                if distance < 2.0:
                    ai_data['current_state'] = AIState.ATTACK
                    return "attack"
                elif distance > 10.0:
                    ai_data['current_state'] = AIState.SEARCH
                    return "search"
                else:
                    return "chase"
        
        elif current_state == AIState.ATTACK:
            if 'target_health' in game_state and game_state['target_health'] <= 0:
                ai_data['current_state'] = AIState.IDLE
                ai_data['target_entity'] = None
                return "idle"
            else:
                return "attack"
        
        return None
    
    def _neural_network_decision(self, entity_id: str, game_state: Dict[str, Any]) -> Optional[str]:
        """Принятие решения на основе нейронной сети"""
        if entity_id not in self.neural_networks:
            return None
        
        # Подготавливаем входные данные
        inputs = self._prepare_inputs(entity_id, game_state)
        
        # Получаем выход нейронной сети
        outputs = self.neural_networks[entity_id].forward(inputs)
        
        # Выбираем действие с максимальным выходом
        action_index = outputs.index(max(outputs))
        actions = ["idle", "patrol", "chase", "attack", "flee", "search", "guard", "interact"]
        
        if action_index < len(actions):
            return actions[action_index]
        
        return None
    
    def _reinforcement_learning_decision(self, entity_id: str, game_state: Dict[str, Any]) -> Optional[str]:
        """Принятие решения на основе обучения с подкреплением"""
        # Упрощенная версия Q-learning
        if entity_id not in self.neural_networks:
            return None
        
        inputs = self._prepare_inputs(entity_id, game_state)
        outputs = self.neural_networks[entity_id].forward(inputs)
        
        # Добавляем случайность для исследования
        if random.random() < 0.1:  # 10% случайности
            action_index = random.randint(0, len(outputs) - 1)
        else:
            action_index = outputs.index(max(outputs))
        
        actions = ["idle", "patrol", "chase", "attack", "flee", "search", "guard", "interact"]
        return actions[action_index] if action_index < len(actions) else None
    
    def _evolutionary_decision(self, entity_id: str, game_state: Dict[str, Any]) -> Optional[str]:
        """Принятие решения на основе эволюционного алгоритма"""
        return self._neural_network_decision(entity_id, game_state)
    
    def _behavior_tree_decision(self, entity_id: str, game_state: Dict[str, Any]) -> Optional[str]:
        """Принятие решения на основе дерева поведения"""
        behaviors = self.behaviors.get(entity_id, [])
        current_time = time.time()
        
        # Сортируем по приоритету
        behaviors.sort(key=lambda b: b.priority, reverse=True)
        
        for behavior in behaviors:
            # Проверяем кулдаун
            if current_time - behavior.last_used < behavior.cooldown:
                continue
            
            # Проверяем условия
            if all(condition(game_state) for condition in behavior.conditions):
                behavior.last_used = current_time
                return behavior.behavior_id
        
        return "idle"
    
    def _prepare_inputs(self, entity_id: str, game_state: Dict[str, Any]) -> List[float]:
        """Подготовка входных данных для нейронной сети"""
        inputs = []
        
        # Позиция сущности
        if 'position' in game_state:
            inputs.extend(game_state['position'][:3])  # x, y, z
        else:
            inputs.extend([0.0, 0.0, 0.0])
        
        # Здоровье
        inputs.append(game_state.get('health', 100.0) / 100.0)
        
        # Ближайший враг
        if 'nearest_enemy' in game_state and game_state['nearest_enemy']:
            enemy = game_state['nearest_enemy']
            inputs.append(enemy.get('distance', 0.0) / 20.0)  # Нормализованное расстояние
            inputs.append(enemy.get('health', 100.0) / 100.0)
            inputs.extend(enemy.get('position', [0.0, 0.0, 0.0])[:3])
        else:
            inputs.extend([1.0, 1.0, 0.0, 0.0, 0.0])  # Нет врага
        
        # Окружение
        inputs.append(game_state.get('time_of_day', 0.5))  # Время дня (0-1)
        inputs.append(game_state.get('weather_intensity', 0.0))  # Интенсивность погоды
        
        # Память
        recent_memories = self.get_relevant_memories(entity_id, MemoryType.COMBAT, 3)
        inputs.append(min(len(recent_memories) / 3.0, 1.0))
        
        # Дополняем до нужного размера
        while len(inputs) < 20:
            inputs.append(0.0)
        
        return inputs[:20]
    
    def _record_decision_data(self, entity_id: str, game_state: Dict[str, Any], decision: str):
        """Запись данных для обучения"""
        if entity_id not in self.ai_entities:
            return
        
        learning_data = {
            'timestamp': time.time(),
            'game_state': game_state.copy(),
            'decision': decision,
            'reward': 0.0  # Будет установлен позже
        }
        
        self.ai_entities[entity_id]['learning_data'].append(learning_data)
        
        # Ограничиваем размер данных
        if len(self.ai_entities[entity_id]['learning_data']) > 1000:
            self.ai_entities[entity_id]['learning_data'] = self.ai_entities[entity_id]['learning_data'][-1000:]
    
    def _reinforcement_learning_update(self, entity_id: str, experience_data: Dict[str, Any]):
        """Обновление обучения с подкреплением"""
        # Упрощенная версия - в реальной реализации здесь был бы Q-learning
        pass
    
    def _evolutionary_learning_update(self, entity_id: str, experience_data: Dict[str, Any]):
        """Обновление эволюционного обучения"""
        # Обновляем фитнес-функцию
        if 'fitness_delta' in experience_data:
            self.ai_entities[entity_id]['fitness_score'] += experience_data['fitness_delta']
