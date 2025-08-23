#!/usr/bin/env python3
"""
Система эмоционального влияния на ИИ.
Интегрирует эмоциональные состояния с принятием решений ИИ.
Вдохновлено механиками из Bloodborne и Dark Souls.
"""

import random
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

from .emotion_system import EmotionCode, EmotionIntensity, EmotionalState
from .generational_memory_system import GenerationalMemorySystem, MemoryType

logger = logging.getLogger(__name__)


class EmotionalInfluenceType(Enum):
    """Типы эмоционального влияния"""
    COMBAT_AGGRESSION = "combat_aggression"
    DEFENSIVE_CAUTION = "defensive_caution"
    EXPLORATION_CURIOSITY = "exploration_curiosity"
    SOCIAL_TRUST = "social_trust"
    SURVIVAL_FEAR = "survival_fear"
    EVOLUTIONARY_DRIVE = "evolutionary_drive"
    TACTICAL_PATIENCE = "tactical_patience"
    CREATIVE_ADAPTATION = "creative_adaptation"


@dataclass
class EmotionalModifier:
    """Модификатор эмоционального влияния"""
    emotion_code: str
    influence_type: EmotionalInfluenceType
    strength: float  # 0.0 - 2.0
    duration: float
    decay_rate: float
    target_actions: List[str]
    action_boost: float
    action_penalty: float
    
    def is_active(self, current_time: float) -> bool:
        """Проверка активности модификатора"""
        return current_time < self.duration
    
    def get_current_strength(self, current_time: float) -> float:
        """Получение текущей силы влияния"""
        if not self.is_active(current_time):
            return 0.0
        
        time_elapsed = current_time - (self.duration - self.duration)
        decay_factor = math.exp(-self.decay_rate * time_elapsed)
        return self.strength * decay_factor


@dataclass
class EmotionalAIState:
    """Эмоциональное состояние ИИ"""
    current_emotions: List[str]
    emotional_stability: float
    dominant_influence: Optional[EmotionalInfluenceType]
    emotional_momentum: float
    last_emotion_change: float
    emotional_trauma_level: float
    
    def get_emotional_balance(self) -> float:
        """Получение эмоционального баланса"""
        return max(0.0, min(1.0, self.emotional_stability - self.emotional_trauma_level))


class EmotionalAIInfluenceSystem:
    """Система эмоционального влияния на ИИ"""
    
    def __init__(self, memory_system: GenerationalMemorySystem):
        self.memory_system = memory_system
        
        # Эмоциональные модификаторы
        self.active_modifiers: List[EmotionalModifier] = []
        
        # Эмоциональные состояния ИИ
        self.ai_emotional_states: Dict[str, EmotionalAIState] = {}
        
        # Матрица эмоционального влияния
        self.emotion_influence_matrix = self._init_emotion_influence_matrix()
        
        # Эмоциональные триггеры
        self.emotional_triggers = self._init_emotional_triggers()
        
        logger.info("Система эмоционального влияния на ИИ инициализирована")
    
    def process_emotion_trigger(self, entity_id: str, trigger_type: str, 
                               context: Dict[str, Any], current_time: float):
        """Обработка эмоционального триггера"""
        if trigger_type not in self.emotional_triggers:
            return
        
        trigger = self.emotional_triggers[trigger_type]
        emotion_code = trigger["emotion"]
        intensity = self._calculate_trigger_intensity(trigger, context)
        
        # Создание эмоционального модификатора
        modifier = self._create_emotion_modifier(
            emotion_code, intensity, context, current_time
        )
        
        if modifier:
            self.active_modifiers.append(modifier)
            
            # Обновление эмоционального состояния ИИ
            self._update_ai_emotional_state(entity_id, emotion_code, intensity, current_time)
            
            # Запись в память поколений
            self._record_emotional_experience(entity_id, trigger_type, context, intensity)
            
            logger.debug(f"Эмоциональный триггер {trigger_type} активирован для {entity_id}")
    
    def get_emotionally_influenced_actions(self, entity_id: str, 
                                         available_actions: List[str],
                                         context: Dict[str, Any],
                                         current_time: float) -> Dict[str, float]:
        """Получение действий с эмоциональным влиянием"""
        # Базовые веса действий
        action_weights = {action: 1.0 for action in available_actions}
        
        # Применение эмоциональных модификаторов
        for modifier in self.active_modifiers:
            if not modifier.is_active(current_time):
                continue
            
            current_strength = modifier.get_current_strength(current_time)
            
            # Применение бустов и штрафов
            for action in modifier.target_actions:
                if action in action_weights:
                    if modifier.action_boost > 0:
                        action_weights[action] += current_strength * modifier.action_boost
                    if modifier.action_penalty > 0:
                        action_weights[action] -= current_strength * modifier.action_penalty
        
        # Влияние эмоционального состояния ИИ
        if entity_id in self.ai_emotional_states:
            ai_state = self.ai_emotional_states[entity_id]
            self._apply_ai_emotional_influence(ai_state, action_weights, context)
        
        # Нормализация весов
        total_weight = sum(action_weights.values())
        if total_weight > 0:
            action_weights = {action: weight / total_weight 
                            for action, weight in action_weights.items()}
        
        return action_weights
    
    def _init_emotion_influence_matrix(self) -> Dict[str, Dict[str, float]]:
        """Инициализация матрицы эмоционального влияния"""
        return {
            EmotionCode.FEAR.value: {
                "combat_aggression": -0.5,
                "defensive_caution": 0.8,
                "exploration_curiosity": -0.3,
                "social_trust": -0.4,
                "survival_fear": 0.9,
                "evolutionary_drive": -0.2,
                "tactical_patience": 0.6,
                "creative_adaptation": -0.1
            },
            EmotionCode.RAGE.value: {
                "combat_aggression": 0.9,
                "defensive_caution": -0.6,
                "exploration_curiosity": -0.2,
                "social_trust": -0.8,
                "survival_fear": -0.3,
                "evolutionary_drive": 0.7,
                "tactical_patience": -0.5,
                "creative_adaptation": 0.3
            },
            EmotionCode.TRUST.value: {
                "combat_aggression": -0.2,
                "defensive_caution": -0.3,
                "exploration_curiosity": 0.4,
                "social_trust": 0.8,
                "survival_fear": -0.1,
                "evolutionary_drive": 0.2,
                "tactical_patience": 0.5,
                "creative_adaptation": 0.6
            },
            EmotionCode.CURIOSITY.value: {
                "combat_aggression": 0.1,
                "defensive_caution": -0.2,
                "exploration_curiosity": 0.9,
                "social_trust": 0.3,
                "survival_fear": -0.1,
                "evolutionary_drive": 0.6,
                "tactical_patience": 0.4,
                "creative_adaptation": 0.8
            },
            EmotionCode.CALMNESS.value: {
                "combat_aggression": -0.3,
                "defensive_caution": 0.4,
                "exploration_curiosity": 0.2,
                "social_trust": 0.5,
                "survival_fear": -0.2,
                "evolutionary_drive": 0.1,
                "tactical_patience": 0.8,
                "creative_adaptation": 0.3
            },
            EmotionCode.EXCITEMENT.value: {
                "combat_aggression": 0.6,
                "defensive_caution": -0.4,
                "exploration_curiosity": 0.7,
                "social_trust": 0.2,
                "survival_fear": -0.3,
                "evolutionary_drive": 0.8,
                "tactical_patience": -0.2,
                "creative_adaptation": 0.5
            }
        }
    
    def _init_emotional_triggers(self) -> Dict[str, Dict[str, Any]]:
        """Инициализация эмоциональных триггеров"""
        return {
            "near_death": {
                "emotion": EmotionCode.FEAR.value,
                "base_intensity": 0.8,
                "context_factors": ["health_percent", "enemy_strength"],
                "duration_multiplier": 2.0
            },
            "victory": {
                "emotion": EmotionCode.EXCITEMENT.value,
                "base_intensity": 0.6,
                "context_factors": ["enemy_difficulty", "battle_duration"],
                "duration_multiplier": 1.5
            },
            "defeat": {
                "emotion": EmotionCode.SADNESS.value,
                "base_intensity": 0.7,
                "context_factors": ["progress_lost", "time_invested"],
                "duration_multiplier": 1.8
            },
            "discovery": {
                "emotion": EmotionCode.CURIOSITY.value,
                "base_intensity": 0.5,
                "context_factors": ["item_rarity", "location_danger"],
                "duration_multiplier": 1.2
            },
            "betrayal": {
                "emotion": EmotionCode.DISGUST.value,
                "base_intensity": 0.9,
                "context_factors": ["trust_level", "relationship_duration"],
                "duration_multiplier": 2.5
            },
            "evolution": {
                "emotion": EmotionCode.JOY.value,
                "base_intensity": 0.8,
                "context_factors": ["evolution_stage", "genes_unlocked"],
                "duration_multiplier": 2.0
            },
            "environmental_hazard": {
                "emotion": EmotionCode.FEAR.value,
                "base_intensity": 0.6,
                "context_factors": ["hazard_damage", "escape_difficulty"],
                "duration_multiplier": 1.5
            },
            "social_success": {
                "emotion": EmotionCode.TRUST.value,
                "base_intensity": 0.5,
                "context_factors": ["interaction_quality", "relationship_gain"],
                "duration_multiplier": 1.3
            }
        }
    
    def _calculate_trigger_intensity(self, trigger: Dict[str, Any], 
                                   context: Dict[str, Any]) -> float:
        """Расчёт интенсивности эмоционального триггера"""
        base_intensity = trigger["base_intensity"]
        context_multiplier = 1.0
        
        # Применение контекстных факторов
        for factor in trigger.get("context_factors", []):
            if factor in context:
                factor_value = context[factor]
                if isinstance(factor_value, (int, float)):
                    # Нормализация фактора к диапазону 0.5 - 1.5
                    normalized_factor = max(0.5, min(1.5, factor_value / 100.0))
                    context_multiplier *= normalized_factor
        
        return min(1.0, base_intensity * context_multiplier)
    
    def _create_emotion_modifier(self, emotion_code: str, intensity: float,
                                context: Dict[str, Any], current_time: float) -> Optional[EmotionalModifier]:
        """Создание эмоционального модификатора"""
        if emotion_code not in self.emotion_influence_matrix:
            return None
        
        influence_data = self.emotion_influence_matrix[emotion_code]
        
        # Определение типа влияния
        dominant_influence = max(influence_data.items(), key=lambda x: abs(x[1]))[0]
        
        # Определение целевых действий
        target_actions = self._get_target_actions_for_influence(dominant_influence, context)
        
        # Расчёт бустов и штрафов
        action_boost = max(0.0, influence_data[dominant_influence])
        action_penalty = max(0.0, -influence_data[dominant_influence])
        
        # Длительность и скорость затухания
        base_duration = 30.0  # секунды
        duration = base_duration * intensity
        decay_rate = 0.1 / duration  # Скорость затухания
        
        return EmotionalModifier(
            emotion_code=emotion_code,
            influence_type=EmotionalInfluenceType(dominant_influence),
            strength=intensity,
            duration=current_time + duration,
            decay_rate=decay_rate,
            target_actions=target_actions,
            action_boost=action_boost,
            action_penalty=action_penalty
        )
    
    def _get_target_actions_for_influence(self, influence_type: str, 
                                        context: Dict[str, Any]) -> List[str]:
        """Получение целевых действий для типа влияния"""
        action_mapping = {
            "combat_aggression": ["attack", "charge", "berserk", "intimidate"],
            "defensive_caution": ["defend", "retreat", "hide", "observe"],
            "exploration_curiosity": ["explore", "investigate", "collect", "analyze"],
            "social_trust": ["interact", "trade", "ally", "communicate"],
            "survival_fear": ["flee", "hide", "defend", "use_consumable"],
            "evolutionary_drive": ["evolve", "mutate", "adapt", "learn"],
            "tactical_patience": ["wait", "plan", "observe", "prepare"],
            "creative_adaptation": ["improvise", "combine", "experiment", "innovate"]
        }
        
        return action_mapping.get(influence_type, [])
    
    def _update_ai_emotional_state(self, entity_id: str, emotion_code: str, 
                                  intensity: float, current_time: float):
        """Обновление эмоционального состояния ИИ"""
        if entity_id not in self.ai_emotional_states:
            self.ai_emotional_states[entity_id] = EmotionalAIState(
                current_emotions=[],
                emotional_stability=0.8,
                dominant_influence=None,
                emotional_momentum=0.0,
                last_emotion_change=current_time,
                emotional_trauma_level=0.0
            )
        
        ai_state = self.ai_emotional_states[entity_id]
        
        # Обновление эмоций
        if emotion_code not in ai_state.current_emotions:
            ai_state.current_emotions.append(emotion_code)
        
        # Ограничение количества одновременных эмоций
        if len(ai_state.current_emotions) > 3:
            ai_state.current_emotions.pop(0)
        
        # Обновление эмоциональной стабильности
        if emotion_code in [EmotionCode.FEAR.value, EmotionCode.RAGE.value, EmotionCode.DISGUST.value]:
            ai_state.emotional_stability = max(0.0, ai_state.emotional_stability - intensity * 0.1)
        elif emotion_code in [EmotionCode.CALMNESS.value, EmotionCode.TRUST.value, EmotionCode.JOY.value]:
            ai_state.emotional_stability = min(1.0, ai_state.emotional_stability + intensity * 0.05)
        
        # Обновление травматического уровня
        if emotion_code == EmotionCode.FEAR.value and intensity > 0.7:
            ai_state.emotional_trauma_level = min(1.0, ai_state.emotional_trauma_level + intensity * 0.2)
        
        # Обновление эмоционального импульса
        ai_state.emotional_momentum = (ai_state.emotional_momentum + intensity) / 2
        
        ai_state.last_emotion_change = current_time
    
    def _apply_ai_emotional_influence(self, ai_state: EmotionalAIState,
                                    action_weights: Dict[str, float],
                                    context: Dict[str, Any]):
        """Применение влияния эмоционального состояния ИИ"""
        # Влияние эмоциональной стабильности
        stability_factor = ai_state.emotional_stability
        
        if stability_factor < 0.3:  # Низкая стабильность
            # Увеличение осторожности
            if "defend" in action_weights:
                action_weights["defend"] *= 1.5
            if "retreat" in action_weights:
                action_weights["retreat"] *= 1.3
        
        elif stability_factor > 0.7:  # Высокая стабильность
            # Увеличение агрессивности
            if "attack" in action_weights:
                action_weights["attack"] *= 1.2
            if "explore" in action_weights:
                action_weights["explore"] *= 1.3
        
        # Влияние эмоционального импульса
        momentum_factor = ai_state.emotional_momentum
        
        if momentum_factor > 0.7:  # Высокий импульс
            # Ускорение действий
            for action in action_weights:
                if action in ["attack", "charge", "explore"]:
                    action_weights[action] *= 1.4
        
        # Влияние травматического уровня
        trauma_factor = ai_state.emotional_trauma_level
        
        if trauma_factor > 0.5:  # Высокая травма
            # Увеличение страха и осторожности
            for action in action_weights:
                if action in ["flee", "hide", "defend"]:
                    action_weights[action] *= 1.6
                elif action in ["attack", "charge"]:
                    action_weights[action] *= 0.7
    
    def _record_emotional_experience(self, entity_id: str, trigger_type: str,
                                   context: Dict[str, Any], intensity: float):
        """Запись эмоционального опыта в память поколений"""
        try:
            memory_content = {
                "trigger_type": trigger_type,
                "context": context,
                "intensity": intensity,
                "entity_id": entity_id,
                "timestamp": time.time()
            }
            
            self.memory_system.add_memory(
                memory_type=MemoryType.EMOTIONAL_TRAUMA,
                content=memory_content,
                intensity=intensity,
                emotional_impact=intensity
            )
            
        except Exception as e:
            logger.error(f"Ошибка записи эмоционального опыта: {e}")
    
    def cleanup_expired_modifiers(self, current_time: float):
        """Очистка истёкших модификаторов"""
        self.active_modifiers = [
            modifier for modifier in self.active_modifiers
            if modifier.is_active(current_time)
        ]
    
    def get_emotional_statistics(self, entity_id: str) -> Dict[str, Any]:
        """Получение статистики эмоционального состояния"""
        if entity_id not in self.ai_emotional_states:
            return {}
        
        ai_state = self.ai_emotional_states[entity_id]
        
        return {
            "current_emotions": ai_state.current_emotions,
            "emotional_stability": ai_state.emotional_stability,
            "emotional_momentum": ai_state.emotional_momentum,
            "emotional_trauma_level": ai_state.emotional_trauma_level,
            "active_modifiers": len(self.active_modifiers),
            "emotional_balance": ai_state.get_emotional_balance()
        }
