#!/usr/bin/env python3
"""
Система эволюции - управление эволюцией существ и их характеристиками
"""

import logging
import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState

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

@dataclass
class EvolutionProgress:
    """Прогресс эволюции"""
    entity_id: str
    current_stage: EvolutionStage
    target_stage: EvolutionStage
    progress_percentage: float
    requirements_met: bool
    last_update: float

class EvolutionSystem(ISystem):
    """Система эволюции существ"""
    
    def __init__(self):
        self._system_name = "evolution"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Пути эволюции
        self.evolution_paths: Dict[str, List[EvolutionStage]] = {}
        
        # Статистики для каждой стадии
        self.stage_stats: Dict[EvolutionStage, EvolutionStats] = {}
        
        # Требования для эволюции
        self.evolution_requirements: Dict[EvolutionStage, EvolutionRequirement] = {}
        
        # Шансы мутаций
        self.mutation_chances: Dict[str, float] = {}
        
        # Активные эволюции
        self.active_evolutions: Dict[str, EvolutionProgress] = {}
        
        # История эволюций
        self.evolution_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Статистика системы
        self.system_stats = {
            'entities_count': 0,
            'evolutions_completed': 0,
            'mutations_triggered': 0,
            'active_evolutions': 0,
            'update_time': 0.0
        }
        
        logger.info("Система эволюции инициализирована")
    
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
        """Инициализация системы эволюции"""
        try:
            logger.info("Инициализация системы эволюции...")
            
            # Настраиваем пути эволюции
            self._setup_evolution_paths()
            
            # Настраиваем статистики для каждой стадии
            self._setup_stage_stats()
            
            # Настраиваем требования для эволюции
            self._setup_evolution_requirements()
            
            # Настраиваем шансы мутаций
            self._setup_mutation_chances()
            
            self._system_state = SystemState.READY
            logger.info("Система эволюции успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы эволюции: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы эволюции"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем активные эволюции
            self._update_active_evolutions(delta_time)
            
            # Проверяем возможность эволюции для всех сущностей
            self._check_evolution_opportunities()
            
            # Обновляем статистику системы
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы эволюции: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы эволюции"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система эволюции приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы эволюции: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы эволюции"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система эволюции возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы эволюции: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы эволюции"""
        try:
            logger.info("Очистка системы эволюции...")
            
            # Очищаем все данные
            self.evolution_paths.clear()
            self.stage_stats.clear()
            self.evolution_requirements.clear()
            self.mutation_chances.clear()
            self.active_evolutions.clear()
            self.evolution_history.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'entities_count': 0,
                'evolutions_completed': 0,
                'mutations_triggered': 0,
                'active_evolutions': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система эволюции очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы эволюции: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'evolution_paths_count': len(self.evolution_paths),
            'stages_count': len(self.stage_stats),
            'active_evolutions': len(self.active_evolutions),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "entity_level_up":
                return self._handle_entity_level_up(event_data)
            elif event_type == "entity_experience_gained":
                return self._handle_entity_experience_gained(event_data)
            elif event_type == "evolution_triggered":
                return self._handle_evolution_triggered(event_data)
            elif event_type == "mutation_triggered":
                return self._handle_mutation_triggered(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
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
            
            # Записываем в историю
            entity_id = entity.get('id', 'unknown')
            if entity_id not in self.evolution_history:
                self.evolution_history[entity_id] = []
            
            evolution_record = {
                'timestamp': time.time(),
                'from_stage': old_stage.value,
                'to_stage': target_stage.value,
                'type': 'natural'
            }
            self.evolution_history[entity_id].append(evolution_record)
            
            # Обновляем статистику
            self.system_stats['evolutions_completed'] += 1
            
            # Удаляем из активных эволюций
            if entity_id in self.active_evolutions:
                del self.active_evolutions[entity_id]
                self.system_stats['active_evolutions'] = len(self.active_evolutions)
            
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
            mutation = self._create_special_mutation(entity)
        elif mutation_roll < self.mutation_chances["special"] + self.mutation_chances["positive"]:
            mutation = self._create_positive_mutation(entity)
        elif mutation_roll < self.mutation_chances["special"] + self.mutation_chances["positive"] + self.mutation_chances["negative"]:
            mutation = self._create_negative_mutation(entity)
        elif mutation_roll < self.mutation_chances["special"] + self.mutation_chances["positive"] + self.mutation_chances["negative"] + self.mutation_chances["neutral"]:
            mutation = self._create_neutral_mutation(entity)
        else:
            return None
        
        # Записываем мутацию в историю
        if mutation:
            entity_id = entity.get('id', 'unknown')
            if entity_id not in self.evolution_history:
                self.evolution_history[entity_id] = []
            
            mutation_record = {
                'timestamp': time.time(),
                'type': 'mutation',
                'mutation_data': mutation
            }
            self.evolution_history[entity_id].append(mutation_record)
            
            # Обновляем статистику
            self.system_stats['mutations_triggered'] += 1
        
        return mutation
    
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
    
    def _update_active_evolutions(self, delta_time: float) -> None:
        """Обновление активных эволюций"""
        try:
            current_time = time.time()
            
            # Обновляем прогресс эволюций
            for entity_id, progress in list(self.active_evolutions.items()):
                # Проверяем, не истекло ли время
                if current_time - progress.last_update > 300:  # 5 минут
                    del self.active_evolutions[entity_id]
                    continue
                
                # Обновляем время последнего обновления
                progress.last_update = current_time
                
        except Exception as e:
            logger.warning(f"Ошибка обновления активных эволюций: {e}")
    
    def _check_evolution_opportunities(self) -> None:
        """Проверка возможностей эволюции"""
        try:
            # Здесь можно добавить логику для автоматической проверки
            # всех сущностей на возможность эволюции
            pass
        except Exception as e:
            logger.warning(f"Ошибка проверки возможностей эволюции: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            entity_data = event_data.get('entity_data', {})
            
            if entity_id and entity_data:
                # Инициализируем эволюцию для новой сущности
                evolution_stage = entity_data.get('evolution_stage', EvolutionStage.EGG)
                entity_data['evolution_stage'] = evolution_stage
                
                # Создаем запись в истории
                if entity_id not in self.evolution_history:
                    self.evolution_history[entity_id] = []
                
                creation_record = {
                    'timestamp': time.time(),
                    'type': 'creation',
                    'stage': evolution_stage.value
                }
                self.evolution_history[entity_id].append(creation_record)
                
                self.system_stats['entities_count'] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_entity_level_up(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события повышения уровня сущности"""
        try:
            entity_id = event_data.get('entity_id')
            new_level = event_data.get('new_level', 1)
            
            if entity_id and new_level:
                # Проверяем возможность эволюции
                # Здесь можно добавить логику автоматической эволюции
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события повышения уровня: {e}")
            return False
    
    def _handle_entity_experience_gained(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события получения опыта сущностью"""
        try:
            entity_id = event_data.get('entity_id')
            experience_gained = event_data.get('experience_gained', 0)
            
            if entity_id and experience_gained:
                # Проверяем возможность эволюции
                # Здесь можно добавить логику автоматической эволюции
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события получения опыта: {e}")
            return False
    
    def _handle_evolution_triggered(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события запуска эволюции"""
        try:
            entity_id = event_data.get('entity_id')
            target_stage = event_data.get('target_stage')
            
            if entity_id and target_stage:
                # Создаем прогресс эволюции
                progress = EvolutionProgress(
                    entity_id=entity_id,
                    current_stage=event_data.get('current_stage', EvolutionStage.EGG),
                    target_stage=target_stage,
                    progress_percentage=0.0,
                    requirements_met=False,
                    last_update=time.time()
                )
                
                self.active_evolutions[entity_id] = progress
                self.system_stats['active_evolutions'] = len(self.active_evolutions)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события запуска эволюции: {e}")
            return False
    
    def _handle_mutation_triggered(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события запуска мутации"""
        try:
            entity_id = event_data.get('entity_id')
            mutation_type = event_data.get('mutation_type', 'random')
            
            if entity_id and mutation_type:
                # Здесь можно добавить логику для принудительной мутации
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события запуска мутации: {e}")
            return False
