#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Panda3D
"""

import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_panda3d_import():
    """Тестирует импорт Panda3D"""
    logger.info("Тестирование импорта Panda3D...")
    
    try:
        from direct.showbase.ShowBase import ShowBase
        logger.info("✓ ShowBase импортирован успешно")
        
        from panda3d.core import Vec3, Vec4, Point3
        logger.info("✓ Основные классы Panda3D импортированы")
        
        from direct.gui.OnscreenText import OnscreenText
        logger.info("✓ OnscreenText импортирован")
        
        from direct.gui.DirectButton import DirectButton
        logger.info("✓ DirectButton импортирован")
        
        return True
        
    except ImportError as e:
        logger.error(f"✗ Ошибка импорта Panda3D: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Неожиданная ошибка: {e}")
        return False


def test_panda3d_window():
    """Тестирует создание окна Panda3D"""
    logger.info("Тестирование создания окна Panda3D...")
    
    try:
        from direct.showbase.ShowBase import ShowBase
        
        # Создаем базовое приложение
        base = ShowBase()
        
        # Проверяем, что окно создано
        if base.win:
            logger.info("✓ Окно Panda3D создано успешно")
            
            # Получаем размеры окна
            width = base.win.get_x_size()
            height = base.win.get_y_size()
            logger.info(f"✓ Размеры окна: {width}x{height}")
            
            # Закрываем приложение
            base.userExit()
            logger.info("✓ Приложение закрыто")
            
            return True
        else:
            logger.error("✗ Окно не создано")
            return False
            
    except Exception as e:
        logger.error(f"✗ Ошибка создания окна: {e}")
        return False


def test_simple_scene():
    """Тестирует создание простой сцены"""
    logger.info("Тестирование создания простой сцены...")
    
    try:
        from direct.showbase.ShowBase import ShowBase
        from panda3d.core import Vec3, Vec4, Point3, CardMaker
        from direct.gui.OnscreenText import OnscreenText
        
        # Создаем базовое приложение
        base = ShowBase()
        
        # Создаем простую плоскость
        cm = CardMaker("test_plane")
        cm.set_frame(-1, 1, -1, 1)
        plane = base.render.attach_new_node(cm.generate())
        plane.set_color(Vec4(0.5, 0.5, 0.5, 1.0))
        
        # Создаем текст
        text = OnscreenText(
            text="Panda3D работает!",
            pos=(0, 0),
            scale=0.1,
            fg=(1, 1, 1, 1)
        )
        
        logger.info("✓ Простая сцена создана")
        logger.info("✓ Должно появиться окно с серой плоскостью и текстом")
        logger.info("✓ Нажмите ESC для выхода")
        
        # Запускаем приложение
        base.run()
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка создания сцены: {e}")
        return False


def main():
    """Основная функция тестирования"""
    logger.info("=" * 50)
    logger.info("ТЕСТИРОВАНИЕ PANDA3D")
    logger.info("=" * 50)
    
    tests = [
        ("Импорт Panda3D", test_panda3d_import),
        ("Создание окна", test_panda3d_window),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Тест: {test_name} ---")
        if test_func():
            passed += 1
            logger.info(f"✓ {test_name} - ПРОЙДЕН")
        else:
            logger.error(f"✗ {test_name} - ПРОВАЛЕН")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Panda3D работает корректно.")
        
        # Спрашиваем пользователя о запуске демо
        try:
            response = input("\nЗапустить демо сцены? (y/n): ").lower().strip()
            if response in ['y', 'yes', 'да', 'д']:
                logger.info("Запуск демо сцены...")
                test_simple_scene()
        except KeyboardInterrupt:
            logger.info("Демо отменено пользователем")
        
        return 0
    else:
        logger.error(f"❌ {total - passed} тестов провалено. Panda3D не работает корректно.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
