#!/usr/bin/env python3
"""
Система крафтинга - управление созданием предметов и рецептами крафтинга
"""

import logging
import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)

class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    ACCESSORY = "accessory"
    MATERIAL = "material"
    TOOL = "tool"
    SPECIAL = "special"

class ItemRarity(Enum):
    """Редкость предметов"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class CraftingDifficulty(Enum):
    """Сложность крафтинга"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"

@dataclass
class Item:
    """Предмет"""
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    value: int
    weight: float
    stackable: bool = False
    max_stack: int = 1
    effects: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = {}

@dataclass
class Recipe:
    """Рецепт крафтинга"""
    id: str
    name: str
    description: str
    result_item: str
    result_quantity: int = 1
    ingredients: Dict[str, int] = None
    required_tools: List[str] = None
    required_skills: Dict[str, int] = None
    difficulty: CraftingDifficulty = CraftingDifficulty.EASY
    crafting_time: float = 1.0
    experience_gain: int = 10
    failure_chance: float = 0.0
    
    def __post_init__(self):
        if self.ingredients is None:
            self.ingredients = {}
        if self.required_tools is None:
            self.required_tools = []
        if self.required_skills is None:
            self.required_skills = {}

@dataclass
class CraftingResult:
    """Результат крафтинга"""
    success: bool = False
    item_created: Optional[Item] = None
    quantity_created: int = 0
    experience_gained: int = 0
    materials_used: Dict[str, int] = None
    failure_reason: str = ""
    quality: float = 1.0
    
    def __post_init__(self):
        if self.materials_used is None:
            self.materials_used = {}

class CraftingSystem(ISystem):
    """Система крафтинга для всех сущностей"""
    
    def __init__(self):
        self._system_name = "crafting"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Предметы в системе
        self.items: Dict[str, Item] = {}
        
        # Рецепты крафтинга
        self.recipes: Dict[str, Recipe] = {}
        
        # Станции крафтинга
        self.crafting_stations: Dict[str, Dict[str, Any]] = {}
        
        # Активные крафты
        self.active_crafts: Dict[str, Dict[str, Any]] = {}
        
        # Навыки крафтеров
        self.crafting_skills: Dict[str, Dict[str, int]] = {}
        
        # Статистика системы
        self.system_stats = {
            'items_count': 0,
            'recipes_count': 0,
            'crafters_count': 0,
            'active_crafts_count': 0,
            'crafts_completed': 0,
            'crafts_failed': 0,
            'update_time': 0.0
        }
        
        logger.info("Система крафтинга инициализирована")
    
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
        """Инициализация системы крафтинга"""
        try:
            logger.info("Инициализация системы крафтинга...")
            
            # Настраиваем базовые предметы
            self._setup_default_items()
            
            # Настраиваем базовые рецепты
            self._setup_default_recipes()
            
            # Настраиваем станции крафтинга
            self._setup_crafting_stations()
            
            # Обновляем статистику
            self._update_system_stats()
            
            self._system_state = SystemState.READY
            logger.info("Система крафтинга успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы крафтинга: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы крафтинга"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем активные крафты
            self._update_active_craftings(delta_time)
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы крафтинга: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы крафтинга"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система крафтинга приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы крафтинга: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы крафтинга"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система крафтинга возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы крафтинга: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы крафтинга"""
        try:
            logger.info("Очистка системы крафтинга...")
            
            # Очищаем все данные
            self.items.clear()
            self.recipes.clear()
            self.crafting_stations.clear()
            self.active_crafts.clear()
            self.crafting_skills.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'items_count': 0,
                'recipes_count': 0,
                'crafters_count': 0,
                'active_crafts_count': 0,
                'crafts_completed': 0,
                'crafts_failed': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система крафтинга очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы крафтинга: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'items_count': len(self.items),
            'recipes_count': len(self.recipes),
            'crafters_count': len(self.crafting_skills),
            'active_crafts_count': len(self.active_crafts),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "crafting_started":
                return self._handle_crafting_started(event_data)
            elif event_type == "crafting_completed":
                return self._handle_crafting_completed(event_data)
            elif event_type == "skill_gained":
                return self._handle_skill_gained(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def register_crafter(self, crafter_id: str, initial_skills: Dict[str, int] = None) -> bool:
        """Регистрация крафтера в системе"""
        try:
            if crafter_id in self.crafting_skills:
                logger.warning(f"Крафтер {crafter_id} уже зарегистрирован")
                return False
            
            if initial_skills is None:
                initial_skills = {}
            
            # Базовые навыки
            base_skills = {
                "blacksmithing": 0,
                "woodworking": 0,
                "leatherworking": 0,
                "alchemy": 0,
                "cooking": 0,
                "jewelcrafting": 0
            }
            
            # Обновляем базовые навыки начальными значениями
            base_skills.update(initial_skills)
            
            self.crafting_skills[crafter_id] = base_skills
            self._update_system_stats()
            
            logger.info(f"Крафтер {crafter_id} зарегистрирован в системе крафтинга")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации крафтера {crafter_id}: {e}")
            return False
    
    def unregister_crafter(self, crafter_id: str) -> bool:
        """Отмена регистрации крафтера"""
        try:
            if crafter_id in self.crafting_skills:
                del self.crafting_skills[crafter_id]
            
            # Удаляем активные крафты
            for craft_id in list(self.active_crafts.keys()):
                if self.active_crafts[craft_id]["crafter_id"] == crafter_id:
                    del self.active_crafts[craft_id]
            
            self._update_system_stats()
            logger.info(f"Крафтер {crafter_id} удален из системы крафтинга")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления крафтера {crafter_id}: {e}")
            return False
    
    def can_craft(self, crafter_id: str, recipe_id: str, inventory: Dict[str, int]) -> Tuple[bool, str]:
        """Проверка возможности крафтинга"""
        try:
            if crafter_id not in self.crafting_skills:
                return False, "Крафтер не зарегистрирован"
            
            if recipe_id not in self.recipes:
                return False, "Рецепт не найден"
            
            recipe = self.recipes[recipe_id]
            skills = self.crafting_skills[crafter_id]
            
            # Проверяем навыки
            for skill, required_level in recipe.required_skills.items():
                if skills.get(skill, 0) < required_level:
                    return False, f"Недостаточный уровень навыка {skill}: {skills.get(skill, 0)}/{required_level}"
            
            # Проверяем ингредиенты
            for ingredient, quantity in recipe.ingredients.items():
                if inventory.get(ingredient, 0) < quantity:
                    return False, f"Недостаточно {ingredient}: {inventory.get(ingredient, 0)}/{quantity}"
            
            return True, "Можно крафтить"
            
        except Exception as e:
            logger.error(f"Ошибка проверки возможности крафтинга: {e}")
            return False, f"Ошибка проверки: {e}"
    
    def start_crafting(self, crafter_id: str, recipe_id: str, station_id: str = None) -> Optional[str]:
        """Начало крафтинга"""
        try:
            if crafter_id not in self.crafting_skills:
                logger.error(f"Крафтер {crafter_id} не зарегистрирован")
                return None
            
            if recipe_id not in self.recipes:
                logger.error(f"Рецепт {recipe_id} не найден")
                return None
            
            recipe = self.recipes[recipe_id]
            
            # Проверяем станцию крафтинга
            if station_id and station_id in self.crafting_stations:
                station = self.crafting_stations[station_id]
                if recipe.result_item in self.items:
                    result_item = self.items[recipe.result_item]
                    if result_item.item_type not in station["allowed_types"]:
                        logger.warning(f"Станция {station_id} не подходит для крафтинга {recipe_id}")
                        station_id = None
            
            # Создаем крафт
            craft_id = f"craft_{crafter_id}_{recipe_id}_{random.randint(1000, 9999)}"
            craft = {
                "id": craft_id,
                "crafter_id": crafter_id,
                "recipe_id": recipe_id,
                "station_id": station_id,
                "start_time": 0.0,
                "progress": 0.0,
                "status": "active"
            }
            
            self.active_crafts[craft_id] = craft
            self._update_system_stats()
            
            logger.info(f"Крафт {craft_id} начат: {crafter_id} создает {recipe.name}")
            return craft_id
            
        except Exception as e:
            logger.error(f"Ошибка начала крафтинга: {e}")
            return None
    
    def get_crafting_info(self, crafter_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о крафтере"""
        try:
            if crafter_id not in self.crafting_skills:
                return None
            
            skills = self.crafting_skills[crafter_id]
            
            # Находим активные крафты
            active_crafts = []
            for craft_id, craft in self.active_crafts.items():
                if craft["crafter_id"] == crafter_id and craft["status"] == "active":
                    active_crafts.append({
                        "id": craft_id,
                        "recipe": self.recipes[craft["recipe_id"]].name,
                        "progress": craft["progress"],
                        "time_remaining": max(0, self.recipes[craft["recipe_id"]].crafting_time - craft["start_time"])
                    })
            
            return {
                "crafter_id": crafter_id,
                "skills": skills,
                "active_crafts": active_crafts,
                "available_recipes": self._get_available_recipes(crafter_id)
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о крафтере {crafter_id}: {e}")
            return None
    
    def get_recipe_info(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о рецепте"""
        try:
            if recipe_id not in self.recipes:
                return None
            
            recipe = self.recipes[recipe_id]
            result_item = self.items.get(recipe.result_item)
            
            return {
                "id": recipe_id,
                "name": recipe.name,
                "description": recipe.description,
                "result_item": {
                    "id": recipe.result_item,
                    "name": result_item.name if result_item else "Unknown",
                    "type": result_item.item_type.value if result_item else "unknown",
                    "rarity": result_item.rarity.value if result_item else "unknown"
                },
                "result_quantity": recipe.result_quantity,
                "ingredients": recipe.ingredients,
                "required_tools": recipe.required_tools,
                "required_skills": recipe.required_skills,
                "difficulty": recipe.difficulty.value,
                "crafting_time": recipe.crafting_time,
                "experience_gain": recipe.experience_gain,
                "failure_chance": recipe.failure_chance
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о рецепте {recipe_id}: {e}")
            return None
    
    def _setup_default_items(self) -> None:
        """Настройка базовых предметов"""
        try:
            # Материалы
            self.items["wood"] = Item(
                id="wood",
                name="Дерево",
                description="Базовый материал для крафтинга",
                item_type=ItemType.MATERIAL,
                rarity=ItemRarity.COMMON,
                value=1,
                weight=0.1,
                stackable=True,
                max_stack=100
            )
            
            self.items["stone"] = Item(
                id="stone",
                name="Камень",
                description="Прочный материал для строительства",
                item_type=ItemType.MATERIAL,
                rarity=ItemRarity.COMMON,
                value=2,
                weight=0.5,
                stackable=True,
                max_stack=100
            )
            
            self.items["iron_ore"] = Item(
                id="iron_ore",
                name="Железная руда",
                description="Руда для выплавки железа",
                item_type=ItemType.MATERIAL,
                rarity=ItemRarity.UNCOMMON,
                value=5,
                weight=1.0,
                stackable=True,
                max_stack=50
            )
            
            # Оружие
            self.items["wooden_sword"] = Item(
                id="wooden_sword",
                name="Деревянный меч",
                description="Простое деревянное оружие",
                item_type=ItemType.WEAPON,
                rarity=ItemRarity.COMMON,
                value=10,
                weight=1.0,
                effects={"attack": 5, "durability": 50}
            )
            
            self.items["iron_sword"] = Item(
                id="iron_sword",
                name="Железный меч",
                description="Надежное железное оружие",
                item_type=ItemType.WEAPON,
                rarity=ItemRarity.UNCOMMON,
                value=25,
                weight=2.0,
                effects={"attack": 12, "durability": 100}
            )
            
            # Броня
            self.items["leather_armor"] = Item(
                id="leather_armor",
                name="Кожаная броня",
                description="Легкая кожаная защита",
                item_type=ItemType.ARMOR,
                rarity=ItemRarity.COMMON,
                value=15,
                weight=3.0,
                effects={"defense": 3, "movement_penalty": 0.1}
            )
            
            # Инструменты
            self.items["crafting_hammer"] = Item(
                id="crafting_hammer",
                name="Молот крафтера",
                description="Инструмент для крафтинга",
                item_type=ItemType.TOOL,
                rarity=ItemRarity.COMMON,
                value=8,
                weight=1.5,
                effects={"crafting_bonus": 0.1}
            )
            
            # Расходники
            self.items["health_potion"] = Item(
                id="health_potion",
                name="Зелье здоровья",
                description="Восстанавливает здоровье",
                item_type=ItemType.CONSUMABLE,
                rarity=ItemRarity.COMMON,
                value=5,
                weight=0.2,
                stackable=True,
                max_stack=10,
                effects={"heal": 25}
            )
            
            logger.debug("Базовые предметы инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать базовые предметы: {e}")
    
    def _setup_default_recipes(self) -> None:
        """Настройка базовых рецептов"""
        try:
            # Деревянный меч
            self.recipes["wooden_sword"] = Recipe(
                id="wooden_sword",
                name="Деревянный меч",
                description="Создание простого деревянного меча",
                result_item="wooden_sword",
                result_quantity=1,
                ingredients={"wood": 3},
                required_tools=["crafting_hammer"],
                difficulty=CraftingDifficulty.EASY,
                crafting_time=2.0,
                experience_gain=15
            )
            
            # Железный меч
            self.recipes["iron_sword"] = Recipe(
                id="iron_sword",
                name="Железный меч",
                description="Создание железного меча",
                result_item="iron_sword",
                result_quantity=1,
                ingredients={"iron_ore": 2, "wood": 1},
                required_tools=["crafting_hammer"],
                required_skills={"blacksmithing": 5},
                difficulty=CraftingDifficulty.MEDIUM,
                crafting_time=5.0,
                experience_gain=30
            )
            
            # Кожаная броня
            self.recipes["leather_armor"] = Recipe(
                id="leather_armor",
                name="Кожаная броня",
                description="Создание кожаной брони",
                result_item="leather_armor",
                result_quantity=1,
                ingredients={"leather": 4, "thread": 2},
                required_tools=["sewing_kit"],
                required_skills={"leatherworking": 3},
                difficulty=CraftingDifficulty.MEDIUM,
                crafting_time=4.0,
                experience_gain=25
            )
            
            # Зелье здоровья
            self.recipes["health_potion"] = Recipe(
                id="health_potion",
                name="Зелье здоровья",
                description="Создание зелья здоровья",
                result_item="health_potion",
                result_quantity=3,
                ingredients={"herb": 2, "water": 1},
                required_tools=["alchemy_set"],
                required_skills={"alchemy": 2},
                difficulty=CraftingDifficulty.EASY,
                crafting_time=1.5,
                experience_gain=20
            )
            
            logger.debug("Базовые рецепты инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать базовые рецепты: {e}")
    
    def _setup_crafting_stations(self) -> None:
        """Настройка станций крафтинга"""
        try:
            self.crafting_stations = {
                "anvil": {
                    "name": "Наковальня",
                    "description": "Станция для кузнечного дела",
                    "allowed_types": [ItemType.WEAPON, ItemType.ARMOR],
                    "skill_bonus": {"blacksmithing": 0.2},
                    "quality_bonus": 0.1
                },
                "workbench": {
                    "name": "Верстак",
                    "description": "Станция для столярного дела",
                    "allowed_types": [ItemType.WEAPON, ItemType.TOOL],
                    "skill_bonus": {"woodworking": 0.2},
                    "quality_bonus": 0.1
                },
                "alchemy_table": {
                    "name": "Алхимический стол",
                    "description": "Станция для алхимии",
                    "allowed_types": [ItemType.CONSUMABLE],
                    "skill_bonus": {"alchemy": 0.2},
                    "quality_bonus": 0.15
                }
            }
            
            logger.debug("Станции крафтинга инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать станции крафтинга: {e}")
    
    def _update_active_craftings(self, delta_time: float) -> None:
        """Обновление активных крафтов"""
        try:
            for craft_id in list(self.active_crafts.keys()):
                craft = self.active_crafts[craft_id]
                
                if craft["status"] != "active":
                    continue
                
                recipe = self.recipes[craft["recipe_id"]]
                
                # Обновляем прогресс
                craft["start_time"] += delta_time
                craft["progress"] = min(1.0, craft["start_time"] / recipe.crafting_time)
                
                # Проверяем завершение
                if craft["progress"] >= 1.0:
                    self._complete_craft(craft_id)
                    
        except Exception as e:
            logger.warning(f"Ошибка обновления активных крафтов: {e}")
    
    def _complete_craft(self, craft_id: str) -> None:
        """Завершение крафта"""
        try:
            craft = self.active_crafts[craft_id]
            crafter_id = craft["crafter_id"]
            recipe_id = craft["recipe_id"]
            station_id = craft["station_id"]
            
            recipe = self.recipes[recipe_id]
            skills = self.crafting_skills[crafter_id]
            
            # Рассчитываем успех крафтинга
            success_chance = self._calculate_success_chance(crafter_id, recipe_id, station_id)
            success = random.random() > recipe.failure_chance * (1.0 - success_chance)
            
            if success:
                # Создаем предмет
                result_item = self.items[recipe.result_item]
                quality = self._calculate_quality(crafter_id, recipe_id, station_id)
                
                # Рассчитываем количество созданных предметов
                base_quantity = recipe.result_quantity
                if quality > 1.2:  # Высокое качество
                    quantity_created = base_quantity + 1
                elif quality < 0.8:  # Низкое качество
                    quantity_created = max(1, base_quantity - 1)
                else:
                    quantity_created = base_quantity
                
                # Рассчитываем опыт
                experience_gained = int(recipe.experience_gain * quality)
                
                # Обновляем навыки
                for skill, required_level in recipe.required_skills.items():
                    if skill in skills:
                        skills[skill] += 1
                
                result = CraftingResult(
                    success=True,
                    item_created=result_item,
                    quantity_created=quantity_created,
                    experience_gained=experience_gained,
                    quality=quality
                )
                
                self.system_stats['crafts_completed'] += 1
                logger.info(f"Крафт {craft_id} успешно завершен: создано {quantity_created}x {result_item.name}")
                
            else:
                result = CraftingResult(
                    success=False,
                    failure_reason="Неудачный крафтинг"
                )
                
                self.system_stats['crafts_failed'] += 1
                logger.info(f"Крафт {craft_id} провалился")
            
            # Завершаем крафт
            craft["status"] = "completed"
            craft["result"] = result
            
        except Exception as e:
            logger.error(f"Ошибка завершения крафта {craft_id}: {e}")
    
    def _calculate_success_chance(self, crafter_id: str, recipe_id: str, station_id: str) -> float:
        """Расчет шанса успеха крафтинга"""
        try:
            base_chance = 0.8
            
            skills = self.crafting_skills[crafter_id]
            recipe = self.recipes[recipe_id]
            
            # Бонус от навыков
            skill_bonus = 0.0
            for skill, required_level in recipe.required_skills.items():
                if skill in skills:
                    skill_level = skills[skill]
                    if skill_level > required_level:
                        skill_bonus += min(0.2, (skill_level - required_level) * 0.02)
            
            # Бонус от станции
            station_bonus = 0.0
            if station_id and station_id in self.crafting_stations:
                station = self.crafting_stations[station_id]
                for skill, bonus in station["skill_bonus"].items():
                    if skill in skills:
                        station_bonus += bonus
            
            return min(0.95, base_chance + skill_bonus + station_bonus)
            
        except Exception as e:
            logger.warning(f"Ошибка расчета шанса успеха: {e}")
            return 0.8
    
    def _calculate_quality(self, crafter_id: str, recipe_id: str, station_id: str) -> float:
        """Расчет качества созданного предмета"""
        try:
            base_quality = 1.0
            
            skills = self.crafting_skills[crafter_id]
            recipe = self.recipes[recipe_id]
            
            # Бонус от навыков
            skill_bonus = 0.0
            for skill, required_level in recipe.required_skills.items():
                if skill in skills:
                    skill_level = skills[skill]
                    if skill_level > required_level:
                        skill_bonus += min(0.3, (skill_level - required_level) * 0.01)
            
            # Бонус от станции
            station_bonus = 0.0
            if station_id and station_id in self.crafting_stations:
                station = self.crafting_stations[station_id]
                station_bonus = station["quality_bonus"]
            
            # Случайный фактор
            random_factor = random.uniform(0.9, 1.1)
            
            return base_quality + skill_bonus + station_bonus + random_factor
            
        except Exception as e:
            logger.warning(f"Ошибка расчета качества: {e}")
            return 1.0
    
    def _get_available_recipes(self, crafter_id: str) -> List[Dict[str, Any]]:
        """Получение доступных рецептов для крафтера"""
        try:
            available = []
            skills = self.crafting_skills[crafter_id]
            
            for recipe_id, recipe in self.recipes.items():
                can_craft = True
                missing_skills = []
                
                for skill, required_level in recipe.required_skills.items():
                    if skills.get(skill, 0) < required_level:
                        can_craft = False
                        missing_skills.append(f"{skill}: {skills.get(skill, 0)}/{required_level}")
                
                if can_craft:
                    available.append({
                        "id": recipe_id,
                        "name": recipe.name,
                        "description": recipe.description,
                        "difficulty": recipe.difficulty.value,
                        "crafting_time": recipe.crafting_time,
                        "experience_gain": recipe.experience_gain
                    })
            
            return available
            
        except Exception as e:
            logger.warning(f"Ошибка получения доступных рецептов: {e}")
            return []
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['items_count'] = len(self.items)
            self.system_stats['recipes_count'] = len(self.recipes)
            self.system_stats['crafters_count'] = len(self.crafting_skills)
            self.system_stats['active_crafts_count'] = len([c for c in self.active_crafts.values() if c["status"] == "active"])
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            initial_skills = event_data.get('initial_skills', {})
            
            if entity_id:
                return self.register_crafter(entity_id, initial_skills)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_crafting_started(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события начала крафтинга"""
        try:
            crafter_id = event_data.get('crafter_id')
            recipe_id = event_data.get('recipe_id')
            station_id = event_data.get('station_id')
            
            if crafter_id and recipe_id:
                craft_id = self.start_crafting(crafter_id, recipe_id, station_id)
                return craft_id is not None
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события начала крафтинга: {e}")
            return False
    
    def _handle_crafting_completed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события завершения крафтинга"""
        try:
            craft_id = event_data.get('craft_id')
            
            if craft_id and craft_id in self.active_crafts:
                craft = self.active_crafts[craft_id]
                if craft["status"] == "completed":
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события завершения крафтинга: {e}")
            return False
    
    def _handle_skill_gained(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события получения навыка"""
        try:
            entity_id = event_data.get('entity_id')
            skill_name = event_data.get('skill_name')
            skill_level = event_data.get('skill_level', 1)
            
            if entity_id and skill_name and entity_id in self.crafting_skills:
                self.crafting_skills[entity_id][skill_name] = skill_level
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события получения навыка: {e}")
            return False
