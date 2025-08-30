#!/usr/bin/env python3
"""
Тестирование продвинутых возможностей утилиты исправления
"""
from fix_python_files import (
    analyze_file_damage,
    smart_repair_strategy,
    validate_python_syntax,
    advanced_string_fix,
    smart_bracket_fix,
    context_aware_fix,
    step_by_step_recovery
)

def test_advanced_string_fix():
    """Тестирует исправление сложных проблем со строками."""
    print("🔤 Тестирую исправление сложных проблем со строками...")
    
    # Тест 1: Незакрытая многострочная строка
    damaged_content1 = '''def test():
    docstring = """Это незакрытая
    многострочная строка
    return "test"
'''
    
    print(f"Тест 1 - Незакрытая многострочная строка:")
    print(f"Исходный код:\n{damaged_content1}")
    
    original_valid = validate_python_syntax(damaged_content1)
    print(f"Исходный синтаксис: {'✅ валиден' if original_valid else '❌ НЕ ВАЛИДЕН'}")
    
    fixed_content1 = advanced_string_fix(damaged_content1)
    final_valid = validate_python_syntax(fixed_content1)
    print(f"Итоговый синтаксис: {'✅ валиден' if final_valid else '❌ НЕ ВАЛИДЕН'}")
    
    if fixed_content1 != damaged_content1:
        print("✅ Строки были исправлены!")
        print(f"Исправленный код:\n{fixed_content1}")
    else:
        print("❌ Строки не были исправлены")
    
    return final_valid

def test_smart_bracket_fix():
    """Тестирует умное исправление скобок."""
    print("\n🔗 Тестирую умное исправление скобок...")
    
    # Тест 2: Несоответствие скобок
    damaged_content2 = '''def test(
    if condition(
        return value
    return result
'''
    
    print(f"Тест 2 - Несоответствие скобок:")
    print(f"Исходный код:\n{damaged_content2}")
    
    original_valid = validate_python_syntax(damaged_content2)
    print(f"Исходный синтаксис: {'✅ валиден' if original_valid else '❌ НЕ ВАЛИДЕН'}")
    
    fixed_content2 = smart_bracket_fix(damaged_content2)
    final_valid = validate_python_syntax(fixed_content2)
    print(f"Итоговый синтаксис: {'✅ валиден' if final_valid else '❌ НЕ ВАЛИДЕН'}")
    
    if fixed_content2 != damaged_content2:
        print("✅ Скобки были исправлены!")
        print(f"Исправленный код:\n{fixed_content2}")
    else:
        print("❌ Скобки не были исправлены")
    
    return final_valid

def test_context_aware_fix():
    """Тестирует контекстно-осознанные исправления."""
    print("\n🧠 Тестирую контекстно-осознанные исправления...")
    
    # Тест 3: Проблемы с отступами и двоеточиями
    damaged_content3 = '''def test()
    if condition
        return True
    else
        return False
'''
    
    print(f"Тест 3 - Проблемы с отступами и двоеточиями:")
    print(f"Исходный код:\n{damaged_content3}")
    
    original_valid = validate_python_syntax(damaged_content3)
    print(f"Исходный синтаксис: {'✅ валиден' if original_valid else '❌ НЕ ВАЛИДЕН'}")
    
    fixed_content3 = context_aware_fix(damaged_content3)
    final_valid = validate_python_syntax(fixed_content3)
    print(f"Итоговый синтаксис: {'✅ валиден' if final_valid else '❌ НЕ ВАЛИДЕН'}")
    
    if fixed_content3 != damaged_content3:
        print("✅ Контекстные исправления применены!")
        print(f"Исправленный код:\n{fixed_content3}")
    else:
        print("❌ Контекстные исправления не применены")
    
    return final_valid

def test_step_by_step_recovery():
    """Тестирует пошаговое восстановление."""
    print("\n🔄 Тестирую пошаговое восстановление...")
    
    # Тест 4: Комплексные проблемы
    damaged_content4 = '''def test(
    docstring = """Незакрытая строка
    if condition(
        return value
    return result
'''
    
    print(f"Тест 4 - Комплексные проблемы:")
    print(f"Исходный код:\n{damaged_content4}")
    
    original_valid = validate_python_syntax(damaged_content4)
    print(f"Исходный синтаксис: {'✅ валиден' if original_valid else '❌ НЕ ВАЛИДЕН'}")
    
    damage_report = analyze_file_damage(damaged_content4)
    print(f"Оценка повреждений: {damage_report['damage_score']}/100")
    print(f"Рекомендации: {', '.join(damage_report['recommendations'])}")
    
    print("\n🔧 Применяю пошаговое восстановление...")
    fixed_content4 = step_by_step_recovery(damaged_content4)
    final_valid = validate_python_syntax(fixed_content4)
    print(f"Итоговый синтаксис: {'✅ валиден' if final_valid else '❌ НЕ ВАЛИДЕН'}")
    
    if fixed_content4 != damaged_content4:
        print("✅ Пошаговое восстановление применено!")
        print(f"Исправленный код:\n{fixed_content4}")
    else:
        print("❌ Пошаговое восстановление не применено")
    
    return final_valid

def test_smart_repair_strategy():
    """Тестирует умную стратегию исправления."""
    print("\n🧠 Тестирую умную стратегию исправления...")
    
    # Тест 5: Стратегия исправления
    damaged_content5 = '''def test(
    docstring = """Незакрытая строка
    if condition(
        return value
    return result
'''
    
    print(f"Тест 5 - Умная стратегия исправления:")
    print(f"Исходный код:\n{damaged_content5}")
    
    original_valid = validate_python_syntax(damaged_content5)
    print(f"Исходный синтаксис: {'✅ валиден' if original_valid else '❌ НЕ ВАЛИДЕН'}")
    
    damage_report = analyze_file_damage(damaged_content5)
    print(f"Оценка повреждений: {damage_report['damage_score']}/100")
    print(f"Рекомендации: {', '.join(damage_report['recommendations'])}")
    
    print("\n🔧 Применяю умную стратегию исправления...")
    fixed_content5 = smart_repair_strategy(damaged_content5, damage_report)
    final_valid = validate_python_syntax(fixed_content5)
    print(f"Итоговый синтаксис: {'✅ валиден' if final_valid else '❌ НЕ ВАЛИДЕН'}")
    
    if fixed_content5 != damaged_content5:
        print("✅ Умная стратегия применена!")
        print(f"Исправленный код:\n{fixed_content5}")
    else:
        print("❌ Умная стратегия не применена")
    
    return final_valid

def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование продвинутых возможностей утилиты исправления")
    print("=" * 70)
    
    tests = [
        test_advanced_string_fix,
        test_smart_bracket_fix,
        test_context_aware_fix,
        test_step_by_step_recovery,
        test_smart_repair_strategy
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
    print("📊 Результаты тестирования:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ ПРОШЕЛ" if result else "❌ НЕ ПРОШЕЛ"
        print(f"  Тест {i}: {test.__name__} - {status}")
    
    print(f"\n🎯 Итого: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("⚠️ Некоторые тесты не прошли")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 Тестирование завершено успешно!")
    else:
        print("\n❌ Тестирование выявило проблемы")
