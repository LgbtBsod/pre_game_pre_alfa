#!/usr/bin/env python3
"""
Тест функциональности стартового меню
"""

print("🧪 Тест функциональности стартового меню...")

try:
    print("📦 Импорт...")
    from direct.showbase.ShowBase import ShowBase
    from direct.gui.DirectFrame import DirectFrame
    from direct.gui.DirectButton import DirectButton
    from direct.gui.DirectLabel import DirectLabel
    print("✅ Импорт успешен")
    
    print("🎬 Создание ShowBase...")
    base = ShowBase()
    print("✅ ShowBase создан")
    
    print("🎮 Создание тестового меню...")
    
    # Создаем тестовую панель
    test_frame = DirectFrame(
        frameColor=(0.2, 0.2, 0.2, 0.8),
        frameSize=(-0.3, 0.3, -0.4, 0.4),
        pos=(0, 0, 0)
    )
    test_frame.reparentTo(base.render2d)
    print("✅ Тестовая панель создана")
    
    # Создаем заголовок
    title = DirectLabel(
        parent=test_frame,
        text="ТЕСТ МЕНЮ",
        scale=0.05,
        pos=(0, 0, 0.25),
        text_fg=(1, 1, 1, 1)
    )
    print("✅ Заголовок создан")
    
    # Функции для тестирования
    def test_button_click():
        print("🎯 КНОПКА НАЖАТА!")
    
    def test_button_click2():
        print("🎯 ВТОРАЯ КНОПКА НАЖАТА!")
    
    # Создаем тестовые кнопки
    button1 = DirectButton(
        parent=test_frame,
        text="ТЕСТ КНОПКА 1",
        scale=0.04,
        pos=(0, 0, 0.1),
        frameColor=(0.3, 0.6, 0.3, 1),
        text_fg=(1, 1, 1, 1),
        command=test_button_click,
        relief=1,
        borderWidth=(0.01, 0.01)
    )
    print("✅ Кнопка 1 создана")
    
    button2 = DirectButton(
        parent=test_frame,
        text="ТЕСТ КНОПКА 2",
        scale=0.04,
        pos=(0, 0, -0.1),
        frameColor=(0.6, 0.3, 0.3, 1),
        text_fg=(1, 1, 1, 1),
        command=test_button_click2,
        relief=1,
        borderWidth=(0.01, 0.01)
    )
    print("✅ Кнопка 2 создана")
    
    # Проверяем свойства кнопок
    print("\n🔍 Проверка свойств кнопок:")
    print(f"   📊 Кнопка 1 имеет обработчик: {hasattr(button1, 'command')}")
    print(f"   📊 Кнопка 2 имеет обработчик: {hasattr(button2, 'command')}")
    print(f"   🔗 Родитель кнопки 1: {button1.getParent()}")
    print(f"   🔗 Родитель кнопки 2: {button2.getParent()}")
    
    # Проверяем mouseWatcherNode
    if hasattr(base, 'mouseWatcherNode'):
        mouse_watcher = base.mouseWatcherNode
        if mouse_watcher:
            print(f"   ✅ mouseWatcherNode доступен")
            if hasattr(mouse_watcher, 'hasMouse'):
                has_mouse = mouse_watcher.hasMouse()
                print(f"   📊 Мышь в окне: {has_mouse}")
        else:
            print(f"   ⚠️  mouseWatcherNode не инициализирован")
    else:
        print(f"   ⚠️  mouseWatcherNode не найден")
    
    print("\n🚀 Запуск теста...")
    print("⚠️  Попробуйте нажать на кнопки!")
    print("   Для выхода закройте окно или нажмите Ctrl+C")
    
    base.run()
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
