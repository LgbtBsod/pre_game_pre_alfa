#!/usr/bin/env python3
"""Интегратор всех систем мира
Координирует работу всех систем мира и обеспечивает их взаимодействие"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import time
import math
import threading
from concurrent.futures import ThreadPoolExecutor

from src.core.architecture import BaseComponent, ComponentType, Priority

# Импорты систем мира
from src.systems.world.height_map_generator import HeightMapGenerator
from src.systems.world.structure_generator import StructureGenerator
from src.systems.world.world_manager import WorldManager
from src.systems.world.dungeon_generator import DungeonGenerator
from src.systems.world.settlement_generator import SettlementGenerator
from src.systems.world.navigation_system import NavigationSystem
from src.systems.world.tower_system import TowerSystem
from src.systems.world.dungeon_map_system import DungeonMapSystem
from src.systems.world.weather_system import WeatherSystem
from src.systems.world.day_night_cycle import DayNightCycle
from src.systems.world.season_system import SeasonSystem
from src.systems.world.environmental_effects import EnvironmentalEffects

# = ТИПЫ ИНТЕГРАЦИИ
class IntegrationType(Enum):
    """Типы интеграции систем"""
    SYNCHRONOUS = "synchronous"     # Синхронная интеграция
    ASYNCHRONOUS = "asynchronous"   # Асинхронная интеграция
    EVENT_DRIVEN = "event_driven"   # Событийная интеграция

# = НАСТРОЙКИ ИНТЕГРАТОРА
@dataclass
class WorldIntegratorSettings:
    """Настройки интегратора мира"""
    update_interval: float = 0.1    # Интервал обновления в секундах
    async_generation: bool = True   # Асинхронная генерация
    max_threads: int = 4           # Максимальное количество потоков
    cache_enabled: bool = True     # Включить кэширование
    performance_monitoring: bool = True  # Мониторинг производительности

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class SystemStatus:
    """Статус системы"""
    system_name: str
    is_initialized: bool = False
    is_running: bool = False
    last_update: float = 0.0
    update_count: int = 0
    error_count: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class IntegrationData:
    """Данные интеграции"""
    weather_data: Optional[Dict[str, Any]] = None
    time_data: Optional[Dict[str, Any]] = None
    season_data: Optional[Dict[str, Any]] = None
    player_position: Optional[Tuple[float, float, float]] = None
    world_state: Optional[Dict[str, Any]] = None
    created_at: float = field(default_factory=time.time)

# = ИНТЕГРАТОР МИРА
class WorldIntegrator(BaseComponent):
    """Интегратор всех систем мира"""
    
    def __init__(self):
        super().__init__(
            component_id="WorldIntegrator",
            component_type=ComponentType.MANAGER,
            priority=Priority.CRITICAL
        )
        
        # Настройки интегратора
        self.settings = WorldIntegratorSettings()
        
        # Системы мира
        self.world_systems: Dict[str, BaseComponent] = {}
        self.system_status: Dict[str, SystemStatus] = {}
        
        # Данные интеграции
        self.integration_data: Optional[IntegrationData] = None
        
        # Потоки и синхронизация
        self.executor: Optional[ThreadPoolExecutor] = None
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Кэши и статистика
        self.integration_cache: Dict[str, Any] = {}
        self.performance_stats = {
            "total_updates": 0,
            "total_update_time": 0.0,
            "system_updates": {},
            "integration_errors": 0
        }
        
        # Слушатели событий
        self.world_changed_callbacks: List[callable] = []
        self.system_status_changed_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация интегратора мира"""
        try:
            # Создание систем мира
            self._create_world_systems()
            
            # Инициализация систем
            self._initialize_world_systems()
            
            # Создание пула потоков
            if self.settings.async_generation:
                self.executor = ThreadPoolExecutor(max_workers=self.settings.max_threads)
            
            # Инициализация данных интеграции
            self.integration_data = IntegrationData()
            
            self.logger.info("WorldIntegrator инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации WorldIntegrator: {e}")
            return False
    
    def _create_world_systems(self):
        """Создание систем мира"""
        # Основные системы генерации
        self.world_systems["HeightMapGenerator"] = HeightMapGenerator()
        self.world_systems["StructureGenerator"] = StructureGenerator()
        self.world_systems["WorldManager"] = WorldManager()
        
        # Системы локаций
        self.world_systems["DungeonGenerator"] = DungeonGenerator()
        self.world_systems["SettlementGenerator"] = SettlementGenerator()
        self.world_systems["TowerSystem"] = TowerSystem()
        
        # Системы навигации
        self.world_systems["NavigationSystem"] = NavigationSystem()
        self.world_systems["DungeonMapSystem"] = DungeonMapSystem()
        
        # Экологические системы
        self.world_systems["WeatherSystem"] = WeatherSystem()
        self.world_systems["DayNightCycle"] = DayNightCycle()
        self.world_systems["SeasonSystem"] = SeasonSystem()
        self.world_systems["EnvironmentalEffects"] = EnvironmentalEffects()
        
        # Инициализация статусов систем
        for system_name, system in self.world_systems.items():
            self.system_status[system_name] = SystemStatus(system_name=system_name)
    
    def _initialize_world_systems(self):
        """Инициализация систем мира"""
        for system_name, system in self.world_systems.items():
            try:
                if system.initialize():
                    self.system_status[system_name].is_initialized = True
                    self.logger.info(f"Система {system_name} инициализирована")
                else:
                    self.logger.error(f"Ошибка инициализации системы {system_name}")
            except Exception as e:
                self.logger.error(f"Исключение при инициализации {system_name}: {e}")
                self.system_status[system_name].error_count += 1
    
    def start_integration(self):
        """Запуск интеграции"""
        if self.running:
            return
        
        self.running = True
        
        # Запуск систем
        for system_name, system in self.world_systems.items():
            if self.system_status[system_name].is_initialized:
                try:
                    system.start()
                    self.system_status[system_name].is_running = True
                except Exception as e:
                    self.logger.error(f"Ошибка запуска системы {system_name}: {e}")
        
        # Запуск потока обновления
        if self.settings.async_generation:
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
        
        self.logger.info("Интеграция мира запущена")
    
    def stop_integration(self):
        """Остановка интеграции"""
        if not self.running:
            return
        
        self.running = False
        
        # Остановка потока обновления
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5.0)
        
        # Остановка систем
        for system_name, system in self.world_systems.items():
            if self.system_status[system_name].is_running:
                try:
                    system.stop()
                    self.system_status[system_name].is_running = False
                except Exception as e:
                    self.logger.error(f"Ошибка остановки системы {system_name}: {e}")
        
        # Закрытие пула потоков
        if self.executor:
            self.executor.shutdown(wait=True)
        
        self.logger.info("Интеграция мира остановлена")
    
    def _update_loop(self):
        """Цикл обновления интеграции"""
        while self.running:
            try:
                start_time = time.time()
                
                # Обновление интеграции
                self._update_integration()
                
                # Обновление систем
                self._update_world_systems()
                
                # Обновление статистики
                update_time = time.time() - start_time
                self.performance_stats["total_updates"] += 1
                self.performance_stats["total_update_time"] += update_time
                
                # Ожидание следующего обновления
                time.sleep(self.settings.update_interval)
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле обновления: {e}")
                self.performance_stats["integration_errors"] += 1
                time.sleep(1.0)
    
    def _update_integration(self):
        """Обновление интеграции"""
        if not self.integration_data:
            return
        
        # Получение данных от систем
        self._collect_system_data()
        
        # Синхронизация данных между системами
        self._synchronize_systems()
        
        # Применение экологических эффектов
        self._apply_environmental_effects()
        
        # Уведомление об изменениях
        self._notify_world_changed()
    
    def _collect_system_data(self):
        """Сбор данных от систем"""
        try:
            # Данные погоды
            weather_system = self.world_systems.get("WeatherSystem")
            if weather_system and self.system_status["WeatherSystem"].is_running:
                self.integration_data.weather_data = weather_system.get_current_weather()
            
            # Данные времени
            time_system = self.world_systems.get("DayNightCycle")
            if time_system and self.system_status["DayNightCycle"].is_running:
                self.integration_data.time_data = time_system.get_current_time_data()
            
            # Данные сезонов
            season_system = self.world_systems.get("SeasonSystem")
            if season_system and self.system_status["SeasonSystem"].is_running:
                self.integration_data.season_data = season_system.get_current_season_data()
            
            # Состояние мира
            world_manager = self.world_systems.get("WorldManager")
            if world_manager and self.system_status["WorldManager"].is_running:
                self.integration_data.world_state = world_manager.get_world_state()
        
        except Exception as e:
            self.logger.error(f"Ошибка сбора данных систем: {e}")
    
    def _synchronize_systems(self):
        """Синхронизация систем"""
        try:
            # Синхронизация погоды с экологическими эффектами
            weather_system = self.world_systems.get("WeatherSystem")
            effects_system = self.world_systems.get("EnvironmentalEffects")
            
            if weather_system and effects_system and self.integration_data.weather_data:
                # Проверка условий для применения эффектов
                applicable_effects = effects_system.check_effect_conditions(
                    weather_data=self.integration_data.weather_data,
                    time_data=self.integration_data.time_data,
                    season_data=self.integration_data.season_data
                )
                
                # Применение эффектов
                for effect_name in applicable_effects:
                    effects_system.apply_environmental_effect(effect_name)
            
            # Синхронизация времени с поведением существ
            time_system = self.world_systems.get("DayNightCycle")
            if time_system and self.integration_data.time_data:
                # Получение модификаторов поведения
                behavior_modifiers = time_system.get_behavior_modifiers()
                
                # Применение модификаторов к миру
                self._apply_behavior_modifiers(behavior_modifiers)
            
            # Синхронизация сезонов с миром
            season_system = self.world_systems.get("SeasonSystem")
            if season_system and self.integration_data.season_data:
                # Получение сезонных эффектов
                seasonal_effects = season_system.get_active_effects()
                
                # Применение сезонных эффектов
                self._apply_seasonal_effects(seasonal_effects)
        
        except Exception as e:
            self.logger.error(f"Ошибка синхронизации систем: {e}")
    
    def _apply_environmental_effects(self):
        """Применение экологических эффектов"""
        try:
            effects_system = self.world_systems.get("EnvironmentalEffects")
            if not effects_system:
                return
            
            # Обновление эффектов
            effects_system.update_effects(self.settings.update_interval)
            
            # Получение модификаторов эффектов
            effect_modifiers = effects_system.get_effect_modifiers()
            
            # Применение модификаторов к игровым системам
            self._apply_effect_modifiers(effect_modifiers)
        
        except Exception as e:
            self.logger.error(f"Ошибка применения экологических эффектов: {e}")
    
    def _apply_behavior_modifiers(self, modifiers: Dict[str, List[Any]]):
        """Применение модификаторов поведения"""
        try:
            # Применение к NPC
            for entity_type, modifier_list in modifiers.items():
                for modifier in modifier_list:
                    # Здесь должна быть логика применения модификаторов к сущностям
                    pass
        
        except Exception as e:
            self.logger.error(f"Ошибка применения модификаторов поведения: {e}")
    
    def _apply_seasonal_effects(self, effects: List[Any]):
        """Применение сезонных эффектов"""
        try:
            # Применение сезонных эффектов к миру
            for effect in effects:
                # Здесь должна быть логика применения сезонных эффектов
                pass
        
        except Exception as e:
            self.logger.error(f"Ошибка применения сезонных эффектов: {e}")
    
    def _apply_effect_modifiers(self, modifiers: Dict[str, float]):
        """Применение модификаторов эффектов"""
        try:
            # Применение модификаторов к игровым системам
            for modifier_name, modifier_value in modifiers.items():
                # Здесь должна быть логика применения модификаторов
                pass
        
        except Exception as e:
            self.logger.error(f"Ошибка применения модификаторов эффектов: {e}")
    
    def _update_world_systems(self):
        """Обновление систем мира"""
        for system_name, system in self.world_systems.items():
            if not self.system_status[system_name].is_running:
                continue
            
            try:
                start_time = time.time()
                
                # Обновление системы
                system.update(self.settings.update_interval)
                
                # Обновление статистики
                update_time = time.time() - start_time
                self.system_status[system_name].last_update = time.time()
                self.system_status[system_name].update_count += 1
                
                if system_name not in self.performance_stats["system_updates"]:
                    self.performance_stats["system_updates"][system_name] = {
                        "total_updates": 0,
                        "total_time": 0.0,
                        "average_time": 0.0
                    }
                
                stats = self.performance_stats["system_updates"][system_name]
                stats["total_updates"] += 1
                stats["total_time"] += update_time
                stats["average_time"] = stats["total_time"] / stats["total_updates"]
                
            except Exception as e:
                self.logger.error(f"Ошибка обновления системы {system_name}: {e}")
                self.system_status[system_name].error_count += 1
    
    def get_world_system(self, system_name: str) -> Optional[BaseComponent]:
        """Получение системы мира"""
        return self.world_systems.get(system_name)
    
    def get_system_status(self, system_name: str) -> Optional[SystemStatus]:
        """Получение статуса системы"""
        return self.system_status.get(system_name)
    
    def get_all_system_status(self) -> Dict[str, SystemStatus]:
        """Получение статуса всех систем"""
        return self.system_status.copy()
    
    def get_integration_data(self) -> Optional[IntegrationData]:
        """Получение данных интеграции"""
        return self.integration_data
    
    def get_world_statistics(self) -> Dict[str, Any]:
        """Получение статистики мира"""
        stats = {
            "integration_running": self.running,
            "systems_count": len(self.world_systems),
            "initialized_systems": sum(1 for status in self.system_status.values() if status.is_initialized),
            "running_systems": sum(1 for status in self.system_status.values() if status.is_running),
            "system_status": {name: {
                "initialized": status.is_initialized,
                "running": status.is_running,
                "update_count": status.update_count,
                "error_count": status.error_count
            } for name, status in self.system_status.items()},
            "performance_statistics": self.performance_stats.copy()
        }
        
        return stats
    
    def add_world_changed_callback(self, callback: callable):
        """Добавление callback для изменений мира"""
        self.world_changed_callbacks.append(callback)
    
    def add_system_status_changed_callback(self, callback: callable):
        """Добавление callback для изменений статуса систем"""
        self.system_status_changed_callbacks.append(callback)
    
    def _notify_world_changed(self):
        """Уведомление об изменениях мира"""
        for callback in self.world_changed_callbacks:
            try:
                callback(self.integration_data)
            except Exception as e:
                self.logger.error(f"Ошибка в callback изменений мира: {e}")
    
    def _notify_system_status_changed(self, system_name: str, status: SystemStatus):
        """Уведомление об изменениях статуса системы"""
        for callback in self.system_status_changed_callbacks:
            try:
                callback(system_name, status)
            except Exception as e:
                self.logger.error(f"Ошибка в callback статуса системы: {e}")
    
    def clear_cache(self):
        """Очистка кэша"""
        self.integration_cache.clear()
        
        # Очистка кэшей систем
        for system in self.world_systems.values():
            if hasattr(system, 'clear_cache'):
                system.clear_cache()
        
        self.logger.info("Кэш WorldIntegrator очищен")
    
    def _on_destroy(self):
        """Уничтожение интегратора мира"""
        # Остановка интеграции
        self.stop_integration()
        
        # Уничтожение систем
        for system_name, system in self.world_systems.items():
            try:
                system.destroy()
            except Exception as e:
                self.logger.error(f"Ошибка уничтожения системы {system_name}: {e}")
        
        # Очистка данных
        self.world_systems.clear()
        self.system_status.clear()
        self.integration_data = None
        self.integration_cache.clear()
        self.world_changed_callbacks.clear()
        self.system_status_changed_callbacks.clear()
        
        self.logger.info("WorldIntegrator уничтожен")
