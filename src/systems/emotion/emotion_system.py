#!/usr/bin/env python3
"""
Emotion System - Система эмоций для влияния на поведение AI
"""

import logging
import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class EmotionType(Enum):
    """Типы эмоций"""
    JOY = "joy"           # Радость
    SADNESS = "sadness"   # Печаль
    ANGER = "anger"       # Гнев
    FEAR = "fear"         # Страх
    SURPRISE = "surprise" # Удивление
    DISGUST = "disgust"   # Отвращение
    NEUTRAL = "neutral"   # Нейтральное состояние

@dataclass
class Emotion:
    """Эмоция"""
    type: EmotionType
    intensity: float  # 0.0 - 1.0
    duration: float   # Время действия в секундах
    start_time: float
    source: str       # Источник эмоции
    
    def is_active(self, current_time: float) -> bool:
        """Проверяет, активна ли эмоция"""
        return current_time - self.start_time < self.duration
    
    def get_remaining_time(self, current_time: float) -> float:
        """Возвращает оставшееся время действия эмоции"""
        elapsed = current_time - self.start_time
        return max(0.0, self.duration - elapsed)

class EmotionSystem:
    """Система эмоций для сущности"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.current_emotions: List[Emotion] = []
        self.base_mood = EmotionType.NEUTRAL
        self.emotion_history: List[Dict[str, Any]] = []
        
        # Модификаторы поведения от эмоций
        self.behavior_modifiers = {
            EmotionType.JOY: {
                'aggression': -0.2,
                'caution': -0.1,
                'social': 0.3,
                'learning_rate': 0.1
            },
            EmotionType.SADNESS: {
                'aggression': -0.3,
                'caution': 0.2,
                'social': -0.2,
                'learning_rate': -0.1
            },
            EmotionType.ANGER: {
                'aggression': 0.4,
                'caution': -0.3,
                'social': -0.2,
                'learning_rate': 0.05
            },
            EmotionType.FEAR: {
                'aggression': -0.2,
                'caution': 0.4,
                'social': -0.1,
                'learning_rate': 0.15
            },
            EmotionType.SURPRISE: {
                'aggression': 0.1,
                'caution': 0.2,
                'social': 0.1,
                'learning_rate': 0.2
            },
            EmotionType.DISGUST: {
                'aggression': 0.1,
                'caution': 0.3,
                'social': -0.3,
                'learning_rate': -0.05
            },
            EmotionType.NEUTRAL: {
                'aggression': 0.0,
                'caution': 0.0,
                'social': 0.0,
                'learning_rate': 0.0
            }
        }
    
    def add_emotion(self, emotion_type: EmotionType, intensity: float, duration: float, source: str = "unknown"):
        """Добавляет эмоцию"""
        current_time = time.time()
        
        # Создаем новую эмоцию
        emotion = Emotion(
            type=emotion_type,
            intensity=intensity,
            duration=duration,
            start_time=current_time,
            source=source
        )
        
        # Добавляем в список активных эмоций
        self.current_emotions.append(emotion)
        
        # Записываем в историю
        self.emotion_history.append({
            'type': emotion_type.value,
            'intensity': intensity,
            'duration': duration,
            'source': source,
            'timestamp': current_time
        })
        
        logger.info(f"Эмоция {emotion_type.value} (интенсивность: {intensity:.2f}) добавлена для {self.entity_id}")
    
    def remove_emotion(self, emotion_type: EmotionType):
        """Удаляет эмоцию"""
        self.current_emotions = [e for e in self.current_emotions if e.type != emotion_type]
    
    def clear_emotions(self):
        """Очищает все эмоции"""
        self.current_emotions.clear()
    
    def get_dominant_emotion(self, current_time: float = None) -> Optional[Emotion]:
        """Возвращает доминирующую эмоцию"""
        if current_time is None:
            current_time = time.time()
        
        # Фильтруем активные эмоции
        active_emotions = [e for e in self.current_emotions if e.is_active(current_time)]
        
        if not active_emotions:
            return None
        
        # Возвращаем эмоцию с наибольшей интенсивностью
        return max(active_emotions, key=lambda e: e.intensity)
    
    def get_behavior_modifiers(self, current_time: float = None) -> Dict[str, float]:
        """Возвращает модификаторы поведения от текущих эмоций"""
        if current_time is None:
            current_time = time.time()
        
        dominant_emotion = self.get_dominant_emotion(current_time)
        
        if dominant_emotion is None:
            return self.behavior_modifiers[EmotionType.NEUTRAL]
        
        # Получаем базовые модификаторы для доминирующей эмоции
        base_modifiers = self.behavior_modifiers[dominant_emotion.type].copy()
        
        # Применяем интенсивность эмоции
        intensity_factor = dominant_emotion.intensity
        for key in base_modifiers:
            base_modifiers[key] *= intensity_factor
        
        return base_modifiers
    
    def get_emotion_summary(self, current_time: float = None) -> Dict[str, Any]:
        """Возвращает сводку эмоций"""
        if current_time is None:
            current_time = time.time()
        
        dominant_emotion = self.get_dominant_emotion(current_time)
        active_emotions = [e for e in self.current_emotions if e.is_active(current_time)]
        
        return {
            'dominant_emotion': dominant_emotion.type.value if dominant_emotion else 'neutral',
            'dominant_intensity': dominant_emotion.intensity if dominant_emotion else 0.0,
            'active_emotions_count': len(active_emotions),
            'behavior_modifiers': self.get_behavior_modifiers(current_time)
        }
    
    def update(self, delta_time: float):
        """Обновляет систему эмоций"""
        current_time = time.time()
        
        # Удаляем истекшие эмоции
        self.current_emotions = [e for e in self.current_emotions if e.is_active(current_time)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Сохранение системы эмоций"""
        return {
            'entity_id': self.entity_id,
            'base_mood': self.base_mood.value,
            'current_emotions': [
                {
                    'type': e.type.value,
                    'intensity': e.intensity,
                    'duration': e.duration,
                    'start_time': e.start_time,
                    'source': e.source
                }
                for e in self.current_emotions
            ],
            'emotion_history': self.emotion_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionSystem':
        """Загрузка системы эмоций"""
        emotion_system = cls(data['entity_id'])
        emotion_system.base_mood = EmotionType(data['base_mood'])
        
        # Восстанавливаем текущие эмоции
        for emotion_data in data.get('current_emotions', []):
            emotion = Emotion(
                type=EmotionType(emotion_data['type']),
                intensity=emotion_data['intensity'],
                duration=emotion_data['duration'],
                start_time=emotion_data['start_time'],
                source=emotion_data['source']
            )
            emotion_system.current_emotions.append(emotion)
        
        emotion_system.emotion_history = data.get('emotion_history', [])
        return emotion_system

class EmotionManager:
    """Менеджер эмоций для всех сущностей"""
    
    def __init__(self):
        self.emotion_systems: Dict[str, EmotionSystem] = {}
        
        logger.info("Emotion Manager инициализирован")
    
    def get_emotion_system(self, entity_id: str) -> EmotionSystem:
        """Получает или создает систему эмоций для сущности"""
        if entity_id not in self.emotion_systems:
            self.emotion_systems[entity_id] = EmotionSystem(entity_id)
        
        return self.emotion_systems[entity_id]
    
    def add_emotion_to_entity(self, entity_id: str, emotion_type: EmotionType, 
                             intensity: float, duration: float, source: str = "unknown"):
        """Добавляет эмоцию к сущности"""
        emotion_system = self.get_emotion_system(entity_id)
        emotion_system.add_emotion(emotion_type, intensity, duration, source)
    
    def get_entity_behavior_modifiers(self, entity_id: str) -> Dict[str, float]:
        """Получает модификаторы поведения для сущности"""
        emotion_system = self.get_emotion_system(entity_id)
        return emotion_system.get_behavior_modifiers()
    
    def update_all(self, delta_time: float):
        """Обновляет все системы эмоций"""
        for emotion_system in self.emotion_systems.values():
            emotion_system.update(delta_time)

# Глобальный менеджер эмоций
emotion_manager = EmotionManager()
