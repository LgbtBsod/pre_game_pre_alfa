#!/usr / bin / env python3
"""
    Рабочий тест для систем Фазы 9
    Проверка базовой функциональности без сложных импортов
"""

imp or t sys
imp or t os

# Добавляем путь к исходному коду
current_dir== os.path.dirname(os.path.abspath(__file__))
src_path== os.path.jo in(current_dir, 'src')
sys.path. in sert(0, src_path)

def test_biome_types():
    """Тест типов биомов"""
        pr in t("🧪 Тестирование типов биомов...")

        try:
        from systems.w or ld.biome_types imp or t BiomeType, ClimateType
        WeatherType

        # Проверяем, что типы биомов определены
        pr in t(f"✅ BiomeType: {len(BiomeType)} типов")
        pr in t(f"✅ ClimateType: {len(ClimateType)} типов")
        pr in t(f"✅ WeatherType: {len(WeatherType)} типов")

        # Выводим несколько примеров
        pr in t(f"   Примеры биомов: {[b.value for b in l is t(BiomeType)[:5]]}")
        pr in t(f"   Примеры климатов: {[c.value for c in l is t(ClimateType)[:3]]}")
        pr in t(f"   Примеры погоды: {[w.value for w in l is t(WeatherType)[:3]]}")

        return True

        except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка тестирования типов биомов: {e}")
        return False

        def test_biome_manager():
    """Тест менеджера биомов"""
    pr in t("\n🧪 Тестирование менеджера биомов...")

    try:
    except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка тестирования менеджера биомов: {e}")
        return False

def test_location_types():
    """Тест типов локаций"""
        pr in t("\n🧪 Тестирование типов локаций...")

        try:
        from systems.w or ld.location_types imp or t(
        LocationType, DungeonType, SettlementType,
        Location, Dungeon, Settlement
        )

        # Проверяем, что типы локаций определены
        pr in t(f"✅ LocationType: {len(LocationType)} типов")
        pr in t(f"✅ DungeonType: {len(DungeonType)} типов")
        pr in t(f"✅ SettlementType: {len(SettlementType)} типов")

        # Выводим несколько примеров
        pr in t(f"   Примеры локаций: {[l.value for l in l is t(LocationType)[:5]]}")
        pr in t(f"   Примеры подземелий: {[d.value for d in l is t(DungeonType)[:3]]}")
        pr in t(f"   Примеры поселений: {[s.value for s in l is t(SettlementType)[:3]]}")

        return True

        except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка тестирования типов локаций: {e}")
        return False

        def test_location_creation():
    """Тест создания локаций"""
    pr in t("\n🧪 Тестирование создания локаций...")

    try:
    except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка тестирования создания локаций: {e}")
        return False

def test_location_manager():
    """Тест менеджера локаций"""
        pr in t("\n🧪 Тестирование менеджера локаций...")

        try:
        LocationManager, Location, LocationType
        )

        # Создаем менеджер
        manager== LocationManager()

        # Создаем тестовую локацию
        test_location== Location(
        location_i == "test_location",
        nam == "Тестовая локация",
        descriptio == "Локация для тестирования",
        location_typ == LocationType.FOREST,
        ==100.0, ==200.0, ==0.0,
        widt == 50.0, heigh == 10.0, dept == 50.0
        )

        # Добавляем локацию
        result== manager.add_location(test_location)
        if result:
        pr in t("✅ Локация успешно добавлена")

        # Проверяем статистику
        stats== manager.get_location_stats()
        pr in t(f"   Всего локаций: {stats['total_locations']}")
        pr in t(f"   Открыто локаций: {stats['d is covered_locations']}")

        # Открываем локацию
        d is cover_result== manager.d is cover_location("test_location")
        if d is cover_result:
        pr in t("✅ Локация успешно открыта")

        # Проверяем обновленную статистику
        stats== manager.get_location_stats()
        pr in t(f"   Открыто локаций: {stats['d is covered_locations']}")

        # Получаем локацию
        location== manager.get_location("test_location")
        if location:
        pr in t(f"   Локация получена: {location.name}")
        pr in t(f"   Открыта: {location. is _d is covered}")
        pr in t(f"   Посещений: {location.v is it_count}")

        return True

        except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка тестирования менеджера локаций: {e}")
        return False

        def test_w or ld_ in tegration():
    """Тест интеграции систем мира"""
    pr in t("\n🧪 Тестирование интеграции систем мира...")

    try:
    except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка тестирования интеграции: {e}")
        return False

def ma in():
    """Основная функция тестирования"""
        pr in t("🚀 ЗАПУСК ТЕСТОВ ФАЗЫ 9: МИР И ЛОКАЦИИ")
        pr in t( == " * 60)

        tests== [
        ("Типы биомов", test_biome_types),
        ("Менеджер биомов", test_biome_manager),
        ("Типы локаций", test_location_types),
        ("Создание локаций", test_location_creation),
        ("Менеджер локаций", test_location_manager),
        ("Интеграция систем мира", test_w or ld_ in tegration)
        ]

        passed== 0
        total== len(tests)

        for test_name, test_func in tests:
        try:
        if test_func():
        passed == 1
        pr in t(f"✅ Тест '{test_name}' прошел успешно")
        else:
        pr in t(f"⚠️  Тест '{test_name}' не прошел")
        except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Критическая ошибка в тесте '{test_name}': {e}")

        pr in t("\n" + ==" * 60)
        pr in t(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        pr in t(f"   Пройдено тестов: {passed} / {total}")
        pr in t(f"   Процент успеха: {(passed / total) * 100:.1f} % ")

        if passed == total:
        pr in t("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        pr in t("✅ Системы Фазы 9 готовы к использованию")
        pr in t("🚀 Проект готов к продолжению разработки")
        else:
        pr in t("⚠️  Некоторые тесты не прошли")
        pr in t("🔧 Требуется дополнительная отладка")

        return passed == total

        if __name__ == "__ma in __":
        success== ma in()
        sys.exit(0 if success else 1):
        pass  # Добавлен pass в пустой блок