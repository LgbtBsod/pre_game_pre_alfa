from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from src.core.architecture import BaseComponent, ComponentType, Priority
from typing import *
from typing import Dict, List, Optional, Any, Union
import logging
import os
import random
import sys
import time

#!/usr/bin/env python3
"""Система крафтинга - создание предметов из материалов"""

logger = logging.getLogger(__name__)

# = ОСНОВНЫЕ ТИПЫ И ПЕРЕЧИСЛЕНИЯ

class CraftingType(Enum):
    """Типы крафтинга"""
    WEAPON = "weapon"
    ARMOR = "armor"
    TOOL = "tool"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    SPECIAL = "special"

class CraftingDifficulty(Enum):
    """Сложность крафтинга"""
    TRIVIAL = "trivial"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"

class CraftingStatus(Enum):
    """Статус крафтинга"""
    IDLE = "idle"
    CRAFTING = "crafting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class Recipe:
    """Рецепт крафтинга"""
    recipe_id: str
    name: str
    description: str
    category: str
    difficulty: int = 1  # 1 - 10
    required_level: int = 1
    crafting_time: float = 1.0  # секунды
    experience_gain: int = 10
    success_chance: float = 1.0
    materials: Dict[str, int] = field(default_factory=dict)  # item_id: count
    tools: List[str] = field(default_factory=list)  # required tools
    result_item: str = ""
    result_count: int = 1
    result_quality: float = 1.0
    unlock_conditions: Dict[str, Any] = field(default_factory=dict)
    is_discovered: bool = False
    discovery_chance: float = 0.1

@dataclass
class CraftingSession:
    """Сессия крафтинга"""
    session_id: str
    entity_id: str
    recipe_id: str
    start_time: float = field(default_factory=time.time)
    progress: float = 0.0  # 0.0 - 1.0
    is_completed: bool = False
    is_failed: bool = False
    result_items: List[str] = field(default_factory=list)
    experience_gained: int = 0
    materials_used: Dict[str, int] = field(default_factory=dict)

@dataclass
class CraftingResult:
    """Результат крафтинга"""
    success: bool
    item_id: str = ""
    item_count: int = 0
    quality: float = 1.0
    experience_gained: int = 0
    materials_consumed: Dict[str, int] = field(default_factory=dict)
    error_message: str = ""
    crafting_time: float = 0.0

@dataclass
class CraftingStation:
    """Станция крафтинга"""
    station_id: str
    name: str
    description: str
    station_type: CraftingType
    location: Tuple[float, float, float]
    available_recipes: List[str] = field(default_factory=list)
    efficiency_bonus: float = 1.0
    quality_bonus: float = 1.0
    is_active: bool = True

class CraftingSystem(BaseComponent):
    """Система крафтинга"""
    
    def __init__(self):
        super().__init__(
            component_id="crafting_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.NORMAL
        )
        
        # Данные системы
        self.recipes: Dict[str, Recipe] = {}
        self.active_sessions: Dict[str, CraftingSession] = {}
        self.crafting_stations: Dict[str, CraftingStation] = {}
        self.crafting_history: List[CraftingResult] = []
        
        # Статистика
        self.total_crafts: int = 0
        self.successful_crafts: int = 0
        self.failed_crafts: int = 0
        self.total_experience_gained: int = 0
        
        # Callbacks
        self.on_craft_start: Optional[Callable] = None
        self.on_craft_complete: Optional[Callable] = None
        self.on_craft_fail: Optional[Callable] = None
        
        logger.info("Система крафтинга инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы крафтинга"""
        try:
            logger.info("Инициализация системы крафтинга...")
            
            # Загрузка рецептов
            self._load_recipes()
            
            # Создание станций крафтинга
            self._create_crafting_stations()
            
            self.state = LifecycleState.READY
            logger.info("Система крафтинга успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы крафтинга: {e}")
            self.state = LifecycleState.ERROR
            return False
    
    def _load_recipes(self):
        """Загрузка рецептов крафтинга"""
        # Базовые рецепты
        basic_recipes = [
            Recipe(
                recipe_id="basic_sword",
                name="Базовый меч",
                description="Простой железный меч",
                category="weapon",
                difficulty=2,
                materials={"iron_ingot": 2, "wood": 1},
                tools=["forge"],
                result_item="basic_sword",
                result_count=1
            ),
            Recipe(
                recipe_id="basic_armor",
                name="Базовая броня",
                description="Простая кожаная броня",
                category="armor",
                difficulty=3,
                materials={"leather": 3, "thread": 1},
                tools=["workbench"],
                result_item="basic_armor",
                result_count=1
            ),
            Recipe(
                recipe_id="health_potion",
                name="Зелье здоровья",
                description="Восстанавливает здоровье",
                category="consumable",
                difficulty=1,
                materials={"herb": 2, "water": 1},
                tools=["alchemy_station"],
                result_item="health_potion",
                result_count=1
            )
        ]
        
        for recipe in basic_recipes:
            self.recipes[recipe.recipe_id] = recipe
        
        logger.info(f"Загружено {len(self.recipes)} рецептов")
    
    def _create_crafting_stations(self):
        """Создание станций крафтинга"""
        stations = [
            CraftingStation(
                station_id="forge",
                name="Кузница",
                description="Кузница для создания оружия",
                station_type=CraftingType.WEAPON,
                location=(0, 0, 0),
                available_recipes=["basic_sword"]
            ),
            CraftingStation(
                station_id="workbench",
                name="Верстак",
                description="Верстак для создания брони",
                station_type=CraftingType.ARMOR,
                location=(5, 0, 0),
                available_recipes=["basic_armor"]
            ),
            CraftingStation(
                station_id="alchemy_station",
                name="Алхимическая станция",
                description="Станция для создания зелий",
                station_type=CraftingType.CONSUMABLE,
                location=(0, 5, 0),
                available_recipes=["health_potion"]
            )
        ]
        
        for station in stations:
            self.crafting_stations[station.station_id] = station
        
        logger.info(f"Создано {len(self.crafting_stations)} станций крафтинга")
    
    def start_crafting(self, entity_id: str, recipe_id: str, station_id: str) -> Optional[str]:
        """Начать крафтинг"""
        try:
            if recipe_id not in self.recipes:
                logger.error(f"Рецепт {recipe_id} не найден")
                return None
            
            if station_id not in self.crafting_stations:
                logger.error(f"Станция {station_id} не найдена")
                return None
            
            recipe = self.recipes[recipe_id]
            station = self.crafting_stations[station_id]
            
            # Проверка доступности рецепта на станции
            if recipe_id not in station.available_recipes:
                logger.error(f"Рецепт {recipe_id} недоступен на станции {station_id}")
                return None
            
            # Создание сессии крафтинга
            session_id = f"craft_{entity_id}_{int(time.time())}"
            session = CraftingSession(
                session_id=session_id,
                entity_id=entity_id,
                recipe_id=recipe_id
            )
            
            self.active_sessions[session_id] = session
            
            # Вызов callback
            if self.on_craft_start:
                self.on_craft_start(session)
            
            logger.info(f"Начат крафтинг {recipe_id} для {entity_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Ошибка начала крафтинга: {e}")
            return None
    
    def update_crafting(self, session_id: str, delta_time: float) -> bool:
        """Обновление прогресса крафтинга"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            recipe = self.recipes[session.recipe_id]
            
            # Обновление прогресса
            progress_increment = delta_time / recipe.crafting_time
            session.progress += progress_increment
            
            # Проверка завершения
            if session.progress >= 1.0:
                return self._complete_crafting(session_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления крафтинга: {e}")
            return False
    
    def _complete_crafting(self, session_id: str) -> bool:
        """Завершение крафтинга"""
        try:
            session = self.active_sessions[session_id]
            recipe = self.recipes[session.recipe_id]
            
            # Расчет успеха
            success = random.random() <= recipe.success_chance
            
            if success:
                # Успешный крафтинг
                result = CraftingResult(
                    success=True,
                    item_id=recipe.result_item,
                    item_count=recipe.result_count,
                    quality=recipe.result_quality,
                    experience_gained=recipe.experience_gain,
                    crafting_time=recipe.crafting_time
                )
                
                session.is_completed = True
                session.result_items.append(recipe.result_item)
                session.experience_gained = recipe.experience_gain
                
                self.successful_crafts += 1
                self.total_experience_gained += recipe.experience_gain
                
                # Вызов callback
                if self.on_craft_complete:
                    self.on_craft_complete(session, result)
                
                logger.info(f"Крафтинг {session.recipe_id} завершен успешно")
                
            else:
                # Неудачный крафтинг
                result = CraftingResult(
                    success=False,
                    error_message="Крафтинг не удался",
                    crafting_time=recipe.crafting_time
                )
                
                session.is_failed = True
                self.failed_crafts += 1
                
                # Вызов callback
                if self.on_craft_fail:
                    self.on_craft_fail(session, result)
                
                logger.info(f"Крафтинг {session.recipe_id} не удался")
            
            # Сохранение результата
            self.crafting_history.append(result)
            self.total_crafts += 1
            
            # Удаление сессии
            del self.active_sessions[session_id]
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка завершения крафтинга: {e}")
            return False
    
    def cancel_crafting(self, session_id: str) -> bool:
        """Отмена крафтинга"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session.is_failed = True
            
            del self.active_sessions[session_id]
            
            logger.info(f"Крафтинг {session.recipe_id} отменен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отмены крафтинга: {e}")
            return False
    
    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Получить рецепт"""
        return self.recipes.get(recipe_id)
    
    def get_available_recipes(self, station_id: str) -> List[Recipe]:
        """Получить доступные рецепты для станции"""
        if station_id not in self.crafting_stations:
            return []
        
        station = self.crafting_stations[station_id]
        return [self.recipes[recipe_id] for recipe_id in station.available_recipes 
                if recipe_id in self.recipes]
    
    def get_crafting_statistics(self) -> Dict[str, Any]:
        """Получить статистику крафтинга"""
        return {
            "total_crafts": self.total_crafts,
            "successful_crafts": self.successful_crafts,
            "failed_crafts": self.failed_crafts,
            "success_rate": self.successful_crafts / max(self.total_crafts, 1),
            "total_experience_gained": self.total_experience_gained,
            "active_sessions": len(self.active_sessions)
        }
    
    def update(self, delta_time: float):
        """Обновление системы крафтинга"""
        try:
            # Обновление активных сессий
            completed_sessions = []
            for session_id, session in self.active_sessions.items():
                if not self.update_crafting(session_id, delta_time):
                    completed_sessions.append(session_id)
            
            # Удаление завершенных сессий
            for session_id in completed_sessions:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                    
        except Exception as e:
            logger.error(f"Ошибка обновления системы крафтинга: {e}")
    
    def cleanup(self):
        """Очистка системы крафтинга"""
        try:
            # Отмена всех активных сессий
            for session_id in list(self.active_sessions.keys()):
                self.cancel_crafting(session_id)
            
            logger.info("Система крафтинга очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы крафтинга: {e}")
