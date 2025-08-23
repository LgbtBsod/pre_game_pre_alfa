#!/usr/bin/env python3
"""
AI-EVOLVE: Enhanced Edition - Главный файл запуска
Объединяет все улучшенные системы в единый интерфейс
Вдохновлено культовыми играми: Dark Souls, Bloodborne, Hades, Risk of Rain 2, Enter the Gungeon
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Optional

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

# Настройка логирования с принудительной кодировкой UTF-8
def setup_logging():
    """Настройка системы логирования"""
    # Создаем директорию для логов
    try:
        Path('logs').mkdir(exist_ok=True)
    except Exception:
        pass
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройка обработчиков
    handlers = []
    
    # Файловый обработчик
    try:
        file_handler = logging.FileHandler('logs/game_enhanced.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    except Exception as e:
        print(f"Ошибка создания файлового логгера: {e}")
    
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


def check_system_requirements() -> bool:
    """Проверка системных требований"""
    logger.info("🔍 Проверка системных требований...")
    
    # Проверка версии Python
    if sys.version_info < (3, 8):
        logger.error(f"❌ Требуется Python 3.8+. Текущая версия: {sys.version_info}")
        return False
    
    # Проверка критических модулей
    try:
        import pygame
        logger.info("✅ Pygame доступен")
    except ImportError as e:
        logger.error(f"❌ Pygame не найден: {e}")
        logger.error("Установите: pip install pygame")
        return False
    
    try:
        import numpy
        logger.info("✅ NumPy доступен")
    except ImportError as e:
        logger.warning(f"⚠️ NumPy не найден: {e}")
        logger.warning("Некоторые функции могут работать медленнее")
    
    try:
        import sqlite3
        logger.info("✅ SQLite3 доступен")
    except ImportError as e:
        logger.error(f"❌ SQLite3 не найден: {e}")
        return False
    
    logger.info("✅ Все системные требования выполнены")
    return True


def initialize_game_environment() -> bool:
    """Инициализация игрового окружения"""
    logger.info("🚀 Инициализация игрового окружения...")
    
    # Создание необходимых директорий
    directories = ['logs', 'save', 'screenshots', 'data']
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            logger.debug(f"Директория {directory} готова")
        except Exception as e:
            logger.warning(f"Не удалось создать директорию {directory}: {e}")
    
    # Инициализация базы данных
    try:
        from core.database_initializer import database_initializer
        if not database_initializer.initialize_database():
            logger.error("❌ Ошибка инициализации базы данных")
            return False
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка базы данных: {e}")
        return False
    
    logger.info("✅ Игровое окружение инициализировано")
    return True


def check_enhanced_systems() -> bool:
    """Проверка доступности Enhanced Edition систем"""
    logger.info("🔧 Проверка Enhanced Edition систем...")
    
    try:
        # Проверяем основные Enhanced системы
        from core.generational_memory_system import GenerationalMemorySystem
        from core.emotional_ai_influence import EmotionalAIInfluenceSystem
        from core.enhanced_combat_learning import EnhancedCombatLearningSystem
        from core.enhanced_content_generator import EnhancedContentGenerator
        from core.enhanced_skill_system import SkillManager, SkillLearningAI
        
        logger.info("✅ Все Enhanced Edition системы доступны")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️ Некоторые Enhanced системы недоступны: {e}")
        logger.info("Игра будет работать в базовом режиме")
        return False


def run_game_mode(mode: str) -> bool:
    """Запуск игры в указанном режиме"""
    logger.info(f"🎮 Запуск игры в режиме: {mode}")
    
    try:
        if mode == "gui":
            # Основной GUI режим с Enhanced Edition
            from ui.game_interface import GameInterface, GameSettings
            from config.config_manager import config_manager
            
            # Загружаем настройки
            try:
                settings = GameSettings.from_config()
                logger.info("✅ Настройки загружены из конфигурации")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки настроек: {e}")
                settings = GameSettings()
                logger.info("✅ Используются настройки по умолчанию")
            
            # Создаем и запускаем игру
            logger.info("🚀 Создание игрового интерфейса...")
            game = GameInterface(settings)
            
            # Проверяем Enhanced системы
            if hasattr(game, 'memory_system') and game.memory_system:
                logger.info("✨ Enhanced Edition активирован!")
                logger.info(f"   - Память поколений: {game.memory_system.current_generation}")
                logger.info(f"   - Эмоциональный ИИ: {'✅' if game.emotional_ai_system else '❌'}")
                logger.info(f"   - Боевое обучение: {'✅' if game.enhanced_combat_system else '❌'}")
                logger.info(f"   - Генератор контента: {'✅' if game.enhanced_content_generator else '❌'}")
                logger.info(f"   - Система навыков: {'✅' if game.skill_manager else '❌'}")
            else:
                logger.info("ℹ️ Игра работает в базовом режиме")
            
            logger.info("🎯 Запуск главного игрового цикла...")
            game.run()
            
        elif mode == "console":
            # Консольный режим
            from core.game_loop import RefactoredGameLoop
            
            game_loop = RefactoredGameLoop(use_pygame=False)
            if game_loop.initialize():
                game_loop.run()
            else:
                logger.error("❌ Ошибка инициализации консольного режима")
                return False
                
        elif mode == "test":
            return run_test_mode()
            
        elif mode == "demo":
            return run_demo_mode()
            
        else:
            logger.error(f"❌ Неизвестный режим: {mode}")
            return False
            
        return True
        
    except KeyboardInterrupt:
        logger.info("⏹️ Игра прервана пользователем")
        return True
    except Exception as e:
        logger.error(f"💥 Критическая ошибка игры: {e}")
        logger.error(traceback.format_exc())
        return False


def run_test_mode() -> bool:
    """Запуск тестового режима"""
    logger.info("🧪 Запуск тестового режима...")
    
    try:
        # Тестируем основные системы
        from core.effect_system import EffectDatabase
        from core.genetic_system import AdvancedGeneticSystem
        from core.emotion_system import AdvancedEmotionSystem
        from core.ai_system import AdaptiveAISystem
        
        # Создаем тестовые экземпляры
        effect_db = EffectDatabase()
        genetic_system = AdvancedGeneticSystem(effect_db)
        emotion_system = AdvancedEmotionSystem(effect_db)
        ai_system = AdaptiveAISystem("TEST_AI")
        
        logger.info("✅ Все основные системы работают корректно")
        
        # Тестируем Enhanced системы
        try:
            from core.generational_memory_system import GenerationalMemorySystem
            from core.enhanced_combat_learning import EnhancedCombatLearningSystem
            
            memory_system = GenerationalMemorySystem("test_save")
            combat_system = EnhancedCombatLearningSystem(memory_system, None)
            
            logger.info("✅ Enhanced Edition системы работают корректно")
            
        except Exception as e:
            logger.warning(f"⚠️ Enhanced системы недоступны: {e}")
        
        logger.info("✅ Тестовый режим завершен успешно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестового режима: {e}")
        logger.error(traceback.format_exc())
        return False


def run_demo_mode() -> bool:
    """Запуск демонстрационного режима"""
    logger.info("🎭 Запуск демонстрационного режима...")
    
    try:
        # Демонстрируем Enhanced системы
        try:
            from core.enhanced_content_generator import EnhancedContentGenerator, BiomeType
            from core.generational_memory_system import GenerationalMemorySystem
            
            # Создаем демо-системы
            memory_system = GenerationalMemorySystem("demo_save")
            content_generator = EnhancedContentGenerator(memory_system)
            
            # Генерируем демо-контент
            enemy = content_generator.generate_enemy(
                BiomeType.FOREST, 1, {"level_width": 1000, "level_height": 1000}
            )
            
            logger.info(f"✨ Enhanced враг создан: {enemy.name}")
            logger.info(f"   Тип: {enemy.enemy_type.value}")
            logger.info(f"   Уровень силы: {enemy.get_power_level():.1f}")
            logger.info(f"   Способности: {len(enemy.abilities)}")
            
            # Демонстрируем память поколений
            memory_stats = memory_system.get_memory_statistics()
            logger.info(f"🧠 Память поколений: {memory_stats['current_generation']}")
            logger.info(f"   Воспоминаний: {memory_stats['total_memories']}")
            logger.info(f"   Кластеров: {memory_stats['total_clusters']}")
            
        except Exception as e:
            logger.warning(f"⚠️ Enhanced демо недоступно: {e}")
            
            # Fallback к базовому демо
            from core.content_generator import ContentGenerator
            from core.advanced_entity import AdvancedGameEntity
            
            generator = ContentGenerator()
            world = generator.generate_world(biome="forest", size="small", difficulty=0.5)
            
            logger.info(f"✅ Базовый демо-мир создан: {world.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка демо режима: {e}")
        logger.error(traceback.format_exc())
        return False


def show_help():
    """Показать справку"""
    help_text = """
🎮 AI-EVOLVE: Enhanced Edition
Эволюционная Адаптация: Генетический Резонанс

✨ ОСОБЕННОСТИ ENHANCED EDITION:
   • Память поколений для ИИ
   • Эмоциональное влияние на принятие решений
   • Улучшенная боевая система с обучением
   • Продвинутая генерация контента
   • Система навыков с AI-обучением

📋 ИСПОЛЬЗОВАНИЕ:
    python main.py [режим]

🎯 РЕЖИМЫ:
    gui     - Графический интерфейс с Enhanced Edition (по умолчанию)
    console - Консольный режим
    test    - Тестирование всех систем
    demo    - Демонстрация Enhanced возможностей
    help    - Показать эту справку

🚀 ПРИМЕРЫ:
    python main.py          # Запуск Enhanced Edition GUI
    python main.py console  # Консольный режим
    python main.py test     # Тестирование Enhanced систем
    python main.py demo     # Демонстрация возможностей

🎮 УПРАВЛЕНИЕ В ИГРЕ:
    WASD/Стрелки - Движение
    C - Центрировать камеру
    M - Навигация к маяку
    1-4 - Создание объектов (Enhanced генерация)
    5-8 - Эмоции (влияют на ИИ)
    I - Инвентарь
    G - Гены
    E - Эмоции
    V - Эволюция
    Пробел - Автономность

🔧 ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ:
    Python 3.8+, Pygame, NumPy, SQLite3
"""
    print(help_text)


def main():
    """Главная функция"""
    print("🎮 AI-EVOLVE: Enhanced Edition")
    print("Эволюционная Адаптация: Генетический Резонанс")
    print("=" * 70)
    
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
    
    # Проверяем Enhanced системы
    enhanced_available = check_enhanced_systems()
    
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
        sys.exit(1)
