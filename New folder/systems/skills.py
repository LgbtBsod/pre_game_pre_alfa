#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

class SkillType(Enum):
    """Типы навыков"""
    COMBAT = "combat"           # Боевые навыки
    MAGIC = "magic"             # Магические навыки
    SURVIVAL = "survival"       # Навыки выживания
    SOCIAL = "social"           # Социальные навыки
    CRAFTING = "crafting"       # Навыки крафтинга
    MOVEMENT = "movement"       # Навыки движения
    PERCEPTION = "perception"   # Навыки восприятия
    STEALTH = "stealth"         # Навыки скрытности

class SkillCategory(Enum):
    """Категории навыков"""
    ACTIVE = "active"           # Активные навыки (требуют активации)
    PASSIVE = "passive"         # Пассивные навыки (работают постоянно)
    AURA = "aura"              # Аура (влияет на окружающих)
    TRIGGER = "trigger"        # Триггерные навыки (срабатывают при условиях)

@dataclass
class SkillRequirement:
    """Требования для изучения навыка"""
    attribute_requirements: Dict[str, int] = field(default_factory=dict)  # Требования к атрибутам
    skill_requirements: Dict[str, int] = field(default_factory=dict)      # Требования к другим навыкам
    level_requirement: int = 1                                              # Требуемый уровень
    experience_cost: int = 100                                              # Стоимость в опыте

@dataclass
class SkillEffect:
    """Эффект навыка"""
    effect_type: str
    value: float
    duration: float = -1.0  # -1 для постоянных эффектов
    target: str = "self"    # self, enemy, ally, area
    condition: Optional[Callable] = None  # Условие применения

@dataclass
class Skill:
    """Навык"""
    skill_id: str
    name: str
    description: str
    skill_type: SkillType
    category: SkillCategory
    max_level: int = 10
    current_level: int = 0
    experience: int = 0
    requirements: SkillRequirement = field(default_factory=SkillRequirement)
    effects: List[SkillEffect] = field(default_factory=list)
    cooldown: float = 0.0
    mana_cost: float = 0.0
    stamina_cost: float = 0.0
    hp_cost: float = 0.0
    last_used: float = 0.0
    is_learned: bool = False
    
    def can_use(self, current_mana: float, current_stamina: float) -> bool:
        """Проверка возможности использования навыка"""
        if not self.is_learned or self.current_level == 0:
            return False
        
        current_time = time.time()
        if current_time - self.last_used < self.cooldown:
            return False
        
        if current_mana < self.mana_cost:
            return False
        
        if current_stamina < self.stamina_cost:
            return False
        
        return True
    
    def use(self):
        """Использование навыка"""
        self.last_used = time.time()
    
    def add_experience(self, amount: int) -> bool:
        """Добавление опыта к навыку"""
        if not self.is_learned or self.current_level >= self.max_level:
            return False
        
        self.experience += amount
        exp_needed = self.get_experience_needed()
        
        if self.experience >= exp_needed:
            self.level_up()
            return True
        
        return False
    
    def level_up(self):
        """Повышение уровня навыка"""
        if self.current_level < self.max_level:
            self.current_level += 1
            self.experience = 0
            print(f"Навык {self.name} повышен до уровня {self.current_level}!")
    
    def get_experience_needed(self) -> int:
        """Получение необходимого опыта для следующего уровня"""
        return self.current_level * 100 + 50

class SkillTree:
    """Дерево навыков"""
    
    def __init__(self, name: str):
        self.name = name
        self.skills: Dict[str, Skill] = {}
        self.connections: Dict[str, List[str]] = {}  # Связи между навыками
    
    def add_skill(self, skill: Skill):
        """Добавление навыка в дерево"""
        self.skills[skill.skill_id] = skill
    
    def add_connection(self, from_skill: str, to_skill: str):
        """Добавление связи между навыками"""
        if from_skill not in self.connections:
            self.connections[from_skill] = []
        if to_skill not in self.connections[from_skill]:
            self.connections[from_skill].append(to_skill)
    
    def can_learn_skill(self, skill_id: str, entity_attributes: Dict[str, float], 
                       entity_skills: Dict[str, int], entity_level: int) -> bool:
        """Проверка возможности изучения навыка"""
        if skill_id not in self.skills:
            return False
        
        skill = self.skills[skill_id]
        
        # Проверяем требования к атрибутам
        for attr, required_value in skill.requirements.attribute_requirements.items():
            if entity_attributes.get(attr, 0) < required_value:
                return False
        
        # Проверяем требования к другим навыкам
        for req_skill, required_level in skill.requirements.skill_requirements.items():
            if entity_skills.get(req_skill, 0) < required_level:
                return False
        
        # Проверяем уровень
        if entity_level < skill.requirements.level_requirement:
            return False
        
        return True
    
    def get_available_skills(self, entity_attributes: Dict[str, float], 
                           entity_skills: Dict[str, int], entity_level: int) -> List[Skill]:
        """Получение доступных для изучения навыков"""
        available = []
        for skill in self.skills.values():
            if not skill.is_learned and self.can_learn_skill(
                skill.skill_id, entity_attributes, entity_skills, entity_level
            ):
                available.append(skill)
        return available

class SkillSystem:
    """Система навыков"""
    
    def __init__(self):
        self.skill_trees: Dict[str, SkillTree] = {}
        self.entity_skills: Dict[str, Dict[str, Skill]] = {}  # Навыки сущностей
        self.skill_experience_gain: Dict[str, float] = {}     # Множители получения опыта
        
        # Инициализация деревьев навыков
        self._initialize_skill_trees()
    
    def _initialize_skill_trees(self):
        """Инициализация деревьев навыков"""
        # Боевое дерево
        combat_tree = SkillTree("Combat")
        
        # Базовые боевые навыки
        sword_mastery = Skill(
            skill_id="sword_mastery",
            name="Sword Mastery",
            description="Увеличивает урон от мечей",
            skill_type=SkillType.COMBAT,
            category=SkillCategory.PASSIVE,
            effects=[
                SkillEffect("physical_damage", 5.0, target="self")
            ]
        )
        combat_tree.add_skill(sword_mastery)
        
        # Активные боевые навыки
        power_strike = Skill(
            skill_id="power_strike",
            name="Power Strike",
            description="Мощный удар с увеличенным уроном",
            skill_type=SkillType.COMBAT,
            category=SkillCategory.ACTIVE,
            cooldown=5.0,
            stamina_cost=20.0,
            effects=[
                SkillEffect("physical_damage", 50.0, duration=1.0, target="enemy")
            ]
        )
        combat_tree.add_skill(power_strike)
        
        # Магическое дерево
        magic_tree = SkillTree("Magic")
        
        fireball = Skill(
            skill_id="fireball",
            name="Fireball",
            description="Огненный шар, наносящий урон",
            skill_type=SkillType.MAGIC,
            category=SkillCategory.ACTIVE,
            cooldown=3.0,
            mana_cost=30.0,
            effects=[
                SkillEffect("magical_damage", 40.0, duration=0.0, target="enemy")
            ]
        )
        magic_tree.add_skill(fireball)
        
        # Навык лечения
        heal = Skill(
            skill_id="heal",
            name="Heal",
            description="Восстанавливает здоровье",
            skill_type=SkillType.MAGIC,
            category=SkillCategory.ACTIVE,
            cooldown=8.0,
            mana_cost=25.0,
            effects=[
                SkillEffect("heal", 30.0, duration=0.0, target="self")
            ]
        )
        magic_tree.add_skill(heal)
        
        # Дерево выживания
        survival_tree = SkillTree("Survival")
        
        # Навык регенерации
        regeneration = Skill(
            skill_id="regeneration",
            name="Regeneration",
            description="Увеличивает скорость регенерации здоровья",
            skill_type=SkillType.SURVIVAL,
            category=SkillCategory.PASSIVE,
            effects=[
                SkillEffect("health_regen", 2.0, target="self")
            ]
        )
        survival_tree.add_skill(regeneration)
        
        # Навык выносливости
        endurance_training = Skill(
            skill_id="endurance_training",
            name="Endurance Training",
            description="Увеличивает максимальную стамину",
            skill_type=SkillType.SURVIVAL,
            category=SkillCategory.PASSIVE,
            effects=[
                SkillEffect("max_stamina", 20.0, target="self")
            ]
        )
        survival_tree.add_skill(endurance_training)
        
        # Социальное дерево
        social_tree = SkillTree("Social")
        
        # Навык торговли
        trading = Skill(
            skill_id="trading",
            name="Trading",
            description="Улучшает цены при торговле",
            skill_type=SkillType.SOCIAL,
            category=SkillCategory.PASSIVE,
            effects=[
                SkillEffect("trade_discount", 5.0, target="self")
            ]
        )
        social_tree.add_skill(trading)
        
        # Навык убеждения
        persuasion = Skill(
            skill_id="persuasion",
            name="Persuasion",
            description="Увеличивает шанс успешного убеждения",
            skill_type=SkillType.SOCIAL,
            category=SkillCategory.PASSIVE,
            effects=[
                SkillEffect("persuasion_chance", 10.0, target="self")
            ]
        )
        social_tree.add_skill(persuasion)
        
        # Добавляем деревья в систему
        self.skill_trees["combat"] = combat_tree
        self.skill_trees["magic"] = magic_tree
        self.skill_trees["survival"] = survival_tree
        self.skill_trees["social"] = social_tree
    
    def initialize_entity_skills(self, entity_id: str):
        """Инициализация навыков для сущности"""
        self.entity_skills[entity_id] = {}
        
        # Копируем все навыки из деревьев
        for tree in self.skill_trees.values():
            for skill in tree.skills.values():
                skill_copy = Skill(
                    skill_id=skill.skill_id,
                    name=skill.name,
                    description=skill.description,
                    skill_type=skill.skill_type,
                    category=skill.category,
                    max_level=skill.max_level,
                    requirements=skill.requirements,
                    effects=skill.effects.copy(),
                    cooldown=skill.cooldown,
                    mana_cost=skill.mana_cost,
                    stamina_cost=skill.stamina_cost
                )
                self.entity_skills[entity_id][skill.skill_id] = skill_copy
    
    def learn_skill(self, entity_id: str, skill_id: str, entity_attributes: Dict[str, float],
                   entity_level: int, experience_cost: int) -> bool:
        """Изучение навыка"""
        if entity_id not in self.entity_skills:
            self.initialize_entity_skills(entity_id)
        
        if skill_id not in self.entity_skills[entity_id]:
            return False
        
        skill = self.entity_skills[entity_id][skill_id]
        
        if skill.is_learned:
            return False
        
        # Проверяем требования
        entity_skills = {sid: s.current_level for sid, s in self.entity_skills[entity_id].items() if s.is_learned}
        
        for tree in self.skill_trees.values():
            if not tree.can_learn_skill(skill_id, entity_attributes, entity_skills, entity_level):
                return False
        
        # Изучаем навык
        skill.is_learned = True
        skill.current_level = 1
        skill.experience = 0
        
        return True
    
    def use_skill(self, entity_id: str, skill_id: str, current_mana: float, 
                 current_stamina: float) -> Optional[List[SkillEffect]]:
        """Использование навыка"""
        if entity_id not in self.entity_skills or skill_id not in self.entity_skills[entity_id]:
            return None
        
        skill = self.entity_skills[entity_id][skill_id]
        
        if not skill.can_use(current_mana, current_stamina):
            return None
        
        skill.use()
        return skill.effects.copy()
    
    def add_skill_experience(self, entity_id: str, skill_id: str, amount: int):
        """Добавление опыта к навыку"""
        if entity_id not in self.entity_skills or skill_id not in self.entity_skills[entity_id]:
            return
        
        skill = self.entity_skills[entity_id][skill_id]
        
        # Применяем множитель опыта
        multiplier = self.skill_experience_gain.get(skill_id, 1.0)
        actual_amount = int(amount * multiplier)
        
        skill.add_experience(actual_amount)
    
    def get_entity_skills(self, entity_id: str) -> Dict[str, Skill]:
        """Получение навыков сущности"""
        return self.entity_skills.get(entity_id, {})
    
    def get_available_skills(self, entity_id: str, entity_attributes: Dict[str, float],
                           entity_level: int) -> List[Skill]:
        """Получение доступных для изучения навыков"""
        if entity_id not in self.entity_skills:
            self.initialize_entity_skills(entity_id)
        
        entity_skills = {sid: s.current_level for sid, s in self.entity_skills[entity_id].items() if s.is_learned}
        available = []
        
        for tree in self.skill_trees.values():
            available.extend(tree.get_available_skills(entity_attributes, entity_skills, entity_level))
        
        return available
    
    def get_skill_effects(self, entity_id: str) -> Dict[str, float]:
        """Получение всех эффектов навыков сущности"""
        effects = {}
        
        if entity_id not in self.entity_skills:
            return effects
        
        for skill in self.entity_skills[entity_id].values():
            if skill.is_learned and skill.category == SkillCategory.PASSIVE:
                for effect in skill.effects:
                    if effect.effect_type not in effects:
                        effects[effect.effect_type] = 0.0
                    effects[effect.effect_type] += effect.value * skill.current_level
        
        return effects
    
    def set_skill_experience_multiplier(self, skill_id: str, multiplier: float):
        """Установка множителя получения опыта для навыка"""
        self.skill_experience_gain[skill_id] = multiplier
    
    def get_skill_tree(self, tree_name: str) -> Optional[SkillTree]:
        """Получение дерева навыков"""
        return self.skill_trees.get(tree_name)
    
    def get_all_skill_trees(self) -> Dict[str, SkillTree]:
        """Получение всех деревьев навыков"""
        return self.skill_trees.copy()
