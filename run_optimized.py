#!/usr/bin/env python3
"""
AI-EVOLVE: Enhanced Edition - Оптимизированный запуск
Запускает игру с новой централизованной архитектурой и простыми объектами
"""

import os
import sys
import time
import logging
import traceback
from pathlib import Path

# Добавляем корневую директорию в путь
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

def setup_logging():
    """Настройка логирования"""
    log_dir = ROOT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настройка файлового обработчика
    file_handler = logging.FileHandler(
        log_dir / f"ai_evolve_optimized_{time.strftime('%Y%m%d_%H%M%S')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Настройка консольного обработчика
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Отключаем логи от сторонних библиотек
    logging.getLogger('pygame').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Ошибка: Требуется Python 3.8 или выше")
        print(f"   Текущая версия: {sys.version}")
        return False
    return True

def check_dependencies():
    """Проверка зависимостей"""
    required_packages = [
        'pygame',
        'numpy',
        'psutil'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Отсутствуют необходимые пакеты:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nУстановите их командой:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_directories():
    """Создание необходимых директорий"""
    directories = [
        "logs",
        "saves",
        "config",
        "graphics",
        "audio",
        "data"
    ]
    
    for directory in directories:
        dir_path = ROOT_DIR / directory
        dir_path.mkdir(exist_ok=True)

def initialize_database():
    """Инициализация базы данных"""
    try:
        from core.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        db_manager.initialize()
        logging.info("База данных инициализирована")
        return True
    except Exception as e:
        logging.error(f"Ошибка инициализации базы данных: {e}")
        return False

def show_banner():
    """Отображение баннера"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  █████  ██ ███████ ███████ ██   ██ ██    ██ ███████ ██   ██ ║
    ║ ██   ██ ██ ██      ██      ███  ██ ██    ██ ██      ███  ██ ║
    ║ ███████ ██ ███████ ███████ ████ ██ ██    ██ ███████ ████ ██ ║
    ║ ██   ██ ██      ██      ██ ██ ████ ██    ██      ██ ██ ████ ║
    ║ ██   ██ ██ ███████ ███████ ██  ████  ██████  ███████ ██  ███ ║
    ║                                                              ║
    ║                    Enhanced Edition                          ║
    ║                                                              ║
    ║  🚀 Оптимизированная архитектура                             ║
    ║  🎯 Улучшенная производительность                            ║
    ║  🛡️  Повышенная надежность                                  ║
    ║  🎨 Простые объекты с цветовой индикацией                   ║
    ║  🖥️  Современный HUD и UI                                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def run_game():
    """Запуск игры"""
    try:
        from core.game_engine import GameEngine
        
        # Создаем и запускаем движок
        engine = GameEngine()
        exit_code = engine.run()
        
        return exit_code
        
    except Exception as e:
        logging.error(f"Критическая ошибка запуска игры: {e}")
        logging.error(traceback.format_exc())
        return 1

def main():
    """Главная функция"""
    start_time = time.time()
    
    try:
        # Отображение баннера
        show_banner()
        
        # Настройка логирования
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("🎯 Запуск AI-EVOLVE: Enhanced Edition (Оптимизированная версия)")
        
        # Проверки
        if not check_python_version():
            return 1
        
        if not check_dependencies():
            return 1
        
        # Создание директорий
        create_directories()
        logger.info("📁 Директории созданы")
        
        # Инициализация базы данных
        if not initialize_database():
            logger.warning("⚠️  База данных не инициализирована, продолжаем без неё")
        
        # Запуск игры
        logger.info("🚀 Запуск игрового движка...")
        exit_code = run_game()
        
        # Завершение
        total_time = time.time() - start_time
        logger.info(f"✅ Игра завершена за {total_time:.2f} секунд")
        
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("⏹️  Игра прервана пользователем")
        return 0
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
        logging.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
