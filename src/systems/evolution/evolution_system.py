#!/usr/bin/env python3
"""
Evolution System - Система эволюции
Отвечает только за эволюцию существ и их характеристики
"""

import logging
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from ...core.interfaces import ISystem

logger = logging.getLogger(__name__)

class EvolutionStage(Enum):
    """Стадии эволюции"""
    EGG = "egg"
    LARVA = "larva"
    JUVENILE = "juvenile"
    ADULT = "adult"
    ELDER = "elder"
    LEGENDARY = "legendary"

class EvolutionType(Enum):
    """Типы эволюции"""
    NATURAL = "natural"      # Естественная эволюция
    COMBAT = "combat"        # Эволюция через бой
    ENVIRONMENTAL = "environmental"  # Эволюция через окружение
    MUTATION = "mutation"    # Мутационная эволюция

@dataclass
class EvolutionStats:
    """Статистика эволюции"""
    health: int = 100
    attack: int = 10
    defense: int = 5
    speed: int = 5
    intelligence: int = 5
    special_ability: str = "none"
    
    def __add__(self, other: 'EvolutionStats') -> 'EvolutionStats':
        """Сложение статистик"""
        return EvolutionStats(
            health=self.health + other.health,
            attack=self.attack + other.attack,
            defense=self.defense + other.defense,
            speed=self.speed + other.speed,
            intelligence=self.intelligence + other.intelligence,
            special_ability=other.special_ability if other.special_ability != "none" else self.special_ability
        )

@dataclass
class EvolutionRequirement:
    """Требования для эволюции"""
    level: int = 1
    experience: int = 0
    items: List[str] = None
    conditions: List[str] = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.conditions is None:
            self.conditions = []

class EvolutionSystem(ISystem):
    """Система эволюции существ"""
    
    def __init__(self):
        self.evolution_paths: Dict[str, List[EvolutionStage]] = {}
        self.stage_stats: Dict[EvolutionStage, EvolutionStats] = {}
        self.evolution_requirements: Dict[EvolutionStage, EvolutionRequirement] = {}
        self.mutation_chances: Dict[str, float] = {}
        self.is_initialized = False
        
        logger.info("Система эволюции инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы эволюции"""
        try:
            self._setup_evolution_paths()
            self._setup_stage_stats()
            self._setup_evolution_requirements()
            self._setup_mutation_chances()
            
            self.is_initialized = True
            logger.info("Система эволюции успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы эволюции: {e}")
            return False
    
    def update(self, delta_time: float) -> None:
        """Обновление системы эволюции"""
        if not self.is_initialized:
            return
        
        try:
            # Обновляем активные эволюции
            self._update_active_evolutions(delta_time)
        except Exception as e:
            logger.error(f"Ошибка обновления системы эволюции: {e}")
    
    def cleanup(self) -> None:
        """Очистка системы эволюции"""
        try:
            self.is_initialized = False
            self.evolution_paths.clear()
            self.stage_stats.clear()
            self.evolution_requirements.clear()
            self.mutation_chances.clear()
            logger.info("Система эволюции очищена")
        except Exception as e:
            logger.error(f"Ошибка очистки системы эволюции: {e}")
    
    def _setup_evolution_paths(self):
        """Настройка путей эволюции"""
        # Базовые пути эволюции
        self.evolution_paths = {
            "basic": [EvolutionStage.EGG, EvolutionStage.LARVA, EvolutionStage.JUVENILE, EvolutionStage.ADULT],
            "combat": [EvolutionStage.EGG, EvolutionStage.LARVA, EvolutionStage.JUVENILE, EvolutionStage.ADULT, EvolutionStage.ELDER],
            "legendary": [EvolutionStage.EGG, EvolutionStage.LARVA, EvolutionStage.JUVENILE, EvolutionStage.ADULT, EvolutionStage.ELDER, EvolutionStage.LEGENDARY]
        }
    
    def _setup_stage_stats(self):
        """Настройка статистик для каждой стадии"""
        self.stage_stats = {
            EvolutionStage.EGG: EvolutionStats(health=50, attack=1, defense=1, speed=1, intelligence=1),
            EvolutionStage.LARVA: EvolutionStats(health=75, attack=3, defense=2, speed=2, intelligence=2),
            EvolutionStage.JUVENILE: EvolutionStats(health=100, attack=6, defense=4, speed=4, intelligence=4),
            EvolutionStage.ADULT: EvolutionStats(health=150, attack=10, defense=7, speed=6, intelligence=6),
            EvolutionStage.ELDER: EvolutionStats(health=200, attack=15, defense=10, speed=8, intelligence=8),
            EvolutionStage.LEGENDARY: EvolutionStats(health=300, attack=25, defense=15, speed=12, intelligence=12, special_ability="legendary_power")
        }
    
    def _setup_evolution_requirements(self):
        """Настройка требований для эволюции"""
        self.evolution_requirements = {
            EvolutionStage.LARVA: EvolutionRequirement(level=5, experience=100),
            EvolutionStage.JUVENILE: EvolutionRequirement(level=10, experience=500),
            EvolutionStage.ADULT: EvolutionRequirement(level=20, experience=2000),
            EvolutionStage.ELDER: EvolutionRequirement(level=35, experience=10000),
            EvolutionStage.LEGENDARY: EvolutionRequirement(level=50, experience=50000, items=["legendary_crystal"])
        }
    
    def _setup_mutation_chances(self):
        """Настройка шансов мутаций"""
        self.mutation_chances = {
            "positive": 0.15,      # 15% шанс положительной мутации
            "negative": 0.10,      # 10% шанс отрицательной мутации
            "neutral": 0.05,       # 5% шанс нейтральной мутации
            "special": 0.02        # 2% шанс специальной мутации
        }
    
    def can_evolve(self, entity: Dict[str, Any], target_stage: EvolutionStage) -> bool:
        """Проверка возможности эволюции"""
        if target_stage not in self.evolution_requirements:
            return False
        
        req = self.evolution_requirements[target_stage]
        
        # Проверка уровня
        if entity.get('level', 0) < req.level:
            return False
        
        # Проверка опыта
        if entity.get('experience', 0) < req.experience:
            return False
        
        # Проверка предметов
        if req.items:
            inventory = entity.get('inventory', [])
            for item in req.items:
                if item not in inventory:
                    return False
        
        # Проверка условий
        if req.conditions:
            for condition in req.conditions:
                if not self._check_condition(entity, condition):
                    return False
        
        return True
    
    def _check_condition(self, entity: Dict[str, Any], condition: str) -> bool:
        """Проверка специального условия"""
        if condition == "combat_mastery":
            return entity.get('combat_wins', 0) >= 10
        elif condition == "environmental_adaptation":
            return entity.get('environment_exposure', 0) >= 100
        elif condition == "social_bonding":
            return entity.get('social_interactions', 0) >= 50
        
        return True
    
    def evolve(self, entity: Dict[str, Any], target_stage: EvolutionStage) -> bool:
        """Эволюция существа"""
        if not self.can_evolve(entity, target_stage):
            logger.warning(f"Существо {entity.get('name', 'unknown')} не может эволюционировать в {target_stage.value}")
            return False
        
        try:
            # Получаем статистики новой стадии
            new_stats = self.stage_stats[target_stage]
            
            # Применяем эволюцию
            old_stage = entity.get('evolution_stage', EvolutionStage.EGG)
            entity['evolution_stage'] = target_stage
            
            # Обновляем базовые характеристики
            entity['health'] = new_stats.health
            entity['max_health'] = new_stats.health
            entity['attack'] = new_stats.attack
            entity['defense'] = new_stats.defense
            entity['speed'] = new_stats.speed
            entity['intelligence'] = new_stats.intelligence
            
            # Добавляем специальные способности
            if new_stats.special_ability != "none":
                if 'abilities' not in entity:
                    entity['abilities'] = []
                entity['abilities'].append(new_stats.special_ability)
            
            # Логируем эволюцию
            logger.info(f"Существо {entity.get('name', 'unknown')} эволюционировало с {old_stage.value} в {target_stage.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка эволюции существа {entity.get('name', 'unknown')}: {e}")
            return False
    
    def check_mutation(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Проверка мутации существа"""
        mutation_roll = random.random()
        
        if mutation_roll < self.mutation_chances["special"]:
            return self._create_special_mutation(entity)
        elif mutation_roll < self.mutation_chances["special"] + self.mutation_chances["positive"]:
            return self._create_positive_mutation(entity)
        elif mutation_roll < self.mutation_chances["special"] + self.mutation_chances["positive"] + self.mutation_chances["negative"]:
            return self._create_negative_mutation(entity)
        elif mutation_roll < self.mutation_chances["special"] + self.mutation_chances["positive"] + self.mutation_chances["negative"] + self.mutation_chances["neutral"]:
            return self._create_neutral_mutation(entity)
        
        return None
    
    def _create_positive_mutation(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Создание положительной мутации"""
        mutations = [
            {"stat": "attack", "bonus": 2, "name": "Усиленная атака"},
            {"stat": "defense", "bonus": 2, "name": "Усиленная защита"},
            {"stat": "speed", "bonus": 1, "name": "Увеличенная скорость"},
            {"stat": "intelligence", "bonus": 1, "name": "Повышенный интеллект"}
        ]
        
        mutation = random.choice(mutations)
        entity[mutation["stat"]] += mutation["bonus"]
        
        logger.info(f"Положительная мутация: {mutation['name']} для {entity.get('name', 'unknown')}")
        
        return {
            "type": "positive",
            "name": mutation["name"],
            "stat": mutation["stat"],
            "bonus": mutation["bonus"]
        }
    
    def _create_negative_mutation(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Создание отрицательной мутации"""
        mutations = [
            {"stat": "attack", "penalty": -1, "name": "Ослабленная атака"},
            {"stat": "defense", "penalty": -1, "name": "Ослабленная защита"},
            {"stat": "speed", "penalty": -1, "name": "Сниженная скорость"}
        ]
        
        mutation = random.choice(mutations)
        entity[mutation["stat"]] = max(1, entity[mutation["stat"]] + mutation["penalty"])
        
        logger.info(f"Отрицательная мутация: {mutation['name']} для {entity.get('name', 'unknown')}")
        
        return {
            "type": "negative",
            "name": mutation["name"],
            "stat": mutation["stat"],
            "penalty": mutation["penalty"]
        }
    
    def _create_neutral_mutation(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Создание нейтральной мутации"""
        mutations = [
            {"name": "Изменение цвета", "effect": "Визуальное изменение"},
            {"name": "Новый звук", "effect": "Звуковое изменение"},
            {"name": "Особый запах", "effect": "Обонятельное изменение"}
        ]
        
        mutation = random.choice(mutations)
        
        logger.info(f"Нейтральная мутация: {mutation['name']} для {entity.get('name', 'unknown')}")
        
        return {
            "type": "neutral",
            "name": mutation["name"],
            "effect": mutation["effect"]
        }
    
    def _create_special_mutation(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Создание специальной мутации"""
        special_mutations = [
            {"name": "Элементальная атака", "ability": "fire_breath", "description": "Дыхание огнем"},
            {"name": "Телепортация", "ability": "teleport", "description": "Кратковременная телепортация"},
            {"name": "Регенерация", "ability": "regeneration", "description": "Быстрое восстановление здоровья"}
        ]
        
        mutation = random.choice(special_mutations)
        
        # Добавляем способность
        if 'abilities' not in entity:
            entity['abilities'] = []
        entity['abilities'].append(mutation["ability"])
        
        logger.info(f"Специальная мутация: {mutation['name']} для {entity.get('name', 'unknown')}")
        
        return {
            "type": "special",
            "name": mutation["name"],
            "ability": mutation["ability"],
            "description": mutation["description"]
        }
    
    def get_evolution_info(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Получение информации об эволюции существа"""
        current_stage = entity.get('evolution_stage', EvolutionStage.EGG)
        next_stage = self._get_next_stage(current_stage)
        
        info = {
            "current_stage": current_stage.value,
            "next_stage": next_stage.value if next_stage else None,
            "can_evolve": False,
            "requirements": None,
            "progress": {}
        }
        
        if next_stage:
            info["can_evolve"] = self.can_evolve(entity, next_stage)
            info["requirements"] = self.evolution_requirements[next_stage]
            
            # Прогресс к следующей стадии
            req = self.evolution_requirements[next_stage]
            info["progress"] = {
                "level": min(100, (entity.get('level', 0) / req.level) * 100),
                "experience": min(100, (entity.get('experience', 0) / req.experience) * 100)
            }
        
        return info
    
    def _get_next_stage(self, current_stage: EvolutionStage) -> Optional[EvolutionStage]:
        """Получение следующей стадии эволюции"""
        # Находим путь эволюции для текущей стадии
        for path in self.evolution_paths.values():
            try:
                current_index = path.index(current_stage)
                if current_index + 1 < len(path):
                    return path[current_index + 1]
            except ValueError:
                continue
        
        return None
    
    def cleanup(self):
        """Очистка системы эволюции"""
        logger.info("Очистка системы эволюции...")
        self.evolution_paths.clear()
        self.stage_stats.clear()
        self.evolution_requirements.clear()
        self.mutation_chances.clear()
