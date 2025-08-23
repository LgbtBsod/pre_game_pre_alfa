#!/usr/bin/env python3
"""
Скрипт сборки релизной версии игры
"Эволюционная Адаптация: Генетический Резонанс"
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_release_directory():
    """Создание директории релиза"""
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    logger.info("Создана директория релиза")
    return release_dir


def copy_game_files(release_dir: Path):
    """Копирование игровых файлов"""
    logger.info("Копирование игровых файлов...")
    
    # Основные файлы
    files_to_copy = [
        "main.py",
        "launcher.py", 
        "run_game.py",
        "requirements.txt",
        "README.md",
        "CHANGELOG.md"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, release_dir / file_name)
            logger.info(f"Скопирован {file_name}")
    
    # Директории
    dirs_to_copy = [
        "core",
        "ui", 
        "config",
        "graphics",
        "audio",
        "data"
    ]
    
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, release_dir / dir_name)
            logger.info(f"Скопирована директория {dir_name}")


def create_batch_files(release_dir: Path):
    """Создание batch файлов для Windows"""
    logger.info("Создание batch файлов...")
    
    # Запуск игры
    start_bat = release_dir / "start_game.bat"
    with open(start_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
title AI-EVOLVE: Эволюционная Адаптация
echo 🎮 Запуск игры AI-EVOLVE...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Ошибка запуска игры
    echo Попробуйте запустить install_dependencies.bat
    pause
)
""")
    
    # Установка зависимостей  
    install_bat = release_dir / "install_dependencies.bat"
    with open(install_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
title Установка зависимостей AI-EVOLVE
echo 📦 Установка зависимостей...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo ✅ Зависимости установлены успешно!
    echo Теперь можно запустить start_game.bat
) else (
    echo ❌ Ошибка установки зависимостей
    echo Проверьте подключение к интернету
)
pause
""")
    
    # Тестовый режим
    test_bat = release_dir / "test_systems.bat"
    with open(test_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
title Тестирование систем AI-EVOLVE
echo 🧪 Тестирование игровых систем...
python main.py test
pause
""")
    
    logger.info("Batch файлы созданы")


def create_shell_scripts(release_dir: Path):
    """Создание shell скриптов для Linux/macOS"""
    logger.info("Создание shell скриптов...")
    
    # Запуск игры
    start_sh = release_dir / "start_game.sh"
    with open(start_sh, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash
echo "🎮 Запуск игры AI-EVOLVE..."
python3 main.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Ошибка запуска игры"
    echo "Попробуйте запустить ./install_dependencies.sh"
    read -p "Нажмите Enter для выхода..."
fi
""")
    start_sh.chmod(0o755)
    
    # Установка зависимостей
    install_sh = release_dir / "install_dependencies.sh"  
    with open(install_sh, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash
echo "📦 Установка зависимостей..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Зависимости установлены успешно!"
    echo "Теперь можно запустить ./start_game.sh"
else
    echo "❌ Ошибка установки зависимостей"
    echo "Проверьте подключение к интернету"
fi
read -p "Нажмите Enter для выхода..."
""")
    install_sh.chmod(0o755)
    
    logger.info("Shell скрипты созданы")


def create_documentation(release_dir: Path):
    """Создание дополнительной документации"""
    logger.info("Создание документации...")
    
    # Быстрый старт
    quick_start = release_dir / "QUICK_START.md"
    with open(quick_start, 'w', encoding='utf-8') as f:
        f.write("""# 🚀 Быстрый старт

## Windows
1. Запустите `install_dependencies.bat`
2. Запустите `start_game.bat`

## Linux/macOS  
1. Запустите `./install_dependencies.sh`
2. Запустите `./start_game.sh`

## Ручной запуск
```bash
pip install -r requirements.txt
python main.py
```

## Режимы запуска
- `python main.py` - Графический интерфейс
- `python main.py test` - Тестирование систем
- `python main.py demo` - Демонстрация
- `python main.py console` - Консольный режим

## Устранение проблем
- Убедитесь что установлен Python 3.8+
- Проверьте подключение к интернету
- Запустите `python main.py test` для диагностики
""")
    
    # Системные требования
    requirements = release_dir / "SYSTEM_REQUIREMENTS.md"
    with open(requirements, 'w', encoding='utf-8') as f:
        f.write("""# 💻 Системные требования

## Минимальные требования
- **ОС**: Windows 10, macOS 10.14, Ubuntu 18.04
- **Python**: 3.8 или выше
- **ОЗУ**: 2 ГБ
- **Место на диске**: 500 МБ
- **Видеокарта**: Поддержка OpenGL 2.1

## Рекомендуемые требования  
- **ОС**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.10 или выше
- **ОЗУ**: 4 ГБ
- **Место на диске**: 1 ГБ
- **Видеокарта**: Поддержка OpenGL 3.0+

## Зависимости
Автоматически устанавливаются из requirements.txt:
- pygame >= 2.5.0
- numpy >= 1.24.0
- Pillow >= 10.0.0
- psutil >= 5.9.0

## Проверка системы
Запустите `python main.py test` для проверки совместимости.
""")
    
    logger.info("Документация создана")


def create_archive(release_dir: Path):
    """Создание архива релиза"""
    logger.info("Создание архива...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"AI-EVOLVE_v1.0.0_{timestamp}.zip"
    
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(release_dir.parent)
                zipf.write(file_path, arc_name)
    
    logger.info(f"Создан архив: {archive_name}")
    return archive_name


def main():
    """Главная функция сборки"""
    print("🏗️ Сборка релизной версии AI-EVOLVE")
    print("=" * 50)
    
    try:
        # Создаем директорию релиза
        release_dir = create_release_directory()
        
        # Копируем файлы
        copy_game_files(release_dir)
        
        # Создаем скрипты запуска
        create_batch_files(release_dir)
        create_shell_scripts(release_dir)
        
        # Создаем документацию
        create_documentation(release_dir)
        
        # Создаем архив
        archive_name = create_archive(release_dir)
        
        print("\n✅ Релиз собран успешно!")
        print(f"📁 Директория: {release_dir}")
        print(f"📦 Архив: {archive_name}")
        print("\n🎯 Готово к распространению!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка сборки: {e}")
        print(f"\n❌ Ошибка сборки: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
