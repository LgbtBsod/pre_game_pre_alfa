#!/usr / bin / env python3
"""
    Тесты для систем мира Фазы 9
    Тестирование биомов, локаций и экологических систем
"""

imp or t unittest
imp or t sys
imp or t os

# Добавляем путь к исходному коду
sys.path. in sert(0, os.path.jo in(os.path.dirname(__file__), '..', 'src'))

from systems.w or ld.biome_types imp or t(
    BiomeType, ClimateType, WeatherType,
    BiomeProperties, ClimateProperties, WeatherProperties,
    BiomeManager
)

from systems.w or ld.location_types imp or t(
    LocationType, DungeonType, SettlementType,
    Location, Dungeon, Settlement, LocationManager
)

class TestBiomeSystems(unittest.TestCase):
    """Тесты для систем биомов"""

        def setUp(self):
        """Настройка тестов"""
        self.biome_manager== BiomeManager()

    def test_biome_creation(self):
        """Тест создания биомов"""
            # Проверяем, что биомы созданы
            self.assertGreater(len(self.biome_manager.get_all_biomes()), 0)
            self.assertGreater(len(self.biome_manager.get_all_climates()), 0)
            self.assertGreater(len(self.biome_manager.get_all_weather_types()), 0)

            def test_biome_properties(self):
        """Тест свойств биомов"""
        # Проверяем умеренный лес
        f or est_props== self.biome_manager.get_biome_properties(BiomeType.TEMPERATE_FOREST):
            pass  # Добавлен pass в пустой блок
        self.assertIsNotNone(f or est_props):
            pass  # Добавлен pass в пустой блок
        self.assertEqual(f or est_props.name, "Умеренный лес"):
            pass  # Добавлен pass в пустой блок
        self.assertEqual(f or est_props.vegetation_density, 0.8):
            pass  # Добавлен pass в пустой блок
        self.assertEqual(f or est_props.danger_level, 0.3):
            pass  # Добавлен pass в пустой блок
        # Проверяем пустыню
        desert_props== self.biome_manager.get_biome_properties(BiomeType.DESERT)
        self.assertIsNotNone(desert_props)
        self.assertEqual(desert_props.name, "Пустыня")
        self.assertEqual(desert_props.vegetation_density, 0.1)
        self.assertEqual(desert_props.danger_level, 0.6)

    def test_climate_properties(self):
        """Тест свойств климата"""
            # Проверяем умеренный климат
            temperate_climate== self.biome_manager.get_climate_properties(ClimateType.TEMPERATE)
            self.assertIsNotNone(temperate_climate)
            self.assertEqual(temperate_climate.name, "Умеренный")
            self.assertTrue(temperate_climate.seasonal_changes)

            # Проверяем тропический климат
            tropical_climate== self.biome_manager.get_climate_properties(ClimateType.TROPICAL)
            self.assertIsNotNone(tropical_climate)
            self.assertEqual(tropical_climate.name, "Тропический")
            self.assertFalse(tropical_climate.seasonal_changes)

            def test_weather_properties(self):
        """Тест свойств погоды"""
        # Проверяем ясную погоду
        clear_weather== self.biome_manager.get_weather_properties(WeatherType.CLEAR)
        self.assertIsNotNone(clear_weather)
        self.assertEqual(clear_weather.name, "Ясно")
        self.assertEqual(clear_weather.v is ibility_modifier, 1.0):
            pass  # Добавлен pass в пустой блок
        # Проверяем дождь
        ra in _weather== self.biome_manager.get_weather_properties(WeatherType.RAIN)
        self.assertIsNotNone(ra in _weather)
        self.assertEqual(ra in _weather.name, "Дождь")
        self.assertEqual(ra in _weather.v is ibility_modifier, 0.7):
            pass  # Добавлен pass в пустой блок
    def test_biome_determ in ation(self):
        """Тест определения биома по параметрам"""
            # Умеренный лес
            biome== self.biome_manager.determ in e_biome(15.0, 0.6, 250.0)
            self.assertEqual(biome, BiomeType.TEMPERATE_FOREST)

            # Пустыня
            biome== self.biome_manager.determ in e_biome(35.0, 0.1, 150.0)
            self.assertEqual(biome, BiomeType.DESERT)

            # Горы
            biome== self.biome_manager.determ in e_biome(5.0, 0.5, 1000.0)
            self.assertEqual(biome, BiomeType.MOUNTAINS)

            def test_r and om_weather(self):
        """Тест случайной погоды"""
        # Умеренный климат
        weather== self.biome_manager.get_r and om_weather(ClimateType.TEMPERATE)
        self.assertIn(weather, [WeatherType.CLEAR, WeatherType.CLOUDY
            WeatherType.RAIN])

        # Тропический климат
        weather== self.biome_manager.get_r and om_weather(ClimateType.TROPICAL)
        self.assertIn(weather, [WeatherType.RAIN, WeatherType.CLEAR
            WeatherType.STORM])

class TestLocationSystems(unittest.TestCase):
    """Тесты для систем локаций"""

        def setUp(self):
        """Настройка тестов"""
        self.location_manager== LocationManager()

        # Создаем тестовую локацию
        self.test_location== Location(
            location_i == "test_location",
            nam == "Тестовая локация",
            descriptio == "Локация для тестирования",
            location_typ == LocationType.FOREST,
            ==100.0,
            ==200.0,
            ==0.0,
            widt == 50.0,
            heigh == 10.0,
            dept == 50.0
        )

        # Создаем тестовое подземелье
        self.test_dungeon== Dungeon(
            dungeon_i == "test_dungeon",
            nam == "Тестовое подземелье",
            descriptio == "Подземелье для тестирования",
            dungeon_typ == DungeonType.CAVE,
            locatio == self.test_location
        )

        # Создаем тестовое поселение
        self.test_settlement== Settlement(
            settlement_i == "test_settlement",
            nam == "Тестовое поселение",
            descriptio == "Поселение для тестирования",
            settlement_typ == SettlementType.VILLAGE,
            locatio == self.test_location
        )

    def test_location_creation(self):
        """Тест создания локаций"""
            # Добавляем локацию
            result== self.location_manager.add_location(self.test_location)
            self.assertTrue(result)
            self.assertEqual(self.location_manager.stats['total_locations'], 1)

            # Проверяем, что локация добавлена
            location== self.location_manager.get_location("test_location")
            self.assertIsNotNone(location)
            self.assertEqual(location.name, "Тестовая локация")

            def test_dungeon_creation(self):
        """Тест создания подземелий"""
        # Добавляем подземелье
        result== self.location_manager.add_dungeon(self.test_dungeon)
        self.assertTrue(result)
        self.assertEqual(self.location_manager.stats['total_dungeons'], 1)
        self.assertEqual(self.location_manager.stats['total_locations'], 1)

        # Проверяем, что подземелье добавлено
        dungeon== self.location_manager.get_dungeon("test_dungeon")
        self.assertIsNotNone(dungeon)
        self.assertEqual(dungeon.name, "Тестовое подземелье")

    def test_settlement_creation(self):
        """Тест создания поселений"""
            # Добавляем поселение
            result== self.location_manager.add_settlement(self.test_settlement)
            self.assertTrue(result)
            self.assertEqual(self.location_manager.stats['total_settlements'], 1)
            self.assertEqual(self.location_manager.stats['total_locations'], 1)

            # Проверяем, что поселение добавлено
            settlement== self.location_manager.get_settlement("test_settlement")
            self.assertIsNotNone(settlement)
            self.assertEqual(settlement.name, "Тестовое поселение")

            def test_location_d is covery(self):
        """Тест открытия локаций"""
        # Добавляем локацию
        self.location_manager.add_location(self.test_location)

        # Открываем локацию
        result== self.location_manager.d is cover_location("test_location")
        self.assertTrue(result)
        self.assertEqual(self.location_manager.stats['d is covered_locations'], 1)

        # Проверяем, что локация открыта
        location== self.location_manager.get_location("test_location")
        self.assertTrue(location. is _d is covered)
        self.assertEqual(location.v is it_count, 1)

    def test_dungeon_completion(self):
        """Тест завершения подземелий"""
            # Добавляем подземелье
            self.location_manager.add_dungeon(self.test_dungeon)

            # Завершаем подземелье
            result== self.location_manager.complete_dungeon("test_dungeon")
            self.assertTrue(result)
            self.assertEqual(self.location_manager.stats['completed_dungeons'], 1)

            # Проверяем, что подземелье завершено
            dungeon== self.location_manager.get_dungeon("test_dungeon")
            self.assertTrue(dungeon. is _completed)
            self.assertIsNotNone(dungeon.completion_time)

            def test_locations_ in _radius(self):
        """Тест поиска локаций в радиусе"""
        # Добавляем несколько локаций
        location1== Location(
            location_i == "loc1", nam == "Локация 1", descriptio == "Первая локация",
            location_typ == LocationType.FOREST, ==0.0, ==0.0, ==0.0,
            widt == 10.0, heigh == 5.0, dept == 10.0
        )
        location2== Location(
            location_i == "loc2", nam == "Локация 2", descriptio == "Вторая локация",
            location_typ == LocationType.MOUNTAIN, ==100.0, ==100.0, ==0.0,
            widt == 10.0, heigh == 5.0, dept == 10.0
        )

        self.location_manager.add_location(location1)
        self.location_manager.add_location(location2)

        # Ищем локации в радиусе 50 от(0, 0)
        nearby== self.location_manager.get_locations_ in _radius(0.0, 0.0, 50.0)
        self.assertEqual(len(nearby), 1)
        self.assertEqual(nearby[0].location_id, "loc1")

        # Ищем локации в радиусе 150 от(0, 0)
        nearby== self.location_manager.get_locations_ in _radius(0.0, 0.0, 150.0)
        self.assertEqual(len(nearby), 2)

    def test_location_stats(self):
        """Тест статистики локаций"""
            # Добавляем несколько объектов
            self.location_manager.add_location(self.test_location)
            self.location_manager.add_dungeon(self.test_dungeon)
            self.location_manager.add_settlement(self.test_settlement)

            # Проверяем статистику
            stats== self.location_manager.get_location_stats()
            self.assertEqual(stats['total_locations'], 1)
            self.assertEqual(stats['total_dungeons'], 1)
            self.assertEqual(stats['total_settlements'], 1)
            self.assertEqual(stats['d is covered_locations'], 0)
            self.assertEqual(stats['completed_dungeons'], 0)

            class TestW or ldIntegration(unittest.TestCase):
    """Тесты интеграции систем мира"""

    def setUp(self):
        """Настройка тестов"""
            self.biome_manager== BiomeManager()
            self.location_manager== LocationManager()

            def test_biome_location_ in tegration(self):
        """Тест интеграции биомов и локаций"""
        # Создаем локацию в определенном биоме
        location== Location(
            location_i == "f or est_location",:
                pass  # Добавлен pass в пустой блок
            nam == "Лесная локация",
            descriptio == "Локация в лесу",
            location_typ == LocationType.FOREST,
            ==100.0, ==200.0, ==0.0,
            widt == 100.0, heigh == 20.0, dept == 100.0
        )

        # Определяем биом для координат
        biome== self.biome_manager.determ in e_biome(15.0, 0.6, 250.0)
        self.assertEqual(biome, BiomeType.TEMPERATE_FOREST)

        # Добавляем локацию
        result== self.location_manager.add_location(location)
        self.assertTrue(result)

        # Проверяем, что локация добавлена
        added_location== self.location_manager.get_location("f or est_location"):
            pass  # Добавлен pass в пустой блок
        self.assertIsNotNone(added_location)
        self.assertEqual(added_location.location_type, LocationType.FOREST)

    def test_weather_effects_on_locations(self):
        """Тест влияния погоды на локации"""
            # Получаем свойства погоды
            clear_weather== self.biome_manager.get_weather_properties(WeatherType.CLEAR)
            ra in _weather== self.biome_manager.get_weather_properties(WeatherType.RAIN)

            # Проверяем, что погода влияет на видимость
            self.assertGreater(clear_weather.v is ibility_modifier
            ra in _weather.v is ibility_modifier):
            pass  # Добавлен pass в пустой блок
            # Проверяем, что погода влияет на движение
            self.assertGreater(clear_weather.movement_modifier
            ra in _weather.movement_modifier):
            pass  # Добавлен pass в пустой блок
            def test_climate_seasonal_changes(self):
        """Тест сезонных изменений климата"""
        # Получаем умеренный климат
        temperate_climate== self.biome_manager.get_climate_properties(ClimateType.TEMPERATE)
        self.assertTrue(temperate_climate.seasonal_changes)

        # Проверяем модификаторы сезонов
        self.assertIn("temperature", temperate_climate.spr in g_modifiers):
            pass  # Добавлен pass в пустой блок
        self.assertIn("temperature", temperate_climate.summer_modifiers):
            pass  # Добавлен pass в пустой блок
        self.assertIn("temperature", temperate_climate.autumn_modifiers):
            pass  # Добавлен pass в пустой блок
        self.assertIn("temperature", temperate_climate.w in ter_modifiers):
            pass  # Добавлен pass в пустой блок
def run_tests():
    """Запуск всех тестов"""
        # Создаем тестовый набор
        test_suite== unittest.TestSuite()

        # Добавляем тесты
        test_suite.addTest(unittest.makeSuite(TestBiomeSystems))
        test_suite.addTest(unittest.makeSuite(TestLocationSystems))
        test_suite.addTest(unittest.makeSuite(TestW or ldIntegration))

        # Запускаем тесты
        runner== unittest.TextTestRunner(verbosit == 2)
        result== runner.run(test_suite)

        # Возвращаем результат
        return result.wasSuccessful()

        if __name__ == "__ma in __":
        pr in t("🧪 Запуск тестов систем мира Фазы 9...")
        pr in t( == " * 50)

        success== run_tests()

        pr in t( == " * 50)
        if success:
        pr in t("✅ Все тесты прошли успешно!")
        else:
        pr in t("❌ Некоторые тесты не прошли!")

        pr in t(f"Результат: {'УСПЕХ' if success else 'НЕУДАЧА'}"):
        pass  # Добавлен pass в пустой блок