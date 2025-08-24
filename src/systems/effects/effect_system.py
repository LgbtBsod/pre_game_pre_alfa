#!/usr/bin/env python3
"""
Effect System - Система эффектов и спецэффектов
Отвечает за управление всеми эффектами в игре
"""

import logging
import random
import time
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class EffectCategory(Enum):
    """Категории эффектов"""
    INSTANT = "instant"           # Мгновенный эффект
    BUFF = "buff"                 # Усиливающий эффект
    DEBUFF = "debuff"             # Ослабляющий эффект
    DOT = "dot"                   # Урон по времени
    HOT = "hot"                   # Лечение по времени
    SHIELD = "shield"             # Защитный эффект
    TRANSFORM = "transform"       # Трансформация
    SUMMON = "summon"             # Призыв

class TargetType(Enum):
    """Типы целей для эффектов"""
    SELF = "self"                 # На себя
    ENEMY = "enemy"               # На врага
    ALLY = "ally"                 # На союзника
    AREA = "area"                 # На область
    PROJECTILE = "projectile"     # Проектиль

class DamageType(Enum):
    """Типы урона"""
    PHYSICAL = "physical"         # Физический
    MAGICAL = "magical"           # Магический
    FIRE = "fire"                 # Огонь
    ICE = "ice"                   # Лед
    LIGHTNING = "lightning"       # Молния
    POISON = "poison"             # Яд
    TRUE = "true"                 # Истинный урон
    COLD = "cold"                 # Холод

@dataclass
class Effect:
    """Базовый класс эффекта"""
    name: str
    category: EffectCategory
    value: Union[float, Dict[str, float]]  # Значение эффекта или словарь статов
    duration: float = 0.0                  # Длительность (0 = мгновенный)
    period: float = 1.0                    # Период применения для DOT/HOT
    damage_types: List[DamageType] = field(default_factory=list)
    scaling: Dict[str, float] = field(default_factory=dict)  # Масштабирование от статов
    target_type: TargetType = TargetType.ENEMY
    area: Optional[Dict[str, Any]] = None  # Параметры области действия
    projectile_speed: float = 0.0          # Скорость проектиля
    ignore_resistance: float = 0.0         # Игнорирование сопротивления
    crit_chance: float = 0.0               # Шанс критического удара
    crit_multiplier: float = 1.5           # Множитель критического удара
    stack_limit: int = 1                   # Лимит стаков
    can_dispel: bool = True                # Можно ли развеять
    is_hidden: bool = False                # Скрытый эффект
    
    def can_apply(self, source: Any, target: Any) -> bool:
        """Проверяет, можно ли применить эффект"""
        # Базовая проверка - всегда можно применить
        return True
    
    def apply_instant(self, source: Any, target: Any):
        """Применяет мгновенный эффект"""
        if self.category == EffectCategory.INSTANT:
            self._apply_damage(source, target)
        elif self.category == EffectCategory.SHIELD:
            self._apply_shield(source, target)
        elif self.category == EffectCategory.SUMMON:
            self._apply_summon(source, target)
    
    def _apply_damage(self, source: Any, target: Any):
        """Применяет урон"""
        if not self.damage_types:
            return
        
        # Базовый урон
        damage = self.value if isinstance(self.value, (int, float)) else 0
        
        # Применяем масштабирование от статов источника
        if self.scaling and hasattr(source, 'stats'):
            for stat, multiplier in self.scaling.items():
                if stat in source.stats:
                    damage += source.stats[stat] * multiplier
        
        # Применяем критический урон
        if random.random() < self.crit_chance:
            damage *= self.crit_multiplier
        
        # Применяем сопротивление цели
        if hasattr(target, 'resistances'):
            for damage_type in self.damage_types:
                if damage_type.value in target.resistances:
                    resistance = target.resistances[damage_type.value]
                    damage *= (1 - resistance * (1 - self.ignore_resistance))
        
        # Наносим урон
        if hasattr(target, 'take_damage'):
            target.take_damage(damage, self.damage_types[0] if self.damage_types else DamageType.PHYSICAL)
    
    def _apply_shield(self, source: Any, target: Any):
        """Применяет защитный эффект"""
        if hasattr(target, 'add_shield'):
            shield_value = self.value if isinstance(self.value, (int, float)) else 0
            target.add_shield(shield_value, self.duration)
    
    def _apply_summon(self, source: Any, target: Any):
        """Применяет призыв"""
        # Реализация призыва будет в отдельной системе
        pass

@dataclass
class SpecialEffect:
    """Структура для специальных эффектов предметов"""
    chance: float  # Вероятность срабатывания (0.0 - 1.0)
    effect: Effect  # Экземпляр класса Effect для применения
    trigger_condition: str = "on_hit"  # Условие срабатывания
    cooldown: float = 0  # Кулдаун между срабатываниями
    max_procs: int = 0  # Максимальное количество срабатываний (0 = без ограничений)
    last_proc_time: float = 0  # Время последнего срабатывания
    proc_count: int = 0  # Счетчик срабатываний
    
    def can_trigger(self, source: Any, target: Any, trigger_type: str) -> bool:
        """Проверяет, может ли эффект сработать в текущих условиях"""
        # Проверка типа триггера
        if self.trigger_condition != trigger_type:
            return False
            
        # Проверка вероятности
        if random.random() > self.chance:
            return False
            
        # Проверка кулдауна
        current_time = time.time()
        if self.cooldown > 0 and (current_time - self.last_proc_time) < self.cooldown:
            return False
            
        # Проверка максимального количества срабатываний
        if self.max_procs > 0 and self.proc_count >= self.max_procs:
            return False
            
        # Проверка условий применения эффекта
        if not self.effect.can_apply(source, target):
            return False
            
        return True
    
    def trigger(self, source: Any, target: Any):
        """Активирует эффект"""
        if self.effect.duration == 0:
            self.effect.apply_instant(source, target)
        else:
            if hasattr(target, 'add_effect'):
                target.add_effect(self.effect, source)
            
        # Обновляем данные о срабатывании
        self.last_proc_time = time.time()
        self.proc_count += 1
    
    def reset(self):
        """Сбрасывает счетчик срабатываний"""
        self.proc_count = 0
        self.last_proc_time = 0

class TriggerSystem:
    """Система для обработки триггеров спецэффектов"""
    
    def __init__(self):
        self.triggers = {
            "on_hit": [],
            "on_crit": [],
            "on_spell_cast": [],
            "on_being_hit": [],
            "on_block": [],
            "on_dodge": [],
            "on_kill": [],
            "on_low_health": [],
            "on_cold_damage": [],
            "on_lightning_damage": [],
            "on_fire_damage": [],
            "on_frost_shock_reaction": []
        }
    
    def register_trigger(self, trigger_type: str, callback: Callable):
        """Регистрирует callback для определенного триггера"""
        if trigger_type in self.triggers:
            self.triggers[trigger_type].append(callback)
    
    def trigger(self, trigger_type: str, source: Any, target: Any = None, **kwargs):
        """Активирует все зарегистрированные триггеры указанного типа"""
        if trigger_type in self.triggers:
            for callback in self.triggers[trigger_type]:
                try:
                    callback(source, target, **kwargs)
                except Exception as e:
                    logger.error(f"Ошибка в триггере {trigger_type}: {e}")

class EffectSystem:
    """Основная система управления эффектами"""
    
    def __init__(self):
        self.active_effects: Dict[str, List[Dict[str, Any]]] = {}
        self.trigger_system = TriggerSystem()
        self.effect_templates: Dict[str, Effect] = {}
        
        logger.info("Система эффектов инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы эффектов"""
        try:
            self._setup_effect_templates()
            self._setup_default_triggers()
            
            logger.info("Система эффектов успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы эффектов: {e}")
            return False
    
    def _setup_effect_templates(self):
        """Настройка шаблонов эффектов"""
        # Эффект поджига
        self.effect_templates["burn"] = Effect(
            name="Ожог",
            category=EffectCategory.DOT,
            value=8,
            damage_types=[DamageType.FIRE],
            duration=5,
            period=1,
            scaling={"intelligence": 0.2},
            target_type=TargetType.ENEMY
        )
        
        # Эффект заморозки
        self.effect_templates["freeze"] = Effect(
            name="Заморозка",
            category=EffectCategory.DEBUFF,
            value={"movement_speed": -0.5, "attack_speed": -0.3},
            duration=3,
            target_type=TargetType.ENEMY
        )
        
        # Эффект электрошока
        self.effect_templates["shock"] = Effect(
            name="Электрошок",
            category=EffectCategory.DOT,
            value=5,
            damage_types=[DamageType.LIGHTNING],
            duration=4,
            period=0.5,
            target_type=TargetType.ENEMY
        )
        
        # Эффект отравления
        self.effect_templates["poison"] = Effect(
            name="Отравление",
            category=EffectCategory.DOT,
            value=3,
            damage_types=[DamageType.POISON],
            duration=6,
            period=1,
            target_type=TargetType.ENEMY
        )
    
    def _setup_default_triggers(self):
        """Настройка стандартных триггеров"""
        # Триггер для оружия при попадании
        def weapon_on_hit(source, target, **kwargs):
            if hasattr(source, 'equipped_weapon') and source.equipped_weapon:
                if hasattr(source.equipped_weapon, 'apply_special_effects'):
                    source.equipped_weapon.apply_special_effects(source, target, "on_hit")
        
        # Триггер для аксессуаров при применении заклинания
        def accessory_on_spell_cast(source, target, **kwargs):
            if hasattr(source, 'equipped_accessories'):
                for accessory in source.equipped_accessories:
                    if hasattr(accessory, 'apply_special_effects'):
                        accessory.apply_special_effects(source, target, "on_spell_cast")
        
        self.trigger_system.register_trigger("on_hit", weapon_on_hit)
        self.trigger_system.register_trigger("on_spell_cast", accessory_on_spell_cast)
    
    def add_effect_to_entity(self, entity_id: str, effect: Effect, source: Any, duration: float = None):
        """Добавляет эффект к сущности"""
        if entity_id not in self.active_effects:
            self.active_effects[entity_id] = []
        
        effect_data = {
            "effect": effect,
            "source": source,
            "start_time": time.time(),
            "duration": duration or effect.duration,
            "last_tick": time.time(),
            "stacks": 1
        }
        
        # Проверяем, есть ли уже такой эффект
        existing_effect = None
        for existing in self.active_effects[entity_id]:
            if existing["effect"].name == effect.name:
                existing_effect = existing
                break
        
        if existing_effect:
            # Увеличиваем стаки или обновляем длительность
            if effect.stack_limit > 1:
                existing_effect["stacks"] = min(existing_effect["stacks"] + 1, effect.stack_limit)
            existing_effect["duration"] = max(existing_effect["duration"], effect_data["duration"])
            existing_effect["last_tick"] = time.time()
        else:
            self.active_effects[entity_id].append(effect_data)
        
        logger.debug(f"Эффект {effect.name} добавлен к {entity_id}")
    
    def remove_effect_from_entity(self, entity_id: str, effect_name: str):
        """Удаляет эффект с сущности"""
        if entity_id in self.active_effects:
            self.active_effects[entity_id] = [
                e for e in self.active_effects[entity_id] 
                if e["effect"].name != effect_name
            ]
    
    def update_entity_effects(self, entity_id: str, delta_time: float):
        """Обновляет эффекты сущности"""
        if entity_id not in self.active_effects:
            return
        
        current_time = time.time()
        effects_to_remove = []
        
        for effect_data in self.active_effects[entity_id]:
            effect = effect_data["effect"]
            
            # Проверяем истечение длительности
            if effect_data["duration"] > 0:
                elapsed = current_time - effect_data["start_time"]
                if elapsed >= effect_data["duration"]:
                    effects_to_remove.append(effect_data)
                    continue
            
            # Применяем периодические эффекты (DOT/HOT)
            if effect.category in [EffectCategory.DOT, EffectCategory.HOT] and effect.period > 0:
                time_since_tick = current_time - effect_data["last_tick"]
                if time_since_tick >= effect.period:
                    self._apply_periodic_effect(effect_data, entity_id)
                    effect_data["last_tick"] = current_time
        
        # Удаляем истекшие эффекты
        for effect_data in effects_to_remove:
            self.active_effects[entity_id].remove(effect_data)
    
    def _apply_periodic_effect(self, effect_data: Dict[str, Any], entity_id: str):
        """Применяет периодический эффект"""
        effect = effect_data["effect"]
        source = effect_data["source"]
        
        # Находим сущность
        # В реальной реализации здесь должна быть связь с системой сущностей
        target = None  # Получаем сущность по entity_id
        
        if target and hasattr(target, 'take_damage'):
            # Применяем урон/лечение
            if effect.category == EffectCategory.DOT:
                damage = effect.value * effect_data["stacks"]
                if effect.damage_types:
                    target.take_damage(damage, effect.damage_types[0])
            elif effect.category == EffectCategory.HOT:
                healing = effect.value * effect_data["stacks"]
                if hasattr(target, 'heal'):
                    target.heal(healing)
    
    def get_entity_effects(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получает список активных эффектов сущности"""
        return self.active_effects.get(entity_id, [])
    
    def cleanup(self):
        """Очистка системы эффектов"""
        logger.info("Очистка системы эффектов...")
        self.active_effects.clear()
        self.effect_templates.clear()
        self.trigger_system.triggers.clear()
