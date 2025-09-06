#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class BaseAttribute(Enum):
    """Базовые атрибуты"""
    STRENGTH = "strength"           # Сила - влияет на физический урон, переносимый вес
    AGILITY = "agility"            # Ловкость - влияет на скорость атаки, уклонение, критический удар
    INTELLIGENCE = "intelligence"   # Интеллект - влияет на магический урон, ману, регенерацию маны
    VITALITY = "vitality"          # Жизненная сила - влияет на здоровье, регенерацию здоровья
    WISDOM = "wisdom"              # Мудрость - влияет на сопротивление магии, регенерацию маны
    CHARISMA = "charisma"          # Харизма - влияет на торговлю, дипломатию, лидерство
    LUCK = "luck"                  # Удача - влияет на критические удары, редкие находки
    ENDURANCE = "endurance"        # Выносливость - влияет на стамину, сопротивление усталости

class DerivedStat(Enum):
    """Производные характеристики"""
    HEALTH = "health"
    MANA = "mana"
    STAMINA = "stamina"
    PHYSICAL_DAMAGE = "physical_damage"
    MAGICAL_DAMAGE = "magical_damage"
    DEFENSE = "defense"
    ATTACK_SPEED = "attack_speed"
    HEALTH_REGEN = "health_regen"
    MANA_REGEN = "mana_regen"
    STAMINA_REGEN = "stamina_regen"
    CRITICAL_CHANCE = "critical_chance"
    CRITICAL_DAMAGE = "critical_damage"
    DODGE_CHANCE = "dodge_chance"
    MAGIC_RESISTANCE = "magic_resistance"
    MAX_WEIGHT = "max_weight"
    MOVEMENT_SPEED = "movement_speed"

@dataclass
class AttributeModifier:
    """Модификатор атрибута"""
    modifier_id: str
    attribute: BaseAttribute
    value: float
    source: str  # Источник модификатора (предмет, эффект, и т.д.)
    duration: float = -1.0  # -1 для постоянных модификаторов
    start_time: float = field(default_factory=time.time)
    is_percentage: bool = False  # Процентный или абсолютный модификатор

@dataclass
class StatModifier:
    """Модификатор характеристики"""
    modifier_id: str
    stat: DerivedStat
    value: float
    source: str
    duration: float = -1.0
    start_time: float = field(default_factory=time.time)
    is_percentage: bool = False

@dataclass
class AttributeSet:
    """Набор атрибутов"""
    strength: float = 10.0
    agility: float = 10.0
    intelligence: float = 10.0
    vitality: float = 10.0
    wisdom: float = 10.0
    charisma: float = 10.0
    luck: float = 10.0
    endurance: float = 10.0
    
    def to_dict(self) -> Dict[str, float]:
        """Преобразование в словарь"""
        return {
            'strength': self.strength,
            'agility': self.agility,
            'intelligence': self.intelligence,
            'vitality': self.vitality,
            'wisdom': self.wisdom,
            'charisma': self.charisma,
            'luck': self.luck,
            'endurance': self.endurance
        }
    
    def from_dict(self, data: Dict[str, float]):
        """Загрузка из словаря"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class AttributeSystem:
    """Система атрибутов и производных характеристик"""
    
    def __init__(self):
        self.attribute_modifiers: Dict[str, List[AttributeModifier]] = {}
        self.stat_modifiers: Dict[str, List[StatModifier]] = {}
        self.cache: Dict[str, Dict[str, float]] = {}
        self.cache_time: Dict[str, float] = {}
        self.cache_duration = 60.0  # Кэш на 60 секунд
        
    def calculate_derived_stats(self, entity_id: str, base_attributes: AttributeSet) -> Dict[str, float]:
        """Расчет производных характеристик на основе базовых атрибутов"""
        # Проверяем кэш
        cache_key = f"{entity_id}_{hash(str(base_attributes.to_dict()))}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Получаем модифицированные атрибуты
        modified_attrs = self._apply_attribute_modifiers(entity_id, base_attributes)
        
        # Рассчитываем производные характеристики
        stats = {}
        
        # Здоровье = 50 + (Vitality * 5)
        stats[DerivedStat.HEALTH.value] = (modified_attrs.vitality * modified_attrs.strength)
        
        # Мана = 30 + (Intelligence * 3) + (Wisdom * 2)
        stats[DerivedStat.MANA.value] = 30 + (modified_attrs.intelligence * modified_attrs.wisdom )
        
        # Стамина = 40 + (Endurance * 4)
        stats[DerivedStat.STAMINA.value] = 40 + (modified_attrs.endurance * modified_attrs.vitality)
        
        # Физический урон = Strength * 2
        stats[DerivedStat.PHYSICAL_DAMAGE.value] = modified_attrs.strength * 2
        
        # Магический урон = Intelligence * 2.5
        stats[DerivedStat.MAGICAL_DAMAGE.value] = modified_attrs.intelligence * 2.5
        
        # Защита = (Vitality + Endurance) * 0.5
        stats[DerivedStat.DEFENSE.value] = (modified_attrs.vitality + modified_attrs.endurance) * 0.5
        
        # Скорость атаки = 1.0 + (Agility * 0.05)
        stats[DerivedStat.ATTACK_SPEED.value] = 1.0 + (modified_attrs.agility * 0.05)
        
        # Регенерация здоровья = Vitality * 0.1
        stats[DerivedStat.HEALTH_REGEN.value] = modified_attrs.vitality * 0.1
        
        # Регенерация маны = (Intelligence + Wisdom) * 0.08
        stats[DerivedStat.MANA_REGEN.value] = (modified_attrs.intelligence + modified_attrs.wisdom) * 0.08
        
        # Регенерация стамины = Endurance * 0.12
        stats[DerivedStat.STAMINA_REGEN.value] = modified_attrs.endurance * 0.12
        
        # Шанс критического удара = (Agility + Luck) * 0.5
        stats[DerivedStat.CRITICAL_CHANCE.value] = (modified_attrs.agility + modified_attrs.luck) * 0.5
        
        # Урон критического удара = 150 + (Luck * 2)
        stats[DerivedStat.CRITICAL_DAMAGE.value] = 150 + (modified_attrs.luck * 2)
        
        # Шанс уклонения = Agility * 0.8
        stats[DerivedStat.DODGE_CHANCE.value] = modified_attrs.agility * 0.8
        
        # Сопротивление магии = Wisdom * 1.5
        stats[DerivedStat.MAGIC_RESISTANCE.value] = modified_attrs.wisdom * 1.5
        
        # Максимальный вес = Strength * 10
        stats[DerivedStat.MAX_WEIGHT.value] = modified_attrs.strength * 10
        
        # Скорость движения = 5.0 + (Agility * 0.1)
        stats[DerivedStat.MOVEMENT_SPEED.value] = 5.0 + (modified_attrs.agility * 0.1)
        
        # Применяем модификаторы характеристик
        stats = self._apply_stat_modifiers(entity_id, stats)
        
        # Сохраняем в кэш
        self.cache[cache_key] = stats
        self.cache_time[cache_key] = time.time()
        
        return stats
    
    def add_attribute_modifier(self, entity_id: str, modifier: AttributeModifier):
        """Добавление модификатора атрибута"""
        if entity_id not in self.attribute_modifiers:
            self.attribute_modifiers[entity_id] = []
        self.attribute_modifiers[entity_id].append(modifier)
        self._clear_entity_cache(entity_id)
    
    def add_stat_modifier(self, entity_id: str, modifier: StatModifier):
        """Добавление модификатора характеристики"""
        if entity_id not in self.stat_modifiers:
            self.stat_modifiers[entity_id] = []
        self.stat_modifiers[entity_id].append(modifier)
        self._clear_entity_cache(entity_id)
    
    def remove_attribute_modifier(self, entity_id: str, modifier_id: str):
        """Удаление модификатора атрибута"""
        if entity_id in self.attribute_modifiers:
            self.attribute_modifiers[entity_id] = [
                m for m in self.attribute_modifiers[entity_id] 
                if m.modifier_id != modifier_id
            ]
            self._clear_entity_cache(entity_id)
    
    def remove_stat_modifier(self, entity_id: str, modifier_id: str):
        """Удаление модификатора характеристики"""
        if entity_id in self.stat_modifiers:
            self.stat_modifiers[entity_id] = [
                m for m in self.stat_modifiers[entity_id] 
                if m.modifier_id != modifier_id
            ]
            self._clear_entity_cache(entity_id)
    
    def _apply_attribute_modifiers(self, entity_id: str, base_attributes: AttributeSet) -> AttributeSet:
        """Применение модификаторов атрибутов"""
        modified = AttributeSet(
            strength=base_attributes.strength,
            agility=base_attributes.agility,
            intelligence=base_attributes.intelligence,
            vitality=base_attributes.vitality,
            wisdom=base_attributes.wisdom,
            charisma=base_attributes.charisma,
            luck=base_attributes.luck,
            endurance=base_attributes.endurance
        )
        
        if entity_id not in self.attribute_modifiers:
            return modified
        
        current_time = time.time()
        for modifier in self.attribute_modifiers[entity_id]:
            # Проверяем, не истек ли модификатор
            if modifier.duration > 0 and (current_time - modifier.start_time) > modifier.duration:
                continue
            
            attr_name = modifier.attribute.value
            if hasattr(modified, attr_name):
                current_value = getattr(modified, attr_name)
                if modifier.is_percentage:
                    new_value = current_value * (1 + modifier.value / 100)
                else:
                    new_value = current_value + modifier.value
                setattr(modified, attr_name, new_value)
        
        return modified
    
    def _apply_stat_modifiers(self, entity_id: str, base_stats: Dict[str, float]) -> Dict[str, float]:
        """Применение модификаторов характеристик"""
        modified = base_stats.copy()
        
        if entity_id not in self.stat_modifiers:
            return modified
        
        current_time = time.time()
        for modifier in self.stat_modifiers[entity_id]:
            # Проверяем, не истек ли модификатор
            if modifier.duration > 0 and (current_time - modifier.start_time) > modifier.duration:
                continue
            
            stat_name = modifier.stat.value
            if stat_name in modified:
                current_value = modified[stat_name]
                if modifier.is_percentage:
                    modified[stat_name] = current_value * (1 + modifier.value / 100)
                else:
                    modified[stat_name] = current_value + modifier.value
        
        return modified
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Проверка валидности кэша"""
        if cache_key not in self.cache or cache_key not in self.cache_time:
            return False
        
        return (time.time() - self.cache_time[cache_key]) < self.cache_duration
    
    def _clear_entity_cache(self, entity_id: str):
        """Очистка кэша для сущности"""
        keys_to_remove = [key for key in self.cache.keys() if key.startswith(entity_id)]
        for key in keys_to_remove:
            self.cache.pop(key, None)
            self.cache_time.pop(key, None)
    
    def cleanup_expired_modifiers(self):
        """Очистка истекших модификаторов"""
        current_time = time.time()
        
        for entity_id in list(self.attribute_modifiers.keys()):
            self.attribute_modifiers[entity_id] = [
                m for m in self.attribute_modifiers[entity_id]
                if m.duration < 0 or (current_time - m.start_time) <= m.duration
            ]
            if not self.attribute_modifiers[entity_id]:
                del self.attribute_modifiers[entity_id]
        
        for entity_id in list(self.stat_modifiers.keys()):
            self.stat_modifiers[entity_id] = [
                m for m in self.stat_modifiers[entity_id]
                if m.duration < 0 or (current_time - m.start_time) <= m.duration
            ]
            if not self.stat_modifiers[entity_id]:
                del self.stat_modifiers[entity_id]
    
    def get_entity_stats(self, entity_id: str, base_attributes: AttributeSet) -> Dict[str, float]:
        """Получение всех характеристик сущности"""
        return self.calculate_derived_stats(entity_id, base_attributes)
