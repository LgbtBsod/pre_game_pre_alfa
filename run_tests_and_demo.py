#!/usr/bin/env python3
"""
AI-EVOLVE: Основной скрипт для запуска тестирования и демо-версии
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def print_header():
    """Вывод заголовка"""
    print("🎮" * 20)
    print("🎮 AI-EVOLVE: ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ 🎮")
    print("🎮 Генетический Резонанс - Демо-версия 🎮")
    print("🎮" * 20)
    print()

def print_menu():
    """Вывод меню"""
    print("📋 Доступные опции:")
    print("   1. 🧪 Запустить все тесты интеграции")
    print("   2. 🎮 Запустить демо-версию")
    print("   3. 🚀 Полный цикл: тесты + демо")
    print("   4. 📊 Показать статус проекта")
    print("   5. 🔧 Проверить зависимости")
    print("   0. ❌ Выход")
    print()

def check_dependencies():
    """Проверка зависимостей"""
    print("🔧 Проверка зависимостей...")
    
    required_files = [
        "src/systems/testing/integration_tester.py",
        "src/systems/testing/test_runner.py",
        "src/systems/integration/system_integrator.py",
        "src/demo/demo_launcher.py",
        "src/core/architecture/__init__.py",
        "src/core/game_engine.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Отсутствуют файлы:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Все необходимые файлы найдены")
    return True

def run_tests():
    """Запуск тестов"""
    print("🧪 Запуск тестов интеграции...")
    print("=" * 50)
    
    try:
        # Запускаем тесты
        result = subprocess.run([
            sys.executable, 
            "src/systems/testing/test_runner.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Выводим результат
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("⚠️ Предупреждения:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Тесты завершены успешно!")
            return True
        else:
            print("❌ Тесты завершились с ошибками")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")
        return False

def run_demo():
    """Запуск демо-версии"""
    print("🎮 Запуск демо-версии...")
    print("=" * 50)
    
    try:
        # Запускаем демо
        result = subprocess.run([
            sys.executable, 
            "src/demo/demo_launcher.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Выводим результат
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("⚠️ Предупреждения:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Демо-версия завершена успешно!")
            return True
        else:
            print("❌ Демо-версия завершилась с ошибками")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска демо: {e}")
        return False

def show_project_status():
    """Показать статус проекта"""
    print("📊 СТАТУС ПРОЕКТА AI-EVOLVE")
    print("=" * 50)
    
    # Проверяем основные компоненты
    components = {
        "Базовая архитектура": "src/core/architecture/",
        "Игровой движок": "src/core/game_engine.py",
        "Система интеграции": "src/systems/integration/",
        "UI система": "src/systems/ui/",
        "HUD система": "src/systems/ui/hud_system.py",
        "Боевая система": "src/systems/combat/",
        "Система здоровья": "src/systems/health/",
        "Система инвентаря": "src/systems/inventory/",
        "Система навыков": "src/systems/skills/",
        "Система эффектов": "src/systems/effects/",
        "Система тестирования": "src/systems/testing/",
        "Демо-версия": "src/demo/"
    }
    
    total_components = len(components)
    available_components = 0
    
    for name, path in components.items():
        if os.path.exists(path):
            print(f"   ✅ {name}")
            available_components += 1
        else:
            print(f"   ❌ {name}")
    
    print()
    print(f"📈 Общий прогресс: {available_components}/{total_components} компонентов")
    progress_percent = (available_components / total_components * 100) if total_components > 0 else 0
    print(f"   Процент готовности: {progress_percent:.1f}%")
    
    if progress_percent >= 95:
        print("🎉 Проект готов к демонстрации!")
    elif progress_percent >= 80:
        print("🚀 Проект близок к завершению!")
    elif progress_percent >= 60:
        print("⚡ Проект в активной разработке!")
    else:
        print("🔧 Проект требует доработки!")

def run_full_cycle():
    """Полный цикл: тесты + демо"""
    print("🚀 Запуск полного цикла: тесты + демо")
    print("=" * 50)
    
    # Шаг 1: Проверка зависимостей
    print("📋 Шаг 1: Проверка зависимостей")
    if not check_dependencies():
        print("❌ Зависимости не удовлетворены. Прерывание.")
        return False
    
    print()
    
    # Шаг 2: Запуск тестов
    print("📋 Шаг 2: Запуск тестов интеграции")
    if not run_tests():
        print("❌ Тесты не прошли. Демо-версия не может быть запущена.")
        return False
    
    print()
    
    # Шаг 3: Запуск демо
    print("📋 Шаг 3: Запуск демо-версии")
    if not run_demo():
        print("❌ Демо-версия не может быть запущена.")
        return False
    
    print()
    print("🎉 Полный цикл завершен успешно!")
    return True

def main():
    """Основная функция"""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input("Выберите опцию (0-5): ").strip()
            
            if choice == "0":
                print("👋 До свидания!")
                break
            elif choice == "1":
                run_tests()
            elif choice == "2":
                run_demo()
            elif choice == "3":
                run_full_cycle()
            elif choice == "4":
                show_project_status()
            elif choice == "5":
                check_dependencies()
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Прервано пользователем")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    main()
