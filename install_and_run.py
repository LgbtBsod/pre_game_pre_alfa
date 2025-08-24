#!/usr/bin/env python3
"""
AI-EVOLVE: Enhanced Edition - Автоматическая установка и запуск
Устанавливает все необходимые зависимости и запускает игру
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Печать баннера игры"""
    banner = """
🎮 AI-EVOLVE: Enhanced Edition
Эволюционная Адаптация: Генетический Резонанс
==================================================
    """
    print(banner)

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print(f"❌ Требуется Python 3.8+. Текущая версия: {sys.version_info}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_package(package_name, description=""):
    """Установка пакета"""
    try:
        print(f"📦 Установка {package_name}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package_name} установлен успешно")
            return True
        else:
            print(f"❌ Ошибка установки {package_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ошибка установки {package_name}: {e}")
        return False

def install_dependencies():
    """Установка всех зависимостей"""
    print("🔧 Установка зависимостей...")
    
    # Основные зависимости
    core_packages = [
        ("pygame>=2.5.0", "pygame"),
        ("numpy>=1.24.0", "numpy")
    ]
    
    # Опциональные зависимости
    optional_packages = [
        ("psutil>=5.9.0", "psutil"),
        ("Pillow>=10.0.0", "Pillow"),
        ("colorama>=0.4.6", "colorama"),
        ("tqdm>=4.65.0", "tqdm")
    ]
    
    # Устанавливаем основные зависимости
    for package, name in core_packages:
        if not install_package(package, name):
            print(f"❌ Критическая ошибка: не удалось установить {name}")
            return False
    
    # Устанавливаем опциональные зависимости
    for package, name in optional_packages:
        install_package(package, name)
    
    print("✅ Все зависимости установлены")
    return True

def create_directories():
    """Создание необходимых директорий"""
    print("📁 Создание директорий...")
    
    directories = [
        'logs', 'save', 'screenshots', 'data', 
        'data/maps', 'data/tilesets'
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Директория {directory} создана/проверена")
        except Exception as e:
            print(f"⚠️ Не удалось создать директорию {directory}: {e}")

def run_game():
    """Запуск игры"""
    print("🚀 Запуск игры...")
    
    try:
        # Импортируем и запускаем игру
        from main import main
        return main()
    except Exception as e:
        print(f"💥 Критическая ошибка запуска игры: {e}")
        return 1

def main():
    """Главная функция"""
    print_banner()
    
    # Проверяем версию Python
    if not check_python_version():
        return 1
    
    # Устанавливаем зависимости
    if not install_dependencies():
        return 1
    
    # Создаем директории
    create_directories()
    
    # Запускаем игру
    return run_game()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Установка прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        sys.exit(1)
