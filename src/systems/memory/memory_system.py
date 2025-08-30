#!/usr/bin/env python3
"""
Система памяти и прогрессии AI-EVOLVE
Накопление опыта для персонажей и врагов
"""

import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.architecture import BaseComponent, ComponentType, Priority, Event, create_event

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Типы памяти"""
    PLAYER = "player"
    ENEMY = "enemy"
    SHARED = "shared"

class ExperienceCategory(Enum):
    """Категории опыта"""
    KILLS = "kills"
    DEATHS = "deaths"
    EXPLORATION = "exploration"
    INTERACTIONS = "interactions"
    COMBAT = "combat"
    CRAFTING = "crafting"
    TRADING = "trading"
    QUESTS = "quests"
    EVOLUTION = "evolution"
    SOCIAL = "social"

@dataclass
class ExperienceEntry:
    """Запись опыта"""
    category: ExperienceCategory
    amount: int
    timestamp: float
    source: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class LevelThreshold:
    """Порог уровня"""
    level: int
    experience_required: int
    rewards: List[str] = field(default_factory=list)
    unlocks: List[str] = field(default_factory=list)

class BaseMemory(ABC):
    """Базовый класс для памяти"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.experience: Dict[ExperienceCategory, int] = {
            category: 0 for category in ExperienceCategory
        }
        self.level = 1
        self.total_experience = 0
        self.experience_history: List[ExperienceEntry] = []
        self.level_history: List[Dict[str, Any]] = []
        
        # Настройки прогрессии
        self.base_experience_per_level = 100
        self.experience_scaling = 1.5
        self.max_level = 100
        
        # Система наград
        self.unlocked_skills: set = set()
        self.unlocked_content: set = set()
        self.achievements: set = set()
    
    def add_experience(self, category: ExperienceCategory, amount: int, 
                      source: str = "", context: Dict[str, Any] = None) -> bool:
        """Добавление опыта"""
        try:
            if context is None:
                context = {}
            
            # Создаем запись опыта
            entry = ExperienceEntry(
                category=category,
                amount=amount,
                timestamp=time.time(),
                source=source,
                context=context
            )
            
            # Добавляем опыт
            self.experience[category] += amount
            self.total_experience += amount
            self.experience_history.append(entry)
            
            # Проверяем повышение уровня
            self._check_level_up()
            
            logger.debug(f"Добавлен опыт {amount} в категорию {category.value} для {self.entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления опыта: {e}")
            return False
    
    def _check_level_up(self) -> bool:
        """Проверка повышения уровня"""
        try:
            current_level = self.level
            required_exp = self._get_experience_for_level(current_level + 1)
            
            if self.total_experience >= required_exp and current_level < self.max_level:
                self.level += 1
                
                # Записываем историю повышения
                level_up_data = {
                    "level": self.level,
                    "timestamp": time.time(),
                    "total_experience": self.total_experience,
                    "experience_gained": required_exp - self._get_experience_for_level(current_level)
                }
                self.level_history.append(level_up_data)
                
                # Разблокируем контент
                self._unlock_level_content()
                
                logger.info(f"Повышение уровня {self.entity_id}: {current_level} -> {self.level}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка проверки повышения уровня: {e}")
            
        return False
    
    def _get_experience_for_level(self, level: int) -> int:
        """Получение требуемого опыта для уровня"""
        if level <= 1:
            return 0
        
        # Формула: base * (scaling ^ (level - 1))
        return int(self.base_experience_per_level * (self.experience_scaling ** (level - 2)))
    
    def _unlock_level_content(self) -> None:
        """Разблокировка контента для уровня"""
        # TODO: Реализовать разблокировку контента
        pass
    
    def get_experience_progress(self) -> Dict[str, Any]:
        """Получение прогресса опыта"""
        next_level_exp = self._get_experience_for_level(self.level + 1)
        current_level_exp = self._get_experience_for_level(self.level)
        progress = self.total_experience - current_level_exp
        required = next_level_exp - current_level_exp
        
        return {
            "current_level": self.level,
            "total_experience": self.total_experience,
            "current_level_exp": current_level_exp,
            "next_level_exp": next_level_exp,
            "progress": progress,
            "required": required,
            "progress_percentage": (progress / required * 100) if required > 0 else 100
        }
    
    def get_category_experience(self, category: ExperienceCategory) -> int:
        """Получение опыта по категории"""
        return self.experience.get(category, 0)
    
    def get_experience_summary(self) -> Dict[str, Any]:
        """Получение сводки по опыту"""
        return {
            "entity_id": self.entity_id,
            "level": self.level,
            "total_experience": self.total_experience,
            "category_experience": self.experience.copy(),
            "experience_progress": self.get_experience_progress(),
            "unlocked_skills": list(self.unlocked_skills),
            "unlocked_content": list(self.unlocked_content),
            "achievements": list(self.achievements)
        }

class PlayerMemory(BaseMemory):
    """Память игрока"""
    
    def __init__(self, entity_id: str):
        super().__init__(entity_id)
        
        # Специфичные для игрока настройки
        self.base_experience_per_level = 100
        self.experience_scaling = 1.2  # Медленнее чем у врагов
        self.max_level = 100
        
        # Дополнительные возможности игрока
        self.skill_points = 0
        self.attribute_points = 0
        self.reputation = 0
        
        logger.info(f"Создана память игрока для {entity_id}")
    
    def add_experience(self, category: ExperienceCategory, amount: int, 
                      source: str = "", context: Dict[str, Any] = None, 
                      multiplier: float = 1.0) -> bool:
        """Добавление опыта с множителем"""
        adjusted_amount = int(amount * multiplier)
        return super().add_experience(category, adjusted_amount, source, context)
    
    def _unlock_level_content(self) -> None:
        """Разблокировка контента для игрока"""
        # Даем очки навыков и атрибутов
        self.skill_points += 2
        self.attribute_points += 1
        
        # TODO: Разблокировка новых навыков, доступа к локациям и т.д.
        logger.info(f"Разблокирован контент для игрока {self.entity_id} на уровне {self.level}")

class EnemyMemoryBank(BaseMemory):
    """Общий банк памяти врагов"""
    
    def __init__(self, entity_id: str = "enemy_collective"):
        super().__init__(entity_id)
        
        # Специфичные для врагов настройки
        self.base_experience_per_level = 500  # Больше опыта для эволюции
        self.experience_scaling = 1.8  # Быстрее эволюционируют
        self.max_level = 50  # Максимальный уровень врагов
        
        # Коллективные настройки
        self.shared_skills: set = set()
        self.evolution_stage = 1
        self.adaptation_rate = 0.1
        
        logger.info(f"Создан банк памяти врагов")
    
    def add_experience(self, category: ExperienceCategory, amount: int, 
                      source: str = "", context: Dict[str, Any] = None, 
                      multiplier: float = 0.05) -> bool:
        """Добавление опыта с низким множителем для врагов"""
        adjusted_amount = int(amount * multiplier)
        return super().add_experience(category, adjusted_amount, source, context)
    
    def _unlock_level_content(self) -> None:
        """Разблокировка контента для врагов"""
        # Эволюция врагов
        if self.level % 5 == 0:  # Каждые 5 уровней
            self.evolution_stage += 1
            self.adaptation_rate += 0.05
            
            # TODO: Разблокировка новых способностей врагов
            logger.info(f"Враги эволюционировали до стадии {self.evolution_stage}")
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Получение статуса эволюции врагов"""
        return {
            "evolution_stage": self.evolution_stage,
            "adaptation_rate": self.adaptation_rate,
            "shared_skills": list(self.shared_skills),
            "experience_summary": self.get_experience_summary()
        }

class MemorySystem(BaseComponent):
    """Центральная система управления памятью"""
    
    def __init__(self):
        super().__init__(
            component_id="MemorySystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Хранилище памяти
        self.player_memories: Dict[str, PlayerMemory] = {}
        self.enemy_memory_bank = EnemyMemoryBank()
        
        # Настройки системы
        self.max_player_memories = 100
        self.memory_cleanup_interval = 3600  # 1 час
        self.last_cleanup = time.time()
        
        # Статистика
        self.total_experience_gained = 0
        self.total_level_ups = 0
        self.memory_usage = 0
        
        logger.info("Система памяти инициализирована")
    
    def _on_initialize(self) -> bool:
        """Инициализация системы"""
        try:
            # Создаем банк памяти врагов
            self.enemy_memory_bank = EnemyMemoryBank()
            
            # Регистрируем обработчики событий
            self._register_event_handlers()
            
            logger.info("Система памяти успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы памяти: {e}")
            return False
    
    def _register_event_handlers(self) -> None:
        """Регистрация обработчиков событий"""
        # TODO: Регистрация обработчиков событий
        pass
    
    def register_player(self, player_id: str) -> bool:
        """Регистрация игрока в системе памяти"""
        try:
            if player_id in self.player_memories:
                logger.warning(f"Игрок {player_id} уже зарегистрирован")
                return True
            
            if len(self.player_memories) >= self.max_player_memories:
                logger.error(f"Достигнут лимит игроков в системе памяти")
                return False
            
            # Создаем память для игрока
            player_memory = PlayerMemory(player_id)
            self.player_memories[player_id] = player_memory
            
            logger.info(f"Игрок {player_id} зарегистрирован в системе памяти")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации игрока {player_id}: {e}")
            return False
    
    def unregister_player(self, player_id: str) -> bool:
        """Отмена регистрации игрока"""
        try:
            if player_id in self.player_memories:
                del self.player_memories[player_id]
                logger.info(f"Игрок {player_id} удален из системы памяти")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка удаления игрока {player_id}: {e}")
            return False
    
    def add_player_experience(self, player_id: str, category: ExperienceCategory, 
                            amount: int, source: str = "", 
                            context: Dict[str, Any] = None) -> bool:
        """Добавление опыта игроку"""
        try:
            if player_id not in self.player_memories:
                logger.error(f"Игрок {player_id} не найден в системе памяти")
                return False
            
            player_memory = self.player_memories[player_id]
            success = player_memory.add_experience(category, amount, source, context)
            
            if success:
                self.total_experience_gained += amount
                if player_memory.level > 1:
                    self.total_level_ups += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка добавления опыта игроку {player_id}: {e}")
            return False
    
    def add_enemy_experience(self, category: ExperienceCategory, amount: int, 
                           source: str = "", context: Dict[str, Any] = None) -> bool:
        """Добавление опыта врагам"""
        try:
            success = self.enemy_memory_bank.add_experience(category, amount, source, context)
            
            if success:
                self.total_experience_gained += int(amount * 0.05)  # Учитываем множитель
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка добавления опыта врагам: {e}")
            return False
    
    def get_player_memory(self, player_id: str) -> Optional[PlayerMemory]:
        """Получение памяти игрока"""
        return self.player_memories.get(player_id)
    
    def get_enemy_memory_bank(self) -> EnemyMemoryBank:
        """Получение банка памяти врагов"""
        return self.enemy_memory_bank
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Получение сводки по системе памяти"""
        return {
            "total_players": len(self.player_memories),
            "total_experience_gained": self.total_experience_gained,
            "total_level_ups": self.total_level_ups,
            "enemy_evolution_stage": self.enemy_memory_bank.evolution_stage,
            "memory_usage": self.memory_usage,
            "system_status": "active"
        }
    
    def update(self, delta_time: float):
        """Обновление системы памяти"""
        try:
            current_time = time.time()
            
            # Очистка старых записей
            if current_time - self.last_cleanup > self.memory_cleanup_interval:
                self._cleanup_old_memories()
                self.last_cleanup = current_time
            
            # Обновление статистики
            self._update_statistics()
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы памяти: {e}")
    
    def _cleanup_old_memories(self) -> None:
        """Очистка старых записей памяти"""
        try:
            current_time = time.time()
            max_age = 86400  # 24 часа
            
            for player_memory in self.player_memories.values():
                # Удаляем записи старше 24 часов
                player_memory.experience_history = [
                    entry for entry in player_memory.experience_history
                    if current_time - entry.timestamp < max_age
                ]
            
            # Очищаем историю врагов
            self.enemy_memory_bank.experience_history = [
                entry for entry in self.enemy_memory_bank.experience_history
                if current_time - entry.timestamp < max_age
            ]
            
            logger.debug("Выполнена очистка старых записей памяти")
            
        except Exception as e:
            logger.error(f"Ошибка очистки памяти: {e}")
    
    def _update_statistics(self) -> None:
        """Обновление статистики системы"""
        try:
            # Подсчитываем использование памяти
            total_entries = 0
            for player_memory in self.player_memories.values():
                total_entries += len(player_memory.experience_history)
                total_entries += len(player_memory.level_history)
            
            total_entries += len(self.enemy_memory_bank.experience_history)
            total_entries += len(self.enemy_memory_bank.level_history)
            
            self.memory_usage = total_entries
            
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
    
    def _on_destroy(self) -> None:
        """Уничтожение системы памяти"""
        try:
            # Очищаем все данные
            self.player_memories.clear()
            self.enemy_memory_bank = None
            
            logger.info("Система памяти уничтожена")
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы памяти: {e}")
