"""Система уровней и характеристик."""

import random
import math
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .attributes import AttributeManager, Attribute

logger = logging.getLogger(__name__)


class AttributeType(Enum):
    """Типы характеристик"""
    STRENGTH = "strength"      # Сила - влияет на физический урон
    DEXTERITY = "dexterity"    # Ловкость - влияет на скорость атаки и критический шанс
    INTELLIGENCE = "intelligence"  # Интеллект - влияет на магический урон и ману
    VITALITY = "vitality"      # Жизненная сила - влияет на здоровье
    ENDURANCE = "endurance"    # Выносливость - влияет на выносливость и защиту
    FAITH = "faith"            # Вера - влияет на священную магию и сопротивление
    LUCK = "luck"              # Удача - влияет на критические удары и редкие находки


@dataclass
class AttributeBonus:
    """Бонус к характеристике"""
    value: float
    source: str  # Источник бонуса (экипировка, эффект, уровень)
    duration: Optional[float] = None  # Длительность в секундах, None = постоянный


@dataclass
class LevelRequirement:
    """Требования для уровня"""
    level: int
    experience: int
    attribute_points: int
    skill_points: int


class LevelingSystem:
    """Система прокачки сущностей"""
    
    def __init__(self, entity):
        self.entity = entity
        self.level = 1
        self.experience = 0
        self.experience_to_next = self._calculate_exp_requirement(2)
        
        # Очки характеристик и умений
        self.attribute_points = 0
        self.skill_points = 0
        
        # Базовые характеристики
        self.base_attributes = {
            AttributeType.STRENGTH: 10,
            AttributeType.DEXTERITY: 10,
            AttributeType.INTELLIGENCE: 10,
            AttributeType.VITALITY: 10,
            AttributeType.ENDURANCE: 10,
            AttributeType.FAITH: 10,
            AttributeType.LUCK: 10
        }
        
        # Текущие значения характеристик (включая бонусы)
        self.attributes = {attr: self.base_attributes[attr] for attr in AttributeType}
        
        # Бонусы к характеристикам
        self.attribute_bonuses: Dict[AttributeType, List[AttributeBonus]] = {
            attr: [] for attr in AttributeType
        }
        
        # Модификаторы характеристик
        self.attribute_modifiers = {
            AttributeType.STRENGTH: 1.0,
            AttributeType.DEXTERITY: 1.0,
            AttributeType.INTELLIGENCE: 1.0,
            AttributeType.VITALITY: 1.0,
            AttributeType.ENDURANCE: 1.0,
            AttributeType.FAITH: 1.0,
            AttributeType.LUCK: 1.0
        }
        
        # История прокачки
        self.leveling_history = []
        
        # Настройки прокачки
        self.leveling_config = {
            'exp_scaling': 1.2,  # Множитель опыта для следующего уровня
            'attribute_points_per_level': 5,  # Очков характеристик за уровень
            'skill_points_per_level': 2,  # Очков умений за уровень
            'max_level': 100,  # Максимальный уровень
            'bonus_levels': [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]  # Уровни с бонусами
        }
    
    def gain_experience(self, amount: int) -> bool:
        """Получить опыт и проверить повышение уровня"""
        self.experience += amount
        leveled_up = False
        
        # Проверяем повышение уровня
        while self.experience >= self.experience_to_next and self.level < self.leveling_config['max_level']:
            self._level_up()
            leveled_up = True
        
        return leveled_up
    
    def _level_up(self):
        """Повысить уровень"""
        old_level = self.level
        self.level += 1
        
        # Очки характеристик
        base_points = self.leveling_config['attribute_points_per_level']
        bonus_points = 0
        
        # Бонусные очки на определенных уровнях
        if self.level in self.leveling_config['bonus_levels']:
            bonus_points = 3
        
        self.attribute_points += base_points + bonus_points
        
        # Очки умений
        self.skill_points += self.leveling_config['skill_points_per_level']
        
        # Обновляем требования к следующему уровню
        self.experience_to_next = self._calculate_exp_requirement(self.level + 1)
        
        # Записываем в историю
        self.leveling_history.append({
            'level': self.level,
            'experience': self.experience,
            'attribute_points': self.attribute_points,
            'skill_points': self.skill_points,
            'timestamp': time.time()
        })
        
        # Уведомляем сущность о повышении уровня
        if hasattr(self.entity, 'on_level_up'):
            self.entity.on_level_up(old_level, self.level)
        
        logger.info(f"Уровень повышен! {old_level} → {self.level}")
    
    def _calculate_exp_requirement(self, level: int) -> int:
        """Рассчитать требуемый опыт для уровня"""
        if level <= 1:
            return 0
        
        # Формула: базовый опыт * (множитель ^ (уровень - 1))
        base_exp = 100
        scaling = self.leveling_config['exp_scaling']
        return int(base_exp * (scaling ** (level - 1)))
    
    def invest_attribute_point(self, attribute: AttributeType, amount: int = 1) -> bool:
        """Инвестировать очки в характеристику"""
        if self.attribute_points < amount:
            return False
        
        if attribute not in self.base_attributes:
            return False
        
        self.base_attributes[attribute] += amount
        self.attribute_points -= amount
        
        # Обновляем текущие значения
        self._recalculate_attributes()
        
        logger.info(f"Характеристика {attribute.value} увеличена на {amount}")
        return True
    
    def add_attribute_bonus(self, attribute: AttributeType, bonus: AttributeBonus):
        """Добавить бонус к характеристике"""
        if attribute not in self.attribute_bonuses:
            return
        
        self.attribute_bonuses[attribute].append(bonus)
        self._recalculate_attributes()
    
    def remove_attribute_bonus(self, attribute: AttributeType, source: str):
        """Убрать бонус к характеристике"""
        if attribute not in self.attribute_bonuses:
            return
        
        # Убираем все бонусы от указанного источника
        self.attribute_bonuses[attribute] = [
            bonus for bonus in self.attribute_bonuses[attribute]
            if bonus.source != source
        ]
        
        self._recalculate_attributes()
    
    def _recalculate_attributes(self):
        """Пересчитать текущие значения характеристик"""
        for attr in AttributeType:
            base_value = self.base_attributes[attr]
            bonus_value = sum(bonus.value for bonus in self.attribute_bonuses[attr])
            modifier = self.attribute_modifiers[attr]
            
            self.attributes[attr] = (base_value + bonus_value) * modifier
    
    def get_attribute_value(self, attribute: AttributeType) -> float:
        """Получить текущее значение характеристики"""
        return self.attributes.get(attribute, 0.0)
    
    def get_base_attribute_value(self, attribute: AttributeType) -> int:
        """Получить базовое значение характеристики"""
        return self.base_attributes.get(attribute, 0)
    
    def get_attribute_bonus(self, attribute: AttributeType) -> float:
        """Получить суммарный бонус к характеристике"""
        return sum(bonus.value for bonus in self.attribute_bonuses.get(attribute, []))
    
    def calculate_derived_stats(self) -> Dict[str, float]:
        """Рассчитать производные характеристики на основе базовых"""
        strength = self.get_attribute_value(AttributeType.STRENGTH)
        dexterity = self.get_attribute_value(AttributeType.DEXTERITY)
        intelligence = self.get_attribute_value(AttributeType.INTELLIGENCE)
        vitality = self.get_attribute_value(AttributeType.VITALITY)
        endurance = self.get_attribute_value(AttributeType.ENDURANCE)
        faith = self.get_attribute_value(AttributeType.FAITH)
        luck = self.get_attribute_value(AttributeType.LUCK)
        
        return {
            'health': 100 + vitality * 10 + endurance * 5,
            'max_health': 100 + vitality * 10 + endurance * 5,
            'mana': 50 + intelligence * 8 + faith * 5,
            'max_mana': 50 + intelligence * 8 + faith * 5,
            'stamina': 100 + endurance * 8 + vitality * 3,
            'max_stamina': 100 + endurance * 8 + vitality * 3,
            'damage_output': 10 + strength * 2 + dexterity * 1.5,
            'defense': 5 + endurance * 1.5 + vitality * 1.0,
            'movement_speed': 100.0 + dexterity * 2.0,
            'attack_speed': 1.0 + dexterity * 0.02,
            'critical_chance': 0.05 + luck * 0.01 + dexterity * 0.005,
            'critical_multiplier': 1.5 + luck * 0.02,
            'magic_power': intelligence * 3 + faith * 2,
            'magic_resistance': faith * 1.5 + intelligence * 1.0,
            'all_resist': luck * 0.5,
            'physical_resist': endurance * 0.8 + vitality * 0.5
        }
    
    def get_leveling_progress(self) -> Dict[str, Any]:
        """Получить прогресс прокачки"""
        return {
            'level': self.level,
            'experience': self.experience,
            'experience_to_next': self.experience_to_next,
            'progress_percent': (self.experience / self.experience_to_next) * 100 if self.experience_to_next > 0 else 100,
            'attribute_points': self.attribute_points,
            'skill_points': self.skill_points,
            'max_level': self.leveling_config['max_level']
        }
    
    def get_attribute_summary(self) -> Dict[str, Any]:
        """Получить сводку по характеристикам"""
        summary = {}
        for attr in AttributeType:
            base = self.get_base_attribute_value(attr)
            bonus = self.get_attribute_bonus(attr)
            total = self.get_attribute_value(attr)
            
            summary[attr.value] = {
                'base': base,
                'bonus': bonus,
                'total': total,
                'modifier': self.attribute_modifiers[attr]
            }
        
        return summary
    
    def reset_attributes(self, cost: int = 0) -> bool:
        """Сбросить характеристики (за определенную плату)"""
        if cost > 0 and hasattr(self.entity, 'currency') and self.entity.currency < cost:
            return False
        
        # Возвращаем очки характеристик
        total_invested = sum(self.base_attributes.values()) - sum(
            self.base_attributes[attr] for attr in AttributeType
        )
        self.attribute_points += total_invested
        
        # Сбрасываем к базовым значениям
        for attr in AttributeType:
            self.base_attributes[attr] = 10
        
        # Убираем все бонусы
        for attr in AttributeType:
            self.attribute_bonuses[attr].clear()
        
        # Пересчитываем
        self._recalculate_attributes()
        
        if cost > 0 and hasattr(self.entity, 'currency'):
            self.entity.currency -= cost
        
        logger.info("Характеристики сброшены")
        return True
    
    def update(self, delta_time: float):
        """Обновление системы прокачки"""
        # Убираем истекшие бонусы
        for attr in AttributeType:
            if attr in self.attribute_bonuses:
                expired_bonuses = [
                    bonus for bonus in self.attribute_bonuses[attr]
                    if bonus.duration is not None and bonus.duration <= 0
                ]
                
                for bonus in expired_bonuses:
                    self.attribute_bonuses[attr].remove(bonus)
                
                # Уменьшаем время действия оставшихся бонусов
                for bonus in self.attribute_bonuses[attr]:
                    if bonus.duration is not None:
                        bonus.duration -= delta_time
        
        # Пересчитываем характеристики если были изменения
        self._recalculate_attributes()
    
    def save_state(self) -> Dict[str, Any]:
        """Сохранить состояние системы прокачки"""
        return {
            'level': self.level,
            'experience': self.experience,
            'experience_to_next': self.experience_to_next,
            'attribute_points': self.attribute_points,
            'skill_points': self.skill_points,
            'base_attributes': {attr.value: value for attr, value in self.base_attributes.items()},
            'leveling_history': self.leveling_history
        }
    
    def load_state(self, state: Dict[str, Any]):
        """Загрузить состояние системы прокачки"""
        self.level = state.get('level', 1)
        self.experience = state.get('experience', 0)
        self.experience_to_next = state.get('experience_to_next', self._calculate_exp_requirement(2))
        self.attribute_points = state.get('attribute_points', 0)
        self.skill_points = state.get('skill_points', 0)
        
        # Загружаем базовые характеристики
        base_attrs = state.get('base_attributes', {})
        for attr_name, value in base_attrs.items():
            try:
                attr_type = AttributeType(attr_name)
                self.base_attributes[attr_type] = value
            except ValueError:
                continue
        
        # Загружаем историю
        self.leveling_history = state.get('leveling_history', [])
        
        # Пересчитываем
        self._recalculate_attributes()


# Импорт time для timestamp
import time
