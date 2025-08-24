#!/usr/bin/env python3
"""
AI-EVOLVE Enhanced Edition - Launcher
Основной файл запуска игры с новой модульной архитектурой на Panda3D
"""

import os
import sys
import time
import logging
import traceback
from pathlib import Path
from typing import Optional

# Добавляем корневую директорию в путь
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))

def setup_logging():
    """Настройка системы логирования"""
    log_dir = ROOT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый обработчик
    file_handler = logging.FileHandler(
        log_dir / f"ai_evolve_{time.strftime('%Y%m%d_%H%M%S')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Отключаем логи от сторонних библиотек
    logging.getLogger('panda3d').setLevel(logging.WARNING)

def check_python_version() -> bool:
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Ошибка: Требуется Python 3.8 или выше")
        print(f"   Текущая версия: {sys.version}")
        return False
    return True

def check_dependencies() -> bool:
    """Проверка зависимостей"""
    required_packages = ['panda3d', 'numpy']
    optional_packages = ['psutil', 'PIL']
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - доступен")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} - отсутствует")
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} - доступен (опционально)")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️  {package} - отсутствует (опционально)")
    
    if missing_required:
        print(f"\n❌ Отсутствуют необходимые пакеты: {', '.join(missing_required)}")
        print("Установите их командой:")
        print(f"pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Отсутствуют опциональные пакеты: {', '.join(missing_optional)}")
        print("Некоторые функции могут работать медленнее")
        print(f"pip install {' '.join(missing_optional)}")
    
    return True

def create_directories():
    """Создание необходимых директорий"""
    directories = [
        "logs",
        "saves",
        "config",
        "assets/audio",
        "assets/graphics",
        "assets/data",
        "assets/maps",
        "assets/models",
        "assets/textures",
        "assets/shaders"
    ]
    
    for directory in directories:
        dir_path = ROOT_DIR / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана директория: {directory}")

def initialize_game():
    """Инициализация игры"""
    try:
        print("🚀 Инициализация AI-EVOLVE Enhanced Edition на Panda3D...")
        
        # Создание директорий
        create_directories()
        
        # Импорт и инициализация игрового движка
        from core.game_engine import GameEngine
        from core.config_manager import ConfigManager
        
        # Загрузка конфигурации
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Создание игрового движка
        engine = GameEngine(config)
        
        print("✅ Игра успешно инициализирована!")
        return engine
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        logging.error(f"Ошибка инициализации: {e}")
        traceback.print_exc()
        return None

def main():
    """Главная функция"""
    print("🎮 AI-EVOLVE Enhanced Edition - Panda3D Version")
    print("=" * 50)
    
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Проверка версии Python
        if not check_python_version():
            return 1
        
        # Проверка зависимостей
        if not check_dependencies():
            return 1
        
        print("\n🔍 Проверка завершена успешно!")
        print("\n📂 Создание структуры проекта...")
        
        # Инициализация игры
        engine = initialize_game()
        if not engine:
            return 1
        
        print("\n🎯 Запуск игрового цикла...")
        
        # Запуск игрового цикла
        engine.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Игра остановлена пользователем")
        return 0
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
