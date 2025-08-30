#!/usr/bin/env python3
"""Система дня и ночи для игрового мира
Включает реалистичный цикл дня и ночи, изменение освещения и поведение существ"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ ВРЕМЕНИ СУТОК
class TimeOfDay(Enum):
    """Время суток"""
    DAWN = "dawn"             # Рассвет
    MORNING = "morning"       # Утро
    NOON = "noon"             # Полдень
    AFTERNOON = "afternoon"   # День
    DUSK = "dusk"             # Закат
    EVENING = "evening"       # Вечер
    NIGHT = "night"           # Ночь
    MIDNIGHT = "midnight"     # Полночь

# = ФАЗЫ ЛУНЫ
class MoonPhase(Enum):
    """Фазы луны"""
    NEW_MOON = "new_moon"         # Новолуние
    WAXING_CRESCENT = "waxing_crescent"  # Растущий серп
    FIRST_QUARTER = "first_quarter"      # Первая четверть
    WAXING_GIBBOUS = "waxing_gibbous"    # Растущая луна
    FULL_MOON = "full_moon"       # Полнолуние
    WANING_GIBBOUS = "waning_gibbous"    # Убывающая луна
    LAST_QUARTER = "last_quarter"        # Последняя четверть
    WANING_CRESCENT = "waning_crescent"  # Убывающий серп

# = НАСТРОЙКИ ЦИКЛА
@dataclass
class DayNightSettings:
    """Настройки цикла дня и ночи"""
    day_length_minutes: float = 24.0  # Длина дня в минутах
    dawn_start_hour: float = 5.0      # Начало рассвета
    dawn_duration_hours: float = 1.0  # Длительность рассвета
    dusk_start_hour: float = 19.0     # Начало заката
    dusk_duration_hours: float = 1.0  # Длительность заката
    night_start_hour: float = 20.0    # Начало ночи
    night_end_hour: float = 6.0       # Конец ночи
    moon_cycle_days: float = 29.5     # Цикл луны в днях
    time_acceleration: float = 1.0    # Ускорение времени

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class TimeData:
    """Данные времени"""
    current_time: float  # Время в часах (0-24)
    day_of_year: int     # День года (1-365)
    year: int           # Год
    time_of_day: TimeOfDay
    moon_phase: MoonPhase
    moon_illumination: float  # Освещенность луны (0-1)
    sun_angle: float    # Угол солнца (0-360)
    moon_angle: float   # Угол луны (0-360)
    ambient_light: float  # Окружающее освещение (0-1)
    sky_color: Tuple[float, float, float]  # Цвет неба (RGB)
    created_at: float = field(default_factory=time.time)

@dataclass
class LightingData:
    """Данные освещения"""
    sun_intensity: float = 1.0
    moon_intensity: float = 0.1
    ambient_intensity: float = 0.3
    shadow_strength: float = 0.5
    fog_density: float = 0.0
    color_temperature: float = 5500.0  # Кельвины

@dataclass
class BehaviorModifier:
    """Модификатор поведения"""
    entity_type: str
    time_of_day: TimeOfDay
    modifier_type: str  # activity, aggression, visibility, etc.
    value: float
    description: str

# = СИСТЕМА ДНЯ И НОЧИ
class DayNightCycle(BaseComponent):
    """Система дня и ночи"""
    
    def __init__(self):
        super().__init__(
            component_id="DayNightCycle",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки системы
        self.settings = DayNightSettings()
        self.current_time_data: Optional[TimeData] = None
        self.lighting_data: Optional[LightingData] = None
        
        # Поведенческие модификаторы
        self.behavior_modifiers: Dict[str, List[BehaviorModifier]] = {}
        
        # Кэши и статистика
        self.time_cache: Dict[str, Any] = {}
        self.cycle_stats = {
            "days_passed": 0,
            "time_updates": 0,
            "phase_changes": 0,
            "total_update_time": 0.0
        }
        
        # Слушатели событий
        self.time_changed_callbacks: List[callable] = []
        self.phase_changed_callbacks: List[callable] = []
        self.day_changed_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация системы дня и ночи"""
        try:
            # Инициализация времени
            self.current_time_data = self._create_initial_time()
            self.lighting_data = self._create_initial_lighting()
            
            # Инициализация поведенческих модификаторов
            self._initialize_behavior_modifiers()
            
            self.logger.info("DayNightCycle инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации DayNightCycle: {e}")
            return False
    
    def _create_initial_time(self) -> TimeData:
        """Создание начального времени"""
        current_time = 12.0  # Полдень
        day_of_year = 1
        year = 1
        
        time_of_day = self._get_time_of_day(current_time)
        moon_phase = self._calculate_moon_phase(day_of_year)
        moon_illumination = self._calculate_moon_illumination(moon_phase)
        
        sun_angle = self._calculate_sun_angle(current_time, day_of_year)
        moon_angle = self._calculate_moon_angle(current_time, day_of_year)
        
        ambient_light = self._calculate_ambient_light(current_time, moon_illumination)
        sky_color = self._calculate_sky_color(current_time, sun_angle)
        
        return TimeData(
            current_time=current_time,
            day_of_year=day_of_year,
            year=year,
            time_of_day=time_of_day,
            moon_phase=moon_phase,
            moon_illumination=moon_illumination,
            sun_angle=sun_angle,
            moon_angle=moon_angle,
            ambient_light=ambient_light,
            sky_color=sky_color
        )
    
    def _create_initial_lighting(self) -> LightingData:
        """Создание начального освещения"""
        return LightingData()
    
    def _initialize_behavior_modifiers(self):
        """Инициализация поведенческих модификаторов"""
        # Модификаторы для животных
        self.behavior_modifiers["animals"] = [
            BehaviorModifier("animals", TimeOfDay.DAWN, "activity", 0.7, "Пробуждение животных"),
            BehaviorModifier("animals", TimeOfDay.MORNING, "activity", 1.0, "Активность животных"),
            BehaviorModifier("animals", TimeOfDay.NOON, "activity", 0.8, "Дневная активность"),
            BehaviorModifier("animals", TimeOfDay.AFTERNOON, "activity", 0.9, "Вечерняя активность"),
            BehaviorModifier("animals", TimeOfDay.DUSK, "activity", 0.6, "Подготовка ко сну"),
            BehaviorModifier("animals", TimeOfDay.NIGHT, "activity", 0.2, "Ночной покой"),
            BehaviorModifier("animals", TimeOfDay.MIDNIGHT, "activity", 0.1, "Глубокий сон")
        ]
        
        # Модификаторы для монстров
        self.behavior_modifiers["monsters"] = [
            BehaviorModifier("monsters", TimeOfDay.DAWN, "aggression", 0.3, "Снижение агрессии на рассвете"),
            BehaviorModifier("monsters", TimeOfDay.MORNING, "aggression", 0.5, "Умеренная агрессия"),
            BehaviorModifier("monsters", TimeOfDay.NOON, "aggression", 0.7, "Дневная агрессия"),
            BehaviorModifier("monsters", TimeOfDay.AFTERNOON, "aggression", 0.8, "Повышенная агрессия"),
            BehaviorModifier("monsters", TimeOfDay.DUSK, "aggression", 0.9, "Агрессия на закате"),
            BehaviorModifier("monsters", TimeOfDay.NIGHT, "aggression", 1.0, "Максимальная агрессия"),
            BehaviorModifier("monsters", TimeOfDay.MIDNIGHT, "aggression", 0.8, "Ночная агрессия")
        ]
        
        # Модификаторы для NPC
        self.behavior_modifiers["npc"] = [
            BehaviorModifier("npc", TimeOfDay.DAWN, "activity", 0.3, "Пробуждение NPC"),
            BehaviorModifier("npc", TimeOfDay.MORNING, "activity", 0.8, "Утренняя активность"),
            BehaviorModifier("npc", TimeOfDay.NOON, "activity", 1.0, "Дневная активность"),
            BehaviorModifier("npc", TimeOfDay.AFTERNOON, "activity", 0.9, "Вечерняя активность"),
            BehaviorModifier("npc", TimeOfDay.DUSK, "activity", 0.6, "Подготовка к отдыху"),
            BehaviorModifier("npc", TimeOfDay.NIGHT, "activity", 0.2, "Ночной отдых"),
            BehaviorModifier("npc", TimeOfDay.MIDNIGHT, "activity", 0.1, "Глубокий сон")
        ]
    
    def update_time(self, delta_time: float):
        """Обновление времени"""
        start_time = time.time()
        
        if not self.current_time_data:
            return
        
        old_time_data = self.current_time_data
        old_day = self.current_time_data.day_of_year
        
        # Обновление времени
        time_increment = (delta_time * self.settings.time_acceleration) / 60.0  # Конвертация в часы
        self.current_time_data.current_time += time_increment
        
        # Проверка перехода на следующий день
        if self.current_time_data.current_time >= 24.0:
            self.current_time_data.current_time -= 24.0
            self.current_time_data.day_of_year += 1
            self.cycle_stats["days_passed"] += 1
            
            # Проверка перехода на следующий год
            if self.current_time_data.day_of_year > 365:
                self.current_time_data.day_of_year = 1
                self.current_time_data.year += 1
        
        # Обновление данных времени
        self._update_time_data()
        
        # Проверка изменений
        if self.current_time_data.time_of_day != old_time_data.time_of_day:
            self.cycle_stats["phase_changes"] += 1
            self._notify_time_changed(old_time_data, self.current_time_data)
        
        if self.current_time_data.day_of_year != old_day:
            self._notify_day_changed(old_day, self.current_time_data.day_of_year)
        
        self.cycle_stats["time_updates"] += 1
        
        # Обновление статистики
        update_time = time.time() - start_time
        self.cycle_stats["total_update_time"] += update_time
    
    def _update_time_data(self):
        """Обновление данных времени"""
        if not self.current_time_data:
            return
        
        # Обновление времени суток
        self.current_time_data.time_of_day = self._get_time_of_day(self.current_time_data.current_time)
        
        # Обновление фазы луны
        self.current_time_data.moon_phase = self._calculate_moon_phase(self.current_time_data.day_of_year)
        self.current_time_data.moon_illumination = self._calculate_moon_illumination(self.current_time_data.moon_phase)
        
        # Обновление углов
        self.current_time_data.sun_angle = self._calculate_sun_angle(
            self.current_time_data.current_time, 
            self.current_time_data.day_of_year
        )
        self.current_time_data.moon_angle = self._calculate_moon_angle(
            self.current_time_data.current_time, 
            self.current_time_data.day_of_year
        )
        
        # Обновление освещения
        self.current_time_data.ambient_light = self._calculate_ambient_light(
            self.current_time_data.current_time, 
            self.current_time_data.moon_illumination
        )
        self.current_time_data.sky_color = self._calculate_sky_color(
            self.current_time_data.current_time, 
            self.current_time_data.sun_angle
        )
        
        # Обновление данных освещения
        self._update_lighting_data()
    
    def _get_time_of_day(self, current_time: float) -> TimeOfDay:
        """Определение времени суток"""
        if self.settings.dawn_start_hour <= current_time < self.settings.dawn_start_hour + self.settings.dawn_duration_hours:
            return TimeOfDay.DAWN
        elif self.settings.dawn_start_hour + self.settings.dawn_duration_hours <= current_time < 12.0:
            return TimeOfDay.MORNING
        elif 12.0 <= current_time < 14.0:
            return TimeOfDay.NOON
        elif 14.0 <= current_time < self.settings.dusk_start_hour:
            return TimeOfDay.AFTERNOON
        elif self.settings.dusk_start_hour <= current_time < self.settings.dusk_start_hour + self.settings.dusk_duration_hours:
            return TimeOfDay.DUSK
        elif self.settings.dusk_start_hour + self.settings.dusk_duration_hours <= current_time < self.settings.night_start_hour:
            return TimeOfDay.EVENING
        elif self.settings.night_start_hour <= current_time < 24.0:
            return TimeOfDay.NIGHT
        else:
            return TimeOfDay.MIDNIGHT
    
    def _calculate_moon_phase(self, day_of_year: int) -> MoonPhase:
        """Расчет фазы луны"""
        # Упрощенный расчет фазы луны
        moon_day = (day_of_year % int(self.settings.moon_cycle_days)) / self.settings.moon_cycle_days
        
        if moon_day < 0.0625:
            return MoonPhase.NEW_MOON
        elif moon_day < 0.1875:
            return MoonPhase.WAXING_CRESCENT
        elif moon_day < 0.3125:
            return MoonPhase.FIRST_QUARTER
        elif moon_day < 0.4375:
            return MoonPhase.WAXING_GIBBOUS
        elif moon_day < 0.5625:
            return MoonPhase.FULL_MOON
        elif moon_day < 0.6875:
            return MoonPhase.WANING_GIBBOUS
        elif moon_day < 0.8125:
            return MoonPhase.LAST_QUARTER
        else:
            return MoonPhase.WANING_CRESCENT
    
    def _calculate_moon_illumination(self, moon_phase: MoonPhase) -> float:
        """Расчет освещенности луны"""
        illumination_map = {
            MoonPhase.NEW_MOON: 0.0,
            MoonPhase.WAXING_CRESCENT: 0.25,
            MoonPhase.FIRST_QUARTER: 0.5,
            MoonPhase.WAXING_GIBBOUS: 0.75,
            MoonPhase.FULL_MOON: 1.0,
            MoonPhase.WANING_GIBBOUS: 0.75,
            MoonPhase.LAST_QUARTER: 0.5,
            MoonPhase.WANING_CRESCENT: 0.25
        }
        
        return illumination_map.get(moon_phase, 0.0)
    
    def _calculate_sun_angle(self, current_time: float, day_of_year: int) -> float:
        """Расчет угла солнца"""
        # Базовый угол на основе времени суток
        base_angle = (current_time / 24.0) * 360.0
        
        # Сезонные изменения
        season_factor = math.sin((day_of_year / 365.0) * 2 * math.pi)
        season_offset = season_factor * 23.5  # Наклон земной оси
        
        return (base_angle + season_offset) % 360.0
    
    def _calculate_moon_angle(self, current_time: float, day_of_year: int) -> float:
        """Расчет угла луны"""
        # Луна движется медленнее солнца
        moon_speed = 360.0 / self.settings.moon_cycle_days
        moon_angle = (current_time / 24.0) * moon_speed + (day_of_year * moon_speed)
        
        return moon_angle % 360.0
    
    def _calculate_ambient_light(self, current_time: float, moon_illumination: float) -> float:
        """Расчет окружающего освещения"""
        # Базовое освещение от солнца
        if 6.0 <= current_time <= 18.0:
            # Дневное время
            sun_factor = 1.0 - abs(current_time - 12.0) / 6.0
            sun_light = max(0.1, sun_factor)
        else:
            # Ночное время
            sun_light = 0.05
        
        # Освещение от луны
        moon_light = moon_illumination * 0.3 if current_time < 6.0 or current_time > 18.0 else 0.0
        
        # Общее освещение
        total_light = sun_light + moon_light
        
        return min(1.0, max(0.0, total_light))
    
    def _calculate_sky_color(self, current_time: float, sun_angle: float) -> Tuple[float, float, float]:
        """Расчет цвета неба"""
        # Базовые цвета для разных времен суток
        if 6.0 <= current_time <= 18.0:
            # Дневное время
            if current_time < 8.0 or current_time > 16.0:
                # Утро/вечер
                return (1.0, 0.8, 0.6)  # Оранжевый
            else:
                # День
                return (0.5, 0.7, 1.0)  # Голубой
        else:
            # Ночное время
            if current_time < 22.0 or current_time > 4.0:
                # Вечер/утро
                return (0.2, 0.1, 0.3)  # Темно-синий
            else:
                # Глубокая ночь
                return (0.05, 0.05, 0.1)  # Очень темный
    
    def _update_lighting_data(self):
        """Обновление данных освещения"""
        if not self.current_time_data or not self.lighting_data:
            return
        
        # Интенсивность солнца
        if 6.0 <= self.current_time_data.current_time <= 18.0:
            sun_factor = 1.0 - abs(self.current_time_data.current_time - 12.0) / 6.0
            self.lighting_data.sun_intensity = max(0.1, sun_factor)
        else:
            self.lighting_data.sun_intensity = 0.0
        
        # Интенсивность луны
        if self.current_time_data.current_time < 6.0 or self.current_time_data.current_time > 18.0:
            self.lighting_data.moon_intensity = self.current_time_data.moon_illumination * 0.3
        else:
            self.lighting_data.moon_intensity = 0.0
        
        # Окружающее освещение
        self.lighting_data.ambient_intensity = self.current_time_data.ambient_light
        
        # Сила теней
        if self.current_time_data.current_time < 6.0 or self.current_time_data.current_time > 18.0:
            self.lighting_data.shadow_strength = 0.8
        else:
            self.lighting_data.shadow_strength = 0.5
        
        # Плотность тумана
        if self.current_time_data.current_time < 7.0 or self.current_time_data.current_time > 17.0:
            self.lighting_data.fog_density = 0.3
        else:
            self.lighting_data.fog_density = 0.0
        
        # Цветовая температура
        if self.current_time_data.current_time < 8.0 or self.current_time_data.current_time > 16.0:
            self.lighting_data.color_temperature = 3000.0  # Теплый свет
        else:
            self.lighting_data.color_temperature = 5500.0  # Дневной свет
    
    def get_current_time_data(self) -> Optional[TimeData]:
        """Получение текущих данных времени"""
        return self.current_time_data
    
    def get_lighting_data(self) -> Optional[LightingData]:
        """Получение данных освещения"""
        return self.lighting_data
    
    def get_behavior_modifiers(self, entity_type: str, time_of_day: TimeOfDay = None) -> List[BehaviorModifier]:
        """Получение модификаторов поведения"""
        if entity_type not in self.behavior_modifiers:
            return []
        
        modifiers = self.behavior_modifiers[entity_type]
        
        if time_of_day:
            return [mod for mod in modifiers if mod.time_of_day == time_of_day]
        
        return modifiers
    
    def set_time(self, hours: float, day_of_year: int = None, year: int = None):
        """Установка времени"""
        if not self.current_time_data:
            return
        
        old_time_data = self.current_time_data
        
        # Установка времени
        self.current_time_data.current_time = max(0.0, min(24.0, hours))
        
        if day_of_year is not None:
            self.current_time_data.day_of_year = max(1, min(365, day_of_year))
        
        if year is not None:
            self.current_time_data.year = max(1, year)
        
        # Обновление данных
        self._update_time_data()
        
        # Уведомление об изменении
        self._notify_time_changed(old_time_data, self.current_time_data)
    
    def add_time_changed_callback(self, callback: callable):
        """Добавление callback для изменения времени"""
        self.time_changed_callbacks.append(callback)
    
    def add_phase_changed_callback(self, callback: callable):
        """Добавление callback для изменения фазы"""
        self.phase_changed_callbacks.append(callback)
    
    def add_day_changed_callback(self, callback: callable):
        """Добавление callback для смены дня"""
        self.day_changed_callbacks.append(callback)
    
    def _notify_time_changed(self, old_time_data: TimeData, new_time_data: TimeData):
        """Уведомление об изменении времени"""
        for callback in self.time_changed_callbacks:
            try:
                callback(old_time_data, new_time_data)
            except Exception as e:
                self.logger.error(f"Ошибка в callback изменения времени: {e}")
    
    def _notify_day_changed(self, old_day: int, new_day: int):
        """Уведомление о смене дня"""
        for callback in self.day_changed_callbacks:
            try:
                callback(old_day, new_day)
            except Exception as e:
                self.logger.error(f"Ошибка в callback смены дня: {e}")
    
    def get_cycle_statistics(self) -> Dict[str, Any]:
        """Получение статистики цикла"""
        if not self.current_time_data:
            return {}
        
        return {
            "current_time": self.current_time_data.current_time,
            "day_of_year": self.current_time_data.day_of_year,
            "year": self.current_time_data.year,
            "time_of_day": self.current_time_data.time_of_day.value,
            "moon_phase": self.current_time_data.moon_phase.value,
            "moon_illumination": self.current_time_data.moon_illumination,
            "ambient_light": self.current_time_data.ambient_light,
            "sun_angle": self.current_time_data.sun_angle,
            "moon_angle": self.current_time_data.moon_angle,
            "system_statistics": self.cycle_stats.copy()
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self.time_cache.clear()
        self.logger.info("Кэш DayNightCycle очищен")
    
    def _on_destroy(self):
        """Уничтожение системы дня и ночи"""
        self.time_cache.clear()
        self.time_changed_callbacks.clear()
        self.phase_changed_callbacks.clear()
        self.day_changed_callbacks.clear()
        
        self.logger.info("DayNightCycle уничтожен")
