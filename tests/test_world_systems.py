#!/usr/bin/env python3
"""
Тесты для систем мира Фазы 9
Тестирование биомов, локаций и экологических систем
"""

import unittest
import sys
import os

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from systems.world.biome_types import (
    BiomeType, ClimateType, WeatherType,
    BiomeProperties, ClimateProperties, WeatherProperties,
    BiomeManager
)

from systems.world.location_types import (
    LocationType, DungeonType, SettlementType,
    Location, Dungeon, Settlement, LocationManager
)

class TestBiomeSystems(unittest.TestCase):
    """Тесты для систем биомов"""
    
    def setUp(self):
        """Настройка тестов"""
        self.biome_manager = BiomeManager()
    
    def test_biome_creation(self):
        """Тест создания биомов"""
        # Проверяем, что биомы созданы
        self.assertGreater(len(self.biome_manager.get_all_biomes()), 0)
        self.assertGreater(len(self.biome_manager.get_all_climates()), 0)
        self.assertGreater(len(self.biome_manager.get_all_weather_types()), 0)
    
    def test_biome_properties(self):
        """Тест свойств биомов"""
        # Проверяем умеренный лес
        forest_props = self.biome_manager.get_biome_properties(BiomeType.TEMPERATE_FOREST)
        self.assertIsNotNone(forest_props)
        self.assertEqual(forest_props.name, "Умеренный лес")
        self.assertEqual(forest_props.vegetation_density, 0.8)
        self.assertEqual(forest_props.danger_level, 0.3)
        
        # Проверяем пустыню
        desert_props = self.biome_manager.get_biome_properties(BiomeType.DESERT)
        self.assertIsNotNone(desert_props)
        self.assertEqual(desert_props.name, "Пустыня")
        self.assertEqual(desert_props.vegetation_density, 0.1)
        self.assertEqual(desert_props.danger_level, 0.6)
    
    def test_climate_properties(self):
        """Тест свойств климата"""
        # Проверяем умеренный климат
        temperate_climate = self.biome_manager.get_climate_properties(ClimateType.TEMPERATE)
        self.assertIsNotNone(temperate_climate)
        self.assertEqual(temperate_climate.name, "Умеренный")
        self.assertTrue(temperate_climate.seasonal_changes)
        
        # Проверяем тропический климат
        tropical_climate = self.biome_manager.get_climate_properties(ClimateType.TROPICAL)
        self.assertIsNotNone(tropical_climate)
        self.assertEqual(tropical_climate.name, "Тропический")
        self.assertFalse(tropical_climate.seasonal_changes)
    
    def test_weather_properties(self):
        """Тест свойств погоды"""
        # Проверяем ясную погоду
        clear_weather = self.biome_manager.get_weather_properties(WeatherType.CLEAR)
        self.assertIsNotNone(clear_weather)
        self.assertEqual(clear_weather.name, "Ясно")
        self.assertEqual(clear_weather.visibility_modifier, 1.0)
        
        # Проверяем дождь
        rain_weather = self.biome_manager.get_weather_properties(WeatherType.RAIN)
        self.assertIsNotNone(rain_weather)
        self.assertEqual(rain_weather.name, "Дождь")
        self.assertEqual(rain_weather.visibility_modifier, 0.7)
    
    def test_biome_determination(self):
        """Тест определения биома по параметрам"""
        # Умеренный лес
        biome = self.biome_manager.determine_biome(15.0, 0.6, 250.0)
        self.assertEqual(biome, BiomeType.TEMPERATE_FOREST)
        
        # Пустыня
        biome = self.biome_manager.determine_biome(35.0, 0.1, 150.0)
        self.assertEqual(biome, BiomeType.DESERT)
        
        # Горы
        biome = self.biome_manager.determine_biome(5.0, 0.5, 1000.0)
        self.assertEqual(biome, BiomeType.MOUNTAINS)
    
    def test_random_weather(self):
        """Тест случайной погоды"""
        # Умеренный климат
        weather = self.biome_manager.get_random_weather(ClimateType.TEMPERATE)
        self.assertIn(weather, [WeatherType.CLEAR, WeatherType.CLOUDY, WeatherType.RAIN])
        
        # Тропический климат
        weather = self.biome_manager.get_random_weather(ClimateType.TROPICAL)
        self.assertIn(weather, [WeatherType.RAIN, WeatherType.CLEAR, WeatherType.STORM])

class TestLocationSystems(unittest.TestCase):
    """Тесты для систем локаций"""
    
    def setUp(self):
        """Настройка тестов"""
        self.location_manager = LocationManager()
        
        # Создаем тестовую локацию
        self.test_location = Location(
            location_id="test_location",
            name="Тестовая локация",
            description="Локация для тестирования",
            location_type=LocationType.FOREST,
            x=100.0,
            y=200.0,
            z=0.0,
            width=50.0,
            height=10.0,
            depth=50.0
        )
        
        # Создаем тестовое подземелье
        self.test_dungeon = Dungeon(
            dungeon_id="test_dungeon",
            name="Тестовое подземелье",
            description="Подземелье для тестирования",
            dungeon_type=DungeonType.CAVE,
            location=self.test_location
        )
        
        # Создаем тестовое поселение
        self.test_settlement = Settlement(
            settlement_id="test_settlement",
            name="Тестовое поселение",
            description="Поселение для тестирования",
            settlement_type=SettlementType.VILLAGE,
            location=self.test_location
        )
    
    def test_location_creation(self):
        """Тест создания локаций"""
        # Добавляем локацию
        result = self.location_manager.add_location(self.test_location)
        self.assertTrue(result)
        self.assertEqual(self.location_manager.stats['total_locations'], 1)
        
        # Проверяем, что локация добавлена
        location = self.location_manager.get_location("test_location")
        self.assertIsNotNone(location)
        self.assertEqual(location.name, "Тестовая локация")
    
    def test_dungeon_creation(self):
        """Тест создания подземелий"""
        # Добавляем подземелье
        result = self.location_manager.add_dungeon(self.test_dungeon)
        self.assertTrue(result)
        self.assertEqual(self.location_manager.stats['total_dungeons'], 1)
        self.assertEqual(self.location_manager.stats['total_locations'], 1)
        
        # Проверяем, что подземелье добавлено
        dungeon = self.location_manager.get_dungeon("test_dungeon")
        self.assertIsNotNone(dungeon)
        self.assertEqual(dungeon.name, "Тестовое подземелье")
    
    def test_settlement_creation(self):
        """Тест создания поселений"""
        # Добавляем поселение
        result = self.location_manager.add_settlement(self.test_settlement)
        self.assertTrue(result)
        self.assertEqual(self.location_manager.stats['total_settlements'], 1)
        self.assertEqual(self.location_manager.stats['total_locations'], 1)
        
        # Проверяем, что поселение добавлено
        settlement = self.location_manager.get_settlement("test_settlement")
        self.assertIsNotNone(settlement)
        self.assertEqual(settlement.name, "Тестовое поселение")
    
    def test_location_discovery(self):
        """Тест открытия локаций"""
        # Добавляем локацию
        self.location_manager.add_location(self.test_location)
        
        # Открываем локацию
        result = self.location_manager.discover_location("test_location")
        self.assertTrue(result)
        self.assertEqual(self.location_manager.stats['discovered_locations'], 1)
        
        # Проверяем, что локация открыта
        location = self.location_manager.get_location("test_location")
        self.assertTrue(location.is_discovered)
        self.assertEqual(location.visit_count, 1)
    
    def test_dungeon_completion(self):
        """Тест завершения подземелий"""
        # Добавляем подземелье
        self.location_manager.add_dungeon(self.test_dungeon)
        
        # Завершаем подземелье
        result = self.location_manager.complete_dungeon("test_dungeon")
        self.assertTrue(result)
        self.assertEqual(self.location_manager.stats['completed_dungeons'], 1)
        
        # Проверяем, что подземелье завершено
        dungeon = self.location_manager.get_dungeon("test_dungeon")
        self.assertTrue(dungeon.is_completed)
        self.assertIsNotNone(dungeon.completion_time)
    
    def test_locations_in_radius(self):
        """Тест поиска локаций в радиусе"""
        # Добавляем несколько локаций
        location1 = Location(
            location_id="loc1", name="Локация 1", description="Первая локация",
            location_type=LocationType.FOREST, x=0.0, y=0.0, z=0.0,
            width=10.0, height=5.0, depth=10.0
        )
        location2 = Location(
            location_id="loc2", name="Локация 2", description="Вторая локация",
            location_type=LocationType.MOUNTAIN, x=100.0, y=100.0, z=0.0,
            width=10.0, height=5.0, depth=10.0
        )
        
        self.location_manager.add_location(location1)
        self.location_manager.add_location(location2)
        
        # Ищем локации в радиусе 50 от (0, 0)
        nearby = self.location_manager.get_locations_in_radius(0.0, 0.0, 50.0)
        self.assertEqual(len(nearby), 1)
        self.assertEqual(nearby[0].location_id, "loc1")
        
        # Ищем локации в радиусе 150 от (0, 0)
        nearby = self.location_manager.get_locations_in_radius(0.0, 0.0, 150.0)
        self.assertEqual(len(nearby), 2)
    
    def test_location_stats(self):
        """Тест статистики локаций"""
        # Добавляем несколько объектов
        self.location_manager.add_location(self.test_location)
        self.location_manager.add_dungeon(self.test_dungeon)
        self.location_manager.add_settlement(self.test_settlement)
        
        # Проверяем статистику
        stats = self.location_manager.get_location_stats()
        self.assertEqual(stats['total_locations'], 1)
        self.assertEqual(stats['total_dungeons'], 1)
        self.assertEqual(stats['total_settlements'], 1)
        self.assertEqual(stats['discovered_locations'], 0)
        self.assertEqual(stats['completed_dungeons'], 0)

class TestWorldIntegration(unittest.TestCase):
    """Тесты интеграции систем мира"""
    
    def setUp(self):
        """Настройка тестов"""
        self.biome_manager = BiomeManager()
        self.location_manager = LocationManager()
    
    def test_biome_location_integration(self):
        """Тест интеграции биомов и локаций"""
        # Создаем локацию в определенном биоме
        location = Location(
            location_id="forest_location",
            name="Лесная локация",
            description="Локация в лесу",
            location_type=LocationType.FOREST,
            x=100.0, y=200.0, z=0.0,
            width=100.0, height=20.0, depth=100.0
        )
        
        # Определяем биом для координат
        biome = self.biome_manager.determine_biome(15.0, 0.6, 250.0)
        self.assertEqual(biome, BiomeType.TEMPERATE_FOREST)
        
        # Добавляем локацию
        result = self.location_manager.add_location(location)
        self.assertTrue(result)
        
        # Проверяем, что локация добавлена
        added_location = self.location_manager.get_location("forest_location")
        self.assertIsNotNone(added_location)
        self.assertEqual(added_location.location_type, LocationType.FOREST)
    
    def test_weather_effects_on_locations(self):
        """Тест влияния погоды на локации"""
        # Получаем свойства погоды
        clear_weather = self.biome_manager.get_weather_properties(WeatherType.CLEAR)
        rain_weather = self.biome_manager.get_weather_properties(WeatherType.RAIN)
        
        # Проверяем, что погода влияет на видимость
        self.assertGreater(clear_weather.visibility_modifier, rain_weather.visibility_modifier)
        
        # Проверяем, что погода влияет на движение
        self.assertGreater(clear_weather.movement_modifier, rain_weather.movement_modifier)
    
    def test_climate_seasonal_changes(self):
        """Тест сезонных изменений климата"""
        # Получаем умеренный климат
        temperate_climate = self.biome_manager.get_climate_properties(ClimateType.TEMPERATE)
        self.assertTrue(temperate_climate.seasonal_changes)
        
        # Проверяем модификаторы сезонов
        self.assertIn("temperature", temperate_climate.spring_modifiers)
        self.assertIn("temperature", temperate_climate.summer_modifiers)
        self.assertIn("temperature", temperate_climate.autumn_modifiers)
        self.assertIn("temperature", temperate_climate.winter_modifiers)

def run_tests():
    """Запуск всех тестов"""
    # Создаем тестовый набор
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_suite.addTest(unittest.makeSuite(TestBiomeSystems))
    test_suite.addTest(unittest.makeSuite(TestLocationSystems))
    test_suite.addTest(unittest.makeSuite(TestWorldIntegration))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Возвращаем результат
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Запуск тестов систем мира Фазы 9...")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("✅ Все тесты прошли успешно!")
    else:
        print("❌ Некоторые тесты не прошли!")
    
    print(f"Результат: {'УСПЕХ' if success else 'НЕУДАЧА'}")
