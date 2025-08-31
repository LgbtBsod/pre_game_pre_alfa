#!/usr/bin/env python3
"""Система навыков - дерево навыков, прогрессия и специализации
Управление навыками, их развитием и комбинациями"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import math
import time
import random

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState

logger = logging.getLogger(__name__)

# = ТИПЫ НАВЫКОВ

class SkillType(Enum):
    """Типы навыков"""
    COMBAT = "combat"          # Боевые навыки
    MAGIC = "magic"            # Магические навыки
    CRAFTING = "crafting"      # Ремесленные навыки
    SOCIAL = "social"          # Социальные навыки
    SURVIVAL = "survival"      # Навыки выживания
    UTILITY = "utility"        # Утилитарные навыки

class SkillCategory(Enum):
    """Категории навыков"""
    ACTIVE = "active"          # Активные навыки
    PASSIVE = "passive"        # Пассивные навыки
    ULTIMATE = "ultimate"      # Ультимативные навыки
    SPECIALIZATION = "specialization"  # Специализации

class SkillTier(Enum):
    """Уровни навыков"""
    BASIC = "basic"            # Базовый
    INTERMEDIATE = "intermediate"  # Промежуточный
    ADVANCED = "advanced"      # Продвинутый
    MASTER = "master"          # Мастерский
    LEGENDARY = "legendary"    # Легендарный

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class SkillRequirement:
    """Требование для навыка"""
    requirement_type: str  # level, skill, item, quest
    target: str
    value: Any
    description: str

@dataclass
class SkillEffect:
    """Эффект навыка"""
    effect_type: str
    value: float
    duration: float = 0.0
    condition: Optional[str] = None
    target: str = "self"  # self, target, area

@dataclass
class SkillModifier:
    """Модификатор навыка"""
    stat_type: str
    value: float
    modifier_type: str = "additive"  # additive, multiplicative
    condition: Optional[str] = None

@dataclass
class SkillNode:
    """Узел дерева навыков"""
    skill_id: str
    name: str
    description: str
    skill_type: SkillType
    category: SkillCategory
    tier: SkillTier
    max_level: int = 1
    requirements: List[SkillRequirement] = field(default_factory=list)
    effects: List[SkillEffect] = field(default_factory=list)
    modifiers: List[SkillModifier] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)  # skill_ids
    children: List[str] = field(default_factory=list)  # skill_ids
    icon_path: Optional[str] = None
    cost: Dict[str, int] = field(default_factory=dict)  # skill_points, experience, etc.
    cooldown: float = 0.0
    cast_time: float = 0.0
    range: float = 0.0
    area_radius: float = 0.0

@dataclass
class SkillTree:
    """Дерево навыков"""
    tree_id: str
    name: str
    description: str
    root_skills: List[str] = field(default_factory=list)
    nodes: Dict[str, SkillNode] = field(default_factory=dict)
    max_skill_points: int = 100
    specialization_count: int = 3

@dataclass
class EntitySkill:
    """Навык сущности"""
    skill_id: str
    entity_id: str
    level: int = 1
    experience: int = 0
    experience_to_next: int = 100
    is_unlocked: bool = False
    is_specialized: bool = False
    last_used: float = 0.0
    total_uses: int = 0
    learned_at: float = field(default_factory=time.time)

@dataclass
class SkillCombo:
    """Комбо навыков"""
    combo_id: str
    name: str
    description: str
    skills: List[str]  # skill_ids в порядке использования
    time_window: float = 5.0  # Время для выполнения комбо
    bonus_effects: List[SkillEffect] = field(default_factory=list)
    bonus_modifiers: List[SkillModifier] = field(default_factory=list)

class SkillSystem(BaseComponent):
    """Система навыков"""
    
    def __init__(self):
        super().__init__(
            component_id="skill_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.NORMAL
        )
        
        # Деревья навыков
        self.skill_trees: Dict[str, SkillTree] = {}
        self.entity_skills: Dict[str, Dict[str, EntitySkill]] = {}  # entity_id -> skills
        
        # Комбо
        self.skill_combos: Dict[str, SkillCombo] = {}
        self.active_combos: Dict[str, List[str]] = {}  # entity_id -> combo_progress
        
        # Статистика
        self.total_skills_learned: int = 0
        self.total_skill_uses: int = 0
        self.skill_statistics: Dict[str, int] = {}
        
        # Callbacks
        self.on_skill_learned: Optional[Callable] = None
        self.on_skill_leveled: Optional[Callable] = None
        self.on_skill_used: Optional[Callable] = None
        self.on_combo_completed: Optional[Callable] = None
        
        logger.info("Система навыков инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы навыков"""
        try:
            logger.info("Инициализация системы навыков...")
            
            # Создание деревьев навыков
            if not self._create_skill_trees():
                return False
            
            # Создание комбо
            if not self._create_skill_combos():
                return False
            
            self.state = LifecycleState.READY
            logger.info("Система навыков успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы навыков: {e}")
            self.state = LifecycleState.ERROR
            return False
    
    def _create_skill_trees(self) -> bool:
        """Создание деревьев навыков"""
        try:
            # Дерево боевых навыков
            combat_tree = SkillTree(
                tree_id="combat_tree",
                name="Боевые навыки",
                description="Навыки для ведения боя",
                max_skill_points=50,
                specialization_count=2
            )
            
            # Базовые боевые навыки
            basic_attack = SkillNode(
                skill_id="basic_attack",
                name="Базовая атака",
                description="Обычная атака оружием",
                skill_type=SkillType.COMBAT,
                category=SkillCategory.ACTIVE,
                tier=SkillTier.BASIC,
                max_level=5,
                effects=[
                    SkillEffect("damage", 10.0, target="target")
                ],
                cost={"skill_points": 0},
                cooldown=1.0,
                cast_time=0.5,
                range=2.0
            )
            
            power_strike = SkillNode(
                skill_id="power_strike",
                name="Мощный удар",
                description="Сильная атака с повышенным уроном",
                skill_type=SkillType.COMBAT,
                category=SkillCategory.ACTIVE,
                tier=SkillTier.INTERMEDIATE,
                max_level=3,
                requirements=[
                    SkillRequirement("skill", "basic_attack", 3, "Базовая атака 3 уровня")
                ],
                effects=[
                    SkillEffect("damage", 25.0, target="target")
                ],
                cost={"skill_points": 5},
                cooldown=3.0,
                cast_time=1.0,
                range=2.0
            )
            
            whirlwind = SkillNode(
                skill_id="whirlwind",
                name="Вихрь",
                description="Атака по области вокруг себя",
                skill_type=SkillType.COMBAT,
                category=SkillCategory.ACTIVE,
                tier=SkillTier.ADVANCED,
                max_level=2,
                requirements=[
                    SkillRequirement("skill", "power_strike", 2, "Мощный удар 2 уровня")
                ],
                effects=[
                    SkillEffect("damage", 15.0, target="area")
                ],
                cost={"skill_points": 10},
                cooldown=8.0,
                cast_time=1.5,
                area_radius=3.0
            )
            
            # Добавление навыков в дерево
            combat_tree.nodes[basic_attack.skill_id] = basic_attack
            combat_tree.nodes[power_strike.skill_id] = power_strike
            combat_tree.nodes[whirlwind.skill_id] = whirlwind
            
            # Установка связей
            combat_tree.root_skills = [basic_attack.skill_id]
            basic_attack.children = [power_strike.skill_id]
            power_strike.prerequisites = [basic_attack.skill_id]
            power_strike.children = [whirlwind.skill_id]
            whirlwind.prerequisites = [power_strike.skill_id]
            
            # Дерево магических навыков
            magic_tree = SkillTree(
                tree_id="magic_tree",
                name="Магические навыки",
                description="Навыки магии и заклинаний",
                max_skill_points=50,
                specialization_count=2
            )
            
            fireball = SkillNode(
                skill_id="fireball",
                name="Огненный шар",
                description="Магическая атака огнем",
                skill_type=SkillType.MAGIC,
                category=SkillCategory.ACTIVE,
                tier=SkillTier.BASIC,
                max_level=5,
                effects=[
                    SkillEffect("magic_damage", 20.0, target="target"),
                    SkillEffect("burn", 5.0, duration=3.0, target="target")
                ],
                cost={"skill_points": 0, "mana": 15},
                cooldown=2.0,
                cast_time=1.0,
                range=10.0
            )
            
            lightning_bolt = SkillNode(
                skill_id="lightning_bolt",
                name="Молния",
                description="Быстрая электрическая атака",
                skill_type=SkillType.MAGIC,
                category=SkillCategory.ACTIVE,
                tier=SkillTier.INTERMEDIATE,
                max_level=3,
                requirements=[
                    SkillRequirement("skill", "fireball", 3, "Огненный шар 3 уровня")
                ],
                effects=[
                    SkillEffect("magic_damage", 30.0, target="target"),
                    SkillEffect("stun", 1.0, duration=1.0, target="target")
                ],
                cost={"skill_points": 5, "mana": 25},
                cooldown=4.0,
                cast_time=0.5,
                range=12.0
            )
            
            # Добавление навыков в дерево
            magic_tree.nodes[fireball.skill_id] = fireball
            magic_tree.nodes[lightning_bolt.skill_id] = lightning_bolt
            
            # Установка связей
            magic_tree.root_skills = [fireball.skill_id]
            fireball.children = [lightning_bolt.skill_id]
            lightning_bolt.prerequisites = [fireball.skill_id]
            
            # Сохранение деревьев
            self.skill_trees[combat_tree.tree_id] = combat_tree
            self.skill_trees[magic_tree.tree_id] = magic_tree
            
            logger.info(f"Создано {len(self.skill_trees)} деревьев навыков")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания деревьев навыков: {e}")
            return False
    
    def _create_skill_combos(self) -> bool:
        """Создание комбо навыков"""
        try:
            # Комбо: Базовая атака + Мощный удар
            basic_combo = SkillCombo(
                combo_id="basic_combo",
                name="Комбо атака",
                description="Базовая атака с последующим мощным ударом",
                skills=["basic_attack", "power_strike"],
                time_window=3.0,
                bonus_effects=[
                    SkillEffect("damage", 10.0, target="target")
                ]
            )
            
            # Комбо: Огненный шар + Молния
            magic_combo = SkillCombo(
                combo_id="magic_combo",
                name="Магическое комбо",
                description="Огненный шар с последующей молнией",
                skills=["fireball", "lightning_bolt"],
                time_window=4.0,
                bonus_effects=[
                    SkillEffect("magic_damage", 15.0, target="target"),
                    SkillEffect("burn", 3.0, duration=2.0, target="target")
                ]
            )
            
            self.skill_combos[basic_combo.combo_id] = basic_combo
            self.skill_combos[magic_combo.combo_id] = magic_combo
            
            logger.info(f"Создано {len(self.skill_combos)} комбо навыков")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания комбо навыков: {e}")
            return False
    
    def learn_skill(self, entity_id: str, skill_id: str, tree_id: str) -> bool:
        """Изучение навыка"""
        try:
            if tree_id not in self.skill_trees:
                logger.error(f"Дерево навыков {tree_id} не найдено")
                return False
            
            tree = self.skill_trees[tree_id]
            
            if skill_id not in tree.nodes:
                logger.error(f"Навык {skill_id} не найден в дереве {tree_id}")
                return False
            
            skill_node = tree.nodes[skill_id]
            
            # Проверка требований
            if not self._check_skill_requirements(entity_id, skill_node):
                logger.warning(f"Требования для навыка {skill_id} не выполнены")
                return False
            
            # Проверка доступности навыка
            if not self._is_skill_available(entity_id, skill_id, tree):
                logger.warning(f"Навык {skill_id} недоступен для изучения")
                return False
            
            # Создание навыка сущности
            if entity_id not in self.entity_skills:
                self.entity_skills[entity_id] = {}
            
            entity_skill = EntitySkill(
                skill_id=skill_id,
                entity_id=entity_id,
                is_unlocked=True
            )
            
            self.entity_skills[entity_id][skill_id] = entity_skill
            
            # Обновление статистики
            self.total_skills_learned += 1
            self.skill_statistics[skill_id] = self.skill_statistics.get(skill_id, 0) + 1
            
            # Вызов callback
            if self.on_skill_learned:
                self.on_skill_learned(entity_id, skill_id)
            
            logger.info(f"Навык {skill_id} изучен сущностью {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка изучения навыка: {e}")
            return False
    
    def _check_skill_requirements(self, entity_id: str, skill_node: SkillNode) -> bool:
        """Проверка требований для навыка"""
        try:
            for requirement in skill_node.requirements:
                if requirement.requirement_type == "skill":
                    if not self.has_skill(entity_id, requirement.target):
                        return False
                    
                    entity_skill = self.get_entity_skill(entity_id, requirement.target)
                    if entity_skill.level < requirement.value:
                        return False
                
                elif requirement.requirement_type == "level":
                    # Здесь должна быть проверка уровня сущности
                    pass
                
                elif requirement.requirement_type == "quest":
                    # Здесь должна быть проверка выполнения квеста
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки требований навыка: {e}")
            return False
    
    def _is_skill_available(self, entity_id: str, skill_id: str, tree: SkillTree) -> bool:
        """Проверка доступности навыка для изучения"""
        try:
            skill_node = tree.nodes[skill_id]
            
            # Проверка предварительных навыков
            for prereq_id in skill_node.prerequisites:
                if not self.has_skill(entity_id, prereq_id):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки доступности навыка: {e}")
            return False
    
    def use_skill(self, entity_id: str, skill_id: str, target_id: Optional[str] = None) -> bool:
        """Использование навыка"""
        try:
            if not self.has_skill(entity_id, skill_id):
                logger.error(f"Сущность {entity_id} не знает навык {skill_id}")
                return False
            
            entity_skill = self.get_entity_skill(entity_id, skill_id)
            
            # Поиск узла навыка
            skill_node = None
            for tree in self.skill_trees.values():
                if skill_id in tree.nodes:
                    skill_node = tree.nodes[skill_id]
                    break
            
            if not skill_node:
                logger.error(f"Узел навыка {skill_id} не найден")
                return False
            
            # Проверка кулдауна
            current_time = time.time()
            if current_time - entity_skill.last_used < skill_node.cooldown:
                logger.warning(f"Навык {skill_id} на кулдауне")
                return False
            
            # Проверка времени произнесения
            if skill_node.cast_time > 0:
                # Здесь должна быть логика произнесения заклинания
                pass
            
            # Применение эффектов навыка
            self._apply_skill_effects(entity_id, skill_node, target_id)
            
            # Обновление статистики
            entity_skill.last_used = current_time
            entity_skill.total_uses += 1
            self.total_skill_uses += 1
            
            # Обработка комбо
            self._process_skill_combo(entity_id, skill_id)
            
            # Вызов callback
            if self.on_skill_used:
                self.on_skill_used(entity_id, skill_id, target_id)
            
            logger.info(f"Навык {skill_id} использован сущностью {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка использования навыка: {e}")
            return False
    
    def _apply_skill_effects(self, entity_id: str, skill_node: SkillNode, target_id: Optional[str]):
        """Применение эффектов навыка"""
        try:
            entity_skill = self.get_entity_skill(entity_id, skill_node.skill_id)
            
            for effect in skill_node.effects:
                # Применение эффекта в зависимости от уровня навыка
                effect_value = effect.value * entity_skill.level
                
                if effect.target == "self":
                    # Применение к себе
                    self._apply_effect_to_entity(entity_id, effect, effect_value)
                
                elif effect.target == "target" and target_id:
                    # Применение к цели
                    self._apply_effect_to_entity(target_id, effect, effect_value)
                
                elif effect.target == "area":
                    # Применение к области
                    self._apply_area_effect(entity_id, effect, effect_value, skill_node.area_radius)
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов навыка: {e}")
    
    def _apply_effect_to_entity(self, entity_id: str, effect: SkillEffect, value: float):
        """Применение эффекта к сущности"""
        try:
            # Здесь должна быть интеграция с другими системами
            # Например, система урона, система эффектов и т.д.
            logger.debug(f"Эффект {effect.effect_type} применен к {entity_id}: {value}")
            
        except Exception as e:
            logger.error(f"Ошибка применения эффекта к сущности: {e}")
    
    def _apply_area_effect(self, caster_id: str, effect: SkillEffect, value: float, radius: float):
        """Применение эффекта к области"""
        try:
            # Здесь должна быть логика поиска сущностей в радиусе
            # и применения эффекта к ним
            logger.debug(f"Областной эффект {effect.effect_type} применен от {caster_id}")
            
        except Exception as e:
            logger.error(f"Ошибка применения областного эффекта: {e}")
    
    def _process_skill_combo(self, entity_id: str, skill_id: str):
        """Обработка комбо навыков"""
        try:
            current_time = time.time()
            
            if entity_id not in self.active_combos:
                self.active_combos[entity_id] = []
            
            # Проверка существующих комбо
            for combo_id in list(self.active_combos[entity_id]):
                combo = self.skill_combos[combo_id]
                
                # Проверка времени выполнения комбо
                if current_time - combo.last_used > combo.time_window:
                    self.active_combos[entity_id].remove(combo_id)
                    continue
                
                # Проверка следующего навыка в комбо
                current_progress = len(self.active_combos[entity_id])
                if current_progress < len(combo.skills):
                    if combo.skills[current_progress] == skill_id:
                        # Добавление навыка к комбо
                        self.active_combos[entity_id].append(skill_id)
                        
                        # Проверка завершения комбо
                        if len(self.active_combos[entity_id]) == len(combo.skills):
                            self._complete_combo(entity_id, combo_id)
                        break
            
            # Проверка новых комбо
            for combo_id, combo in self.skill_combos.items():
                if combo.skills[0] == skill_id:
                    self.active_combos[entity_id] = [skill_id]
                    combo.last_used = current_time
                    break
            
        except Exception as e:
            logger.error(f"Ошибка обработки комбо навыков: {e}")
    
    def _complete_combo(self, entity_id: str, combo_id: str):
        """Завершение комбо"""
        try:
            combo = self.skill_combos[combo_id]
            
            # Применение бонусных эффектов
            for effect in combo.bonus_effects:
                self._apply_effect_to_entity(entity_id, effect, effect.value)
            
            # Очистка комбо
            if entity_id in self.active_combos:
                self.active_combos[entity_id] = []
            
            # Вызов callback
            if self.on_combo_completed:
                self.on_combo_completed(entity_id, combo_id)
            
            logger.info(f"Комбо {combo_id} завершено сущностью {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка завершения комбо: {e}")
    
    def gain_skill_experience(self, entity_id: str, skill_id: str, experience: int) -> bool:
        """Получение опыта навыка"""
        try:
            if not self.has_skill(entity_id, skill_id):
                return False
            
            entity_skill = self.get_entity_skill(entity_id, skill_id)
            entity_skill.experience += experience
            
            # Проверка повышения уровня
            while entity_skill.experience >= entity_skill.experience_to_next:
                if entity_skill.level >= self._get_max_skill_level(skill_id):
                    break
                
                entity_skill.experience -= entity_skill.experience_to_next
                entity_skill.level += 1
                entity_skill.experience_to_next = self._calculate_next_level_exp(entity_skill.level)
                
                # Вызов callback
                if self.on_skill_leveled:
                    self.on_skill_leveled(entity_id, skill_id, entity_skill.level)
                
                logger.info(f"Навык {skill_id} повышен до уровня {entity_skill.level}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка получения опыта навыка: {e}")
            return False
    
    def _get_max_skill_level(self, skill_id: str) -> int:
        """Получение максимального уровня навыка"""
        try:
            for tree in self.skill_trees.values():
                if skill_id in tree.nodes:
                    return tree.nodes[skill_id].max_level
            return 1
            
        except Exception as e:
            logger.error(f"Ошибка получения максимального уровня навыка: {e}")
            return 1
    
    def _calculate_next_level_exp(self, current_level: int) -> int:
        """Расчет опыта для следующего уровня"""
        try:
            # Простая формула: базовый опыт * уровень^1.5
            base_exp = 100
            return int(base_exp * (current_level ** 1.5))
            
        except Exception as e:
            logger.error(f"Ошибка расчета опыта для следующего уровня: {e}")
            return 100
    
    def has_skill(self, entity_id: str, skill_id: str) -> bool:
        """Проверка наличия навыка у сущности"""
        try:
            if entity_id not in self.entity_skills:
                return False
            
            return skill_id in self.entity_skills[entity_id]
            
        except Exception as e:
            logger.error(f"Ошибка проверки наличия навыка: {e}")
            return False
    
    def get_entity_skill(self, entity_id: str, skill_id: str) -> Optional[EntitySkill]:
        """Получение навыка сущности"""
        try:
            if not self.has_skill(entity_id, skill_id):
                return None
            
            return self.entity_skills[entity_id][skill_id]
            
        except Exception as e:
            logger.error(f"Ошибка получения навыка сущности: {e}")
            return None
    
    def get_entity_skills(self, entity_id: str, skill_type: Optional[SkillType] = None) -> List[EntitySkill]:
        """Получение всех навыков сущности"""
        try:
            if entity_id not in self.entity_skills:
                return []
            
            skills = list(self.entity_skills[entity_id].values())
            
            if skill_type is None:
                return skills
            
            # Фильтрация по типу
            filtered_skills = []
            for skill in skills:
                for tree in self.skill_trees.values():
                    if skill.skill_id in tree.nodes:
                        if tree.nodes[skill.skill_id].skill_type == skill_type:
                            filtered_skills.append(skill)
                        break
            
            return filtered_skills
            
        except Exception as e:
            logger.error(f"Ошибка получения навыков сущности: {e}")
            return []
    
    def get_available_skills(self, entity_id: str, tree_id: str) -> List[SkillNode]:
        """Получение доступных для изучения навыков"""
        try:
            if tree_id not in self.skill_trees:
                return []
            
            tree = self.skill_trees[tree_id]
            available_skills = []
            
            for skill_node in tree.nodes.values():
                if not self.has_skill(entity_id, skill_node.skill_id):
                    if self._is_skill_available(entity_id, skill_node.skill_id, tree):
                        if self._check_skill_requirements(entity_id, skill_node):
                            available_skills.append(skill_node)
            
            return available_skills
            
        except Exception as e:
            logger.error(f"Ошибка получения доступных навыков: {e}")
            return []
    
    def get_skill_statistics(self) -> Dict[str, Any]:
        """Получение статистики навыков"""
        try:
            return {
                "total_skills_learned": self.total_skills_learned,
                "total_skill_uses": self.total_skill_uses,
                "skill_trees_count": len(self.skill_trees),
                "skill_combos_count": len(self.skill_combos),
                "skill_statistics": self.skill_statistics.copy()
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики навыков: {e}")
            return {}
    
    def cleanup(self):
        """Очистка системы навыков"""
        try:
            # Очистка данных
            self.skill_trees.clear()
            self.entity_skills.clear()
            self.skill_combos.clear()
            self.active_combos.clear()
            self.skill_statistics.clear()
            
            logger.info("Система навыков очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы навыков: {e}")
