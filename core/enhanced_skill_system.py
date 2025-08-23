#!/usr/bin/env python3
"""
Расширенная система навыков и способностей.
Вдохновлено Hades, Risk of Rain 2, Enter the Gungeon.
Включает комбо-систему, эволюцию навыков и адаптивное обучение.
"""

import random
import math
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

from .generational_memory_system import GenerationalMemorySystem, MemoryType
from .emotional_ai_influence import EmotionalAIInfluenceSystem

logger = logging.getLogger(__name__)


class SkillType(Enum):
    """Типы навыков"""
    COMBAT = "combat"           # Боевые навыки
    UTILITY = "utility"         # Утилитарные навыки
    PASSIVE = "passive"         # Пассивные навыки
    ACTIVE = "active"           # Активные навыки
    ULTIMATE = "ultimate"       # Ультимативные навыки
    EVOLUTIONARY = "evolutionary"  # Эволюционные навыки
    CORRUPTION = "corruption"   # Коррупционные навыки
    TEMPORAL = "temporal"       # Временные навыки


class SkillElement(Enum):
    """Элементы навыков"""
    PHYSICAL = "physical"       # Физический
    FIRE = "fire"               # Огонь
    ICE = "ice"                 # Лёд
    LIGHTNING = "lightning"     # Молния
    EARTH = "earth"             # Земля
    WATER = "water"             # Вода
    WIND = "wind"               # Ветер
    LIGHT = "light"             # Свет
    DARK = "dark"               # Тьма
    VOID = "void"               # Пустота
    EVOLUTION = "evolution"     # Эволюция
    CORRUPTION = "corruption"
    TRUE = "true"
    FALSE = "false"


class SkillTarget(Enum):
    """Цели навыков"""
    SELF = "self"               # Себя
    SINGLE_ENEMY = "single_enemy"  # Один враг
    MULTIPLE_ENEMIES = "multiple_enemies"  # Несколько врагов
    ALL_ENEMIES = "all_enemies"    # Все враги
    ALLY = "ally"               # Союзник
    ALL_ALLIES = "all_allies"   # Все союзники
    AREA = "area"               # Область
    PROJECTILE = "projectile"   # Снаряд
    SUMMON = "summon"           # Призыв
    ENVIRONMENT = "environment" # Окружение


class SkillRequirement(Enum):
    """Требования к навыкам"""
    LEVEL = "level"             # Уровень
    STAT = "stat"               # Характеристика
    ITEM = "item"               # Предмет
    SKILL = "skill"             # Навык
    EMOTION = "emotion"         # Эмоция
    MEMORY = "memory"           # Память
    EVOLUTION = "evolution"     # Эволюция
    CORRUPTION = "corruption"   # Коррупция


@dataclass
class SkillEffect:
    """Эффект навыка"""
    effect_type: str
    value: float
    duration: float
    stack_limit: int
    decay_rate: float
    elemental_bonus: float
    evolution_bonus: float
    
    def get_effective_value(self, evolution_level: float = 0.0, 
                           corruption_level: float = 0.0) -> float:
        """Получение эффективного значения эффекта"""
        effective_value = self.value
        
        # Бонус от эволюции
        if self.evolution_bonus > 0:
            effective_value += self.evolution_bonus * evolution_level
        
        # Бонус от коррупции
        if self.corruption_level > 0:
            effective_value += self.corruption_level * corruption_level
        
        return effective_value


@dataclass
class SkillCombo:
    """Комбо навыков"""
    id: str
    name: str
    skills: List[str]
    combo_multiplier: float
    execution_time: float
    difficulty: float
    evolution_requirement: float
    memory_boost: float
    
    def can_execute(self, available_skills: List[str], 
                    evolution_level: float) -> bool:
        """Проверка возможности выполнения комбо"""
        if evolution_level < self.evolution_requirement:
            return False
        
        return all(skill in available_skills for skill in self.skills)


@dataclass
class Skill:
    """Навык"""
    id: str
    name: str
    skill_type: SkillType
    element: SkillElement
    target: SkillTarget
    base_damage: float
    base_cost: float
    cooldown: float
    range: float
    effects: List[SkillEffect]
    requirements: Dict[str, Any]
    evolution_stages: List[Dict[str, Any]]
    combo_potential: List[str]
    memory_cost: float
    emotional_triggers: List[str]
    
    def get_current_damage(self, evolution_level: float = 0.0, 
                          corruption_level: float = 0.0) -> float:
        """Получение текущего урона навыка"""
        damage = self.base_damage
        
        # Бонус от эволюции
        for stage in self.evolution_stages:
            if evolution_level >= stage.get("level", 0):
                damage *= stage.get("damage_multiplier", 1.0)
        
        # Бонус от коррупции
        if corruption_level > 0:
            damage *= (1.0 + corruption_level * 0.5)
        
        return damage
    
    def get_current_cost(self, evolution_level: float = 0.0) -> float:
        """Получение текущей стоимости навыка"""
        cost = self.base_cost
        
        # Снижение стоимости от эволюции
        for stage in self.evolution_stages:
            if evolution_level >= stage.get("level", 0):
                cost *= stage.get("cost_reduction", 1.0)
        
        return cost


class SkillManager:
    """Менеджер навыков"""
    
    def __init__(self, memory_system: GenerationalMemorySystem,
                 emotional_system: EmotionalAIInfluenceSystem):
        self.memory_system = memory_system
        self.emotional_system = emotional_system
        
        # Доступные навыки
        self.available_skills: Dict[str, Skill] = {}
        
        # Изученные навыки
        self.learned_skills: Dict[str, Skill] = {}
        
        # Комбо навыков
        self.skill_combos: Dict[str, SkillCombo] = {}
        
        # История использования навыков
        self.skill_usage_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Система эволюции навыков
        self.skill_evolution_system = SkillEvolutionSystem()
        
        # Инициализация базовых навыков
        self._init_base_skills()
        
        logger.info("Менеджер навыков инициализирован")
    
    def learn_skill(self, skill_id: str, entity_id: str, 
                    context: Dict[str, Any]) -> bool:
        """Изучение навыка"""
        if skill_id not in self.available_skills:
            logger.warning(f"Навык {skill_id} недоступен для изучения")
            return False
        
        skill = self.available_skills[skill_id]
        
        # Проверка требований
        if not self._check_skill_requirements(skill, entity_id, context):
            logger.warning(f"Требования для навыка {skill_id} не выполнены")
            return False
        
        # Изучение навыка
        self.learned_skills[skill_id] = skill
        
        # Запись в память
        self._record_skill_learning(skill, entity_id, context)
        
        # Обновление комбо
        self._update_available_combos(entity_id)
        
        logger.info(f"Навык {skill_id} изучен для {entity_id}")
        return True
    
    def use_skill(self, skill_id: str, entity_id: str, 
                  target: Optional[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Использование навыка"""
        if skill_id not in self.learned_skills:
            return {"success": False, "reason": "Skill not learned"}
        
        skill = self.learned_skills[skill_id]
        
        # Проверка возможности использования
        can_use, reason = self._can_use_skill(skill, entity_id, context)
        if not can_use:
            return {"success": False, "reason": reason}
        
        # Использование навыка
        result = self._execute_skill(skill, entity_id, target, context)
        
        # Запись использования
        self._record_skill_usage(skill, entity_id, target, context, result)
        
        # Обновление эволюции
        self.skill_evolution_system.update_skill_evolution(skill_id, entity_id, result)
        
        return result
    
    def execute_combo(self, combo_id: str, entity_id: str, 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение комбо"""
        if combo_id not in self.skill_combos:
            return {"success": False, "reason": "Combo not found"}
        
        combo = self.skill_combos[combo_id]
        
        # Проверка возможности выполнения
        if not combo.can_execute(list(self.learned_skills.keys()), 
                                context.get("evolution_level", 0.0)):
            return {"success": False, "reason": "Combo requirements not met"}
        
        # Выполнение комбо
        combo_result = self._execute_combo(combo, entity_id, context)
        
        # Запись комбо
        self._record_combo_execution(combo, entity_id, context, combo_result)
        
        return combo_result
    
    def get_available_skills(self, entity_id: str, 
                            context: Dict[str, Any]) -> List[Skill]:
        """Получение доступных навыков"""
        available = []
        
        for skill in self.learned_skills.values():
            if self._can_use_skill(skill, entity_id, context)[0]:
                available.append(skill)
        
        return available
    
    def get_skill_suggestions(self, entity_id: str, 
                             context: Dict[str, Any]) -> List[Skill]:
        """Получение предложений по навыкам"""
        suggestions = []
        
        # Анализ истории использования
        usage_patterns = self._analyze_skill_usage(entity_id)
        
        # Предложения на основе паттернов
        for skill_id, pattern in usage_patterns.items():
            if pattern["success_rate"] > 0.7:  # Успешные навыки
                if skill_id in self.learned_skills:
                    skill = self.learned_skills[skill_id]
                    if self._can_use_skill(skill, entity_id, context)[0]:
                        suggestions.append(skill)
        
        # Сортировка по приоритету
        suggestions.sort(key=lambda s: self._calculate_skill_priority(s, context))
        
        return suggestions[:5]  # Топ-5 предложений
    
    def _init_base_skills(self):
        """Инициализация базовых навыков"""
        base_skills = [
            Skill(
                id="basic_attack",
                name="Basic Attack",
                skill_type=SkillType.COMBAT,
                element=SkillElement.PHYSICAL,
                target=SkillTarget.SINGLE_ENEMY,
                base_damage=25.0,
                base_cost=5.0,
                cooldown=0.5,
                range=50.0,
                effects=[
                    SkillEffect(
                        effect_type="damage",
                        value=25.0,
                        duration=0.0,
                        stack_limit=1,
                        decay_rate=0.0,
                        elemental_bonus=0.0,
                        evolution_bonus=0.1
                    )
                ],
                requirements={"level": 1},
                evolution_stages=[
                    {"level": 5, "damage_multiplier": 1.2, "cost_reduction": 0.9},
                    {"level": 15, "damage_multiplier": 1.5, "cost_reduction": 0.8}
                ],
                combo_potential=["basic_combo", "aggressive_combo"],
                memory_cost=1.0,
                emotional_triggers=["rage", "excitement"]
            ),
            Skill(
                id="fire_ball",
                name="Fire Ball",
                skill_type=SkillType.COMBAT,
                element=SkillElement.FIRE,
                target=SkillTarget.PROJECTILE,
                base_damage=40.0,
                base_cost=15.0,
                cooldown=2.0,
                range=200.0,
                effects=[
                    SkillEffect(
                        effect_type="damage",
                        value=40.0,
                        duration=0.0,
                        stack_limit=1,
                        decay_rate=0.0,
                        elemental_bonus=0.2,
                        evolution_bonus=0.15
                    ),
                    SkillEffect(
                        effect_type="burning",
                        value=10.0,
                        duration=3.0,
                        stack_limit=3,
                        decay_rate=0.3,
                        elemental_bonus=0.1,
                        evolution_bonus=0.05
                    )
                ],
                requirements={"level": 5, "element": "fire"},
                evolution_stages=[
                    {"level": 10, "damage_multiplier": 1.3, "cost_reduction": 0.9},
                    {"level": 25, "damage_multiplier": 1.6, "cost_reduction": 0.8}
                ],
                combo_potential=["elemental_combo", "fire_combo"],
                memory_cost=2.0,
                emotional_triggers=["excitement", "curiosity"]
            ),
            Skill(
                id="heal",
                name="Heal",
                skill_type=SkillType.UTILITY,
                element=SkillElement.LIGHT,
                target=SkillTarget.SELF,
                base_damage=-30.0,  # Отрицательный урон = лечение
                base_cost=20.0,
                cooldown=5.0,
                range=0.0,
                effects=[
                    SkillEffect(
                        effect_type="healing",
                        value=30.0,
                        duration=0.0,
                        stack_limit=1,
                        decay_rate=0.0,
                        elemental_bonus=0.0,
                        evolution_bonus=0.1
                    )
                ],
                requirements={"level": 3},
                evolution_stages=[
                    {"level": 8, "damage_multiplier": 1.2, "cost_reduction": 0.9},
                    {"level": 20, "damage_multiplier": 1.4, "cost_reduction": 0.8}
                ],
                combo_potential=["support_combo", "defensive_combo"],
                memory_cost=1.5,
                emotional_triggers=["fear", "calmness"]
            )
        ]
        
        for skill in base_skills:
            self.available_skills[skill.id] = skill
        
        # Инициализация комбо
        self._init_skill_combos()
    
    def _init_skill_combos(self):
        """Инициализация комбо навыков"""
        base_combos = [
            SkillCombo(
                id="basic_combo",
                name="Basic Combo",
                skills=["basic_attack", "basic_attack"],
                combo_multiplier=1.5,
                execution_time=1.0,
                difficulty=0.3,
                evolution_requirement=0.0,
                memory_boost=0.2
            ),
            SkillCombo(
                id="elemental_combo",
                name="Elemental Combo",
                skills=["fire_ball", "basic_attack"],
                combo_multiplier=2.0,
                execution_time=1.5,
                difficulty=0.6,
                evolution_requirement=5.0,
                memory_boost=0.4
            ),
            SkillCombo(
                id="aggressive_combo",
                name="Aggressive Combo",
                skills=["basic_attack", "basic_attack", "basic_attack"],
                combo_multiplier=2.5,
                execution_time=2.0,
                difficulty=0.8,
                evolution_requirement=10.0,
                memory_boost=0.6
            )
        ]
        
        for combo in base_combos:
            self.skill_combos[combo.id] = combo
    
    def _check_skill_requirements(self, skill: Skill, entity_id: str, 
                                 context: Dict[str, Any]) -> bool:
        """Проверка требований к навыку"""
        for req_type, req_value in skill.requirements.items():
            if req_type == "level":
                if context.get("level", 0) < req_value:
                    return False
            elif req_type == "element":
                if context.get("element", "") != req_value:
                    return False
            elif req_type == "stat":
                if context.get(req_value, 0) < skill.requirements.get(f"{req_value}_min", 0):
                    return False
        
        return True
    
    def _can_use_skill(self, skill: Skill, entity_id: str, 
                       context: Dict[str, Any]) -> Tuple[bool, str]:
        """Проверка возможности использования навыка"""
        # Проверка энергии
        if context.get("energy", 0) < skill.get_current_cost(context.get("evolution_level", 0.0)):
            return False, "Insufficient energy"
        
        # Проверка кулдауна
        last_used = self.skill_usage_history.get(entity_id, {}).get(skill.id, [])
        if last_used:
            time_since_last = time.time() - last_used[-1]["timestamp"]
            if time_since_last < skill.cooldown:
                return False, "Skill on cooldown"
        
        # Проверка памяти
        if context.get("memory", 0) < skill.memory_cost:
            return False, "Insufficient memory"
        
        return True, "OK"
    
    def _execute_skill(self, skill: Skill, entity_id: str, 
                       target: Optional[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение навыка"""
        # Расчёт урона
        damage = skill.get_current_damage(
            context.get("evolution_level", 0.0),
            context.get("corruption_level", 0.0)
        )
        
        # Применение эффектов
        applied_effects = []
        for effect in skill.effects:
            effective_value = effect.get_effective_value(
                context.get("evolution_level", 0.0),
                context.get("corruption_level", 0.0)
            )
            
            applied_effects.append({
                "type": effect.effect_type,
                "value": effective_value,
                "duration": effect.duration,
                "stack_limit": effect.stack_limit
            })
        
        # Расчёт стоимости
        cost = skill.get_current_cost(context.get("evolution_level", 0.0))
        
        result = {
            "success": True,
            "skill_id": skill.id,
            "damage": damage,
            "effects": applied_effects,
            "cost": cost,
            "target": target,
            "timestamp": time.time()
        }
        
        return result
    
    def _execute_combo(self, combo: SkillCombo, entity_id: str, 
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение комбо"""
        # Выполнение навыков в комбо
        combo_results = []
        total_damage = 0.0
        total_cost = 0.0
        
        for skill_id in combo.skills:
            if skill_id in self.learned_skills:
                skill = self.learned_skills[skill_id]
                skill_result = self._execute_skill(skill, entity_id, None, context)
                combo_results.append(skill_result)
                total_damage += skill_result["damage"]
                total_cost += skill_result["cost"]
        
        # Применение множителя комбо
        final_damage = total_damage * combo.combo_multiplier
        
        # Бонус к памяти
        memory_boost = combo.memory_boost
        
        result = {
            "success": True,
            "combo_id": combo.id,
            "total_damage": final_damage,
            "total_cost": total_cost,
            "combo_multiplier": combo.combo_multiplier,
            "memory_boost": memory_boost,
            "skill_results": combo_results,
            "timestamp": time.time()
        }
        
        return result
    
    def _record_skill_usage(self, skill: Skill, entity_id: str, 
                           target: Optional[str], context: Dict[str, Any], 
                           result: Dict[str, Any]):
        """Запись использования навыка"""
        if entity_id not in self.skill_usage_history:
            self.skill_usage_history[entity_id] = {}
        
        if skill.id not in self.skill_usage_history[entity_id]:
            self.skill_usage_history[entity_id][skill.id] = []
        
        usage_record = {
            "skill_id": skill.id,
            "target": target,
            "context": context,
            "result": result,
            "timestamp": time.time()
        }
        
        self.skill_usage_history[entity_id][skill.id].append(usage_record)
        
        # Ограничение истории
        if len(self.skill_usage_history[entity_id][skill.id]) > 100:
            self.skill_usage_history[entity_id][skill.id] = \
                self.skill_usage_history[entity_id][skill.id][-50:]
    
    def _record_combo_execution(self, combo: SkillCombo, entity_id: str, 
                               context: Dict[str, Any], result: Dict[str, Any]):
        """Запись выполнения комбо"""
        # Запись каждого навыка в комбо
        for skill_result in result["skill_results"]:
            skill_id = skill_result["skill_id"]
            if skill_id in self.learned_skills:
                skill = self.learned_skills[skill_id]
                self._record_skill_usage(skill, entity_id, None, context, skill_result)
    
    def _record_skill_learning(self, skill: Skill, entity_id: str, 
                              context: Dict[str, Any]):
        """Запись изучения навыка"""
        memory_content = {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "skill_type": skill.skill_type.value,
            "element": skill.element.value,
            "requirements": skill.requirements,
            "context": context,
            "timestamp": time.time()
        }
        
        self.memory_system.add_memory(
            memory_type=MemoryType.ITEM_USAGE,
            content=memory_content,
            intensity=0.5,
            emotional_impact=0.3
        )
    
    def _update_available_combos(self, entity_id: str):
        """Обновление доступных комбо"""
        # Логика обновления комбо на основе изученных навыков
        pass
    
    def _analyze_skill_usage(self, entity_id: str) -> Dict[str, Dict[str, Any]]:
        """Анализ использования навыков"""
        if entity_id not in self.skill_usage_history:
            return {}
        
        analysis = {}
        
        for skill_id, usage_records in self.skill_usage_history[entity_id].items():
            if not usage_records:
                continue
            
            total_uses = len(usage_records)
            successful_uses = sum(1 for record in usage_records if record["result"]["success"])
            success_rate = successful_uses / total_uses if total_uses > 0 else 0.0
            
            analysis[skill_id] = {
                "total_uses": total_uses,
                "successful_uses": successful_uses,
                "success_rate": success_rate,
                "last_used": usage_records[-1]["timestamp"] if usage_records else 0
            }
        
        return analysis
    
    def _calculate_skill_priority(self, skill: Skill, context: Dict[str, Any]) -> float:
        """Расчёт приоритета навыка"""
        priority = 0.0
        
        # Приоритет по типу
        type_priorities = {
            SkillType.COMBAT: 1.0,
            SkillType.UTILITY: 0.8,
            SkillType.PASSIVE: 0.6,
            SkillType.ACTIVE: 0.9,
            SkillType.ULTIMATE: 1.2
        }
        priority += type_priorities.get(skill.skill_type, 0.5)
        
        # Приоритет по элементу
        if context.get("element", "") == skill.element.value:
            priority += 0.3
        
        # Приоритет по эволюции
        evolution_level = context.get("evolution_level", 0.0)
        for stage in skill.evolution_stages:
            if evolution_level >= stage.get("level", 0):
                priority += 0.2
        
        return priority


class SkillLearningAI:
    """ИИ для обучения навыкам"""
    
    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager
        self.learning_patterns: Dict[str, List[str]] = {}
        self.adaptation_strategies: Dict[str, Dict[str, Any]] = {}
    
    def suggest_skill_improvements(self, entity_id: str, 
                                 context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Предложение улучшений навыков"""
        suggestions = []
        
        # Анализ текущих навыков
        current_skills = self.skill_manager.get_available_skills(entity_id, context)
        
        for skill in current_skills:
            # Анализ эффективности
            effectiveness = self._analyze_skill_effectiveness(skill, entity_id)
            
            if effectiveness < 0.6:  # Низкая эффективность
                improvement = self._suggest_skill_improvement(skill, effectiveness, context)
                if improvement:
                    suggestions.append(improvement)
        
        return suggestions
    
    def _analyze_skill_effectiveness(self, skill: Skill, entity_id: str) -> float:
        """Анализ эффективности навыка"""
        # Получение истории использования
        usage_history = self.skill_manager.skill_usage_history.get(entity_id, {}).get(skill.id, [])
        
        if not usage_history:
            return 0.5  # Нейтральная эффективность для новых навыков
        
        # Расчёт эффективности на основе успешности и частоты использования
        success_rate = sum(1 for record in usage_history if record["result"]["success"]) / len(usage_history)
        
        # Учёт частоты использования
        recent_usage = [record for record in usage_history if time.time() - record["timestamp"] < 3600]  # Последний час
        usage_frequency = len(recent_usage) / 10.0  # Нормализация к 10 использованиям в час
        
        effectiveness = (success_rate * 0.7) + (min(usage_frequency, 1.0) * 0.3)
        
        return effectiveness
    
    def _suggest_skill_improvement(self, skill: Skill, effectiveness: float, 
                                  context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Предложение улучшения навыка"""
        if effectiveness > 0.8:  # Высокая эффективность
            return None
        
        suggestions = []
        
        # Предложения по улучшению
        if effectiveness < 0.4:
            suggestions.append("Consider replacing with more effective skill")
        elif effectiveness < 0.6:
            suggestions.append("Practice timing and positioning")
            suggestions.append("Combine with other skills for combos")
        
        # Предложения по эволюции
        evolution_level = context.get("evolution_level", 0.0)
        for stage in skill.evolution_stages:
            if evolution_level < stage.get("level", 0):
                suggestions.append(f"Evolve to level {stage['level']} for better performance")
        
        if suggestions:
            return {
                "skill_id": skill.id,
                "skill_name": skill.name,
                "current_effectiveness": effectiveness,
                "suggestions": suggestions,
                "priority": "high" if effectiveness < 0.4 else "medium"
            }
        
        return None


class SkillEvolutionSystem:
    """Система эволюции навыков"""
    
    def __init__(self):
        self.evolution_tracks: Dict[str, List[Dict[str, Any]]] = {}
        self.mutation_chances: Dict[str, float] = {}
    
    def update_skill_evolution(self, skill_id: str, entity_id: str, 
                              usage_result: Dict[str, Any]):
        """Обновление эволюции навыка"""
        if skill_id not in self.evolution_tracks:
            self.evolution_tracks[skill_id] = []
        
        # Анализ результата использования
        evolution_data = {
            "entity_id": entity_id,
            "usage_result": usage_result,
            "timestamp": time.time(),
            "evolution_factor": self._calculate_evolution_factor(usage_result)
        }
        
        self.evolution_tracks[skill_id].append(evolution_data)
        
        # Проверка возможности эволюции
        if self._should_evolve_skill(skill_id, entity_id):
            self._trigger_skill_evolution(skill_id, entity_id)
    
    def _calculate_evolution_factor(self, usage_result: Dict[str, Any]) -> float:
        """Расчёт фактора эволюции"""
        factor = 0.1  # Базовый фактор
        
        # Бонус за успешное использование
        if usage_result.get("success", False):
            factor += 0.2
        
        # Бонус за высокий урон
        damage = usage_result.get("damage", 0)
        if damage > 50:
            factor += 0.1
        if damage > 100:
            factor += 0.2
        
        # Бонус за комбо
        if "combo_multiplier" in usage_result:
            factor += 0.3
        
        return min(1.0, factor)
    
    def _should_evolve_skill(self, skill_id: str, entity_id: str) -> bool:
        """Проверка необходимости эволюции навыка"""
        if skill_id not in self.evolution_tracks:
            return False
        
        # Анализ истории эволюции
        evolution_history = self.evolution_tracks[skill_id]
        recent_evolution = [e for e in evolution_history if e["entity_id"] == entity_id]
        
        if len(recent_evolution) < 10:  # Недостаточно данных
            return False
        
        # Расчёт общего фактора эволюции
        total_factor = sum(e["evolution_factor"] for e in recent_evolution[-10:])
        
        return total_factor > 5.0  # Порог для эволюции
    
    def _trigger_skill_evolution(self, skill_id: str, entity_id: str):
        """Запуск эволюции навыка"""
        logger.info(f"Запуск эволюции навыка {skill_id} для {entity_id}")
        
        # Здесь должна быть логика эволюции навыка
        # Например, увеличение урона, снижение стоимости, новые эффекты
        pass
