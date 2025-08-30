#!/usr/bin/env python3
"""Система погоды для игрового мира
Включает динамическую погоду, осадки, ветер и влияние на геймплей"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ ПОГОДЫ
class WeatherType(Enum):
    """Типы погоды"""
    CLEAR = "clear"           # Ясно
    CLOUDY = "cloudy"         # Облачно
    RAIN = "rain"             # Дождь
    STORM = "storm"           # Буря
    SNOW = "snow"             # Снег
    HAIL = "hail"             # Град
    FOG = "fog"               # Туман
    WINDY = "windy"           # Ветрено
    DROUGHT = "drought"       # Засуха
    EXTREME = "extreme"       # Экстремальная погода

# = ТИПЫ ОСАДКОВ
class PrecipitationType(Enum):
    """Типы осадков"""
    NONE = "none"             # Нет осадков
    LIGHT_RAIN = "light_rain" # Легкий дождь
    HEAVY_RAIN = "heavy_rain" # Сильный дождь
    DRIZZLE = "drizzle"       # Морось
    LIGHT_SNOW = "light_snow" # Легкий снег
    HEAVY_SNOW = "heavy_snow" # Сильный снег
    HAIL = "hail"             # Град
    SLEET = "sleet"           # Мокрый снег

# = НАПРАВЛЕНИЯ ВЕТРА
class WindDirection(Enum):
    """Направления ветра"""
    NORTH = "north"           # Север
    NORTHEAST = "northeast"   # Северо-восток
    EAST = "east"             # Восток
    SOUTHEAST = "southeast"   # Юго-восток
    SOUTH = "south"           # Юг
    SOUTHWEST = "southwest"   # Юго-запад
    WEST = "west"             # Запад
    NORTHWEST = "northwest"   # Северо-запад

# = НАСТРОЙКИ ПОГОДЫ
@dataclass
class WeatherSettings:
    """Настройки погоды"""
    base_temperature: float = 20.0
    temperature_variation: float = 15.0
    humidity_base: float = 0.5
    humidity_variation: float = 0.3
    wind_base_speed: float = 5.0
    wind_max_speed: float = 30.0
    precipitation_chance: float = 0.3
    weather_change_rate: float = 0.1
    season_influence: bool = True
    biome_influence: bool = True

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class WeatherCondition:
    """Погодное условие"""
    weather_type: WeatherType
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: WindDirection
    precipitation_type: PrecipitationType
    precipitation_intensity: float
    visibility: float
    pressure: float
    duration: float = 0.0
    intensity: float = 1.0

@dataclass
class WeatherZone:
    """Погодная зона"""
    zone_id: str
    center_x: float
    center_y: float
    radius: float
    current_weather: WeatherCondition
    weather_history: List[WeatherCondition]
    biome_type: str
    season: str
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class WeatherEffect:
    """Эффект погоды"""
    effect_type: str
    intensity: float
    duration: float
    target_type: str  # player, npc, environment
    description: str
    modifiers: Dict[str, float] = field(default_factory=dict)

# = СИСТЕМА ПОГОДЫ
class WeatherSystem(BaseComponent):
    """Система погоды"""
    
    def __init__(self):
        super().__init__(
            component_id="WeatherSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки системы
        self.settings = WeatherSettings()
        self.weather_zones: Dict[str, WeatherZone] = {}
        self.global_weather: Optional[WeatherCondition] = None
        
        # Шаблоны погоды
        self.weather_templates: Dict[WeatherType, Dict[str, Any]] = {}
        self.biome_weather_modifiers: Dict[str, Dict[str, float]] = {}
        self.season_weather_modifiers: Dict[str, Dict[str, float]] = {}
        
        # Эффекты погоды
        self.active_effects: Dict[str, WeatherEffect] = {}
        self.weather_effects: Dict[WeatherType, List[WeatherEffect]] = {}
        
        # Кэши и статистика
        self.weather_cache: Dict[str, Any] = {}
        self.weather_stats = {
            "zones_created": 0,
            "weather_changes": 0,
            "effects_applied": 0,
            "total_update_time": 0.0
        }
        
        # Слушатели событий
        self.weather_changed_callbacks: List[callable] = []
        self.effect_applied_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация системы погоды"""
        try:
            self._initialize_weather_templates()
            self._initialize_biome_modifiers()
            self._initialize_season_modifiers()
            self._initialize_weather_effects()
            
            # Создание глобальной погоды
            self.global_weather = self._create_base_weather()
            
            self.logger.info("WeatherSystem инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации WeatherSystem: {e}")
            return False
    
    def _initialize_weather_templates(self):
        """Инициализация шаблонов погоды"""
        self.weather_templates = {
            WeatherType.CLEAR: {
                "temperature_modifier": 1.0,
                "humidity_modifier": 0.8,
                "wind_modifier": 0.5,
                "visibility": 1.0,
                "precipitation_chance": 0.0
            },
            WeatherType.CLOUDY: {
                "temperature_modifier": 0.9,
                "humidity_modifier": 1.2,
                "wind_modifier": 0.8,
                "visibility": 0.8,
                "precipitation_chance": 0.2
            },
            WeatherType.RAIN: {
                "temperature_modifier": 0.8,
                "humidity_modifier": 2.0,
                "wind_modifier": 1.2,
                "visibility": 0.6,
                "precipitation_chance": 1.0
            },
            WeatherType.STORM: {
                "temperature_modifier": 0.7,
                "humidity_modifier": 2.5,
                "wind_modifier": 2.0,
                "visibility": 0.3,
                "precipitation_chance": 1.0
            },
            WeatherType.SNOW: {
                "temperature_modifier": 0.3,
                "humidity_modifier": 1.5,
                "wind_modifier": 1.0,
                "visibility": 0.7,
                "precipitation_chance": 1.0
            },
            WeatherType.HAIL: {
                "temperature_modifier": 0.4,
                "humidity_modifier": 1.8,
                "wind_modifier": 1.5,
                "visibility": 0.5,
                "precipitation_chance": 1.0
            },
            WeatherType.FOG: {
                "temperature_modifier": 0.9,
                "humidity_modifier": 1.8,
                "wind_modifier": 0.3,
                "visibility": 0.2,
                "precipitation_chance": 0.1
            },
            WeatherType.WINDY: {
                "temperature_modifier": 0.9,
                "humidity_modifier": 0.9,
                "wind_modifier": 2.5,
                "visibility": 0.9,
                "precipitation_chance": 0.0
            },
            WeatherType.DROUGHT: {
                "temperature_modifier": 1.5,
                "humidity_modifier": 0.3,
                "wind_modifier": 1.8,
                "visibility": 1.0,
                "precipitation_chance": 0.0
            },
            WeatherType.EXTREME: {
                "temperature_modifier": 0.5,
                "humidity_modifier": 3.0,
                "wind_modifier": 3.0,
                "visibility": 0.1,
                "precipitation_chance": 1.0
            }
        }
    
    def _initialize_biome_modifiers(self):
        """Инициализация модификаторов биомов"""
        self.biome_weather_modifiers = {
            "forest": {
                "temperature_modifier": 0.9,
                "humidity_modifier": 1.3,
                "wind_modifier": 0.7
            },
            "desert": {
                "temperature_modifier": 1.4,
                "humidity_modifier": 0.4,
                "wind_modifier": 1.2
            },
            "mountain": {
                "temperature_modifier": 0.7,
                "humidity_modifier": 1.1,
                "wind_modifier": 1.5
            },
            "ocean": {
                "temperature_modifier": 1.0,
                "humidity_modifier": 1.6,
                "wind_modifier": 1.3
            },
            "tundra": {
                "temperature_modifier": 0.5,
                "humidity_modifier": 0.8,
                "wind_modifier": 1.4
            },
            "swamp": {
                "temperature_modifier": 1.1,
                "humidity_modifier": 1.8,
                "wind_modifier": 0.6
            }
        }
    
    def _initialize_season_modifiers(self):
        """Инициализация модификаторов сезонов"""
        self.season_weather_modifiers = {
            "spring": {
                "temperature_modifier": 0.8,
                "humidity_modifier": 1.2,
                "precipitation_chance": 1.3
            },
            "summer": {
                "temperature_modifier": 1.3,
                "humidity_modifier": 0.9,
                "precipitation_chance": 0.7
            },
            "autumn": {
                "temperature_modifier": 0.9,
                "humidity_modifier": 1.1,
                "precipitation_chance": 1.1
            },
            "winter": {
                "temperature_modifier": 0.4,
                "humidity_modifier": 0.8,
                "precipitation_chance": 1.5
            }
        }
    
    def _initialize_weather_effects(self):
        """Инициализация эффектов погоды"""
        self.weather_effects = {
            WeatherType.RAIN: [
                WeatherEffect(
                    effect_type="movement_speed",
                    intensity=0.8,
                    duration=0.0,
                    target_type="player",
                    description="Снижение скорости движения",
                    modifiers={"movement_speed": -0.2}
                ),
                WeatherEffect(
                    effect_type="visibility",
                    intensity=0.6,
                    duration=0.0,
                    target_type="player",
                    description="Снижение видимости",
                    modifiers={"visibility": -0.4}
                )
            ],
            WeatherType.STORM: [
                WeatherEffect(
                    effect_type="movement_speed",
                    intensity=0.5,
                    duration=0.0,
                    target_type="player",
                    description="Сильное снижение скорости движения",
                    modifiers={"movement_speed": -0.5}
                ),
                WeatherEffect(
                    effect_type="damage",
                    intensity=0.3,
                    duration=0.0,
                    target_type="player",
                    description="Повреждения от молний",
                    modifiers={"lightning_damage": 0.1}
                )
            ],
            WeatherType.SNOW: [
                WeatherEffect(
                    effect_type="movement_speed",
                    intensity=0.7,
                    duration=0.0,
                    target_type="player",
                    description="Снижение скорости в снегу",
                    modifiers={"movement_speed": -0.3}
                ),
                WeatherEffect(
                    effect_type="temperature",
                    intensity=0.8,
                    duration=0.0,
                    target_type="player",
                    description="Снижение температуры тела",
                    modifiers={"body_temperature": -0.2}
                )
            ],
            WeatherType.FOG: [
                WeatherEffect(
                    effect_type="visibility",
                    intensity=0.2,
                    duration=0.0,
                    target_type="player",
                    description="Сильное снижение видимости",
                    modifiers={"visibility": -0.8}
                )
            ],
            WeatherType.DROUGHT: [
                WeatherEffect(
                    effect_type="hydration",
                    intensity=1.0,
                    duration=0.0,
                    target_type="player",
                    description="Ускоренная потеря влаги",
                    modifiers={"hydration_loss": 2.0}
                )
            ]
        }
    
    def create_weather_zone(self, zone_id: str, center_x: float, center_y: float, 
                           radius: float, biome_type: str = "forest", 
                           season: str = "summer") -> WeatherZone:
        """Создание погодной зоны"""
        # Создание базовой погоды для зоны
        base_weather = self._create_base_weather()
        
        # Применение модификаторов биома и сезона
        modified_weather = self._apply_biome_modifiers(base_weather, biome_type)
        modified_weather = self._apply_season_modifiers(modified_weather, season)
        
        # Создание зоны
        weather_zone = WeatherZone(
            zone_id=zone_id,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            current_weather=modified_weather,
            weather_history=[modified_weather],
            biome_type=biome_type,
            season=season
        )
        
        self.weather_zones[zone_id] = weather_zone
        self.weather_stats["zones_created"] += 1
        
        self.logger.info(f"Создана погодная зона {zone_id}: {biome_type}, {season}")
        
        return weather_zone
    
    def _create_base_weather(self) -> WeatherCondition:
        """Создание базовой погоды"""
        # Выбор типа погоды
        weather_type = random.choice(list(WeatherType))
        
        # Базовые параметры
        temperature = self.settings.base_temperature + random.uniform(
            -self.settings.temperature_variation, 
            self.settings.temperature_variation
        )
        
        humidity = self.settings.humidity_base + random.uniform(
            -self.settings.humidity_variation, 
            self.settings.humidity_variation
        )
        humidity = max(0.0, min(1.0, humidity))
        
        wind_speed = random.uniform(0.0, self.settings.wind_max_speed)
        wind_direction = random.choice(list(WindDirection))
        
        # Определение типа осадков
        precipitation_type = PrecipitationType.NONE
        precipitation_intensity = 0.0
        
        if random.random() < self.settings.precipitation_chance:
            if temperature > 5.0:
                precipitation_type = random.choice([
                    PrecipitationType.LIGHT_RAIN,
                    PrecipitationType.HEAVY_RAIN,
                    PrecipitationType.DRIZZLE
                ])
            else:
                precipitation_type = random.choice([
                    PrecipitationType.LIGHT_SNOW,
                    PrecipitationType.HEAVY_SNOW,
                    PrecipitationType.SLEET
                ])
            
            precipitation_intensity = random.uniform(0.1, 1.0)
        
        # Видимость
        visibility = 1.0
        if weather_type in [WeatherType.FOG, WeatherType.STORM, WeatherType.EXTREME]:
            visibility = random.uniform(0.1, 0.5)
        elif weather_type in [WeatherType.RAIN, WeatherType.SNOW]:
            visibility = random.uniform(0.5, 0.8)
        
        # Давление
        pressure = random.uniform(980.0, 1020.0)
        
        return WeatherCondition(
            weather_type=weather_type,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            precipitation_type=precipitation_type,
            precipitation_intensity=precipitation_intensity,
            visibility=visibility,
            pressure=pressure
        )
    
    def _apply_biome_modifiers(self, weather: WeatherCondition, biome_type: str) -> WeatherCondition:
        """Применение модификаторов биома"""
        if biome_type not in self.biome_weather_modifiers:
            return weather
        
        modifiers = self.biome_weather_modifiers[biome_type]
        
        modified_weather = WeatherCondition(
            weather_type=weather.weather_type,
            temperature=weather.temperature * modifiers.get("temperature_modifier", 1.0),
            humidity=weather.humidity * modifiers.get("humidity_modifier", 1.0),
            wind_speed=weather.wind_speed * modifiers.get("wind_modifier", 1.0),
            wind_direction=weather.wind_direction,
            precipitation_type=weather.precipitation_type,
            precipitation_intensity=weather.precipitation_intensity,
            visibility=weather.visibility,
            pressure=weather.pressure,
            duration=weather.duration,
            intensity=weather.intensity
        )
        
        return modified_weather
    
    def _apply_season_modifiers(self, weather: WeatherCondition, season: str) -> WeatherCondition:
        """Применение модификаторов сезона"""
        if season not in self.season_weather_modifiers:
            return weather
        
        modifiers = self.season_weather_modifiers[season]
        
        modified_weather = WeatherCondition(
            weather_type=weather.weather_type,
            temperature=weather.temperature * modifiers.get("temperature_modifier", 1.0),
            humidity=weather.humidity * modifiers.get("humidity_modifier", 1.0),
            wind_speed=weather.wind_speed,
            wind_direction=weather.wind_direction,
            precipitation_type=weather.precipitation_type,
            precipitation_intensity=weather.precipitation_intensity,
            visibility=weather.visibility,
            pressure=weather.pressure,
            duration=weather.duration,
            intensity=weather.intensity
        )
        
        return modified_weather
    
    def update_weather(self, delta_time: float):
        """Обновление погоды"""
        start_time = time.time()
        
        # Обновление глобальной погоды
        if self.global_weather:
            self.global_weather = self._update_weather_condition(
                self.global_weather, delta_time
            )
        
        # Обновление погодных зон
        for zone_id, zone in self.weather_zones.items():
            old_weather = zone.current_weather
            zone.current_weather = self._update_weather_condition(
                zone.current_weather, delta_time
            )
            
            # Проверка изменения погоды
            if zone.current_weather.weather_type != old_weather.weather_type:
                zone.weather_history.append(zone.current_weather)
                self.weather_stats["weather_changes"] += 1
                
                # Уведомление об изменении погоды
                self._notify_weather_changed(zone_id, old_weather, zone.current_weather)
                
                # Применение эффектов новой погоды
                self._apply_weather_effects(zone_id, zone.current_weather)
            
            zone.last_update = time.time()
        
        # Обновление статистики
        update_time = time.time() - start_time
        self.weather_stats["total_update_time"] += update_time
    
    def _update_weather_condition(self, weather: WeatherCondition, delta_time: float) -> WeatherCondition:
        """Обновление погодного условия"""
        # Увеличение длительности
        new_duration = weather.duration + delta_time
        
        # Проверка необходимости смены погоды
        if random.random() < self.settings.weather_change_rate * delta_time:
            # Создание новой погоды
            new_weather = self._create_base_weather()
            new_weather.duration = 0.0
            return new_weather
        
        # Плавное изменение параметров
        temperature_change = random.uniform(-0.1, 0.1) * delta_time
        humidity_change = random.uniform(-0.05, 0.05) * delta_time
        wind_change = random.uniform(-0.5, 0.5) * delta_time
        
        updated_weather = WeatherCondition(
            weather_type=weather.weather_type,
            temperature=weather.temperature + temperature_change,
            humidity=max(0.0, min(1.0, weather.humidity + humidity_change)),
            wind_speed=max(0.0, weather.wind_speed + wind_change),
            wind_direction=weather.wind_direction,
            precipitation_type=weather.precipitation_type,
            precipitation_intensity=weather.precipitation_intensity,
            visibility=weather.visibility,
            pressure=weather.pressure,
            duration=new_duration,
            intensity=weather.intensity
        )
        
        return updated_weather
    
    def get_weather_at_position(self, x: float, y: float) -> Optional[WeatherCondition]:
        """Получение погоды в позиции"""
        # Проверка погодных зон
        for zone in self.weather_zones.values():
            distance = math.sqrt((x - zone.center_x)**2 + (y - zone.center_y)**2)
            if distance <= zone.radius:
                return zone.current_weather
        
        # Возврат глобальной погоды
        return self.global_weather
    
    def _apply_weather_effects(self, zone_id: str, weather: WeatherCondition):
        """Применение эффектов погоды"""
        if weather.weather_type not in self.weather_effects:
            return
        
        effects = self.weather_effects[weather.weather_type]
        
        for effect in effects:
            effect_id = f"{zone_id}_{effect.effect_type}_{int(time.time())}"
            
            # Создание копии эффекта с уникальным ID
            active_effect = WeatherEffect(
                effect_type=effect.effect_type,
                intensity=effect.intensity * weather.intensity,
                duration=effect.duration,
                target_type=effect.target_type,
                description=effect.description,
                modifiers=effect.modifiers.copy()
            )
            
            self.active_effects[effect_id] = active_effect
            self.weather_stats["effects_applied"] += 1
            
            # Уведомление о применении эффекта
            self._notify_effect_applied(zone_id, active_effect)
    
    def get_active_effects(self, target_type: str = None) -> List[WeatherEffect]:
        """Получение активных эффектов"""
        if target_type:
            return [effect for effect in self.active_effects.values() 
                   if effect.target_type == target_type]
        
        return list(self.active_effects.values())
    
    def remove_effect(self, effect_id: str) -> bool:
        """Удаление эффекта"""
        if effect_id in self.active_effects:
            del self.active_effects[effect_id]
            return True
        
        return False
    
    def get_weather_forecast(self, zone_id: str, hours: int = 24) -> List[WeatherCondition]:
        """Получение прогноза погоды"""
        if zone_id not in self.weather_zones:
            return []
        
        zone = self.weather_zones[zone_id]
        forecast = []
        
        # Симуляция погоды на указанное время
        current_weather = zone.current_weather
        current_time = 0.0
        
        while current_time < hours * 3600:  # Конвертация в секунды
            # Обновление погоды
            current_weather = self._update_weather_condition(current_weather, 3600)  # 1 час
            
            # Добавление в прогноз каждый час
            if len(forecast) < hours:
                forecast.append(current_weather)
            
            current_time += 3600
        
        return forecast
    
    def add_weather_changed_callback(self, callback: callable):
        """Добавление callback для изменения погоды"""
        self.weather_changed_callbacks.append(callback)
    
    def add_effect_applied_callback(self, callback: callable):
        """Добавление callback для применения эффекта"""
        self.effect_applied_callbacks.append(callback)
    
    def _notify_weather_changed(self, zone_id: str, old_weather: WeatherCondition, 
                               new_weather: WeatherCondition):
        """Уведомление об изменении погоды"""
        for callback in self.weather_changed_callbacks:
            try:
                callback(zone_id, old_weather, new_weather)
            except Exception as e:
                self.logger.error(f"Ошибка в callback изменения погоды: {e}")
    
    def _notify_effect_applied(self, zone_id: str, effect: WeatherEffect):
        """Уведомление о применении эффекта"""
        for callback in self.effect_applied_callbacks:
            try:
                callback(zone_id, effect)
            except Exception as e:
                self.logger.error(f"Ошибка в callback применения эффекта: {e}")
    
    def get_weather_statistics(self) -> Dict[str, Any]:
        """Получение статистики погоды"""
        zone_stats = {}
        
        for zone_id, zone in self.weather_zones.items():
            zone_stats[zone_id] = {
                "biome_type": zone.biome_type,
                "season": zone.season,
                "current_weather": zone.current_weather.weather_type.value,
                "temperature": zone.current_weather.temperature,
                "humidity": zone.current_weather.humidity,
                "wind_speed": zone.current_weather.wind_speed,
                "precipitation_type": zone.current_weather.precipitation_type.value,
                "visibility": zone.current_weather.visibility,
                "weather_changes": len(zone.weather_history),
                "created_at": zone.created_at,
                "last_update": zone.last_update
            }
        
        return {
            "total_zones": len(self.weather_zones),
            "active_effects": len(self.active_effects),
            "global_weather": self.global_weather.weather_type.value if self.global_weather else None,
            "zone_statistics": zone_stats,
            "system_statistics": self.weather_stats.copy()
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self.weather_cache.clear()
        self.logger.info("Кэш WeatherSystem очищен")
    
    def _on_destroy(self):
        """Уничтожение системы погоды"""
        self.weather_zones.clear()
        self.active_effects.clear()
        self.weather_cache.clear()
        self.weather_changed_callbacks.clear()
        self.effect_applied_callbacks.clear()
        
        self.logger.info("WeatherSystem уничтожен")
