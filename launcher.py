#!/usr/bin/env python3
"""
Простой лаунчер для игры "Эволюционная Адаптация: Генетический Резонанс"
Проверяет зависимости и запускает игру в безопасном режиме
"""

import sys
import os
import traceback
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        logger.error(f"❌ Требуется Python 3.8+. Текущая версия: {sys.version_info}")
        return False
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_dependencies():
    """Проверка основных зависимостей"""
    dependencies = {
        'pygame': 'Графический движок',
        'numpy': 'Математические вычисления', 
        'sqlite3': 'База данных',
    }
    
    missing = []
    for dep, desc in dependencies.items():
        try:
            __import__(dep)
            logger.info(f"✅ {dep} - {desc}")
        except ImportError:
            logger.warning(f"⚠️ {dep} не найден - {desc}")
            missing.append(dep)
    
    if missing:
        logger.warning(f"Отсутствуют зависимости: {', '.join(missing)}")
        logger.info("Запустите: pip install pygame numpy")
    
    return len(missing) == 0


def check_game_files():
    """Проверка игровых файлов"""
    required_files = [
        'run_game.py',
        'core/__init__.py',
        'ui/__init__.py',
        'config/game_settings.json'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
        else:
            logger.info(f"✅ {file_path}")
    
    if missing:
        logger.error(f"❌ Отсутствуют файлы: {', '.join(missing)}")
        return False
    
    return True


def create_directories():
    """Создание необходимых директорий"""
    dirs = ['logs', 'save', 'screenshots']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        logger.info(f"✅ Директория {dir_name}")


def run_game_safe():
    """Безопасный запуск игры"""
    try:
        logger.info("🚀 Запуск игры...")
        
        # Добавляем путь к игре
        game_dir = Path(__file__).parent
        if str(game_dir) not in sys.path:
            sys.path.insert(0, str(game_dir))
        
        # Импортируем и запускаем
        from run_game import main as game_main
        return game_main()
        
    except KeyboardInterrupt:
        logger.info("🛑 Игра прервана пользователем")
        return 0
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        logger.error("Проверьте установку зависимостей")
        return 1
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        logger.error("Трассировка:")
        logger.error(traceback.format_exc())
        return 1


def main():
    """Главная функция лаунчера"""
    print("🎮 AI-EVOLVE: Эволюционная Адаптация")
    print("=" * 50)
    
    # Проверяем систему
    if not check_python_version():
        input("Нажмите Enter для выхода...")
        return 1
    
    # Создаем директории
    create_directories()
    
    # Проверяем файлы
    if not check_game_files():
        input("Нажмите Enter для выхода...")
        return 1
    
    # Проверяем зависимости
    deps_ok = check_dependencies()
    if not deps_ok:
        logger.warning("⚠️ Некоторые зависимости отсутствуют")
        logger.info("Игра может работать некорректно")
        
        choice = input("Продолжить? (y/n): ").lower()
        if choice != 'y':
            return 1
    
    # Запускаем игру
    result = run_game_safe()
    
    if result == 0:
        logger.info("✅ Игра завершена успешно")
    else:
        logger.error("❌ Игра завершена с ошибками")
    
    return result


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"💥 Критическая ошибка лаунчера: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
