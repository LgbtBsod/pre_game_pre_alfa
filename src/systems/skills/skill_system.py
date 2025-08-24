#!/usr/bin/env python3
"""
Skill System - Система скиллов с поддержкой AI обучения
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
import time
import random

from ..effects.effect_system import Effect, SpecialEffect, TriggerType, DamageType, EffectCategory
from ..genome.genome_system import GeneType, genome_manager
from ..ai.ai_entity import MemoryType

logger = logging.getLogger(__name__)

class SkillType(Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    ULTIMATE = "ultimate"
    COMBAT = "combat"
    UTILITY = "utility"

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
        self.effects: List[Effect] = []
        self.special_effects: List[SpecialEffect] = []
        
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
        """Проверяет, может ли сущность изучить скилл с учетом генома"""
        # Проверяем базовые требования
        if not self._check_basic_requirements(entity):
            return False
        
        # Проверяем геном
        if hasattr(entity, 'get') and entity.get('id'):
            genome = genome_manager.get_genome(entity['id'])
            if genome:
                # Получаем требования скилла в формате для генома
                skill_requirements = {
                    'strength': self.requirements.strength,
                    'agility': self.requirements.agility,
                    'intelligence': self.requirements.intelligence,
                    'vitality': self.requirements.vitality
                }
                
                # Проверяем, может ли геном удовлетворить требования
                if not genome.can_learn_skill(skill_requirements):
                    return False
                
                # Дополнительная проверка на эволюционный потенциал
                evolution_potential = genome.get_evolution_potential()
                if evolution_potential < 0.3:  # Минимальный эволюционный потенциал
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
        for effect in self.effects:
            if effect.duration == 0:
                effect.apply_instant(caster, target)
            else:
                if hasattr(target, 'add_effect'):
                    target.add_effect(effect, caster)
        
        # Применяем специальные эффекты
        for special_effect in self.special_effects:
            if special_effect.can_trigger(caster, target, TriggerType.ON_SPELL_CAST, context):
                special_effect.trigger(caster, target, context)
    
    def _calculate_distance(self, caster: Any, target: Any) -> float:
        """Рассчитывает дистанцию между кастером и целью"""
        import math
        
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
            "effects": [effect.to_dict() for effect in self.effects],
            "special_effects": [effect.to_dict() for effect in self.special_effects],
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
        
        # Восстанавливаем эффекты
        for effect_data in data.get("effects", []):
            effect = Effect.from_dict(effect_data)
            skill.effects.append(effect)
        
        for effect_data in data.get("special_effects", []):
            effect = SpecialEffect.from_dict(effect_data)
            skill.special_effects.append(effect)
        
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
    
    def __init__(self, name: str, description: str, damage: int, damage_type: DamageType,
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
        """Изучает скилл с учетом генома"""
        if skill_name not in self.skills:
            logger.warning(f"Скилл {skill_name} не найден в дереве скиллов")
            return False
        
        skill = self.skills[skill_name]
        
        # Проверяем базовые требования
        if not self._check_requirements(skill, character):
            return False
        
        # Проверяем геном
        if not skill.can_learn(character):
            logger.warning(f"Геном не позволяет изучить скилл {skill_name}")
            return False
        
        # Проверяем наличие очков скиллов
        if self.skill_points < skill.requirements.skill_points:
            logger.warning(f"Недостаточно очков скиллов для изучения {skill_name}")
            return False
        
        # Изучаем скилл
        self.learned_skills.append(skill_name)
        self.skill_points -= skill.requirements.skill_points
        
        # Записываем в память AI
        if hasattr(character, 'ai_entity'):
            character['ai_entity'].add_memory(
                MemoryType.SKILL_USAGE,
                {'skill_name': skill_name, 'action': 'learn'},
                f"learn_skill_{skill_name}",
                {'skill_type': skill.skill_type.value},
                True
            )
        
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

# SkillFactory удален - теперь используется ContentGenerator для создания скиллов
# Пример использования:
# from ..content.content_generator import ContentGenerator
# content_gen = ContentGenerator()
# fireball_skill = content_gen.generate_unique_skill(session_id, level, "combat")
