#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

class EffectType(Enum):
    """Типы эффектов"""
    BUFF = "buff"               # Положительный эффект
    DEBUFF = "debuff"           # Отрицательный эффект
    DOT = "dot"                 # Урон со временем
    HOT = "hot"                 # Лечение со временем
    SHIELD = "shield"           # Защитный щит
    STUN = "stun"               # Оглушение
    SLOW = "slow"               # Замедление
    HASTE = "haste"             # Ускорение
    INVISIBILITY = "invisibility"  # Невидимость
    POISON = "poison"           # Отравление
    BURN = "burn"               # Горение
    FREEZE = "freeze"           # Заморозка
    CONFUSION = "confusion"     # Смятение
    CHARM = "charm"             # Очарование
    FEAR = "fear"               # Страх
    BERSERK = "berserk"         # Берсерк

class EffectStackType(Enum):
    """Типы наложения эффектов"""
    NONE = "none"               # Не накладывается
    STACK = "stack"             # Накладывается (увеличивает силу)
    REFRESH = "refresh"         # Обновляет время действия
    REPLACE = "replace"         # Заменяет предыдущий

@dataclass
class Effect:
    """Эффект"""
    effect_id: str
    name: str
    description: str
    effect_type: EffectType
    value: float
    duration: float
    tick_interval: float = 1.0  # Интервал срабатывания для DOT/HOT
    stack_type: EffectStackType = EffectStackType.NONE
    max_stacks: int = 1
    source: str = "unknown"     # Источник эффекта
    start_time: float = field(default_factory=time.time)
    last_tick: float = field(default_factory=time.time)
    stacks: int = 1
    
    def is_expired(self) -> bool:
        """Проверка истечения эффекта"""
        return time.time() - self.start_time >= self.duration
    
    def can_tick(self) -> bool:
        """Проверка возможности срабатывания"""
        return time.time() - self.last_tick >= self.tick_interval
    
    def tick(self):
        """Срабатывание эффекта"""
        self.last_tick = time.time()
    
    def get_remaining_time(self) -> float:
        """Получение оставшегося времени"""
        elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)
    
    def get_effective_value(self) -> float:
        """Получение эффективного значения с учетом стаков"""
        return self.value * self.stacks

class EffectSystem:
    """Система эффектов"""
    
    def __init__(self):
        self.entity_effects: Dict[str, List[Effect]] = {}  # Эффекты сущностей
        self.effect_templates: Dict[str, Effect] = {}      # Шаблоны эффектов
        
        # Инициализация шаблонов эффектов
        self._initialize_effect_templates()
    
    def _initialize_effect_templates(self):
        """Инициализация шаблонов эффектов"""
        # Положительные эффекты
        strength_boost = Effect(
            effect_id="strength_boost",
            name="Strength Boost",
            description="Увеличивает силу",
            effect_type=EffectType.BUFF,
            value=5.0,
            duration=30.0,
            stack_type=EffectStackType.STACK,
            max_stacks=5
        )
        self.effect_templates["strength_boost"] = strength_boost
        
        speed_boost = Effect(
            effect_id="speed_boost",
            name="Speed Boost",
            description="Увеличивает скорость движения",
            effect_type=EffectType.BUFF,
            value=2.0,
            duration=20.0,
            stack_type=EffectStackType.REFRESH
        )
        self.effect_templates["speed_boost"] = speed_boost
        
        regeneration = Effect(
            effect_id="regeneration",
            name="Regeneration",
            description="Восстанавливает здоровье со временем",
            effect_type=EffectType.HOT,
            value=5.0,
            duration=15.0,
            tick_interval=2.0,
            stack_type=EffectStackType.REFRESH
        )
        self.effect_templates["regeneration"] = regeneration
        
        shield = Effect(
            effect_id="shield",
            name="Shield",
            description="Поглощает урон",
            effect_type=EffectType.SHIELD,
            value=50.0,
            duration=10.0,
            stack_type=EffectStackType.STACK,
            max_stacks=3
        )
        self.effect_templates["shield"] = shield
        
        # Отрицательные эффекты
        weakness = Effect(
            effect_id="weakness",
            name="Weakness",
            description="Уменьшает силу",
            effect_type=EffectType.DEBUFF,
            value=-3.0,
            duration=25.0,
            stack_type=EffectStackType.STACK,
            max_stacks=3
        )
        self.effect_templates["weakness"] = weakness
        
        slow = Effect(
            effect_id="slow",
            name="Slow",
            description="Замедляет движение",
            effect_type=EffectType.SLOW,
            value=-1.5,
            duration=15.0,
            stack_type=EffectStackType.REFRESH
        )
        self.effect_templates["slow"] = slow
        
        poison = Effect(
            effect_id="poison",
            name="Poison",
            description="Наносит урон отравлением",
            effect_type=EffectType.DOT,
            value=3.0,
            duration=20.0,
            tick_interval=2.0,
            stack_type=EffectStackType.STACK,
            max_stacks=5
        )
        self.effect_templates["poison"] = poison
        
        burn = Effect(
            effect_id="burn",
            name="Burn",
            description="Наносит урон огнем",
            effect_type=EffectType.BURN,
            value=4.0,
            duration=12.0,
            tick_interval=1.5,
            stack_type=EffectStackType.STACK,
            max_stacks=3
        )
        self.effect_templates["burn"] = burn
        
        stun = Effect(
            effect_id="stun",
            name="Stun",
            description="Оглушает цель",
            effect_type=EffectType.STUN,
            value=0.0,
            duration=3.0,
            stack_type=EffectStackType.REFRESH
        )
        self.effect_templates["stun"] = stun
        
        freeze = Effect(
            effect_id="freeze",
            name="Freeze",
            description="Замораживает цель",
            effect_type=EffectType.FREEZE,
            value=0.0,
            duration=5.0,
            stack_type=EffectStackType.REFRESH
        )
        self.effect_templates["freeze"] = freeze
    
    def apply_effect(self, entity_id: str, effect_template_id: str, source: str = "unknown",
                    custom_value: Optional[float] = None, custom_duration: Optional[float] = None) -> bool:
        """Применение эффекта к сущности"""
        if effect_template_id not in self.effect_templates:
            return False
        
        template = self.effect_templates[effect_template_id]
        
        # Создаем новый эффект на основе шаблона
        effect = Effect(
            effect_id=template.effect_id,
            name=template.name,
            description=template.description,
            effect_type=template.effect_type,
            value=custom_value if custom_value is not None else template.value,
            duration=custom_duration if custom_duration is not None else template.duration,
            tick_interval=template.tick_interval,
            stack_type=template.stack_type,
            max_stacks=template.max_stacks,
            source=source
        )
        
        if entity_id not in self.entity_effects:
            self.entity_effects[entity_id] = []
        
        # Обрабатываем наложение эффекта
        return self._handle_effect_application(entity_id, effect)
    
    def _handle_effect_application(self, entity_id: str, new_effect: Effect) -> bool:
        """Обработка наложения эффекта"""
        effects = self.entity_effects[entity_id]
        
        # Ищем существующий эффект того же типа
        existing_effect = None
        for effect in effects:
            if effect.effect_id == new_effect.effect_id:
                existing_effect = effect
                break
        
        if existing_effect is None:
            # Новый эффект
            effects.append(new_effect)
            return True
        
        # Обрабатываем наложение в зависимости от типа
        if new_effect.stack_type == EffectStackType.NONE:
            return False  # Нельзя наложить
        
        elif new_effect.stack_type == EffectStackType.REFRESH:
            # Обновляем время действия
            existing_effect.start_time = new_effect.start_time
            existing_effect.last_tick = new_effect.last_tick
            return True
        
        elif new_effect.stack_type == EffectStackType.STACK:
            # Накладываем стаки
            if existing_effect.stacks < existing_effect.max_stacks:
                existing_effect.stacks += 1
                existing_effect.start_time = new_effect.start_time  # Обновляем время
                return True
            else:
                return False  # Максимум стаков достигнут
        
        elif new_effect.stack_type == EffectStackType.REPLACE:
            # Заменяем эффект
            effects.remove(existing_effect)
            effects.append(new_effect)
            return True
        
        return False
    
    def remove_effect(self, entity_id: str, effect_id: str) -> bool:
        """Удаление эффекта"""
        if entity_id not in self.entity_effects:
            return False
        
        effects = self.entity_effects[entity_id]
        for effect in effects:
            if effect.effect_id == effect_id:
                effects.remove(effect)
                return True
        
        return False
    
    def remove_all_effects(self, entity_id: str, effect_type: Optional[EffectType] = None):
        """Удаление всех эффектов или эффектов определенного типа"""
        if entity_id not in self.entity_effects:
            return
        
        effects = self.entity_effects[entity_id]
        if effect_type is None:
            effects.clear()
        else:
            effects[:] = [e for e in effects if e.effect_type != effect_type]
    
    def get_entity_effects(self, entity_id: str) -> List[Effect]:
        """Получение эффектов сущности"""
        return self.entity_effects.get(entity_id, []).copy()
    
    def get_effect_modifiers(self, entity_id: str) -> Dict[str, float]:
        """Получение модификаторов от эффектов"""
        modifiers = {}
        
        if entity_id not in self.entity_effects:
            return modifiers
        
        for effect in self.entity_effects[entity_id]:
            if effect.is_expired():
                continue
            
            # Определяем тип модификатора на основе типа эффекта
            if effect.effect_type == EffectType.BUFF:
                if "strength" in effect.effect_id:
                    modifiers["strength"] = modifiers.get("strength", 0) + effect.get_effective_value()
                elif "speed" in effect.effect_id:
                    modifiers["movement_speed"] = modifiers.get("movement_speed", 0) + effect.get_effective_value()
            
            elif effect.effect_type == EffectType.DEBUFF:
                if "weakness" in effect.effect_id:
                    modifiers["strength"] = modifiers.get("strength", 0) + effect.get_effective_value()
                elif "slow" in effect.effect_id:
                    modifiers["movement_speed"] = modifiers.get("movement_speed", 0) + effect.get_effective_value()
            
            elif effect.effect_type == EffectType.SHIELD:
                modifiers["shield"] = modifiers.get("shield", 0) + effect.get_effective_value()
        
        return modifiers
    
    def update_effects(self, entity_id: str, dt: float) -> Dict[str, Any]:
        """Обновление эффектов и получение результатов"""
        if entity_id not in self.entity_effects:
            return {}
        
        results = {
            "healing": 0.0,
            "damage": 0.0,
            "status_effects": []
        }
        
        effects = self.entity_effects[entity_id]
        expired_effects = []
        
        for effect in effects:
            if effect.is_expired():
                expired_effects.append(effect)
                continue
            
            # Обрабатываем тики для DOT/HOT эффектов
            if effect.can_tick() and effect.effect_type in [EffectType.DOT, EffectType.HOT, EffectType.POISON, EffectType.BURN]:
                effect.tick()
                
                if effect.effect_type in [EffectType.HOT, EffectType.REGENERATION]:
                    results["healing"] += effect.get_effective_value()
                elif effect.effect_type in [EffectType.DOT, EffectType.POISON, EffectType.BURN]:
                    results["damage"] += effect.get_effective_value()
            
            # Проверяем статусные эффекты
            if effect.effect_type in [EffectType.STUN, EffectType.FREEZE, EffectType.CONFUSION, EffectType.CHARM, EffectType.FEAR]:
                results["status_effects"].append(effect.effect_type.value)
        
        # Удаляем истекшие эффекты
        for effect in expired_effects:
            effects.remove(effect)
        
        return results
    
    def has_effect(self, entity_id: str, effect_id: str) -> bool:
        """Проверка наличия эффекта"""
        if entity_id not in self.entity_effects:
            return False
        
        for effect in self.entity_effects[entity_id]:
            if effect.effect_id == effect_id and not effect.is_expired():
                return True
        
        return False
    
    def has_status_effect(self, entity_id: str, effect_type: EffectType) -> bool:
        """Проверка наличия статусного эффекта"""
        if entity_id not in self.entity_effects:
            return False
        
        for effect in self.entity_effects[entity_id]:
            if effect.effect_type == effect_type and not effect.is_expired():
                return True
        
        return False
    
    def get_effect_count(self, entity_id: str, effect_id: str) -> int:
        """Получение количества стаков эффекта"""
        if entity_id not in self.entity_effects:
            return 0
        
        for effect in self.entity_effects[entity_id]:
            if effect.effect_id == effect_id and not effect.is_expired():
                return effect.stacks
        
        return 0
    
    def create_custom_effect(self, effect_id: str, name: str, description: str,
                           effect_type: EffectType, value: float, duration: float,
                           tick_interval: float = 1.0, stack_type: EffectStackType = EffectStackType.NONE,
                           max_stacks: int = 1) -> bool:
        """Создание пользовательского эффекта"""
        if effect_id in self.effect_templates:
            return False  # Эффект уже существует
        
        effect = Effect(
            effect_id=effect_id,
            name=name,
            description=description,
            effect_type=effect_type,
            value=value,
            duration=duration,
            tick_interval=tick_interval,
            stack_type=stack_type,
            max_stacks=max_stacks
        )
        
        self.effect_templates[effect_id] = effect
        return True
    
    def get_effect_template(self, effect_id: str) -> Optional[Effect]:
        """Получение шаблона эффекта"""
        return self.effect_templates.get(effect_id)
    
    def get_all_effect_templates(self) -> Dict[str, Effect]:
        """Получение всех шаблонов эффектов"""
        return self.effect_templates.copy()
    
    def cleanup_expired_effects(self):
        """Очистка всех истекших эффектов"""
        for entity_id in list(self.entity_effects.keys()):
            effects = self.entity_effects[entity_id]
            effects[:] = [e for e in effects if not e.is_expired()]
            
            # Удаляем пустые списки
            if not effects:
                del self.entity_effects[entity_id]
    
    def initialize_entity_effects(self, entity_id: str):
        """Инициализация эффектов для сущности"""
        if entity_id not in self.entity_effects:
            self.entity_effects[entity_id] = []
    
    def add_effect(self, entity_id: str, effect: Effect):
        """Добавление эффекта к сущности"""
        if entity_id not in self.entity_effects:
            self.entity_effects[entity_id] = []
        self._handle_effect_application(entity_id, effect)
