#!/usr/bin/env python3
"""
Тестирование улучшенной утилиты исправления
"""
from fix_python_files import (
    analyze_file_damage,
    smart_repair_strategy,
    validate_python_syntax,
    enhanced_step_by_step_recovery,
    ultra_aggressive_repair
)

def test_complex_damage_scenario():
    """Тестирует сложный сценарий повреждения."""
    print("💀 Тестирую сложный сценарий повреждения...")
    
    # Создаем файл с множественными проблемами
    damaged_content = '''def broken_function(
    docstring = """Незакрытая многострочная строка
    if condition(
        return value
    return result

class BrokenClass
    def broken_method
        if broken_condition
            return broken_value
        else
            return other_value

import os
from typing import *
from pathlib import Path

def another_function
    try
        result = some_calculation(
        return result
    except
        return None
'''
    
    print(f"Исходный код:\n{damaged_content}")
    
    original_valid = validate_python_syntax(damaged_content)
    print(f"Исходный синтаксис: {'✅ валиден' if original_valid else '❌ НЕ ВАЛИДЕН'}")
    
    damage_report = analyze_file_damage(damaged_content)
    print(f"Оценка повреждений: {damage_report['damage_score']}/100")
    print(f"Рекомендации: {', '.join(damage_report['recommendations'])}")
    
    print("\n🔧 Применяю улучшенное пошаговое восстановление...")
    fixed_content = enhanced_step_by_step_recovery(damaged_content)
    final_valid = validate_python_syntax(fixed_content)
    print(f"Итоговый синтаксис: {'✅ валиден' if final_valid else '❌ НЕ ВАЛИДЕН'}")
    
    if fixed_content != damaged_content:
        print("✅ Файл был исправлен!")
        print(f"Исправленный код:\n{fixed_content}")
    else:
        print("❌ Файл не был исправлен")
    
    return final_valid

def test_ultra_aggressive_repair():
    """Тестирует ультра-агрессивный ремонт."""
    print("\n💀 Тестирую ультра-агрессивный ремонт...")
    
    # Создаем критически поврежденный файл
    critical_content = '''def critical_function
    docstring = """Критически поврежденная строка
    if critical_condition(
        return critical_value
    return critical_result

class CriticalClass
    def critical_method
        if critical_condition
            return critical_value
        else
            return other_value

import os
from typing import *
from pathlib import Path

def another_critical_function
    try
        result = critical_calculation(
        return result
    except
        return None
'''
    
    print(f"Критически поврежденный код:\n{critical_content}")
    
    original_valid = validate_python_syntax(critical_content)
    print(f"Исходный синтаксис: {'✅ валиден' if original_valid else '❌ НЕ ВАЛИДЕН'}")
    
    damage_report = analyze_file_damage(critical_content)
    print(f"Оценка повреждений: {damage_report['damage_score']}/100")
    print(f"Рекомендации: {', '.join(damage_report['recommendations'])}")
    
    print("\n🔧 Применяю ультра-агрессивный ремонт...")
    fixed_content = ultra_aggressive_repair(critical_content)
    final_valid = validate_python_syntax(fixed_content)
    print(f"Итоговый синтаксис: {'✅ валиден' if final_valid else '❌ НЕ ВАЛИДЕН'}")
    
    if fixed_content != critical_content:
        print("✅ Критически поврежденный файл был исправлен!")
        print(f"Исправленный код:\n{fixed_content}")
    else:
        print("❌ Критически поврежденный файл не был исправлен")
    
    return final_valid

def test_smart_strategy():
    """Тестирует умную стратегию исправления."""
    print("\n🧠 Тестирую умную стратегию исправления...")
    
    # Создаем файл с умеренными повреждениями
    moderate_content = '''def moderate_function
    docstring = """Умеренно поврежденная строка
    if moderate_condition(
        return moderate_value
    return moderate_result
'''
    
    print(f"Умеренно поврежденный код:\n{moderate_content}")
    
    original_valid = validate_python_syntax(moderate_content)
    print(f"Исходный синтаксис: {'✅ валиден' if original_valid else '❌ НЕ ВАЛИДЕН'}")
    
    damage_report = analyze_file_damage(moderate_content)
    print(f"Оценка повреждений: {damage_report['damage_score']}/100")
    print(f"Рекомендации: {', '.join(damage_report['recommendations'])}")
    
    print("\n🔧 Применяю умную стратегию исправления...")
    fixed_content = smart_repair_strategy(moderate_content, damage_report)
    final_valid = validate_python_syntax(fixed_content)
    print(f"Итоговый синтаксис: {'✅ валиден' if final_valid else '❌ НЕ ВАЛИДЕН'}")
    
    if fixed_content != moderate_content:
        print("✅ Умеренно поврежденный файл был исправлен!")
        print(f"Исправленный код:\n{fixed_content}")
    else:
        print("❌ Умеренно поврежденный файл не был исправлен")
    
    return final_valid

def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование улучшенной утилиты исправления")
    print("=" * 70)
    
    tests = [
        test_complex_damage_scenario,
        test_ultra_aggressive_repair,
        test_smart_strategy
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Ошибка в тесте {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("📊 Результаты тестирования улучшенной утилиты:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ ПРОШЕЛ" if result else "❌ НЕ ПРОШЕЛ"
        print(f"  Тест {i}: {test.__name__} - {status}")
    
    print(f"\n🎯 Итого: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно! Утилита готова к работе!")
    else:
        print("⚠️ Некоторые тесты не прошли, требуется дополнительная доработка")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 Тестирование завершено успешно!")
        print("🚀 Утилита готова к исправлению сложных проблем!")
    else:
        print("\n❌ Тестирование выявило проблемы")
        print("🔧 Требуется дополнительная доработка")
