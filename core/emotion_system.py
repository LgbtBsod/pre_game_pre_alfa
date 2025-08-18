"""
Эмоциональная система с резонансом и комбинациями эмоций.
Управляет эмоциональными состояниями и их влиянием на характеристики.
"""

import random
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from .effect_system import EffectCode, EffectDatabase

logger = logging.getLogger(__name__)


class EmotionCode(Enum):
    """Кодовые идентификаторы эмоций"""
    # Базовые эмоции
    FEAR = "EMO_101"
    RAGE = "EMO_102"
    TRUST = "EMO_103"
    CURIOSITY = "EMO_104"
    CALMNESS = "EMO_105"
    EXCITEMENT = "EMO_106"
    SADNESS = "EMO_107"
    JOY = "EMO_108"
    SURPRISE = "EMO_109"
    DISGUST = "EMO_110"
    
    # Комплексные эмоции
    PANIC = "EMO_201"  # Страх + Гнев
    EXPLORATION_FERVOR = "EMO_202"  # Доверие + Любопытство
    BATTLE_FURY = "EMO_203"  # Гнев + Возбуждение
    MEDITATIVE_STATE = "EMO_204"  # Спокойствие + Доверие
    PARANOIA = "EMO_205"  # Страх + Недоверие


class EmotionIntensity(Enum):
    """Уровни интенсивности эмоций"""
    SUBTLE = 0.25
    MILD = 0.5
    MODERATE = 0.75
    STRONG = 1.0
    INTENSE = 1.5
    OVERWHELMING = 2.0


@dataclass
class Emotion:
    """Эмоция с кодовым идентификатором"""
    code: str
    name: str
    description: str
    base_intensity: float
    duration: float
    effects: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    synergies: List[str] = field(default_factory=list)


@dataclass
class EmotionalState:
    """Эмоциональное состояние сущности"""
    primary_emotion: Optional[str] = None
    secondary_emotions: List[str] = field(default_factory=list)
    emotional_stability: float = 0.8
    resonance_level: float = 0.0
    emotional_memory: Dict[str, float] = field(default_factory=dict)
    
    def get_dominant_emotion(self) -> Optional[str]:
        """Получение доминирующей эмоции"""
        if self.primary_emotion:
            return self.primary_emotion
        elif self.secondary_emotions:
            return max(self.secondary_emotions, 
                      key=lambda e: self.emotional_memory.get(e, 0.0))
        return None
    
    def get_emotional_balance(self) -> float:
        """Расчёт эмоционального баланса"""
        if not self.emotional_memory:
            return 0.5
        
        positive_emotions = ["joy", "trust", "curiosity", "calmness"]
        negative_emotions = ["fear", "rage", "sadness", "disgust"]
        
        positive_score = sum(self.emotional_memory.get(e, 0.0) 
                           for e in positive_emotions)
        negative_score = sum(self.emotional_memory.get(e, 0.0) 
                           for e in negative_emotions)
        
        total = positive_score + negative_score
        if total == 0:
            return 0.5
        
        return positive_score / total


class AdvancedEmotionSystem:
    """Продвинутая эмоциональная система"""
    
    def __init__(self, effect_db: EffectDatabase):
        self.effect_db = effect_db
        self.current_state = EmotionalState()
        self.emotion_history: List[Dict[str, Any]] = []
        self.emotional_resonance: Dict[str, float] = {}
        
        # Комбинации эмоций
        self.emotion_combos = {
            (EmotionCode.FEAR.value, EmotionCode.RAGE.value): {
                "result": EmotionCode.PANIC.value,
                "chance": 0.8,
                "description": "Страх + Гнев = Паника (+30% урон, -30% защита)",
                "effects": [EffectCode.DAMAGE_BOOST.value, "DEFENSE_REDUCTION"]
            },
            (EmotionCode.TRUST.value, EmotionCode.CURIOSITY.value): {
                "result": EmotionCode.EXPLORATION_FERVOR.value,
                "chance": 0.9,
                "description": "Доверие + Любопытство = Исследовательский азарт",
                "effects": [EffectCode.SPEED_BOOST.value, "EXPLORATION_BOOST"]
            },
            (EmotionCode.RAGE.value, EmotionCode.EXCITEMENT.value): {
                "result": EmotionCode.BATTLE_FURY.value,
                "chance": 0.7,
                "description": "Гнев + Возбуждение = Боевая ярость",
                "effects": [EffectCode.DAMAGE_BOOST.value, EffectCode.SPEED_BOOST.value]
            },
            (EmotionCode.CALMNESS.value, EmotionCode.TRUST.value): {
                "result": EmotionCode.MEDITATIVE_STATE.value,
                "chance": 0.6,
                "description": "Спокойствие + Доверие = Медитативное состояние",
                "effects": ["DEFENSE_BOOST", "HEALING_BOOST"]
            },
            (EmotionCode.FEAR.value, EmotionCode.DISGUST.value): {
                "result": EmotionCode.PARANOIA.value,
                "chance": 0.5,
                "description": "Страх + Отвращение = Паранойя",
                "effects": ["DETECTION_BOOST", "SPEED_REDUCTION"]
            }
        }
        
        # Эмоциональные паттерны
        self.emotional_patterns = {
            "aggressive": [EmotionCode.RAGE.value, EmotionCode.EXCITEMENT.value],
            "defensive": [EmotionCode.FEAR.value, EmotionCode.CALMNESS.value],
            "explorative": [EmotionCode.CURIOSITY.value, EmotionCode.TRUST.value],
            "social": [EmotionCode.TRUST.value, EmotionCode.JOY.value],
            "cautious": [EmotionCode.FEAR.value, EmotionCode.CURIOSITY.value]
        }
        
        # Инициализация базовых эмоций
        self._init_base_emotions()
    
    def _init_base_emotions(self):
        """Инициализация базовых эмоций"""
        base_emotions = [
            Emotion(EmotionCode.FEAR.value, "Страх", "Чувство опасности", 0.7, 10.0),
            Emotion(EmotionCode.RAGE.value, "Гнев", "Сильное раздражение", 0.8, 15.0),
            Emotion(EmotionCode.TRUST.value, "Доверие", "Вера в надёжность", 0.6, 20.0),
            Emotion(EmotionCode.CURIOSITY.value, "Любопытство", "Желание узнать", 0.5, 0.0),
            Emotion(EmotionCode.CALMNESS.value, "Спокойствие", "Внутреннее равновесие", 0.5, 25.0),
            Emotion(EmotionCode.EXCITEMENT.value, "Возбуждение", "Повышенная активность", 0.7, 12.0),
            Emotion(EmotionCode.SADNESS.value, "Грусть", "Печальное настроение", 0.6, 18.0),
            Emotion(EmotionCode.JOY.value, "Радость", "Положительные эмоции", 0.6, 20.0),
            Emotion(EmotionCode.SURPRISE.value, "Удивление", "Неожиданность", 0.8, 5.0),
            Emotion(EmotionCode.DISGUST.value, "Отвращение", "Сильное неприятие", 0.7, 8.0)
        ]
        
        # Добавление эмоций в систему
        for emotion in base_emotions:
            self._add_emotion(emotion)
    
    def _add_emotion(self, emotion: Emotion):
        """Добавление эмоции в систему"""
        # Здесь можно добавить логику сохранения эмоций в БД
        pass
    
    def trigger_emotion(self, emotion_code: str, intensity: float = 1.0, 
                       source: str = "unknown") -> bool:
        """Триггер эмоции"""
        try:
            # Проверка существования эмоции
            if not self._is_valid_emotion(emotion_code):
                logger.warning(f"Неизвестная эмоция: {emotion_code}")
                return False
            
            # Применение эмоции
            if self._apply_emotion(emotion_code, intensity, source):
                # Запись в историю
                self.emotion_history.append({
                    "emotion_code": emotion_code,
                    "intensity": intensity,
                    "source": source,
                    "timestamp": 0.0,  # Здесь будет время игры
                    "action": "triggered"
                })
                
                # Обновление эмоциональной памяти
                self._update_emotional_memory(emotion_code, intensity)
                
                # Проверка комбинаций эмоций
                self._check_emotion_combos()
                
                logger.info(f"Триггер эмоции {emotion_code} с интенсивностью {intensity}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка триггера эмоции {emotion_code}: {e}")
            return False
    
    def _is_valid_emotion(self, emotion_code: str) -> bool:
        """Проверка валидности эмоции"""
        return emotion_code in [e.value for e in EmotionCode]
    
    def _apply_emotion(self, emotion_code: str, intensity: float, source: str) -> bool:
        """Применение эмоции"""
        try:
            # Определение типа эмоции
            if emotion_code in [EmotionCode.FEAR.value, EmotionCode.RAGE.value, 
                              EmotionCode.SADNESS.value, EmotionCode.DISGUST.value]:
                emotion_type = "negative"
            elif emotion_code in [EmotionCode.JOY.value, EmotionCode.TRUST.value, 
                                EmotionCode.CURIOSITY.value, EmotionCode.CALMNESS.value]:
                emotion_type = "positive"
            else:
                emotion_type = "neutral"
            
            # Применение эффекта эмоции
            effect_code = self._get_emotion_effect(emotion_code, intensity)
            if effect_code:
                # Здесь будет применение эффекта через систему эффектов
                pass
            
            # Обновление эмоционального состояния
            if not self.current_state.primary_emotion:
                self.current_state.primary_emotion = emotion_code
            elif emotion_code not in self.current_state.secondary_emotions:
                self.current_state.secondary_emotions.append(emotion_code)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка применения эмоции {emotion_code}: {e}")
            return False
    
    def _get_emotion_effect(self, emotion_code: str, intensity: float) -> Optional[str]:
        """Получение эффекта эмоции"""
        emotion_effects = {
            EmotionCode.FEAR.value: EffectCode.FEAR.value,
            EmotionCode.RAGE.value: EffectCode.RAGE.value,
            EmotionCode.TRUST.value: EffectCode.TRUST.value,
            EmotionCode.CURIOSITY.value: EffectCode.CURIOSITY.value,
            EmotionCode.CALMNESS.value: "CALMNESS_EFFECT",
            EmotionCode.EXCITEMENT.value: "EXCITEMENT_EFFECT",
            EmotionCode.SADNESS.value: "SADNESS_EFFECT",
            EmotionCode.JOY.value: "JOY_EFFECT",
            EmotionCode.SURPRISE.value: "SURPRISE_EFFECT",
            EmotionCode.DISGUST.value: "DISGUST_EFFECT"
        }
        
        return emotion_effects.get(emotion_code)
    
    def _update_emotional_memory(self, emotion_code: str, intensity: float):
        """Обновление эмоциональной памяти"""
        current_value = self.current_state.emotional_memory.get(emotion_code, 0.0)
        new_value = min(1.0, current_value + intensity * 0.1)
        self.current_state.emotional_memory[emotion_code] = new_value
        
        # Постепенное затухание эмоций
        for emotion in self.current_state.emotional_memory:
            if emotion != emotion_code:
                decay = self.current_state.emotional_memory[emotion] * 0.95
                self.current_state.emotional_memory[emotion] = max(0.0, decay)
    
    def _check_emotion_combos(self):
        """Проверка комбинаций эмоций"""
        active_emotions = [self.current_state.primary_emotion] + self.current_state.secondary_emotions
        active_emotions = [e for e in active_emotions if e]
        
        if len(active_emotions) < 2:
            return
        
        # Проверка всех возможных комбинаций
        for i, emotion1 in enumerate(active_emotions):
            for emotion2 in active_emotions[i+1:]:
                combo_key = (emotion1, emotion2)
                reverse_key = (emotion2, emotion1)
                
                combo_data = self.emotion_combos.get(combo_key) or self.emotion_combos.get(reverse_key)
                
                if combo_data and random.random() < combo_data["chance"]:
                    self._trigger_emotion_combo(combo_data, emotion1, emotion2)
    
    def _trigger_emotion_combo(self, combo_data: Dict[str, Any], 
                              emotion1: str, emotion2: str):
        """Триггер комбинации эмоций"""
        try:
            # Создание комплексной эмоции
            complex_emotion = combo_data["result"]
            
            # Применение эффектов комбинации
            for effect_code in combo_data["effects"]:
                # Здесь будет применение эффекта
                pass
            
            # Запись в историю
            self.emotion_history.append({
                "emotion_code": complex_emotion,
                "intensity": 1.0,
                "source": f"combo_{emotion1}_{emotion2}",
                "timestamp": 0.0,
                "action": "combo_triggered",
                "description": combo_data["description"]
            })
            
            logger.info(f"Триггер комбинации эмоций: {combo_data['description']}")
            
        except Exception as e:
            logger.error(f"Ошибка триггера комбинации эмоций: {e}")
    
    def handle_dialogue(self, npc_emotion: str, player_emotions: List[str]) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Обработка диалога с NPC на основе эмоций"""
        try:
            # Расчёт уровня резонанса
            resonance_level = self._calculate_resonance(npc_emotion, player_emotions)
            
            if resonance_level > 0.8:  # Синхрония
                if random.random() < 0.9:
                    return "valuable_info", self._apply_dialogue_bonus(0.2)
            elif resonance_level < 0.3:  # Диссонанс
                if random.random() < 0.4:
                    return "aggression", None
                else:
                    return "false_info", None
            
            return "neutral", None
            
        except Exception as e:
            logger.error(f"Ошибка обработки диалога: {e}")
            return "neutral", None
    
    def _calculate_resonance(self, npc_emotion: str, player_emotions: List[str]) -> float:
        """Расчёт уровня эмоционального резонанса"""
        if not player_emotions:
            return 0.5
        
        # Простой расчёт резонанса на основе совпадения эмоций
        if npc_emotion in player_emotions:
            return 0.9
        elif self._are_emotions_compatible(npc_emotion, player_emotions):
            return 0.7
        elif self._are_emotions_conflicting(npc_emotion, player_emotions):
            return 0.2
        else:
            return 0.5
    
    def _are_emotions_compatible(self, emotion1: str, emotions2: List[str]) -> bool:
        """Проверка совместимости эмоций"""
        compatible_pairs = [
            (EmotionCode.TRUST.value, EmotionCode.CURIOSITY.value),
            (EmotionCode.CALMNESS.value, EmotionCode.TRUST.value),
            (EmotionCode.JOY.value, EmotionCode.EXCITEMENT.value)
        ]
        
        for emotion2 in emotions2:
            if (emotion1, emotion2) in compatible_pairs or (emotion2, emotion1) in compatible_pairs:
                return True
        return False
    
    def _are_emotions_conflicting(self, emotion1: str, emotions2: List[str]) -> bool:
        """Проверка конфликтности эмоций"""
        conflicting_pairs = [
            (EmotionCode.FEAR.value, EmotionCode.TRUST.value),
            (EmotionCode.RAGE.value, EmotionCode.CALMNESS.value),
            (EmotionCode.DISGUST.value, EmotionCode.JOY.value)
        ]
        
        for emotion2 in emotions2:
            if (emotion1, emotion2) in conflicting_pairs or (emotion2, emotion1) in conflicting_pairs:
                return True
        return False
    
    def _apply_dialogue_bonus(self, bonus_value: float) -> Dict[str, Any]:
        """Применение бонуса за диалог"""
        return {
            "type": "dialogue_bonus",
            "value": bonus_value,
            "description": "Бонус за эмоциональный резонанс в диалоге"
        }
    
    def get_emotional_pattern(self, pattern_name: str) -> List[str]:
        """Получение эмоционального паттерна"""
        return self.emotional_patterns.get(pattern_name, [])
    
    def set_emotional_pattern(self, pattern_name: str, emotions: List[str]):
        """Установка эмоционального паттерна"""
        self.emotional_patterns[pattern_name] = emotions
        logger.info(f"Установлен эмоциональный паттерн: {pattern_name}")
    
    def get_emotional_stability(self) -> float:
        """Получение уровня эмоциональной стабильности"""
        return self.current_state.emotional_stability
    
    def modify_emotional_stability(self, modifier: float):
        """Изменение эмоциональной стабильности"""
        self.current_state.emotional_stability = max(0.0, min(1.0, 
            self.current_state.emotional_stability + modifier))
    
    def get_current_emotions(self) -> List[str]:
        """Получение текущих эмоций"""
        emotions = []
        if self.current_state.primary_emotion:
            emotions.append(self.current_state.primary_emotion)
        emotions.extend(self.current_state.secondary_emotions)
        return emotions
    
    def clear_emotions(self):
        """Очистка всех эмоций"""
        self.current_state.primary_emotion = None
        self.current_state.secondary_emotions.clear()
        self.current_state.emotional_memory.clear()
        logger.info("Все эмоции очищены")
    
    def get_emotion_history(self) -> List[Dict[str, Any]]:
        """Получение истории эмоций"""
        return self.emotion_history.copy()
    
    def get_emotional_resonance(self, target_emotion: str) -> float:
        """Получение уровня резонанса с целевой эмоцией"""
        return self.emotional_resonance.get(target_emotion, 0.0)
    
    def set_emotional_resonance(self, target_emotion: str, value: float):
        """Установка уровня резонанса с целевой эмоцией"""
        self.emotional_resonance[target_emotion] = max(0.0, min(1.0, value))
