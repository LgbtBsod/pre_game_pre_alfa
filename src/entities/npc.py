#!/usr/bin/env python3
"""
Класс NPC - неигровые персонажи
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ..core.constants import constants_manager, StatType, DamageType, AIState, EntityType
from .base_entity import BaseEntity, EntityType as BaseEntityType

logger = logging.getLogger(__name__)

@dataclass
class NPCStats:
    """Дополнительные характеристики NPC"""
    # Социальные характеристики
    reputation: int = 0
    influence: int = 0
    
    # Профессиональные характеристики
    profession: str = "civilian"
    skill_level: int = 1
    
    # Экономические характеристики
    wealth: int = 0
    trade_skill: float = 0.5

@dataclass
class NPCPersonality:
    """Личность NPC"""
    # Основные черты характера
    friendliness: float = 0.5  # -1.0 до 1.0
    aggression: float = 0.3    # 0.0 до 1.0
    curiosity: float = 0.4     # 0.0 до 1.0
    loyalty: float = 0.6       # 0.0 до 1.0
    
    # Поведенческие паттерны
    talkativeness: float = 0.5  # 0.0 до 1.0
    generosity: float = 0.4     # 0.0 до 1.0
    honesty: float = 0.7        # 0.0 до 1.0
    
    # Предпочтения
    preferred_topics: List[str] = field(default_factory=list)
    disliked_topics: List[str] = field(default_factory=list)

@dataclass
class NPCMemory:
    """Дополнительная память NPC"""
    # Социальные связи
    known_players: List[str] = field(default_factory=list)
    known_npcs: List[str] = field(default_factory=list)
    relationships: Dict[str, float] = field(default_factory=dict)  # entity_id -> relationship_value
    
    # История взаимодействий
    conversations: List[Dict[str, Any]] = field(default_factory=list)
    trades: List[Dict[str, Any]] = field(default_factory=list)
    
    # Временные метки
    last_conversation: float = 0.0
    last_trade: float = 0.0
    last_mood_change: float = 0.0

class NPC(BaseEntity):
    """Класс неигрового персонажа - наследуется от BaseEntity"""
    
    def __init__(self, npc_id: str, name: str, npc_type: str = "civilian"):
        # Инициализируем базовую сущность
        super().__init__(npc_id, BaseEntityType.NPC, name)
        
        # Дополнительные характеристики NPC
        self.npc_stats = NPCStats(profession=npc_type)
        self.personality = NPCPersonality()
        self.npc_memory = NPCMemory()
        
        # Специфичные для NPC настройки
        self.inventory.max_slots = 15  # Меньше слотов инвентаря
        self.inventory.max_weight = 80.0  # Меньше веса
        self.memory.max_memories = 150  # Средняя память
        self.memory.learning_rate = 0.5  # Средняя скорость обучения
        
        # Поведение и состояние
        self.behavior = "passive"  # passive, aggressive, friendly, neutral
        self.current_mood = "neutral"  # happy, sad, angry, scared, neutral
        self.is_busy = False
        self.is_interacting = False
        
        # Диалоги и квесты
        self.dialogue_options: List[str] = []
        self.available_quests: List[str] = []
        self.completed_quests: List[str] = []
        self.quest_giver = False
        
        # Торговля
        self.is_merchant = False
        self.shop_inventory: List[str] = []
        self.prices: Dict[str, int] = {}
        
        # Расписание
        self.schedule: Dict[str, str] = {}  # time -> activity
        self.current_activity = "idle"
        
        logger.info(f"Создан NPC: {name} ({npc_type})")
    
    def update(self, delta_time: float):
        """Обновление состояния NPC"""
        try:
            # Обновляем базовую сущность
            super().update(delta_time)
            
            # Обновляем расписание
            self._update_schedule(delta_time)
            
            # Обновляем настроение
            self._update_mood(delta_time)
            
            # Обновляем поведение
            self._update_behavior(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления NPC {self.entity_id}: {e}")
    
    def _update_schedule(self, delta_time: float):
        """Обновление расписания NPC"""
        try:
            current_time = time.time()
            hour = (int(current_time) // 3600) % 24
            
            # Определяем текущую активность по расписанию
            if hour in self.schedule:
                self.current_activity = self.schedule[hour]
            else:
                # Базовое расписание
                if 6 <= hour < 12:
                    self.current_activity = "work"
                elif 12 <= hour < 18:
                    self.current_activity = "social"
                elif 18 <= hour < 22:
                    self.current_activity = "leisure"
                else:
                    self.current_activity = "sleep"
            
        except Exception as e:
            logger.error(f"Ошибка обновления расписания NPC {self.entity_id}: {e}")
    
    def _update_mood(self, delta_time: float):
        """Обновление настроения NPC"""
        try:
            current_time = time.time()
            
            # Базовое изменение настроения в зависимости от активности
            mood_change = 0.0
            
            if self.current_activity == "work":
                mood_change = -0.01 * delta_time  # Работа немного утомляет
            elif self.current_activity == "leisure":
                mood_change = 0.02 * delta_time   # Досуг поднимает настроение
            elif self.current_activity == "social":
                mood_change = 0.015 * delta_time  # Общение улучшает настроение
            elif self.current_activity == "sleep":
                mood_change = 0.01 * delta_time   # Сон восстанавливает
            
            # Применяем изменение настроения
            self.emotions.mood = max(-1.0, min(1.0, self.emotions.mood + mood_change))
            
            # Обновляем текущее настроение
            if self.emotions.mood > 0.3:
                self.current_mood = "happy"
            elif self.emotions.mood < -0.3:
                self.current_mood = "sad"
            else:
                self.current_mood = "neutral"
            
        except Exception as e:
            logger.error(f"Ошибка обновления настроения NPC {self.entity_id}: {e}")
    
    def _update_behavior(self, delta_time: float):
        """Обновление поведения NPC"""
        try:
            # Поведение зависит от настроения и личности
            if self.current_mood == "happy" and self.personality.friendliness > 0.7:
                self.behavior = "friendly"
            elif self.current_mood == "sad" and self.personality.aggression > 0.6:
                self.behavior = "aggressive"
            elif self.current_mood == "sad" and self.personality.aggression < 0.3:
                self.behavior = "passive"
            else:
                self.behavior = "neutral"
            
        except Exception as e:
            logger.error(f"Ошибка обновления поведения NPC {self.entity_id}: {e}")
    
    def interact_with_player(self, player_id: str, interaction_type: str, 
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Взаимодействие с игроком"""
        try:
            if not context:
                context = {}
            
            # Обновляем время последнего взаимодействия
            self.npc_memory.last_conversation = time.time()
            
            # Добавляем игрока в известных, если его там нет
            if player_id not in self.npc_memory.known_players:
                self.npc_memory.known_players.append(player_id)
                self.npc_memory.relationships[player_id] = 0.0
            
            # Рассчитываем изменение отношений
            relationship_change = self._calculate_relationship_change(interaction_type, context)
            self.npc_memory.relationships[player_id] += relationship_change
            
            # Обновляем настроение от взаимодействия
            self._update_mood_from_interaction(interaction_type, relationship_change)
            
            # Записываем взаимодействие
            interaction_record = {
                'player_id': player_id,
                'interaction_type': interaction_type,
                'context': context,
                'relationship_change': relationship_change,
                'timestamp': time.time()
            }
            self.npc_memory.conversations.append(interaction_record)
            
            # Добавляем память о взаимодействии
            self.add_memory('social', {
                'action': 'player_interaction',
                'player_id': player_id,
                'interaction_type': interaction_type
            }, 'player_interaction', {
                'player_id': player_id,
                'relationship_change': relationship_change,
                'new_relationship': self.npc_memory.relationships[player_id]
            }, True)
            
            # Формируем ответ
            response = self._generate_response(interaction_type, context, relationship_change)
            
            logger.debug(f"NPC {self.entity_id} взаимодействовал с игроком {player_id}: {interaction_type}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка взаимодействия NPC {self.entity_id} с игроком: {e}")
            return {'success': False, 'message': 'Ошибка взаимодействия'}
    
    def _calculate_relationship_change(self, interaction_type: str, context: Dict[str, Any]) -> float:
        """Расчет изменения отношений"""
        base_change = 0.0
        
        if interaction_type == "greeting":
            base_change = 0.1
        elif interaction_type == "gift":
            gift_value = context.get('gift_value', 0)
            base_change = min(0.5, gift_value / 100.0)
        elif interaction_type == "trade":
            trade_fairness = context.get('trade_fairness', 0.5)
            base_change = (trade_fairness - 0.5) * 0.3
        elif interaction_type == "quest_completion":
            base_change = 0.2
        elif interaction_type == "insult":
            base_change = -0.3
        elif interaction_type == "attack":
            base_change = -0.8
        
        # Модифицируем базовое изменение личностью
        if self.personality.friendliness > 0.7:
            base_change *= 1.2  # Дружелюбные NPC более отзывчивы
        elif self.personality.friendliness < 0.3:
            base_change *= 0.8  # Неприветливые NPC менее отзывчивы
        
        return base_change
    
    def _update_mood_from_interaction(self, interaction_type: str, relationship_change: float):
        """Обновление настроения от взаимодействия"""
        mood_change = relationship_change * 0.5  # Настроение меняется медленнее отношений
        
        if interaction_type == "gift":
            mood_change += 0.1  # Подарки всегда поднимают настроение
        elif interaction_type == "insult":
            mood_change -= 0.2  # Оскорбления портят настроение
        
        self.emotions.mood = max(-1.0, min(1.0, self.emotions.mood + mood_change))
    
    def _generate_response(self, interaction_type: str, context: Dict[str, Any], 
                          relationship_change: float) -> Dict[str, Any]:
        """Генерация ответа на взаимодействие"""
        response = {
            'success': True,
            'npc_id': self.entity_id,
            'npc_name': self.name,
            'interaction_type': interaction_type,
            'relationship_change': relationship_change,
            'current_relationship': self.npc_memory.relationships.get(context.get('player_id', ''), 0.0),
            'mood': self.current_mood,
            'behavior': self.behavior
        }
        
        # Генерируем сообщение в зависимости от типа взаимодействия
        if interaction_type == "greeting":
            if self.current_mood == "happy":
                response['message'] = f"Привет! Рад тебя видеть, {context.get('player_name', 'путник')}!"
            elif self.current_mood == "sad":
                response['message'] = f"Привет... {context.get('player_name', 'путник')}..."
            else:
                response['message'] = f"Здравствуй, {context.get('player_name', 'путник')}."
        
        elif interaction_type == "gift":
            response['message'] = "Спасибо за подарок! Это очень мило с твоей стороны."
        
        elif interaction_type == "trade":
            if relationship_change > 0:
                response['message'] = "Приятно иметь дело с честным торговцем!"
            else:
                response['message'] = "Хм, думаю мы могли бы договориться о лучшей цене..."
        
        elif interaction_type == "quest_completion":
            response['message'] = "Отлично! Ты справился с заданием. Спасибо!"
        
        else:
            response['message'] = "Интересно..."
        
        return response
    
    def get_dialogue_options(self, player_id: str) -> List[Dict[str, Any]]:
        """Получение доступных диалоговых опций"""
        try:
            options = []
            relationship = self.npc_memory.relationships.get(player_id, 0.0)
            
            # Базовые опции
            options.append({
                'id': 'greeting',
                'text': 'Поздороваться',
                'available': True,
                'relationship_required': -1.0
            })
            
            # Опции в зависимости от отношений
            if relationship > 0.3:
                options.append({
                    'id': 'personal_question',
                    'text': 'Спросить о личном',
                    'available': True,
                    'relationship_required': 0.3
                })
            
            if relationship > 0.5:
                options.append({
                    'id': 'favor_request',
                    'text': 'Попросить услугу',
                    'available': True,
                    'relationship_required': 0.5
                })
            
            # Торговые опции для торговцев
            if self.is_merchant:
                options.append({
                    'id': 'trade',
                    'text': 'Торговать',
                    'available': True,
                    'relationship_required': 0.0
                })
            
            # Квестовые опции
            if self.quest_giver and self.available_quests:
                options.append({
                    'id': 'quest_offer',
                    'text': 'Спросить о заданиях',
                    'available': True,
                    'relationship_required': 0.0
                })
            
            return options
            
        except Exception as e:
            logger.error(f"Ошибка получения диалоговых опций NPC {self.entity_id}: {e}")
            return []
    
    def respond_to_dialogue(self, dialogue_id: str, player_id: str, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ответ на диалог"""
        try:
            if not context:
                context = {}
            
            response = {
                'success': True,
                'npc_id': self.entity_id,
                'dialogue_id': dialogue_id,
                'message': '',
                'options': []
            }
            
            if dialogue_id == 'greeting':
                response['message'] = f"Привет! Я {self.name}. Чем могу помочь?"
                response['options'] = self.get_dialogue_options(player_id)
            
            elif dialogue_id == 'personal_question':
                response['message'] = f"Ну, я работаю {self.npc_stats.profession}. Жизнь идет своим чередом."
            
            elif dialogue_id == 'favor_request':
                response['message'] = "Хм, зависит от того, что именно тебе нужно..."
            
            elif dialogue_id == 'trade':
                if self.is_merchant:
                    response['message'] = "Конечно! У меня есть отличные товары. Что интересует?"
                    response['shop_items'] = self.shop_inventory
                else:
                    response['message'] = "Извини, но я не торгую."
            
            elif dialogue_id == 'quest_offer':
                if self.available_quests:
                    response['message'] = "Да, у меня есть несколько заданий. Какое тебя интересует?"
                    response['available_quests'] = self.available_quests
                else:
                    response['message'] = "Извини, но сейчас у меня нет заданий для тебя."
            
            else:
                response['message'] = "Извини, я не понимаю, о чем ты говоришь."
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка ответа на диалог NPC {self.entity_id}: {e}")
            return {'success': False, 'message': 'Ошибка диалога'}
    
    def add_quest(self, quest_id: str) -> bool:
        """Добавление квеста NPC"""
        try:
            if quest_id not in self.available_quests:
                self.available_quests.append(quest_id)
                self.quest_giver = True
                
                logger.debug(f"Квест {quest_id} добавлен NPC {self.entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка добавления квеста NPC {self.entity_id}: {e}")
            return False
    
    def complete_quest(self, quest_id: str) -> bool:
        """Завершение квеста NPC"""
        try:
            if quest_id in self.available_quests:
                self.available_quests.remove(quest_id)
                self.completed_quests.append(quest_id)
                
                logger.debug(f"Квест {quest_id} завершен NPC {self.entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка завершения квеста NPC {self.entity_id}: {e}")
            return False
    
    def set_merchant(self, is_merchant: bool, shop_items: List[str] = None, 
                    prices: Dict[str, int] = None) -> bool:
        """Установка NPC как торговца"""
        try:
            self.is_merchant = is_merchant
            
            if is_merchant:
                self.shop_inventory = shop_items or []
                self.prices = prices or {}
                self.npc_stats.profession = "merchant"
                
                logger.debug(f"NPC {self.entity_id} стал торговцем")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки торговца NPC {self.entity_id}: {e}")
            return False
    
    def get_npc_data(self) -> Dict[str, Any]:
        """Получение данных NPC"""
        base_data = super().get_entity_data()
        
        # Добавляем специфичные для NPC данные
        npc_data = {
            **base_data,
            'npc_stats': {
                'reputation': self.npc_stats.reputation,
                'influence': self.npc_stats.influence,
                'profession': self.npc_stats.profession,
                'skill_level': self.npc_stats.skill_level,
                'wealth': self.npc_stats.wealth,
                'trade_skill': self.npc_stats.trade_skill
            },
            'personality': {
                'friendliness': self.personality.friendliness,
                'aggression': self.personality.aggression,
                'curiosity': self.personality.curiosity,
                'loyalty': self.personality.loyalty,
                'talkativeness': self.personality.talkativeness,
                'generosity': self.personality.generosity,
                'honesty': self.personality.honesty,
                'preferred_topics': self.personality.preferred_topics,
                'disliked_topics': self.personality.disliked_topics
            },
            'npc_memory': {
                'known_players': self.npc_memory.known_players,
                'known_npcs': self.npc_memory.known_npcs,
                'relationships': self.npc_memory.relationships,
                'conversations_count': len(self.npc_memory.conversations),
                'trades_count': len(self.npc_memory.trades),
                'last_conversation': self.npc_memory.last_conversation,
                'last_trade': self.npc_memory.last_trade
            },
            'behavior': {
                'current_behavior': self.behavior,
                'current_mood': self.current_mood,
                'current_activity': self.current_activity,
                'is_busy': self.is_busy,
                'is_interacting': self.is_interacting
            },
            'quests': {
                'available_quests': self.available_quests,
                'completed_quests': self.completed_quests,
                'quest_giver': self.quest_giver
            },
            'trade': {
                'is_merchant': self.is_merchant,
                'shop_inventory': self.shop_inventory,
                'prices': self.prices
            },
            'schedule': {
                'current_schedule': self.schedule,
                'current_activity': self.current_activity
            }
        }
        
        return npc_data
    
    def get_info(self) -> str:
        """Получение информации о NPC"""
        base_info = super().get_info()
        
        npc_info = (f"\n--- NPC ---\n"
                   f"Профессия: {self.npc_stats.profession} | Репутация: {self.npc_stats.reputation}\n"
                   f"Поведение: {self.behavior} | Настроение: {self.current_mood}\n"
                   f"Активность: {self.current_activity} | Дружелюбие: {self.personality.friendliness:.2f}\n"
                   f"Известные игроки: {len(self.npc_memory.known_players)} | "
                   f"Известные NPC: {len(self.npc_memory.known_npcs)}\n"
                   f"Доступные квесты: {len(self.available_quests)} | "
                   f"Торговец: {'Да' if self.is_merchant else 'Нет'}")
        
        return base_info + npc_info
