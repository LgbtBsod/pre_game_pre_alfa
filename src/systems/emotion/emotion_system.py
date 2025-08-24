#!/usr/bin/env python3
"""
Система эмоций - управление эмоциональным состоянием сущностей
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import (
    EmotionType, EmotionIntensity, StatType, BASE_STATS,
    PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class Emotion:
    """Эмоция сущности"""
    emotion_id: str
    emotion_type: EmotionType
    intensity: EmotionIntensity
    value: float = 0.0  # -1.0 до 1.0
    duration: float = 0.0  # 0.0 = постоянная
    start_time: float = field(default_factory=time.time)
    source: str = "system"
    target: Optional[str] = None
    decay_rate: float = 0.1  # Скорость затухания в секунду

@dataclass
class EmotionalState:
    """Эмоциональное состояние сущности"""
    entity_id: str
    emotions: List[Emotion] = field(default_factory=list)
    mood: float = 0.0  # Общее настроение (-1.0 до 1.0)
    stress_level: float = 0.0  # Уровень стресса (0.0 до 1.0)
    emotional_stability: float = 0.5  # Эмоциональная стабильность
    last_update: float = field(default_factory=time.time)
    emotional_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class EmotionalTrigger:
    """Триггер эмоции"""
    trigger_id: str
    trigger_type: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    emotion_type: EmotionType
    intensity: EmotionIntensity
    duration: float = 0.0
    probability: float = 1.0
    cooldown: float = 0.0
    last_triggered: float = 0.0

class EmotionSystem(ISystem):
    """Система управления эмоциями"""
    
    def __init__(self):
        self._system_name = "emotions"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Эмоциональные состояния сущностей
        self.emotional_states: Dict[str, EmotionalState] = {}
        
        # Триггеры эмоций
        self.emotional_triggers: List[EmotionalTrigger] = []
        
        # История эмоций
        self.emotion_history: List[Dict[str, Any]] = []
        
        # Настройки системы
        self.system_settings = {
            'max_emotions_per_entity': SYSTEM_LIMITS["max_emotions_per_entity"],
            'emotion_decay_rate': 0.1,
            'mood_update_interval': TIME_CONSTANTS["emotion_update_interval"],
            'stress_decay_rate': 0.05,
            'emotional_stability_range': (0.1, 0.9)
        }
        
        # Статистика системы
        self.system_stats = {
            'entities_with_emotions': 0,
            'total_emotions': 0,
            'emotions_triggered': 0,
            'mood_changes': 0,
            'stress_events': 0,
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
            
            # Настраиваем систему
            self._setup_emotion_system()
            
            # Создаем базовые триггеры эмоций
            self._create_base_triggers()
            
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
            
            # Обновляем эмоциональные состояния
            self._update_emotional_states(delta_time)
            
            # Проверяем триггеры эмоций
            self._check_emotional_triggers(delta_time)
            
            # Обновляем статистику системы
            self._update_system_stats()
            
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
            
            # Очищаем все данные
            self.emotional_states.clear()
            self.emotional_triggers.clear()
            self.emotion_history.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'entities_with_emotions': 0,
                'total_emotions': 0,
                'emotions_triggered': 0,
                'mood_changes': 0,
                'stress_events': 0,
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
            'entities_with_emotions': len(self.emotional_states),
            'emotional_triggers': len(self.emotional_triggers),
            'total_emotions': self.system_stats['total_emotions'],
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "entity_destroyed":
                return self._handle_entity_destroyed(event_data)
            elif event_type == "combat_ended":
                return self._handle_combat_ended(event_data)
            elif event_type == "item_acquired":
                return self._handle_item_acquired(event_data)
            elif event_type == "skill_learned":
                return self._handle_skill_learned(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _setup_emotion_system(self) -> None:
        """Настройка системы эмоций"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система эмоций настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему эмоций: {e}")
    
    def _create_base_triggers(self) -> None:
        """Создание базовых триггеров эмоций"""
        try:
            # Триггеры для боевых событий
            combat_triggers = [
                EmotionalTrigger(
                    trigger_id="victory",
                    trigger_type="combat",
                    conditions={'result': 'victory'},
                    emotion_type=EmotionType.JOY,
                    intensity=EmotionIntensity.MEDIUM,
                    duration=300.0,  # 5 минут
                    probability=0.9
                ),
                EmotionalTrigger(
                    trigger_id="defeat",
                    trigger_type="combat",
                    conditions={'result': 'defeat'},
                    emotion_type=EmotionType.SADNESS,
                    intensity=EmotionIntensity.MEDIUM,
                    duration=600.0,  # 10 минут
                    probability=0.8
                ),
                EmotionalTrigger(
                    trigger_id="critical_hit",
                    trigger_type="combat",
                    conditions={'action': 'critical_hit'},
                    emotion_type=EmotionType.EXCITEMENT,
                    intensity=EmotionIntensity.HIGH,
                    duration=120.0,  # 2 минуты
                    probability=0.7
                )
            ]
            
            # Триггеры для предметов
            item_triggers = [
                EmotionalTrigger(
                    trigger_id="rare_item",
                    trigger_type="item",
                    conditions={'rarity': 'rare'},
                    emotion_type=EmotionType.JOY,
                    intensity=EmotionIntensity.HIGH,
                    duration=1800.0,  # 30 минут
                    probability=0.8
                ),
                EmotionalTrigger(
                    trigger_id="item_lost",
                    trigger_type="item",
                    conditions={'action': 'lost'},
                    emotion_type=EmotionType.SADNESS,
                    intensity=EmotionIntensity.LOW,
                    duration=900.0,  # 15 минут
                    probability=0.6
                )
            ]
            
            # Триггеры для навыков
            skill_triggers = [
                EmotionalTrigger(
                    trigger_id="skill_mastered",
                    trigger_type="skill",
                    conditions={'action': 'mastered'},
                    emotion_type=EmotionType.PRIDE,
                    intensity=EmotionIntensity.HIGH,
                    duration=3600.0,  # 1 час
                    probability=0.9
                ),
                EmotionalTrigger(
                    trigger_id="skill_failed",
                    trigger_type="skill",
                    conditions={'action': 'failed'},
                    emotion_type=EmotionType.FRUSTRATION,
                    intensity=EmotionIntensity.LOW,
                    duration=300.0,  # 5 минут
                    probability=0.5
                )
            ]
            
            # Триггеры для окружения
            environment_triggers = [
                EmotionalTrigger(
                    trigger_id="beautiful_scene",
                    trigger_type="environment",
                    conditions={'scene_type': 'beautiful'},
                    emotion_type=EmotionType.WONDER,
                    intensity=EmotionIntensity.MEDIUM,
                    duration=600.0,  # 10 минут
                    probability=0.6
                ),
                EmotionalTrigger(
                    trigger_id="dangerous_area",
                    trigger_type="environment",
                    conditions={'area_type': 'dangerous'},
                    emotion_type=EmotionType.FEAR,
                    intensity=EmotionIntensity.MEDIUM,
                    duration=300.0,  # 5 минут
                    probability=0.7
                )
            ]
            
            self.emotional_triggers = (
                combat_triggers + item_triggers + skill_triggers + environment_triggers
            )
            
            logger.info(f"Создано {len(self.emotional_triggers)} базовых триггеров эмоций")
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых триггеров эмоций: {e}")
    
    def _update_emotional_states(self, delta_time: float) -> None:
        """Обновление эмоциональных состояний"""
        try:
            current_time = time.time()
            
            for entity_id, emotional_state in self.emotional_states.items():
                # Обновляем время последнего обновления
                emotional_state.last_update = current_time
                
                # Обновляем эмоции
                active_emotions = []
                for emotion in emotional_state.emotions:
                    # Проверяем, не истекла ли эмоция
                    if emotion.duration > 0 and current_time - emotion.start_time > emotion.duration:
                        # Эмоция истекла, будет удалена
                        continue
                    
                    # Применяем затухание
                    if emotion.duration > 0:
                        emotion.value *= (1 - emotion.decay_rate * delta_time)
                        # Ограничиваем значение
                        emotion.value = max(-1.0, min(1.0, emotion.value))
                    
                    active_emotions.append(emotion)
                
                # Обновляем список эмоций
                emotional_state.emotions = active_emotions
                
                # Пересчитываем общее настроение
                self._recalculate_mood(emotional_state)
                
                # Обновляем уровень стресса
                self._update_stress_level(emotional_state, delta_time)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления эмоциональных состояний: {e}")
    
    def _check_emotional_triggers(self, delta_time: float) -> None:
        """Проверка триггеров эмоций"""
        try:
            current_time = time.time()
            
            for trigger in self.emotional_triggers:
                # Проверяем кулдаун
                if current_time - trigger.last_triggered < trigger.cooldown:
                    continue
                
                # Проверяем условия
                if self._check_trigger_conditions(trigger):
                    # Пытаемся активировать триггер
                    if random.random() < trigger.probability:
                        self._activate_emotional_trigger(trigger)
                        trigger.last_triggered = current_time
                
        except Exception as e:
            logger.warning(f"Ошибка проверки триггеров эмоций: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['entities_with_emotions'] = len(self.emotional_states)
            self.system_stats['total_emotions'] = sum(len(state.emotions) for state in self.emotional_states.values())
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            initial_emotions = event_data.get('initial_emotions', [])
            
            if entity_id:
                return self.create_emotional_entity(entity_id, initial_emotions)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                return self.destroy_emotional_entity(entity_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения сущности: {e}")
            return False
    
    def _handle_combat_ended(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события окончания боя"""
        try:
            combat_id = event_data.get('combat_id')
            participants = event_data.get('participants')
            result = event_data.get('result')
            
            if combat_id and participants and result:
                # Применяем эмоции к участникам
                for participant_id in participants:
                    if participant_id in self.emotional_states:
                        if result == "victory":
                            self.add_emotion(participant_id, EmotionType.JOY, EmotionIntensity.MEDIUM, 0.6, 300.0)
                        elif result == "defeat":
                            self.add_emotion(participant_id, EmotionType.SADNESS, EmotionIntensity.MEDIUM, -0.5, 600.0)
                        elif result == "draw":
                            self.add_emotion(participant_id, EmotionType.NEUTRAL, EmotionIntensity.LOW, 0.0, 180.0)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события окончания боя: {e}")
            return False
    
    def _handle_item_acquired(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события получения предмета"""
        try:
            entity_id = event_data.get('entity_id')
            item_rarity = event_data.get('item_rarity')
            
            if entity_id and item_rarity and entity_id in self.emotional_states:
                if item_rarity in ['rare', 'epic', 'legendary']:
                    self.add_emotion(entity_id, EmotionType.JOY, EmotionIntensity.HIGH, 0.8, 1800.0)
                elif item_rarity == 'common':
                    self.add_emotion(entity_id, EmotionType.SATISFACTION, EmotionIntensity.LOW, 0.2, 300.0)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события получения предмета: {e}")
            return False
    
    def _handle_skill_learned(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изучения навыка"""
        try:
            entity_id = event_data.get('entity_id')
            skill_name = event_data.get('skill_name')
            
            if entity_id and skill_name and entity_id in self.emotional_states:
                self.add_emotion(entity_id, EmotionType.PRIDE, EmotionIntensity.MEDIUM, 0.6, 900.0)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события изучения навыка: {e}")
            return False
    
    def create_emotional_entity(self, entity_id: str, initial_emotions: List[Dict[str, Any]] = None) -> bool:
        """Создание сущности для эмоций"""
        try:
            if entity_id in self.emotional_states:
                logger.warning(f"Сущность {entity_id} уже существует в системе эмоций")
                return False
            
            # Создаем эмоциональное состояние
            emotional_state = EmotionalState(
                entity_id=entity_id,
                emotional_stability=random.uniform(*self.system_settings['emotional_stability_range'])
            )
            
            # Добавляем начальные эмоции
            if initial_emotions:
                for emotion_data in initial_emotions:
                    emotion = Emotion(
                        emotion_id=f"initial_{int(time.time() * 1000)}",
                        emotion_type=EmotionType(emotion_data.get('emotion_type', EmotionType.NEUTRAL.value)),
                        intensity=EmotionIntensity(emotion_data.get('intensity', EmotionIntensity.LOW.value)),
                        value=emotion_data.get('value', 0.0),
                        duration=emotion_data.get('duration', 0.0),
                        source=emotion_data.get('source', 'system')
                    )
                    emotional_state.emotions.append(emotion)
            
            # Добавляем в систему
            self.emotional_states[entity_id] = emotional_state
            
            # Пересчитываем настроение
            self._recalculate_mood(emotional_state)
            
            logger.info(f"Создана сущность {entity_id} для эмоций")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания сущности {entity_id} для эмоций: {e}")
            return False
    
    def destroy_emotional_entity(self, entity_id: str) -> bool:
        """Уничтожение сущности из системы эмоций"""
        try:
            if entity_id not in self.emotional_states:
                return False
            
            # Удаляем эмоциональное состояние
            del self.emotional_states[entity_id]
            
            logger.info(f"Сущность {entity_id} удалена из системы эмоций")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления сущности {entity_id} из системы эмоций: {e}")
            return False
    
    def add_emotion(self, entity_id: str, emotion_type: EmotionType, intensity: EmotionIntensity, 
                    value: float, duration: float = 0.0, source: str = "system", target: Optional[str] = None) -> bool:
        """Добавление эмоции сущности"""
        try:
            if entity_id not in self.emotional_states:
                logger.warning(f"Сущность {entity_id} не найдена в системе эмоций")
                return False
            
            emotional_state = self.emotional_states[entity_id]
            
            # Проверяем лимит эмоций
            if len(emotional_state.emotions) >= self.system_settings['max_emotions_per_entity']:
                # Удаляем самую слабую эмоцию
                weakest_emotion = min(emotional_state.emotions, key=lambda e: abs(e.value))
                emotional_state.emotions.remove(weakest_emotion)
            
            # Создаем новую эмоцию
            emotion = Emotion(
                emotion_id=f"emotion_{int(time.time() * 1000)}",
                emotion_type=emotion_type,
                intensity=intensity,
                value=value,
                duration=duration,
                source=source,
                target=target,
                decay_rate=self.system_settings['emotion_decay_rate']
            )
            
            # Добавляем эмоцию
            emotional_state.emotions.append(emotion)
            
            # Пересчитываем настроение
            self._recalculate_mood(emotional_state)
            
            # Записываем в историю
            current_time = time.time()
            self.emotion_history.append({
                'timestamp': current_time,
                'action': 'emotion_added',
                'entity_id': entity_id,
                'emotion_type': emotion_type.value,
                'intensity': intensity.value,
                'value': value,
                'duration': duration,
                'source': source
            })
            
            emotional_state.emotional_history.append({
                'timestamp': current_time,
                'emotion_type': emotion_type.value,
                'intensity': intensity.value,
                'value': value,
                'source': source
            })
            
            self.system_stats['emotions_triggered'] += 1
            logger.debug(f"Добавлена эмоция {emotion_type.value} для {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления эмоции для {entity_id}: {e}")
            return False
    
    def _recalculate_mood(self, emotional_state: EmotionalState) -> None:
        """Пересчет общего настроения"""
        try:
            if not emotional_state.emotions:
                emotional_state.mood = 0.0
                return
            
            # Взвешенная сумма эмоций
            total_weight = 0.0
            weighted_sum = 0.0
            
            for emotion in emotional_state.emotions:
                # Вес зависит от интенсивности и времени
                weight = self._get_emotion_weight(emotion)
                weighted_sum += emotion.value * weight
                total_weight += weight
            
            if total_weight > 0:
                emotional_state.mood = weighted_sum / total_weight
                # Ограничиваем настроение
                emotional_state.mood = max(-1.0, min(1.0, emotional_state.mood))
            
            # Записываем изменение настроения
            if hasattr(emotional_state, '_last_mood'):
                if abs(emotional_state.mood - emotional_state._last_mood) > 0.1:
                    self.system_stats['mood_changes'] += 1
                    emotional_state._last_mood = emotional_state.mood
            else:
                emotional_state._last_mood = emotional_state.mood
                
        except Exception as e:
            logger.warning(f"Ошибка пересчета настроения: {e}")
    
    def _get_emotion_weight(self, emotion: Emotion) -> float:
        """Получение веса эмоции для расчета настроения"""
        try:
            # Базовый вес от интенсивности
            intensity_weights = {
                EmotionIntensity.LOW: 0.5,
                EmotionIntensity.MEDIUM: 1.0,
                EmotionIntensity.HIGH: 1.5,
                EmotionIntensity.EXTREME: 2.0
            }
            
            weight = intensity_weights.get(emotion.intensity, 1.0)
            
            # Корректируем вес по времени
            if emotion.duration > 0:
                time_factor = 1.0 - (time.time() - emotion.start_time) / emotion.duration
                time_factor = max(0.1, time_factor)
                weight *= time_factor
            
            return weight
            
        except Exception as e:
            logger.warning(f"Ошибка расчета веса эмоции: {e}")
            return 1.0
    
    def _update_stress_level(self, emotional_state: EmotionalState, delta_time: float) -> None:
        """Обновление уровня стресса"""
        try:
            # Стресс зависит от отрицательных эмоций
            negative_emotions = [e for e in emotional_state.emotions if e.value < 0]
            
            if negative_emotions:
                # Увеличиваем стресс
                stress_increase = sum(abs(e.value) * 0.1 for e in negative_emotions) * delta_time
                emotional_state.stress_level = min(1.0, emotional_state.stress_level + stress_increase)
            else:
                # Уменьшаем стресс
                stress_decrease = self.system_settings['stress_decay_rate'] * delta_time
                emotional_state.stress_level = max(0.0, emotional_state.stress_level - stress_decrease)
            
            # Корректируем стресс на основе эмоциональной стабильности
            stability_factor = 1.0 - emotional_state.emotional_stability
            emotional_state.stress_level *= (1.0 + stability_factor * 0.5)
            emotional_state.stress_level = min(1.0, emotional_state.stress_level)
            
        except Exception as e:
            logger.warning(f"Ошибка обновления уровня стресса: {e}")
    
    def _check_trigger_conditions(self, trigger: EmotionalTrigger) -> bool:
        """Проверка условий триггера"""
        try:
            # Здесь должна быть логика проверки условий
            # Пока просто возвращаем True для демонстрации
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки условий триггера {trigger.trigger_id}: {e}")
            return False
    
    def _activate_emotional_trigger(self, trigger: EmotionalTrigger) -> None:
        """Активация триггера эмоций"""
        try:
            # Здесь должна быть логика активации триггера
            logger.debug(f"Активирован триггер эмоций {trigger.trigger_id}")
            
        except Exception as e:
            logger.error(f"Ошибка активации триггера {trigger.trigger_id}: {e}")
    
    def get_emotional_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение эмоционального состояния сущности"""
        try:
            if entity_id not in self.emotional_states:
                return None
            
            emotional_state = self.emotional_states[entity_id]
            
            return {
                'entity_id': emotional_state.entity_id,
                'mood': emotional_state.mood,
                'stress_level': emotional_state.stress_level,
                'emotional_stability': emotional_state.emotional_stability,
                'last_update': emotional_state.last_update,
                'emotions_count': len(emotional_state.emotions),
                'active_emotions': [
                    {
                        'emotion_type': emotion.emotion_type.value,
                        'intensity': emotion.intensity.value,
                        'value': emotion.value,
                        'duration': emotion.duration,
                        'source': emotion.source,
                        'target': emotion.target
                    }
                    for emotion in emotional_state.emotions
                ]
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения эмоционального состояния для {entity_id}: {e}")
            return None
    
    def get_emotion_history(self, entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение истории эмоций сущности"""
        try:
            if entity_id not in self.emotional_states:
                return []
            
            emotional_state = self.emotional_states[entity_id]
            
            # Возвращаем последние записи
            return emotional_state.emotional_history[-limit:]
            
        except Exception as e:
            logger.error(f"Ошибка получения истории эмоций для {entity_id}: {e}")
            return []
    
    def remove_emotion(self, entity_id: str, emotion_id: str) -> bool:
        """Удаление эмоции"""
        try:
            if entity_id not in self.emotional_states:
                return False
            
            emotional_state = self.emotional_states[entity_id]
            emotion_to_remove = None
            
            for emotion in emotional_state.emotions:
                if emotion.emotion_id == emotion_id:
                    emotion_to_remove = emotion
                    break
            
            if not emotion_to_remove:
                return False
            
            # Удаляем эмоцию
            emotional_state.emotions.remove(emotion_to_remove)
            
            # Пересчитываем настроение
            self._recalculate_mood(emotional_state)
            
            logger.debug(f"Удалена эмоция {emotion_id} у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления эмоции {emotion_id} у {entity_id}: {e}")
            return False
    
    def set_emotional_stability(self, entity_id: str, stability: float) -> bool:
        """Установка эмоциональной стабильности"""
        try:
            if entity_id not in self.emotional_states:
                return False
            
            # Ограничиваем значение
            stability = max(0.1, min(0.9, stability))
            
            emotional_state = self.emotional_states[entity_id]
            old_stability = emotional_state.emotional_stability
            emotional_state.emotional_stability = stability
            
            logger.debug(f"Эмоциональная стабильность {entity_id} изменена с {old_stability:.2f} на {stability:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки эмоциональной стабильности для {entity_id}: {e}")
            return False
    
    def get_entities_by_mood(self, mood_range: tuple) -> List[str]:
        """Получение сущностей по диапазону настроения"""
        try:
            min_mood, max_mood = mood_range
            entities = []
            
            for entity_id, emotional_state in self.emotional_states.items():
                if min_mood <= emotional_state.mood <= max_mood:
                    entities.append(entity_id)
            
            return entities
            
        except Exception as e:
            logger.error(f"Ошибка получения сущностей по настроению: {e}")
            return []
    
    def get_entities_by_stress(self, stress_range: tuple) -> List[str]:
        """Получение сущностей по диапазону стресса"""
        try:
            min_stress, max_stress = stress_range
            entities = []
            
            for entity_id, emotional_state in self.emotional_states.items():
                if min_stress <= emotional_state.stress_level <= max_stress:
                    entities.append(entity_id)
            
            return entities
            
        except Exception as e:
            logger.error(f"Ошибка получения сущностей по стрессу: {e}")
            return []
    
    def force_emotion(self, entity_id: str, emotion_type: EmotionType, intensity: EmotionIntensity, 
                     value: float, duration: float = 0.0) -> bool:
        """Принудительное добавление эмоции"""
        try:
            return self.add_emotion(entity_id, emotion_type, intensity, value, duration, "forced")
        except Exception as e:
            logger.error(f"Ошибка принудительного добавления эмоции для {entity_id}: {e}")
            return False
    
    def clear_emotions(self, entity_id: str) -> bool:
        """Очистка всех эмоций сущности"""
        try:
            if entity_id not in self.emotional_states:
                return False
            
            emotional_state = self.emotional_states[entity_id]
            emotional_state.emotions.clear()
            
            # Пересчитываем настроение
            self._recalculate_mood(emotional_state)
            
            logger.debug(f"Очищены все эмоции у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки эмоций у {entity_id}: {e}")
            return False
