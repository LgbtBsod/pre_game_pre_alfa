#!/usr/bin/env python3
"""
Ультра-простой тест Panda3D
"""

print("🧪 Ультра-простой тест Panda3D...")

try:
    print("📦 Импорт...")
    from direct.showbase.ShowBase import ShowBase
    print("✅ Импорт успешен")
    
    print("🎬 Создание ShowBase...")
    base = ShowBase()
    print("✅ ShowBase создан")
    
    print("🔍 Проверка базовых компонентов...")
    
    # Проверяем render2d
    if hasattr(base, 'render2d'):
        print("✅ render2d доступен")
    else:
        print("❌ render2d недоступен")
        exit(1)
    
    # Проверяем mouseWatcherNode
    if hasattr(base, 'mouseWatcherNode'):
        mouse_watcher = base.mouseWatcherNode
        if mouse_watcher:
            print("✅ mouseWatcherNode доступен")
            if hasattr(mouse_watcher, 'hasMouse'):
                has_mouse = mouse_watcher.hasMouse()
                print(f"📊 Мышь в окне: {has_mouse}")
        else:
            print("⚠️  mouseWatcherNode не инициализирован")
    else:
        print("❌ mouseWatcherNode не найден")
    
    print("\n🎮 Создание простейшего меню...")
    
    # Создаем простую панель
    from direct.gui.DirectFrame import DirectFrame
    panel = DirectFrame(
        frameColor=(0.5, 0.5, 0.5, 0.8),
        frameSize=(-0.2, 0.2, -0.2, 0.2),
        pos=(0, 0, 0)
    )
    panel.reparentTo(base.render2d)
    print("✅ Панель создана")
    
    # Создаем простую кнопку
    from direct.gui.DirectButton import DirectButton
    
    def test_click():
        print("🎯 КНОПКА НАЖАТА!")
    
    button = DirectButton(
        parent=panel,
        text="ТЕСТ",
        scale=0.03,
        pos=(0, 0, 0),
        frameColor=(0.3, 0.6, 0.3, 1),
        text_fg=(1, 1, 1, 1),
        command=test_click
    )
    print("✅ Кнопка создана")
    
    # Проверяем свойства кнопки
    print(f"📊 Кнопка имеет обработчик: {hasattr(button, 'command')}")
    print(f"📊 Обработчик вызываемый: {callable(button.command)}")
    print(f"🔗 Родитель кнопки: {button.getParent()}")
    
    print("\n🚀 Запуск...")
    print("⚠️  Попробуйте нажать на кнопку ТЕСТ!")
    print("   Для выхода закройте окно или нажмите Ctrl+C")
    
    base.run()
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
