#!/usr/bin/env python3
"""
Система эмоций - управление эмоциональным состоянием сущностей для влияния на поведение AI
"""

import logging
import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState

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

class EmotionSystem(ISystem):
    """Система управления эмоциями для всех сущностей"""
    
    def __init__(self):
        self._system_name = "emotion"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Системы эмоций для сущностей
        self.emotion_systems: Dict[str, 'EntityEmotionSystem'] = {}
        
        # Глобальные эмоциональные события
        self.global_emotions: List[Dict[str, Any]] = []
        
        # Эмоциональные паттерны
        self.emotion_patterns: Dict[str, Dict[str, Any]] = {}
        
        # Статистика системы
        self.system_stats = {
            'entities_count': 0,
            'emotions_triggered': 0,
            'active_emotions': 0,
            'update_time': 0.0
        }
        
        logger.info("Система эмоций инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы эмоций"""
        try:
            logger.info("Инициализация системы эмоций...")
            
            # Инициализируем эмоциональные паттерны
            self._initialize_emotion_patterns()
            
            # Загружаем сохраненные эмоции
            self._load_saved_emotions()
            
            self._system_state = SystemState.READY
            logger.info("Система эмоций успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы эмоций: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы эмоций"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем все системы эмоций сущностей
            self._update_all_entity_emotions(delta_time)
            
            # Обрабатываем глобальные эмоции
            self._process_global_emotions(delta_time)
            
            # Обновляем статистику системы
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы эмоций: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы эмоций"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система эмоций приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы эмоций: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы эмоций"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система эмоций возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы эмоций: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы эмоций"""
        try:
            logger.info("Очистка системы эмоций...")
            
            # Сохраняем эмоции перед очисткой
            self._save_emotions()
            
            # Очищаем все данные
            self.emotion_systems.clear()
            self.global_emotions.clear()
            self.emotion_patterns.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'entities_count': 0,
                'emotions_triggered': 0,
                'active_emotions': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система эмоций очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы эмоций: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'entities_count': len(self.emotion_systems),
            'global_emotions_count': len(self.global_emotions),
            'active_emotions': self.system_stats['active_emotions'],
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "emotion_triggered":
                return self._handle_emotion_triggered(event_data)
            elif event_type == "emotion_removed":
                return self._handle_emotion_removed(event_data)
            elif event_type == "global_emotion_event":
                return self._handle_global_emotion_event(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def get_emotion_system(self, entity_id: str) -> 'EntityEmotionSystem':
        """Получает или создает систему эмоций для сущности"""
        if entity_id not in self.emotion_systems:
            self.emotion_systems[entity_id] = EntityEmotionSystem(entity_id)
            self.system_stats['entities_count'] = len(self.emotion_systems)
        
        return self.emotion_systems[entity_id]
    
    def add_emotion_to_entity(self, entity_id: str, emotion_type: EmotionType, 
                             intensity: float, duration: float, source: str = "unknown") -> bool:
        """Добавляет эмоцию к сущности"""
        try:
            emotion_system = self.get_emotion_system(entity_id)
            emotion_system.add_emotion(emotion_type, intensity, duration, source)
            
            # Обновляем статистику
            self.system_stats['emotions_triggered'] += 1
            self.system_stats['active_emotions'] = sum(
                len(es.current_emotions) for es in self.emotion_systems.values()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления эмоции к сущности {entity_id}: {e}")
            return False
    
    def get_entity_behavior_modifiers(self, entity_id: str) -> Dict[str, float]:
        """Получает модификаторы поведения для сущности"""
        try:
            emotion_system = self.get_emotion_system(entity_id)
            return emotion_system.get_behavior_modifiers()
        except Exception as e:
            logger.error(f"Ошибка получения модификаторов поведения для {entity_id}: {e}")
            return {}
    
    def trigger_global_emotion(self, emotion_type: EmotionType, intensity: float, 
                              duration: float, source: str = "global") -> bool:
        """Запускает глобальное эмоциональное событие"""
        try:
            global_emotion = {
                'type': emotion_type,
                'intensity': intensity,
                'duration': duration,
                'start_time': time.time(),
                'source': source,
                'affected_entities': []
            }
            
            self.global_emotions.append(global_emotion)
            
            # Применяем к всем сущностям
            for entity_id in self.emotion_systems:
                self.add_emotion_to_entity(entity_id, emotion_type, intensity * 0.5, duration, source)
                global_emotion['affected_entities'].append(entity_id)
            
            logger.info(f"Глобальная эмоция {emotion_type.value} запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска глобальной эмоции: {e}")
            return False
    
    def _initialize_emotion_patterns(self) -> None:
        """Инициализация эмоциональных паттернов"""
        try:
            # Паттерны для разных типов событий
            self.emotion_patterns = {
                'combat_victory': {
                    'primary': EmotionType.JOY,
                    'secondary': EmotionType.SURPRISE,
                    'intensity_range': (0.6, 0.9),
                    'duration_range': (30.0, 120.0)
                },
                'combat_defeat': {
                    'primary': EmotionType.SADNESS,
                    'secondary': EmotionType.FEAR,
                    'intensity_range': (0.5, 0.8),
                    'duration_range': (60.0, 300.0)
                },
                'discovery': {
                    'primary': EmotionType.SURPRISE,
                    'secondary': EmotionType.JOY,
                    'intensity_range': (0.4, 0.7),
                    'duration_range': (20.0, 60.0)
                },
                'danger': {
                    'primary': EmotionType.FEAR,
                    'secondary': EmotionType.ANGER,
                    'intensity_range': (0.7, 1.0),
                    'duration_range': (10.0, 60.0)
                }
            }
            
            logger.debug("Эмоциональные паттерны инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать эмоциональные паттерны: {e}")
    
    def _update_all_entity_emotions(self, delta_time: float) -> None:
        """Обновление всех систем эмоций сущностей"""
        try:
            for emotion_system in self.emotion_systems.values():
                emotion_system.update(delta_time)
                
            # Обновляем статистику активных эмоций
            self.system_stats['active_emotions'] = sum(
                len(es.current_emotions) for es in self.emotion_systems.values()
            )
            
        except Exception as e:
            logger.warning(f"Ошибка обновления эмоций сущностей: {e}")
    
    def _process_global_emotions(self, delta_time: float) -> None:
        """Обработка глобальных эмоций"""
        try:
            current_time = time.time()
            
            # Удаляем истекшие глобальные эмоции
            self.global_emotions = [
                ge for ge in self.global_emotions 
                if current_time - ge['start_time'] < ge['duration']
            ]
            
        except Exception as e:
            logger.warning(f"Ошибка обработки глобальных эмоций: {e}")
    
    def _save_emotions(self) -> None:
        """Сохранение эмоций"""
        try:
            # Здесь можно добавить логику сохранения эмоций
            pass
        except Exception as e:
            logger.warning(f"Не удалось сохранить эмоции: {e}")
    
    def _load_saved_emotions(self) -> None:
        """Загрузка сохраненных эмоций"""
        try:
            # Здесь можно добавить логику загрузки эмоций
            pass
        except Exception as e:
            logger.warning(f"Не удалось загрузить сохраненные эмоции: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                # Создаем систему эмоций для новой сущности
                self.get_emotion_system(entity_id)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_emotion_triggered(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события запуска эмоции"""
        try:
            entity_id = event_data.get('entity_id')
            emotion_type = EmotionType(event_data.get('emotion_type', 'neutral'))
            intensity = event_data.get('intensity', 0.5)
            duration = event_data.get('duration', 60.0)
            source = event_data.get('source', 'unknown')
            
            if entity_id and emotion_type:
                return self.add_emotion_to_entity(entity_id, emotion_type, intensity, duration, source)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события запуска эмоции: {e}")
            return False
    
    def _handle_emotion_removed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события удаления эмоции"""
        try:
            entity_id = event_data.get('entity_id')
            emotion_type = EmotionType(event_data.get('emotion_type', 'neutral'))
            
            if entity_id and emotion_type:
                emotion_system = self.get_emotion_system(entity_id)
                emotion_system.remove_emotion(emotion_type)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события удаления эмоции: {e}")
            return False
    
    def _handle_global_emotion_event(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события глобального эмоционального события"""
        try:
            emotion_type = EmotionType(event_data.get('emotion_type', 'neutral'))
            intensity = event_data.get('intensity', 0.5)
            duration = event_data.get('duration', 60.0)
            source = event_data.get('source', 'global')
            
            return self.trigger_global_emotion(emotion_type, intensity, duration, source)
            
        except Exception as e:
            logger.error(f"Ошибка обработки события глобального эмоционального события: {e}")
            return False

class EntityEmotionSystem:
    """Система эмоций для конкретной сущности"""
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityEmotionSystem':
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
