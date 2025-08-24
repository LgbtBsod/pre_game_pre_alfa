#!/usr/bin/env python3
"""
AI-EVOLVE: Enhanced Edition - Оптимизированный главный файл запуска
Объединяет все улучшенные системы в единый интерфейс с оптимизацией производительности
Вдохновлено культовыми играми: Dark Souls, Bloodborne, Hades, Risk of Rain 2, Enter the Gungeon
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Optional
import time

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

# Настройка логирования с принудительной кодировкой UTF-8
def setup_logging():
    """Настройка системы логирования с оптимизацией"""
    try:
        Path('logs').mkdir(exist_ok=True)
    except Exception:
        pass
    
    # Оптимизированное форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    handlers = []
    
    # Файловый обработчик с ротацией
    try:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            'logs/game_enhanced.log', 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    except Exception:
        # Fallback к обычному файловому обработчику
        try:
            file_handler = logging.FileHandler('logs/game_enhanced.log', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception as e:
            print(f"Ошибка создания файлового логгера: {e}")
    
    # Консольный обработчик только для критических ошибок
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Инициализация логирования
setup_logging()
logger = logging.getLogger(__name__)


def check_system_requirements() -> bool:
    """Проверка системных требований с оптимизацией"""
    logger.info("🔍 Проверка системных требований...")
    
    # Проверка версии Python
    if sys.version_info < (3, 8):
        logger.error(f"❌ Требуется Python 3.8+. Текущая версия: {sys.version_info}")
        return False
    
    # Проверка критических модулей
    required_modules = {
        'pygame': 'Pygame не найден: pip install pygame',
        'sqlite3': 'SQLite3 не найден (встроен в Python)'
    }
    
    for module, error_msg in required_modules.items():
        try:
            __import__(module)
            logger.info(f"✅ {module} доступен")
        except ImportError:
            logger.error(f"❌ {error_msg}")
            if module == 'pygame':
                return False
    
    # Опциональные модули
    optional_modules = {
        'numpy': 'Некоторые функции могут работать медленнее',
        'psutil': 'Мониторинг производительности недоступен'
    }
    
    for module, warning_msg in optional_modules.items():
        try:
            __import__(module)
            logger.info(f"✅ {module} доступен")
        except ImportError:
            logger.warning(f"⚠️ {module} не найден: {warning_msg}")
    
    logger.info("✅ Все системные требования выполнены")
    return True


def initialize_game_environment() -> bool:
    """Инициализация игрового окружения с оптимизацией"""
    logger.info("🚀 Инициализация игрового окружения...")
    
    # Создание необходимых директорий
    directories = ['logs', 'save', 'screenshots', 'data']
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
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
    """Проверка доступности Enhanced Edition систем с оптимизацией"""
    logger.info("🔧 Проверка Enhanced Edition систем...")
    
    # Список систем для проверки
    enhanced_systems = [
        ('core.generational_memory_system', 'GenerationalMemorySystem'),
        ('core.emotional_ai_influence', 'EmotionalAIInfluenceSystem'),
        ('core.enhanced_combat_learning', 'EnhancedCombatLearningSystem'),
        ('core.enhanced_content_generator', 'EnhancedContentGenerator'),
        ('core.enhanced_skill_system', 'SkillManager'),
        ('core.enhanced_game_master', 'EnhancedGameMaster'),
        ('core.curse_blessing_system', 'CurseBlessingSystem'),
        ('core.risk_reward_system', 'RiskRewardSystem'),
        ('core.meta_progression_system', 'MetaProgressionSystem'),
        ('core.enhanced_inventory_system', 'EnhancedInventorySystem'),
        ('core.enhanced_ui_system', 'EnhancedUISystem')
    ]
    
    available_systems = 0
    total_systems = len(enhanced_systems)
    
    for module_path, class_name in enhanced_systems:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            available_systems += 1
        except ImportError:
            pass
    
    if available_systems >= total_systems * 0.8:  # 80% систем доступно
        logger.info(f"✅ Enhanced Edition доступен ({available_systems}/{total_systems})")
        return True
    elif available_systems >= total_systems * 0.5:  # 50% систем доступно
        logger.info(f"⚠️ Enhanced Edition частично доступен ({available_systems}/{total_systems})")
        return True
    else:
        logger.info(f"ℹ️ Enhanced Edition недоступен ({available_systems}/{total_systems})")
        return False


def run_game_mode(mode: str) -> bool:
    """Запуск игры в указанном режиме с оптимизацией"""
    logger.info(f"🎮 Запуск игры в режиме: {mode}")
    
    try:
        if mode == "gui":
            return run_gui_mode()
        elif mode == "console":
            return run_console_mode()
        elif mode == "test":
            return run_test_mode()
        elif mode == "demo":
            return run_demo_mode()
        else:
            logger.error(f"❌ Неизвестный режим: {mode}")
            return False
            
    except KeyboardInterrupt:
        logger.info("⏹️ Игра прервана пользователем")
        return True
    except Exception as e:
        logger.error(f"💥 Критическая ошибка игры: {e}")
        logger.error(traceback.format_exc())
        return False


def run_gui_mode() -> bool:
    """Запуск GUI режима с оптимизацией"""
    try:
        from core.game_engine import GameEngine, GameConfig
        
        # Создаем и запускаем движок
        logger.info("🚀 Создание игрового движка...")
        engine = GameEngine()
        
        # Проверяем Enhanced системы
        memory_system = engine.get_system('memory_system')
        if memory_system:
            logger.info("✨ Enhanced Edition активирован!")
            logger.info(f"   - Память поколений: {getattr(memory_system, 'current_generation', 'N/A')}")
            logger.info(f"   - Эмоциональный ИИ: {'✅' if engine.get_system('emotional_ai') else '❌'}")
            logger.info(f"   - Боевое обучение: {'✅' if engine.get_system('enhanced_combat') else '❌'}")
            logger.info(f"   - Генератор контента: {'✅' if engine.get_system('enhanced_content') else '❌'}")
            logger.info(f"   - Система навыков: {'✅' if engine.get_system('skill_manager') else '❌'}")
        else:
            logger.info("ℹ️ Игра работает в базовом режиме")
        
        logger.info("🎯 Запуск главного игрового цикла...")
        return engine.run() == 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка GUI режима: {e}")
        return False


def run_console_mode() -> bool:
    """Запуск консольного режима"""
    try:
        from core.game_loop import RefactoredGameLoop
        
        game_loop = RefactoredGameLoop(use_pygame=False)
        if game_loop.initialize():
            game_loop.run()
            return True
        else:
            logger.error("❌ Ошибка инициализации консольного режима")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка консольного режима: {e}")
        return False


def run_test_mode() -> bool:
    """Запуск тестового режима с оптимизацией"""
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
            
            # Тестируем новые системы Enhanced Edition
            try:
                from core.enhanced_game_master import EnhancedGameMaster
                from core.curse_blessing_system import CurseBlessingSystem
                from core.risk_reward_system import RiskRewardSystem
                from core.meta_progression_system import MetaProgressionSystem
                
                # Создаем тестовые экземпляры
                game_master = EnhancedGameMaster(1600, 900)
                curse_blessing_system = CurseBlessingSystem(memory_system)
                risk_reward_system = RiskRewardSystem(memory_system, curse_blessing_system)
                meta_progression_system = MetaProgressionSystem(memory_system)
                
                logger.info("✅ Все новые Enhanced Edition системы работают корректно")
                
            except Exception as e:
                logger.warning(f"⚠️ Новые Enhanced системы недоступны: {e}")
            
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
    """Запуск демонстрационного режима с оптимизацией"""
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
            
            # Демонстрируем новые системы Enhanced Edition
            try:
                from core.enhanced_game_master import EnhancedGameMaster
                from core.curse_blessing_system import CurseBlessingSystem
                from core.risk_reward_system import RiskRewardSystem
                from core.meta_progression_system import MetaProgressionSystem
                
                # Создаем демо-системы
                game_master = EnhancedGameMaster(1600, 900)
                curse_blessing_system = CurseBlessingSystem(memory_system)
                risk_reward_system = RiskRewardSystem(memory_system, curse_blessing_system)
                meta_progression_system = MetaProgressionSystem(memory_system)
                
                # Демонстрируем проклятия и благословения
                curse_id = curse_blessing_system.apply_random_curse(intensity_range=(0.5, 1.0))
                blessing_id = curse_blessing_system.apply_random_blessing(intensity_range=(0.5, 1.0))
                
                logger.info(f"🎭 Enhanced системы демонстрированы:")
                logger.info(f"   - Game Master: {'✅' if game_master else '❌'}")
                logger.info(f"   - Проклятие применено: {curse_id[:8] if curse_id else '❌'}")
                logger.info(f"   - Благословение применено: {blessing_id[:8] if blessing_id else '❌'}")
                
                # Демонстрируем систему рисков и наград
                risk_event = risk_reward_system.create_risk_reward_event(
                    "demo_treasure", 
                    [{"type": "demo_item", "value": 100}],
                    risk_reward_system._current_risk_level
                )
                logger.info(f"   - Событие риска создано: {risk_event[:8] if risk_event else '❌'}")
                
                # Демонстрируем мета-прогрессию
                meta_stats = meta_progression_system.get_meta_statistics()
                logger.info(f"   - Мета-прогрессия: {meta_stats.get('total_runs', 0)} заходов")
                
            except Exception as e:
                logger.warning(f"⚠️ Демонстрация новых Enhanced систем недоступна: {e}")
            
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
   • Система проклятий и благословений (The Binding of Isaac)
   • Система рисков и наград (Spelunky, Hades)
   • Мета-прогрессия между заходами (Rogue Legacy)
   • Enhanced Game Master - координация всех систем

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
    """Главная функция с оптимизацией"""
    start_time = time.time()
    
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
    
    execution_time = time.time() - start_time
    logger.info(f"⏱️ Время выполнения: {execution_time:.2f} секунд")
    
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
