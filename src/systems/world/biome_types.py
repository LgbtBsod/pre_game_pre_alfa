#!/usr/bin/env python3
"""
Типы биомов и экологические системы
Система биомов для процедурной генерации мира
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import random

class BiomeType(Enum):
    """Типы биомов"""
    # Лесные биомы
    TEMPERATE_FOREST = "temperate_forest"      # Умеренный лес
    BOREAL_FOREST = "boreal_forest"            # Бореальный лес
    TROPICAL_FOREST = "tropical_forest"        # Тропический лес
    RAINFOREST = "rainforest"                  # Дождевой лес
    
    # Пустынные биомы
    DESERT = "desert"                          # Пустыня
    SAVANNA = "savanna"                        # Саванна
    STEPPE = "steppe"                          # Степь
    TUNDRA = "tundra"                          # Тундра
    
    # Горные биомы
    MOUNTAINS = "mountains"                    # Горы
    VOLCANIC = "volcanic"                      # Вулканические
    GLACIER = "glacier"                        # Ледниковые
    HILLS = "hills"                            # Холмы
    
    # Водные биомы
    OCEAN = "ocean"                            # Океан
    RIVER = "river"                            # Река
    LAKE = "lake"                              # Озеро
    SWAMP = "swamp"                            # Болото
    BEACH = "beach"                            # Пляж
    
    # Специальные биомы
    CAVE = "cave"                              # Пещера
    RUINS = "ruins"                            # Руины
    CRYSTAL_CAVE = "crystal_cave"              # Кристальная пещера
    UNDERWATER = "underwater"                  # Подводный

class ClimateType(Enum):
    """Типы климата"""
    TROPICAL = "tropical"                      # Тропический
    SUBTROPICAL = "subtropical"                # Субтропический
    TEMPERATE = "temperate"                    # Умеренный
    SUBARCTIC = "subarctic"                    # Субарктический
    ARCTIC = "arctic"                          # Арктический
    DESERT = "desert"                          # Пустынный
    ALPINE = "alpine"                          # Альпийский

class SeasonType(Enum):
    """Типы сезонов"""
    SPRING = "spring"                          # Весна
    SUMMER = "summer"                          # Лето
    AUTUMN = "autumn"                          # Осень
    WINTER = "winter"                          # Зима
    DRY = "dry"                                # Сухой сезон
    WET = "wet"                                # Влажный сезон

class WeatherType(Enum):
    """Типы погоды"""
    CLEAR = "clear"                            # Ясно
    CLOUDY = "cloudy"                          # Облачно
    RAIN = "rain"                              # Дождь
    SNOW = "snow"                              # Снег
    STORM = "storm"                            # Буря
    FOG = "fog"                                # Туман
    WINDY = "windy"                            # Ветрено
    HOT = "hot"                                # Жарко
    COLD = "cold"                              # Холодно

@dataclass
class BiomeProperties:
    """Свойства биома"""
    name: str
    description: str
    temperature_range: Tuple[float, float]     # Минимальная и максимальная температура
    humidity_range: Tuple[float, float]        # Минимальная и максимальная влажность
    elevation_range: Tuple[float, float]       # Минимальная и максимальная высота
    vegetation_density: float                  # Плотность растительности (0.0 - 1.0)
    water_availability: float                  # Доступность воды (0.0 - 1.0)
    resource_richness: float                   # Богатство ресурсов (0.0 - 1.0)
    danger_level: float                        # Уровень опасности (0.0 - 1.0)
    travel_difficulty: float                   # Сложность передвижения (0.0 - 1.0)
    
    # Визуальные свойства
    ground_texture: str                        # Текстура земли
    vegetation_texture: str                    # Текстура растительности
    sky_color: Tuple[float, float, float]     # Цвет неба (RGB)
    ambient_light: float                      # Окружающее освещение
    
    # Аудио свойства
    ambient_sounds: List[str]                  # Окружающие звуки
    music_track: Optional[str]                 # Музыкальная дорожка
    
    # Игровые эффекты
    movement_speed_modifier: float             # Модификатор скорости движения
    stamina_drain_modifier: float              # Модификатор расхода выносливости
    health_regen_modifier: float               # Модификатор восстановления здоровья
    experience_gain_modifier: float            # Модификатор получения опыта

@dataclass
class ClimateProperties:
    """Свойства климата"""
    name: str
    description: str
    base_temperature: float                    # Базовая температура
    temperature_variation: float               # Вариация температуры
    base_humidity: float                       # Базовая влажность
    humidity_variation: float                  # Вариация влажности
    wind_strength: float                       # Сила ветра
    precipitation_frequency: float             # Частота осадков
    seasonal_changes: bool                     # Есть ли сезонные изменения
    
    # Сезонные модификаторы
    spring_modifiers: Dict[str, float]         # Модификаторы весны
    summer_modifiers: Dict[str, float]         # Модификаторы лета
    autumn_modifiers: Dict[str, float]         # Модификаторы осени
    winter_modifiers: Dict[str, float]         # Модификаторы зимы

@dataclass
class WeatherProperties:
    """Свойства погоды"""
    name: str
    description: str
    temperature_modifier: float                # Модификатор температуры
    humidity_modifier: float                   # Модификатор влажности
    visibility_modifier: float                 # Модификатор видимости
    movement_modifier: float                   # Модификатор движения
    
    # Визуальные эффекты
    particle_effects: List[str]                # Эффекты частиц
    lighting_modifier: float                   # Модификатор освещения
    fog_density: float                         # Плотность тумана
    
    # Аудио эффекты
    sound_effects: List[str]                   # Звуковые эффекты
    volume_modifier: float                     # Модификатор громкости
    
    # Игровые эффекты
    combat_modifier: float                     # Модификатор боя
    exploration_modifier: float                # Модификатор исследования
    survival_modifier: float                   # Модификатор выживания

class BiomeManager:
    """Менеджер биомов"""
    
    def __init__(self):
        self.biomes: Dict[BiomeType, BiomeProperties] = {}
        self.climates: Dict[ClimateType, ClimateProperties] = {}
        self.weather_types: Dict[WeatherType, WeatherProperties] = {}
        
        self._initialize_default_biomes()
        self._initialize_default_climates()
        self._initialize_default_weather()
    
    def _initialize_default_biomes(self):
        """Инициализация стандартных биомов"""
        
        # Умеренный лес
        self.biomes[BiomeType.TEMPERATE_FOREST] = BiomeProperties(
            name="Умеренный лес",
            description="Лиственные деревья, умеренный климат, богатая фауна",
            temperature_range=(5.0, 25.0),
            humidity_range=(0.4, 0.8),
            elevation_range=(0.0, 500.0),
            vegetation_density=0.8,
            water_availability=0.7,
            resource_richness=0.7,
            danger_level=0.3,
            travel_difficulty=0.4,
            ground_texture="forest_ground",
            vegetation_texture="temperate_trees",
            sky_color=(0.6, 0.8, 1.0),
            ambient_light=0.8,
            ambient_sounds=["forest_ambient", "bird_songs", "wind_leaves"],
            music_track="temperate_forest_theme",
            movement_speed_modifier=0.9,
            stamina_drain_modifier=1.1,
            health_regen_modifier=1.2,
            experience_gain_modifier=1.1
        )
        
        # Пустыня
        self.biomes[BiomeType.DESERT] = BiomeProperties(
            name="Пустыня",
            description="Песчаные дюны, жаркий климат, скудная растительность",
            temperature_range=(20.0, 45.0),
            humidity_range=(0.0, 0.2),
            elevation_range=(0.0, 300.0),
            vegetation_density=0.1,
            water_availability=0.1,
            resource_richness=0.3,
            danger_level=0.6,
            travel_difficulty=0.8,
            ground_texture="desert_sand",
            vegetation_texture="desert_plants",
            sky_color=(1.0, 0.9, 0.7),
            ambient_light=1.2,
            ambient_sounds=["desert_wind", "sand_storm"],
            music_track="desert_theme",
            movement_speed_modifier=0.7,
            stamina_drain_modifier=1.5,
            health_regen_modifier=0.8,
            experience_gain_modifier=1.3
        )
        
        # Горы
        self.biomes[BiomeType.MOUNTAINS] = BiomeProperties(
            name="Горы",
            description="Скалистые вершины, холодный климат, сложная навигация",
            temperature_range=(-10.0, 15.0),
            humidity_range=(0.3, 0.7),
            elevation_range=(500.0, 2000.0),
            vegetation_density=0.4,
            water_availability=0.6,
            resource_richness=0.8,
            danger_level=0.7,
            travel_difficulty=0.9,
            ground_texture="mountain_rock",
            vegetation_texture="mountain_plants",
            sky_color=(0.7, 0.8, 1.0),
            ambient_light=0.9,
            ambient_sounds=["mountain_wind", "avalanche_risk"],
            music_track="mountain_theme",
            movement_speed_modifier=0.6,
            stamina_drain_modifier=1.8,
            health_regen_modifier=0.9,
            experience_gain_modifier=1.4
        )
        
        # Озеро
        self.biomes[BiomeType.LAKE] = BiomeProperties(
            name="Озеро",
            description="Пресная вода, умеренный климат, рыбные ресурсы",
            temperature_range=(0.0, 30.0),
            humidity_range=(0.8, 1.0),
            elevation_range=(0.0, 100.0),
            vegetation_density=0.6,
            water_availability=1.0,
            resource_richness=0.6,
            danger_level=0.2,
            travel_difficulty=0.3,
            ground_texture="lake_water",
            vegetation_texture="water_plants",
            sky_color=(0.5, 0.7, 1.0),
            ambient_light=0.7,
            ambient_sounds=["water_splash", "frog_croak"],
            music_track="lake_theme",
            movement_speed_modifier=1.0,
            stamina_drain_modifier=1.0,
            health_regen_modifier=1.1,
            experience_gain_modifier=1.0
        )
    
    def _initialize_default_climates(self):
        """Инициализация стандартных климатов"""
        
        # Умеренный климат
        self.climates[ClimateType.TEMPERATE] = ClimateProperties(
            name="Умеренный",
            description="Умеренные температуры, четкие сезоны",
            base_temperature=15.0,
            temperature_variation=20.0,
            base_humidity=0.6,
            humidity_variation=0.3,
            wind_strength=0.4,
            precipitation_frequency=0.5,
            seasonal_changes=True,
            spring_modifiers={"temperature": 1.2, "humidity": 1.3},
            summer_modifiers={"temperature": 1.8, "humidity": 0.8},
            autumn_modifiers={"temperature": 0.8, "humidity": 1.1},
            winter_modifiers={"temperature": 0.3, "humidity": 0.9}
        )
        
        # Тропический климат
        self.climates[ClimateType.TROPICAL] = ClimateProperties(
            name="Тропический",
            description="Высокие температуры, высокая влажность",
            base_temperature=30.0,
            temperature_variation=10.0,
            base_humidity=0.8,
            humidity_variation=0.2,
            wind_strength=0.3,
            precipitation_frequency=0.8,
            seasonal_changes=False,
            spring_modifiers={},
            summer_modifiers={},
            autumn_modifiers={},
            winter_modifiers={}
        )
    
    def _initialize_default_weather(self):
        """Инициализация стандартных типов погоды"""
        
        # Ясная погода
        self.weather_types[WeatherType.CLEAR] = WeatherProperties(
            name="Ясно",
            description="Чистое небо, хорошая видимость",
            temperature_modifier=1.0,
            humidity_modifier=1.0,
            visibility_modifier=1.0,
            movement_modifier=1.0,
            particle_effects=[],
            lighting_modifier=1.0,
            fog_density=0.0,
            sound_effects=[],
            volume_modifier=1.0,
            combat_modifier=1.0,
            exploration_modifier=1.0,
            survival_modifier=1.0
        )
        
        # Дождь
        self.weather_types[WeatherType.RAIN] = WeatherProperties(
            name="Дождь",
            description="Осадки, сниженная видимость",
            temperature_modifier=0.9,
            humidity_modifier=1.3,
            visibility_modifier=0.7,
            movement_modifier=0.8,
            particle_effects=["rain_drops", "water_splash"],
            lighting_modifier=0.8,
            fog_density=0.2,
            sound_effects=["rain_sound", "thunder"],
            volume_modifier=1.2,
            combat_modifier=0.9,
            exploration_modifier=0.8,
            survival_modifier=0.9
        )
    
    def get_biome_properties(self, biome_type: BiomeType) -> Optional[BiomeProperties]:
        """Получение свойств биома"""
        return self.biomes.get(biome_type)
    
    def get_climate_properties(self, climate_type: ClimateType) -> Optional[ClimateProperties]:
        """Получение свойств климата"""
        return self.climates.get(climate_type)
    
    def get_weather_properties(self, weather_type: WeatherType) -> Optional[WeatherProperties]:
        """Получение свойств погоды"""
        return self.weather_types.get(weather_type)
    
    def determine_biome(self, temperature: float, humidity: float, elevation: float) -> BiomeType:
        """Определение биома по параметрам"""
        best_biome = BiomeType.TEMPERATE_FOREST
        best_score = 0.0
        
        for biome_type, properties in self.biomes.items():
            # Вычисляем оценку соответствия
            temp_score = 1.0 - abs(temperature - (properties.temperature_range[0] + properties.temperature_range[1]) / 2) / 25.0
            humidity_score = 1.0 - abs(humidity - (properties.humidity_range[0] + properties.humidity_range[1]) / 2)
            elevation_score = 1.0 - abs(elevation - (properties.elevation_range[0] + properties.elevation_range[1]) / 2) / 1000.0
            
            # Общая оценка
            total_score = (temp_score + humidity_score + elevation_score) / 3.0
            
            if total_score > best_score:
                best_score = total_score
                best_biome = biome_type
        
        return best_biome
    
    def get_random_weather(self, climate_type: ClimateType) -> WeatherType:
        """Получение случайной погоды для климата"""
        # Простая логика выбора погоды
        if climate_type == ClimateType.TROPICAL:
            return random.choice([WeatherType.RAIN, WeatherType.CLEAR, WeatherType.STORM])
        elif climate_type == ClimateType.TEMPERATE:
            return random.choice([WeatherType.CLEAR, WeatherType.CLOUDY, WeatherType.RAIN])
        else:
            return random.choice([WeatherType.CLEAR, WeatherType.CLOUDY, WeatherType.SNOW])
    
    def get_all_biomes(self) -> List[BiomeType]:
        """Получение всех типов биомов"""
        return list(self.biomes.keys())
    
    def get_all_climates(self) -> List[ClimateType]:
        """Получение всех типов климатов"""
        return list(self.climates.keys())
    
    def get_all_weather_types(self) -> List[WeatherType]:
        """Получение всех типов погоды"""
        return list(self.weather_types.keys())
