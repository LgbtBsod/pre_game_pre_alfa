#!/usr/bin/env python3
"""
Класс игрока - основная сущность под управлением пользователя
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from core.constants import constants_manager, StatType, DamageType, AIState, EntityType
from .base_entity import BaseEntity, EntityType as BaseEntityType

logger = logging.getLogger(__name__)

@dataclass
class PlayerStats:
    """Дополнительные характеристики игрока"""
    # Репутация и слава
    reputation: int = 0
    fame: int = 0
    
    # Достижения
    achievements: List[str] = field(default_factory=list)
    total_playtime: float = 0.0
    
    # Социальные характеристики
    charisma_bonus: float = 0.0
    persuasion_skill: float = 0.5

@dataclass
class PlayerMemory:
    """Дополнительная память игрока"""
    # История игрока
    quests_completed: List[str] = field(default_factory=list)
    locations_visited: List[str] = field(default_factory=list)
    npcs_met: List[str] = field(default_factory=list)
    
    # Временные метки
    last_save: float = 0.0
    last_exploration: float = 0.0
    last_social: float = 0.0

class Player(BaseEntity):
    """Класс игрока - наследуется от BaseEntity"""
    
    def __init__(self, player_id: str, name: str):
        # Инициализируем базовую сущность
        super().__init__(player_id, BaseEntityType.PLAYER, name)
        
        # Дополнительные характеристики игрока
        self.player_stats = PlayerStats()
        self.player_memory = PlayerMemory()
        
        # Специфичные для игрока настройки
        self.inventory.max_slots = 30  # Больше слотов инвентаря
        self.inventory.max_weight = 150.0  # Больше веса
        self.memory.max_memories = 200  # Больше памяти
        self.memory.learning_rate = 0.8  # Быстрее учится
        
        # Игровые настройки
        self.auto_save_interval = 300.0  # 5 минут
        self.last_auto_save = time.time()
        
        # Квесты и задания
        self.active_quests: List[str] = []
        self.completed_quests: List[str] = []
        self.quest_progress: Dict[str, Dict[str, Any]] = {}
        
        # Социальные связи
        self.friends: List[str] = []
        self.enemies: List[str] = []
        self.reputation_with_factions: Dict[str, int] = {}
        
        logger.info(f"Создан игрок: {name} ({player_id})")
    
    def update(self, delta_time: float):
        """Обновление состояния игрока"""
        try:
            # Обновляем базовую сущность
            super().update(delta_time)
            
            # Обновляем игровое время
            self.player_stats.total_playtime += delta_time
            
            # Автосохранение
            current_time = time.time()
            if current_time - self.last_auto_save >= self.auto_save_interval:
                self.save_game()
                self.last_auto_save = current_time
            
            # Обновляем время последнего исследования
            if self.is_moving:
                self.player_memory.last_exploration = current_time
            
        except Exception as e:
            logger.error(f"Ошибка обновления игрока {self.entity_id}: {e}")
    
    def save_game(self) -> bool:
        """Сохранение игры"""
        try:
            self.player_memory.last_save = time.time()
            # Здесь будет логика сохранения в файл
            logger.info(f"Игра сохранена для игрока {self.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения игры: {e}")
            return False
    
    def load_game(self) -> bool:
        """Загрузка игры"""
        try:
            # Здесь будет логика загрузки из файла
            logger.info(f"Игра загружена для игрока {self.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки игры: {e}")
            return False
    
    def start_quest(self, quest_id: str) -> bool:
        """Начало квеста"""
        try:
            if quest_id in self.active_quests:
                logger.warning(f"Квест {quest_id} уже активен")
                return False
            
            self.active_quests.append(quest_id)
            self.quest_progress[quest_id] = {
                'start_time': time.time(),
                'progress': 0.0,
                'objectives': {}
            }
            
            # Добавляем память о начале квеста
            self.add_memory('quests', {
                'action': 'quest_started',
                'quest_id': quest_id
            }, 'quest_started', {
                'quest_id': quest_id,
                'active_quests_count': len(self.active_quests)
            }, True)
            
            logger.info(f"Игрок {self.entity_id} начал квест {quest_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка начала квеста: {e}")
            return False
    
    def complete_quest(self, quest_id: str) -> bool:
        """Завершение квеста"""
        try:
            if quest_id not in self.active_quests:
                logger.warning(f"Квест {quest_id} не активен")
                return False
            
            # Удаляем из активных квестов
            self.active_quests.remove(quest_id)
            
            # Добавляем в завершенные
            if quest_id not in self.completed_quests:
                self.completed_quests.append(quest_id)
            
            # Удаляем прогресс
            if quest_id in self.quest_progress:
                del self.quest_progress[quest_id]
            
            # Добавляем память о завершении квеста
            self.add_memory('quests', {
                'action': 'quest_completed',
                'quest_id': quest_id
            }, 'quest_completed', {
                'quest_id': quest_id,
                'completed_quests_count': len(self.completed_quests)
            }, True)
            
            # Добавляем эмоцию радости
            self.add_emotion('joy', 0.4, 15.0, 'quest_completion')
            
            logger.info(f"Игрок {self.entity_id} завершил квест {quest_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка завершения квеста: {e}")
            return False
    
    def visit_location(self, location_id: str) -> bool:
        """Посещение локации"""
        try:
            if location_id not in self.player_memory.locations_visited:
                self.player_memory.locations_visited.append(location_id)
                
                # Добавляем память о посещении
                self.add_memory('exploration', {
                    'action': 'location_visited',
                    'location_id': location_id
                }, 'location_visited', {
                    'location_id': location_id,
                    'locations_visited_count': len(self.player_memory.locations_visited)
                }, True)
                
                logger.debug(f"Игрок {self.entity_id} посетил локацию {location_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка посещения локации: {e}")
            return False
    
    def meet_npc(self, npc_id: str) -> bool:
        """Встреча с NPC"""
        try:
            if npc_id not in self.player_memory.npcs_met:
                self.player_memory.npcs_met.append(npc_id)
                
                # Добавляем память о встрече
                self.add_memory('social', {
                    'action': 'npc_met',
                    'npc_id': npc_id
                }, 'npc_met', {
                    'npc_id': npc_id,
                    'npcs_met_count': len(self.player_memory.npcs_met)
                }, True)
                
                logger.debug(f"Игрок {self.entity_id} встретил NPC {npc_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка встречи с NPC: {e}")
            return False
    
    def gain_reputation(self, faction: str, amount: int) -> bool:
        """Получение репутации с фракцией"""
        try:
            current_reputation = self.reputation_with_factions.get(faction, 0)
            self.reputation_with_factions[faction] = current_reputation + amount
            
            # Обновляем общую репутацию
            self.player_stats.reputation += amount
            
            # Добавляем память о изменении репутации
            self.add_memory('social', {
                'action': 'reputation_gained',
                'faction': faction,
                'amount': amount
            }, 'reputation_gained', {
                'faction': faction,
                'new_reputation': self.reputation_with_factions[faction]
            }, True)
            
            logger.debug(f"Игрок {self.entity_id} получил {amount} репутации с фракцией {faction}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка получения репутации: {e}")
            return False
    
    def get_player_data(self) -> Dict[str, Any]:
        """Получение данных игрока"""
        base_data = super().get_entity_data()
        
        # Добавляем специфичные для игрока данные
        player_data = {
            **base_data,
            'player_stats': {
                'reputation': self.player_stats.reputation,
                'fame': self.player_stats.fame,
                'achievements': self.player_stats.achievements,
                'total_playtime': self.player_stats.total_playtime,
                'charisma_bonus': self.player_stats.charisma_bonus,
                'persuasion_skill': self.player_stats.persuasion_skill
            },
            'player_memory': {
                'quests_completed': self.player_memory.quests_completed,
                'locations_visited': self.player_memory.locations_visited,
                'npcs_met': self.player_memory.npcs_met,
                'last_save': self.player_memory.last_save,
                'last_exploration': self.player_memory.last_exploration,
                'last_social': self.player_memory.last_social
            },
            'quests': {
                'active_quests': self.active_quests,
                'completed_quests': self.completed_quests,
                'quest_progress': self.quest_progress
            },
            'social': {
                'friends': self.friends,
                'enemies': self.enemies,
                'reputation_with_factions': self.reputation_with_factions
            }
        }
        
        return player_data
    
    def get_info(self) -> str:
        """Получение информации об игроке"""
        base_info = super().get_info()
        
        player_info = (f"\n--- Игрок ---\n"
                      f"Репутация: {self.player_stats.reputation} | Слава: {self.player_stats.fame}\n"
                      f"Время игры: {self.player_stats.total_playtime:.1f} сек\n"
                      f"Активные квесты: {len(self.active_quests)} | Завершенные: {len(self.completed_quests)}\n"
                      f"Посещенные локации: {len(self.player_memory.locations_visited)}\n"
                      f"Встреченные NPC: {len(self.player_memory.npcs_met)}\n"
                      f"Друзья: {len(self.friends)} | Враги: {len(self.enemies)}")
        
        return base_info + player_info
