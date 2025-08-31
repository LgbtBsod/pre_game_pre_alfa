#!/usr/bin/env python3
"""AI-EVOLVE Enhanced Edition - Launcher
Основной файл запуска игры с новой модульной архитектурой на Panda3D"""

import logging
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

# Добавляем корневую директорию в путь
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))

def _configure_console_encoding():
    """Конфигурируем кодировку консоли для Windows/PowerShell"""
    try:
        if os.name == 'nt':
            os.system('chcp 65001 > nul')
    except Exception:
        pass

_configure_console_encoding()

def load_logging_config():
    """Загрузка конфигурации логирования"""
    try:
        # В будущем можно загружать из файла конфигурации
        return {
            "level": "INFO",
            "file_level": "DEBUG",
            "console_level": "INFO",
            "max_archive_files": 10,
            "cleanup_on_startup": True,
            "save_last_session": True,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "external_libraries": {
                "panda3d": "WARNING",
                "numpy": "WARNING",
                "PIL": "WARNING"
            }
        }
    except Exception as e:
        print(f"⚠️  Ошибка загрузки конфигурации логирования: {e}")
        # Возвращаем настройки по умолчанию
        return {
            "level": "INFO",
            "file_level": "DEBUG",
            "console_level": "INFO",
            "max_archive_files": 10,
            "cleanup_on_startup": True,
            "save_last_session": True,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "external_libraries": {
                "panda3d": "WARNING",
                "numpy": "WARNING",
                "PIL": "WARNING"
            }
        }

def cleanup_old_logs(log_dir: Path, archive_dir: Path, config: dict):
    """Очистка старых логов при каждом запуске игры"""
    try:
        # Получаем все файлы логов (исключаем папку archive)
        log_files = [f for f in log_dir.glob("*.log") if f.parent == log_dir]
        
        if not log_files:
            print("📁 Папка логов пуста")
            return
        
        # Если есть логи, сохраняем самый последний в архив
        if config.get("save_last_session", True) and log_files:
            # Сортируем по времени модификации (новые сначала)
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            latest_log = log_files[0]
            
            # Копируем последний лог в архив
            try:
                import shutil
                archive_name = f"last_session_{time.strftime('%Y%m%d_%H%M%S')}.log"
                archive_path = archive_dir / archive_name
                shutil.copy2(latest_log, archive_path)
                print(f"💾 Последний лог сохранен в архив: {archive_name}")
            except Exception as e:
                print(f"⚠️  Не удалось сохранить лог в архив: {e}")
        
        # Удаляем все старые логи
        for log_file in log_files:
            try:
                log_file.unlink()
                print(f"🗑️  Удален старый лог: {log_file.name}")
            except Exception as e:
                print(f"⚠️  Не удалось удалить лог {log_file.name}: {e}")
        
        print(f"🧹 Очищено {len(log_files)} старых логов")
        
        # Очищаем архив логов (оставляем только последние 10)
        cleanup_log_archive(archive_dir, config)
        
    except Exception as e:
        print(f"⚠️  Ошибка при очистке логов: {e}")

def cleanup_log_archive(archive_dir: Path, config: dict):
    """Очистка архива логов, оставляя только последние 10"""
    try:
        archive_files = list(archive_dir.glob("*.log"))
        if len(archive_files) > config.get("max_archive_files", 10):
            # Сортируем по времени модификации (старые сначала)
            archive_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Удаляем старые файлы
            files_to_remove = archive_files[:-config.get("max_archive_files", 10)]
            for file in files_to_remove:
                try:
                    file.unlink()
                    print(f"🗑️  Удален архивный лог: {file.name}")
                except Exception as e:
                    print(f"⚠️  Не удалось удалить архивный лог {file.name}: {e}")
    except Exception as e:
        print(f"⚠️  Ошибка при очистке архива логов: {e}")

def setup_logging():
    """Настройка системы логирования с очисткой старых логов"""
    log_dir = ROOT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Создаем папку для архива логов
    archive_dir = ROOT_DIR / "logs" / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    # Загружаем конфигурацию логирования
    logging_config = load_logging_config()
    
    # Очистка старых логов (если включено)
    if logging_config.get("cleanup_on_startup", True):
        cleanup_old_logs(log_dir, archive_dir, logging_config)
    
    # Форматтер для логов
    formatter = logging.Formatter(
        logging_config.get("format", '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        datefmt=logging_config.get("date_format", '%Y-%m-%d %H:%M:%S')
    )
    
    # Файловый обработчик
    current_log_file = log_dir / f"ai_evolve_{time.strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(
        current_log_file,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, logging_config.get("file_level", "DEBUG")))
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, logging_config.get("console_level", "INFO")))
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, logging_config.get("level", "DEBUG")))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Настройка уровней для внешних библиотек
    external_libs = logging_config.get("external_libraries", {})
    for lib_name, level in external_libs.items():
        try:
            logging.getLogger(lib_name).setLevel(getattr(logging, level))
        except Exception as e:
            print(f"⚠️  Не удалось установить уровень логирования для {lib_name}: {e}")
    
    # Сохраняем путь к текущему лог-файлу для возможного архивирования
    root_logger.current_log_file = current_log_file
    
    print(f"📝 Логирование настроено: {current_log_file.name}")
    print(f"📊 Уровень файла: {logging_config.get('file_level', 'DEBUG')}")
    print(f"📊 Уровень консоли: {logging_config.get('console_level', 'INFO')}")

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
            print(f"✅ {package} - установлен")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} - отсутствует")
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} - установлен")
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
        # Импортируем основные компоненты
        from src.core.state_manager import StateManager
        from src.systems.attributes.attribute_system import AttributeSystem
        from src.core.master_integrator import MasterIntegrator
        
        print("🔧 Инициализация основных систем...")
        
        # Создаем менеджер состояний
        state_manager = StateManager()
        print("✅ StateManager инициализирован")
        
        # Создаем систему атрибутов
        attribute_system = AttributeSystem()
        print("✅ AttributeSystem инициализирована")
        
        # Создаем главный интегратор
        master_integrator = MasterIntegrator()
        master_integrator.set_architecture_components(state_manager, attribute_system)
        print("✅ MasterIntegrator инициализирован")
        
        # Инициализируем все системы
        if not master_integrator.initialize():
            raise Exception("Ошибка инициализации MasterIntegrator")
        print("✅ Все системы инициализированы")
        
        # Запускаем все системы
        if not master_integrator.start():
            raise Exception("Ошибка запуска MasterIntegrator")
        print("✅ Все системы запущены")
        
        return master_integrator
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        logging.error(f"Ошибка инициализации: {e}")
        traceback.print_exc()
        return None

def cleanup_on_exit():
    """Очистка ресурсов при выходе из игры"""
    try:
        print("\n🧹 Очистка ресурсов...")
        
        # Получаем текущий лог-файл
        root_logger = logging.getLogger()
        if hasattr(root_logger, 'current_log_file') and root_logger.current_log_file:
            current_log = root_logger.current_log_file
            
            # Если лог-файл существует и не пустой, копируем его в архив
            if current_log.exists() and current_log.stat().st_size > 0:
                try:
                    import shutil
                    archive_dir = ROOT_DIR / "logs" / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    archive_name = f"session_end_{time.strftime('%Y%m%d_%H%M%S')}.log"
                    archive_path = archive_dir / archive_name
                    shutil.copy2(current_log, archive_path)
                    print(f"💾 Финальный лог сохранен в архив: {archive_name}")
                except Exception as e:
                    print(f"⚠️  Не удалось сохранить финальный лог: {e}")
        
        print("✅ Очистка завершена")
        
    except Exception as e:
        print(f"⚠️  Ошибка при очистке: {e}")

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
        
        # Создание директорий
        create_directories()
        
        # Инициализация игры
        game = initialize_game()
        if not game:
            return 1
        
        print("\n🎉 Игра успешно запущена!")
        print("📊 Статистика систем:")
        
        # Получаем информацию о системах
        system_info = game.get_system_info()
        for key, value in system_info.items():
            print(f"   {key}: {value}")
        
        print("\n🎮 Игра готова к использованию!")
        print("🚀 Запуск окна игры...")
        
        # Запускаем окно игры
        try:
            game.run()
        except Exception as e:
            logger.error(f"Ошибка запуска окна игры: {e}")
            print(f"⚠️  Ошибка запуска окна игры: {e}")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Игра остановлена пользователем")
        return 0
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Очистка при любом выходе
        cleanup_on_exit()

if __name__ == "__main__":
    try:
        exit_code = main()
        if exit_code == 0:
            print("\n✅ Игра завершена успешно")
        else:
            print(f"\n❌ Игра завершена с ошибкой (код: {exit_code})")
        sys.exit(exit_code)
    except SystemExit:
        cleanup_on_exit()
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        cleanup_on_exit()
        sys.exit(1)

