#!/usr/bin/env python3
"""
Запуск всех тестов для проекта "Эволюционная Адаптация: Генетический Резонанс"
"""

import unittest
import sys
import os
import time

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов для проекта 'Эволюционная Адаптация: Генетический Резонанс'")
    print("=" * 80)
    
    # Создаем тестовый набор
    test_suite = unittest.TestSuite()
    
    # Добавляем базовые тесты архитектуры
    try:
        from tests.test_basic_architecture import TestBasicArchitecture
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBasicArchitecture))
        print("✅ Базовые тесты архитектуры добавлены")
    except ImportError as e:
        print(f"❌ Ошибка импорта базовых тестов архитектуры: {e}")
    
    # Добавляем тесты для EvolutionSystem
    try:
        from tests.test_evolution_system import TestEvolutionSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEvolutionSystem))
        print("✅ EvolutionSystem тесты добавлены")
    except ImportError as e:
        print(f"❌ Ошибка импорта EvolutionSystem тестов: {e}")
    
    # Добавляем тесты для EmotionSystem
    try:
        from tests.test_emotion_system import TestEmotionSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmotionSystem))
        print("✅ EmotionSystem тесты добавлены")
    except ImportError as e:
        print(f"❌ Ошибка импорта EmotionSystem тестов: {e}")
    
    # Добавляем тесты для CombatSystem
    try:
        from tests.test_combat_system import TestCombatSystem
        test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCombatSystem))
        print("✅ CombatSystem тесты добавлены")
    except ImportError as e:
        print(f"❌ Ошибка импорта CombatSystem тестов: {e}")
    
    # Добавляем тесты для других систем (когда они будут созданы)
    
    print(f"\n📊 Всего тестовых случаев: {test_suite.countTestCases()}")
    print("=" * 80)
    
    # Запускаем тесты
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    end_time = time.time()
    
    # Выводим результаты
    print("=" * 80)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"⏱️  Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Проваленных тестов: {len(result.failures)}")
    print(f"⚠️  Тестов с ошибками: {len(result.errors)}")
    print(f"📊 Всего тестов: {result.testsRun}")
    
    if result.failures:
        print("\n❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n⚠️  ТЕСТЫ С ОШИБКАМИ:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Определяем общий результат
    if result.wasSuccessful():
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return True
    else:
        print("\n💥 НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        return False

def run_specific_test(test_name):
    """Запуск конкретного теста"""
    print(f"🧪 Запуск теста: {test_name}")
    print("=" * 80)
    
    # Создаем тестовый набор для конкретного теста
    test_suite = unittest.TestSuite()
    
    if test_name.lower() == "evolution":
        try:
            from tests.test_evolution_system import TestEvolutionSystem
            test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEvolutionSystem))
            print("✅ EvolutionSystem тесты добавлены")
        except ImportError as e:
            print(f"❌ Ошибка импорта EvolutionSystem тестов: {e}")
            return False
    
    elif test_name.lower() == "emotion":
        try:
            from tests.test_emotion_system import TestEmotionSystem
            test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmotionSystem))
            print("✅ EmotionSystem тесты добавлены")
        except ImportError as e:
            print(f"❌ Ошибка импорта EmotionSystem тестов: {e}")
            return False
    
    elif test_name.lower() == "combat":
        try:
            from tests.test_combat_system import TestCombatSystem
            test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCombatSystem))
            print("✅ CombatSystem тесты добавлены")
        except ImportError as e:
            print(f"❌ Ошибка импорта CombatSystem тестов: {e}")
            return False
    
    elif test_name.lower() == "basic":
        try:
            from tests.test_basic_architecture import TestBasicArchitecture
            test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBasicArchitecture))
            print("✅ Базовые тесты архитектуры добавлены")
        except ImportError as e:
            print(f"❌ Ошибка импорта базовых тестов архитектуры: {e}")
            return False
    
    else:
        print(f"❌ Неизвестный тест: {test_name}")
        print("Доступные тесты: basic, evolution, emotion, combat")
        return False
    
    print(f"\n📊 Тестовых случаев: {test_suite.countTestCases()}")
    print("=" * 80)
    
    # Запускаем тесты
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    end_time = time.time()
    
    # Выводим результаты
    print("=" * 80)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"⏱️  Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Проваленных тестов: {len(result.failures)}")
    print(f"⚠️  Тестов с ошибками: {len(result.errors)}")
    print(f"📊 Всего тестов: {result.testsRun}")
    
    return result.wasSuccessful()

def main():
    """Основная функция"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        success = run_all_tests()
    
    # Возвращаем код выхода
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
