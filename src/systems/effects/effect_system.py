#!/usr/bin/env python3
"""
Effect System - Консолидированная система эффектов
Объединяет все типы эффектов в единую архитектуру
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

from ...core.architecture import BaseComponent, ComponentType, Priority, LifecycleState

logger = logging.getLogger(__name__)

# ============================================================================
# БАЗОВЫЕ ТИПЫ И КОНСТАНТЫ
# ============================================================================

class EffectCategory(Enum):
    """Категории эффектов"""
    INSTANT = "instant"           # Мгновенные эффекты
    DURATION = "duration"         # Эффекты с длительностью
    PERMANENT = "permanent"       # Постоянные эффекты
    TRIGGER = "trigger"           # Эффекты по триггеру
    STACKING = "stacking"         # Накладывающиеся эффекты

class EffectType(Enum):
    """Типы эффектов"""
    BUFF = "buff"                 # Усиливающий эффект
    DEBUFF = "debuff"             # Ослабляющий эффект
    DAMAGE = "damage"             # Урон
    HEAL = "heal"                 # Лечение
    MOVEMENT = "movement"         # Движение
    VISUAL = "visual"             # Визуальный эффект
    AUDIO = "audio"               # Звуковой эффект
    COMBINATION = "combination"   # Комбинированный эффект

class ConflictResolution(Enum):
    """Способы разрешения конфликтов эффектов"""
    IGNORE = "ignore"             # Игнорировать новый эффект
    REPLACE = "replace"           # Заменить старый эффект
    STACK = "stack"               # Накладывать эффекты
    MERGE = "merge"               # Объединить эффекты

@dataclass
class EffectVisuals:
    """Визуальные эффекты"""
    particle_effect: Optional[str] = None
    sound_effect: Optional[str] = None
    screen_shake: float = 0.0
    color_change: Optional[tuple] = None
    scale_change: Optional[float] = None
    animation: Optional[str] = None

@dataclass
class EffectBalance:
    """Баланс эффекта"""
    base_power: float = 1.0
    scaling_factor: float = 1.0
    pvp_modifier: float = 1.0
    pve_modifier: float = 1.0
    level_scaling: float = 0.1
    max_stacks: int = 1

# ============================================================================
# БАЗОВЫЕ КЛАССЫ ЭФФЕКТОВ
# ============================================================================

class Effect:
    """Базовый класс для всех эффектов"""
    
    def __init__(
        self,
        name: str,
        category: EffectCategory,
        effect_type: EffectType,
        value: Union[int, float, Dict[str, Any]],
        duration: float = 0.0,
        tags: List[str] = None,
        visuals: Optional[EffectVisuals] = None,
        balance: Optional[EffectBalance] = None,
        cancellation_tags: List[str] = None,
        conflict_resolution: ConflictResolution = ConflictResolution.IGNORE,
        is_permanent: bool = False,
        permanent_condition: Optional[Callable] = None,
        dynamic_parameters: Dict[str, Callable] = None
    ):
        self.name = name
        self.category = category
        self.effect_type = effect_type
        self.value = value
        self.duration = duration
        self.tags = tags or []
        self.visuals = visuals or EffectVisuals()
        self.balance = balance or EffectBalance()
        self.cancellation_tags = cancellation_tags or []
        self.conflict_resolution = conflict_resolution
        self.is_permanent = is_permanent
        self.permanent_condition = permanent_condition
        self.dynamic_parameters = dynamic_parameters or {}
        
        # Состояние эффекта
        self.applied_time = 0.0
        self.expiry_time = 0.0
        self.stack_count = 1
        self.is_active = False
        
        # Метаданные
        self.source_id = None
        self.target_id = None
        self.application_context = {}
        
        logger.debug(f"Создан эффект: {name} ({category.value})")
    
    def apply(self, target: Any, source: Any, context: Dict[str, Any] = None) -> bool:
        """Применение эффекта к цели"""
        try:
            if context is None:
                context = {}
            
            # Проверка возможности применения
            if not self.can_apply(source, target):
                return False
            
            # Обновляем контекст
            self.source_id = getattr(source, 'id', str(source))
            self.target_id = getattr(target, 'id', str(target))
            self.application_context = context
            
            # Применяем эффект
            if self._apply_effect(target, source, context):
                self._on_effect_applied(target, source, context)
            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка применения эффекта {self.name}: {e}")
            return False
    
    def remove(self, target: Any) -> bool:
        """Удаление эффекта с цели"""
        try:
            if not self.is_active:
                return True
            
            # Убираем эффект
            if self._remove_effect(target):
                self._on_effect_removed(target)
            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка удаления эффекта {self.name}: {e}")
            return False
    
    def update(self, target: Any, delta_time: float) -> bool:
        """Обновление эффекта"""
        try:
            if not self.is_active:
                return True
            
            # Проверяем истечение времени
            if self.duration > 0 and time.time() > self.expiry_time:
                return self.remove(target)
            
            # Обновляем эффект
            return self._update_effect(target, delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления эффекта {self.name}: {e}")
            return False
    
    def can_apply(self, source: Any, target: Any, context: Dict[str, Any] = None) -> bool:
        """Проверка возможности применения эффекта"""
        try:
            if context is None:
                context = {}
            
            # Проверка постоянных условий
            if self.is_permanent and self.permanent_condition:
                return self.permanent_condition(source, target, context)
            
            # Проверка конфликтов
            if hasattr(target, 'active_effects'):
                for active_effect in target.active_effects:
                    if self.conflicts_with(active_effect):
                        if self.conflict_resolution == ConflictResolution.IGNORE:
                            return False
                        elif self.conflict_resolution == ConflictResolution.REPLACE:
                            target.remove_effect(active_effect)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки возможности применения {self.name}: {e}")
            return False
    
    def conflicts_with(self, other: 'Effect') -> bool:
        """Проверка конфликта с другим эффектом"""
        return any(tag in other.tags for tag in self.cancellation_tags)
    
    def get_modified_value(self, context: Dict[str, Any]) -> Union[int, float, Dict[str, Any]]:
        """Расчет модифицированного значения эффекта"""
        try:
            modified_value = self.value
            
            # Применение базовых модификаторов
            if isinstance(modified_value, (int, float)):
                modified_value *= self.balance.base_power * self.balance.scaling_factor
            else:
                # Для словарей применяем модификаторы к каждому значению
                modified_value = {
                    k: v * self.balance.base_power * self.balance.scaling_factor
                    for k, v in modified_value.items()
                }
            
            # Применение динамических параметров
            for param, func in self.dynamic_parameters.items():
                if param in modified_value if isinstance(modified_value, dict) else True:
                    modified_value = func(context.get("source"), context.get("target"))
            
            # Применение контекстных модификаторов
            if context.get("is_pvp"):
                multiplier = self.balance.pvp_modifier
            else:
                multiplier = self.balance.pve_modifier
            
            if isinstance(modified_value, dict):
                modified_value = {k: v * multiplier for k, v in modified_value.items()}
            else:
                modified_value *= multiplier
            
            # Применение масштабирования с уровнем
            if "source_level" in context and self.balance.level_scaling > 0:
                level_factor = 1.0 + (context["source_level"] - 1) * self.balance.level_scaling
                if isinstance(modified_value, dict):
                    modified_value = {k: v * level_factor for k, v in modified_value.items()}
                else:
                    modified_value *= level_factor
            
            return modified_value
            
        except Exception as e:
            logger.error(f"Ошибка расчета модифицированного значения {self.name}: {e}")
            return self.value
    
    def _apply_effect(self, target: Any, source: Any, context: Dict[str, Any]) -> bool:
        """Внутреннее применение эффекта"""
        try:
            # Создаем контекст для применения
            apply_context = {
                "source": source,
                "target": target,
                "source_level": getattr(source, 'level', 1),
                "target_level": getattr(target, 'level', 1),
                "is_pvp": context.get("is_pvp", False),
                "combat_state": context.get("combat_state", "normal")
            }
            
            # Получаем модифицированное значение
            modified_value = self.get_modified_value(apply_context)
            
            # Применяем эффект
            if isinstance(modified_value, dict):
                for stat, modifier in modified_value.items():
                    if hasattr(target, stat):
                        current = getattr(target, stat, 0)
                        setattr(target, stat, current + modifier)
            else:
                # Прямое применение
                if hasattr(target, 'apply_direct_effect'):
                    target.apply_direct_effect(modified_value)
                else:
                    # Fallback: пытаемся применить к здоровью
                    if hasattr(target, 'health'):
                        target.health = max(0, target.health + modified_value)
            
            # Устанавливаем время применения
            self.applied_time = time.time()
            if self.duration > 0:
                self.expiry_time = self.applied_time + self.duration
            
            # Активируем эффект
            self.is_active = True
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка внутреннего применения эффекта {self.name}: {e}")
            return False
    
    def _remove_effect(self, target: Any) -> bool:
        """Внутреннее удаление эффекта"""
        try:
            # Убираем эффект
            if isinstance(self.value, dict):
                for stat, modifier in self.value.items():
                    if hasattr(target, stat):
                        current = getattr(target, stat, 0)
                        setattr(target, stat, current - modifier)
            else:
                # Прямое удаление
                if hasattr(target, 'remove_direct_effect'):
                    target.remove_direct_effect(self.value)
            
            # Деактивируем эффект
            self.is_active = False
            self.applied_time = 0.0
            self.expiry_time = 0.0
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка внутреннего удаления эффекта {self.name}: {e}")
            return False
    
    def _update_effect(self, target: Any, delta_time: float) -> bool:
        """Внутреннее обновление эффекта"""
        # Базовая реализация - ничего не делает
        # Переопределяется в наследниках для специфичной логики
        return True
    
    def _on_effect_applied(self, target: Any, source: Any, context: Dict[str, Any]):
        """Обработчик применения эффекта"""
        try:
            # Воспроизведение визуальных эффектов
            if self.visuals:
                self._play_visuals(target)
            
            # Логирование
            logger.debug(f"Эффект {self.name} применен к {getattr(target, 'id', target)}")
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике применения эффекта {self.name}: {e}")
    
    def _on_effect_removed(self, target: Any):
        """Обработчик удаления эффекта"""
        try:
            # Логирование
            logger.debug(f"Эффект {self.name} удален с {getattr(target, 'id', target)}")
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике удаления эффекта {self.name}: {e}")
    
    def _play_visuals(self, target: Any):
        """Воспроизведение визуальных эффектов"""
        try:
            # Здесь будет логика воспроизведения эффектов
            # Пока просто логируем
            if self.visuals.particle_effect:
                logger.debug(f"Воспроизводится частичный эффект: {self.visuals.particle_effect}")
            
            if self.visuals.sound_effect:
                logger.debug(f"Воспроизводится звук: {self.visuals.sound_effect}")
            
            if self.visuals.screen_shake > 0:
                logger.debug(f"Тряска экрана: {self.visuals.screen_shake}")
                
        except Exception as e:
            logger.error(f"Ошибка воспроизведения визуальных эффектов {self.name}: {e}")

# ============================================================================
# СПЕЦИАЛЬНЫЕ ЭФФЕКТЫ
# ============================================================================

class SpecialEffect:
    """Специальный эффект с дополнительной логикой"""
    
    def __init__(
        self,
        chance: float,
        effect: Effect,
        trigger_condition: str,
        cooldown: float = 0,
        max_procs: int = 0,
        conditions: List[Callable] = None,
        combination_effects: List['SpecialEffect'] = None,
        track_stats: bool = False,
        achievement_id: Optional[str] = None,
        delay: float = 0,
        delayed_effect: Optional['SpecialEffect'] = None,
        chain_effects: List['SpecialEffect'] = None,
        chain_delay: float = 0
    ):
        self.chance = chance
        self.effect = effect
        self.trigger_condition = trigger_condition
        self.cooldown = cooldown
        self.max_procs = max_procs
        self.conditions = conditions or []
        self.combination_effects = combination_effects or []
        self.track_stats = track_stats
        self.achievement_id = achievement_id
        self.delay = delay
        self.delayed_effect = delayed_effect
        self.chain_effects = chain_effects or []
        self.chain_delay = chain_delay
        
        # Состояние
        self.last_proc_time = 0
        self.proc_count = 0
        
        logger.debug(f"Создан специальный эффект: {effect.name} (шанс: {chance})")
    
    def can_trigger(self, source: Any, target: Any, trigger_type: str, context: Dict[str, Any] = None) -> bool:
        """Проверяет, может ли эффект сработать в текущих условиях"""
        try:
            if context is None:
                context = {}
            
            # Проверка типа триггера
            if self.trigger_condition != trigger_type:
            return False
            
            # Проверка шанса
            if random.random() > self.chance:
            return False
    
            # Проверка кулдауна
            current_time = time.time()
            if self.cooldown > 0 and (current_time - self.last_proc_time) < self.cooldown:
            return False
            
            # Проверка максимального количества срабатываний
            if self.max_procs > 0 and self.proc_count >= self.max_procs:
            return False
    
            # Проверка возможности применения эффекта
            if not self.effect.can_apply(source, target, context):
            return False
            
            # Проверка дополнительных условий
            for condition in self.conditions:
                if not condition(source, target, context):
            return False
    
                return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки возможности срабатывания специального эффекта: {e}")
            return False
    
    def trigger(self, source: Any, target: Any, context: Dict[str, Any] = None) -> bool:
        """Активирует специальный эффект"""
        try:
            if context is None:
                context = {}
            
            # Обрабатываем задержку
            if self.delay > 0:
                self._schedule_delayed_effect(source, target, context)
                return True
            
            # Применяем основной эффект
            if self.effect.apply(target, source, context):
                # Применяем комбинационные эффекты
                for combo_effect in self.combination_effects:
                    if combo_effect.can_trigger(source, target, self.trigger_condition, context):
                        combo_effect.trigger(source, target, context)
                
                # Планируем цепные эффекты
                if self.chain_effects:
                    self._schedule_chain_effects(source, target, context)
                
                # Обновляем данные о срабатывании
                self.last_proc_time = time.time()
                self.proc_count += 1
                
                # Записываем статистику
                if self.track_stats and hasattr(source, 'effect_statistics'):
                    source.effect_statistics.record_trigger(self.effect.name)
                
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка срабатывания специального эффекта: {e}")
            return False
    
    def _schedule_delayed_effect(self, source: Any, target: Any, context: Dict[str, Any]):
        """Планирует отложенный эффект"""
        try:
            if self.delayed_effect:
                # В реальной реализации здесь был бы таймер
                # Пока просто логируем
                logger.debug(f"Запланирован отложенный эффект: {self.delayed_effect.effect.name}")
            
        except Exception as e:
            logger.error(f"Ошибка планирования отложенного эффекта: {e}")
    
    def _schedule_chain_effects(self, source: Any, target: Any, context: Dict[str, Any]):
        """Планирует цепные эффекты"""
        try:
            if self.chain_effects:
                # В реальной реализации здесь был бы таймер
                # Пока просто логируем
                logger.debug(f"Запланированы цепные эффекты: {len(self.chain_effects)}")
                
        except Exception as e:
            logger.error(f"Ошибка планирования цепных эффектов: {e}")

# ============================================================================
# СИСТЕМА УПРАВЛЕНИЯ ЭФФЕКТАМИ
# ============================================================================

class EffectSystem(BaseComponent):
    """Система управления эффектами"""
    
    def __init__(self):
        super().__init__("effect_system", ComponentType.SYSTEM, Priority.NORMAL)
        
        # Реестр эффектов
        self.effects_registry: Dict[str, Effect] = {}
        self.special_effects_registry: Dict[str, SpecialEffect] = {}
        
        # Активные эффекты
        self.active_effects: Dict[str, List[Effect]] = {}  # target_id -> [effects]
        
        # Статистика
        self.total_effects_applied = 0
        self.total_special_effects_triggered = 0
        self.last_cleanup = time.time()
        
        logger.info("Effect System инициализирован")
    
    def _on_initialize(self) -> bool:
        """Инициализация системы"""
        try:
            # Регистрируем базовые эффекты
            self._register_base_effects()
            
            # Регистрируем специальные эффекты
            self._register_special_effects()
            
            logger.info("Effect System готов к работе")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Effect System: {e}")
            return False
    
    def _on_start(self) -> bool:
        """Запуск системы"""
        try:
            logger.info("Effect System запущен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска Effect System: {e}")
            return False
    
    def _on_stop(self) -> bool:
        """Остановка системы"""
        try:
            logger.info("Effect System остановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки Effect System: {e}")
            return False
    
    def _on_destroy(self) -> bool:
        """Уничтожение системы"""
        try:
            # Очищаем все эффекты
            self.clear_all_effects()
            
            # Очищаем реестры
            self.effects_registry.clear()
            self.special_effects_registry.clear()
            
            logger.info("Effect System уничтожен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения Effect System: {e}")
            return False
    
    def _register_base_effects(self):
        """Регистрация базовых эффектов"""
        try:
            # Эффекты урона
            damage_effect = Effect(
                name="Урон",
                category=EffectCategory.INSTANT,
                effect_type=EffectType.DAMAGE,
                value={"health": -10},
                tags=["damage", "combat"]
            )
            self.register_effect("damage", damage_effect)
            
            # Эффекты лечения
            heal_effect = Effect(
                name="Лечение",
                category=EffectCategory.INSTANT,
                effect_type=EffectType.HEAL,
                value={"health": 10},
                tags=["heal", "support"]
            )
            self.register_effect("heal", heal_effect)
            
            # Эффекты усиления
            buff_effect = Effect(
                name="Усиление",
                category=EffectCategory.DURATION,
                effect_type=EffectType.BUFF,
                value={"strength": 5},
                duration=30.0,
                tags=["buff", "combat"]
            )
            self.register_effect("buff", buff_effect)
            
            logger.info("Базовые эффекты зарегистрированы")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации базовых эффектов: {e}")
    
    def _register_special_effects(self):
        """Регистрация специальных эффектов"""
        try:
            # Критический удар
            crit_effect = Effect(
                name="Критический урон",
                category=EffectCategory.INSTANT,
                effect_type=EffectType.DAMAGE,
                value={"health": -20},
                tags=["damage", "critical", "combat"]
            )
            
            crit_special = SpecialEffect(
                chance=0.25,
                effect=crit_effect,
                trigger_condition="on_hit",
                cooldown=5.0,
                track_stats=True
            )
            self.register_special_effect("critical_hit", crit_special)
            
            logger.info("Специальные эффекты зарегистрированы")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации специальных эффектов: {e}")
    
    def register_effect(self, effect_id: str, effect: Effect) -> bool:
        """Регистрация эффекта в системе"""
        try:
            if effect_id in self.effects_registry:
                logger.warning(f"Эффект {effect_id} уже зарегистрирован")
            return False

            self.effects_registry[effect_id] = effect
            logger.debug(f"Эффект {effect_id} зарегистрирован")
                return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации эффекта {effect_id}: {e}")
            return False
    
    def register_special_effect(self, effect_id: str, special_effect: SpecialEffect) -> bool:
        """Регистрация специального эффекта в системе"""
        try:
            if effect_id in self.special_effects_registry:
                logger.warning(f"Специальный эффект {effect_id} уже зарегистрирован")
                return False
            
            self.special_effects_registry[effect_id] = special_effect
            logger.debug(f"Специальный эффект {effect_id} зарегистрирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации специального эффекта {effect_id}: {e}")
            return False
    
    def apply_effect(self, target: Any, effect_id: str, source: Any = None, context: Dict[str, Any] = None) -> bool:
        """Применение эффекта к цели"""
        try:
            if effect_id not in self.effects_registry:
                logger.warning(f"Эффект {effect_id} не найден")
                return False
            
            effect = self.effects_registry[effect_id]
            
            if effect.apply(target, source or target, context or {}):
                # Добавляем в активные эффекты
                target_id = getattr(target, 'id', str(target))
                if target_id not in self.active_effects:
                    self.active_effects[target_id] = []
                
                self.active_effects[target_id].append(effect)
                self.total_effects_applied += 1
                
                logger.debug(f"Эффект {effect_id} применен к {target_id}")
            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка применения эффекта {effect_id}: {e}")
            return False
    
    def remove_effect(self, target: Any, effect_name: str) -> bool:
        """Удаление эффекта с цели"""
        try:
            target_id = getattr(target, 'id', str(target))
            
            if target_id not in self.active_effects:
                return False
            
            # Ищем эффект по имени
            for effect in self.active_effects[target_id]:
                if effect.name == effect_name:
                    if effect.remove(target):
                        self.active_effects[target_id].remove(effect)
                        logger.debug(f"Эффект {effect_name} удален с {target_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка удаления эффекта {effect_name}: {e}")
            return False
    
    def clear_all_effects(self):
        """Очистка всех эффектов"""
        try:
            for target_id, effects in self.active_effects.items():
                for effect in effects:
                    try:
                        # Получаем объект цели (в реальной реализации)
                        # effect.remove(target)
                        pass
        except Exception as e:
                        logger.error(f"Ошибка очистки эффекта {effect.name}: {e}")
            
            self.active_effects.clear()
            logger.info("Все эффекты очищены")
            
        except Exception as e:
            logger.error(f"Ошибка очистки всех эффектов: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        return {
            'total_effects_applied': self.total_effects_applied,
            'total_special_effects_triggered': self.total_special_effects_triggered,
            'registered_effects': len(self.effects_registry),
            'registered_special_effects': len(self.special_effects_registry),
            'active_effects': sum(len(effects) for effects in self.active_effects.values()),
            'last_cleanup': self.last_cleanup
        }
