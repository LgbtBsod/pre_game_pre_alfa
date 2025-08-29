#!/usr/bin/env python3
"""
Проверка зависимостей AI-EVOLVE
"""

import os
import sys

def check_dependencies():
    """Проверка зависимостей"""
    print("🔧 Проверка зависимостей AI-EVOLVE...")
    print("=" * 50)
    
    required_files = [
        "src/systems/testing/integration_tester.py",
        "src/systems/testing/test_runner.py",
        "src/systems/integration/system_integrator.py",
        "src/demo/demo_launcher.py",
        "src/core/architecture.py",
        "src/core/game_engine.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)
    
    print()
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {len(missing_files)}")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Все необходимые файлы найдены")
    
    # Проверка импортов
    print("\n🔍 Проверка импортов...")
    
    try:
        from src.core.architecture import Event, create_event
        print("   ✅ Event и create_event импортированы успешно")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта Event: {e}")
        return False
    
    try:
        from src.core.architecture import ComponentManager, EventBus, StateManager
        print("   ✅ ComponentManager, EventBus, StateManager импортированы успешно")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта базовых компонентов: {e}")
        return False
    
    try:
        from src.systems.testing.integration_tester import IntegrationTester
        print("   ✅ IntegrationTester импортирован успешно")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта IntegrationTester: {e}")
        return False
    
    try:
        from src.systems.integration.system_integrator import SystemIntegrator
        print("   ✅ SystemIntegrator импортирован успешно")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта SystemIntegrator: {e}")
        return False
    
    print("\n🎉 Все зависимости проверены успешно!")
    return True

def main():
    """Основная функция"""
    success = check_dependencies()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
