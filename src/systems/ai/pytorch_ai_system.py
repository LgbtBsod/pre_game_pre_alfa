#!/usr/bin/env python3
"""
PyTorch AI System - Продвинутая система искусственного интеллекта
Расширяет базовую AI систему нейронными сетями PyTorch
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

from .ai_system import AISystem, AIConfig, AIMemory, AIDecision

logger = logging.getLogger(__name__)

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
    
    def __init__(self, memories: List[AIMemory], sequence_length: int = 10):
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

class PyTorchAISystem(AISystem):
    """Продвинутая AI система на основе PyTorch"""
    
    def __init__(self):
        # Инициализируем базовую AI систему
        super().__init__()
        
        # Нейронные сети
        self.decision_networks: Dict[str, NeuralNetwork] = {}
        self.emotional_networks: Dict[str, EmotionalNetwork] = {}
        self.optimizers: Dict[str, optim.Adam] = {}
        
        # Параметры обучения
        self.learning_rate = 0.001
        self.learning_iterations = 0
        
        logger.info("PyTorch AI система инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация PyTorch AI системы"""
        try:
            logger.info("Инициализация PyTorch AI системы...")
            
            # Инициализируем базовую систему
            if not super().initialize():
                return False
            
            if not PYTORCH_AVAILABLE:
                logger.warning("PyTorch недоступен, используется базовая AI система")
            
            logger.info("PyTorch AI система успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации PyTorch AI системы: {e}")
            return False
    
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any], 
                       memory_group: str = "default") -> bool:
        """Регистрация сущности в PyTorch AI системе"""
        try:
            # Регистрируем в базовой системе
            if not super().register_entity(entity_id, entity_data, memory_group):
                return False
            
            # Инициализируем нейронные сети для PyTorch
            if PYTORCH_AVAILABLE:
                self._initialize_networks(entity_id)
            
            logger.info(f"Сущность {entity_id} зарегистрирована в PyTorch AI системе")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации сущности {entity_id}: {e}")
            return False
    
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
        """Обновление AI сущности с использованием нейронных сетей"""
        if entity_id not in self.entities:
            return
        
        try:
            # Обновляем в базовой системе
            super().update_entity(entity_id, entity_data, delta_time)
            
            # Если доступен PyTorch, используем нейронные сети
            if PYTORCH_AVAILABLE and entity_id in self.decision_networks:
                # Принимаем решение с помощью нейронной сети
                decision = self._make_neural_decision(entity_id, entity_data)
                
                # Обновляем решение в базовой системе
                self.entities[entity_id]['last_action'] = decision
                
                # Обучение на основе результата
                if self.learning_enabled:
                    self._learn_from_experience(entity_id, decision, entity_data)
            
        except Exception as e:
            logger.error(f"Ошибка обновления PyTorch AI сущности {entity_id}: {e}")
    
    def _make_neural_decision(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Принятие решения с помощью нейронной сети"""
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
                self.entities[entity_id]['decision_history'].append({
                    'action': decision,
                    'timestamp': time.time(),
                    'confidence': action_probs[0][action_idx].item()
                })
                
                self.total_decisions += 1
                return decision
                
        except Exception as e:
            logger.error(f"Ошибка принятия решения для {entity_id}: {e}")
            return self._make_decision(entity_id, entity_data)
    
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
    
    def save_generation_memory(self, filename: str):
        """Сохранение памяти поколений с нейронными сетями"""
        try:
            # Сохраняем базовую память
            super().save_generation_memory(filename)
            
            # Сохраняем нейронные сети
            if PYTORCH_AVAILABLE:
                for entity_id, network in self.decision_networks.items():
                    torch.save(network.state_dict(), f"saves/{filename}_{entity_id}_decision.pth")
                
                for entity_id, network in self.emotional_networks.items():
                    torch.save(network.state_dict(), f"saves/{filename}_{entity_id}_emotion.pth")
            
            logger.info(f"Память PyTorch AI сохранена в {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения памяти PyTorch AI: {e}")
    
    def load_generation_memory(self, filename: str):
        """Загрузка памяти поколений с нейронными сетями"""
        try:
            # Загружаем базовую память
            super().load_generation_memory(filename)
            
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
            
            logger.info(f"Память PyTorch AI загружена из {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки памяти PyTorch AI: {e}")
    
    def get_ai_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об AI сущности с PyTorch данными"""
        base_info = super().get_ai_info(entity_id)
        if not base_info:
            return None
        
        # Добавляем PyTorch информацию
        if PYTORCH_AVAILABLE:
            base_info.update({
                'pytorch_enabled': True,
                'learning_iterations': self.learning_iterations,
                'has_decision_network': entity_id in self.decision_networks,
                'has_emotion_network': entity_id in self.emotional_networks
            })
        else:
            base_info['pytorch_enabled'] = False
        
        return base_info
    
    def cleanup(self):
        """Очистка PyTorch AI системы"""
        logger.info("Очистка PyTorch AI системы...")
        
        # Сохраняем память перед выходом
        self.save_generation_memory("final_ai_memory")
        
        # Очищаем нейронные сети
        if PYTORCH_AVAILABLE:
            self.decision_networks.clear()
            self.emotional_networks.clear()
            self.optimizers.clear()
        
        # Очищаем базовую систему
        super().cleanup()
        
        logger.info("PyTorch AI система очищена")
