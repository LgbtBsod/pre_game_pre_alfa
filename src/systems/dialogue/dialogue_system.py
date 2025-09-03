#!/usr/bin/env python3
"""Система адаптивных диалогов
Поддерживает динамические ответы, память о разговорах, эмоциональные реакции"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import logging
import random
import time
import json
import math
from pathlib import Path

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from src.core.constants import DialogueType, EmotionType
from src.core.state_manager import StateManager, StateType

# = ДОПОЛНИТЕЛЬНЫЕ ТИПЫ ДИАЛОГОВ

class RelationshipType(Enum):
    """Типы отношений"""
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    LOVER = "lover"
    ENEMY = "enemy"
    RIVAL = "rival"
    MENTOR = "mentor"
    STUDENT = "student"

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class DialogueMemory:
    """Память о диалоге"""
    dialogue_id: str
    timestamp: float
    speaker_id: str
    listener_id: str
    dialogue_type: DialogueType
    topic: str
    emotion: EmotionType
    relationship_change: float
    key_phrases: List[str] = field(default_factory=list)
    important_info: Dict[str, Any] = field(default_factory=dict)
    success: bool = True

@dataclass
class DialogueOption:
    """Вариант ответа в диалоге"""
    option_id: str
    text: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    consequences: Dict[str, Any] = field(default_factory=dict)
    emotion_requirement: Optional[EmotionType] = None
    relationship_requirement: Optional[RelationshipType] = None
    skill_requirement: Optional[str] = None
    skill_level: int = 0
    success_rate: float = 1.0
    learning_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DialogueNode:
    """Узел диалога"""
    node_id: str
    speaker_id: str
    text: str
    emotion: EmotionType
    options: List[DialogueOption] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    consequences: Dict[str, Any] = field(default_factory=dict)
    memory_impact: float = 0.0
    relationship_impact: float = 0.0

@dataclass
class CharacterPersonality:
    """Личность персонажа для диалогов"""
    character_id: str
    base_emotion: EmotionType
    personality_traits: Dict[str, float] = field(default_factory=dict)
    relationship_preferences: Dict[str, RelationshipType] = field(default_factory=dict)
    dialogue_style: Dict[str, float] = field(default_factory=dict)
    memory_decay_rate: float = 0.95
    emotional_stability: float = 0.5
    trust_level: float = 0.5

@dataclass
class DialogueContext:
    """Контекст диалога"""
    current_topic: str
    emotional_state: EmotionType
    relationship_level: RelationshipType
    trust_level: float
    previous_topics: List[str] = field(default_factory=list)
    recent_memories: List[DialogueMemory] = field(default_factory=list)
    conversation_history: List[str] = field(default_factory=list)
    key_phrases: Set[str] = field(default_factory=set)

# = НАСТРОЙКИ ДИАЛОГОВ
@dataclass
class DialogueSettings:
    """Настройки системы диалогов"""
    max_memory_entries: int = 100
    memory_decay_rate: float = 0.95
    emotional_influence: float = 0.3
    relationship_influence: float = 0.4
    context_influence: float = 0.3
    learning_rate: float = 0.1
    max_conversation_length: int = 50
    enable_emotional_adaptation: bool = True
    enable_relationship_evolution: bool = True
    enable_context_memory: bool = True

# = СИСТЕМА ДИАЛОГОВ
class DialogueSystem(BaseComponent):
    """Система адаптивных диалогов"""
    
    def __init__(self):
        super().__init__(
            component_id="DialogueSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки системы
        self.settings = DialogueSettings()
        
        # Персонажи и их личности
        self.character_personalities: Dict[str, CharacterPersonality] = {}
        
        # Память диалогов
        self.dialogue_memories: Dict[str, List[DialogueMemory]] = {}
        
        # Шаблоны диалогов
        self.dialogue_templates: Dict[str, List[DialogueNode]] = {}
        
        # Активные диалоги
        self.active_dialogues: Dict[str, DialogueContext] = {}
        
        # Статистика
        self.stats = {
            "total_dialogues": 0,
            "successful_dialogues": 0,
            "emotional_changes": 0,
            "relationship_changes": 0,
            "memory_entries": 0,
            "context_adaptations": 0
        }
        
        # Callbacks
        self.dialogue_callbacks: List[callable] = []
        self.emotion_callbacks: List[callable] = []
        self.relationship_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация системы диалогов"""
        try:
            # Загрузка шаблонов диалогов
            self._load_dialogue_templates()
            
            # Инициализация базовых личностей
            self._initialize_base_personalities()
            
            self.logger.info("DialogueSystem инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации DialogueSystem: {e}")
            return False
    
    def _load_dialogue_templates(self):
        """Загрузка шаблонов диалогов"""
        try:
            # Базовые шаблоны для разных типов диалогов
            self.dialogue_templates["greeting"] = [
                DialogueNode(
                    node_id="greeting_friendly",
                    speaker_id="npc",
                    text="Привет! Рад тебя видеть.",
                    emotion=EmotionType.HAPPY,
                    options=[
                        DialogueOption(
                            option_id="greet_back",
                            text="Привет! Как дела?",
                            consequences={"relationship": 0.1, "emotion": EmotionType.HAPPY}
                        ),
                        DialogueOption(
                            option_id="greet_casual",
                            text="Привет.",
                            consequences={"relationship": 0.0, "emotion": EmotionType.NEUTRAL}
                        )
                    ]
                )
            ]
            
            self.dialogue_templates["quest"] = [
                DialogueNode(
                    node_id="quest_offer",
                    speaker_id="npc",
                    text="У меня есть для тебя задание. Заинтересован?",
                    emotion=EmotionType.NEUTRAL,
                    options=[
                        DialogueOption(
                            option_id="accept_quest",
                            text="Конечно, расскажи подробнее.",
                            consequences={"relationship": 0.2, "quest_accept": True}
                        ),
                        DialogueOption(
                            option_id="decline_quest",
                            text="Извини, сейчас не время.",
                            consequences={"relationship": -0.1, "quest_accept": False}
                        )
                    ]
                )
            ]
            
            self.logger.info("Шаблоны диалогов загружены")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки шаблонов диалогов: {e}")
    
    def _initialize_base_personalities(self):
        """Инициализация базовых личностей"""
        # Дружелюбный торговец
        self.character_personalities["merchant_friendly"] = CharacterPersonality(
            character_id="merchant_friendly",
            base_emotion=EmotionType.HAPPY,
            personality_traits={
                "friendliness": 0.8,
                "honesty": 0.7,
                "curiosity": 0.6,
                "patience": 0.9
            },
            dialogue_style={
                "formal": 0.3,
                "casual": 0.7,
                "enthusiastic": 0.8
            }
        )
        
        # Подозрительный стражник
        self.character_personalities["guard_suspicious"] = CharacterPersonality(
            character_id="guard_suspicious",
            base_emotion=EmotionType.SUSPICIOUS,
            personality_traits={
                "friendliness": 0.2,
                "honesty": 0.8,
                "suspicion": 0.9,
                "loyalty": 0.9
            },
            dialogue_style={
                "formal": 0.8,
                "casual": 0.2,
                "threatening": 0.6
            }
        )
        
        # Мудрый наставник
        self.character_personalities["mentor_wise"] = CharacterPersonality(
            character_id="mentor_wise",
            base_emotion=EmotionType.NEUTRAL,
            personality_traits={
                "wisdom": 0.9,
                "patience": 0.8,
                "kindness": 0.7,
                "knowledge": 0.9
            },
            dialogue_style={
                "formal": 0.6,
                "casual": 0.4,
                "philosophical": 0.8
            }
        )
    
    def register_character(self, character_id: str, personality: CharacterPersonality) -> bool:
        """Регистрация персонажа в системе диалогов"""
        try:
            self.character_personalities[character_id] = personality
            self.dialogue_memories[character_id] = []
            
            self.logger.info(f"Персонаж {character_id} зарегистрирован в системе диалогов")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка регистрации персонажа {character_id}: {e}")
            return False
    
    def start_dialogue(self, speaker_id: str, listener_id: str, 
                      dialogue_type: DialogueType = DialogueType.CASUAL) -> str:
        """Начало диалога"""
        try:
            dialogue_id = f"dialogue_{speaker_id}_{listener_id}_{int(time.time())}"
            
            # Создание контекста диалога
            context = DialogueContext(
                current_topic="greeting",
                emotional_state=self._get_character_emotion(speaker_id),
                relationship_level=self._get_relationship_level(speaker_id, listener_id),
                trust_level=self._get_trust_level(speaker_id, listener_id)
            )
            
            self.active_dialogues[dialogue_id] = context
            
            # Добавление в статистику
            self.stats["total_dialogues"] += 1
            
            self.logger.info(f"Начат диалог {dialogue_id} между {speaker_id} и {listener_id}")
            return dialogue_id
            
        except Exception as e:
            self.logger.error(f"Ошибка начала диалога: {e}")
            return ""
    
    def get_dialogue_options(self, dialogue_id: str, speaker_id: str, 
                           current_text: str = "") -> List[DialogueOption]:
        """Получение вариантов ответа для диалога"""
        try:
            if dialogue_id not in self.active_dialogues:
                return []
            
            context = self.active_dialogues[dialogue_id]
            
            # Получение подходящих шаблонов
            templates = self._get_relevant_templates(context.current_topic, speaker_id)
            
            # Фильтрация по условиям
            available_options = []
            for template in templates:
                for option in template.options:
                    if self._check_option_conditions(option, context, speaker_id):
                        # Адаптация текста под контекст
                        adapted_option = self._adapt_option_to_context(option, context)
                        available_options.append(adapted_option)
            
            # Сортировка по приоритету
            available_options.sort(key=lambda x: x.success_rate, reverse=True)
            
            return available_options
            
        except Exception as e:
            self.logger.error(f"Ошибка получения вариантов диалога: {e}")
            return []
    
    def _get_relevant_templates(self, topic: str, speaker_id: str) -> List[DialogueNode]:
        """Получение релевантных шаблонов диалогов"""
        templates = []
        
        # Поиск по теме
        if topic in self.dialogue_templates:
            templates.extend(self.dialogue_templates[topic])
        
        # Поиск по типу персонажа
        personality = self.character_personalities.get(speaker_id)
        if personality:
            # Фильтрация по стилю диалога
            for template_list in self.dialogue_templates.values():
                for template in template_list:
                    if self._matches_personality_style(template, personality):
                        templates.append(template)
        
        return templates
    
    def _matches_personality_style(self, template: DialogueNode, 
                                 personality: CharacterPersonality) -> bool:
        """Проверка соответствия шаблона стилю личности"""
        # Проверка эмоционального соответствия
        if template.emotion != personality.base_emotion:
            return False
        
        # Проверка стиля диалога
        for option in template.options:
            if hasattr(option, 'dialogue_style'):
                for style, value in option.dialogue_style.items():
                    if style in personality.dialogue_style:
                        if abs(value - personality.dialogue_style[style]) > 0.3:
                            return False
        
        return True
    
    def _check_option_conditions(self, option: DialogueOption, context: DialogueContext, 
                               speaker_id: str) -> bool:
        """Проверка условий для варианта ответа"""
        try:
            # Проверка эмоциональных требований
            if option.emotion_requirement and context.emotional_state != option.emotion_requirement:
                return False
            
            # Проверка требований к отношениям
            if option.relationship_requirement and context.relationship_level != option.relationship_requirement:
                return False
            
            # Проверка навыков
            if option.skill_requirement:
                # Здесь должна быть проверка навыков игрока
                pass
            
            # Проверка других условий
            for condition, value in option.conditions.items():
                if condition == "trust_level" and context.trust_level < value:
                    return False
                elif condition == "previous_topics" and value not in context.previous_topics:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки условий: {e}")
            return False
    
    def _adapt_option_to_context(self, option: DialogueOption, 
                                context: DialogueContext) -> DialogueOption:
        """Адаптация варианта ответа под контекст"""
        try:
            # Создание копии опции
            adapted_option = DialogueOption(
                option_id=option.option_id,
                text=option.text,
                conditions=option.conditions.copy(),
                consequences=option.consequences.copy(),
                emotion_requirement=option.emotion_requirement,
                relationship_requirement=option.relationship_requirement,
                skill_requirement=option.skill_requirement,
                skill_level=option.skill_level,
                success_rate=option.success_rate,
                learning_data=option.learning_data.copy()
            )
            
            # Адаптация текста на основе эмоций
            if context.emotional_state != EmotionType.NEUTRAL:
                adapted_option.text = self._adapt_text_to_emotion(
                    adapted_option.text, context.emotional_state
                )
            
            # Адаптация на основе отношений
            if context.relationship_level != RelationshipType.STRANGER:
                adapted_option.text = self._adapt_text_to_relationship(
                    adapted_option.text, context.relationship_level
                )
            
            # Адаптация успешности на основе контекста
            adapted_option.success_rate = self._calculate_context_success_rate(
                option, context
            )
            
            return adapted_option
            
        except Exception as e:
            self.logger.error(f"Ошибка адаптации опции: {e}")
            return option
    
    def _adapt_text_to_emotion(self, text: str, emotion: EmotionType) -> str:
        """Адаптация текста под эмоцию"""
        emotion_modifiers = {
            EmotionType.HAPPY: ["с радостью", "весело", "с улыбкой"],
            EmotionType.SAD: ["грустно", "с вздохом", "печально"],
            EmotionType.ANGRY: ["сердито", "с раздражением", "гневно"],
            EmotionType.FEAR: ["боязливо", "с тревогой", "нервно"],
            EmotionType.SURPRISE: ["с удивлением", "пораженно", "изумленно"],
            EmotionType.EXCITED: ["с энтузиазмом", "воодушевленно", "с азартом"]
        }
        
        if emotion in emotion_modifiers:
            modifier = random.choice(emotion_modifiers[emotion])
            return f"{text} ({modifier})"
        
        return text
    
    def _adapt_text_to_relationship(self, text: str, relationship: RelationshipType) -> str:
        """Адаптация текста под отношения"""
        relationship_modifiers = {
            RelationshipType.FRIEND: ["друг", "приятель"],
            RelationshipType.CLOSE_FRIEND: ["старый друг", "близкий друг"],
            RelationshipType.LOVER: ["любимый", "дорогой"],
            RelationshipType.ENEMY: ["враг", "противник"],
            RelationshipType.MENTOR: ["учитель", "наставник"]
        }
        
        if relationship in relationship_modifiers:
            modifier = random.choice(relationship_modifiers[relationship])
            return text.replace("ты", f"ты, {modifier}")
        
        return text
    
    def _calculate_context_success_rate(self, option: DialogueOption, 
                                      context: DialogueContext) -> float:
        """Расчет успешности на основе контекста"""
        base_rate = option.success_rate
        
        # Влияние эмоций
        if context.emotional_state == EmotionType.HAPPY:
            base_rate *= 1.1
        elif context.emotional_state == EmotionType.ANGRY:
            base_rate *= 0.8
        
        # Влияние отношений
        relationship_bonus = {
            RelationshipType.FRIEND: 1.2,
            RelationshipType.CLOSE_FRIEND: 1.4,
            RelationshipType.LOVER: 1.5,
            RelationshipType.ENEMY: 0.6,
            RelationshipType.STRANGER: 1.0
        }
        
        if context.relationship_level in relationship_bonus:
            base_rate *= relationship_bonus[context.relationship_level]
        
        # Влияние доверия
        base_rate *= (0.5 + context.trust_level * 0.5)
        
        return min(1.0, max(0.0, base_rate))
    
    def make_dialogue_choice(self, dialogue_id: str, option_id: str, 
                           speaker_id: str, listener_id: str) -> Dict[str, Any]:
        """Выбор варианта в диалоге"""
        try:
            if dialogue_id not in self.active_dialogues:
                return {"success": False, "error": "Диалог не найден"}
            
            context = self.active_dialogues[dialogue_id]
            
            # Поиск выбранной опции
            selected_option = None
            for template in self._get_relevant_templates(context.current_topic, speaker_id):
                for option in template.options:
                    if option.option_id == option_id:
                        selected_option = option
                        break
                if selected_option:
                    break
            
            if not selected_option:
                return {"success": False, "error": "Вариант не найден"}
            
            # Применение последствий
            consequences = self._apply_dialogue_consequences(
                selected_option, context, speaker_id, listener_id
            )
            
            # Обновление контекста
            self._update_dialogue_context(dialogue_id, selected_option, consequences)
            
            # Сохранение в память
            self._save_dialogue_memory(dialogue_id, speaker_id, listener_id, selected_option, consequences)
            
            # Уведомление о выборе
            self._notify_dialogue_choice(dialogue_id, selected_option, consequences)
            
            self.stats["successful_dialogues"] += 1
            
            return {
                "success": True,
                "option": selected_option,
                "consequences": consequences,
                "context": context
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка выбора в диалоге: {e}")
            return {"success": False, "error": str(e)}
    
    def _apply_dialogue_consequences(self, option: DialogueOption, context: DialogueContext,
                                   speaker_id: str, listener_id: str) -> Dict[str, Any]:
        """Применение последствий выбора"""
        consequences = {}
        
        try:
            # Изменение отношений
            if "relationship" in option.consequences:
                relationship_change = option.consequences["relationship"]
                self._update_relationship(speaker_id, listener_id, relationship_change)
                consequences["relationship_change"] = relationship_change
                self.stats["relationship_changes"] += 1
            
            # Изменение эмоций
            if "emotion" in option.consequences:
                new_emotion = option.consequences["emotion"]
                self._update_emotion(speaker_id, new_emotion)
                consequences["emotion_change"] = new_emotion
                self.stats["emotional_changes"] += 1
            
            # Изменение доверия
            if "trust" in option.consequences:
                trust_change = option.consequences["trust"]
                self._update_trust(speaker_id, listener_id, trust_change)
                consequences["trust_change"] = trust_change
            
            # Другие последствия
            for key, value in option.consequences.items():
                if key not in ["relationship", "emotion", "trust"]:
                    consequences[key] = value
            
            return consequences
            
        except Exception as e:
            self.logger.error(f"Ошибка применения последствий: {e}")
            return consequences
    
    def _update_dialogue_context(self, dialogue_id: str, option: DialogueOption, 
                                consequences: Dict[str, Any]):
        """Обновление контекста диалога"""
        try:
            context = self.active_dialogues[dialogue_id]
            
            # Обновление эмоций
            if "emotion_change" in consequences:
                context.emotional_state = consequences["emotion_change"]
            
            # Обновление отношений
            if "relationship_change" in consequences:
                # Логика обновления уровня отношений
                pass
            
            # Обновление доверия
            if "trust_change" in consequences:
                context.trust_level = max(0.0, min(1.0, context.trust_level + consequences["trust_change"]))
            
            # Добавление в историю
            context.conversation_history.append(option.text)
            
            # Ограничение длины истории
            if len(context.conversation_history) > self.settings.max_conversation_length:
                context.conversation_history.pop(0)
            
            # Обновление ключевых фраз
            key_phrases = self._extract_key_phrases(option.text)
            context.key_phrases.update(key_phrases)
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления контекста: {e}")
    
    def _save_dialogue_memory(self, dialogue_id: str, speaker_id: str, listener_id: str,
                            option: DialogueOption, consequences: Dict[str, Any]):
        """Сохранение диалога в память"""
        try:
            memory = DialogueMemory(
                dialogue_id=dialogue_id,
                timestamp=time.time(),
                speaker_id=speaker_id,
                listener_id=listener_id,
                dialogue_type=DialogueType.CASUAL,  # Можно определить по контексту
                topic="dialogue",
                emotion=EmotionType.NEUTRAL,  # Можно определить по последствиям
                relationship_change=consequences.get("relationship_change", 0.0),
                key_phrases=self._extract_key_phrases(option.text),
                important_info=consequences,
                success=consequences.get("success", True)
            )
            
            # Добавление в память обоих участников
            for participant_id in [speaker_id, listener_id]:
                if participant_id in self.dialogue_memories:
                    self.dialogue_memories[participant_id].append(memory)
                    
                    # Ограничение размера памяти
                    if len(self.dialogue_memories[participant_id]) > self.settings.max_memory_entries:
                        self.dialogue_memories[participant_id].pop(0)
            
            self.stats["memory_entries"] += 1
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения памяти диалога: {e}")
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Извлечение ключевых фраз из текста"""
        # Простая реализация - можно улучшить с помощью NLP
        words = text.lower().split()
        key_words = [word for word in words if len(word) > 3]
        return key_words[:5]  # Ограничиваем количество
    
    def _get_character_emotion(self, character_id: str) -> EmotionType:
        """Получение текущей эмоции персонажа"""
        personality = self.character_personalities.get(character_id)
        if personality:
            return personality.base_emotion
        return EmotionType.NEUTRAL
    
    def _get_relationship_level(self, speaker_id: str, listener_id: str) -> RelationshipType:
        """Получение уровня отношений между персонажами"""
        # Простая реализация - можно улучшить
        return RelationshipType.STRANGER
    
    def _get_trust_level(self, speaker_id: str, listener_id: str) -> float:
        """Получение уровня доверия между персонажами"""
        # Простая реализация - можно улучшить
        return 0.5
    
    def _update_relationship(self, speaker_id: str, listener_id: str, change: float):
        """Обновление отношений между персонажами"""
        # Реализация обновления отношений
        pass
    
    def _update_emotion(self, character_id: str, new_emotion: EmotionType):
        """Обновление эмоции персонажа"""
        personality = self.character_personalities.get(character_id)
        if personality:
            personality.base_emotion = new_emotion
    
    def _update_trust(self, speaker_id: str, listener_id: str, change: float):
        """Обновление доверия между персонажами"""
        # Реализация обновления доверия
        pass
    
    def end_dialogue(self, dialogue_id: str) -> bool:
        """Завершение диалога"""
        try:
            if dialogue_id in self.active_dialogues:
                del self.active_dialogues[dialogue_id]
                self.logger.info(f"Диалог {dialogue_id} завершен")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка завершения диалога: {e}")
            return False
    
    def get_character_memories(self, character_id: str) -> List[DialogueMemory]:
        """Получение воспоминаний персонажа"""
        return self.dialogue_memories.get(character_id, [])
    
    def get_dialogue_statistics(self) -> Dict[str, Any]:
        """Получение статистики диалогов"""
        return {
            "total_dialogues": self.stats["total_dialogues"],
            "successful_dialogues": self.stats["successful_dialogues"],
            "emotional_changes": self.stats["emotional_changes"],
            "relationship_changes": self.stats["relationship_changes"],
            "memory_entries": self.stats["memory_entries"],
            "context_adaptations": self.stats["context_adaptations"],
            "active_dialogues": len(self.active_dialogues),
            "registered_characters": len(self.character_personalities),
            "total_memories": sum(len(memories) for memories in self.dialogue_memories.values())
        }
    
    def add_dialogue_callback(self, callback: callable):
        """Добавление callback для диалогов"""
        self.dialogue_callbacks.append(callback)
    
    def add_emotion_callback(self, callback: callable):
        """Добавление callback для эмоций"""
        self.emotion_callbacks.append(callback)
    
    def add_relationship_callback(self, callback: callable):
        """Добавление callback для отношений"""
        self.relationship_callbacks.append(callback)
    
    def _notify_dialogue_choice(self, dialogue_id: str, option: DialogueOption, 
                               consequences: Dict[str, Any]):
        """Уведомление о выборе в диалоге"""
        for callback in self.dialogue_callbacks:
            try:
                callback(dialogue_id, option, consequences)
            except Exception as e:
                self.logger.error(f"Ошибка в callback диалога: {e}")
    
    def _on_destroy(self):
        """Уничтожение системы диалогов"""
        self.character_personalities.clear()
        self.dialogue_memories.clear()
        self.dialogue_templates.clear()
        self.active_dialogues.clear()
        self.dialogue_callbacks.clear()
        self.emotion_callbacks.clear()
        self.relationship_callbacks.clear()
        
        self.logger.info("DialogueSystem уничтожен")
