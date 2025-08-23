#!/usr/bin/env python3
"""
Главный файл запуска игры "Эволюционная Адаптация: Генетический Резонанс"
Улучшенная версия с обработкой ошибок и оптимизацией
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Optional

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    # Создаем директорию для логов
    Path('logs').mkdir(exist_ok=True)
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройка обработчиков
    handlers = []
    
    # Файловый обработчик
    file_handler = logging.FileHandler('logs/game.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Инициализация логирования
setup_logging()
logger = logging.getLogger(__name__)


def check_system_requirements():
    """Проверка системных требований"""
    logger.info("Проверка системных требований...")
    
    # Проверка версии Python
    if sys.version_info < (3, 8):
        logger.error(f"Требуется Python 3.8+. Текущая версия: {sys.version_info}")
        return False
    
    # Проверка критических модулей
    try:
        import pygame
        import numpy
        import sqlite3
        logger.info("Все критические модули найдены")
    except ImportError as e:
        logger.error(f"Отсутствует критический модуль: {e}")
        logger.error("Установите зависимости: pip install -r requirements.txt")
        return False
    
    return True


def initialize_game_environment():
    """Инициализация игрового окружения"""
    logger.info("Инициализация игрового окружения...")
    
    # Создание необходимых директорий
    directories = ['logs', 'save', 'screenshots', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.debug(f"Директория {directory} готова")
    
    # Инициализация базы данных
    try:
        from core.database_initializer import database_initializer
        if not database_initializer.initialize_database():
            logger.error("Ошибка инициализации базы данных")
            return False
    except Exception as e:
        logger.error(f"Критическая ошибка базы данных: {e}")
        return False
    
    logger.info("Игровое окружение инициализировано")
    return True


def run_game_mode(mode: str):
    """Запуск игры в указанном режиме"""
    logger.info(f"Запуск игры в режиме: {mode}")
    
    try:
        if mode == "gui":
            from ui.game_interface import GameInterface
            from config.config_manager import config_manager
            
            # Загружаем настройки
            settings_class = getattr(
                __import__('ui.game_interface', fromlist=['GameSettings']), 
                'GameSettings'
            )
            settings = settings_class.from_config()
            
            # Создаем и запускаем игру
            game = GameInterface(settings)
            game.run()
            
        elif mode == "console":
            from core.game_loop import RefactoredGameLoop
            
            game_loop = RefactoredGameLoop(use_pygame=False)
            if game_loop.initialize():
                game_loop.run()
            else:
                logger.error("Ошибка инициализации консольного режима")
                return False
                
        elif mode == "test":
            return run_test_mode()
            
        elif mode == "demo":
            return run_demo_mode()
            
        else:
            logger.error(f"Неизвестный режим: {mode}")
            return False
            
        return True
        
    except KeyboardInterrupt:
        logger.info("Игра прервана пользователем")
        return True
    except Exception as e:
        logger.error(f"Критическая ошибка игры: {e}")
        logger.error(traceback.format_exc())
        return False


def run_test_mode():
    """Запуск тестового режима"""
    logger.info("Запуск тестового режима...")
    
    try:
        # Импортируем и тестируем основные системы
        from core.effect_system import EffectDatabase
        from core.genetic_system import AdvancedGeneticSystem
        from core.emotion_system import AdvancedEmotionSystem
        from core.ai_system import AdaptiveAISystem
        from core.performance_manager import performance_optimizer
        
        # Создаем тестовые экземпляры
        effect_db = EffectDatabase()
        genetic_system = AdvancedGeneticSystem(effect_db)
        emotion_system = AdvancedEmotionSystem(effect_db)
        ai_system = AdaptiveAISystem("TEST_AI")
        
        logger.info("✅ Все основные системы работают корректно")
        
        # Тестируем производительность
        performance_optimizer.start_monitoring()
        import time
        time.sleep(2)  # Тестируем 2 секунды
        performance_optimizer.stop_monitoring()
        
        metrics = performance_optimizer.get_performance_report()
        logger.info(f"✅ Система производительности: {metrics['current_metrics']['memory_mb']:.1f} MB")
        
        logger.info("✅ Тестовый режим завершен успешно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестового режима: {e}")
        logger.error(traceback.format_exc())
        return False


def run_demo_mode():
    """Запуск демонстрационного режима"""
    logger.info("Запуск демонстрационного режима...")
    
    try:
        from core.content_generator import ContentGenerator
        from core.advanced_entity import AdvancedGameEntity
        
        # Создаем демо-контент
        generator = ContentGenerator()
        world = generator.generate_world(biome="forest", size="small", difficulty=0.5)
        
        # Создаем демо-сущности
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
        
        logger.info(f"✅ Демо-мир создан: {world.name}")
        logger.info(f"✅ Биомов: {len(world.biomes)}")
        logger.info(f"✅ Игрок: {player.name}")
        logger.info(f"✅ Враг: {enemy.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка демо режима: {e}")
        logger.error(traceback.format_exc())
        return False


def show_help():
    """Показать справку"""
    help_text = """
🎮 Эволюционная Адаптация: Генетический Резонанс

Использование:
    python main.py [режим]

Режимы:
    gui     - Графический интерфейс (по умолчанию)
    console - Консольный режим  
    test    - Тестовый режим
    demo    - Демонстрационный режим
    help    - Показать эту справку

Примеры:
    python main.py          # Запуск GUI
    python main.py console  # Консольный режим
    python main.py test     # Тестирование систем
    python main.py demo     # Демонстрация возможностей

Альтернативные способы запуска:
    python launcher.py      # Автоматическая проверка и запуск
    python run_game.py      # Оригинальный лаунчер
"""
    print(help_text)


def main():
    """Главная функция"""
    print("🎮 Эволюционная Адаптация: Генетический Резонанс")
    print("=" * 60)
    
    # Определяем режим
    mode = "gui"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    if mode == "help":
        show_help()
        return 0
    
    # Проверяем системные требования
    if not check_system_requirements():
        logger.error("❌ Системные требования не выполнены")
        return 1
    
    # Инициализируем окружение
    if not initialize_game_environment():
        logger.error("❌ Ошибка инициализации игрового окружения")
        return 1
    
    # Запускаем игру
    success = run_game_mode(mode)
    
    if success:
        logger.info("✅ Игра завершена успешно")
        return 0
    else:
        logger.error("❌ Игра завершена с ошибками")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        logger.error(traceback.format_exc())
        input("Нажмите Enter для выхода...")
        sys.exit(1)
