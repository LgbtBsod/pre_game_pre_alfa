#!/usr/bin/env python3
"""
Скрипт автоматической установки зависимостей и запуска игры
"Эволюционная Адаптация: Генетический Резонанс"
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        logger.error("Требуется Python 3.8 или выше!")
        logger.error(f"Текущая версия: {sys.version}")
        return False
    
    logger.info(f"Python версия: {sys.version}")
    return True


def install_dependencies():
    """Установка зависимостей"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        logger.error("Файл requirements.txt не найден!")
        return False
    
    try:
        logger.info("Установка зависимостей...")
        
        # Обновляем pip
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        
        # Устанавливаем зависимости
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        logger.info("Зависимости успешно установлены!")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка установки зависимостей: {e}")
        return False


def check_assets():
    """Проверка наличия игровых ресурсов"""
    required_dirs = [
        "graphics",
        "audio", 
        "data",
        "config"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        logger.warning(f"Отсутствуют директории: {', '.join(missing_dirs)}")
        logger.warning("Игра может работать некорректно")
    else:
        logger.info("Все ресурсы найдены!")
    
    return len(missing_dirs) == 0


def create_missing_configs():
    """Создание недостающих конфигурационных файлов"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Базовый конфиг игры
    game_config = {
        "display": {
            "window_width": 1280,
            "window_height": 720,
            "fullscreen": False,
            "vsync": True,
            "render_fps": 60
        },
        "audio": {
            "master_volume": 0.8,
            "music_volume": 0.6,
            "effects_volume": 0.8
        },
        "gameplay": {
            "difficulty": "normal",
            "auto_save": True,
            "save_interval": 300
        }
    }
    
    game_config_path = config_dir / "game_settings.json"
    if not game_config_path.exists():
        import json
        with open(game_config_path, 'w', encoding='utf-8') as f:
            json.dump(game_config, f, indent=2, ensure_ascii=False)
        logger.info("Создан базовый конфиг игры")


def run_game():
    """Запуск игры"""
    try:
        logger.info("Запуск игры...")
        
        # Проверяем наличие главного файла
        main_file = Path("run_game.py")
        if not main_file.exists():
            logger.error("Файл run_game.py не найден!")
            return False
        
        # Запускаем игру
        result = subprocess.run([sys.executable, "run_game.py"], 
                               capture_output=False)
        
        if result.returncode == 0:
            logger.info("Игра завершена успешно")
            return True
        else:
            logger.error(f"Игра завершена с кодом ошибки: {result.returncode}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка запуска игры: {e}")
        return False


def main():
    """Главная функция"""
    print("🎮 Эволюционная Адаптация: Генетический Резонанс")
    print("=" * 60)
    print("Автоматическая установка и запуск игры")
    print("=" * 60)
    
    # Проверяем версию Python
    if not check_python_version():
        input("Нажмите Enter для выхода...")
        return 1
    
    # Устанавливаем зависимости
    print("\n📦 Установка зависимостей...")
    if not install_dependencies():
        input("Нажмите Enter для выхода...")
        return 1
    
    # Проверяем ресурсы
    print("\n🔍 Проверка игровых ресурсов...")
    check_assets()
    
    # Создаем недостающие конфиги
    print("\n⚙️ Создание конфигурационных файлов...")
    create_missing_configs()
    
    # Запускаем игру
    print("\n🚀 Запуск игры...")
    success = run_game()
    
    if success:
        print("\n✅ Игра завершена успешно!")
        return 0
    else:
        print("\n❌ Произошла ошибка при запуске игры")
        input("Нажмите Enter для выхода...")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Установка прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
