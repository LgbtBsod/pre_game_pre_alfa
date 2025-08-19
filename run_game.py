#!/usr/bin/env python3
"""
Главный запуск игры "Эволюционная Адаптация: Генетический Резонанс"
Поддерживает различные режимы запуска: GUI, консоль, тест, демо
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
        logging.FileHandler('logs/game.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies() -> bool:
    """Проверка зависимостей"""
    try:
        import pygame
        logger.info("Pygame доступен")
    except ImportError:
        logger.warning("Pygame не найден. GUI режим недоступен.")
        return False
    
    try:
        import sqlite3
        logger.info("SQLite3 доступен")
    except ImportError:
        logger.error("SQLite3 не найден. Игра не может работать.")
        return False
    
    try:
        import numpy
        logger.info("NumPy доступен")
    except ImportError:
        logger.warning("NumPy не найден. Некоторые функции могут работать медленнее.")
    
    return True


def create_directories():
    """Создание необходимых директорий"""
    directories = ['logs', 'save', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Директория {directory} готова")


def run_graphical_interface():
    """Запуск графического интерфейса"""
    try:
        from ui.game_interface import GameInterface
        logger.info("Запуск графического интерфейса...")
        
        game = GameInterface()
        game.run()
        
    except Exception as e:
        logger.error(f"Ошибка запуска GUI: {e}")
        print(f"Ошибка запуска графического интерфейса: {e}")
        return False
    
    return True


def run_console_mode():
    """Запуск консольного режима"""
    try:
        from core.refactored_game_loop import RefactoredGameLoop
        logger.info("Запуск консольного режима...")
        
        game_loop = RefactoredGameLoop(use_pygame=False)
        game_loop.initialize()
        game_loop.run()
        
    except Exception as e:
        logger.error(f"Ошибка запуска консольного режима: {e}")
        print(f"Ошибка запуска консольного режима: {e}")
        return False
    
    return True


def run_test_mode():
    """Запуск тестового режима"""
    try:
        logger.info("Запуск тестового режима...")
        
        # Тестирование основных систем
        from core.effect_system import EffectDatabase
        from core.genetic_system import AdvancedGeneticSystem
        from core.emotion_system import AdvancedEmotionSystem
        from core.ai_system import AdaptiveAISystem
        
        # Создание тестовых экземпляров
        effect_db = EffectDatabase()
        genetic_system = AdvancedGeneticSystem(effect_db)
        emotion_system = AdvancedEmotionSystem(effect_db)
        ai_system = AdaptiveAISystem(entity_id="TEST_AI")
        
        logger.info("Все основные системы инициализированы успешно")
        print("✓ Все основные системы работают корректно")
        
        # Тестирование базы данных
        try:
            from core.database_manager import database_manager
            effects = database_manager.get_effects()
            logger.info(f"База данных доступна: {len(effects)} эффектов загружено")
            print(f"✓ База данных: {len(effects)} эффектов")
        except Exception as e:
            logger.warning(f"Проблема с базой данных: {e}")
            print(f"⚠ База данных: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестового режима: {e}")
        print(f"✗ Ошибка тестирования: {e}")
        return False


def run_demo_mode():
    """Запуск демонстрационного режима"""
    try:
        logger.info("Запуск демонстрационного режима...")
        
        # Создание демо мира
        from core.content_generator import ContentGenerator
        from core.advanced_entity import AdvancedGameEntity
        
        generator = ContentGenerator()
        world = generator.generate_world(biome="forest", size="small", difficulty=0.5)
        
        # Создание демо сущностей
        player = AdvancedGameEntity(
            entity_id="DEMO_PLAYER",
            entity_type="player",
            name="Демо Игрок",
            position=(0, 0, 0)
        )
        
        enemy = AdvancedGameEntity(
            entity_id="DEMO_ENEMY",
            entity_type="enemy",
            name="Демо Враг",
            position=(100, 0, 0)
        )
        
        logger.info("Демо режим запущен успешно")
        print("✓ Демо режим: мир и сущности созданы")
        print(f"  - Мир: {world.name}, seed: {world.seed}")
        print(f"  - Биомы: {len(world.biomes)}")
        print(f"  - Игрок: {player.name}")
        print(f"  - Враг: {enemy.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка демо режима: {e}")
        print(f"✗ Ошибка демо режима: {e}")
        return False


def show_help():
    """Показать справку по использованию"""
    help_text = """
Эволюционная Адаптация: Генетический Резонанс

Использование:
  python run_game.py [режим]

Режимы:
  gui     - Графический интерфейс (по умолчанию)
  console - Консольный режим
  test    - Тестовый режим
  demo    - Демонстрационный режим
  help    - Показать эту справку

Примеры:
  python run_game.py          # Запуск GUI
  python run_game.py console  # Запуск консоли
  python run_game.py test     # Запуск тестов
  python run_game.py demo     # Запуск демо
"""
    print(help_text)


def main():
    """Главная функция"""
    print("🎮 Эволюционная Адаптация: Генетический Резонанс")
    print("=" * 50)
    
    # Создание директорий
    create_directories()
    
    # Проверка зависимостей
    if not check_dependencies():
        print("❌ Критические зависимости не найдены. Установите необходимые пакеты.")
        return 1
    
    # Определение режима запуска
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "gui"
    
    if mode == "help":
        show_help()
        return 0
    
    # Запуск выбранного режима
    success = False
    
    if mode == "gui":
        success = run_graphical_interface()
    elif mode == "console":
        success = run_console_mode()
    elif mode == "test":
        success = run_test_mode()
    elif mode == "demo":
        success = run_demo_mode()
    else:
        print(f"❌ Неизвестный режим: {mode}")
        show_help()
        return 1
    
    if success:
        print("✅ Игра завершена успешно")
        return 0
    else:
        print("❌ Игра завершена с ошибками")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Игра прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"💥 Критическая ошибка: {e}")
        sys.exit(1)
