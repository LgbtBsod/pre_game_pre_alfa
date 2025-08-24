#!/usr/bin/env python3
"""
AI System - Базовая система искусственного интеллекта
Отвечает только за базовую логику AI, эмоции и память
"""

import logging
import json
import random
import math
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
from ...core.interfaces import ISystem

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

class AISystem(ISystem):
    """Базовая AI система"""
    
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.memories: Dict[str, List[Memory]] = defaultdict(list)
        self.emotions: Dict[str, List[Emotion]] = defaultdict(list)
        self.personalities: Dict[str, Personality] = {}
        
        # Параметры
        self.memory_size = 1000
        self.emotion_decay = 0.95
        self.learning_enabled = True
        
        # Статистика
        self.total_decisions = 0
        self.successful_decisions = 0
        
        logger.info("Базовая AI система инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация AI системы"""
        try:
            logger.info("Инициализация базовой AI системы...")
            logger.info("Базовая AI система успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации базовой AI системы: {e}")
            return False
    
    def register_entity(self, entity_id: str, entity_data: Dict[str, Any], 
                       memory_group: str = "default") -> bool:
        """Регистрация сущности в AI системе"""
        try:
            # Создаем личность для сущности
            personality = self._create_personality(entity_data.get('ai_personality', 'curious'))
            self.personalities[entity_id] = personality
            
            # Сохраняем данные сущности
            self.entities[entity_id] = {
                'data': entity_data,
                'memory_group': memory_group,
                'last_action': None,
                'current_emotion': EmotionType.NEUTRAL,
                'emotion_intensity': 0.0,
                'decision_history': deque(maxlen=100)
            }
            
            logger.info(f"Сущность {entity_id} зарегистрирована в базовой AI системе")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации сущности {entity_id}: {e}")
            return False
    
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
            
        except Exception as e:
            logger.error(f"Ошибка обновления AI сущности {entity_id}: {e}")
    
    def _update_emotions(self, entity_id: str, delta_time: float):
        """Обновление эмоционального состояния"""
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
        """Принятие решения"""
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
                    'successful_decisions': self.successful_decisions
                }
            }
            
            with open(f"saves/{filename}_ai_memory.json", 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
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
        logger.info("Очистка базовой AI системы...")
        
        # Сохраняем память перед выходом
        self.save_generation_memory("final_ai_memory")
        
        # Очищаем данные
        self.entities.clear()
        self.memories.clear()
        self.emotions.clear()
        self.personalities.clear()
        
        logger.info("Базовая AI система очищена")
