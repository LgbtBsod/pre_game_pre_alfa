#!/usr/bin/env python3
"""
Entity Stats System - Система характеристик игровых сущностей
"""

import logging
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import time

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Типы игровых сущностей"""
    PLAYER = "player"
    ENEMY = "enemy"
    BOSS = "boss"
    NPC = "npc"

class StatType(Enum):
    """Типы характеристик"""
    # Основные характеристики
    STRENGTH = "strength"           # Сила - влияет на физический урон и перенос веса
    AGILITY = "agility"            # Ловкость - влияет на скорость, точность и уклонение
    INTELLIGENCE = "intelligence"  # Интеллект - влияет на магический урон и ману
    VITALITY = "vitality"          # Жизнеспособность - влияет на здоровье и регенерацию
    WISDOM = "wisdom"              # Мудрость - влияет на магическую защиту и регенерацию маны
    CHARISMA = "charisma"          # Харизма - влияет на торговлю и социальные взаимодействия
    LUCK = "luck"                  # Удача - влияет на шанс критического удара и уклонения
    ENDURANCE = "endurance"        # Выносливость - влияет на переносимый вес и скорость
    PERCEPTION = "perception"      # Восприятие - влияет на обнаружение и реакцию на окружение
    WILLPOWER = "willpower"        # Воля - влияет на сопротивление и регенерацию маны
    STEALTH = "stealth"            # Скрытность - влияет на скрытность и обнаружение
    TRICKERY = "trickery"          # Хитрость - влияет на хитрость и обман
    DEXTERITY = "dexterity"        # Ловкость - влияет на скорость, точность и уклонение
    CONSTITUTION = "constitution"  # Конституция - влияет на здоровье и регенерацию
    PIRERCING = "piercing"          # Пробивание - влияет на пробивание брони
    
    # Боевые характеристики
    ATTACK = "attack"              # Атака - базовый физический урон
    DEFENSE = "defense"            # Защита - снижает получаемый урон
    CRITICAL_CHANCE = "critical_chance"  # Шанс критического удара
    CRITICAL_DAMAGE = "critical_damage"  # Множитель критического урона
    DODGE_CHANCE = "dodge_chance"  # Шанс уклонения
    BLOCK_CHANCE = "block_chance"  # Шанс блока
    BREAK_DAMAGE = "break_damage"  # Урон при снятии endurance
    BREAK_EFFECTIVENESS = "break_effectiveness"  # Эффективность уменьшения ednurance
    ACURACY = "accuracy"          # Точность - влияет на точность атаки
    RESISTANCE_EFFECT = "resistance_effect"      # Сопротивление эффектам - влияет на сопротивление эффектам
    RESISTANCE_MAGIC = "resistance_magic"  # Сопротивление магии - влияет на сопротивление магическому урону
    RESISTANCE_PHYSICAL = "resistance_physical"  # Сопротивление физическому урону - влияет на сопротивление физическому урону
    RESISTANCE_POISON = "resistance_poison"  # Сопротивление яду - влияет на сопротивление яду
    RESISTANCE_DARK = "resistance_dark"  # Сопротивление тьме - влияет на сопротивление тьме
    RESISTANCE_LIGHTNING = "resistance_lightning"  # Сопротивление молнии - влияет на сопротивление молнии
    RESISTANCE_FIRE = "resistance_fire"  # Сопротивление огню - влияет на сопротивление огню
    RESISTANCE_ICE = "resistance_ice"  # Сопротивление льду - влияет на сопротивление льду
    RESISTANCE_WATER = "resistance_water"  # Сопротивление воде - влияет на сопротивление воде
    RESISTANCE_WIND = "resistance_wind"  # Сопротивление ветру - влияет на сопротивление ветру
    RESISTANCE_EARTH = "resistance_earth"  # Сопротивление земле - влияет на сопротивление земле
    RESISTANCE_ACID = "resistance_acid"  # Сопротивление кислоте - влияет на сопротивление кислоте
    RESISTANCE_RADIATION = "resistance_radiation"  # Сопротивление радиации - влияет на сопротивление радиации
    RESISTANCE_RADIOACTIVE = "resistance_radioactive"  # Сопротивление радиоактивности - влияет на сопротивление радиоактивности
    FIRE_RES_PENETRATION = "fire_res_penetration"  # Сопротивление огню - влияет на сопротивление огню
    ICE_RES_PENETRATION = "ice_res_penetration"  # Сопротивление льду - влияет на сопротивление льду
    POISON_RES_PENETRATION = "poison_res_penetration"  # Сопротивление яду - влияет на сопротивление яду
    DARK_RES_PENETRATION = "dark_res_penetration"  # Сопротивление тьме - влияет на сопротивление тьме
    LIGHTNING_RES_PENETRATION = "lightning_res_penetration"  # Сопротивление молнии - влияет на сопротивление молнии
    WATER_RES_PENETRATION = "water_res_penetration"  # Сопротивление воде - влияет на сопротивление воде
    WIND_RES_PENETRATION = "wind_res_penetration"  # Сопротивление ветру - влияет на сопротивление ветру
    EARTH_RES_PENETRATION = "earth_res_penetration"  # Сопротивление земле - влияет на сопротивление земле
    ACID_RES_PENETRATION = "acid_res_penetration"  # Сопротивление кислоте - влияет на сопротивление кислоте
    RADIATION_RES_PENETRATION = "radiation_res_penetration"  # Сопротивление радиации - влияет на сопротивление радиации
    RADIOACTIVE_RES_PENETRATION = "radioactive_res_penetration"  # Сопротивление радиоактивности - влияет на сопротивление радиоактивности
    FIRE_DAMAGE_PENETRATION = "fire_damage_penetration"  # Пробивание огнем - влияет на пробивание огнем
    ICE_DAMAGE_PENETRATION = "ice_damage_penetration"  # Пробивание льдом - влияет на пробивание льдом
    POISON_DAMAGE_PENETRATION = "poison_damage_penetration"  # Пробивание ядом - влияет на пробивание ядом
    DARK_DAMAGE_PENETRATION = "dark_damage_penetration"  # Пробивание тьмой - влияет на пробивание тьмой
    LIGHTNING_DAMAGE_PENETRATION = "lightning_damage_penetration"  # Пробивание молнией - влияет на пробивание молнией
    WATER_DAMAGE_PENETRATION = "water_damage_penetration"  # Пробивание водой - влияет на пробивание водой
    WIND_DAMAGE_PENETRATION = "wind_damage_penetration"  # Пробивание ветром - влияет на пробивание ветром
    EARTH_DAMAGE_PENETRATION = "earth_damage_penetration"  # Пробивание землей - влияет на пробивание землей
    ACID_DAMAGE_PENETRATION = "acid_damage_penetration"  # Пробивание кислотой - влияет на пробивание кислотой
    RADIATION_DAMAGE_PENETRATION = "radiation_damage_penetration"  # Пробивание радиацией - влияет на пробивание радиацией
    RADIOACTIVE_DAMAGE_PENETRATION = "radioactive_damage_penetration"  # Пробивание радиоактивностью - влияет на пробивание радиоактивностью
    FIRE_DAMAGE_BOOST  = "fire_damage_boost"  # Усиление огнем - влияет на усиление огнем
    ICE_DAMAGE_BOOST = "ice_damage_boost"  # Усиление льдом - влияет на усиление льдом
    POISON_DAMAGE_BOOST = "poison_damage_boost"  # Усиление ядом - влияет на усиление ядом
    DARK_DAMAGE_BOOST = "dark_damage_boost"  # Усиление тьмой - влияет на усиление тьмой
    LIGHTNING_DAMAGE_BOOST = "lightning_damage_boost"  # Усиление молнией - влияет на усиление молнией
    WATER_DAMAGE_BOOST = "water_damage_boost"  # Усиление водой - влияет на усиление водой
    WIND_DAMAGE_BOOST = "wind_damage_boost"  # Усиление ветром - влияет на усиление ветром
    EARTH_DAMAGE_BOOST = "earth_damage_boost"  # Усиление землей - влияет на усиление землей
    ACID_DAMAGE_BOOST = "acid_damage_boost"  # Усиление кислотой - влияет на усиление кислотой
    RADIATION_DAMAGE_BOOST = "radiation_damage_boost"  # Усиление радиацией - влияет на усиление радиацией
    RADIOACTIVE_DAMAGE_BOOST = "radioactive_damage_boost"  # Усиление радиоактивностью - влияет на усиление радиоактивностью



    # Вторичные характеристики
    HEALTH = "health"              # Здоровье
    MANA = "mana"                  # Мана
    STAMINA = "stamina"            # Выносливость
    HEALTH_REGEN = "health_regen"  # Регенерация здоровья
    MANA_REGEN = "mana_regen"      # Регенерация маны
    STAMINA_REGEN = "stamina_regen"  # Регенерация выносливости
    SKILL_RECOVERY = "skill_recovery"  # Восстановление навыков
    SKILL_RECOVERY_SPEED = "skill_recovery_speed"  # Скорость восстановления навыков
    SKILL_RECOVERY_EFFECT = "skill_recovery_effect"  # Эффект восстановления навыков
    SKILL_RECOVERY_EFFECT_DURATION = "skill_recovery_effect_duration"  # Длительность эффекта восстановления навыков
    SKILL_RECOVERY_EFFECT_DURATION_SPEED = "skill_recovery_effect_duration_speed"  # Скорость длительности эффекта восстановления навыков
    SKILL_RECOVERY_EFFECT_DURATION_SPEED_EFFECT = "skill_recovery_effect_duration_speed_effect"  # Эффект скорости длительности эффекта восстановления навыков
    SKILL_RECOVERY_EFFECT_DURATION_SPEED_EFFECT_DURATION = "skill_recovery_effect_duration_speed_effect_duration"  # Длительность эффекта скорости длительности эффекта восстановления навыков
    EFFECT_DURATION = "effect_duration"  # Длительность эффекта

@dataclass
class BaseStats:
    """Базовые характеристики сущности"""
    # Основные характеристики
    strength: int = 10
    agility: int = 10
    intelligence: int = 10
    vitality: int = 10
    wisdom: int = 10
    charisma: int = 10
    endurance: int = 1000
    
    # Боевые характеристики
    attack: int = 15
    defense: int = 8
    critical_chance: float = 0.05
    critical_damage: float = 1.5
    dodge_chance: float = 0.1
    block_chance: float = 0.15
    
    # Вторичные характеристики
    health: int = 100
    mana: int = 50
    stamina: int = 100
    health_regen: float = 1.0
    mana_regen: float = 0.5
    stamina_regen: float = 2.0

@dataclass
class StatModifier:
    """Модификатор характеристики"""
    stat_type: StatType
    value: Union[int, float]
    modifier_type: str  # "flat", "percent", "multiplier"
    source: str  # Источник модификатора
    duration: Optional[float] = None  # Длительность в секундах, None = постоянный
    expires_at: Optional[float] = None  # Время истечения

@dataclass
class EntityStats:
    """Полные характеристики сущности"""
    entity_id: str
    entity_type: EntityType
    level: int = 1
    experience: int = 0
    experience_to_next: int = 100
    
    # Базовые характеристики
    base_stats: BaseStats = field(default_factory=BaseStats)
    
    # Текущие значения
    current_health: int = 100
    current_mana: int = 50
    current_stamina: int = 100
    
    # Модификаторы
    stat_modifiers: List[StatModifier] = field(default_factory=list)
    
    # Очки характеристик для распределения
    available_stat_points: int = 0
    
    # Ограничения характеристик
    max_stat_value: int = 100
    min_stat_value: int = 1
    
    def __post_init__(self):
        """Инициализация после создания"""
        self._calculate_derived_stats()
        self._update_current_values()
    
    def _calculate_derived_stats(self):
        """Расчет производных характеристик на основе базовых"""
        # Здоровье = базовая жизнеспособность * 10 + сила * 2
        self.base_stats.health = self.base_stats.vitality * 10 + self.base_stats.strength * 2
        
        # Мана = базовая мудрость * 5 + интеллект * 3
        self.base_stats.mana = self.base_stats.wisdom * 5 + self.base_stats.intelligence * 3
        
        # Выносливость = базовая ловкость * 8 + жизнеспособность * 2
        self.base_stats.stamina = self.base_stats.agility * 8 + self.base_stats.vitality * 2
        
        # Атака = базовая сила * 1.5 + ловкость * 0.5
        self.base_stats.attack = int(self.base_stats.strength * 1.5 + self.base_stats.agility * 0.5)
        
        # Защита = базовая жизнеспособность * 0.8 + ловкость * 0.3
        self.base_stats.defense = int(self.base_stats.vitality * 0.8 + self.base_stats.agility * 0.3)
        
        # Регенерация здоровья = базовая жизнеспособность * 0.1
        self.base_stats.health_regen = self.base_stats.vitality * 0.1
        
        # Регенерация маны = базовая мудрость * 0.05
        self.base_stats.mana_regen = self.base_stats.wisdom * 0.05
        
        # Регенерация выносливости = базовая ловкость * 0.2
        self.base_stats.stamina_regen = self.base_stats.agility * 0.2
    
    def _update_current_values(self):
        """Обновление текущих значений"""
        self.current_health = min(self.current_health, self.base_stats.health)
        self.current_mana = min(self.current_mana, self.base_stats.mana)
        self.current_stamina = min(self.current_stamina, self.base_stats.stamina)
    
    def get_stat_value(self, stat_type: StatType) -> Union[int, float]:
        """Получение значения характеристики с учетом модификаторов"""
        base_value = getattr(self.base_stats, stat_type.value, 0)
        total_value = base_value
        
        # Применяем модификаторы
        for modifier in self.stat_modifiers:
            if modifier.stat_type == stat_type:
                if modifier.modifier_type == "flat":
                    total_value += modifier.value
                elif modifier.modifier_type == "percent":
                    total_value += base_value * (modifier.value / 100)
                elif modifier.modifier_type == "multiplier":
                    total_value *= modifier.value
        
        # Ограничиваем значения
        if isinstance(total_value, int):
            return max(self.min_stat_value, min(self.max_stat_value, total_value))
        else:
            return max(self.min_stat_value, min(self.max_stat_value, total_value))
    
    def add_stat_modifier(self, modifier: StatModifier):
        """Добавление модификатора характеристики"""
        self.stat_modifiers.append(modifier)
        self._update_current_values()
        logger.debug(f"Добавлен модификатор {modifier.stat_type.value} для {self.entity_id}")
    
    def remove_stat_modifier(self, source: str):
        """Удаление модификаторов по источнику"""
        self.stat_modifiers = [m for m in self.stat_modifiers if m.source != source]
        self._update_current_values()
        logger.debug(f"Удалены модификаторы от {source} для {self.entity_id}")
    
    def gain_experience(self, exp_amount: int) -> bool:
        """Получение опыта и проверка повышения уровня"""
        self.experience += exp_amount
        
        if self.experience >= self.experience_to_next:
            self._level_up()
            return True
        return False
    
    def _level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.experience -= self.experience_to_next
        
        # Рассчитываем опыт для следующего уровня
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        # Даем очки характеристик в зависимости от типа сущности
        if self.entity_type == EntityType.PLAYER:
            self.available_stat_points += 10
        elif self.entity_type == EntityType.ENEMY:
            self.available_stat_points += 5
        elif self.entity_type == EntityType.BOSS:
            self.available_stat_points += 10
        
        # Автоматическое распределение очков для врагов и боссов
        if self.entity_type in [EntityType.ENEMY, EntityType.BOSS]:
            self._auto_distribute_stat_points()
        
        logger.info(f"{self.entity_id} достиг уровня {self.level}")
    
    def _auto_distribute_stat_points(self):
        """Автоматическое распределение очков характеристик"""
        if self.available_stat_points <= 0:
            return
        
        # Определяем количество очков для каждой характеристики
        if self.entity_type == EntityType.ENEMY:
            points_per_stat = 5
        elif self.entity_type == EntityType.BOSS:
            points_per_stat = 10
        else:
            return
        
        # Основные характеристики для распределения
        primary_stats = [
            StatType.STRENGTH, StatType.AGILITY, StatType.INTELLIGENCE,
            StatType.VITALITY, StatType.WISDOM, StatType.CHARISMA
        ]
        
        for stat_type in primary_stats:
            current_value = getattr(self.base_stats, stat_type.value)
            new_value = min(self.max_stat_value, current_value + points_per_stat)
            setattr(self.base_stats, stat_type.value, new_value)
        
        # Пересчитываем производные характеристики
        self._calculate_derived_stats()
        self._update_current_values()
        
        self.available_stat_points = 0
        logger.debug(f"Автоматически распределены очки характеристик для {self.entity_id}")
    
    def distribute_stat_point(self, stat_type: StatType) -> bool:
        """Распределение очка характеристики (для игрока)"""
        if self.available_stat_points <= 0:
            logger.warning(f"Нет доступных очков характеристик для {self.entity_id}")
            return False
        
        current_value = getattr(self.base_stats, stat_type.value)
        if current_value >= self.max_stat_value:
            logger.warning(f"Характеристика {stat_type.value} уже максимальна для {self.entity_id}")
            return False
        
        # Увеличиваем характеристику
        setattr(self.base_stats, stat_type.value, current_value + 1)
        self.available_stat_points -= 1
        
        # Пересчитываем производные характеристики
        self._calculate_derived_stats()
        self._update_current_values()
        
        logger.info(f"{self.entity_id} увеличил {stat_type.value} до {current_value + 1}")
        return True
    
    def take_damage(self, damage: int, damage_type: str = "physical") -> int:
        """Получение урона"""
        # Применяем защиту
        defense = self.get_stat_value(StatType.DEFENSE)
        actual_damage = max(1, damage - defense)
        
        self.current_health = max(0, self.current_health - actual_damage)
        
        # Проверяем рейдж режим для боссов (при 10% HP)
        if (self.entity_type == EntityType.BOSS and 
            self.current_health <= self.base_stats.health * 0.1):
            self._enter_rage_mode()
        
        logger.debug(f"{self.entity_id} получил {actual_damage} урона, HP: {self.current_health}")
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Восстановление здоровья"""
        old_health = self.current_health
        self.current_health = min(self.base_stats.health, self.current_health + amount)
        actual_heal = self.current_health - old_health
        
        logger.debug(f"{self.entity_id} восстановил {actual_heal} HP, HP: {self.current_health}")
        return actual_heal
    
    def use_mana(self, amount: int) -> bool:
        """Использование маны"""
        if self.current_mana >= amount:
            self.current_mana -= amount
            logger.debug(f"{self.entity_id} использовал {amount} маны, MP: {self.current_mana}")
            return True
        return False
    
    def restore_mana(self, amount: int) -> int:
        """Восстановление маны"""
        old_mana = self.current_mana
        self.current_mana = min(self.base_stats.mana, self.current_mana + amount)
        actual_restore = self.current_mana - old_mana
        
        logger.debug(f"{self.entity_id} восстановил {actual_restore} MP, MP: {self.current_mana}")
        return actual_restore
    
    def _enter_rage_mode(self):
        """Вход в режим ярости для боссов"""
        if self.entity_type == EntityType.BOSS:
            # Увеличиваем атаку и скорость
            rage_modifier = StatModifier(
                stat_type=StatType.ATTACK,
                value=1.5,
                modifier_type="multiplier",
                source="rage_mode",
                duration=60.0  # 1 минута
            )
            self.add_stat_modifier(rage_modifier)
            
            speed_modifier = StatModifier(
                stat_type=StatType.AGILITY,
                value=1.3,
                modifier_type="multiplier",
                source="rage_mode",
                duration=60.0
            )
            self.add_stat_modifier(speed_modifier)
            
            logger.info(f"{self.entity_id} входит в режим ярости!")
    
    def update(self, delta_time: float):
        """Обновление характеристик"""
        # Регенерация
        health_regen = self.get_stat_value(StatType.HEALTH_REGEN) * delta_time
        if health_regen > 0:
            self.heal(int(health_regen))
        
        mana_regen = self.get_stat_value(StatType.MANA_REGEN) * delta_time
        if mana_regen > 0:
            self.restore_mana(int(mana_regen))
        
        # Очистка истекших модификаторов
        current_time = time.time()
        self.stat_modifiers = [
            m for m in self.stat_modifiers 
            if m.expires_at is None or m.expires_at > current_time
        ]
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Получение сводки характеристик"""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type.value,
            'level': self.level,
            'experience': self.experience,
            'experience_to_next': self.experience_to_next,
            'current_health': self.current_health,
            'max_health': self.base_stats.health,
            'current_mana': self.current_mana,
            'max_mana': self.base_stats.mana,
            'current_stamina': self.current_stamina,
            'max_stamina': self.base_stats.stamina,
            'available_stat_points': self.available_stat_points,
            'base_stats': {
                'strength': self.base_stats.strength,
                'agility': self.base_stats.agility,
                'intelligence': self.base_stats.intelligence,
                'vitality': self.base_stats.vitality,
                'wisdom': self.base_stats.wisdom,
                'charisma': self.base_stats.charisma
            },
            'combat_stats': {
                'attack': self.get_stat_value(StatType.ATTACK),
                'defense': self.get_stat_value(StatType.DEFENSE),
                'critical_chance': self.get_stat_value(StatType.CRITICAL_CHANCE),
                'critical_damage': self.get_stat_value(StatType.CRITICAL_DAMAGE),
                'dodge_chance': self.get_stat_value(StatType.DODGE_CHANCE),
                'block_chance': self.get_stat_value(StatType.BLOCK_CHANCE)
            }
        }
    
    def is_alive(self) -> bool:
        """Проверка, жива ли сущность"""
        return self.current_health > 0
    
    def get_health_percentage(self) -> float:
        """Получение процента здоровья"""
        if self.base_stats.health <= 0:
            return 0.0
        return (self.current_health / self.base_stats.health) * 100.0
    
    def get_mana_percentage(self) -> float:
        """Получение процента маны"""
        if self.base_stats.mana <= 0:
            return 0.0
        return (self.current_mana / self.base_stats.mana) * 100.0
