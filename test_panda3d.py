#!/usr/bin/env python3
"""
Минимальный тест Panda3D для выявления проблемы с окном
"""

import sys
import os

def test_panda3d_basic():
    """Базовый тест Panda3D"""
    print("🔍 Тестирование базовой функциональности Panda3D...")
    
    try:
        # Пробуем импортировать Panda3D
        print("📦 Импорт Panda3D...")
        
        # Способ 1: прямой импорт
        try:
            from panda3d.core import ShowBase, WindowProperties
            print("✅ Способ 1: прямой импорт успешен")
            showbase_import = True
        except ImportError as e:
            print(f"❌ Способ 1 не сработал: {e}")
            showbase_import = False
        
        # Способ 2: через direct
        try:
            from direct.showbase.ShowBase import ShowBase
            print("✅ Способ 2: через direct успешен")
            direct_import = True
        except ImportError as e:
            print(f"❌ Способ 2 не сработал: {e}")
            direct_import = False
        
        if not showbase_import and not direct_import:
            print("❌ Не удалось импортировать Panda3D")
            return False
        
        print("✅ Panda3D импортирован успешно")
        
        # Тестируем создание окна
        print("\n🪟 Тестирование создания окна...")
        
        try:
            # Создаем ShowBase
            print("🎬 Создание ShowBase...")
            base = ShowBase()
            print("✅ ShowBase создан")
            
            # Проверяем атрибуты
            print("🔍 Проверка атрибутов ShowBase...")
            attrs = ['render', 'render2d', 'camera', 'win', 'taskMgr']
            for attr in attrs:
                if hasattr(base, attr):
                    value = getattr(base, attr)
                    print(f"   ✅ {attr}: {type(value).__name__}")
                else:
                    print(f"   ❌ {attr}: отсутствует")
            
            # Проверяем окно
            if hasattr(base, 'win'):
                win = base.win
                print(f"\n🪟 Проверка окна: {type(win).__name__}")
                
                if hasattr(win, 'isValid'):
                    is_valid = win.isValid()
                    print(f"   📊 Окно валидно: {is_valid}")
                
                if hasattr(win, 'getXSize') and hasattr(win, 'getYSize'):
                    width = win.getXSize()
                    height = win.getYSize()
                    print(f"   📏 Размеры: {width}x{height}")
                
                if hasattr(win, 'getTitle'):
                    title = win.getTitle()
                    print(f"   🏷️  Заголовок: {title}")
            else:
                print("❌ Окно не найдено")
                return False
            
            # Тестируем простую сцену
            print("\n🎨 Тестирование простой сцены...")
            
            try:
                from panda3d.core import GeomNode, NodePath
                
                # Создаем простой узел
                test_node = GeomNode("test")
                test_np = base.render.attachNewNode(test_node)
                test_np.setPos(0, 0, 0)
                print("✅ Тестовый узел создан")
                
            except Exception as e:
                print(f"⚠️  Не удалось создать тестовый узел: {e}")
            
            # Тестируем запуск
            print("\n🚀 Тестирование запуска...")
            print("⚠️  ВНИМАНИЕ: Окно должно открыться и остаться открытым!")
            print("   Для выхода закройте окно или нажмите Ctrl+C")
            
            try:
                # Запускаем главный цикл
                print("🎬 Запуск base.run()...")
                base.run()
                print("✅ base.run() завершен")
                
            except KeyboardInterrupt:
                print("\n🛑 Получен сигнал прерывания")
            except Exception as e:
                print(f"❌ Ошибка при запуске: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания ShowBase: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_panda3d_alternatives():
    """Тестирование альтернативных способов"""
    print("\n🔄 Тестирование альтернативных способов...")
    
    # Проверяем переменные окружения
    print("🔍 Проверка переменных окружения...")
    env_vars = ['PANDA_PRC_DIR', 'PANDA_LOG', 'PANDA_WINDOW_TITLE']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"   📋 {var}: {value}")
        else:
            print(f"   ⚠️  {var}: не установлена")
    
    # Проверяем доступные модули
    print("\n🔍 Проверка доступных модулей...")
    modules = ['panda3d.core', 'direct.showbase', 'direct.gui', 'direct.task']
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}: доступен")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")

def main():
    """Главная функция"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ PANDA3D")
    print("=" * 60)
    
    # Тестируем альтернативы
    test_panda3d_alternatives()
    
    # Основной тест
    print("\n" + "=" * 60)
    print("🎯 ОСНОВНОЙ ТЕСТ")
    print("=" * 60)
    
    success = test_panda3d_basic()
    
    if success:
        print("\n🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("✅ Panda3D работает корректно")
    else:
        print("\n❌ ТЕСТ НЕ ПРОЙДЕН!")
        print("❌ Panda3D имеет проблемы")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
