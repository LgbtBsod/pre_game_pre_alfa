#!/usr/bin/env python3
"""
PyTorch AI System - Продвинутая система искусственного интеллекта
Использует PyTorch для нейронных сетей, обучения с подкреплением и эмоционального отклика
"""

import logging
import json
import pickle
import random
import math
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import numpy as np

# PyTorch imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("PyTorch не установлен. AI система будет использовать базовую логику.")

logger = logging.getLogger(__name__)

class EmotionType(Enum):
    """Типы эмоций AI"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"

class PersonalityType(Enum):
    """Типы личности AI"""
    CURIOUS = "curious"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    SOCIAL = "social"
    LONER = "loner"
    LEADER = "leader"
    FOLLOWER = "follower"

@dataclass
class Memory:
    """Структура памяти AI"""
    id: str
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    emotional_impact: float
    importance: float
    associations: List[str]

@dataclass
class Emotion:
    """Структура эмоции"""
    type: EmotionType
    intensity: float
    duration: float
    trigger: str
    timestamp: float

@dataclass
class Personality:
    """Структура личности AI"""
    type: PersonalityType
    traits: Dict[str, float]
    preferences: Dict[str, float]
    fears: List[str]
    desires: List[str]

class NeuralNetwork(nn.Module):
    """Нейронная сеть для принятия решений AI"""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

class EmotionalNetwork(nn.Module):
    """Нейронная сеть для обработки эмоций"""
    
    def __init__(self, input_size: int, emotion_size: int):
        super(EmotionalNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, emotion_size)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))  # Нормализуем эмоции
        return x

class MemoryDataset(Dataset):
    """Датасет для обучения на основе памяти"""
    
    def __init__(self, memories: List[Memory], sequence_length: int = 10):
        self.memories = memories
        self.sequence_length = sequence_length
        
    def __len__(self):
        return max(0, len(self.memories) - self.sequence_length)
        
    def __getitem__(self, idx):
        sequence = self.memories[idx:idx + self.sequence_length]
        # Создаем входные данные из последовательности воспоминаний
        inputs = []
        for memory in sequence:
            # Векторизуем память
            memory_vector = [
                memory.emotional_impact,
                memory.importance,
                time.time() - memory.timestamp,  # Время с момента события
                len(memory.associations)
            ]
            inputs.extend(memory_vector)
        
        # Цель - предсказать следующее действие
        target = random.choice([0, 1, 2, 3])  # Простые действия
        
        return torch.FloatTensor(inputs), torch.LongTensor([target])

class PyTorchAISystem:
    """Продвинутая AI система на основе PyTorch"""
    
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.memories: Dict[str, List[Memory]] = defaultdict(list)
        self.emotions: Dict[str, List[Emotion]] = defaultdict(list)
        self.personalities: Dict[str, Personality] = {}
        
        # Нейронные сети
        self.decision_networks: Dict[str, NeuralNetwork] = {}
        self.emotional_networks: Dict[str, EmotionalNetwork] = {}
        self.optimizers: Dict[str, optim.Adam] = {}
        
        # Параметры обучения
        self.learning_rate = 0.001
        self.memory_size = 1000
        self.emotion_decay = 0.95
        self.learning_enabled = True
        
        # Статистика
        self.total_decisions = 0
        self.successful_decisions = 0
        self.learning_iterations = 0
        
        logger.info("PyTorch AI система инициализирована")
    
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any], 
                       memory_group: str = "default") -> bool:
        """Регистрация сущности в AI системе"""
        try:
            if not PYTORCH_AVAILABLE:
                logger.warning("PyTorch недоступен, используется базовая AI")
                return self._register_basic_entity(entity_id, entity_data, memory_group)
            
            # Создаем личность для сущности
            personality = self._create_personality(entity_data.get('ai_personality', 'curious'))
            self.personalities[entity_id] = personality
            
            # Инициализируем нейронные сети
            self._initialize_networks(entity_id)
            
            # Сохраняем данные сущности
            self.entities[entity_id] = {
                'data': entity_data,
                'memory_group': memory_group,
                'last_action': None,
                'current_emotion': EmotionType.NEUTRAL,
                'emotion_intensity': 0.0,
                'learning_rate': self.learning_rate,
                'decision_history': deque(maxlen=100)
            }
            
            logger.info(f"Сущность {entity_id} зарегистрирована в PyTorch AI системе")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации сущности {entity_id}: {e}")
            return False
    
    def _register_basic_entity(self, entity_id: str, entity_data: Dict[str, Any], 
                              memory_group: str) -> bool:
        """Базовая регистрация без PyTorch"""
        self.entities[entity_id] = {
            'data': entity_data,
            'memory_group': memory_group,
            'last_action': None,
            'current_emotion': EmotionType.NEUTRAL,
            'emotion_intensity': 0.0
        }
        return True
    
    def _create_personality(self, personality_type: str) -> Personality:
        """Создание личности для AI"""
        personality_map = {
            'curious': {
                'traits': {'exploration': 0.8, 'learning': 0.9, 'social': 0.6},
                'preferences': {'new_experiences': 0.9, 'knowledge': 0.8},
                'fears': ['boredom', 'ignorance'],
                'desires': ['discovery', 'understanding']
            },
            'aggressive': {
                'traits': {'combat': 0.9, 'dominance': 0.8, 'territory': 0.7},
                'preferences': {'conflict': 0.8, 'power': 0.9},
                'fears': ['weakness', 'submission'],
                'desires': ['victory', 'control']
            },
            'defensive': {
                'traits': {'caution': 0.8, 'protection': 0.9, 'stability': 0.7},
                'preferences': {'safety': 0.9, 'peace': 0.8},
                'fears': ['danger', 'chaos'],
                'desires': ['security', 'order']
            },
            'social': {
                'traits': {'cooperation': 0.9, 'empathy': 0.8, 'communication': 0.8},
                'preferences': {'interaction': 0.9, 'harmony': 0.8},
                'fears': ['isolation', 'conflict'],
                'desires': ['friendship', 'community']
            }
        }
        
        config = personality_map.get(personality_type, personality_map['curious'])
        
        return Personality(
            type=PersonalityType(personality_type),
            traits=config['traits'],
            preferences=config['preferences'],
            fears=config['fears'],
            desires=config['desires']
        )
    
    def _initialize_networks(self, entity_id: str):
        """Инициализация нейронных сетей для сущности"""
        if not PYTORCH_AVAILABLE:
            return
        
        # Сеть принятия решений
        input_size = 20  # Состояние + память + эмоции
        hidden_size = 64
        output_size = 8  # Количество возможных действий
        
        self.decision_networks[entity_id] = NeuralNetwork(input_size, hidden_size, output_size)
        self.optimizers[entity_id] = optim.Adam(
            self.decision_networks[entity_id].parameters(), 
            lr=self.learning_rate
        )
        
        # Сеть эмоций
        emotion_input_size = 10  # Входные данные для эмоций
        emotion_size = len(EmotionType)
        
        self.emotional_networks[entity_id] = EmotionalNetwork(emotion_input_size, emotion_size)
        
        logger.debug(f"Нейронные сети для {entity_id} инициализированы")
    
    def update_entity(self, entity_id: str, entity_data: Dict[str, Any], delta_time: float):
        """Обновление AI сущности"""
        if entity_id not in self.entities:
            return
        
        try:
            # Обновляем данные сущности
            self.entities[entity_id]['data'] = entity_data
            
            # Обрабатываем эмоции
            self._update_emotions(entity_id, delta_time)
            
            # Принимаем решение
            decision = self._make_decision(entity_id, entity_data)
            
            # Сохраняем память о решении
            self._store_memory(entity_id, "decision", {
                'action': decision,
                'context': self._get_context(entity_id, entity_data)
            })
            
            # Обучение на основе результата
            if self.learning_enabled:
                self._learn_from_experience(entity_id, decision, entity_data)
            
        except Exception as e:
            logger.error(f"Ошибка обновления AI сущности {entity_id}: {e}")
    
    def _update_emotions(self, entity_id: str, delta_time: float):
        """Обновление эмоционального состояния"""
        if not PYTORCH_AVAILABLE:
            return self._update_basic_emotions(entity_id, delta_time)
        
        # Получаем текущие эмоции
        current_emotions = self.emotions[entity_id]
        
        # Создаем входные данные для эмоциональной сети
        emotion_input = self._create_emotion_input(entity_id)
        
        # Предсказываем новые эмоции
        with torch.no_grad():
            emotion_tensor = torch.FloatTensor(emotion_input).unsqueeze(0)
            emotion_output = self.emotional_networks[entity_id](emotion_tensor)
            
            # Находим доминирующую эмоцию
            emotion_probs = emotion_output.squeeze().numpy()
            dominant_emotion_idx = np.argmax(emotion_probs)
            intensity = emotion_probs[dominant_emotion_idx]
            
            emotion_type = list(EmotionType)[dominant_emotion_idx]
            
            # Создаем новую эмоцию
            new_emotion = Emotion(
                type=emotion_type,
                intensity=intensity,
                duration=delta_time,
                trigger="neural_network",
                timestamp=time.time()
            )
            
            current_emotions.append(new_emotion)
            
            # Обновляем состояние сущности
            self.entities[entity_id]['current_emotion'] = emotion_type
            self.entities[entity_id]['emotion_intensity'] = intensity
            
            # Ограничиваем количество эмоций
            if len(current_emotions) > 50:
                current_emotions.pop(0)
    
    def _update_basic_emotions(self, entity_id: str, delta_time: float):
        """Базовая обработка эмоций без PyTorch"""
        entity = self.entities[entity_id]
        personality = self.personalities.get(entity_id)
        
        if not personality:
            return
        
        # Простая логика эмоций на основе личности
        current_emotion = entity['current_emotion']
        intensity = entity['emotion_intensity']
        
        # Эмоции затухают со временем
        intensity *= self.emotion_decay
        
        # Новые эмоции могут возникнуть случайно
        if random.random() < 0.1:  # 10% шанс
            emotion_types = list(EmotionType)
            new_emotion = random.choice(emotion_types)
            new_intensity = random.uniform(0.3, 0.8)
            
            current_emotion = new_emotion
            intensity = new_intensity
        
        entity['current_emotion'] = current_emotion
        entity['emotion_intensity'] = intensity
    
    def _make_decision(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Принятие решения с помощью нейронной сети"""
        if not PYTORCH_AVAILABLE:
            return self._make_basic_decision(entity_id, entity_data)
        
        try:
            # Создаем входные данные для сети
            network_input = self._create_decision_input(entity_id, entity_data)
            
            # Получаем предсказание
            with torch.no_grad():
                input_tensor = torch.FloatTensor(network_input).unsqueeze(0)
                output = self.decision_networks[entity_id](input_tensor)
                action_probs = F.softmax(output, dim=1)
                
                # Выбираем действие
                action_idx = torch.multinomial(action_probs, 1).item()
                
                # Создаем решение
                decision = self._action_idx_to_decision(action_idx, entity_data)
                
                # Сохраняем в истории
                self.entities[entity_id]['last_action'] = decision
                self.entities[entity_id]['decision_history'].append({
                    'action': decision,
                    'timestamp': time.time(),
                    'confidence': action_probs[0][action_idx].item()
                })
                
                self.total_decisions += 1
                return decision
                
        except Exception as e:
            logger.error(f"Ошибка принятия решения для {entity_id}: {e}")
            return self._make_basic_decision(entity_id, entity_data)
    
    def _make_basic_decision(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Базовая логика принятия решений без PyTorch"""
        entity = self.entities[entity_id]
        personality = self.personalities.get(entity_id)
        
        if not personality:
            return {'action': 'idle', 'target': None, 'confidence': 0.5}
        
        # Простые решения на основе личности
        personality_type = personality.type.value
        
        if personality_type == 'curious':
            actions = ['explore', 'investigate', 'learn']
        elif personality_type == 'aggressive':
            actions = ['attack', 'chase', 'threaten']
        elif personality_type == 'defensive':
            actions = ['retreat', 'hide', 'defend']
        elif personality_type == 'social':
            actions = ['approach', 'communicate', 'cooperate']
        else:
            actions = ['idle', 'wander', 'observe']
        
        action = random.choice(actions)
        
        decision = {
            'action': action,
            'target': None,
            'confidence': random.uniform(0.3, 0.8)
        }
        
        entity['last_action'] = decision
        return decision
    
    def _create_decision_input(self, entity_id: str, entity_data: Dict[str, Any]) -> List[float]:
        """Создание входных данных для сети принятия решений"""
        entity = self.entities[entity_id]
        personality = self.personalities.get(entity_id, None)
        
        # Базовые характеристики
        input_data = [
            entity_data.get('health', 100) / 100.0,  # Нормализованное здоровье
            entity_data.get('x', 0) / 100.0,  # Позиция X
            entity_data.get('y', 0) / 100.0,  # Позиция Y
            entity_data.get('speed', 1) / 10.0,  # Скорость
            entity['emotion_intensity'],  # Интенсивность эмоций
            len(self.memories[entity_id]) / 100.0,  # Количество воспоминаний
        ]
        
        # Личностные черты
        if personality:
            for trait_name, trait_value in personality.traits.items():
                input_data.append(trait_value)
        else:
            input_data.extend([0.5] * 5)  # Нейтральные черты
        
        # Эмоциональное состояние
        emotion_vector = [0.0] * len(EmotionType)
        current_emotion = entity['current_emotion']
        emotion_idx = list(EmotionType).index(current_emotion)
        emotion_vector[emotion_idx] = entity['emotion_intensity']
        input_data.extend(emotion_vector)
        
        # Дополняем до нужного размера
        while len(input_data) < 20:
            input_data.append(0.0)
        
        return input_data[:20]
    
    def _create_emotion_input(self, entity_id: str) -> List[float]:
        """Создание входных данных для эмоциональной сети"""
        entity = self.entities[entity_id]
        personality = self.personalities.get(entity_id, None)
        
        input_data = [
            entity['emotion_intensity'],
            len(self.memories[entity_id]) / 100.0,
            entity['data'].get('health', 100) / 100.0,
        ]
        
        # Личностные предпочтения
        if personality:
            for pref_name, pref_value in personality.preferences.items():
                input_data.append(pref_value)
        else:
            input_data.extend([0.5] * 3)
        
        # Недавние события
        recent_memories = self.memories[entity_id][-5:]
        avg_emotional_impact = sum(m.emotional_impact for m in recent_memories) / max(len(recent_memories), 1)
        input_data.append(avg_emotional_impact)
        
        # Дополняем до нужного размера
        while len(input_data) < 10:
            input_data.append(0.0)
        
        return input_data[:10]
    
    def _action_idx_to_decision(self, action_idx: int, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразование индекса действия в решение"""
        actions = [
            {'action': 'idle', 'target': None},
            {'action': 'move', 'target': 'random'},
            {'action': 'explore', 'target': 'nearest_interesting'},
            {'action': 'attack', 'target': 'nearest_enemy'},
            {'action': 'retreat', 'target': 'safe_location'},
            {'action': 'communicate', 'target': 'nearest_friendly'},
            {'action': 'gather', 'target': 'nearest_resource'},
            {'action': 'craft', 'target': 'workbench'}
        ]
        
        if 0 <= action_idx < len(actions):
            decision = actions[action_idx].copy()
            decision['confidence'] = random.uniform(0.6, 0.9)
            return decision
        else:
            return {'action': 'idle', 'target': None, 'confidence': 0.5}
    
    def _store_memory(self, entity_id: str, event_type: str, data: Dict[str, Any]):
        """Сохранение памяти о событии"""
        memory = Memory(
            id=f"{entity_id}_{int(time.time() * 1000)}",
            timestamp=time.time(),
            event_type=event_type,
            data=data,
            emotional_impact=self._calculate_emotional_impact(entity_id, event_type, data),
            importance=self._calculate_importance(entity_id, event_type, data),
            associations=self._find_associations(entity_id, event_type, data)
        )
        
        self.memories[entity_id].append(memory)
        
        # Ограничиваем размер памяти
        if len(self.memories[entity_id]) > self.memory_size:
            self.memories[entity_id].pop(0)
    
    def _calculate_emotional_impact(self, entity_id: str, event_type: str, data: Dict[str, Any]) -> float:
        """Расчет эмоционального воздействия события"""
        personality = self.personalities.get(entity_id)
        if not personality:
            return 0.5
        
        base_impact = 0.5
        
        # Модификаторы на основе личности
        if event_type == 'combat' and 'combat' in personality.traits:
            base_impact *= personality.traits['combat']
        elif event_type == 'social' and 'social' in personality.traits:
            base_impact *= personality.traits['social']
        elif event_type == 'exploration' and 'exploration' in personality.traits:
            base_impact *= personality.traits['exploration']
        
        # Модификаторы на основе данных события
        if 'damage' in data:
            base_impact += data['damage'] / 100.0
        if 'reward' in data:
            base_impact += data['reward'] / 100.0
        
        return max(0.0, min(1.0, base_impact))
    
    def _calculate_importance(self, entity_id: str, event_type: str, data: Dict[str, Any]) -> float:
        """Расчет важности события"""
        base_importance = 0.5
        
        # Важные события
        if event_type in ['death', 'victory', 'defeat', 'level_up']:
            base_importance = 0.9
        elif event_type in ['combat', 'social_interaction']:
            base_importance = 0.7
        elif event_type in ['exploration', 'discovery']:
            base_importance = 0.6
        
        # Модификаторы
        if 'rare' in data and data['rare']:
            base_importance += 0.2
        if 'first_time' in data and data['first_time']:
            base_importance += 0.3
        
        return max(0.0, min(1.0, base_importance))
    
    def _find_associations(self, entity_id: str, event_type: str, data: Dict[str, Any]) -> List[str]:
        """Поиск ассоциаций для события"""
        associations = [event_type]
        
        # Добавляем ассоциации на основе данных
        for key, value in data.items():
            if isinstance(value, str) and len(value) < 20:
                associations.append(f"{key}_{value}")
        
        # Добавляем ассоциации на основе личности
        personality = self.personalities.get(entity_id)
        if personality:
            if event_type == 'combat':
                associations.extend(['aggressive', 'conflict'])
            elif event_type == 'social':
                associations.extend(['cooperation', 'friendship'])
            elif event_type == 'exploration':
                associations.extend(['curiosity', 'discovery'])
        
        return list(set(associations))  # Убираем дубликаты
    
    def _get_context(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Получение контекста для принятия решений"""
        return {
            'position': (entity_data.get('x', 0), entity_data.get('y', 0)),
            'health': entity_data.get('health', 100),
            'surroundings': self._analyze_surroundings(entity_id, entity_data),
            'recent_events': len(self.memories[entity_id][-10:]),
            'emotional_state': self.entities[entity_id]['current_emotion'].value
        }
    
    def _analyze_surroundings(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ окружения"""
        # Простой анализ - в реальной игре здесь была бы логика определения объектов вокруг
        return {
            'nearby_enemies': random.randint(0, 3),
            'nearby_allies': random.randint(0, 2),
            'resources_available': random.randint(0, 5),
            'danger_level': random.uniform(0.0, 1.0)
        }
    
    def _learn_from_experience(self, entity_id: str, decision: Dict[str, Any], 
                              entity_data: Dict[str, Any]):
        """Обучение на основе опыта"""
        if not PYTORCH_AVAILABLE or entity_id not in self.decision_networks:
            return
        
        try:
            # Создаем обучающие данные
            memories = self.memories[entity_id]
            if len(memories) < 10:
                return
            
            # Создаем датасет
            dataset = MemoryDataset(memories)
            if len(dataset) == 0:
                return
            
            # Обучаем сеть
            self.decision_networks[entity_id].train()
            optimizer = self.optimizers[entity_id]
            
            # Простая эпоха обучения
            for i in range(min(10, len(dataset))):
                inputs, targets = dataset[i]
                
                optimizer.zero_grad()
                outputs = self.decision_networks[entity_id](inputs.unsqueeze(0))
                loss = F.cross_entropy(outputs, targets)
                loss.backward()
                optimizer.step()
            
            self.learning_iterations += 1
            logger.debug(f"AI {entity_id} завершил обучение (итерация {self.learning_iterations})")
            
        except Exception as e:
            logger.error(f"Ошибка обучения AI {entity_id}: {e}")
    
    def get_ai_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об AI сущности"""
        if entity_id not in self.entities:
            return None
        
        entity = self.entities[entity_id]
        personality = self.personalities.get(entity_id)
        
        return {
            'state': entity['last_action']['action'] if entity['last_action'] else 'idle',
            'personality': personality.type.value if personality else 'unknown',
            'emotion': entity['current_emotion'].value,
            'emotion_intensity': entity['emotion_intensity'],
            'memory_count': len(self.memories[entity_id]),
            'decision_count': self.total_decisions,
            'learning_iterations': self.learning_iterations,
            'confidence': entity['last_action']['confidence'] if entity['last_action'] else 0.5
        }
    
    def save_generation_memory(self, filename: str):
        """Сохранение памяти поколений"""
        try:
            memory_data = {
                'memories': {k: [asdict(m) for m in v] for k, v in self.memories.items()},
                'emotions': {k: [asdict(e) for e in v] for k, v in self.emotions.items()},
                'personalities': {k: asdict(v) for k, v in self.personalities.items()},
                'statistics': {
                    'total_decisions': self.total_decisions,
                    'successful_decisions': self.successful_decisions,
                    'learning_iterations': self.learning_iterations
                }
            }
            
            with open(f"saves/{filename}_ai_memory.json", 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            # Сохраняем нейронные сети
            if PYTORCH_AVAILABLE:
                for entity_id, network in self.decision_networks.items():
                    torch.save(network.state_dict(), f"saves/{filename}_{entity_id}_decision.pth")
                
                for entity_id, network in self.emotional_networks.items():
                    torch.save(network.state_dict(), f"saves/{filename}_{entity_id}_emotion.pth")
            
            logger.info(f"Память AI сохранена в {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения памяти AI: {e}")
    
    def load_generation_memory(self, filename: str):
        """Загрузка памяти поколений"""
        try:
            with open(f"saves/{filename}_ai_memory.json", 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # Загружаем память
            for entity_id, memories_list in memory_data['memories'].items():
                self.memories[entity_id] = [Memory(**m) for m in memories_list]
            
            # Загружаем эмоции
            for entity_id, emotions_list in memory_data['emotions'].items():
                self.emotions[entity_id] = [Emotion(**e) for e in emotions_list]
            
            # Загружаем личности
            for entity_id, personality_data in memory_data['personalities'].items():
                self.personalities[entity_id] = Personality(**personality_data)
            
            # Загружаем статистику
            stats = memory_data['statistics']
            self.total_decisions = stats['total_decisions']
            self.successful_decisions = stats['successful_decisions']
            self.learning_iterations = stats['learning_iterations']
            
            # Загружаем нейронные сети
            if PYTORCH_AVAILABLE:
                for entity_id in self.decision_networks:
                    try:
                        state_dict = torch.load(f"saves/{filename}_{entity_id}_decision.pth")
                        self.decision_networks[entity_id].load_state_dict(state_dict)
                    except FileNotFoundError:
                        pass
                
                for entity_id in self.emotional_networks:
                    try:
                        state_dict = torch.load(f"saves/{filename}_{entity_id}_emotion.pth")
                        self.emotional_networks[entity_id].load_state_dict(state_dict)
                    except FileNotFoundError:
                        pass
            
            logger.info(f"Память AI загружена из {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки памяти AI: {e}")
    
    def update(self, delta_time: float):
        """Обновление AI системы"""
        # Обновляем эмоции всех сущностей
        for entity_id in list(self.entities.keys()):
            if entity_id in self.entities:
                self._update_emotions(entity_id, delta_time)
    
    def cleanup(self):
        """Очистка AI системы"""
        logger.info("Очистка PyTorch AI системы...")
        
        # Сохраняем память перед выходом
        self.save_generation_memory("final_ai_memory")
        
        # Очищаем данные
        self.entities.clear()
        self.memories.clear()
        self.emotions.clear()
        self.personalities.clear()
        
        if PYTORCH_AVAILABLE:
            self.decision_networks.clear()
            self.emotional_networks.clear()
            self.optimizers.clear()
        
        logger.info("PyTorch AI система очищена")
