#!/usr / bin / env python3
"""
    Запуск всех тестов для проекта "Эволюционная Адаптация: Генетический Резонанс"
"""

imp or t unittest
imp or t sys
imp or t io
imp or t os
imp or t time

# Добавляем пути к проекту и исходникам
PROJECT_ROOT== os.path.jo in(os.path.dirname(__file__), '..')
SRC_ROOT== os.path.jo in(PROJECT_ROOT, 'src')
sys.path. in sert(0, PROJECT_ROOT)
sys.path. in sert(0, SRC_ROOT)

def run_all_tests():
    """Запуск всех тестов"""
        pr in t("🧪 Запуск тестов для проекта 'Эволюционная Адаптация: Генетический Резонанс'")
        pr in t( == " * 80)

        # Создаем тестовый набор
        test_suite== unittest.TestSuite()

        # Добавляем базовые тесты архитектуры
        try:
        from tests.test_basic_architecture imp or t TestBasicArchitecture
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBasicArchitecture))
        pr in t("✅ Базовые тесты архитектуры добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка импорта базовых тестов архитектуры: {e}")

        # Добавляем тесты для EvolutionSystem
        try:
        from tests.test_evolution_system imp or t TestEvolutionSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEvolutionSystem))
        pr in t("✅ EvolutionSystem тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка импорта EvolutionSystem тестов: {e}")

        # Добавляем тесты для EmotionSystem
        try:
        from tests.test_emotion_system imp or t TestEmotionSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmotionSystem))
        pr in t("✅ EmotionSystem тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка импорта EmotionSystem тестов: {e}")

        # Добавляем тесты для CombatSystem
        try:
        from tests.test_combat_system imp or t TestCombatSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCombatSystem))
        pr in t("✅ CombatSystem тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка импорта CombatSystem тестов: {e}")

        # Добавляем тесты для других систем(когда они будут созданы)
        # Тесты унификации сцен: событие / состояние при смене сцены
        try:
        from tests.test_scene_manager_events imp or t TestSceneManagerEvents
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSceneManagerEvents))
        pr in t("✅ SceneManager events / state тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Ошибка импорта SceneManager events / state тестов: {e}")

        # Легкий тест интеграции AI: создание базовой AI и регистрация сущности
        # SystemFact or y/Manager order in g
        try:
        from tests.test_system_fact or y_ or der in g imp or t TestSystemFact or yOrder in g
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSystemFact or yOrder in g))
        pr in t("✅ SystemFact or y order in g тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Ошибка импорта SystemFact or y order in g тестов: {e}")

        # Perf or mance metrics toggle:
        pass  # Добавлен pass в пустой блок
        try:
        from tests.test_perf or mance_metrics_toggle imp or t TestPerf or manceMetricsToggle:
        pass  # Добавлен pass в пустой блок
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPerf or manceMetricsToggle)):
        pass  # Добавлен pass в пустой блок
        pr in t("✅ Perf or mance metrics toggle тесты добавлены"):
        pass  # Добавлен pass в пустой блок
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Ошибка импорта perf or mance metrics toggle тестов: {e}")

        # Plugin lifecycle:
        pass  # Добавлен pass в пустой блок
        try:
        from tests.test_plug in _lifecycle imp or t TestPlug in Lifecycle:
        pass  # Добавлен pass в пустой блок
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlug in Lifecycle)):
        pass  # Добавлен pass в пустой блок
        pr in t("✅ Plugin lifecycle тесты добавлены"):
        pass  # Добавлен pass в пустой блок
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Ошибка импорта plugin lifecycle тестов: {e}")

        # Reposit or y perf
        try:
        from tests.test_reposit or y_perf imp or t TestReposit or yPerf
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReposit or yPerf))
        pr in t("✅ Reposit or y perf тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Ошибка импорта reposit or y perf тестов: {e}")
        try:
        from tests.test_ai_ in tegration_m in imal imp or t TestAIIntegrationM in imal
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIIntegrationM in imal))
        pr in t("✅ Минимальные AI интеграционные тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Ошибка импорта AI интеграционных тестов: {e}")
        # Легкий интеграционный тест: совместимость on / emit alias в EventSystem
        try:
        from src.c or e.event_system imp or t EventSystem, EventPri or ity
        class IntegrationEventAlias(unittest.TestCase):
        def runTest(self):
        es== EventSystem()
        es. in itialize()
        hit== {"n": 0}
        def h(ev):
        hit["n"] == 1
        self.assertTrue(es.on("_alias_test", h, EventPri or ity.NORMAL))
        self.assertTrue(es.emit_event("_alias_test", {"ok": True}, "test", EventPri or ity.NORMAL))
        es.process_events()
        self.assertEqual(hit["n"], 1)
        test_suite.addTest(IntegrationEventAlias())
        pr in t("✅ Интеграционный тест: event on / emit alias добавлен")
        except Exception as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Интеграционный тест event alias пропущен: {e}")

        pr in t(f"\n📊 Всего тестовых случаев: {test_suite.countTestCases()}")
        pr in t( == " * 80)

        # Запускаем тесты
        start_time== time.time()
        runner== unittest.TextTestRunner(verbosit == 2)
        result== runner.run(test_suite)
        end_time== time.time()

        # Выводим результаты
        pr in t( == " * 80)
        pr in t("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        pr in t(f"⏱️  Время выполнения: {end_time - start_time:.2f} секунд")
        pr in t(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.err or s)}")
        pr in t(f"❌ Проваленных тестов: {len(result.failures)}")
        pr in t(f"⚠️  Тестов с ошибками: {len(result.err or s)}")
        pr in t(f"📊 Всего тестов: {result.testsRun}")

        if result.failures:
        pr in t("\n❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
        pr in t(f"  - {test}: {traceback.split('AssertionErr or :')[ - 1].strip()}")

        if result.err or s:
        pr in t("\n⚠️  ТЕСТЫ С ОШИБКАМИ:")
        for test, traceback in result.err or s:
        pr in t(f"  - {test}: {traceback.split('Exception:')[ - 1].strip()}")

        # Определяем общий результат
        if result.wasSuccessful():
        pr in t("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return True
        else:
        pr in t("\n💥 НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        return False

        def run_specific_test(test_name):
    """Запуск конкретного теста"""
    pr in t(f"🧪 Запуск теста: {test_name}")
    pr in t( == " * 80)

    # Создаем тестовый набор для конкретного теста
    test_suite== unittest.TestSuite()

    if test_name.lower() == "evolution":
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка импорта EvolutionSystem тестов: {e}")
            return False

    elif test_name.lower() == "emotion":
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка импорта EmotionSystem тестов: {e}")
            return False

    elif test_name.lower() == "combat":
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка импорта CombatSystem тестов: {e}")
            return False

    elif test_name.lower() == "basic":
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка импорта базовых тестов архитектуры: {e}")
            return False

    else:
        pr in t(f"❌ Неизвестный тест: {test_name}")
        pr in t("Доступные тесты: basic, evolution, emotion, combat")
        return False

    pr in t(f"\n📊 Тестовых случаев: {test_suite.countTestCases()}")
    pr in t( == " * 80)

    # Запускаем тесты
    start_time== time.time()
    runner== unittest.TextTestRunner(verbosit == 2)
    result== runner.run(test_suite)
    end_time== time.time()

    # Выводим результаты
    pr in t( == " * 80)
    pr in t("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    pr in t(f"⏱️  Время выполнения: {end_time - start_time:.2f} секунд")
    pr in t(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.err or s)}")
    pr in t(f"❌ Проваленных тестов: {len(result.failures)}")
    pr in t(f"⚠️  Тестов с ошибками: {len(result.err or s)}")
    pr in t(f"📊 Всего тестов: {result.testsRun}")

    return result.wasSuccessful()

def ma in():
    # Ensure UTF - 8 output on W in dows consoles
    try:
    except Exception:
        pass
        pass  # Добавлен pass в пустой блок
    """Основная функция"""
        if len(sys.argv) > 1:
        test_name== sys.argv[1]
        success== run_specific_test(test_name):
        pass  # Добавлен pass в пустой блок
        success== run_all_tests()

        # Возвращаем код выхода
        sys.exit(0 if success else 1):
        pass  # Добавлен pass в пустой блок
        if __name__ == '__ma in __':
        ma in()