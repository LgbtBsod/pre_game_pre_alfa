"""
Система урона - консолидированная система для всех типов урона
"""

import time
import random
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority


class DamageType(Enum):
    """Типы урона в игре"""
    PHYSICAL = "physical"      # Физический урон
    FIRE = "fire"              # Огненный урон
    COLD = "cold"              # Ледяной урон
    LIGHTNING = "lightning"    # Электрический урон
    ACID = "acid"              # Кислотный урон
    POISON = "poison"          # Ядовитый урон
    PSYCHIC = "psychic"        # Психический урон
    TRUE = "true"              # Истинный урон (игнорирует защиту)
    GENETIC = "genetic"        # Генетический урон
    EMOTIONAL = "emotional"    # Эмоциональный урон


class DamageCategory(Enum):
    """Категории урона"""
    DIRECT = "direct"          # Прямой урон
    OVER_TIME = "over_time"    # Урон по времени
    REFLECTED = "reflected"    # Отраженный урон
    SPLASH = "splash"          # Разбрызгивающийся урон
    CHAIN = "chain"            # Цепной урон


@dataclass
class DamageModifier:
    """Модификатор урона"""
    multiplier: float = 1.0
    flat_bonus: float = 0.0
    critical_chance: float = 0.0
    critical_multiplier: float = 2.0
    penetration: float = 0.0  # Проникновение через защиту
    source: Optional[str] = None


@dataclass
class DamageResistance:
    """Сопротивление урону"""
    resistance: float = 0.0  # 0.0 = нет сопротивления, 1.0 = полный иммунитет
    armor: float = 0.0       # Броня (для физического урона)
    absorption: float = 0.0  # Поглощение урона
    reflection: float = 0.0  # Отражение урона


@dataclass
class DamageInstance:
    """Экземпляр урона"""
    amount: float
    damage_type: DamageType
    category: DamageCategory
    source_id: str
    target_id: str
    timestamp: float = field(default_factory=time.time)
    modifiers: List[DamageModifier] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def get_total_amount(self) -> float:
        """Получить итоговую сумму урона с учетом модификаторов"""
        total = self.amount
        
        for modifier in self.modifiers:
            total = total * modifier.multiplier + modifier.flat_bonus
            
        return max(0, total)
    
    def is_critical(self) -> bool:
        """Проверить, является ли урон критическим"""
        for modifier in self.modifiers:
            if random.random() < modifier.critical_chance:
                return True
        return False
    
    def get_critical_multiplier(self) -> float:
        """Получить множитель критического урона"""
        max_multiplier = 1.0
        for modifier in self.modifiers:
            max_multiplier = max(max_multiplier, modifier.critical_multiplier)
        return max_multiplier


@dataclass
class DamageResult:
    """Результат применения урона"""
    original_damage: float
    final_damage: float
    damage_type: DamageType
    was_critical: bool
    was_blocked: bool
    was_absorbed: bool
    was_reflected: bool
    resistance_applied: float
    armor_applied: float
    timestamp: float = field(default_factory=time.time)


class DamageSystem(BaseComponent):
    """
    Консолидированная система урона
    Управляет всеми аспектами урона в игре
    """
    
    def __init__(self):
        super().__init__(
            name="DamageSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Регистры урона
        self.damage_types: Dict[str, DamageType] = {}
        self.damage_combinations: List[tuple] = []
        self.catalytic_effects: List[Callable] = []
        self.damage_history: List[DamageInstance] = []
        
        # Система сопротивлений
        self.resistance_modifiers: Dict[str, Dict[DamageType, float]] = {}
        self.armor_modifiers: Dict[str, float] = {}
        
        # Система комбо
        self.combo_timers: Dict[str, float] = {}
        self.combo_multipliers: Dict[str, float] = {}
        
        # Настройки
        self.max_damage_history = 1000
        self.combo_timeout = 3.0  # секунды
        
    def _on_initialize(self) -> bool:
        """Инициализация системы урона"""
        try:
            # Регистрация типов урона
            self._register_damage_types()
            
            # Регистрация комбинаций урона
            self._register_damage_combinations()
            
            # Регистрация каталитических эффектов
            self._register_catalytic_effects()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации DamageSystem: {e}")
            return False
    
    def _register_damage_types(self):
        """Регистрация всех типов урона"""
        for damage_type in DamageType:
            self.damage_types[damage_type.value] = damage_type
    
    def _register_damage_combinations(self):
        """Регистрация комбинаций урона"""
        # Огонь + Лед = Взрыв
        self.damage_combinations.append((
            [DamageType.FIRE, DamageType.COLD],
            self._create_explosion_effect()
        ))
        
        # Огонь + Электричество = Плазма
        self.damage_combinations.append((
            [DamageType.FIRE, DamageType.LIGHTNING],
            self._create_plasma_effect()
        ))
        
        # Кислота + Яд = Коррозия
        self.damage_combinations.append((
            [DamageType.ACID, DamageType.POISON],
            self._create_corrosion_effect()
        ))
        
        # Электричество + Вода = Шок
        self.damage_combinations.append((
            [DamageType.LIGHTNING, DamageType.COLD],
            self._create_shock_effect()
        ))
        
        # Психический + Эмоциональный = Ментальный взрыв
        self.damage_combinations.append((
            [DamageType.PSYCHIC, DamageType.EMOTIONAL],
            self._create_mental_explosion_effect()
        ))
        
        # Генетический + Физический = Мутация
        self.damage_combinations.append((
            [DamageType.GENETIC, DamageType.PHYSICAL],
            self._create_mutation_effect()
        ))
    
    def _register_catalytic_effects(self):
        """Регистрация каталитических эффектов"""
        # Эффект при критическом уроне
        self.catalytic_effects.append(self._critical_damage_effect)
        
        # Эффект при комбо
        self.catalytic_effects.append(self._combo_damage_effect)
        
        # Эффект при отражении
        self.catalytic_effects.append(self._reflection_damage_effect)
    
    def deal_damage(self, target_id: str, damage: DamageInstance) -> DamageResult:
        """
        Нанесение урона цели
        
        Args:
            target_id: ID цели
            damage: Экземпляр урона
            
        Returns:
            DamageResult: Результат применения урона
        """
        try:
            # Получаем сопротивления цели
            resistances = self._get_target_resistances(target_id)
            
            # Рассчитываем финальный урон
            final_damage = self._calculate_final_damage(damage, resistances)
            
            # Создаем результат
            result = DamageResult(
                original_damage=damage.amount,
                final_damage=final_damage,
                damage_type=damage.damage_type,
                was_critical=damage.is_critical(),
                was_blocked=final_damage <= 0,
                was_absorbed=False,  # TODO: Реализовать поглощение
                was_reflected=False,  # TODO: Реализовать отражение
                resistance_applied=resistances.get(damage.damage_type, 0.0),
                armor_applied=resistances.get('armor', 0.0)
            )
            
            # Применяем урон к цели
            if final_damage > 0:
                self._apply_damage_to_target(target_id, final_damage, damage)
            
            # Обновляем комбо
            self._update_combo(damage.source_id, damage.damage_type)
            
            # Проверяем комбинации урона
            self._check_damage_combinations(target_id, damage)
            
            # Применяем каталитические эффекты
            self._apply_catalytic_effects(target_id, damage, result)
            
            # Сохраняем в историю
            self._add_to_history(damage)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при нанесении урона: {e}")
            return DamageResult(
                original_damage=damage.amount,
                final_damage=0,
                damage_type=damage.damage_type,
                was_critical=False,
                was_blocked=True,
                was_absorbed=False,
                was_reflected=False,
                resistance_applied=0,
                armor_applied=0
            )
    
    def _get_target_resistances(self, target_id: str) -> Dict[str, float]:
        """Получить сопротивления цели"""
        resistances = {}
        
        # Базовые сопротивления
        if target_id in self.resistance_modifiers:
            resistances.update(self.resistance_modifiers[target_id])
        
        # Броня
        if target_id in self.armor_modifiers:
            resistances['armor'] = self.armor_modifiers[target_id]
        
        return resistances
    
    def _calculate_final_damage(self, damage: DamageInstance, resistances: Dict[str, float]) -> float:
        """Рассчитать финальный урон с учетом сопротивлений"""
        base_damage = damage.get_total_amount()
        
        # Истинный урон игнорирует все сопротивления
        if damage.damage_type == DamageType.TRUE:
            return base_damage
        
        # Применяем сопротивление к типу урона
        damage_resistance = resistances.get(damage.damage_type, 0.0)
        base_damage *= (1.0 - damage_resistance)
        
        # Применяем броню для физического урона
        if damage.damage_type == DamageType.PHYSICAL:
            armor = resistances.get('armor', 0.0)
            base_damage *= (1.0 - armor * 0.01)  # 1 броня = 1% снижение
        
        # Применяем критический урон
        if damage.is_critical():
            critical_multiplier = damage.get_critical_multiplier()
            base_damage *= critical_multiplier
        
        return max(1, int(base_damage))
    
    def _apply_damage_to_target(self, target_id: str, damage: float, damage_instance: DamageInstance):
        """Применить урон к цели"""
        # TODO: Интеграция с системой здоровья
        # target = self.get_entity(target_id)
        # if target:
        #     target.take_damage(damage, damage_instance.damage_type)
        pass
    
    def _update_combo(self, source_id: str, damage_type: DamageType):
        """Обновить комбо для источника урона"""
        current_time = time.time()
        combo_key = f"{source_id}_{damage_type.value}"
        
        if combo_key in self.combo_timers:
            # Увеличиваем множитель комбо
            self.combo_multipliers[combo_key] = min(3.0, self.combo_multipliers.get(combo_key, 1.0) + 0.2)
                else:
            # Начинаем новое комбо
            self.combo_multipliers[combo_key] = 1.0
        
        self.combo_timers[combo_key] = current_time
        
        # Очищаем старые комбо
        self._cleanup_old_combos(current_time)
    
    def _cleanup_old_combos(self, current_time: float):
        """Очистка старых комбо"""
        expired_combos = []
        
        for combo_key, timestamp in self.combo_timers.items():
            if current_time - timestamp > self.combo_timeout:
                expired_combos.append(combo_key)
        
        for combo_key in expired_combos:
            del self.combo_timers[combo_key]
            if combo_key in self.combo_multipliers:
                del self.combo_multipliers[combo_key]
    
    def _check_damage_combinations(self, target_id: str, damage: DamageInstance):
        """Проверить комбинации урона"""
        # TODO: Реализовать проверку комбинаций
        pass
    
    def _apply_catalytic_effects(self, target_id: str, damage: DamageInstance, result: DamageResult):
        """Применить каталитические эффекты"""
        for effect_func in self.catalytic_effects:
            try:
                effect_func(target_id, damage, result)
        except Exception as e:
                self.logger.error(f"Ошибка в каталитическом эффекте: {e}")
    
    def _add_to_history(self, damage: DamageInstance):
        """Добавить урон в историю"""
        self.damage_history.append(damage)
        
        # Ограничиваем размер истории
        if len(self.damage_history) > self.max_damage_history:
            self.damage_history.pop(0)
    
    # Каталитические эффекты
    def _critical_damage_effect(self, target_id: str, damage: DamageInstance, result: DamageResult):
        """Эффект критического урона"""
        if result.was_critical:
            # TODO: Визуальные эффекты критического урона
            pass
    
    def _combo_damage_effect(self, target_id: str, damage: DamageInstance, result: DamageResult):
        """Эффект комбо урона"""
        combo_key = f"{damage.source_id}_{damage.damage_type.value}"
        if combo_key in self.combo_multipliers:
            multiplier = self.combo_multipliers[combo_key]
            if multiplier > 1.5:
                # TODO: Визуальные эффекты комбо
                pass
    
    def _reflection_damage_effect(self, target_id: str, damage: DamageInstance, result: DamageResult):
        """Эффект отраженного урона"""
        if result.was_reflected:
            # TODO: Логика отражения урона
            
            pass
    
    # Создание эффектов комбинаций
    def _create_explosion_effect(self):
        """Создать эффект взрыва"""
        # TODO: Реализовать эффект взрыва
        pass
    
    def _create_plasma_effect(self):
        """Создать эффект плазмы"""
        # TODO: Реализовать эффект плазмы
        pass
    
    def _create_corrosion_effect(self):
        """Создать эффект коррозии"""
        # TODO: Реализовать эффект коррозии
        pass
    
    def _create_shock_effect(self):
        """Создать эффект шока"""
        # TODO: Реализовать эффект шока
        pass
    
    def _create_mental_explosion_effect(self):
        """Создать эффект ментального взрыва"""
        # TODO: Реализовать эффект ментального взрыва
        pass
    
    def _create_mutation_effect(self):
        """Создать эффект мутации"""
        # TODO: Реализовать эффект мутации
        pass
    
    # Публичные методы
    def register_resistance_modifier(self, entity_id: str, damage_type: DamageType, resistance: float):
        """Зарегистрировать модификатор сопротивления"""
        if entity_id not in self.resistance_modifiers:
            self.resistance_modifiers[entity_id] = {}
        self.resistance_modifiers[entity_id][damage_type] = resistance
    
    def register_armor_modifier(self, entity_id: str, armor: float):
        """Зарегистрировать модификатор брони"""
        self.armor_modifiers[entity_id] = armor
    
    def get_damage_history(self, entity_id: Optional[str] = None) -> List[DamageInstance]:
        """Получить историю урона"""
        if entity_id:
            return [d for d in self.damage_history if d.target_id == entity_id or d.source_id == entity_id]
        return self.damage_history.copy()
    
    def get_combo_multiplier(self, source_id: str, damage_type: DamageType) -> float:
        """Получить множитель комбо"""
        combo_key = f"{source_id}_{damage_type.value}"
        return self.combo_multipliers.get(combo_key, 1.0)
    
    def clear_damage_history(self):
        """Очистить историю урона"""
        self.damage_history.clear()
    
    def get_damage_statistics(self, entity_id: str) -> Dict[str, Any]:
        """Получить статистику урона для сущности"""
        entity_damage = [d for d in self.damage_history if d.target_id == entity_id or d.source_id == entity_id]
        
        if not entity_damage:
            return {}
        
        total_damage_dealt = sum(d.amount for d in entity_damage if d.source_id == entity_id)
        total_damage_taken = sum(d.amount for d in entity_damage if d.target_id == entity_id)
        critical_hits = sum(1 for d in entity_damage if d.source_id == entity_id and d.is_critical())
        
        return {
            'total_damage_dealt': total_damage_dealt,
            'total_damage_taken': total_damage_taken,
            'critical_hits': critical_hits,
            'damage_dealt_count': len([d for d in entity_damage if d.source_id == entity_id]),
            'damage_taken_count': len([d for d in entity_damage if d.target_id == entity_id])
        }
