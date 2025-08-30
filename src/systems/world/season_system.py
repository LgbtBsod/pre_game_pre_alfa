#!/usr/bin/env python3
"""Система сезонов для игрового мира
Включает сезонные изменения, миграцию животных и сезонные события"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = СЕЗОНЫ
class Season(Enum):
    """Сезоны"""
    SPRING = "spring"     # Весна
    SUMMER = "summer"     # Лето
    AUTUMN = "autumn"     # Осень
    WINTER = "winter"     # Зима

# = СЕЗОННЫЕ СОБЫТИЯ
class SeasonalEvent(Enum):
    """Сезонные события"""
    SPRING_EQUINOX = "spring_equinox"     # Весеннее равноденствие
    SUMMER_SOLSTICE = "summer_solstice"   # Летнее солнцестояние
    AUTUMN_EQUINOX = "autumn_equinox"     # Осеннее равноденствие
    WINTER_SOLSTICE = "winter_solstice"   # Зимнее солнцестояние
    HARVEST_FESTIVAL = "harvest_festival" # Праздник урожая
    WINTER_FESTIVAL = "winter_festival"   # Зимний праздник
    SPRING_FESTIVAL = "spring_festival"   # Весенний праздник
    SUMMER_FESTIVAL = "summer_festival"   # Летний праздник

# = НАСТРОЙКИ СЕЗОНОВ
@dataclass
class SeasonSettings:
    """Настройки сезонов"""
    days_per_season: int = 90
    transition_days: int = 7
    event_duration_days: int = 3
    migration_enabled: bool = True
    seasonal_effects_enabled: bool = True

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class SeasonData:
    """Данные сезона"""
    current_season: Season
    day_in_season: int
    season_progress: float  # 0.0 - 1.0
    temperature_modifier: float
    humidity_modifier: float
    wind_modifier: float
    precipitation_chance: float
    vegetation_growth: float
    animal_activity: float
    created_at: float = field(default_factory=time.time)

@dataclass
class SeasonalEventData:
    """Данные сезонного события"""
    event_type: SeasonalEvent
    start_day: int
    duration_days: int
    active: bool = False
    effects: Dict[str, float] = field(default_factory=dict)
    description: str = ""

@dataclass
class MigrationData:
    """Данные миграции"""
    animal_type: str
    source_biome: str
    destination_biome: str
    start_day: int
    duration_days: int
    population_size: int
    active: bool = False

@dataclass
class SeasonalEffect:
    """Сезонный эффект"""
    effect_type: str
    season: Season
    intensity: float
    target_type: str  # player, npc, environment, animals
    description: str
    modifiers: Dict[str, float] = field(default_factory=dict)

# = СИСТЕМА СЕЗОНОВ
class SeasonSystem(BaseComponent):
    """Система сезонов"""
    
    def __init__(self):
        super().__init__(
            component_id="SeasonSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки системы
        self.settings = SeasonSettings()
        self.current_season_data: Optional[SeasonData] = None
        
        # Сезонные события
        self.seasonal_events: Dict[str, SeasonalEventData] = {}
        self.active_events: List[SeasonalEventData] = []
        
        # Миграция животных
        self.migrations: Dict[str, MigrationData] = {}
        self.active_migrations: List[MigrationData] = []
        
        # Сезонные эффекты
        self.seasonal_effects: Dict[Season, List[SeasonalEffect]] = {}
        self.active_effects: Dict[str, SeasonalEffect] = {}
        
        # Кэши и статистика
        self.season_cache: Dict[str, Any] = {}
        self.season_stats = {
            "seasons_completed": 0,
            "events_triggered": 0,
            "migrations_started": 0,
            "effects_applied": 0,
            "total_update_time": 0.0
        }
        
        # Слушатели событий
        self.season_changed_callbacks: List[callable] = []
        self.event_started_callbacks: List[callable] = []
        self.migration_started_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация системы сезонов"""
        try:
            # Инициализация сезонных данных
            self.current_season_data = self._create_initial_season()
            
            # Инициализация сезонных событий
            self._initialize_seasonal_events()
            
            # Инициализация миграций
            self._initialize_migrations()
            
            # Инициализация сезонных эффектов
            self._initialize_seasonal_effects()
            
            self.logger.info("SeasonSystem инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации SeasonSystem: {e}")
            return False
    
    def _create_initial_season(self) -> SeasonData:
        """Создание начального сезона"""
        current_season = Season.SPRING
        day_in_season = 1
        season_progress = 0.0
        
        # Базовые модификаторы для весны
        temperature_modifier = 0.8
        humidity_modifier = 1.2
        wind_modifier = 1.1
        precipitation_chance = 0.4
        vegetation_growth = 1.5
        animal_activity = 1.2
        
        return SeasonData(
            current_season=current_season,
            day_in_season=day_in_season,
            season_progress=season_progress,
            temperature_modifier=temperature_modifier,
            humidity_modifier=humidity_modifier,
            wind_modifier=wind_modifier,
            precipitation_chance=precipitation_chance,
            vegetation_growth=vegetation_growth,
            animal_activity=animal_activity
        )
    
    def _initialize_seasonal_events(self):
        """Инициализация сезонных событий"""
        # Весенние события
        self.seasonal_events["spring_equinox"] = SeasonalEventData(
            event_type=SeasonalEvent.SPRING_EQUINOX,
            start_day=20,
            duration_days=self.settings.event_duration_days,
            effects={"temperature_modifier": 1.1, "vegetation_growth": 2.0},
            description="Весеннее равноденствие - пробуждение природы"
        )
        
        self.seasonal_events["spring_festival"] = SeasonalEventData(
            event_type=SeasonalEvent.SPRING_FESTIVAL,
            start_day=45,
            duration_days=self.settings.event_duration_days,
            effects={"animal_activity": 1.5, "precipitation_chance": 0.6},
            description="Весенний праздник - празднование новой жизни"
        )
        
        # Летние события
        self.seasonal_events["summer_solstice"] = SeasonalEventData(
            event_type=SeasonalEvent.SUMMER_SOLSTICE,
            start_day=20,
            duration_days=self.settings.event_duration_days,
            effects={"temperature_modifier": 1.3, "animal_activity": 1.8},
            description="Летнее солнцестояние - самый длинный день"
        )
        
        self.seasonal_events["summer_festival"] = SeasonalEventData(
            event_type=SeasonalEvent.SUMMER_FESTIVAL,
            start_day=60,
            duration_days=self.settings.event_duration_days,
            effects={"vegetation_growth": 1.8, "humidity_modifier": 0.8},
            description="Летний праздник - праздник солнца"
        )
        
        # Осенние события
        self.seasonal_events["autumn_equinox"] = SeasonalEventData(
            event_type=SeasonalEvent.AUTUMN_EQUINOX,
            start_day=20,
            duration_days=self.settings.event_duration_days,
            effects={"temperature_modifier": 0.9, "wind_modifier": 1.3},
            description="Осеннее равноденствие - подготовка к зиме"
        )
        
        self.seasonal_events["harvest_festival"] = SeasonalEventData(
            event_type=SeasonalEvent.HARVEST_FESTIVAL,
            start_day=70,
            duration_days=self.settings.event_duration_days,
            effects={"vegetation_growth": 0.5, "animal_activity": 1.4},
            description="Праздник урожая - сбор даров природы"
        )
        
        # Зимние события
        self.seasonal_events["winter_solstice"] = SeasonalEventData(
            event_type=SeasonalEvent.WINTER_SOLSTICE,
            start_day=20,
            duration_days=self.settings.event_duration_days,
            effects={"temperature_modifier": 0.6, "precipitation_chance": 0.8},
            description="Зимнее солнцестояние - самый короткий день"
        )
        
        self.seasonal_events["winter_festival"] = SeasonalEventData(
            event_type=SeasonalEvent.WINTER_FESTIVAL,
            start_day=75,
            duration_days=self.settings.event_duration_days,
            effects={"animal_activity": 0.5, "wind_modifier": 0.8},
            description="Зимний праздник - праздник света"
        )
    
    def _initialize_migrations(self):
        """Инициализация миграций"""
        # Весенние миграции
        self.migrations["spring_birds"] = MigrationData(
            animal_type="birds",
            source_biome="south",
            destination_biome="north",
            start_day=15,
            duration_days=30,
            population_size=1000
        )
        
        # Осенние миграции
        self.migrations["autumn_birds"] = MigrationData(
            animal_type="birds",
            source_biome="north",
            destination_biome="south",
            start_day=75,
            duration_days=30,
            population_size=1000
        )
        
        # Летние миграции
        self.migrations["summer_herds"] = MigrationData(
            animal_type="herbivores",
            source_biome="forest",
            destination_biome="plains",
            start_day=30,
            duration_days=45,
            population_size=500
        )
        
        # Зимние миграции
        self.migrations["winter_herds"] = MigrationData(
            animal_type="herbivores",
            source_biome="plains",
            destination_biome="forest",
            start_day=15,
            duration_days=30,
            population_size=500
        )
    
    def _initialize_seasonal_effects(self):
        """Инициализация сезонных эффектов"""
        # Весенние эффекты
        self.seasonal_effects[Season.SPRING] = [
            SeasonalEffect(
                effect_type="regeneration",
                season=Season.SPRING,
                intensity=1.2,
                target_type="player",
                description="Весеннее обновление - ускоренная регенерация",
                modifiers={"health_regeneration": 1.2, "stamina_regeneration": 1.1}
            ),
            SeasonalEffect(
                effect_type="growth",
                season=Season.SPRING,
                intensity=1.5,
                target_type="environment",
                description="Весенний рост - ускоренный рост растений",
                modifiers={"plant_growth": 1.5, "crop_yield": 1.3}
            )
        ]
        
        # Летние эффекты
        self.seasonal_effects[Season.SUMMER] = [
            SeasonalEffect(
                effect_type="heat",
                season=Season.SUMMER,
                intensity=1.0,
                target_type="player",
                description="Летняя жара - повышенная потребность в воде",
                modifiers={"hydration_loss": 1.5, "heat_resistance": 0.8}
            ),
            SeasonalEffect(
                effect_type="activity",
                season=Season.SUMMER,
                intensity=1.3,
                target_type="animals",
                description="Летняя активность - повышенная активность животных",
                modifiers={"animal_activity": 1.3, "spawn_rate": 1.2}
            )
        ]
        
        # Осенние эффекты
        self.seasonal_effects[Season.AUTUMN] = [
            SeasonalEffect(
                effect_type="harvest",
                season=Season.AUTUMN,
                intensity=1.4,
                target_type="environment",
                description="Осенний урожай - увеличенный урожай",
                modifiers={"crop_yield": 1.4, "resource_gathering": 1.2}
            ),
            SeasonalEffect(
                effect_type="preparation",
                season=Season.AUTUMN,
                intensity=1.1,
                target_type="animals",
                description="Осенняя подготовка - животные готовятся к зиме",
                modifiers={"animal_aggression": 1.1, "food_consumption": 1.3}
            )
        ]
        
        # Зимние эффекты
        self.seasonal_effects[Season.WINTER] = [
            SeasonalEffect(
                effect_type="cold",
                season=Season.WINTER,
                intensity=1.0,
                target_type="player",
                description="Зимний холод - повышенная потребность в тепле",
                modifiers={"body_temperature": 0.7, "cold_resistance": 0.8}
            ),
            SeasonalEffect(
                effect_type="hibernation",
                season=Season.WINTER,
                intensity=0.5,
                target_type="animals",
                description="Зимняя спячка - сниженная активность животных",
                modifiers={"animal_activity": 0.5, "spawn_rate": 0.7}
            )
        ]
    
    def update_season(self, day_of_year: int):
        """Обновление сезона"""
        start_time = time.time()
        
        if not self.current_season_data:
            return
        
        old_season = self.current_season_data.current_season
        
        # Определение текущего сезона
        season_day = (day_of_year - 1) % (self.settings.days_per_season * 4)
        season_index = season_day // self.settings.days_per_season
        day_in_season = (season_day % self.settings.days_per_season) + 1
        
        # Обновление сезона
        seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
        current_season = seasons[season_index]
        
        # Обновление прогресса сезона
        season_progress = day_in_season / self.settings.days_per_season
        
        # Обновление модификаторов
        modifiers = self._calculate_season_modifiers(current_season, season_progress)
        
        # Обновление данных сезона
        self.current_season_data.current_season = current_season
        self.current_season_data.day_in_season = day_in_season
        self.current_season_data.season_progress = season_progress
        self.current_season_data.temperature_modifier = modifiers["temperature"]
        self.current_season_data.humidity_modifier = modifiers["humidity"]
        self.current_season_data.wind_modifier = modifiers["wind"]
        self.current_season_data.precipitation_chance = modifiers["precipitation"]
        self.current_season_data.vegetation_growth = modifiers["vegetation"]
        self.current_season_data.animal_activity = modifiers["activity"]
        
        # Проверка смены сезона
        if current_season != old_season:
            self.season_stats["seasons_completed"] += 1
            self._notify_season_changed(old_season, current_season)
            self._apply_seasonal_effects(current_season)
        
        # Обновление событий
        self._update_seasonal_events(day_in_season)
        
        # Обновление миграций
        self._update_migrations(day_in_season)
        
        self.season_stats["total_update_time"] += time.time() - start_time
    
    def _calculate_season_modifiers(self, season: Season, progress: float) -> Dict[str, float]:
        """Расчет модификаторов сезона"""
        base_modifiers = {
            Season.SPRING: {
                "temperature": 0.8,
                "humidity": 1.2,
                "wind": 1.1,
                "precipitation": 0.4,
                "vegetation": 1.5,
                "activity": 1.2
            },
            Season.SUMMER: {
                "temperature": 1.3,
                "humidity": 0.9,
                "wind": 0.8,
                "precipitation": 0.2,
                "vegetation": 1.8,
                "activity": 1.5
            },
            Season.AUTUMN: {
                "temperature": 0.9,
                "humidity": 1.1,
                "wind": 1.3,
                "precipitation": 0.5,
                "vegetation": 0.7,
                "activity": 1.0
            },
            Season.WINTER: {
                "temperature": 0.5,
                "humidity": 0.8,
                "wind": 1.2,
                "precipitation": 0.7,
                "vegetation": 0.3,
                "activity": 0.6
            }
        }
        
        modifiers = base_modifiers[season].copy()
        
        # Плавные переходы между сезонами
        if progress < 0.1:  # Начало сезона
            transition_factor = progress / 0.1
            # Интерполяция с предыдущим сезоном
            pass
        elif progress > 0.9:  # Конец сезона
            transition_factor = (1.0 - progress) / 0.1
            # Интерполяция со следующим сезоном
            pass
        
        return modifiers
    
    def _update_seasonal_events(self, day_in_season: int):
        """Обновление сезонных событий"""
        current_season = self.current_season_data.current_season
        
        # Проверка событий для текущего сезона
        for event_id, event in self.seasonal_events.items():
            if event.start_day <= day_in_season <= event.start_day + event.duration_days:
                if not event.active:
                    event.active = True
                    self.active_events.append(event)
                    self.season_stats["events_triggered"] += 1
                    self._notify_event_started(event)
            else:
                if event.active:
                    event.active = False
                    if event in self.active_events:
                        self.active_events.remove(event)
    
    def _update_migrations(self, day_in_season: int):
        """Обновление миграций"""
        current_season = self.current_season_data.current_season
        
        # Проверка миграций для текущего сезона
        for migration_id, migration in self.migrations.items():
            if migration.start_day <= day_in_season <= migration.start_day + migration.duration_days:
                if not migration.active:
                    migration.active = True
                    self.active_migrations.append(migration)
                    self.season_stats["migrations_started"] += 1
                    self._notify_migration_started(migration)
            else:
                if migration.active:
                    migration.active = False
                    if migration in self.active_migrations:
                        self.active_migrations.remove(migration)
    
    def _apply_seasonal_effects(self, season: Season):
        """Применение сезонных эффектов"""
        if season not in self.seasonal_effects:
            return
        
        effects = self.seasonal_effects[season]
        
        for effect in effects:
            effect_id = f"{season.value}_{effect.effect_type}_{int(time.time())}"
            
            # Создание активного эффекта
            active_effect = SeasonalEffect(
                effect_type=effect.effect_type,
                season=effect.season,
                intensity=effect.intensity,
                target_type=effect.target_type,
                description=effect.description,
                modifiers=effect.modifiers.copy()
            )
            
            self.active_effects[effect_id] = active_effect
            self.season_stats["effects_applied"] += 1
    
    def get_current_season_data(self) -> Optional[SeasonData]:
        """Получение текущих данных сезона"""
        return self.current_season_data
    
    def get_active_events(self) -> List[SeasonalEventData]:
        """Получение активных событий"""
        return self.active_events.copy()
    
    def get_active_migrations(self) -> List[MigrationData]:
        """Получение активных миграций"""
        return self.active_migrations.copy()
    
    def get_active_effects(self, target_type: str = None) -> List[SeasonalEffect]:
        """Получение активных эффектов"""
        if target_type:
            return [effect for effect in self.active_effects.values() 
                   if effect.target_type == target_type]
        
        return list(self.active_effects.values())
    
    def get_season_progress(self) -> float:
        """Получение прогресса текущего сезона"""
        if not self.current_season_data:
            return 0.0
        
        return self.current_season_data.season_progress
    
    def get_next_season(self) -> Season:
        """Получение следующего сезона"""
        if not self.current_season_data:
            return Season.SPRING
        
        seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
        current_index = seasons.index(self.current_season_data.current_season)
        next_index = (current_index + 1) % 4
        
        return seasons[next_index]
    
    def get_days_until_next_season(self) -> int:
        """Получение дней до следующего сезона"""
        if not self.current_season_data:
            return 0
        
        return self.settings.days_per_season - self.current_season_data.day_in_season
    
    def add_season_changed_callback(self, callback: callable):
        """Добавление callback для смены сезона"""
        self.season_changed_callbacks.append(callback)
    
    def add_event_started_callback(self, callback: callable):
        """Добавление callback для начала события"""
        self.event_started_callbacks.append(callback)
    
    def add_migration_started_callback(self, callback: callable):
        """Добавление callback для начала миграции"""
        self.migration_started_callbacks.append(callback)
    
    def _notify_season_changed(self, old_season: Season, new_season: Season):
        """Уведомление о смене сезона"""
        for callback in self.season_changed_callbacks:
            try:
                callback(old_season, new_season)
            except Exception as e:
                self.logger.error(f"Ошибка в callback смены сезона: {e}")
    
    def _notify_event_started(self, event: SeasonalEventData):
        """Уведомление о начале события"""
        for callback in self.event_started_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Ошибка в callback начала события: {e}")
    
    def _notify_migration_started(self, migration: MigrationData):
        """Уведомление о начале миграции"""
        for callback in self.migration_started_callbacks:
            try:
                callback(migration)
            except Exception as e:
                self.logger.error(f"Ошибка в callback начала миграции: {e}")
    
    def get_season_statistics(self) -> Dict[str, Any]:
        """Получение статистики сезонов"""
        if not self.current_season_data:
            return {}
        
        return {
            "current_season": self.current_season_data.current_season.value,
            "day_in_season": self.current_season_data.day_in_season,
            "season_progress": self.current_season_data.season_progress,
            "next_season": self.get_next_season().value,
            "days_until_next_season": self.get_days_until_next_season(),
            "active_events": len(self.active_events),
            "active_migrations": len(self.active_migrations),
            "active_effects": len(self.active_effects),
            "season_modifiers": {
                "temperature": self.current_season_data.temperature_modifier,
                "humidity": self.current_season_data.humidity_modifier,
                "wind": self.current_season_data.wind_modifier,
                "precipitation": self.current_season_data.precipitation_chance,
                "vegetation": self.current_season_data.vegetation_growth,
                "activity": self.current_season_data.animal_activity
            },
            "system_statistics": self.season_stats.copy()
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self.season_cache.clear()
        self.logger.info("Кэш SeasonSystem очищен")
    
    def _on_destroy(self):
        """Уничтожение системы сезонов"""
        self.season_cache.clear()
        self.season_changed_callbacks.clear()
        self.event_started_callbacks.clear()
        self.migration_started_callbacks.clear()
        
        self.logger.info("SeasonSystem уничтожен")
