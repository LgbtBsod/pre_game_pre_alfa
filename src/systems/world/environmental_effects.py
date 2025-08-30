#!/usr/bin/env python3
"""Система экологических эффектов для игрового мира
Включает влияние погоды, времени и сезонов на геймплей"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ ЭФФЕКТОВ
class EffectType(Enum):
    """Типы экологических эффектов"""
    MOVEMENT = "movement"           # Влияние на движение
    COMBAT = "combat"               # Влияние на бой
    SURVIVAL = "survival"           # Влияние на выживание
    VISIBILITY = "visibility"       # Влияние на видимость
    RESOURCE = "resource"           # Влияние на ресурсы
    PSYCHOLOGICAL = "psychological" # Психологическое влияние

# = КАТЕГОРИИ ЭФФЕКТОВ
class EffectCategory(Enum):
    """Категории экологических эффектов"""
    WEATHER = "weather"             # Погодные эффекты
    TIME = "time"                   # Временные эффекты
    SEASONAL = "seasonal"           # Сезонные эффекты
    COMBINED = "combined"           # Комбинированные эффекты

# = НАСТРОЙКИ ЭФФЕКТОВ
@dataclass
class EnvironmentalSettings:
    """Настройки экологических эффектов"""
    effect_duration: float = 30.0  # Длительность эффекта в секундах
    intensity_decay: float = 0.1   # Скорость затухания интенсивности
    max_effects: int = 10          # Максимальное количество активных эффектов
    stacking_enabled: bool = True  # Разрешить наложение эффектов
    psychological_effects: bool = True  # Включить психологические эффекты

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class EnvironmentalEffect:
    """Экологический эффект"""
    effect_id: str
    effect_type: EffectType
    category: EffectCategory
    name: str
    description: str
    intensity: float  # 0.0 - 1.0
    duration: float
    target_type: str  # player, npc, enemy, environment
    modifiers: Dict[str, float] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0

@dataclass
class EffectCondition:
    """Условие применения эффекта"""
    weather_type: Optional[str] = None
    time_of_day: Optional[str] = None
    season: Optional[str] = None
    temperature_range: Optional[Tuple[float, float]] = None
    humidity_range: Optional[Tuple[float, float]] = None
    wind_speed_range: Optional[Tuple[float, float]] = None
    location_type: Optional[str] = None

@dataclass
class EffectStack:
    """Стек эффектов"""
    effect_type: EffectType
    effects: List[EnvironmentalEffect] = field(default_factory=list)
    total_intensity: float = 0.0
    combined_modifiers: Dict[str, float] = field(default_factory=dict)

# = СИСТЕМА ЭКОЛОГИЧЕСКИХ ЭФФЕКТОВ
class EnvironmentalEffects(BaseComponent):
    """Система экологических эффектов"""
    
    def __init__(self):
        super().__init__(
            component_id="EnvironmentalEffects",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки системы
        self.settings = EnvironmentalSettings()
        
        # Активные эффекты
        self.active_effects: Dict[str, EnvironmentalEffect] = {}
        self.effect_stacks: Dict[EffectType, EffectStack] = {}
        
        # Шаблоны эффектов
        self.effect_templates: Dict[str, Dict[str, Any]] = {}
        
        # Кэши и статистика
        self.effect_cache: Dict[str, Any] = {}
        self.effect_stats = {
            "effects_applied": 0,
            "effects_expired": 0,
            "effects_stacked": 0,
            "total_update_time": 0.0
        }
        
        # Слушатели событий
        self.effect_applied_callbacks: List[callable] = []
        self.effect_expired_callbacks: List[callable] = []
        self.effect_intensity_changed_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация системы экологических эффектов"""
        try:
            # Инициализация шаблонов эффектов
            self._initialize_effect_templates()
            
            # Инициализация стеков эффектов
            for effect_type in EffectType:
                self.effect_stacks[effect_type] = EffectStack(effect_type)
            
            self.logger.info("EnvironmentalEffects инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации EnvironmentalEffects: {e}")
            return False
    
    def _initialize_effect_templates(self):
        """Инициализация шаблонов эффектов"""
        # Погодные эффекты
        self.effect_templates["rain_movement"] = {
            "effect_type": EffectType.MOVEMENT,
            "category": EffectCategory.WEATHER,
            "name": "Скользкая дорога",
            "description": "Дождь делает дорогу скользкой, снижая скорость движения",
            "modifiers": {"movement_speed": -0.3, "slipping_chance": 0.2},
            "conditions": {"weather_type": "rain"}
        }
        
        self.effect_templates["storm_visibility"] = {
            "effect_type": EffectType.VISIBILITY,
            "category": EffectCategory.WEATHER,
            "name": "Плохая видимость",
            "description": "Буря значительно снижает видимость",
            "modifiers": {"visibility_range": -0.6, "detection_chance": -0.4},
            "conditions": {"weather_type": "storm"}
        }
        
        self.effect_templates["heat_survival"] = {
            "effect_type": EffectType.SURVIVAL,
            "category": EffectCategory.WEATHER,
            "name": "Жара",
            "description": "Высокая температура ускоряет потерю влаги",
            "modifiers": {"hydration_loss": 2.0, "heat_resistance": -0.2},
            "conditions": {"temperature_range": (30.0, 50.0)}
        }
        
        self.effect_templates["cold_survival"] = {
            "effect_type": EffectType.SURVIVAL,
            "category": EffectCategory.WEATHER,
            "name": "Холод",
            "description": "Низкая температура снижает температуру тела",
            "modifiers": {"body_temperature": -0.3, "cold_resistance": -0.2},
            "conditions": {"temperature_range": (-20.0, 5.0)}
        }
        
        # Временные эффекты
        self.effect_templates["night_visibility"] = {
            "effect_type": EffectType.VISIBILITY,
            "category": EffectCategory.TIME,
            "name": "Темнота",
            "description": "Ночная темнота снижает видимость",
            "modifiers": {"visibility_range": -0.7, "night_vision": 0.5},
            "conditions": {"time_of_day": "night"}
        }
        
        self.effect_templates["dawn_psychological"] = {
            "effect_type": EffectType.PSYCHOLOGICAL,
            "category": EffectCategory.TIME,
            "name": "Рассвет",
            "description": "Рассвет поднимает настроение и мораль",
            "modifiers": {"morale": 0.3, "stress_reduction": 0.2},
            "conditions": {"time_of_day": "dawn"}
        }
        
        # Сезонные эффекты
        self.effect_templates["spring_regeneration"] = {
            "effect_type": EffectType.SURVIVAL,
            "category": EffectCategory.SEASONAL,
            "name": "Весеннее обновление",
            "description": "Весна ускоряет регенерацию здоровья",
            "modifiers": {"health_regeneration": 1.5, "stamina_regeneration": 1.3},
            "conditions": {"season": "spring"}
        }
        
        self.effect_templates["summer_heat"] = {
            "effect_type": EffectType.SURVIVAL,
            "category": EffectCategory.SEASONAL,
            "name": "Летняя жара",
            "description": "Летняя жара увеличивает потребность в воде",
            "modifiers": {"hydration_loss": 1.8, "heat_resistance": -0.3},
            "conditions": {"season": "summer"}
        }
        
        self.effect_templates["autumn_harvest"] = {
            "effect_type": EffectType.RESOURCE,
            "category": EffectCategory.SEASONAL,
            "name": "Осенний урожай",
            "description": "Осень увеличивает урожайность",
            "modifiers": {"crop_yield": 1.4, "resource_gathering": 1.2},
            "conditions": {"season": "autumn"}
        }
        
        self.effect_templates["winter_cold"] = {
            "effect_type": EffectType.SURVIVAL,
            "category": EffectCategory.SEASONAL,
            "name": "Зимний холод",
            "description": "Зимний холод требует больше тепла",
            "modifiers": {"body_temperature": -0.4, "cold_resistance": -0.4},
            "conditions": {"season": "winter"}
        }
        
        # Комбинированные эффекты
        self.effect_templates["storm_night_terror"] = {
            "effect_type": EffectType.PSYCHOLOGICAL,
            "category": EffectCategory.COMBINED,
            "name": "Ночной ужас",
            "description": "Буря ночью вызывает страх и тревогу",
            "modifiers": {"fear": 0.6, "stress": 0.4, "courage": -0.3},
            "conditions": {"weather_type": "storm", "time_of_day": "night"}
        }
        
        self.effect_templates["winter_storm_survival"] = {
            "effect_type": EffectType.SURVIVAL,
            "category": EffectCategory.COMBINED,
            "name": "Зимняя буря",
            "description": "Зимняя буря крайне опасна для выживания",
            "modifiers": {"body_temperature": -0.6, "visibility_range": -0.8, "movement_speed": -0.5},
            "conditions": {"weather_type": "storm", "season": "winter"}
        }
    
    def apply_environmental_effect(self, template_name: str, intensity: float = 1.0, 
                                  duration: float = None, target_type: str = "player") -> Optional[str]:
        """Применение экологического эффекта"""
        if template_name not in self.effect_templates:
            self.logger.warning(f"Шаблон эффекта {template_name} не найден")
            return None
        
        template = self.effect_templates[template_name]
        
        # Создание эффекта
        effect_id = f"{template_name}_{int(time.time())}"
        effect_duration = duration or self.settings.effect_duration
        
        effect = EnvironmentalEffect(
            effect_id=effect_id,
            effect_type=template["effect_type"],
            category=template["category"],
            name=template["name"],
            description=template["description"],
            intensity=intensity,
            duration=effect_duration,
            target_type=target_type,
            modifiers=template["modifiers"].copy(),
            conditions=template.get("conditions", {}),
            expires_at=time.time() + effect_duration
        )
        
        # Применение эффекта
        self.active_effects[effect_id] = effect
        self.effect_stats["effects_applied"] += 1
        
        # Обновление стека эффектов
        self._update_effect_stack(effect)
        
        # Уведомление о применении эффекта
        self._notify_effect_applied(effect)
        
        self.logger.info(f"Применен эффект {template_name} с интенсивностью {intensity}")
        
        return effect_id
    
    def remove_effect(self, effect_id: str) -> bool:
        """Удаление эффекта"""
        if effect_id not in self.active_effects:
            return False
        
        effect = self.active_effects[effect_id]
        
        # Удаление из активных эффектов
        del self.active_effects[effect_id]
        self.effect_stats["effects_expired"] += 1
        
        # Обновление стека эффектов
        self._update_effect_stack(effect, remove=True)
        
        # Уведомление об удалении эффекта
        self._notify_effect_expired(effect)
        
        self.logger.info(f"Удален эффект {effect.name}")
        
        return True
    
    def update_effects(self, delta_time: float):
        """Обновление эффектов"""
        start_time = time.time()
        
        current_time = time.time()
        expired_effects = []
        
        # Проверка истечения эффектов
        for effect_id, effect in self.active_effects.items():
            if current_time >= effect.expires_at:
                expired_effects.append(effect_id)
            else:
                # Обновление интенсивности (затухание)
                if self.settings.intensity_decay > 0:
                    effect.intensity = max(0.0, effect.intensity - self.settings.intensity_decay * delta_time)
                    
                    if effect.intensity <= 0:
                        expired_effects.append(effect_id)
        
        # Удаление истекших эффектов
        for effect_id in expired_effects:
            self.remove_effect(effect_id)
        
        # Ограничение количества эффектов
        if len(self.active_effects) > self.settings.max_effects:
            self._cleanup_oldest_effects()
        
        self.effect_stats["total_update_time"] += time.time() - start_time
    
    def _update_effect_stack(self, effect: EnvironmentalEffect, remove: bool = False):
        """Обновление стека эффектов"""
        effect_type = effect.effect_type
        
        if effect_type not in self.effect_stacks:
            return
        
        stack = self.effect_stacks[effect_type]
        
        if remove:
            # Удаление эффекта из стека
            stack.effects = [e for e in stack.effects if e.effect_id != effect.effect_id]
        else:
            # Добавление эффекта в стек
            if self.settings.stacking_enabled:
                stack.effects.append(effect)
            else:
                # Замена существующего эффекта
                stack.effects = [effect]
        
        # Пересчет общей интенсивности и модификаторов
        self._recalculate_stack_modifiers(stack)
    
    def _recalculate_stack_modifiers(self, stack: EffectStack):
        """Пересчет модификаторов стека"""
        total_intensity = 0.0
        combined_modifiers = {}
        
        for effect in stack.effects:
            total_intensity += effect.intensity
            
            for modifier, value in effect.modifiers.items():
                if modifier not in combined_modifiers:
                    combined_modifiers[modifier] = 0.0
                combined_modifiers[modifier] += value * effect.intensity
        
        stack.total_intensity = total_intensity
        stack.combined_modifiers = combined_modifiers
        
        self.effect_stats["effects_stacked"] += 1
    
    def _cleanup_oldest_effects(self):
        """Очистка старых эффектов"""
        if len(self.active_effects) <= self.settings.max_effects:
            return
        
        # Сортировка по времени создания
        sorted_effects = sorted(
            self.active_effects.items(),
            key=lambda x: x[1].created_at
        )
        
        # Удаление старых эффектов
        effects_to_remove = len(self.active_effects) - self.settings.max_effects
        
        for i in range(effects_to_remove):
            effect_id, _ = sorted_effects[i]
            self.remove_effect(effect_id)
    
    def get_active_effects(self, target_type: str = None, effect_type: EffectType = None) -> List[EnvironmentalEffect]:
        """Получение активных эффектов"""
        effects = list(self.active_effects.values())
        
        if target_type:
            effects = [e for e in effects if e.target_type == target_type]
        
        if effect_type:
            effects = [e for e in effects if e.effect_type == effect_type]
        
        return effects
    
    def get_effect_modifiers(self, target_type: str = "player") -> Dict[str, float]:
        """Получение комбинированных модификаторов эффектов"""
        modifiers = {}
        
        for effect in self.get_active_effects(target_type):
            for modifier, value in effect.modifiers.items():
                if modifier not in modifiers:
                    modifiers[modifier] = 0.0
                modifiers[modifier] += value * effect.intensity
        
        return modifiers
    
    def get_effect_stack(self, effect_type: EffectType) -> Optional[EffectStack]:
        """Получение стека эффектов"""
        return self.effect_stacks.get(effect_type)
    
    def check_effect_conditions(self, weather_data: Dict[str, Any] = None, 
                               time_data: Dict[str, Any] = None,
                               season_data: Dict[str, Any] = None) -> List[str]:
        """Проверка условий для применения эффектов"""
        applicable_effects = []
        
        for template_name, template in self.effect_templates.items():
            conditions = template.get("conditions", {})
            
            if self._check_conditions(conditions, weather_data, time_data, season_data):
                applicable_effects.append(template_name)
        
        return applicable_effects
    
    def _check_conditions(self, conditions: Dict[str, Any], weather_data: Dict[str, Any] = None,
                         time_data: Dict[str, Any] = None, season_data: Dict[str, Any] = None) -> bool:
        """Проверка условий"""
        if not conditions:
            return True
        
        # Проверка погодных условий
        if "weather_type" in conditions and weather_data:
            if weather_data.get("weather_type") != conditions["weather_type"]:
                return False
        
        # Проверка временных условий
        if "time_of_day" in conditions and time_data:
            if time_data.get("time_of_day") != conditions["time_of_day"]:
                return False
        
        # Проверка сезонных условий
        if "season" in conditions and season_data:
            if season_data.get("current_season") != conditions["season"]:
                return False
        
        # Проверка диапазонов температуры
        if "temperature_range" in conditions and weather_data:
            temp_range = conditions["temperature_range"]
            temperature = weather_data.get("temperature", 0)
            if not (temp_range[0] <= temperature <= temp_range[1]):
                return False
        
        # Проверка диапазонов влажности
        if "humidity_range" in conditions and weather_data:
            humidity_range = conditions["humidity_range"]
            humidity = weather_data.get("humidity", 0)
            if not (humidity_range[0] <= humidity <= humidity_range[1]):
                return False
        
        # Проверка диапазонов скорости ветра
        if "wind_speed_range" in conditions and weather_data:
            wind_range = conditions["wind_speed_range"]
            wind_speed = weather_data.get("wind_speed", 0)
            if not (wind_range[0] <= wind_speed <= wind_range[1]):
                return False
        
        return True
    
    def add_effect_applied_callback(self, callback: callable):
        """Добавление callback для применения эффекта"""
        self.effect_applied_callbacks.append(callback)
    
    def add_effect_expired_callback(self, callback: callable):
        """Добавление callback для истечения эффекта"""
        self.effect_expired_callbacks.append(callback)
    
    def add_intensity_changed_callback(self, callback: callable):
        """Добавление callback для изменения интенсивности"""
        self.effect_intensity_changed_callbacks.append(callback)
    
    def _notify_effect_applied(self, effect: EnvironmentalEffect):
        """Уведомление о применении эффекта"""
        for callback in self.effect_applied_callbacks:
            try:
                callback(effect)
            except Exception as e:
                self.logger.error(f"Ошибка в callback применения эффекта: {e}")
    
    def _notify_effect_expired(self, effect: EnvironmentalEffect):
        """Уведомление об истечении эффекта"""
        for callback in self.effect_expired_callbacks:
            try:
                callback(effect)
            except Exception as e:
                self.logger.error(f"Ошибка в callback истечения эффекта: {e}")
    
    def get_effect_statistics(self) -> Dict[str, Any]:
        """Получение статистики эффектов"""
        effect_counts = {}
        for effect_type in EffectType:
            effect_counts[effect_type.value] = len(self.get_active_effects(effect_type=effect_type))
        
        return {
            "active_effects": len(self.active_effects),
            "effect_counts": effect_counts,
            "effect_stacks": {k.value: len(v.effects) for k, v in self.effect_stacks.items()},
            "system_statistics": self.effect_stats.copy()
        }
    
    def clear_all_effects(self):
        """Очистка всех эффектов"""
        effect_ids = list(self.active_effects.keys())
        
        for effect_id in effect_ids:
            self.remove_effect(effect_id)
        
        self.logger.info("Все экологические эффекты очищены")
    
    def clear_cache(self):
        """Очистка кэша"""
        self.effect_cache.clear()
        self.logger.info("Кэш EnvironmentalEffects очищен")
    
    def _on_destroy(self):
        """Уничтожение системы экологических эффектов"""
        self.active_effects.clear()
        self.effect_stacks.clear()
        self.effect_cache.clear()
        self.effect_applied_callbacks.clear()
        self.effect_expired_callbacks.clear()
        self.effect_intensity_changed_callbacks.clear()
        
        self.logger.info("EnvironmentalEffects уничтожен")
