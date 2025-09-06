#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

class WeatherType(Enum):
    """Типы погоды"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    FOGGY = "foggy"
    SNOWY = "snowy"
    WINDY = "windy"

class Season(Enum):
    """Сезоны"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

class TimeOfDay(Enum):
    """Время дня"""
    DAWN = "dawn"       # Рассвет
    MORNING = "morning" # Утро
    NOON = "noon"       # Полдень
    AFTERNOON = "afternoon"  # День
    DUSK = "dusk"       # Закат
    EVENING = "evening" # Вечер
    NIGHT = "night"     # Ночь
    MIDNIGHT = "midnight"  # Полночь

@dataclass
class WeatherState:
    """Состояние погоды"""
    weather_type: WeatherType
    intensity: float  # 0.0 - 1.0
    temperature: float  # Температура
    humidity: float    # Влажность
    wind_speed: float  # Скорость ветра
    duration: float    # Длительность в секундах
    start_time: float = field(default_factory=time.time)

@dataclass
class WorldState:
    """Состояние мира"""
    current_season: Season
    day_of_year: int  # День года (1-365)
    time_of_day: TimeOfDay
    day_cycle_progress: float  # Прогресс дня (0.0 - 1.0)
    current_weather: WeatherState
    temperature: float
    light_level: float  # Уровень освещения (0.0 - 1.0)

class WeatherSystem:
    """Система погоды"""
    
    def __init__(self):
        self.current_weather: Optional[WeatherState] = None
        self.weather_transition_time = 5.0  # Время перехода между погодными состояниями
        self.weather_probabilities = {
            WeatherType.CLEAR: 0.4,
            WeatherType.CLOUDY: 0.25,
            WeatherType.RAINY: 0.15,
            WeatherType.STORMY: 0.05,
            WeatherType.FOGGY: 0.08,
            WeatherType.SNOWY: 0.05,
            WeatherType.WINDY: 0.02
        }
        
        # Инициализация начальной погоды
        self._initialize_weather()
    
    def _initialize_weather(self):
        """Инициализация начальной погоды"""
        weather_type = random.choices(
            list(self.weather_probabilities.keys()),
            weights=list(self.weather_probabilities.values())
        )[0]
        
        self.current_weather = WeatherState(
            weather_type=weather_type,
            intensity=random.uniform(0.3, 0.8),
            temperature=random.uniform(15.0, 25.0),
            humidity=random.uniform(0.3, 0.7),
            wind_speed=random.uniform(0.0, 10.0),
            duration=random.uniform(300.0, 1800.0)  # 5-30 минут
        )
    
    def update(self, dt: float, season: Season, time_of_day: TimeOfDay):
        """Обновление системы погоды"""
        if not self.current_weather:
            self._initialize_weather()
            return
        
        # Проверяем, не истекло ли время текущей погоды
        if time.time() - self.current_weather.start_time >= self.current_weather.duration:
            self._change_weather(season, time_of_day)
        
        # Обновляем параметры погоды
        self._update_weather_parameters(dt, season, time_of_day)
    
    def _change_weather(self, season: Season, time_of_day: TimeOfDay):
        """Смена погоды"""
        # Модифицируем вероятности в зависимости от сезона
        probabilities = self._get_seasonal_probabilities(season)
        
        # Выбираем новую погоду
        new_weather_type = random.choices(
            list(probabilities.keys()),
            weights=list(probabilities.values())
        )[0]
        
        # Создаем новое состояние погоды
        self.current_weather = WeatherState(
            weather_type=new_weather_type,
            intensity=random.uniform(0.2, 1.0),
            temperature=self._calculate_temperature(season, time_of_day),
            humidity=random.uniform(0.2, 0.9),
            wind_speed=random.uniform(0.0, 15.0),
            duration=random.uniform(600.0, 2400.0)  # 10-40 минут
        )
    
    def _get_seasonal_probabilities(self, season: Season) -> Dict[WeatherType, float]:
        """Получение вероятностей погоды для сезона"""
        base_probabilities = self.weather_probabilities.copy()
        
        if season == Season.SPRING:
            base_probabilities[WeatherType.RAINY] *= 1.5
            base_probabilities[WeatherType.CLOUDY] *= 1.3
        elif season == Season.SUMMER:
            base_probabilities[WeatherType.CLEAR] *= 1.5
            base_probabilities[WeatherType.STORMY] *= 1.2
        elif season == Season.AUTUMN:
            base_probabilities[WeatherType.CLOUDY] *= 1.4
            base_probabilities[WeatherType.WINDY] *= 1.5
        elif season == Season.WINTER:
            base_probabilities[WeatherType.SNOWY] *= 3.0
            base_probabilities[WeatherType.FOGGY] *= 1.3
            base_probabilities[WeatherType.CLEAR] *= 0.5
        
        # Нормализуем вероятности
        total = sum(base_probabilities.values())
        return {k: v / total for k, v in base_probabilities.items()}
    
    def _calculate_temperature(self, season: Season, time_of_day: TimeOfDay) -> float:
        """Расчет температуры"""
        base_temp = {
            Season.SPRING: 15.0,
            Season.SUMMER: 25.0,
            Season.AUTUMN: 10.0,
            Season.WINTER: -5.0
        }[season]
        
        # Модификатор времени дня
        time_modifier = {
            TimeOfDay.DAWN: -2.0,
            TimeOfDay.MORNING: 0.0,
            TimeOfDay.NOON: 5.0,
            TimeOfDay.AFTERNOON: 3.0,
            TimeOfDay.DUSK: 0.0,
            TimeOfDay.EVENING: -2.0,
            TimeOfDay.NIGHT: -5.0,
            TimeOfDay.MIDNIGHT: -7.0
        }[time_of_day]
        
        return base_temp + time_modifier + random.uniform(-3.0, 3.0)
    
    def _update_weather_parameters(self, dt: float, season: Season, time_of_day: TimeOfDay):
        """Обновление параметров погоды"""
        if not self.current_weather:
            return
        
        # Плавные изменения интенсивности
        target_intensity = random.uniform(0.2, 1.0)
        self.current_weather.intensity += (target_intensity - self.current_weather.intensity) * dt * 0.1
        
        # Обновление температуры
        self.current_weather.temperature = self._calculate_temperature(season, time_of_day)
        
        # Изменения ветра
        wind_change = random.uniform(-2.0, 2.0) * dt
        self.current_weather.wind_speed = max(0.0, self.current_weather.wind_speed + wind_change)
    
    def get_weather_effects(self) -> Dict[str, float]:
        """Получение эффектов погоды"""
        if not self.current_weather:
            return {}
        
        effects = {}
        
        if self.current_weather.weather_type == WeatherType.RAINY:
            effects["visibility"] = 1.0 - self.current_weather.intensity * 0.3
            effects["movement_speed"] = 1.0 - self.current_weather.intensity * 0.1
        
        elif self.current_weather.weather_type == WeatherType.STORMY:
            effects["visibility"] = 1.0 - self.current_weather.intensity * 0.5
            effects["movement_speed"] = 1.0 - self.current_weather.intensity * 0.2
            effects["accuracy"] = 1.0 - self.current_weather.intensity * 0.15
        
        elif self.current_weather.weather_type == WeatherType.FOGGY:
            effects["visibility"] = 1.0 - self.current_weather.intensity * 0.7
        
        elif self.current_weather.weather_type == WeatherType.SNOWY:
            effects["movement_speed"] = 1.0 - self.current_weather.intensity * 0.3
            effects["visibility"] = 1.0 - self.current_weather.intensity * 0.2
        
        elif self.current_weather.weather_type == WeatherType.WINDY:
            effects["accuracy"] = 1.0 - self.current_weather.intensity * 0.1
            effects["movement_speed"] = 1.0 + self.current_weather.intensity * 0.1  # Ветер может помочь
        
        return effects

class DayNightCycle:
    """Система дня и ночи"""
    
    def __init__(self, day_duration: float = 1200.0):  # 20 минут на день
        self.day_duration = day_duration
        self.current_time = 0.0  # Время дня (0.0 - 1.0)
        self.time_multiplier = 1.0  # Множитель скорости времени
    
    def update(self, dt: float):
        """Обновление цикла дня и ночи"""
        self.current_time += (dt * self.time_multiplier) / self.day_duration
        
        if self.current_time >= 1.0:
            self.current_time = 0.0
    
    def get_time_of_day(self) -> TimeOfDay:
        """Получение времени дня"""
        if 0.0 <= self.current_time < 0.125:
            return TimeOfDay.DAWN
        elif 0.125 <= self.current_time < 0.25:
            return TimeOfDay.MORNING
        elif 0.25 <= self.current_time < 0.375:
            return TimeOfDay.NOON
        elif 0.375 <= self.current_time < 0.5:
            return TimeOfDay.AFTERNOON
        elif 0.5 <= self.current_time < 0.625:
            return TimeOfDay.DUSK
        elif 0.625 <= self.current_time < 0.75:
            return TimeOfDay.EVENING
        elif 0.75 <= self.current_time < 0.875:
            return TimeOfDay.NIGHT
        else:
            return TimeOfDay.MIDNIGHT
    
    def get_light_level(self) -> float:
        """Получение уровня освещения"""
        # Синусоидальная функция для плавного перехода
        light = (math.sin(self.current_time * 2 * math.pi - math.pi/2) + 1) / 2
        return max(0.1, light)  # Минимальный уровень освещения
    
    def get_temperature_modifier(self) -> float:
        """Получение модификатора температуры"""
        time_of_day = self.get_time_of_day()
        modifiers = {
            TimeOfDay.DAWN: -2.0,
            TimeOfDay.MORNING: 0.0,
            TimeOfDay.NOON: 5.0,
            TimeOfDay.AFTERNOON: 3.0,
            TimeOfDay.DUSK: 0.0,
            TimeOfDay.EVENING: -2.0,
            TimeOfDay.NIGHT: -5.0,
            TimeOfDay.MIDNIGHT: -7.0
        }
        return modifiers[time_of_day]
    
    def set_time_multiplier(self, multiplier: float):
        """Установка множителя скорости времени"""
        self.time_multiplier = max(0.1, min(10.0, multiplier))
    
    def set_time(self, time_progress: float):
        """Установка времени дня"""
        self.current_time = max(0.0, min(1.0, time_progress))

class SeasonSystem:
    """Система сезонов"""
    
    def __init__(self, season_duration: float = 7200.0):  # 2 часа на сезон
        self.season_duration = season_duration
        self.current_season_progress = 0.0  # Прогресс сезона (0.0 - 1.0)
        self.current_season = Season.SPRING
        self.season_multiplier = 1.0
    
    def update(self, dt: float):
        """Обновление системы сезонов"""
        self.current_season_progress += (dt * self.season_multiplier) / self.season_duration
        
        if self.current_season_progress >= 1.0:
            self.current_season_progress = 0.0
            self._advance_season()
    
    def _advance_season(self):
        """Переход к следующему сезону"""
        seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
        current_index = seasons.index(self.current_season)
        next_index = (current_index + 1) % len(seasons)
        self.current_season = seasons[next_index]
        print(f"Сезон изменился на: {self.current_season.value}")
    
    def get_season_effects(self) -> Dict[str, float]:
        """Получение эффектов сезона"""
        effects = {}
        
        if self.current_season == Season.SPRING:
            effects["growth_rate"] = 1.2
            effects["regeneration"] = 1.1
        elif self.current_season == Season.SUMMER:
            effects["growth_rate"] = 1.5
            effects["water_consumption"] = 1.3
        elif self.current_season == Season.AUTUMN:
            effects["harvest_bonus"] = 1.3
            effects["movement_speed"] = 0.9  # Скользкие листья
        elif self.current_season == Season.WINTER:
            effects["movement_speed"] = 0.8  # Снег и лед
            effects["visibility"] = 0.9      # Снегопад
            effects["cold_resistance"] = 1.2
        
        return effects
    
    def get_temperature_modifier(self) -> float:
        """Получение модификатора температуры"""
        modifiers = {
            Season.SPRING: 0.0,
            Season.SUMMER: 10.0,
            Season.AUTUMN: -5.0,
            Season.WINTER: -15.0
        }
        return modifiers[self.current_season]
    
    def set_season_multiplier(self, multiplier: float):
        """Установка множителя скорости смены сезонов"""
        self.season_multiplier = max(0.1, min(10.0, multiplier))

class WorldSystem:
    """Объединенная система мира"""
    
    def __init__(self):
        self.weather_system = WeatherSystem()
        self.day_night_cycle = DayNightCycle()
        self.season_system = SeasonSystem()
        
        self.world_state = WorldState(
            current_season=Season.SPRING,
            day_of_year=1,
            time_of_day=TimeOfDay.MORNING,
            day_cycle_progress=0.0,
            current_weather=WeatherState(
                weather_type=WeatherType.CLEAR,
                intensity=0.5,
                temperature=20.0,
                humidity=0.5,
                wind_speed=2.0,
                duration=600.0
            ),
            temperature=20.0,
            light_level=1.0
        )
    
    def update(self, dt: float):
        """Обновление всех систем мира"""
        # Обновляем цикл дня и ночи
        self.day_night_cycle.update(dt)
        
        # Обновляем сезоны
        self.season_system.update(dt)
        
        # Обновляем погоду
        self.weather_system.update(dt, self.season_system.current_season, 
                                 self.day_night_cycle.get_time_of_day())
        
        # Обновляем состояние мира
        self._update_world_state()
    
    def _update_world_state(self):
        """Обновление состояния мира"""
        self.world_state.current_season = self.season_system.current_season
        self.world_state.time_of_day = self.day_night_cycle.get_time_of_day()
        self.world_state.day_cycle_progress = self.day_night_cycle.current_time
        self.world_state.current_weather = self.weather_system.current_weather
        self.world_state.light_level = self.day_night_cycle.get_light_level()
        
        # Рассчитываем общую температуру
        base_temp = self.season_system.get_temperature_modifier()
        time_temp = self.day_night_cycle.get_temperature_modifier()
        weather_temp = self.weather_system.current_weather.temperature if self.weather_system.current_weather else 20.0
        
        self.world_state.temperature = base_temp + time_temp + weather_temp
    
    def get_environmental_effects(self) -> Dict[str, float]:
        """Получение всех экологических эффектов"""
        effects = {}
        
        # Эффекты погоды
        weather_effects = self.weather_system.get_weather_effects()
        effects.update(weather_effects)
        
        # Эффекты сезона
        season_effects = self.season_system.get_season_effects()
        effects.update(season_effects)
        
        # Эффекты времени дня
        light_level = self.world_state.light_level
        if light_level < 0.3:  # Ночь
            effects["visibility"] = effects.get("visibility", 1.0) * 0.7
            effects["stealth_bonus"] = 1.2
        
        return effects
    
    def get_world_state(self) -> WorldState:
        """Получение состояния мира"""
        return self.world_state
    
    def set_time_speed(self, multiplier: float):
        """Установка скорости времени"""
        self.day_night_cycle.set_time_multiplier(multiplier)
        self.season_system.set_season_multiplier(multiplier)
    
    def force_weather_change(self, weather_type: WeatherType):
        """Принудительная смена погоды"""
        if self.weather_system.current_weather:
            self.weather_system.current_weather.weather_type = weather_type
            self.weather_system.current_weather.start_time = time.time()
    
    def force_season_change(self, season: Season):
        """Принудительная смена сезона"""
        self.season_system.current_season = season
        self.season_system.current_season_progress = 0.0
