#!/usr/bin/env python3
"""
Очень простой тест Panda3D
"""

print("🧪 Простой тест Panda3D...")

try:
    print("📦 Импорт...")
    from direct.showbase.ShowBase import ShowBase
    print("✅ Импорт успешен")
    
    print("🎬 Создание ShowBase...")
    base = ShowBase()
    print("✅ ShowBase создан")
    
    print("🪟 Проверка окна...")
    if hasattr(base, 'win'):
        win = base.win
        print(f"✅ Окно найдено: {type(win).__name__}")
        
        if hasattr(win, 'isValid'):
            is_valid = win.isValid()
            print(f"📊 Окно валидно: {is_valid}")
        
        if hasattr(win, 'getXSize') and hasattr(win, 'getYSize'):
            width = win.getXSize()
            height = win.getYSize()
            print(f"📏 Размеры: {width}x{height}")
    else:
        print("❌ Окно не найдено")
    
    print("🚀 Запуск...")
    print("⚠️  Окно должно открыться!")
    base.run()
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
