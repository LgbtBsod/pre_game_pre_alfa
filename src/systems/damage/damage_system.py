#!/usr/bin/env python3
"""
Система урона - расчет и применение урона с различными типами и защитами
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from core.system_interfaces import BaseGameSystem, Priority
from core.constants import constants_manager, (
    SYSTEM_LIMITS_RO, PROBABILITY_CONSTANTS, DamageType,
    TIME_CONSTANTS_RO, get_float, canonicalize_damage_type
)
from core.entity_registry import get_entity

logger = logging.getLogger(__name__)

@dataclass
class Damage:
    """Класс урона"""
    amount: float
    damage_type: DamageType
    source: Optional[Any] = None
    critical: bool = False
    critical_multiplier: float = 2.0
    penetration: float = 0.0  # Игнорирование защиты
    elemental_affinity: float = 1.0  # Бонус к элементальному урону
    
    def calculate(self, target) -> float:
        """Расчет финального урона с учетом защит"""
        if self.damage_type == DamageType.TRUE:
            return self.amount
        
        # Базовый расчет
        final_damage = self.amount
        
        # Критический урон
        if self.critical:
            final_damage *= self.critical_multiplier
        
        # Учет сопротивлений
        resistance = target.get_resistance(self.damage_type)
        # Ограничиваем проникновение максимальным значением
        penetration = min(self.penetration, SYSTEM_LIMITS_RO["max_penetration_value"])
        resistance = max(0, resistance - penetration)  # Применяем проникновение
        # Ограничиваем сопротивление максимальным значением
        resistance = min(resistance, PROBABILITY_CONSTANTS["base_resistance_cap"])
        final_damage *= (1 - resistance)
        
        # Учет брони для физического урона
        if self.damage_type == DamageType.PHYSICAL:
            armor = target.get_armor()
            final_damage *= (1 - armor * PROBABILITY_CONSTANTS["base_armor_reduction"])  # 1 armor = 1% reduction
        
        # Элементальная стихия
        final_damage *= self.elemental_affinity
        
        # Ограничиваем финальный урон
        final_damage = max(PROBABILITY_CONSTANTS["base_damage_floor"], 
                          min(SYSTEM_LIMITS_RO["max_damage_value"], final_damage))
        
        return int(final_damage)

@dataclass
class DamageModifier:
    """Модификатор урона"""
    damage_type: DamageType
    multiplier: float
    source: str
    duration: float = 0.0
    stackable: bool = False
    max_stacks: int = 1

class DamageSystem(BaseGameSystem):
    """Система управления уроном (интегрирована с BaseGameSystem)"""
    
    def __init__(self):
        super().__init__("damage", Priority.HIGH)
        
        # Модификаторы урона
        self.damage_modifiers: Dict[str, DamageModifier] = {}
        
        # Статистика урона
        self.damage_stats = {
            'total_damage_dealt': 0,
            'total_damage_taken': 0,
            'critical_hits': 0,
            'damage_by_type': {dt.value: 0 for dt in DamageType},
            'effects_combined': 0,
            'update_time': 0.0
        }
        
        # Настройки системы
        self.system_settings = {
            'max_damage_modifiers': SYSTEM_LIMITS_RO["max_damage_modifiers"],
            'damage_combination_threshold': PROBABILITY_CONSTANTS["base_damage_combination_threshold"],
            'critical_chance_base': PROBABILITY_CONSTANTS["base_critical_chance"],
            'critical_multiplier_base': PROBABILITY_CONSTANTS["base_critical_multiplier"]
        }
        
        logger.info("Система урона инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы урона"""
        try:
            if not super().initialize():
                return False
            # Подпишемся на события шины для интеграции с другими системами
            try:
                if self.event_bus:
                    self.event_bus.on("deal_damage", self._on_deal_damage_event)
            except Exception:
                pass
            logger.info("Система урона успешно инициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации системы урона: {e}")
            return False
    
    def deal_damage(self, target, damage: Damage) -> float:
        """Нанесение урона"""
        # Расчет финального урона
        final_damage = damage.calculate(target)
        
        # Ограничиваем урон константами
        final_damage = max(PROBABILITY_CONSTANTS["base_damage_floor"], 
                          min(PROBABILITY_CONSTANTS["base_damage_ceiling"], final_damage))
        
        # Применение урона к цели
        target.take_damage(final_damage, damage.damage_type)
        
        # Обновление статистики
        self._update_damage_stats(damage, final_damage)
        
        # Логирование
        logger.debug(f"Нанесен урон {final_damage} типа {damage.damage_type.value} по {target}")
        
        return final_damage
    
    def _update_damage_stats(self, damage: Damage, final_damage: float):
        """Обновление статистики урона"""
        self.damage_stats['total_damage_dealt'] += final_damage
        self.damage_stats['damage_by_type'][damage.damage_type.value] += final_damage
        
        if damage.critical:
            self.damage_stats['critical_hits'] += 1
    
    def add_damage_modifier(self, modifier: DamageModifier):
        """Добавление модификатора урона"""
        if len(self.damage_modifiers) < SYSTEM_LIMITS_RO["max_damage_modifiers"]:
            self.damage_modifiers[modifier.source] = modifier
            logger.debug(f"Добавлен модификатор урона: {modifier.source}")
        else:
            logger.warning(f"Достигнут лимит модификаторов урона: {SYSTEM_LIMITS_RO['max_damage_modifiers']}")
    
    def remove_damage_modifier(self, source: str):
        """Удаление модификатора урона"""
        if source in self.damage_modifiers:
            del self.damage_modifiers[source]
            logger.debug(f"Удален модификатор урона: {source}")
    
    def get_damage_multiplier(self, damage_type: DamageType) -> float:
        """Получение множителя урона для типа"""
        multiplier = 1.0
        
        for modifier in self.damage_modifiers.values():
            if modifier.damage_type == damage_type:
                if modifier.stackable:
                    multiplier *= modifier.multiplier
                else:
                    multiplier = max(multiplier, modifier.multiplier)
        
        return multiplier
    
    def calculate_critical_chance(self, attacker) -> float:
        """Расчет шанса критического удара"""
        base_chance = self.system_settings['critical_chance_base']
        
        if hasattr(attacker, 'critical_chance'):
            base_chance += attacker.critical_chance
        
        # Ограничиваем шанс константами
        return min(PROBABILITY_CONSTANTS["max_critical_chance"], 
                  max(PROBABILITY_CONSTANTS["base_critical_chance"], base_chance))
    
    def calculate_critical_multiplier(self, attacker) -> float:
        """Расчет множителя критического удара"""
        base_multiplier = self.system_settings['critical_multiplier_base']
        
        if hasattr(attacker, 'critical_multiplier'):
            base_multiplier += attacker.critical_multiplier
        
        # Ограничиваем множитель константами
        return max(PROBABILITY_CONSTANTS["min_critical_multiplier"], 
                  min(PROBABILITY_CONSTANTS["max_critical_multiplier"], base_multiplier))
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы урона"""
        try:
            if not super().update(delta_time):
                return False
            # Очистка истекших модификаторов
            self._cleanup_expired_modifiers(delta_time)
            # Обновление статистики
            self.damage_stats['update_time'] += delta_time
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления системы урона: {e}")
            return False
    
    def _cleanup_expired_modifiers(self, dt: float):
        """Очистка истекших модификаторов"""
        # Проверяем, нужно ли очищать модификаторы
        if not hasattr(self, '_last_cleanup_time'):
            self._last_cleanup_time = 0
        
        self._last_cleanup_time += dt
        
        # Очищаем только через определенные интервалы
        if self._last_cleanup_time < get_float(TIME_CONSTANTS_RO, "damage_modifier_cleanup", 5.0):
            return
        
        expired_modifiers = []
        
        for source, modifier in self.damage_modifiers.items():
            modifier.duration -= self._last_cleanup_time
            if modifier.duration <= 0:
                expired_modifiers.append(source)
        
        for source in expired_modifiers:
            self.remove_damage_modifier(source)
        
        # Сбрасываем счетчик времени
        self._last_cleanup_time = 0
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return {
            'system_name': self.system_name,
            'system_state': self.system_state.value,
            'damage_stats': self.damage_stats,
            'active_modifiers': len(self.damage_modifiers),
            'system_limits': {
                'max_damage_modifiers': SYSTEM_LIMITS_RO["max_damage_modifiers"],
                'max_damage_value': SYSTEM_LIMITS_RO["max_damage_value"],
                'max_penetration_value': SYSTEM_LIMITS_RO["max_penetration_value"]
            }
        }

    # --- Event bus integration ---
    def _on_deal_damage_event(self, data: Dict[str, Any]) -> None:
        try:
            target = data.get('target')
            source = data.get('source')
            target_id = data.get('target_id')
            source_id = data.get('source_id')
            if target is None and target_id:
                target = get_entity(target_id)
            if source is None and source_id:
                source = get_entity(source_id)
            amount = data.get('amount', 0)
            damage_type = data.get('damage_type', DamageType.PHYSICAL.value)
            # В реальной интеграции здесь получаем объекты сущностей по id
            if hasattr(target, 'take_damage'):
                dmg = Damage(amount=amount, damage_type=canonicalize_damage_type(damage_type), source=source)
                self.deal_damage(target, dmg)
        except Exception:
            pass
    
    def reset_stats(self):
        """Сброс статистики"""
        self.damage_stats = {
            'total_damage_dealt': 0,
            'total_damage_taken': 0,
            'critical_hits': 0,
            'damage_by_type': {dt.value: 0 for dt in DamageType},
            'effects_combined': 0,
            'update_time': 0.0
        }
        logger.info("Статистика системы урона сброшена")
