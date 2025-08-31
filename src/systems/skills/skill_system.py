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
from src.core.constants import DamageType, constants_manager
from src.core.state_manager import StateManager, StateType
from src.systems.attributes.attribute_system import AttributeSystem, AttributeSet, AttributeModifier, StatModifier, BaseAttribute, DerivedStat

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
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"
    LEGENDARY = "legendary"

class SkillTarget(Enum):
    """Цели навыков"""
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    SINGLE_ALLY = "single_ally"
    AREA_ENEMIES = "area_enemies"
    AREA_ALLIES = "area_allies"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class SkillRequirement:
    """Требование для навыка"""
    requirement_type: str  # skill, level, attribute, item
    requirement_id: str
    value: int
    description: str

@dataclass
class SkillEffect:
    """Эффект навыка"""
    effect_type: str  # damage, heal, buff, debuff, movement
    value: float
    target: str
    duration: float = 0.0
    radius: float = 0.0
    angle: float = 360.0
    condition: Optional[str] = None

@dataclass
class SkillModifier:
    """Модификатор навыка (интеграция с системой атрибутов)"""
    modifier_type: str  # attribute, stat, temporary
    target: str  # attribute_name или stat_name
    value: float
    duration: float = -1.0  # -1 для постоянных модификаторов
    is_percentage: bool = False
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
    
    # Интеграция с системой атрибутов
    attribute_requirements: Dict[str, int] = field(default_factory=dict)  # attribute_name -> min_value
    stat_requirements: Dict[str, int] = field(default_factory=dict)  # stat_name -> min_value
    attribute_scaling: Dict[str, float] = field(default_factory=dict)  # attribute_name -> scaling_factor
    stat_scaling: Dict[str, float] = field(default_factory=dict)  # stat_name -> scaling_factor

@dataclass
class SkillTree:
    """Дерево навыков"""
    tree_id: str
    name: str
    description: str
    skill_points: int = 0
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
    
    # Интеграция с системой атрибутов
    active_modifiers: List[AttributeModifier] = field(default_factory=list)
    active_stat_modifiers: List[StatModifier] = field(default_factory=list)

@dataclass
class SkillCombo:
    """Комбо навыков"""
    combo_id: str
    name: str
    description: str
    skill_sequence: List[str]  # skill_ids в правильном порядке
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
        
        # Архитектурные компоненты
        self.state_manager: Optional[StateManager] = None
        self.attribute_system: Optional[AttributeSystem] = None
        
        # Деревья навыков
        self.skill_trees: Dict[str, SkillTree] = {}
        self.entity_skills: Dict[str, Dict[str, EntitySkill]] = {}  # entity_id -> skills
        
        # Комбо
        self.skill_combos: Dict[str, SkillCombo] = {}
        self.active_combos: Dict[str, List[str]] = {}  # entity_id -> combo_progress
        
        # Настройки системы
        self.system_settings = {
            'auto_calculate_skill_power_from_attributes': True,
            'enable_skill_modifiers': True,
            'enable_skill_combos': True,
            'skill_experience_enabled': True,
            'max_active_modifiers_per_skill': 10
        }
        
        # Статистика
        self.system_stats = {
            'total_skills_learned': 0,
            'total_skill_uses': 0,
            'total_skill_levels': 0,
            'active_modifiers': 0,
            'combo_completions': 0,
            'update_time': 0.0
        }
        
        # Callbacks
        self.on_skill_learned: Optional[Callable] = None
        self.on_skill_leveled: Optional[Callable] = None
        self.on_skill_used: Optional[Callable] = None
        self.on_combo_completed: Optional[Callable] = None
        
        logger.info("Система навыков инициализирована")
    
    def set_architecture_components(self, state_manager: StateManager, attribute_system: AttributeSystem):
        """Установка архитектурных компонентов"""
        self.state_manager = state_manager
        self.attribute_system = attribute_system
        logger.info("Архитектурные компоненты установлены в SkillSystem")
    
    def _register_system_states(self):
        """Регистрация состояний системы"""
        if self.state_manager:
            self.state_manager.set_state(
                f"{self.system_name}_settings",
                self.system_settings,
                StateType.SETTINGS
            )
            
            self.state_manager.set_state(
                f"{self.system_name}_stats",
                self.system_stats,
                StateType.STATISTICS
            )
            
            self.state_manager.set_state(
                f"{self.system_name}_state",
                self.system_state,
                StateType.SYSTEM_STATE
            )
    
    def initialize(self) -> bool:
        """Инициализация системы навыков"""
        try:
            logger.info("Инициализация SkillSystem...")
            
            self._register_system_states()
            
            # Создание базовых деревьев навыков
            self._create_skill_trees()
            
            self.system_state = LifecycleState.READY
            logger.info("SkillSystem инициализирован успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации SkillSystem: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def start(self) -> bool:
        """Запуск системы навыков"""
        try:
            logger.info("Запуск SkillSystem...")
            
            if self.system_state != LifecycleState.READY:
                logger.error("SkillSystem не готов к запуску")
                return False
            
            self.system_state = LifecycleState.RUNNING
            logger.info("SkillSystem запущен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска SkillSystem: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def update(self, delta_time: float):
        """Обновление системы навыков"""
        if self.system_state != LifecycleState.RUNNING:
            return
        
        try:
            start_time = time.time()
            
            # Обновление активных модификаторов навыков
            self._update_skill_modifiers(delta_time)
            
            # Обновление комбо
            if self.system_settings['enable_skill_combos']:
                self._update_skill_combos(delta_time)
            
            self.system_stats['update_time'] = time.time() - start_time
            
            # Обновляем состояние в менеджере состояний
            if self.state_manager:
                self.state_manager.set_state(
                    f"{self.system_name}_stats",
                    self.system_stats,
                    StateType.STATISTICS
                )
                
        except Exception as e:
            logger.error(f"Ошибка обновления SkillSystem: {e}")
    
    def stop(self) -> bool:
        """Остановка системы навыков"""
        try:
            logger.info("Остановка SkillSystem...")
            
            self.system_state = LifecycleState.STOPPED
            logger.info("SkillSystem остановлен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки SkillSystem: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы навыков"""
        try:
            logger.info("Уничтожение SkillSystem...")
            
            # Очистка всех модификаторов навыков
            self._clear_all_skill_modifiers()
            
            self.skill_trees.clear()
            self.entity_skills.clear()
            self.skill_combos.clear()
            self.active_combos.clear()
            
            self.system_state = LifecycleState.DESTROYED
            logger.info("SkillSystem уничтожен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения SkillSystem: {e}")
            return False
    
    def _update_skill_modifiers(self, delta_time: float):
        """Обновление модификаторов навыков"""
        current_time = time.time()
        
        for entity_id, skills in self.entity_skills.items():
            for skill_id, skill in skills.items():
                # Очищаем истекшие модификаторы
                skill.active_modifiers = [
                    mod for mod in skill.active_modifiers
                    if mod.duration == -1.0 or current_time - mod.start_time < mod.duration
                ]
                
                skill.active_stat_modifiers = [
                    mod for mod in skill.active_stat_modifiers
                    if mod.duration == -1.0 or current_time - mod.start_time < mod.duration
                ]
        
        # Обновляем статистику
        total_modifiers = sum(
            len(skill.active_modifiers) + len(skill.active_stat_modifiers)
            for skills in self.entity_skills.values()
            for skill in skills.values()
        )
        self.system_stats['active_modifiers'] = total_modifiers
    
    def _update_skill_combos(self, delta_time: float):
        """Обновление комбо навыков"""
        current_time = time.time()
        
        expired_combos = []
        for entity_id, combo_progress in self.active_combos.items():
            # Проверяем истечение времени комбо
            if len(combo_progress) > 0:
                first_skill_time = combo_progress[0].get('time', 0)
                if current_time - first_skill_time > 5.0:  # 5 секунд на комбо
                    expired_combos.append(entity_id)
        
        # Очищаем истекшие комбо
        for entity_id in expired_combos:
            del self.active_combos[entity_id]
    
    def _clear_all_skill_modifiers(self):
        """Очистка всех модификаторов навыков"""
        for entity_id, skills in self.entity_skills.items():
            for skill_id, skill in skills.items():
                skill.active_modifiers.clear()
                skill.active_stat_modifiers.clear()
    
    def _create_skill_trees(self):
        """Создание базовых деревьев навыков"""
        try:
            # Дерево боевых навыков
            combat_tree = SkillTree(
                tree_id="combat_tree",
                name="Боевые навыки",
                description="Навыки для ведения боя",
                max_skill_points=50,
                specialization_count=2
            )
            
            # Базовые боевые навыки с интеграцией атрибутов
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
                modifiers=[
                    SkillModifier("stat", "physical_damage", 5.0, duration=5.0, is_percentage=True)
                ],
                cost={"skill_points": 0},
                cooldown=1.0,
                cast_time=0.5,
                range=2.0,
                attribute_scaling={"strength": 0.5, "agility": 0.3},
                stat_scaling={"physical_damage": 1.0}
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
                    SkillRequirement("skill", "basic_attack", 3, "Базовая атака 3 уровня"),
                    SkillRequirement("attribute", "strength", 15, "Сила 15")
                ],
                effects=[
                    SkillEffect("damage", 25.0, target="target")
                ],
                modifiers=[
                    SkillModifier("attribute", "strength", 10.0, duration=10.0),
                    SkillModifier("stat", "critical_chance", 0.1, duration=5.0, is_percentage=True)
                ],
                cost={"skill_points": 5},
                cooldown=3.0,
                cast_time=1.0,
                range=2.0,
                attribute_requirements={"strength": 15},
                attribute_scaling={"strength": 1.0, "agility": 0.2},
                stat_scaling={"physical_damage": 1.5, "critical_damage": 0.5}
            )
            
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
                    SkillEffect("damage", 15.0, target="target", radius=2.0)
                ],
                modifiers=[
                    SkillModifier("stat", "magical_damage", 10.0, duration=8.0),
                    SkillModifier("stat", "mana_regen", 2.0, duration=5.0)
                ],
                cost={"skill_points": 3, "mana": 20},
                cooldown=2.0,
                cast_time=1.0,
                range=8.0,
                area_radius=2.0,
                attribute_requirements={"intelligence": 12},
                attribute_scaling={"intelligence": 0.8, "wisdom": 0.4},
                stat_scaling={"magical_damage": 1.2}
            )
            
            # Добавляем деревья в систему
            self.skill_trees["combat_tree"] = combat_tree
            self.skill_trees["magic_tree"] = magic_tree
            
            # Добавляем навыки в деревья
            combat_tree.skills = {
                "basic_attack": basic_attack,
                "power_strike": power_strike
            }
            
            magic_tree.skills = {
                "fireball": fireball
            }
            
            logger.info(f"Создано {len(self.skill_trees)} деревьев навыков")
            
        except Exception as e:
            logger.error(f"Ошибка создания деревьев навыков: {e}")
    
    def learn_skill(self, entity_id: str, skill_id: str, base_attributes: AttributeSet,
                   attribute_modifiers: List[AttributeModifier] = None,
                   stat_modifiers: List[StatModifier] = None) -> bool:
        """Изучение навыка с проверкой требований атрибутов"""
        try:
            # Находим навык
            skill_node = self._find_skill_node(skill_id)
            if not skill_node:
                logger.warning(f"Навык {skill_id} не найден")
                return False
            
            # Проверяем требования атрибутов
            if not self._check_attribute_requirements(skill_node, base_attributes, attribute_modifiers, stat_modifiers):
                logger.warning(f"Сущность {entity_id} не соответствует требованиям атрибутов для навыка {skill_id}")
                return False
            
            # Проверяем требования навыков
            if not self._check_skill_requirements(entity_id, skill_node):
                logger.warning(f"Сущность {entity_id} не соответствует требованиям навыков для {skill_id}")
                return False
            
            # Создаем навык сущности
            entity_skill = EntitySkill(
                skill_id=skill_id,
                entity_id=entity_id,
                is_unlocked=True
            )
            
            # Добавляем в систему
            if entity_id not in self.entity_skills:
                self.entity_skills[entity_id] = {}
            
            self.entity_skills[entity_id][skill_id] = entity_skill
            
            # Обновляем статистику
            self.system_stats['total_skills_learned'] += 1
            
            # Вызываем callback
            if self.on_skill_learned:
                self.on_skill_learned(entity_id, skill_id, skill_node)
            
            logger.info(f"Сущность {entity_id} изучила навык {skill_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка изучения навыка {skill_id} сущностью {entity_id}: {e}")
            return False
    
    def use_skill(self, entity_id: str, skill_id: str, target_id: str = None,
                  base_attributes: AttributeSet = None,
                  attribute_modifiers: List[AttributeModifier] = None,
                  stat_modifiers: List[StatModifier] = None) -> bool:
        """Использование навыка с интеграцией атрибутов"""
        try:
            # Проверяем наличие навыка
            if entity_id not in self.entity_skills or skill_id not in self.entity_skills[entity_id]:
                logger.warning(f"Сущность {entity_id} не знает навык {skill_id}")
                return False
            
            entity_skill = self.entity_skills[entity_id][skill_id]
            skill_node = self._find_skill_node(skill_id)
            
            if not skill_node:
                logger.warning(f"Навык {skill_id} не найден")
                return False
            
            # Проверяем возможность использования
            if not self._can_use_skill(entity_skill, skill_node):
                logger.warning(f"Навык {skill_id} не может быть использован")
                return False
            
            # Рассчитываем силу навыка на основе атрибутов
            skill_power = self._calculate_skill_power(skill_node, entity_skill.level, 
                                                    base_attributes, attribute_modifiers, stat_modifiers)
            
            # Применяем эффекты навыка
            self._apply_skill_effects(skill_node, entity_id, target_id, skill_power)
            
            # Применяем модификаторы навыка
            if self.system_settings['enable_skill_modifiers']:
                self._apply_skill_modifiers(skill_node, entity_id, entity_skill)
            
            # Обновляем статистику навыка
            entity_skill.last_used = time.time()
            entity_skill.total_uses += 1
            
            # Обновляем статистику системы
            self.system_stats['total_skill_uses'] += 1
            
            # Вызываем callback
            if self.on_skill_used:
                self.on_skill_used(entity_id, skill_id, target_id, skill_power)
            
            logger.info(f"Сущность {entity_id} использовала навык {skill_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка использования навыка {skill_id} сущностью {entity_id}: {e}")
            return False
    
    def _find_skill_node(self, skill_id: str) -> Optional[SkillNode]:
        """Поиск узла навыка"""
        for tree in self.skill_trees.values():
            if hasattr(tree, 'skills') and skill_id in tree.skills:
                return tree.skills[skill_id]
        return None
    
    def _check_attribute_requirements(self, skill_node: SkillNode, base_attributes: AttributeSet,
                                    attribute_modifiers: List[AttributeModifier] = None,
                                    stat_modifiers: List[StatModifier] = None) -> bool:
        """Проверка требований атрибутов"""
        try:
            if not base_attributes:
                return True
            
            # Получаем финальные атрибуты с модификаторами
            if self.attribute_system:
                calculated_stats = self.attribute_system.calculate_stats_for_entity(
                    entity_id="temp_check",
                    base_attributes=base_attributes,
                    attribute_modifiers=attribute_modifiers,
                    stat_modifiers=stat_modifiers
                )
                
                # Проверяем требования атрибутов
                for attr_name, min_value in skill_node.attribute_requirements.items():
                    attr_value = getattr(base_attributes, attr_name, 0)
                    if attr_value < min_value:
                        return False
                
                # Проверяем требования характеристик
                for stat_name, min_value in skill_node.stat_requirements.items():
                    stat_value = calculated_stats.get(stat_name, 0)
                    if stat_value < min_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки требований атрибутов: {e}")
            return False
    
    def _check_skill_requirements(self, entity_id: str, skill_node: SkillNode) -> bool:
        """Проверка требований навыков"""
        try:
            for requirement in skill_node.requirements:
                if requirement.requirement_type == "skill":
                    if not self._has_skill_at_level(entity_id, requirement.requirement_id, requirement.value):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки требований навыков: {e}")
            return False
    
    def _has_skill_at_level(self, entity_id: str, skill_id: str, min_level: int) -> bool:
        """Проверка наличия навыка на определенном уровне"""
        if entity_id in self.entity_skills and skill_id in self.entity_skills[entity_id]:
            return self.entity_skills[entity_id][skill_id].level >= min_level
        return False
    
    def _can_use_skill(self, entity_skill: EntitySkill, skill_node: SkillNode) -> bool:
        """Проверка возможности использования навыка"""
        current_time = time.time()
        
        # Проверяем кулдаун
        if current_time - entity_skill.last_used < skill_node.cooldown:
            return False
        
        # Проверяем разблокировку
        if not entity_skill.is_unlocked:
            return False
        
        return True
    
    def _calculate_skill_power(self, skill_node: SkillNode, skill_level: int,
                              base_attributes: AttributeSet = None,
                              attribute_modifiers: List[AttributeModifier] = None,
                              stat_modifiers: List[StatModifier] = None) -> float:
        """Расчет силы навыка на основе атрибутов"""
        try:
            if not self.system_settings['auto_calculate_skill_power_from_attributes']:
                return 1.0
            
            base_power = 1.0
            
            if base_attributes and self.attribute_system:
                # Получаем характеристики из системы атрибутов
                calculated_stats = self.attribute_system.calculate_stats_for_entity(
                    entity_id="temp_calc",
                    base_attributes=base_attributes,
                    attribute_modifiers=attribute_modifiers,
                    stat_modifiers=stat_modifiers
                )
                
                # Применяем масштабирование атрибутов
                for attr_name, scaling in skill_node.attribute_scaling.items():
                    attr_value = getattr(base_attributes, attr_name, 0)
                    base_power += attr_value * scaling
                
                # Применяем масштабирование характеристик
                for stat_name, scaling in skill_node.stat_scaling.items():
                    stat_value = calculated_stats.get(stat_name, 0)
                    base_power += stat_value * scaling
            
            # Множитель уровня навыка
            level_multiplier = 1.0 + (skill_level - 1) * 0.2
            
            return base_power * level_multiplier
            
        except Exception as e:
            logger.error(f"Ошибка расчета силы навыка: {e}")
            return 1.0
    
    def _apply_skill_effects(self, skill_node: SkillNode, caster_id: str, target_id: str, skill_power: float):
        """Применение эффектов навыка"""
        try:
            for effect in skill_node.effects:
                # Здесь должна быть логика применения эффектов
                # Например, нанесение урона, лечение, баффы и т.д.
                logger.debug(f"Применен эффект {effect.effect_type} от навыка {skill_node.skill_id}")
                
        except Exception as e:
            logger.error(f"Ошибка применения эффектов навыка: {e}")
    
    def _apply_skill_modifiers(self, skill_node: SkillNode, entity_id: str, entity_skill: EntitySkill):
        """Применение модификаторов навыка"""
        try:
            current_time = time.time()
            
            # Применяем модификаторы атрибутов
            for modifier in skill_node.modifiers:
                if modifier.modifier_type == "attribute":
                    attr_modifier = AttributeModifier(
                        modifier_id=f"skill_{skill_node.skill_id}_{modifier.target}",
                        attribute=BaseAttribute(modifier.target),
                        value=modifier.value,
                        source=f"skill_{skill_node.skill_id}",
                        duration=modifier.duration,
                        start_time=current_time,
                        is_percentage=modifier.is_percentage
                    )
                    entity_skill.active_modifiers.append(attr_modifier)
                
                elif modifier.modifier_type == "stat":
                    stat_modifier = StatModifier(
                        modifier_id=f"skill_{skill_node.skill_id}_{modifier.target}",
                        stat=DerivedStat(modifier.target),
                        value=modifier.value,
                        source=f"skill_{skill_node.skill_id}",
                        duration=modifier.duration,
                        start_time=current_time,
                        is_percentage=modifier.is_percentage
                    )
                    entity_skill.active_stat_modifiers.append(stat_modifier)
            
            logger.debug(f"Применены модификаторы навыка {skill_node.skill_id}")
            
        except Exception as e:
            logger.error(f"Ошибка применения модификаторов навыка: {e}")
    
    def get_skill_modifiers_for_entity(self, entity_id: str) -> Tuple[List[AttributeModifier], List[StatModifier]]:
        """Получение всех активных модификаторов навыков для сущности"""
        try:
            if entity_id not in self.entity_skills:
                return [], []
            
            all_attribute_modifiers = []
            all_stat_modifiers = []
            
            for skill in self.entity_skills[entity_id].values():
                all_attribute_modifiers.extend(skill.active_modifiers)
                all_stat_modifiers.extend(skill.active_stat_modifiers)
            
            return all_attribute_modifiers, all_stat_modifiers
            
        except Exception as e:
            logger.error(f"Ошибка получения модификаторов навыков для сущности {entity_id}: {e}")
            return [], []
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'skill_trees_count': len(self.skill_trees),
            'entities_with_skills': len(self.entity_skills),
            'total_skills_learned': self.system_stats['total_skills_learned'],
            'total_skill_uses': self.system_stats['total_skill_uses'],
            'active_modifiers': self.system_stats['active_modifiers'],
            'combo_completions': self.system_stats['combo_completions'],
            'update_time': self.system_stats['update_time']
        }
    
    def reset_stats(self):
        """Сброс статистики"""
        self.system_stats = {
            'total_skills_learned': 0,
            'total_skill_uses': 0,
            'total_skill_levels': 0,
            'active_modifiers': 0,
            'combo_completions': 0,
            'update_time': 0.0
        }
