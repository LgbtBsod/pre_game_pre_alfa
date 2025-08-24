#!/usr/bin/env python3
"""
Система навыков - управление навыками и способностями сущностей с поддержкой AI обучения
"""

import logging
import time
import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)

class SkillType(Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    ULTIMATE = "ultimate"
    COMBAT = "combat"
    UTILITY = "utility"
    REACTIVE = "reactive"

class SkillTarget(Enum):
    SELF = "self"
    ENEMY = "enemy"
    ALLY = "ally"
    AREA = "area"
    PROJECTILE = "projectile"

@dataclass
class SkillRequirements:
    """Требования для изучения скилла"""
    level: int = 1
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    vitality: int = 0
    skill_points: int = 1
    prerequisites: List[str] = field(default_factory=list)

@dataclass
class SkillCooldown:
    """Система перезарядки скиллов"""
    base_cooldown: float
    current_cooldown: float = 0.0
    cooldown_reduction: float = 0.0
    
    def is_ready(self) -> bool:
        """Проверяет, готов ли скилл к использованию"""
        return self.current_cooldown <= 0
    
    def start_cooldown(self):
        """Запускает перезарядку"""
        self.current_cooldown = self.base_cooldown * (1 - self.cooldown_reduction)
    
    def update(self, delta_time: float):
        """Обновляет перезарядку"""
        if self.current_cooldown > 0:
            self.current_cooldown -= delta_time

class Skill:
    """Базовый класс для всех скиллов"""
    
    def __init__(self, name: str, description: str, skill_type: SkillType, 
                 target_type: SkillTarget, cooldown: float = 0.0):
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.target_type = target_type
        self.cooldown_system = SkillCooldown(cooldown)
        self.requirements = SkillRequirements()
        self.effects: List[Any] = []  # Упрощено для совместимости
        self.special_effects: List[Any] = []  # Упрощено для совместимости
        
        # AI обучение
        self.ai_learning_data = {
            "usage_count": 0,
            "success_count": 0,
            "effectiveness_score": 0.0,
            "last_used": 0.0,
            "preferred_targets": {},
            "avoided_targets": {},
            "combinations": []
        }
        
        # Визуальные эффекты
        self.cast_time: float = 0.0
        self.range: float = 1.0
        self.mana_cost: int = 0
        self.health_cost: int = 0
        
    def can_use(self, caster: Any, target: Any = None) -> bool:
        """Проверяет, можно ли использовать скилл"""
        if not self.cooldown_system.is_ready():
            return False
        
        # Проверка ресурсов
        if hasattr(caster, 'mana') and caster.mana < self.mana_cost:
            return False
        if hasattr(caster, 'health') and caster.health <= self.health_cost:
            return False
        
        # Проверка дистанции
        if target and self.range > 0:
            distance = self._calculate_distance(caster, target)
            if distance > self.range:
                return False
        
        return True
    
    def use(self, caster: Any, target: Any = None, context: Dict[str, Any] = None):
        """Использует скилл"""
        if not self.can_use(caster, target):
            return False
        
        if context is None:
            context = {}
        
        # Расходуем ресурсы
        if hasattr(caster, 'mana'):
            caster.mana -= self.mana_cost
        if hasattr(caster, 'health'):
            caster.health -= self.health_cost
        
        # Запускаем перезарядку
        self.cooldown_system.start_cooldown()
        
        # Применяем эффекты
        self._apply_effects(caster, target, context)
        
        # Обновляем статистику AI
        self._update_ai_learning(caster, target, context)
        
        logger.info(f"Скилл {self.name} использован {caster.get('id', 'unknown')}")
        return True
    
    def can_learn(self, entity: Any) -> bool:
        """Проверяет, может ли сущность изучить скилл"""
        # Проверяем базовые требования
        if not self._check_basic_requirements(entity):
            return False
        
        return True
    
    def _check_basic_requirements(self, entity: Any) -> bool:
        """Проверяет базовые требования для изучения скилла"""
        if not hasattr(entity, 'get'):
            return False
        
        # Проверка уровня
        if entity.get('level', 0) < self.requirements.level:
            return False
        
        # Проверка очков скиллов
        if hasattr(entity, 'skill_tree') and entity.skill_tree:
            if entity.skill_tree.skill_points < self.requirements.skill_points:
                return False
        
        # Проверка предварительных требований
        if self.requirements.prerequisites:
            learned_skills = entity.skill_tree.learned_skills if hasattr(entity, 'skill_tree') else []
            for prereq in self.requirements.prerequisites:
                if prereq not in learned_skills:
                    return False
        
        return True
    
    def _apply_effects(self, caster: Any, target: Any, context: Dict[str, Any]):
        """Применяет эффекты скилла"""
        # Упрощенная логика применения эффектов
        for effect in self.effects:
            if hasattr(effect, 'apply'):
                effect.apply(caster, target)
        
        # Применяем специальные эффекты
        for special_effect in self.special_effects:
            if hasattr(special_effect, 'trigger'):
                special_effect.trigger(caster, target, context)
    
    def _calculate_distance(self, caster: Any, target: Any) -> float:
        """Рассчитывает дистанцию между кастером и целью"""
        caster_x = caster.get('x', 0)
        caster_y = caster.get('y', 0)
        target_x = target.get('x', 0)
        target_y = target.get('y', 0)
        
        dx = target_x - caster_x
        dy = target_y - caster_y
        
        return math.sqrt(dx*dx + dy*dy)
    
    def _update_ai_learning(self, caster: Any, target: Any, context: Dict[str, Any]):
        """Обновляет данные обучения AI"""
        self.ai_learning_data["usage_count"] += 1
        self.ai_learning_data["last_used"] = time.time()
        
        # Анализируем эффективность
        if target and hasattr(target, 'health'):
            initial_health = target.get('initial_health', target.health)
            damage_dealt = initial_health - target.health
            if damage_dealt > 0:
                self.ai_learning_data["success_count"] += 1
                self.ai_learning_data["effectiveness_score"] = (
                    self.ai_learning_data["success_count"] / self.ai_learning_data["usage_count"]
                )
        
        # Записываем предпочтения по целям
        if target:
            target_id = target.get('id', 'unknown')
            if target_id not in self.ai_learning_data["preferred_targets"]:
                self.ai_learning_data["preferred_targets"][target_id] = 0
            self.ai_learning_data["preferred_targets"][target_id] += 1
    
    def get_ai_effectiveness(self) -> float:
        """Возвращает оценку эффективности скилла для AI"""
        return self.ai_learning_data["effectiveness_score"]
    
    def get_ai_preference_score(self, target: Any) -> float:
        """Возвращает оценку предпочтения цели для AI"""
        target_id = target.get('id', 'unknown')
        return self.ai_learning_data["preferred_targets"].get(target_id, 0)
    
    def update(self, delta_time: float):
        """Обновляет скилл"""
        self.cooldown_system.update(delta_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация скилла"""
        return {
            "name": self.name,
            "description": self.description,
            "skill_type": self.skill_type.value,
            "target_type": self.target_type.value,
            "cooldown": self.cooldown_system.base_cooldown,
            "current_cooldown": self.cooldown_system.current_cooldown,
            "requirements": self.requirements.__dict__,
            "effects": [effect.to_dict() if hasattr(effect, 'to_dict') else str(effect) for effect in self.effects],
            "special_effects": [effect.to_dict() if hasattr(effect, 'to_dict') else str(effect) for effect in self.special_effects],
            "ai_learning_data": self.ai_learning_data,
            "cast_time": self.cast_time,
            "range": self.range,
            "mana_cost": self.mana_cost,
            "health_cost": self.health_cost
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skill':
        """Десериализация скилла"""
        skill = cls(
            name=data["name"],
            description=data["description"],
            skill_type=SkillType(data["skill_type"]),
            target_type=SkillTarget(data["target_type"]),
            cooldown=data["cooldown"]
        )
        
        # Восстанавливаем остальные свойства
        skill.cooldown_system.current_cooldown = data.get("current_cooldown", 0)
        skill.requirements = SkillRequirements(**data.get("requirements", {}))
        skill.ai_learning_data = data.get("ai_learning_data", {})
        skill.cast_time = data.get("cast_time", 0.0)
        skill.range = data.get("range", 1.0)
        skill.mana_cost = data.get("mana_cost", 0)
        skill.health_cost = data.get("health_cost", 0)
        
        return skill

class CombatSkill(Skill):
    """Боевой скилл"""
    
    def __init__(self, name: str, description: str, damage: int, damage_type: str,
                 target_type: SkillTarget = SkillTarget.ENEMY, cooldown: float = 0.0):
        super().__init__(name, description, SkillType.COMBAT, target_type, cooldown)
        self.damage = damage
        self.damage_type = damage_type
        self.critical_chance = 0.05
        self.critical_multiplier = 1.5
        
    def calculate_damage(self, caster: Any, target: Any) -> float:
        """Рассчитывает урон скилла"""
        base_damage = self.damage
        
        # Модификаторы от характеристик кастера
        if hasattr(caster, 'stats'):
            strength_bonus = caster.stats.get("strength", 0) * 0.1
            intelligence_bonus = caster.stats.get("intelligence", 0) * 0.15
            base_damage += strength_bonus + intelligence_bonus
        
        # Критический удар
        if random.random() < self.critical_chance:
            base_damage *= self.critical_multiplier
        
        return base_damage
    
    def use(self, caster: Any, target: Any = None, context: Dict[str, Any] = None):
        """Использует боевой скилл"""
        if not super().can_use(caster, target):
            return False
        
        if context is None:
            context = {}
        
        # Рассчитываем урон
        damage = self.calculate_damage(caster, target)
        
        # Наносим урон
        if target and hasattr(target, 'health'):
            target.health = max(0, target.health - damage)
            context["damage_dealt"] = damage
            context["damage_type"] = self.damage_type
        
        # Вызываем родительский метод
        return super().use(caster, target, context)

class UtilitySkill(Skill):
    """Утилитарный скилл"""
    
    def __init__(self, name: str, description: str, effect_type: str,
                 target_type: SkillTarget = SkillTarget.SELF, cooldown: float = 0.0):
        super().__init__(name, description, SkillType.UTILITY, target_type, cooldown)
        self.effect_type = effect_type  # heal, buff, debuff, teleport, etc.
        
    def use(self, caster: Any, target: Any = None, context: Dict[str, Any] = None):
        """Использует утилитарный скилл"""
        if not super().can_use(caster, target):
            return False
        
        if context is None:
            context = {}
        
        # Применяем эффект в зависимости от типа
        if self.effect_type == "heal":
            self._apply_heal(caster, target, context)
        elif self.effect_type == "buff":
            self._apply_buff(caster, target, context)
        elif self.effect_type == "debuff":
            self._apply_debuff(caster, target, context)
        
        # Вызываем родительский метод
        return super().use(caster, target, context)
    
    def _apply_heal(self, caster: Any, target: Any, context: Dict[str, Any]):
        """Применяет исцеление"""
        if target and hasattr(target, 'health') and hasattr(target, 'max_health'):
            heal_amount = 20  # Базовая величина исцеления
            target.health = min(target.max_health, target.health + heal_amount)
            context["heal_amount"] = heal_amount
    
    def _apply_buff(self, caster: Any, target: Any, context: Dict[str, Any]):
        """Применяет усиление"""
        # Логика применения баффа
        pass
    
    def _apply_debuff(self, caster: Any, target: Any, context: Dict[str, Any]):
        """Применяет ослабление"""
        # Логика применения дебаффа
        pass

class SkillTree:
    """Дерево скиллов для персонажа"""
    
    def __init__(self, character_id: str):
        self.character_id = character_id
        self.skills: Dict[str, Skill] = {}
        self.learned_skills: List[str] = []
        self.skill_points: int = 0
        self.max_skill_points: int = 0
        
        # AI данные для дерева скиллов
        self.ai_skill_preferences = {}
        self.ai_skill_combinations = []
        
    def add_skill(self, skill: Skill):
        """Добавляет скилл в дерево"""
        self.skills[skill.name] = skill
    
    def learn_skill(self, skill_name: str, character: Any) -> bool:
        """Изучает скилл"""
        if skill_name not in self.skills:
            logger.warning(f"Скилл {skill_name} не найден в дереве скиллов")
            return False
        
        skill = self.skills[skill_name]
        
        # Проверяем базовые требования
        if not self._check_requirements(skill, character):
            return False
        
        # Проверяем геном
        if not skill.can_learn(character):
            logger.warning(f"Не удается изучить скилл {skill_name}")
            return False
        
        # Проверяем наличие очков скиллов
        if self.skill_points < skill.requirements.skill_points:
            logger.warning(f"Недостаточно очков скиллов для изучения {skill_name}")
            return False
        
        # Изучаем скилл
        self.learned_skills.append(skill_name)
        self.skill_points -= skill.requirements.skill_points
        
        logger.info(f"Персонаж {self.character_id} изучил скилл {skill_name}")
        return True
    
    def _check_requirements(self, skill: Skill, character: Any) -> bool:
        """Проверяет требования для изучения скилла"""
        req = skill.requirements
        
        # Проверка уровня
        if hasattr(character, 'level') and character.level < req.level:
            return False
        
        # Проверка характеристик
        if hasattr(character, 'stats'):
            if character.stats.get("strength", 0) < req.strength:
                return False
            if character.stats.get("agility", 0) < req.agility:
                return False
            if character.stats.get("intelligence", 0) < req.intelligence:
                return False
            if character.stats.get("vitality", 0) < req.vitality:
                return False
        
        # Проверка предварительных требований
        for prereq in req.prerequisites:
            if prereq not in self.learned_skills:
                return False
        
        return True
    
    def get_available_skills(self, character: Any) -> List[Skill]:
        """Возвращает список доступных для изучения скиллов"""
        available = []
        
        for skill_name, skill in self.skills.items():
            if skill_name not in self.learned_skills:
                if self._check_requirements(skill, character):
                    available.append(skill)
        
        return available
    
    def get_ai_recommended_skill(self, character: Any, context: Dict[str, Any]) -> Optional[Skill]:
        """Возвращает рекомендуемый AI скилл для использования"""
        available_skills = [self.skills[name] for name in self.learned_skills]
        
        if not available_skills:
            return None
        
        # Сортируем по эффективности AI
        available_skills.sort(key=lambda s: s.get_ai_effectiveness(), reverse=True)
        
        # Фильтруем готовые к использованию
        ready_skills = [s for s in available_skills if s.can_use(character)]
        
        if ready_skills:
            return ready_skills[0]
        
        return None
    
    def update(self, delta_time: float):
        """Обновляет дерево скиллов"""
        for skill in self.skills.values():
            skill.update(delta_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация дерева скиллов"""
        return {
            "character_id": self.character_id,
            "skills": {name: skill.to_dict() for name, skill in self.skills.items()},
            "learned_skills": self.learned_skills,
            "skill_points": self.skill_points,
            "max_skill_points": self.max_skill_points,
            "ai_skill_preferences": self.ai_skill_preferences,
            "ai_skill_combinations": self.ai_skill_combinations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillTree':
        """Десериализация дерева скиллов"""
        skill_tree = cls(data["character_id"])
        
        # Восстанавливаем скиллы
        for name, skill_data in data.get("skills", {}).items():
            skill = Skill.from_dict(skill_data)
            skill_tree.add_skill(skill)
        
        # Восстанавливаем остальные свойства
        skill_tree.learned_skills = data.get("learned_skills", [])
        skill_tree.skill_points = data.get("skill_points", 0)
        skill_tree.max_skill_points = data.get("max_skill_points", 0)
        skill_tree.ai_skill_preferences = data.get("ai_skill_preferences", {})
        skill_tree.ai_skill_combinations = data.get("ai_skill_combinations", [])
        
        return skill_tree

class SkillSystem(ISystem):
    """Система управления навыками для всех сущностей"""
    
    def __init__(self):
        self._system_name = "skill"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Деревья скиллов для сущностей
        self.skill_trees: Dict[str, SkillTree] = {}
        
        # Доступные скиллы
        self.available_skills: Dict[str, Skill] = {}
        
        # Шаблоны скиллов
        self.skill_templates: Dict[str, Dict[str, Any]] = {}
        
        # Статистика системы
        self.system_stats = {
            'entities_count': 0,
            'skills_learned': 0,
            'skills_used': 0,
            'update_time': 0.0
        }
        
        logger.info("Система навыков инициализирована")
    
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
        """Инициализация системы навыков"""
        try:
            logger.info("Инициализация системы навыков...")
            
            # Инициализируем шаблоны скиллов
            self._initialize_skill_templates()
            
            # Создаем базовые скиллы
            self._create_base_skills()
            
            self._system_state = SystemState.READY
            logger.info("Система навыков успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы навыков: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы навыков"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем все деревья скиллов
            self._update_all_skill_trees(delta_time)
            
            # Обновляем статистику системы
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы навыков: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы навыков"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система навыков приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы навыков: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы навыков"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система навыков возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы навыков: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы навыков"""
        try:
            logger.info("Очистка системы навыков...")
            
            # Очищаем все данные
            self.skill_trees.clear()
            self.available_skills.clear()
            self.skill_templates.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'entities_count': 0,
                'skills_learned': 0,
                'skills_used': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система навыков очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы навыков: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'entities_count': len(self.skill_trees),
            'available_skills_count': len(self.available_skills),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "skill_learned":
                return self._handle_skill_learned(event_data)
            elif event_type == "skill_used":
                return self._handle_skill_used(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def create_skill_tree(self, entity_id: str) -> SkillTree:
        """Создает дерево скиллов для сущности"""
        if entity_id not in self.skill_trees:
            skill_tree = SkillTree(entity_id)
            self.skill_trees[entity_id] = skill_tree
            self.system_stats['entities_count'] = len(self.skill_trees)
            
            # Добавляем базовые скиллы
            for skill_name, skill in self.available_skills.items():
                skill_tree.add_skill(skill)
        
        return self.skill_trees[entity_id]
    
    def get_skill_tree(self, entity_id: str) -> Optional[SkillTree]:
        """Получает дерево скиллов для сущности"""
        return self.skill_trees.get(entity_id)
    
    def learn_skill(self, entity_id: str, skill_name: str, character: Any) -> bool:
        """Изучает скилл для сущности"""
        try:
            skill_tree = self.get_skill_tree(entity_id)
            if not skill_tree:
                skill_tree = self.create_skill_tree(entity_id)
            
            if skill_tree.learn_skill(skill_name, character):
                self.system_stats['skills_learned'] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка изучения скилла {skill_name} для {entity_id}: {e}")
            return False
    
    def use_skill(self, entity_id: str, skill_name: str, caster: Any, target: Any = None, context: Dict[str, Any] = None) -> bool:
        """Использует скилл"""
        try:
            skill_tree = self.get_skill_tree(entity_id)
            if not skill_tree or skill_name not in skill_tree.learned_skills:
                return False
            
            skill = skill_tree.skills[skill_name]
            if skill.use(caster, target, context):
                self.system_stats['skills_used'] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка использования скилла {skill_name} для {entity_id}: {e}")
            return False
    
    def _initialize_skill_templates(self) -> None:
        """Инициализация шаблонов скиллов"""
        try:
            # Шаблоны для разных типов скиллов
            self.skill_templates = {
                'basic_attack': {
                    'name': 'Базовая атака',
                    'description': 'Простая физическая атака',
                    'skill_type': SkillType.COMBAT,
                    'target_type': SkillTarget.ENEMY,
                    'cooldown': 1.0,
                    'damage': 10,
                    'damage_type': 'physical'
                },
                'fireball': {
                    'name': 'Огненный шар',
                    'description': 'Магическая атака огнем',
                    'skill_type': SkillType.COMBAT,
                    'target_type': SkillTarget.ENEMY,
                    'cooldown': 5.0,
                    'damage': 25,
                    'damage_type': 'fire'
                },
                'heal': {
                    'name': 'Исцеление',
                    'description': 'Восстанавливает здоровье',
                    'skill_type': SkillType.UTILITY,
                    'target_type': SkillTarget.ALLY,
                    'cooldown': 8.0,
                    'effect_type': 'heal'
                }
            }
            
            logger.debug("Шаблоны скиллов инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать шаблоны скиллов: {e}")
    
    def _create_base_skills(self) -> None:
        """Создание базовых скиллов"""
        try:
            # Создаем базовые скиллы из шаблонов
            for skill_id, template in self.skill_templates.items():
                if template['skill_type'] == SkillType.COMBAT:
                    skill = CombatSkill(
                        name=template['name'],
                        description=template['description'],
                        damage=template['damage'],
                        damage_type=template['damage_type'],
                        target_type=template['target_type'],
                        cooldown=template['cooldown']
                    )
                elif template['skill_type'] == SkillType.UTILITY:
                    skill = UtilitySkill(
                        name=template['name'],
                        description=template['description'],
                        effect_type=template['effect_type'],
                        target_type=template['target_type'],
                        cooldown=template['cooldown']
                    )
                else:
                    skill = Skill(
                        name=template['name'],
                        description=template['description'],
                        skill_type=template['skill_type'],
                        target_type=template['target_type'],
                        cooldown=template['cooldown']
                    )
                
                self.available_skills[skill_id] = skill
            
            logger.info(f"Создано {len(self.available_skills)} базовых скиллов")
            
        except Exception as e:
            logger.warning(f"Не удалось создать базовые скиллы: {e}")
    
    def _update_all_skill_trees(self, delta_time: float) -> None:
        """Обновление всех деревьев скиллов"""
        try:
            for skill_tree in self.skill_trees.values():
                skill_tree.update(delta_time)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления деревьев скиллов: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                # Создаем дерево скиллов для новой сущности
                self.create_skill_tree(entity_id)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_skill_learned(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изучения скилла"""
        try:
            entity_id = event_data.get('entity_id')
            skill_name = event_data.get('skill_name')
            character = event_data.get('character')
            
            if entity_id and skill_name and character:
                return self.learn_skill(entity_id, skill_name, character)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события изучения скилла: {e}")
            return False
    
    def _handle_skill_used(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события использования скилла"""
        try:
            entity_id = event_data.get('entity_id')
            skill_name = event_data.get('skill_name')
            caster = event_data.get('caster')
            target = event_data.get('target')
            context = event_data.get('context', {})
            
            if entity_id and skill_name and caster:
                return self.use_skill(entity_id, skill_name, caster, target, context)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события использования скилла: {e}")
            return False
