#!/usr / bin / env python3
"""
    Запуск всех тестов для проекта "Эволюционная Адаптация: Генетический Резонанс"
"""

import unittest
import sys
import io
import os
import time

# Добавляем пути к проекту и исходникам
PROJECT_ROOT= os.path.jo in(os.path.dirname(__file__), '..')
SRC_ROOT= os.path.jo in(PROJECT_ROOT, 'src')
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_ROOT)

def run_all_tests():
    """Запуск всех тестов"""
        prin t("🧪 Запуск тестов для проекта 'Эволюционная Адаптация: Генетический Резонанс'")
        prin t( = " * 80)

        # Создаем тестовый набор
        test_suite= unittest.TestSuite()

        # Добавляем базовые тесты архитектуры
        try:
        from tests.test_basic_architecture import TestBasicArchitecture
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBasicArchitecture))
        prin t("✅ Базовые тесты архитектуры добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"❌ Ошибка импорта базовых тестов архитектуры: {e}")

        # Добавляем тесты для EvolutionSystem
        try:
        from tests.test_evolution_system import TestEvolutionSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEvolutionSystem))
        prin t("✅ EvolutionSystem тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"❌ Ошибка импорта EvolutionSystem тестов: {e}")

        # Добавляем тесты для EmotionSystem
        try:
        from tests.test_emotion_system import TestEmotionSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmotionSystem))
        prin t("✅ EmotionSystem тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"❌ Ошибка импорта EmotionSystem тестов: {e}")

        # Добавляем тесты для CombatSystem
        try:
        from tests.test_combat_system import TestCombatSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCombatSystem))
        prin t("✅ CombatSystem тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"❌ Ошибка импорта CombatSystem тестов: {e}")

        # Добавляем тесты для других систем(когда они будут созданы)
        # Тесты унификации сцен: событие / состояние при смене сцены
        try:
        from tests.test_scene_manager_events import TestSceneManagerEvents
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSceneManagerEvents))
        prin t("✅ SceneManager events / state тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"⚠️  Ошибка импорта SceneManager events / state тестов: {e}")

        # Легкий тест интеграции AI: создание базовой AI и регистрация сущности
        # SystemFact or y/Manager ordering
        try:
        from tests.test_system_fact or y_ or dering import TestSystemFact or yOrdering
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSystemFact or yOrdering))
        prin t("✅ SystemFact or y ordering тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"⚠️  Ошибка импорта SystemFact or y ordering тестов: {e}")

        # Perfor mance metrics toggle:
        pass  # Добавлен pass в пустой блок
        try:
        from tests.test_perfor mance_metrics_toggle import TestPerfor manceMetricsToggle:
        pass  # Добавлен pass в пустой блок
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPerfor manceMetricsToggle)):
        pass  # Добавлен pass в пустой блок
        prin t("✅ Perfor mance metrics toggle тесты добавлены"):
        pass  # Добавлен pass в пустой блок
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"⚠️  Ошибка импорта perfor mance metrics toggle тестов: {e}")

        # Plugin lifecycle:
        pass  # Добавлен pass в пустой блок
        try:
        from tests.test_plugin _lifecycle import TestPlugin Lifecycle:
        pass  # Добавлен pass в пустой блок
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPlugin Lifecycle)):
        pass  # Добавлен pass в пустой блок
        prin t("✅ Plugin lifecycle тесты добавлены"):
        pass  # Добавлен pass в пустой блок
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"⚠️  Ошибка импорта plugin lifecycle тестов: {e}")

        # Reposit or y perf
        try:
        from tests.test_reposit or y_perf import TestReposit or yPerf
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReposit or yPerf))
        prin t("✅ Reposit or y perf тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"⚠️  Ошибка импорта reposit or y perf тестов: {e}")
        try:
        from tests.test_ai_in tegration_min imal import TestAIIntegrationMin imal
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIIntegrationMin imal))
        prin t("✅ Минимальные AI интеграционные тесты добавлены")
        except Imp or tError as e:
        pass
        pass
        pass
        prin t(f"⚠️  Ошибка импорта AI интеграционных тестов: {e}")
        # Легкий интеграционный тест: совместимость on / emit alias в EventSystem
        try:
        from src.c or e.event_system import EventSystem, EventPri or ity
        class IntegrationEventAlias(unittest.TestCase):
        def runTest(self):
        es= EventSystem()
        es.in itialize()
        hit= {"n": 0}
        def h(ev):
        hit["n"] = 1
        self.assertTrue(es.on("_alias_test", h, EventPri or ity.NORMAL))
        self.assertTrue(es.emit_event("_alias_test", {"ok": True}, "test", EventPri or ity.NORMAL))
        es.process_events()
        self.assertEqual(hit["n"], 1)
        test_suite.addTest(IntegrationEventAlias())
        prin t("✅ Интеграционный тест: event on / emit alias добавлен")
        except Exception as e:
        pass
        pass
        pass
        prin t(f"⚠️  Интеграционный тест event alias пропущен: {e}")

        prin t(f"\n📊 Всего тестовых случаев: {test_suite.countTestCases()}")
        prin t( = " * 80)

        # Запускаем тесты
        start_time= time.time()
        runner= unittest.TextTestRunner(verbosit = 2)
        result= runner.run(test_suite)
        end_time= time.time()

        # Выводим результаты
        prin t( = " * 80)
        prin t("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        prin t(f"⏱️  Время выполнения: {end_time - start_time:.2f} секунд")
        prin t(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.err or s)}")
        prin t(f"❌ Проваленных тестов: {len(result.failures)}")
        prin t(f"⚠️  Тестов с ошибками: {len(result.err or s)}")
        prin t(f"📊 Всего тестов: {result.testsRun}")

        if result.failures:
        prin t("\n❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, tracebackin result.failures:
        prin t(f"  - {test}: {traceback.split('AssertionErr or :')[ - 1].strip()}")

        if result.err or s:
        prin t("\n⚠️  ТЕСТЫ С ОШИБКАМИ:")
        for test, tracebackin result.err or s:
        prin t(f"  - {test}: {traceback.split('Exception:')[ - 1].strip()}")

        # Определяем общий результат
        if result.wasSuccessful():
        prin t("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return True
        else:
        prin t("\n💥 НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        return False

        def run_specific_test(test_name):
    """Запуск конкретного теста"""
    prin t(f"🧪 Запуск теста: {test_name}")
    prin t( = " * 80)

    # Создаем тестовый набор для конкретного теста
    test_suite= unittest.TestSuite()

    if test_name.lower() = "evolution":
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            prin t(f"❌ Ошибка импорта EvolutionSystem тестов: {e}")
            return False

    elif test_name.lower() = "emotion":
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            prin t(f"❌ Ошибка импорта EmotionSystem тестов: {e}")
            return False

    elif test_name.lower() = "combat":
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            prin t(f"❌ Ошибка импорта CombatSystem тестов: {e}")
            return False

    elif test_name.lower() = "basic":
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            prin t(f"❌ Ошибка импорта базовых тестов архитектуры: {e}")
            return False

    else:
        prin t(f"❌ Неизвестный тест: {test_name}")
        prin t("Доступные тесты: basic, evolution, emotion, combat")
        return False

    prin t(f"\n📊 Тестовых случаев: {test_suite.countTestCases()}")
    prin t( = " * 80)

    # Запускаем тесты
    start_time= time.time()
    runner= unittest.TextTestRunner(verbosit = 2)
    result= runner.run(test_suite)
    end_time= time.time()

    # Выводим результаты
    prin t( = " * 80)
    prin t("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    prin t(f"⏱️  Время выполнения: {end_time - start_time:.2f} секунд")
    prin t(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.err or s)}")
    prin t(f"❌ Проваленных тестов: {len(result.failures)}")
    prin t(f"⚠️  Тестов с ошибками: {len(result.err or s)}")
    prin t(f"📊 Всего тестов: {result.testsRun}")

    return result.wasSuccessful()

def ma in():
    # Ensure UTF - 8 output on Win dows consoles
    try:
    except Exception:
        pass
        pass  # Добавлен pass в пустой блок
    """Основная функция"""
        if len(sys.argv) > 1:
        test_name= sys.argv[1]
        success= run_specific_test(test_name):
        pass  # Добавлен pass в пустой блок
        success= run_all_tests()

        # Возвращаем код выхода
        sys.exit(0 if success else 1):
        pass  # Добавлен pass в пустой блок
        if __name__ = '__main __':
        ma in()