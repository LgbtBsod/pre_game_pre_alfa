#!/usr/bin/env python3
"""
Effect System - Система специальных эффектов предметов (версия 2.0)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
import random
import time
from enum import Enum

logger = logging.getLogger(__name__)

class EffectCategory(Enum):
    INSTANT = "instant"
    DOT = "dot"
    BUFF = "buff"
    DEBUFF = "debuff"
    HEAL = "heal"

class DamageType(Enum):
    PHYSICAL = "physical"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    TRUE = "true"

class TargetType(Enum):
    SELF = "self"
    ENEMY = "enemy"
    ALLY = "ally"
    AREA = "area"

class TriggerType(Enum):
    ON_HIT = "on_hit"
    ON_CRIT = "on_crit"
    ON_SPELL_CAST = "on_spell_cast"
    ON_BEING_HIT = "on_being_hit"
    ON_BLOCK = "on_block"
    ON_DODGE = "on_dodge"
    ON_KILL = "on_kill"
    ON_LOW_HEALTH = "on_low_health"
    ON_ELEMENT_DAMAGE = "on_element_damage"

@dataclass
class EffectVisuals:
    """Визуальные и звуковые эффекты для применения эффекта"""
    particle_effect: Optional[str] = None
    sound_effect: Optional[str] = None
    screen_shake: Optional[float] = None
    color_overlay: Optional[Tuple[int, int, int, float]] = None
    animation: Optional[str] = None
    duration: float = 1.0

@dataclass
class EffectBalance:
    """Параметры балансировки эффекта"""
    base_power: float = 1.0
    scaling_factor: float = 1.0
    pvp_modifier: float = 1.0
    pve_modifier: float = 1.0
    level_scaling: float = 0.0

@dataclass
class Effect:
    """Базовый класс для игровых эффектов"""
    name: str
    category: EffectCategory
    value: Union[float, Dict[str, float]]
    damage_types: List[DamageType] = field(default_factory=list)
    duration: float = 0
    period: float = 1.0
    scaling: Dict[str, float] = field(default_factory=dict)
    target_type: TargetType = TargetType.SELF
    area: Optional[Dict[str, Any]] = None
    projectile_speed: float = 0
    ignore_resistance: float = 0
    visuals: Optional[EffectVisuals] = None
    balance: EffectBalance = field(default_factory=EffectBalance)
    tags: List[str] = field(default_factory=list)
    
    def can_apply(self, source: Any, target: Any) -> bool:
        """Проверяет, можно ли применить эффект"""
        return True  # Базовая проверка
    
    def apply_instant(self, source: Any, target: Any):
        """Применение мгновенного эффекта"""
        self._play_visuals(source, target)
        
    def apply_over_time(self, source: Any, target: Any):
        """Применение эффекта с течением времени"""
        # Логика применения DOT эффекта
        pass
    
    def _play_visuals(self, source: Any, target: Any):
        """Воспроизведение визуальных эффектов"""
        if self.visuals:
            # Интеграция с системой визуализации
            logger.debug(f"Воспроизведение визуальных эффектов для {self.name}")
    
    def get_modified_value(self, context: Dict[str, Any]) -> float:
        """Рассчитывает модифицированное значение эффекта"""
        modified_value = self.value * self.balance.base_power * self.balance.scaling_factor
        
        if context.get("is_pvp"):
            modified_value *= self.balance.pvp_modifier
        else:
            modified_value *= self.balance.pve_modifier
        
        if "source_level" in context and self.balance.level_scaling > 0:
            level_factor = 1.0 + (context["source_level"] - 1) * self.balance.level_scaling
            modified_value *= level_factor
        
        return modified_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация эффекта"""
        return {
            "name": self.name,
            "category": self.category.value,
            "value": self.value,
            "damage_types": [dt.value for dt in self.damage_types],
            "duration": self.duration,
            "period": self.period,
            "scaling": self.scaling,
            "target_type": self.target_type.value,
            "area": self.area,
            "projectile_speed": self.projectile_speed,
            "ignore_resistance": self.ignore_resistance,
            "visuals": self.visuals.__dict__ if self.visuals else None,
            "balance": self.balance.__dict__,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Effect':
        """Десериализация эффекта"""
        visuals_data = data.pop("visuals", None)
        balance_data = data.pop("balance", None)
        
        effect = cls(**data)
        if visuals_data:
            effect.visuals = EffectVisuals(**visuals_data)
        if balance_data:
            effect.balance = EffectBalance(**balance_data)
        
        return effect

class EffectCondition:
    """Базовый класс для условий срабатывания эффектов"""
    
    def check(self, source: Any, target: Any, context: Dict[str, Any]) -> bool:
        """Проверяет выполнение условия"""
        raise NotImplementedError

class HealthCondition(EffectCondition):
    """Условие, основанное на уровне здоровья"""
    
    def __init__(self, health_percent: float, comparison: str = "less"):
        self.health_percent = health_percent
        self.comparison = comparison
    
    def check(self, source: Any, target: Any, context: Dict[str, Any]) -> bool:
        if not hasattr(target, 'health') or not hasattr(target, 'max_health'):
            return False
        
        current_percent = target.health / target.max_health
        
        if self.comparison == "less":
            return current_percent < self.health_percent
        elif self.comparison == "greater":
            return current_percent > self.health_percent
        
        return False

class ElementCondition(EffectCondition):
    """Условие, основанное на типе урона"""
    
    def __init__(self, element: DamageType):
        self.element = element
    
    def check(self, source: Any, target: Any, context: Dict[str, Any]) -> bool:
        return context.get("damage_type") == self.element

@dataclass
class SpecialEffect:
    """Структура для специальных эффектов предметов"""
    chance: float
    effect: Effect
    trigger_condition: TriggerType
    cooldown: float = 0
    max_procs: int = 0
    last_proc_time: float = 0
    proc_count: int = 0
    conditions: List[EffectCondition] = field(default_factory=list)
    combination_effects: List['SpecialEffect'] = field(default_factory=list)
    track_stats: bool = False
    achievement_id: Optional[str] = None
    
    def can_trigger(self, source: Any, target: Any, trigger_type: TriggerType, context: Dict[str, Any]) -> bool:
        """Проверяет, может ли эффект сработать в текущих условиях"""
        if self.trigger_condition != trigger_type:
            return False
            
        if random.random() > self.chance:
            return False
            
        current_time = time.time()
        if self.cooldown > 0 and (current_time - self.last_proc_time) < self.cooldown:
            return False
            
        if self.max_procs > 0 and self.proc_count >= self.max_procs:
            return False
            
        if not self.effect.can_apply(source, target):
            return False
            
        for condition in self.conditions:
            if not condition.check(source, target, context):
                return False
                
        return True
    
    def trigger(self, source: Any, target: Any, context: Dict[str, Any] = None):
        """Активирует эффект"""
        if context is None:
            context = {}
            
        # Применяем основной эффект
        if self.effect.duration == 0:
            self.effect.apply_instant(source, target)
        else:
            if hasattr(target, 'add_effect'):
                target.add_effect(self.effect, source)
        
        # Применяем комбинационные эффекты
        for combo_effect in self.combination_effects:
            if combo_effect.can_trigger(source, target, self.trigger_condition, context):
                combo_effect.trigger(source, target, context)
        
        # Обновляем данные о срабатывании
        self.last_proc_time = time.time()
        self.proc_count += 1
        
        # Записываем статистику
        if self.track_stats:
            self._record_statistics(source, target)
    
    def _record_statistics(self, source: Any, target: Any):
        """Записывает статистику по эффекту"""
        if hasattr(source, 'effect_statistics'):
            source.effect_statistics.record_trigger(self.effect.name)
    
    def reset(self):
        """Сбрасывает счетчик срабатываний"""
        self.proc_count = 0
        self.last_proc_time = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация эффекта"""
        return {
            "chance": self.chance,
            "effect": self.effect.to_dict(),
            "trigger_condition": self.trigger_condition.value,
            "cooldown": self.cooldown,
            "max_procs": self.max_procs,
            "last_proc_time": self.last_proc_time,
            "proc_count": self.proc_count,
            "conditions": [cond.__dict__ for cond in self.conditions],
            "combination_effects": [eff.to_dict() for eff in self.combination_effects],
            "track_stats": self.track_stats,
            "achievement_id": self.achievement_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpecialEffect':
        """Десериализация эффекта"""
        effect = Effect.from_dict(data.pop("effect"))
        
        conditions_data = data.pop("conditions", [])
        conditions = []
        for cond_data in conditions_data:
            if "health_percent" in cond_data:
                conditions.append(HealthCondition(**cond_data))
            elif "element" in cond_data:
                conditions.append(ElementCondition(DamageType(cond_data["element"])))
        
        combination_effects_data = data.pop("combination_effects", [])
        combination_effects = [cls.from_dict(eff_data) for eff_data in combination_effects_data]
        
        return cls(
            effect=effect,
            trigger_condition=TriggerType(data["trigger_condition"]),
            conditions=conditions,
            combination_effects=combination_effects,
            **data
        )

class OptimizedTriggerSystem:
    """Оптимизированная система триггеров с индексацией эффектов"""
    
    def __init__(self):
        self.triggers = {trigger_type.value: [] for trigger_type in TriggerType}
        self.effect_index = {trigger_type.value: [] for trigger_type in TriggerType}
        self.combination_system = CombinationSystem()
    
    def register_trigger(self, trigger_type: TriggerType, callback: Callable):
        """Регистрирует callback для определенного триггера"""
        self.triggers[trigger_type.value].append(callback)
    
    def register_item_effects(self, item):
        """Регистрирует все эффекты предмета в индексе"""
        for effect in item.special_effects:
            trigger_type = effect.trigger_condition.value
            self.effect_index[trigger_type].append((item, effect))
    
    def trigger(self, trigger_type: TriggerType, source: Any, target: Any = None, context: Dict[str, Any] = None):
        """Активирует все зарегистрированные триггеры указанного типа"""
        if context is None:
            context = {}
        
        # Обработка оптимизированных эффектов
        for item, effect in self.effect_index[trigger_type.value]:
            if effect.can_trigger(source, target, trigger_type, context):
                effect.trigger(source, target, context)
        
        # Обработка комбинаций
        for item, effect in self.effect_index[trigger_type.value]:
            self.combination_system.apply_effect(effect, source, target)
        
        # Обработка общих триггеров
        for callback in self.triggers[trigger_type.value]:
            callback(source, target, **context)

class CombinationSystem:
    """Система для обработки комбинаций эффектов"""
    
    def __init__(self):
        self.active_effects = {}  # Активные эффекты на целях
        self.combinations = {}  # Определенные комбинации эффектов
    
    def register_combination(self, tags: List[str], result_effect: SpecialEffect):
        """Регистрирует комбинацию тегов и результирующий эффект"""
        key = tuple(sorted(tags))
        self.combinations[key] = result_effect
    
    def apply_effect(self, effect: SpecialEffect, source: Any, target: Any):
        """Применяет эффект и проверяет комбинации"""
        # Обновляем активные эффекты цели
        if target not in self.active_effects:
            self.active_effects[target] = {}
        
        for tag in effect.effect.tags:
            if tag not in self.active_effects[target]:
                self.active_effects[target][tag] = []
            self.active_effects[target][tag].append(effect)
        
        # Проверяем комбинации
        self._check_combinations(source, target)
    
    def _check_combinations(self, source: Any, target: Any):
        """Проверяет наличие комбинаций эффектов на цели"""
        if target not in self.active_effects:
            return
        
        active_tags = list(self.active_effects[target].keys())
        
        for combo_tags, result_effect in self.combinations.items():
            if all(tag in active_tags for tag in combo_tags):
                result_effect.trigger(source, target)

class EffectStatistics:
    """Статистика по эффектам"""
    
    def __init__(self):
        self.effect_triggers = {}  # Количество срабатываний эффектов
        self.effect_damage = {}  # Урон от эффектов
        self.effect_healing = {}  # Исцеление от эффектов
    
    def record_trigger(self, effect_name: str):
        """Регистрирует срабатывание эффекта"""
        if effect_name not in self.effect_triggers:
            self.effect_triggers[effect_name] = 0
        self.effect_triggers[effect_name] += 1
    
    def record_damage(self, effect_name: str, damage: float):
        """Регистрирует урон от эффекта"""
        if effect_name not in self.effect_damage:
            self.effect_damage[effect_name] = 0
        self.effect_damage[effect_name] += damage
    
    def record_healing(self, effect_name: str, healing: float):
        """Регистрирует исцеление от эффекта"""
        if effect_name not in self.effect_healing:
            self.effect_healing[effect_name] = 0
        self.effect_healing[effect_name] += healing
