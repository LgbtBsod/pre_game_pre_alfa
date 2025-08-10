#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности основных систем проекта AI EVOLVE.
"""

import sys
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_imports():
    """Тестирует импорт основных модулей"""
    logger.info("Тестирование импортов...")
    
    try:
        # Тестируем основные системы
        from config.settings_manager import settings_manager
        logger.info("✓ settings_manager импортирован")
        
        from core.data_manager import data_manager
        logger.info("✓ data_manager импортирован")
        
        from core.game_state_manager import game_state_manager
        logger.info("✓ game_state_manager импортирован")
        
        from entities.entity_factory import entity_factory
        logger.info("✓ entity_factory импортирован")
        
        from items.item_manager import item_manager
        logger.info("✓ item_manager импортирован")
        
        from core.game_logic_manager import GameLogicManager
        logger.info("✓ GameLogicManager импортирован")
        
        from ai.ai_manager import ai_manager
        logger.info("✓ ai_manager импортирован")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка импорта: {e}")
        return False


def test_initialization():
    """Тестирует инициализацию основных систем"""
    logger.info("Тестирование инициализации...")
    
    try:
        from config.settings_manager import settings_manager
        from core.data_manager import data_manager
        
        # Тестируем загрузку настроек
        settings_manager.reload_settings()
        logger.info("✓ Настройки загружены")
        
        # Тестируем загрузку данных
        data_manager.reload_data()
        logger.info("✓ Данные загружены")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка инициализации: {e}")
        return False


def test_entity_creation():
    """Тестирует создание сущностей"""
    logger.info("Тестирование создания сущностей...")
    
    try:
        from entities.entity_factory import entity_factory
        
        # Создаем игрока
        player = entity_factory.create_player("test_player", (0, 0))
        if player:
            logger.info("✓ Игрок создан успешно")
        else:
            logger.error("✗ Не удалось создать игрока")
            return False
        
        # Создаем врага
        enemy = entity_factory.create_enemy("warrior", 1, (100, 100))
        if enemy:
            logger.info("✓ Враг создан успешно")
        else:
            logger.error("✗ Не удалось создать врага")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка создания сущностей: {e}")
        return False


def test_ai_system():
    """Тестирует AI систему"""
    logger.info("Тестирование AI системы...")
    
    try:
        from ai.ai_manager import ai_manager
        from entities.entity_factory import entity_factory
        
        # Создаем сущность с AI
        entity = entity_factory.create_enemy("warrior", 1, (0, 0))
        
        # Регистрируем в AI системе
        if hasattr(entity, 'ai_core'):
            ai_manager.register_entity(entity, entity.ai_core)
            logger.info("✓ Сущность зарегистрирована в AI системе")
        else:
            logger.warning("⚠ Сущность не имеет AI компонента")
        
        # Обновляем AI
        ai_manager.update(0.016)  # 60 FPS
        logger.info("✓ AI система обновлена")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка AI системы: {e}")
        return False


def test_item_system():
    """Тестирует систему предметов"""
    logger.info("Тестирование системы предметов...")
    
    try:
        from items.item_manager import item_manager
        
        # Создаем предмет
        item = item_manager.create_item("health_potion")
        if item:
            logger.info("✓ Предмет создан успешно")
        else:
            logger.warning("⚠ Не удалось создать предмет")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка системы предметов: {e}")
        return False


def main():
    """Основная функция тестирования"""
    logger.info("=" * 50)
    logger.info("НАЧАЛО ТЕСТИРОВАНИЯ ПРОЕКТА AI EVOLVE")
    logger.info("=" * 50)
    
    tests = [
        ("Импорты", test_imports),
        ("Инициализация", test_initialization),
        ("Создание сущностей", test_entity_creation),
        ("AI система", test_ai_system),
        ("Система предметов", test_item_system),
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
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Проект готов к работе.")
        return 0
    else:
        logger.error(f"❌ {total - passed} тестов провалено. Требуется доработка.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
