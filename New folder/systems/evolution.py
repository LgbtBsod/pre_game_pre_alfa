#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class MutationType(Enum):
    """Типы мутаций"""
    POSITIVE = "positive"       # Положительная мутация
    NEGATIVE = "negative"       # Отрицательная мутация
    NEUTRAL = "neutral"         # Нейтральная мутация
    RANDOM = "random"          # Случайная мутация

class EvolutionStage(Enum):
    """Стадии эволюции"""
    BASIC = "basic"            # Базовая форма
    EVOLVED = "evolved"        # Эволюционированная форма
    ADVANCED = "advanced"     # Продвинутая форма
    MASTER = "master"         # Мастерская форма
    LEGENDARY = "legendary"   # Легендарная форма

@dataclass
class Mutation:
    """Мутация"""
    mutation_id: str
    name: str
    description: str
    mutation_type: MutationType
    attribute_modifiers: Dict[str, float]  # Модификаторы атрибутов
    stat_modifiers: Dict[str, float]       # Модификаторы характеристик
    visual_changes: Dict[str, Any]         # Визуальные изменения
    evolution_points: int                 # Очки эволюции
    requirements: Dict[str, Any]          # Требования для получения
    is_permanent: bool = True             # Постоянная ли мутация
    duration: float = -1.0                # Длительность (-1 для постоянных)
    start_time: float = field(default_factory=time.time)

class EvolutionPath:
    """Путь эволюции"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.stages: Dict[EvolutionStage, Dict[str, Any]] = {}
        self.mutations: List[Mutation] = []
        self.current_stage = EvolutionStage.BASIC
        self.evolution_points = 0
        self.total_mutations = 0
        
    def add_stage(self, stage: EvolutionStage, requirements: Dict[str, Any], 
                  bonuses: Dict[str, float]):
        """Добавление стадии эволюции"""
        self.stages[stage] = {
            'requirements': requirements,
            'bonuses': bonuses,
            'unlocked': False
        }
    
    def add_mutation(self, mutation: Mutation):
        """Добавление мутации"""
        self.mutations.append(mutation)
    
    def can_evolve(self, entity_stats: Dict[str, Any]) -> bool:
        """Проверка возможности эволюции"""
        if self.current_stage not in self.stages:
            return False
        
        stage_data = self.stages[self.current_stage]
        requirements = stage_data['requirements']
        
        for req_type, req_value in requirements.items():
            if req_type == 'level' and entity_stats.get('level', 0) < req_value:
                return False
            elif req_type == 'evolution_points' and self.evolution_points < req_value:
                return False
            elif req_type == 'mutations' and self.total_mutations < req_value:
                return False
            elif req_type == 'experience' and entity_stats.get('experience', 0) < req_value:
                return False
        
        return True
    
    def evolve(self, entity_stats: Dict[str, Any]) -> bool:
        """Эволюция"""
        if not self.can_evolve(entity_stats):
            return False
        
        # Определяем следующую стадию
        stages_list = list(EvolutionStage)
        current_index = stages_list.index(self.current_stage)
        
        if current_index + 1 < len(stages_list):
            next_stage = stages_list[current_index + 1]
            if next_stage in self.stages:
                self.current_stage = next_stage
                self.stages[next_stage]['unlocked'] = True
                return True
        
        return False

class EvolutionSystem:
    """Система эволюции и мутаций"""
    
    def __init__(self):
        self.entity_evolution: Dict[str, EvolutionPath] = {}
        self.mutation_templates: Dict[str, Mutation] = {}
        self.evolution_paths: Dict[str, EvolutionPath] = {}
        
        # Инициализация шаблонов мутаций
        self._initialize_mutation_templates()
        # Инициализация путей эволюции
        self._initialize_evolution_paths()
    
    def _initialize_mutation_templates(self):
        """Инициализация шаблонов мутаций"""
        # Положительные мутации
        strength_mutation = Mutation(
            mutation_id="enhanced_strength",
            name="Enhanced Strength",
            description="Увеличивает силу и физический урон",
            mutation_type=MutationType.POSITIVE,
            attribute_modifiers={"strength": 5.0},
            stat_modifiers={"physical_damage": 10.0},
            visual_changes={"color": (1.2, 0.8, 0.8, 1)},
            evolution_points=10,
            requirements={}
        )
        self.mutation_templates["enhanced_strength"] = strength_mutation
        
        speed_mutation = Mutation(
            mutation_id="enhanced_speed",
            name="Enhanced Speed",
            description="Увеличивает скорость движения и атаки",
            mutation_type=MutationType.POSITIVE,
            attribute_modifiers={"agility": 4.0},
            stat_modifiers={"movement_speed": 2.0, "attack_speed": 0.2},
            visual_changes={"scale": 0.9},
            evolution_points=8,
            requirements={}
        )
        self.mutation_templates["enhanced_speed"] = speed_mutation
        
        intelligence_mutation = Mutation(
            mutation_id="enhanced_intelligence",
            name="Enhanced Intelligence",
            description="Увеличивает интеллект и магический урон",
            mutation_type=MutationType.POSITIVE,
            attribute_modifiers={"intelligence": 5.0},
            stat_modifiers={"magical_damage": 15.0, "mana": 20.0},
            visual_changes={"glow": True},
            evolution_points=12,
            requirements={}
        )
        self.mutation_templates["enhanced_intelligence"] = intelligence_mutation
        
        # Отрицательные мутации
        weakness_mutation = Mutation(
            mutation_id="weakness",
            name="Weakness",
            description="Уменьшает силу и выносливость",
            mutation_type=MutationType.NEGATIVE,
            attribute_modifiers={"strength": -3.0, "endurance": -2.0},
            stat_modifiers={"physical_damage": -5.0},
            visual_changes={"color": (0.8, 0.8, 0.8, 1)},
            evolution_points=5,
            requirements={}
        )
        self.mutation_templates["weakness"] = weakness_mutation
        
        slow_mutation = Mutation(
            mutation_id="slowness",
            name="Slowness",
            description="Замедляет движение и атаку",
            mutation_type=MutationType.NEGATIVE,
            attribute_modifiers={"agility": -3.0},
            stat_modifiers={"movement_speed": -1.0, "attack_speed": -0.1},
            visual_changes={"scale": 1.1},
            evolution_points=5,
            requirements={}
        )
        self.mutation_templates["slowness"] = slow_mutation
        
        # Нейтральные мутации
        strange_mutation = Mutation(
            mutation_id="strange_appearance",
            name="Strange Appearance",
            description="Изменяет внешний вид",
            mutation_type=MutationType.NEUTRAL,
            attribute_modifiers={},
            stat_modifiers={},
            visual_changes={"color": (0.5, 0.5, 1.0, 1)},
            evolution_points=3,
            requirements={}
        )
        self.mutation_templates["strange_appearance"] = strange_mutation
    
    def _initialize_evolution_paths(self):
        """Инициализация путей эволюции"""
        # Путь воина
        warrior_path = EvolutionPath("Warrior", "Путь воина - сила и выносливость")
        warrior_path.add_stage(EvolutionStage.EVOLVED, {"level": 10, "evolution_points": 50}, 
                              {"strength": 10.0, "vitality": 15.0})
        warrior_path.add_stage(EvolutionStage.ADVANCED, {"level": 20, "evolution_points": 100}, 
                               {"strength": 20.0, "vitality": 25.0, "physical_damage": 30.0})
        warrior_path.add_stage(EvolutionStage.MASTER, {"level": 30, "evolution_points": 200}, 
                               {"strength": 30.0, "vitality": 35.0, "physical_damage": 50.0})
        warrior_path.add_stage(EvolutionStage.LEGENDARY, {"level": 50, "evolution_points": 500}, 
                               {"strength": 50.0, "vitality": 50.0, "physical_damage": 100.0})
        
        # Путь мага
        mage_path = EvolutionPath("Mage", "Путь мага - интеллект и мудрость")
        mage_path.add_stage(EvolutionStage.EVOLVED, {"level": 10, "evolution_points": 50}, 
                           {"intelligence": 10.0, "wisdom": 10.0})
        mage_path.add_stage(EvolutionStage.ADVANCED, {"level": 20, "evolution_points": 100}, 
                           {"intelligence": 20.0, "wisdom": 15.0, "magical_damage": 40.0})
        mage_path.add_stage(EvolutionStage.MASTER, {"level": 30, "evolution_points": 200}, 
                           {"intelligence": 30.0, "wisdom": 25.0, "magical_damage": 70.0})
        mage_path.add_stage(EvolutionStage.LEGENDARY, {"level": 50, "evolution_points": 500}, 
                           {"intelligence": 50.0, "wisdom": 40.0, "magical_damage": 120.0})
        
        # Путь ловкача
        rogue_path = EvolutionPath("Rogue", "Путь ловкача - ловкость и удача")
        rogue_path.add_stage(EvolutionStage.EVOLVED, {"level": 10, "evolution_points": 50}, 
                            {"agility": 10.0, "luck": 8.0})
        rogue_path.add_stage(EvolutionStage.ADVANCED, {"level": 20, "evolution_points": 100}, 
                            {"agility": 20.0, "luck": 15.0, "critical_chance": 10.0})
        rogue_path.add_stage(EvolutionStage.MASTER, {"level": 30, "evolution_points": 200}, 
                            {"agility": 30.0, "luck": 25.0, "critical_chance": 20.0})
        rogue_path.add_stage(EvolutionStage.LEGENDARY, {"level": 50, "evolution_points": 500}, 
                            {"agility": 50.0, "luck": 40.0, "critical_chance": 35.0})
        
        self.evolution_paths["warrior"] = warrior_path
        self.evolution_paths["mage"] = mage_path
        self.evolution_paths["rogue"] = rogue_path
    
    def initialize_entity_evolution(self, entity_id: str, path_name: str = "warrior"):
        """Инициализация эволюции для сущности"""
        if path_name not in self.evolution_paths:
            path_name = "warrior"  # По умолчанию
        
        evolution_path = EvolutionPath(
            self.evolution_paths[path_name].name,
            self.evolution_paths[path_name].description
        )
        
        # Копируем стадии
        for stage, data in self.evolution_paths[path_name].stages.items():
            evolution_path.add_stage(stage, data['requirements'], data['bonuses'])
        
        # Копируем мутации
        for mutation in self.evolution_paths[path_name].mutations:
            evolution_path.add_mutation(mutation)
        
        self.entity_evolution[entity_id] = evolution_path
    
    def add_evolution_points(self, entity_id: str, points: int):
        """Добавление очков эволюции"""
        if entity_id not in self.entity_evolution:
            return
        
        self.entity_evolution[entity_id].evolution_points += points
    
    def apply_mutation(self, entity_id: str, mutation_id: str) -> bool:
        """Применение мутации к сущности"""
        if entity_id not in self.entity_evolution or mutation_id not in self.mutation_templates:
            return False
        
        template = self.mutation_templates[mutation_id]
        evolution_path = self.entity_evolution[entity_id]
        
        # Создаем копию мутации
        mutation = Mutation(
            mutation_id=template.mutation_id,
            name=template.name,
            description=template.description,
            mutation_type=template.mutation_type,
            attribute_modifiers=template.attribute_modifiers.copy(),
            stat_modifiers=template.stat_modifiers.copy(),
            visual_changes=template.visual_changes.copy(),
            evolution_points=template.evolution_points,
            requirements=template.requirements.copy(),
            is_permanent=template.is_permanent,
            duration=template.duration
        )
        
        evolution_path.add_mutation(mutation)
        evolution_path.total_mutations += 1
        evolution_path.evolution_points += mutation.evolution_points
        
        return True
    
    def random_mutation(self, entity_id: str, mutation_type: MutationType = MutationType.RANDOM) -> bool:
        """Случайная мутация"""
        available_mutations = []
        
        for mutation_id, mutation in self.mutation_templates.items():
            if mutation_type == MutationType.RANDOM or mutation.mutation_type == mutation_type:
                available_mutations.append(mutation_id)
        
        if not available_mutations:
            return False
        
        selected_mutation = random.choice(available_mutations)
        return self.apply_mutation(entity_id, selected_mutation)
    
    def can_evolve(self, entity_id: str, entity_stats: Dict[str, Any]) -> bool:
        """Проверка возможности эволюции"""
        if entity_id not in self.entity_evolution:
            return False
        
        evolution_path = self.entity_evolution[entity_id]
        return evolution_path.can_evolve(entity_stats)
    
    def evolve(self, entity_id: str, entity_stats: Dict[str, Any]) -> bool:
        """Эволюция сущности"""
        if entity_id not in self.entity_evolution:
            return False
        
        evolution_path = self.entity_evolution[entity_id]
        if evolution_path.evolve(entity_stats):
            return True
        
        return False
    
    def get_evolution_bonuses(self, entity_id: str) -> Dict[str, float]:
        """Получение бонусов от эволюции"""
        if entity_id not in self.entity_evolution:
            return {}
        
        evolution_path = self.entity_evolution[entity_id]
        current_stage = evolution_path.current_stage
        
        if current_stage in evolution_path.stages:
            return evolution_path.stages[current_stage]['bonuses']
        
        return {}
    
    def get_mutation_modifiers(self, entity_id: str) -> Dict[str, float]:
        """Получение модификаторов от мутаций"""
        if entity_id not in self.entity_evolution:
            return {}
        
        modifiers = {}
        evolution_path = self.entity_evolution[entity_id]
        
        for mutation in evolution_path.mutations:
            # Объединяем модификаторы атрибутов
            for attr, value in mutation.attribute_modifiers.items():
                if attr not in modifiers:
                    modifiers[attr] = 0.0
                modifiers[attr] += value
            
            # Объединяем модификаторы характеристик
            for stat, value in mutation.stat_modifiers.items():
                if stat not in modifiers:
                    modifiers[stat] = 0.0
                modifiers[stat] += value
        
        return modifiers
    
    def get_evolution_info(self, entity_id: str) -> Dict[str, Any]:
        """Получение информации об эволюции"""
        if entity_id not in self.entity_evolution:
            return {}
        
        evolution_path = self.entity_evolution[entity_id]
        
        return {
            'path_name': evolution_path.name,
            'current_stage': evolution_path.current_stage.value,
            'evolution_points': evolution_path.evolution_points,
            'total_mutations': evolution_path.total_mutations,
            'mutations': [m.name for m in evolution_path.mutations],
            'next_stage_requirements': self._get_next_stage_requirements(entity_id)
        }
    
    def _get_next_stage_requirements(self, entity_id: str) -> Dict[str, Any]:
        """Получение требований для следующей стадии"""
        if entity_id not in self.entity_evolution:
            return {}
        
        evolution_path = self.entity_evolution[entity_id]
        stages_list = list(EvolutionStage)
        current_index = stages_list.index(evolution_path.current_stage)
        
        if current_index + 1 < len(stages_list):
            next_stage = stages_list[current_index + 1]
            if next_stage in evolution_path.stages:
                return evolution_path.stages[next_stage]['requirements']
        
        return {}
    
    def get_available_mutations(self, entity_id: str) -> List[Mutation]:
        """Получение доступных мутаций"""
        return list(self.mutation_templates.values())
    
    def get_evolution_paths(self) -> Dict[str, EvolutionPath]:
        """Получение всех путей эволюции"""
        return self.evolution_paths.copy()
