#!/usr/bin/env python3
"""
Система эффектов - управление специальными эффектами и их применением
"""

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState

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
    ICE = "ice"
    LIGHTNING = "lightning"
    IMAGINARY = "imaginary"
    QUANTUM = "quantum"
    DARK = "dark"
    LIGHT = "light"
    EARTH = "earth"
    AIR = "air"
    WATER = "water"
    LIGHTNING = "lightning"
    HOLY = "holy"
    POISON = "poison"
    TRUE = "true"
    ACID = "acid"
    COLD = "cold"
    MAGIC = "magic"
    NECROTIC = "necrotic"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SHADOW = "shadow"
    SOUND = "sound"
    VIBRATION = "vibration"
    MAGICAL = "magical"
    ENERGY = "energy"
    CHAOS = "chaos"
    LIGHT = "light"
    DARK = "dark"
    WIND = "wind"
    EARTH = "earth"
    LIGHT = "light"
    DARK = "dark"
    WIND = "wind"
    EARTH = "earth"
    LIGHT = "light"

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
    ON_RESIST = "on_resist"
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
        if self.target_type == TargetType.SELF:
            return True
        elif self.target_type == TargetType.ENEMY:
            return not hasattr(target, 'is_ally') or not target.is_ally
        elif self.target_type == TargetType.ALLY:
            return hasattr(target, 'is_ally') and target.is_ally
        elif self.target_type == TargetType.AREA:
            return True
        
        return False
    
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

class EffectSystem(ISystem):
    """Система управления эффектами для всех сущностей"""
    
    def __init__(self):
        self._system_name = "effect"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Оптимизированная система триггеров
        self.trigger_system = OptimizedTriggerSystem()
        
        # Система комбинаций
        self.combination_system = CombinationSystem()
        
        # Активные эффекты на сущностях
        self.active_effects: Dict[str, List[Effect]] = {}
        
        # Статистика эффектов
        self.effect_statistics = EffectStatistics()
        
        # Шаблоны эффектов
        self.effect_templates: Dict[str, Dict[str, Any]] = {}
        
        # Статистика системы
        self.system_stats = {
            'entities_count': 0,
            'active_effects_count': 0,
            'effects_triggered': 0,
            'update_time': 0.0
        }
        
        logger.info("Система эффектов инициализирована")
    
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
        """Инициализация системы эффектов"""
        try:
            logger.info("Инициализация системы эффектов...")
            
            # Инициализируем шаблоны эффектов
            self._initialize_effect_templates()
            
            # Настраиваем систему комбинаций
            self._setup_effect_combinations()
            
            self._system_state = SystemState.READY
            logger.info("Система эффектов успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы эффектов: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы эффектов"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем активные эффекты
            self._update_active_effects(delta_time)
            
            # Обрабатываем истекшие эффекты
            self._process_expired_effects()
            
            # Обновляем статистику системы
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы эффектов: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы эффектов"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система эффектов приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы эффектов: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы эффектов"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система эффектов возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы эффектов: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы эффектов"""
        try:
            logger.info("Очистка системы эффектов...")
            
            # Очищаем все данные
            self.active_effects.clear()
            self.effect_templates.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'entities_count': 0,
                'active_effects_count': 0,
                'effects_triggered': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система эффектов очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы эффектов: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'entities_count': len(self.active_effects),
            'active_effects_count': self.system_stats['active_effects_count'],
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "effect_applied":
                return self._handle_effect_applied(event_data)
            elif event_type == "effect_removed":
                return self._handle_effect_removed(event_data)
            elif event_type == "trigger_activated":
                return self._handle_trigger_activated(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def add_effect_to_entity(self, entity_id: str, effect: Effect, source: Any = None) -> bool:
        """Добавляет эффект к сущности"""
        try:
            if entity_id not in self.active_effects:
                self.active_effects[entity_id] = []
                self.system_stats['entities_count'] = len(self.active_effects)
            
            self.active_effects[entity_id].append(effect)
            self.system_stats['active_effects_count'] = sum(len(effects) for effects in self.active_effects.values())
            
            logger.debug(f"Эффект {effect.name} добавлен к сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления эффекта к сущности {entity_id}: {e}")
            return False
    
    def remove_effect_from_entity(self, entity_id: str, effect_name: str) -> bool:
        """Удаляет эффект с сущности"""
        try:
            if entity_id in self.active_effects:
                self.active_effects[entity_id] = [
                    effect for effect in self.active_effects[entity_id] 
                    if effect.name != effect_name
                ]
                
                self.system_stats['active_effects_count'] = sum(len(effects) for effects in self.active_effects.values())
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка удаления эффекта с сущности {entity_id}: {e}")
            return False
    
    def get_entity_effects(self, entity_id: str) -> List[Effect]:
        """Получает все активные эффекты сущности"""
        return self.active_effects.get(entity_id, [])
    
    def trigger_effect(self, trigger_type: TriggerType, source: Any, target: Any = None, context: Dict[str, Any] = None) -> bool:
        """Активирует эффекты по триггеру"""
        try:
            if context is None:
                context = {}
            
            # Активируем триггеры
            self.trigger_system.trigger(trigger_type, source, target, context)
            
            # Обновляем статистику
            self.system_stats['effects_triggered'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка активации триггера {trigger_type.value}: {e}")
            return False
    
    def _initialize_effect_templates(self) -> None:
        """Инициализация шаблонов эффектов"""
        try:
            # Шаблоны для разных типов эффектов
            self.effect_templates = {
                'fire_damage': {
                    'name': 'Огненный урон',
                    'category': EffectCategory.INSTANT,
                    'value': 25.0,
                    'damage_types': [DamageType.FIRE],
                    'duration': 0,
                    'target_type': TargetType.ENEMY
                },
                'poison_dot': {
                    'name': 'Отравление',
                    'category': EffectCategory.DOT,
                    'value': 5.0,
                    'damage_types': [DamageType.POISON],
                    'duration': 10.0,
                    'period': 1.0,
                    'target_type': TargetType.ENEMY
                },
                'strength_buff': {
                    'name': 'Усиление силы',
                    'category': EffectCategory.BUFF,
                    'value': 10.0,
                    'duration': 30.0,
                    'target_type': TargetType.SELF
                }
            }
            
            logger.debug("Шаблоны эффектов инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать шаблоны эффектов: {e}")
    
    def _setup_effect_combinations(self) -> None:
        """Настройка комбинаций эффектов"""
        try:
            # Регистрируем комбинации эффектов
            # Например: огонь + лед = взрыв пара
            pass
        except Exception as e:
            logger.warning(f"Не удалось настроить комбинации эффектов: {e}")
    
    def _update_active_effects(self, delta_time: float) -> None:
        """Обновление активных эффектов"""
        try:
            # Обновляем все активные эффекты
            for entity_id, effects in self.active_effects.items():
                for effect in effects:
                    if effect.duration > 0:
                        effect.apply_over_time(None, None)  # source и target можно передавать
                        
        except Exception as e:
            logger.warning(f"Ошибка обновления активных эффектов: {e}")
    
    def _process_expired_effects(self) -> None:
        """Обработка истекших эффектов"""
        try:
            current_time = time.time()
            
            # Удаляем истекшие эффекты
            for entity_id in list(self.active_effects.keys()):
                if entity_id in self.active_effects:
                    self.active_effects[entity_id] = [
                        effect for effect in self.active_effects[entity_id]
                        if effect.duration == 0 or effect.duration > current_time
                    ]
                    
                    # Удаляем пустые записи
                    if not self.active_effects[entity_id]:
                        del self.active_effects[entity_id]
            
            # Обновляем статистику
            self.system_stats['entities_count'] = len(self.active_effects)
            self.system_stats['active_effects_count'] = sum(len(effects) for effects in self.active_effects.values())
            
        except Exception as e:
            logger.warning(f"Ошибка обработки истекших эффектов: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                # Инициализируем список эффектов для новой сущности
                self.active_effects[entity_id] = []
                self.system_stats['entities_count'] = len(self.active_effects)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_effect_applied(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события применения эффекта"""
        try:
            entity_id = event_data.get('entity_id')
            effect_data = event_data.get('effect_data', {})
            
            if entity_id and effect_data:
                # Создаем эффект из данных
                effect = Effect.from_dict(effect_data)
                return self.add_effect_to_entity(entity_id, effect)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события применения эффекта: {e}")
            return False
    
    def _handle_effect_removed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события удаления эффекта"""
        try:
            entity_id = event_data.get('entity_id')
            effect_name = event_data.get('effect_name')
            
            if entity_id and effect_name:
                return self.remove_effect_from_entity(entity_id, effect_name)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события удаления эффекта: {e}")
            return False
    
    def _handle_trigger_activated(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события активации триггера"""
        try:
            trigger_type = TriggerType(event_data.get('trigger_type', 'on_hit'))
            source = event_data.get('source')
            target = event_data.get('target')
            context = event_data.get('context', {})
            
            return self.trigger_effect(trigger_type, source, target, context)
            
        except Exception as e:
            logger.error(f"Ошибка обработки события активации триггера: {e}")
            return False

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
