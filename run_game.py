#!/usr/bin/env python3
"""
Главный файл запуска игры "Эволюционная Адаптация: Генетический Резонанс"
Запускает графический интерфейс или консольный режим в зависимости от доступности Pygame
"""

import sys
import os
import logging
from pathlib import Path

# Добавление корневой директории в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Настройка логирования (форс UTF-8 на Windows)"""
    # Переконфигурируем stdout/stderr в UTF-8 для русских сообщений
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/game.log', encoding='utf-8')
        ]
    )

def check_dependencies():
    """Проверка зависимостей"""
    missing_deps = []
    
    try:
        import pygame
        print("✓ Pygame доступен")
    except ImportError:
        missing_deps.append("pygame")
        print("✗ Pygame не найден")
    
    try:
        import numpy
        print("✓ NumPy доступен")
    except ImportError:
        missing_deps.append("numpy")
        print("✗ NumPy не найден")
    
    if missing_deps:
        print(f"\nДля установки зависимостей выполните:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    return True

def create_directories():
    """Создание необходимых директорий"""
    directories = ["logs", "save", "data", "config"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Директория {directory} создана/проверена")

def run_graphical_interface():
    """Запуск графического интерфейса"""
    try:
        from ui.game_interface import main as run_gui
        print("Запуск графического интерфейса...")
        run_gui()
    except Exception as e:
        print(f"✗ Ошибка запуска графического интерфейса: {e}")
        logging.error(f"Ошибка запуска графического интерфейса: {e}")
        return False
    return True

def run_console_mode():
    """Запуск консольного режима"""
    try:
        from core.game_loop import GameLoop
        print("Запуск консольного режима...")
        
        game_loop = GameLoop(use_pygame=False)
        if game_loop.start_new_game():
            print("Игра запущена. Нажмите Ctrl+C для выхода")
            game_loop.run()
        else:
            print("✗ Не удалось запустить игру")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка запуска консольного режима: {e}")
        logging.error(f"Ошибка запуска консольного режима: {e}")
        return False
    return True

def run_test_mode():
    """Запуск тестового режима"""
    try:
        from main_game import test_systems
        print("Запуск тестирования систем...")
        return test_systems()
    except Exception as e:
        print(f"✗ Ошибка тестирования: {e}")
        logging.error(f"Ошибка тестирования: {e}")
        return False

def run_demo_mode():
    """Запуск демо-режима"""
    try:
        from main_game import run_demo_mode as run_demo
        print("Запуск демо-режима...")
        run_demo()
        return True
    except Exception as e:
        print(f"✗ Ошибка демо-режима: {e}")
        logging.error(f"Ошибка демо-режима: {e}")
        return False

def show_help():
    """Показать справку"""
    print("""
ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ: ГЕНЕТИЧЕСКИЙ РЕЗОНАНС
================================================

Использование:
  python run_game.py [опция]

Опции:
  --gui, -g          Запуск графического интерфейса (по умолчанию)
  --console, -c      Запуск консольного режима
  --test, -t         Тестирование всех систем
  --demo, -d         Демо-режим (30 секунд)
  --help, -h         Показать эту справку

Примеры:
  python run_game.py              # Графический интерфейс
  python run_game.py --console    # Консольный режим
  python run_game.py --test       # Тестирование
  python run_game.py --demo       # Демо-режим
""")

def main():
    """Главная функция"""
    # Парсинг аргументов командной строки
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Обработка флага помощи
    if any(arg in ['--help', '-h'] for arg in args):
        show_help()
        return
    
    # Настройка логирования
    setup_logging()
    
    # Создание директорий
    create_directories()
    
    # Проверка зависимостей
    if not check_dependencies():
        print("\n⚠ Некоторые зависимости отсутствуют. Игра может работать некорректно.")
    
    # Вывод заголовка
    print("\n" + "=" * 60)
    print("  ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ: ГЕНЕТИЧЕСКИЙ РЕЗОНАНС")
    print("=" * 60)
    print("  Версия: 1.0.0")
    print("  Автор: AI Assistant")
    print("  Описание: Инновационная игра с эволюционными циклами")
    print("=" * 60)
    
    try:
        # Определение режима запуска
        if any(arg in ['--test', '-t'] for arg in args):
            # Тестовый режим
            success = run_test_mode()
            if success:
                print("\n✓ Все системы работают корректно!")
            else:
                print("\n✗ Обнаружены проблемы в системах!")
                sys.exit(1)
                
        elif any(arg in ['--demo', '-d'] for arg in args):
            # Демо-режим
            run_demo_mode()
            
        elif any(arg in ['--console', '-c'] for arg in args):
            # Консольный режим
            run_console_mode()
            
        else:
            # Графический интерфейс (по умолчанию)
            try:
                import pygame
                run_graphical_interface()
            except ImportError:
                print("⚠ Pygame недоступен, переключение на консольный режим")
                run_console_mode()
                
    except KeyboardInterrupt:
        print("\n\nИгра прервана пользователем")
        logging.info("Игра прервана пользователем")
        
    except Exception as e:
        print(f"\n\n✗ Критическая ошибка: {e}")
        logging.critical(f"Критическая ошибка: {e}")
        sys.exit(1)
        
    finally:
        print("\nСпасибо за игру!")
        print("=" * 60)

if __name__ == "__main__":
    main()
