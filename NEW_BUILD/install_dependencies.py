#!/usr/bin/env python3
"""
Install Dependencies Script
Скрипт для установки всех необходимых зависимостей
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package_name: str, pip_name: str = None) -> bool:
    """Установка пакета"""
    if pip_name is None:
        pip_name = package_name
    
    print(f"📦 Установка {package_name}...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pip_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ {package_name} успешно установлен")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Ошибка установки {package_name}")
        return False

def check_package(package_name: str) -> bool:
    """Проверка наличия пакета"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    """Главная функция"""
    print("🚀 Установка зависимостей для AI-EVOLVE Enhanced Edition")
    print("=" * 60)
    
    # Список необходимых пакетов
    required_packages = [
        ("pygame", "pygame>=2.5.0"),
        ("numpy", "numpy>=1.24.0"),
        ("psutil", "psutil>=5.9.0")
    ]
    
    # Список опциональных пакетов
    optional_packages = [
        ("PIL", "pillow>=10.0.0"),
        ("tiledtmxloader", "tiledtmxloader>=3.0.0")
    ]
    
    # Проверяем и устанавливаем необходимые пакеты
    print("\n🔍 Проверка необходимых пакетов...")
    missing_required = []
    
    for package_name, pip_name in required_packages:
        if check_package(package_name):
            print(f"✅ {package_name} уже установлен")
        else:
            missing_required.append((package_name, pip_name))
    
    # Устанавливаем недостающие необходимые пакеты
    if missing_required:
        print(f"\n📥 Установка {len(missing_required)} недостающих пакетов...")
        
        for package_name, pip_name in missing_required:
            if not install_package(package_name, pip_name):
                print(f"❌ Критическая ошибка: не удалось установить {package_name}")
                print("Игра не может работать без этого пакета!")
                return 1
    else:
        print("✅ Все необходимые пакеты уже установлены")
    
    # Проверяем и устанавливаем опциональные пакеты
    print("\n🔍 Проверка опциональных пакетов...")
    missing_optional = []
    
    for package_name, pip_name in optional_packages:
        if check_package(package_name):
            print(f"✅ {package_name} уже установлен")
        else:
            missing_optional.append((package_name, pip_name))
    
    # Устанавливаем недостающие опциональные пакеты
    if missing_optional:
        print(f"\n📥 Установка {len(missing_optional)} опциональных пакетов...")
        
        for package_name, pip_name in missing_optional:
            if install_package(package_name, pip_name):
                print(f"✅ {package_name} установлен (опционально)")
            else:
                print(f"⚠️  {package_name} не установлен (не критично)")
    else:
        print("✅ Все опциональные пакеты уже установлены")
    
    # Проверяем финальное состояние
    print("\n🔍 Финальная проверка...")
    all_installed = True
    
    for package_name, _ in required_packages:
        if not check_package(package_name):
            print(f"❌ {package_name} не найден после установки")
            all_installed = False
    
    if all_installed:
        print("\n🎉 Все зависимости успешно установлены!")
        print("Теперь вы можете запустить игру командой: python launcher.py")
        return 0
    else:
        print("\n❌ Не все зависимости установлены корректно")
        print("Попробуйте установить их вручную:")
        print("pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
