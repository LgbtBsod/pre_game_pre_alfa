#!/usr/bin/env python3
"""
Система крафтинга и ремёсел для эволюционной адаптации.
Управляет созданием предметов, рецептами и навыками ремёсел.
"""

import random
import json
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CraftingCategory(Enum):
    """Категории крафтинга"""
    WEAPONSMITHING = "weaponsmithing"
    ARMORSMITHING = "armorsmithing"
    ALCHEMY = "alchemy"
    ENCHANTING = "enchanting"
    GENETIC_ENGINEERING = "genetic_engineering"
    NANOTECH = "nanotech"
    QUANTUM_CRAFTING = "quantum_crafting"
    COSMIC_FORGING = "cosmic_forging"


class RecipeDifficulty(Enum):
    """Сложность рецепта"""
    BEGINNER = "beginner"
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    EXPERT = "expert"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    LEGENDARY = "legendary"


@dataclass
class CraftingIngredient:
    """Ингредиент для крафтинга"""
    item_id: str
    quantity: int
    quality_required: float = 1.0
    is_optional: bool = False
    alternatives: List[str] = field(default_factory=list)


@dataclass
class CraftingTool:
    """Инструмент для крафтинга"""
    tool_id: str
    name: str
    category: CraftingCategory
    efficiency: float = 1.0
    durability: float = 100.0
    max_durability: float = 100.0
    quality_bonus: float = 0.0
    
    def use_tool(self, wear_amount: float = 1.0):
        """Использование инструмента"""
        self.durability = max(0.0, self.durability - wear_amount)
    
    def can_use(self) -> bool:
        """Проверка возможности использования"""
        return self.durability > 0.0
    
    def repair(self, amount: float):
        """Ремонт инструмента"""
        self.durability = min(self.max_durability, self.durability + amount)


@dataclass
class CraftingRecipe:
    """Рецепт крафтинга"""
    recipe_id: str
    name: str
    description: str
    category: CraftingCategory
    difficulty: RecipeDifficulty
    ingredients: List[CraftingIngredient]
    tools_required: List[str]  # tool_ids
    crafting_time: float  # в секундах
    experience_gained: int
    skill_level_required: int
    success_chance_base: float = 0.8
    quality_multiplier: float = 1.0
    is_discovered: bool = False
    discovery_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def can_craft(self, player_skills: Dict[str, int], 
                  player_inventory: Dict[str, int]) -> Tuple[bool, List[str]]:
        """Проверка возможности крафтинга"""
        issues = []
        
        # Проверка уровня навыка
        skill_key = f"{self.category.value}_skill"
        if skill_key not in player_skills or player_skills[skill_key] < self.skill_level_required:
            issues.append(f"Требуется уровень {self.category.value}: {self.skill_level_required}")
        
        # Проверка ингредиентов
        for ingredient in self.ingredients:
            if not ingredient.is_optional:
                if (ingredient.item_id not in player_inventory or 
                    player_inventory[ingredient.item_id] < ingredient.quantity):
                    issues.append(f"Недостаточно {ingredient.item_id}: {ingredient.quantity}")
        
        return len(issues) == 0, issues
    
    def calculate_success_chance(self, player_skills: Dict[str, int], 
                                tool_efficiency: float = 1.0) -> float:
        """Расчёт шанса успеха"""
        skill_key = f"{self.category.value}_skill"
        skill_level = player_skills.get(skill_key, 0)
        
        # Базовый шанс + бонус от навыка + бонус от инструмента
        skill_bonus = min(0.3, skill_level * 0.01)
        tool_bonus = (tool_efficiency - 1.0) * 0.2
        
        return min(0.99, self.success_chance_base + skill_bonus + tool_bonus)
    
    def calculate_quality(self, player_skills: Dict[str, int], 
                         tool_quality: float = 0.0) -> float:
        """Расчёт качества результата"""
        skill_key = f"{self.category.value}_skill"
        skill_level = player_skills.get(skill_key, 0)
        
        # Базовое качество + бонус от навыка + бонус от инструмента
        skill_quality = min(0.5, skill_level * 0.01)
        
        return min(1.0, self.quality_multiplier + skill_quality + tool_quality)


@dataclass
class CraftingResult:
    """Результат крафтинга"""
    success: bool
    item_id: Optional[str] = None
    quantity: int = 1
    quality: float = 1.0
    experience_gained: int = 0
    materials_used: Dict[str, int] = field(default_factory=dict)
    tools_worn: Dict[str, float] = field(default_factory=dict)
    failure_reason: Optional[str] = None


class CraftingSkill:
    """Навык крафтинга"""
    
    def __init__(self, category: CraftingCategory):
        self.category = category
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.specializations: Set[str] = set()
        self.unlocked_recipes: Set[str] = set()
        
    def gain_experience(self, amount: int) -> bool:
        """Получение опыта"""
        self.experience += amount
        
        # Проверка повышения уровня
        if self.experience >= self.experience_to_next:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.experience -= self.experience_to_next
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        logger.info(f"Навык {self.category.value} повышен до уровня {self.level}")
    
    def unlock_specialization(self, specialization: str):
        """Разблокировка специализации"""
        self.specializations.add(specialization)
        logger.info(f"Разблокирована специализация: {specialization}")
    
    def unlock_recipe(self, recipe_id: str):
        """Разблокировка рецепта"""
        self.unlocked_recipes.add(recipe_id)
        logger.info(f"Разблокирован рецепт: {recipe_id}")


class CraftingWorkstation:
    """Рабочая станция для крафтинга"""
    
    def __init__(self, workstation_id: str, name: str, category: CraftingCategory):
        self.workstation_id = workstation_id
        self.name = name
        self.category = category
        self.tools: Dict[str, CraftingTool] = {}
        self.upgrades: Dict[str, float] = {}
        self.efficiency_bonus: float = 1.0
        self.quality_bonus: float = 0.0
        
    def add_tool(self, tool: CraftingTool):
        """Добавление инструмента"""
        self.tools[tool.tool_id] = tool
    
    def remove_tool(self, tool_id: str) -> Optional[CraftingTool]:
        """Удаление инструмента"""
        return self.tools.pop(tool_id, None)
    
    def get_tool_efficiency(self, tool_id: str) -> float:
        """Получение эффективности инструмента"""
        if tool_id in self.tools:
            tool = self.tools[tool_id]
            return tool.efficiency * self.efficiency_bonus
        return 1.0
    
    def get_tool_quality(self, tool_id: str) -> float:
        """Получение качества инструмента"""
        if tool_id in self.tools:
            tool = self.tools[tool_id]
            return tool.quality_bonus + self.quality_bonus
        return 0.0
    
    def upgrade_workstation(self, upgrade_type: str, value: float):
        """Улучшение станции"""
        if upgrade_type == "efficiency":
            self.efficiency_bonus += value
        elif upgrade_type == "quality":
            self.quality_bonus += value
        else:
            self.upgrades[upgrade_type] = value


class CraftingSystem:
    """Система крафтинга"""
    
    def __init__(self):
        self.recipes: Dict[str, CraftingRecipe] = {}
        self.workstations: Dict[str, CraftingWorkstation] = {}
        self.player_skills: Dict[str, CraftingSkill] = {}
        self.crafting_queue: List[Dict[str, Any]] = []
        
        # Инициализация навыков
        self._init_skills()
        
        # Инициализация рецептов
        self._init_recipes()
        
        # Инициализация рабочих станций
        self._init_workstations()
        
        logger.info("Система крафтинга инициализирована")
    
    def _init_skills(self):
        """Инициализация навыков"""
        for category in CraftingCategory:
            skill_key = f"{category.value}_skill"
            self.player_skills[skill_key] = CraftingSkill(category)
    
    def _init_recipes(self):
        """Инициализация рецептов"""
        base_recipes = {
            "sword_basic": {
                "name": "Базовый меч",
                "description": "Простой железный меч",
                "category": CraftingCategory.WEAPONSMITHING,
                "difficulty": RecipeDifficulty.BEGINNER,
                "ingredients": [
                    {"item_id": "iron_ingot", "quantity": 3},
                    {"item_id": "wood", "quantity": 1}
                ],
                "tools_required": ["hammer"],
                "crafting_time": 30.0,
                "experience_gained": 50,
                "skill_level_required": 1
            },
            "health_potion": {
                "name": "Зелье здоровья",
                "description": "Восстанавливает здоровье",
                "category": CraftingCategory.ALCHEMY,
                "difficulty": RecipeDifficulty.BEGINNER,
                "ingredients": [
                    {"item_id": "herb_red", "quantity": 2},
                    {"item_id": "water", "quantity": 1}
                ],
                "tools_required": ["mortar"],
                "crafting_time": 15.0,
                "experience_gained": 30,
                "skill_level_required": 1
            },
            "gene_enhancer": {
                "name": "Усилитель генов",
                "description": "Улучшает генетические характеристики",
                "category": CraftingCategory.GENETIC_ENGINEERING,
                "difficulty": RecipeDifficulty.EXPERT,
                "ingredients": [
                    {"item_id": "dna_sample", "quantity": 1},
                    {"item_id": "catalyst", "quantity": 2},
                    {"item_id": "nanobots", "quantity": 1}
                ],
                "tools_required": ["gene_lab"],
                "crafting_time": 120.0,
                "experience_gained": 200,
                "skill_level_required": 10
            }
        }
        
        for recipe_id, data in base_recipes.items():
            ingredients = [
                CraftingIngredient(
                    item_id=ing["item_id"],
                    quantity=ing["quantity"]
                )
                for ing in data["ingredients"]
            ]
            
            recipe = CraftingRecipe(
                recipe_id=recipe_id,
                name=data["name"],
                description=data["description"],
                category=data["category"],
                difficulty=data["difficulty"],
                ingredients=ingredients,
                tools_required=data["tools_required"],
                crafting_time=data["crafting_time"],
                experience_gained=data["experience_gained"],
                skill_level_required=data["skill_level_required"]
            )
            
            self.recipes[recipe_id] = recipe
    
    def _init_workstations(self):
        """Инициализация рабочих станций"""
        workstations_data = {
            "forge": {
                "name": "Кузница",
                "category": CraftingCategory.WEAPONSMITHING
            },
            "alchemy_lab": {
                "name": "Алхимическая лаборатория",
                "category": CraftingCategory.ALCHEMY
            },
            "gene_lab": {
                "name": "Генетическая лаборатория",
                "category": CraftingCategory.GENETIC_ENGINEERING
            }
        }
        
        for station_id, data in workstations_data.items():
            workstation = CraftingWorkstation(
                workstation_id=station_id,
                name=data["name"],
                category=data["category"]
            )
            self.workstations[station_id] = workstation
    
    def start_crafting(self, recipe_id: str, workstation_id: str, 
                      player_inventory: Dict[str, int]) -> Optional[str]:
        """Начало крафтинга"""
        if recipe_id not in self.recipes:
            logger.error(f"Рецепт не найден: {recipe_id}")
            return None
        
        if workstation_id not in self.workstations:
            logger.error(f"Рабочая станция не найдена: {workstation_id}")
            return None
        
        recipe = self.recipes[recipe_id]
        workstation = self.workstations[workstation_id]
        
        # Проверка возможности крафтинга
        can_craft, issues = recipe.can_craft(self._get_skill_levels(), player_inventory)
        if not can_craft:
            logger.warning(f"Невозможно создать {recipe.name}: {', '.join(issues)}")
            return None
        
        # Создание задачи крафтинга
        crafting_task = {
            "task_id": f"craft_{int(time.time())}_{random.randint(1000, 9999)}",
            "recipe_id": recipe_id,
            "workstation_id": workstation_id,
            "start_time": time.time(),
            "end_time": time.time() + recipe.crafting_time,
            "status": "in_progress"
        }
        
        self.crafting_queue.append(crafting_task)
        logger.info(f"Начат крафтинг: {recipe.name}")
        
        return crafting_task["task_id"]
    
    def complete_crafting(self, task_id: str, player_inventory: Dict[str, int]) -> Optional[CraftingResult]:
        """Завершение крафтинга"""
        task = None
        for t in self.crafting_queue:
            if t["task_id"] == task_id:
                task = t
                break
        
        if not task or task["status"] != "in_progress":
            return None
        
        if time.time() < task["end_time"]:
            return None
        
        recipe = self.recipes[task["recipe_id"]]
        workstation = self.workstations[task["workstation_id"]]
        
        # Расчёт шанса успеха и качества
        tool_efficiency = 1.0
        tool_quality = 0.0
        
        for tool_id in recipe.tools_required:
            tool_efficiency *= workstation.get_tool_efficiency(tool_id)
            tool_quality += workstation.get_tool_quality(tool_id)
        
        success_chance = recipe.calculate_success_chance(self._get_skill_levels(), tool_efficiency)
        quality = recipe.calculate_quality(self._get_skill_levels(), tool_quality)
        
        # Определение успеха
        success = random.random() < success_chance
        
        result = CraftingResult(
            success=success,
            experience_gained=recipe.experience_gained if success else recipe.experience_gained // 4
        )
        
        if success:
            # Успешный крафтинг
            result.item_id = f"{recipe.recipe_id}_item"
            result.quality = quality
            
            # Использование материалов
            for ingredient in recipe.ingredients:
                if not ingredient.is_optional:
                    player_inventory[ingredient.item_id] -= ingredient.quantity
                    result.materials_used[ingredient.item_id] = ingredient.quantity
            
            # Износ инструментов
            for tool_id in recipe.tools_required:
                if tool_id in workstation.tools:
                    wear_amount = recipe.crafting_time / 60.0  # Износ за минуту
                    workstation.tools[tool_id].use_tool(wear_amount)
                    result.tools_worn[tool_id] = wear_amount
            
            # Получение опыта
            skill_key = f"{recipe.category.value}_skill"
            if skill_key in self.player_skills:
                self.player_skills[skill_key].gain_experience(recipe.experience_gained)
        else:
            # Неудачный крафтинг
            result.failure_reason = "Неудачная попытка крафтинга"
            
            # Частичная потеря материалов
            for ingredient in recipe.ingredients:
                if not ingredient.is_optional and random.random() < 0.5:
                    lost_quantity = ingredient.quantity // 2
                    player_inventory[ingredient.item_id] -= lost_quantity
                    result.materials_used[ingredient.item_id] = lost_quantity
        
        # Завершение задачи
        task["status"] = "completed"
        
        logger.info(f"Крафтинг завершён: {recipe.name} - {'успех' if success else 'неудача'}")
        return result
    
    def _get_skill_levels(self) -> Dict[str, int]:
        """Получение уровней навыков"""
        return {skill_key: skill.level for skill_key, skill in self.player_skills.items()}
    
    def get_available_recipes(self, player_inventory: Dict[str, int]) -> List[CraftingRecipe]:
        """Получение доступных рецептов"""
        available = []
        
        for recipe in self.recipes.values():
            can_craft, _ = recipe.can_craft(self._get_skill_levels(), player_inventory)
            if can_craft:
                available.append(recipe)
        
        return available
    
    def discover_recipe(self, recipe_id: str, discovery_method: str = "exploration"):
        """Открытие нового рецепта"""
        if recipe_id in self.recipes:
            self.recipes[recipe_id].is_discovered = True
            logger.info(f"Открыт рецепт: {self.recipes[recipe_id].name}")
    
    def get_crafting_progress(self) -> List[Dict[str, Any]]:
        """Получение прогресса крафтинга"""
        progress = []
        
        for task in self.crafting_queue:
            if task["status"] == "in_progress":
                recipe = self.recipes[task["recipe_id"]]
                elapsed = time.time() - task["start_time"]
                progress_percent = min(100.0, (elapsed / recipe.crafting_time) * 100.0)
                
                progress.append({
                    "task_id": task["task_id"],
                    "recipe_name": recipe.name,
                    "progress_percent": progress_percent,
                    "time_remaining": max(0, task["end_time"] - time.time())
                })
        
        return progress
    
    def get_skill_info(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о навыках"""
        skill_info = {}
        
        for skill_key, skill in self.player_skills.items():
            skill_info[skill_key] = {
                "level": skill.level,
                "experience": skill.experience,
                "experience_to_next": skill.experience_to_next,
                "specializations": list(skill.specializations),
                "unlocked_recipes": len(skill.unlocked_recipes)
            }
        
        return skill_info
