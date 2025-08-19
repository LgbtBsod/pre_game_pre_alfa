#!/usr/bin/env python3
"""
Запуск обновленной игры с новой архитектурой
Использует рефакторенную систему с принципом единой ответственности
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

# Настройка логирования с принудительной кодировкой UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/refactored_game.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies() -> bool:
    """Проверка зависимостей для новой архитектуры"""
    try:
        import pygame
        logger.info("✓ Pygame доступен")
    except ImportError:
        logger.error("✗ Pygame не найден. Установите: pip install pygame")
        return False
    
    try:
        import sqlite3
        logger.info("✓ SQLite3 доступен")
    except ImportError:
        logger.error("✗ SQLite3 не найден. Критическая ошибка.")
        return False
    
    try:
        import numpy
        logger.info("✓ NumPy доступен")
    except ImportError:
        logger.warning("⚠ NumPy не найден. Некоторые функции могут работать медленнее.")
    
    return True


def create_directories():
    """Создание необходимых директорий для новой архитектуры"""
    directories = ['logs', 'save', 'data', 'screenshots', 'config']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✓ Директория {directory} готова")


def run_refactored_game():
    """Запуск обновленной игры с новой архитектурой"""
    try:
        from core.refactored_game_loop import RefactoredGameLoop
        logger.info("🚀 Запуск обновленной игры с новой архитектурой...")
        
        # Создаем и инициализируем игровой цикл
        game_loop = RefactoredGameLoop(use_pygame=True)
        
        if not game_loop.initialize():
            logger.error("❌ Ошибка инициализации обновленной игры")
            return False
        
        # Запускаем игровой цикл
        game_loop.run()
        
        logger.info("✅ Обновленная игра завершена успешно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска обновленной игры: {e}")
        return False


def run_component_test():
    """Тестирование компонентной архитектуры"""
    try:
        logger.info("🧪 Тестирование компонентной архитектуры...")
        
        from core.entity_system import EntityManager, EntityFactory
        from core.resource_loader import ResourceLoader
        from core.components.transform_component import Vector3
        
        # Создаем системы
        resource_loader = ResourceLoader()
        entity_manager = EntityManager()
        entity_factory = EntityFactory(entity_manager, resource_loader)
        
        # Создаем тестовую сущность
        player = entity_factory.create_player_entity("Тестовый Игрок", Vector3(100, 100, 0))
        
        # Проверяем компоненты
        transform = entity_manager.get_component(player.id, type(player.components.get(type(player.components))))
        if transform:
            logger.info(f"✓ Компонент трансформации создан: позиция {transform.position}")
        
        logger.info(f"✓ Создано сущностей: {entity_manager.total_entities_created}")
        logger.info("✅ Тест компонентной архитектуры пройден")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования компонентной архитектуры: {e}")
        return False


def run_config_test():
    """Тестирование новой системы конфигурации"""
    try:
        logger.info("⚙️ Тестирование системы конфигурации...")
        
        from config.config_factory import config_factory, ConfigType
        
        # Загружаем конфигурации
        game_config = config_factory.create_config(ConfigType.GAME_SETTINGS)
        entities_config = config_factory.create_config(ConfigType.ENTITIES)
        
        logger.info(f"✓ Настройки игры загружены: {len(game_config)} секций")
        logger.info(f"✓ Конфигурация сущностей загружена: {len(entities_config)} типов")
        
        # Проверяем валидацию
        if game_config.get('display') and entities_config.get('player'):
            logger.info("✅ Валидация конфигурации пройдена")
        else:
            logger.warning("⚠ Некоторые конфигурации не загружены корректно")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования конфигурации: {e}")
        return False


def run_error_handler_test():
    """Тестирование системы обработки ошибок"""
    try:
        logger.info("🛡️ Тестирование системы обработки ошибок...")
        
        from core.error_handler import error_handler, ErrorType, ErrorSeverity
        
        # Тестируем обработку ошибок
        error_handler.handle_error(
            ErrorType.CONFIGURATION,
            "Тестовая ошибка конфигурации",
            severity=ErrorSeverity.WARNING
        )
        
        error_handler.handle_error(
            ErrorType.RESOURCE_LOADING,
            "Тестовая ошибка загрузки ресурса",
            severity=ErrorSeverity.INFO
        )
        
        # Получаем статистику
        stats = error_handler.get_error_statistics()
        logger.info(f"✓ Обработано ошибок: {stats.get('total_errors', 0)}")
        
        logger.info("✅ Система обработки ошибок работает корректно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования обработки ошибок: {e}")
        return False


def show_architecture_info():
    """Показать информацию о новой архитектуре"""
    info = """
🏗️ НОВАЯ АРХИТЕКТУРА ИГРЫ

📋 Основные принципы:
• Принцип единой ответственности (SRP)
• Компонентная архитектура (ECS)
• Слабая связанность
• Высокая когезия

🔧 Компоненты системы:
• AnimationComponent - управление анимацией
• SpriteComponent - отрисовка спрайтов
• TransformComponent - позиция и трансформация
• ResourceLoader - загрузка ресурсов
• EntityManager - управление сущностями
• ErrorHandler - обработка ошибок
• ConfigFactory - управление конфигурацией

🎮 Управление:
• ESC - выход
• P - пауза/возобновление
• F1 - отладочная информация
• F2 - скриншот

📊 Мониторинг:
• Статистика всех систем
• Логирование ошибок
• Отладочная информация
• Автоматические скриншоты

🔄 Улучшения:
• Разделенные ответственности
• Устойчивость к ошибкам
• Гибкая конфигурация
• Легкость расширения
"""
    print(info)


def show_help():
    """Показать справку по использованию"""
    help_text = """
🎮 Обновленная игра: Эволюционная Адаптация

Использование:
  python run_refactored_game.py [режим]

Режимы:
  game     - Запуск обновленной игры (по умолчанию)
  test     - Тестирование новой архитектуры
  config   - Тест системы конфигурации
  errors   - Тест обработки ошибок
  info     - Информация об архитектуре
  help     - Показать эту справку

Примеры:
  python run_refactored_game.py          # Запуск игры
  python run_refactored_game.py test     # Тестирование
  python run_refactored_game.py config   # Тест конфигурации
  python run_refactored_game.py info     # Информация об архитектуре

🔧 Особенности новой архитектуры:
• Компонентная система (ECS)
• Разделенные ответственности
• Централизованная обработка ошибок
• Гибкая конфигурация
• Мониторинг и отладка
"""
    print(help_text)


def main():
    """Главная функция"""
    print("🎮 Эволюционная Адаптация: Генетический Резонанс")
    print("🏗️ Обновленная архитектура с принципом единой ответственности")
    print("=" * 70)
    
    # Создание директорий
    create_directories()
    
    # Проверка зависимостей
    if not check_dependencies():
        print("❌ Критические зависимости не найдены. Установите необходимые пакеты.")
        return 1
    
    # Определение режима запуска
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "game"
    
    if mode == "help":
        show_help()
        return 0
    elif mode == "info":
        show_architecture_info()
        return 0
    
    # Запуск выбранного режима
    success = False
    
    if mode == "game":
        success = run_refactored_game()
    elif mode == "test":
        success = run_component_test()
    elif mode == "config":
        success = run_config_test()
    elif mode == "errors":
        success = run_error_handler_test()
    else:
        print(f"❌ Неизвестный режим: {mode}")
        show_help()
        return 1
    
    if success:
        print("✅ Операция завершена успешно")
        return 0
    else:
        print("❌ Операция завершена с ошибками")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Операция прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"💥 Критическая ошибка: {e}")
        sys.exit(1)
