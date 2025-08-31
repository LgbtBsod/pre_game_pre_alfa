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

def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 ПРОВЕРКА ЗАВИСИМОСТЕЙ")
    print("=" * 50)
    
    # Обязательные пакеты
    required_packages = [
        "panda3d",
        "numpy"
    ]
    
    # Опциональные пакеты
    optional_packages = [
        "PIL",
        "cv2",
        "matplotlib"
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            if package == "panda3d":
                # Специальная проверка Panda3D
                import panda3d
                print(f"✅ {package} - установлен (версия: {panda3d.__version__})")
                
                # Проверяем возможность создания окна с разными импортами
                try:
                    print("🔍 Тестирование создания окна Panda3D...")
                    
                    # Пробуем разные способы импорта ShowBase
                    try:
                        from panda3d.core import ShowBase, WindowProperties
                        print("✅ Импорт из panda3d.core успешен")
                    except ImportError:
                        try:
                            from direct.showbase.ShowBase import ShowBase
                            print("✅ Импорт из direct.showbase.ShowBase успешен")
                        except ImportError:
                            try:
                                from direct.showbase import ShowBase
                                print("✅ Импорт из direct.showbase успешен")
                            except ImportError:
                                raise ImportError("Не удалось импортировать ShowBase ни одним способом")
                    
                    # Тестируем создание окна
                    test_base = ShowBase()
                    test_base.destroy()
                    print("✅ Panda3D окно создается успешно")
                    
                except Exception as window_e:
                    print(f"⚠️  Panda3D окно не создается: {window_e}")
                    # Не прерываем запуск, так как Panda3D может работать в headless режиме
                    
            else:
                __import__(package)
                print(f"✅ {package} - установлен")
        except ImportError as e:
            missing_required.append(package)
            print(f"❌ {package} - отсутствует: {e}")
        except Exception as e:
            missing_required.append(package)
            print(f"❌ {package} - ошибка: {e}")
    
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
    
    print("\n✅ Все необходимые зависимости установлены")
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
        print("\n🔧 ДЕТАЛЬНАЯ ИНИЦИАЛИЗАЦИЯ СИСТЕМ")
        print("=" * 50)
        
        # Импортируем основные компоненты
        print("📦 Импорт основных компонентов...")
        try:
            from src.core.state_manager import StateManager
            print("✅ StateManager импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта StateManager: {e}")
            raise
        
        try:
            from src.systems.attributes.attribute_system import AttributeSystem
            print("✅ AttributeSystem импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта AttributeSystem: {e}")
            raise
        
        try:
            from src.core.master_integrator import MasterIntegrator
            print("✅ MasterIntegrator импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта MasterIntegrator: {e}")
            raise
        
        print("\n🏗️  Создание экземпляров систем...")
        
        # Создаем менеджер состояний
        try:
            state_manager = StateManager()
            print("✅ StateManager создан")
        except Exception as e:
            print(f"❌ Ошибка создания StateManager: {e}")
            raise
        
        # Создаем систему атрибутов
        try:
            attribute_system = AttributeSystem()
            print("✅ AttributeSystem создана")
        except Exception as e:
            print(f"❌ Ошибка создания AttributeSystem: {e}")
            raise
        
        # Создаем главный интегратор
        try:
            master_integrator = MasterIntegrator()
            print("✅ MasterIntegrator создан")
        except Exception as e:
            print(f"❌ Ошибка создания MasterIntegrator: {e}")
            raise
        
        print("\n🔗 Настройка архитектуры...")
        try:
            master_integrator.set_architecture_components(state_manager, attribute_system)
            print("✅ Архитектурные компоненты настроены")
        except Exception as e:
            print(f"❌ Ошибка настройки архитектуры: {e}")
            raise
        
        print("\n🚀 Инициализация всех систем...")
        try:
            if not master_integrator.initialize():
                raise Exception("Ошибка инициализации MasterIntegrator")
            print("✅ Все системы инициализированы")
        except Exception as e:
            print(f"❌ Ошибка инициализации систем: {e}")
            raise
        
        print("\n▶️  Запуск всех систем...")
        try:
            if not master_integrator.start():
                raise Exception("Ошибка запуска MasterIntegrator")
            print("✅ Все системы запущены")
        except Exception as e:
            print(f"❌ Ошибка запуска систем: {e}")
            raise
        
        print("\n📊 Проверка состояния систем...")
        try:
            system_info = master_integrator.get_system_info()
            print(f"✅ Получена информация о {len(system_info)} системах")
            for key, value in system_info.items():
                print(f"   📋 {key}: {value}")
        except Exception as e:
            print(f"⚠️  Не удалось получить информацию о системах: {e}")
        
        return master_integrator
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА ИНИЦИАЛИЗАЦИИ: {e}")
        print("🔍 Детали ошибки:")
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
        print("🚀 ЗАПУСК ОКНА ИГРЫ")
        print("=" * 50)
        
        # Дополнительная диагностика состояния игры
        print("🔍 ДИАГНОСТИКА СОСТОЯНИЯ ИГРЫ:")
        try:
            if hasattr(game, 'systems'):
                print(f"📋 Количество систем: {len(game.systems)}")
                print(f"📋 Доступные системы: {list(game.systems.keys())}")
                
                # Проверяем ключевые системы
                key_systems = ['rendering_system', 'attribute_system', 'content_system']
                for system_name in key_systems:
                    if system_name in game.systems:
                        system = game.systems[system_name]
                        print(f"✅ {system_name}: {type(system).__name__}")
                        
                        # Специальная проверка системы рендеринга
                        if system_name == 'rendering_system':
                            if hasattr(system, 'showbase'):
                                print(f"   🎬 ShowBase: {type(system.showbase).__name__}")
                            else:
                                print(f"   ⚠️  ShowBase: отсутствует")
                            
                            if hasattr(system, 'run'):
                                print(f"   ▶️  Метод run: доступен")
                            else:
                                print(f"   ❌ Метод run: отсутствует")
                    else:
                        print(f"❌ {system_name}: отсутствует")
            else:
                print("❌ Игра не имеет атрибута 'systems'")
                
            if hasattr(game, 'state'):
                print(f"📊 Состояние игры: {game.state}")
            else:
                print("⚠️  Игра не имеет атрибута 'state'")
                
        except Exception as diag_e:
            print(f"⚠️  Ошибка диагностики состояния: {diag_e}")
        
        print("\n🎬 Запуск главного цикла игры...")
        
        # Детальная диагностика состояния систем
        print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА СИСТЕМ:")
        try:
            if hasattr(game, 'systems'):
                for system_name, system in game.systems.items():
                    print(f"📋 {system_name}:")
                    print(f"   🏷️  Тип: {type(system).__name__}")
                    if hasattr(system, 'state'):
                        print(f"   📊 Состояние: {system.state}")
                    if hasattr(system, 'component_id'):
                        print(f"   🆔 ID: {system.component_id}")
                    if hasattr(system, 'priority'):
                        print(f"   ⚡ Приоритет: {system.priority}")
                    
                    # Специальная проверка для системы рендеринга
                    if system_name == 'rendering_system':
                        if hasattr(system, 'showbase'):
                            print(f"   🎬 ShowBase: {type(system.showbase).__name__}")
                            if hasattr(system.showbase, 'win'):
                                print(f"   🪟 Окно: {type(system.showbase.win).__name__}")
                            else:
                                print(f"   ⚠️  Окно: отсутствует")
                        else:
                            print(f"   ⚠️  ShowBase: отсутствует")
                        
                        if hasattr(system, 'run'):
                            print(f"   ▶️  Метод run: доступен")
                        else:
                            print(f"   ❌ Метод run: отсутствует")
                    
                    print()  # Пустая строка для разделения
            else:
                print("❌ Игра не имеет атрибута 'systems'")
        except Exception as diag_e:
            print(f"⚠️  Ошибка детальной диагностики: {diag_e}")
        
        # Запускаем систему рендеринга напрямую
        try:
            print(f"\n🔍 КОМПЛЕКСНАЯ ДИАГНОСТИКА СИСТЕМЫ РЕНДЕРИНГА:")
            print(f"   =================================================")
            
            if hasattr(game, 'systems') and 'rendering_system' in game.systems:
                rendering_system = game.systems['rendering_system']
                print(f"✅ Система рендеринга найдена: {type(rendering_system).__name__}")
                
                # 1. ПРОВЕРКА ВСЕХ АТРИБУТОВ RenderingSystem
                print(f"\n📋 1. ПРОВЕРКА АТРИБУТОВ RenderingSystem:")
                all_attrs = dir(rendering_system)
                rendering_attrs = [attr for attr in all_attrs if not attr.startswith('_')]
                
                for attr in rendering_attrs:
                    try:
                        value = getattr(rendering_system, attr)
                        if callable(value):
                            print(f"   🔧 {attr}: {type(value).__name__} (callable)")
                        else:
                            print(f"   📊 {attr}: {type(value).__name__} = {value}")
                    except Exception as e:
                        print(f"   ❌ {attr}: ошибка доступа - {e}")
                
                # 2. ДЕТАЛЬНАЯ ПРОВЕРКА ShowBase
                print(f"\n🎬 2. ДЕТАЛЬНАЯ ПРОВЕРКА ShowBase:")
                if hasattr(rendering_system, 'showbase'):
                    showbase = rendering_system.showbase
                    print(f"   🏷️  Тип: {type(showbase).__name__}")
                    
                    # Проверяем все атрибуты ShowBase
                    showbase_attrs = ['render', 'render2d', 'camera', 'win', 'taskMgr', 'mouseWatcherNode', 'dataRoot']
                    for attr in showbase_attrs:
                        if hasattr(showbase, attr):
                            value = getattr(showbase, attr)
                            print(f"   ✅ {attr}: {type(value).__name__}")
                        else:
                            print(f"   ❌ {attr}: отсутствует")
                    
                    # 3. ПРОВЕРКА ОКНА
                    print(f"\n🪟 3. ПРОВЕРКА ОКНА:")
                    if hasattr(showbase, 'win'):
                        win = showbase.win
                        print(f"   🏷️  Тип окна: {type(win).__name__}")
                        
                        # Проверяем все методы окна
                        window_methods = [
                            'isValid', 'getXSize', 'getYSize', 'getState', 'getTitle',
                            'getOrigin', 'getSize', 'getProperties', 'getPipe'
                        ]
                        
                        for method in window_methods:
                            if hasattr(win, method):
                                try:
                                    if method == 'isValid':
                                        result = win.isValid()
                                        print(f"   ✅ {method}: {result}")
                                    elif method == 'getXSize':
                                        result = win.getXSize()
                                        print(f"   📏 {method}: {result}")
                                    elif method == 'getYSize':
                                        result = win.getYSize()
                                        print(f"   📏 {method}: {result}")
                                    elif method == 'getState':
                                        result = win.getState()
                                        print(f"   📊 {method}: {result}")
                                    elif method == 'getTitle':
                                        result = win.getTitle()
                                        print(f"   🏷️  {method}: {result}")
                                    elif method == 'getOrigin':
                                        result = win.getOrigin()
                                        print(f"   📍 {method}: {result}")
                                    elif method == 'getSize':
                                        result = win.getSize()
                                        print(f"   📐 {method}: {result}")
                                    else:
                                        result = getattr(win, method)()
                                        print(f"   ✅ {method}: {result}")
                                except Exception as e:
                                    print(f"   ⚠️  {method}: ошибка вызова - {e}")
                            else:
                                print(f"   ❌ {method}: отсутствует")
                        
                        # Проверяем свойства окна
                        print(f"\n   🔧 Проверка свойств окна:")
                        if hasattr(win, 'getProperties'):
                            try:
                                props = win.getProperties()
                                print(f"      📋 Свойства окна: {props}")
                            except Exception as e:
                                print(f"      ⚠️  Не удалось получить свойства: {e}")
                        
                        # Проверяем pipe
                        if hasattr(win, 'getPipe'):
                            try:
                                pipe = win.getPipe()
                                print(f"      🔌 Pipe: {type(pipe).__name__}")
                            except Exception as e:
                                print(f"      ⚠️  Не удалось получить pipe: {e}")
                    else:
                        print(f"   ❌ Окно не найдено в ShowBase")
                else:
                    print(f"   ❌ ShowBase не найден в системе рендеринга")
                
                # 4. ПРОВЕРКА МЕТОДА RUN
                print(f"\n▶️  4. ПРОВЕРКА МЕТОДА RUN:")
                if hasattr(rendering_system, 'run'):
                    run_method = rendering_system.run
                    print(f"   ✅ Метод 'run' найден: {type(run_method).__name__}")
                    print(f"   🔧 Вызываемый: {callable(run_method)}")
                    
                    # Проверяем сигнатуру метода
                    import inspect
                    try:
                        sig = inspect.signature(run_method)
                        print(f"   📝 Сигнатура: {sig}")
                    except Exception as e:
                        print(f"   ⚠️  Не удалось получить сигнатуру: {e}")
                    
                    # Проверяем docstring
                    if hasattr(run_method, '__doc__') and run_method.__doc__:
                        print(f"   📖 Docstring: {run_method.__doc__.strip()}")
                    else:
                        print(f"   ⚠️  Docstring отсутствует")
                else:
                    print(f"   ❌ Метод 'run' не найден в системе рендеринга")
                    raise Exception("Система рендеринга не имеет метода 'run'")
                
                # 5. ПРОВЕРКА СОСТОЯНИЯ СИСТЕМЫ
                print(f"\n📊 5. ПРОВЕРКА СОСТОЯНИЯ СИСТЕМЫ:")
                if hasattr(rendering_system, 'state'):
                    print(f"   📊 Состояние: {rendering_system.state}")
                    print(f"   🔍 Значение: {rendering_system.state.value}")
                else:
                    print(f"   ⚠️  Состояние: не определено")
                
                # 6. ФИНАЛЬНАЯ ПРОВЕРКА ПЕРЕД ЗАПУСКОМ
                print(f"\n🚀 6. ФИНАЛЬНАЯ ПРОВЕРКА ПЕРЕД ЗАПУСКОМ:")
                print(f"   🔍 Проверяем все критические компоненты...")
                
                # Проверяем, что все критически важные компоненты присутствуют
                critical_components = ['showbase']
                missing_components = []
                for component in critical_components:
                    if not hasattr(rendering_system, component):
                        missing_components.append(component)
                
                if missing_components:
                    raise Exception(f"Отсутствуют критические компоненты: {missing_components}")
                
                # Дополнительная проверка showbase компонентов
                showbase_critical = ['render', 'render2d', 'win']
                missing_showbase = []
                for component in showbase_critical:
                    if not hasattr(rendering_system.showbase, component):
                        missing_showbase.append(component)
                
                if missing_showbase:
                    raise Exception(f"Отсутствуют критические компоненты ShowBase: {missing_showbase}")
                
                print(f"   ✅ Все критические компоненты присутствуют")
                print(f"   ✅ Все компоненты ShowBase присутствуют")
                print(f"   🚀 Запуск окна игры...")
                
                # 7. ЗАПУСК С МОНИТОРИНГОМ
                print(f"\n🎬 7. ЗАПУСК С МОНИТОРИНГОМ:")
                print(f"   🚀 Вызываем rendering_system.run()...")
                
                try:
                    print(f"   🔍 Состояние перед вызовом run():")
                    print(f"      📊 Система: {rendering_system.state}")
                    print(f"      🎬 ShowBase: {type(rendering_system.showbase).__name__}")
                    print(f"      🪟 Окно: {type(rendering_system.showbase.win).__name__}")
                    
                    # Проверяем, что окно действительно готово
                    win = rendering_system.showbase.win
                    if hasattr(win, 'isValid'):
                        is_valid = win.isValid()
                        print(f"      ✅ Окно валидно: {is_valid}")
                    else:
                        print(f"      ⚠️  Метод isValid отсутствует")
                    
                    if hasattr(win, 'getXSize') and hasattr(win, 'getYSize'):
                        width = win.getXSize()
                        height = win.getYSize()
                        print(f"      📏 Размеры: {width}x{height}")
                    else:
                        print(f"      ⚠️  Методы получения размеров отсутствуют")
                    
                    print(f"   🚀 ВЫЗЫВАЕМ run()...")
                    
                    # ПРОБУЕМ РАЗНЫЕ СПОСОБЫ ЗАПУСКА
                    print(f"\n   🔄 ПРОБУЕМ РАЗНЫЕ СПОСОБЫ ЗАПУСКА:")
                    
                    # Способ 1: Прямой вызов
                    print(f"   📋 Способ 1: Прямой вызов rendering_system.run()")
                    try:
                        # Запускаем в отдельном потоке с таймаутом
                        import threading
                        import time
                        
                        # Создаем флаг для отслеживания запуска
                        run_started = threading.Event()
                        run_completed = threading.Event()
                        run_error = None
                        
                        def run_with_monitoring():
                            nonlocal run_error
                            try:
                                run_started.set()
                                print(f"      📝 run() начал выполнение")
                                result = rendering_system.run()
                                print(f"      📊 run() завершился с результатом: {result}")
                                run_completed.set()
                            except Exception as e:
                                run_error = e
                                print(f"      ❌ run() завершился с ошибкой: {e}")
                                import traceback
                                print(f"      🔍 Детали ошибки:")
                                traceback.print_exc()
                                run_completed.set()
                        
                        # Запускаем в отдельном потоке
                        run_thread = threading.Thread(target=run_with_monitoring, daemon=True)
                        run_thread.start()
                        
                        # Ждем начала выполнения
                        if run_started.wait(timeout=5.0):
                            print(f"      ✅ run() начал выполняться")
                            
                            # Ждем завершения с таймаутом
                            if run_completed.wait(timeout=15.0):  # Увеличиваем таймаут
                                if run_error:
                                    print(f"      ❌ run() завершился с ошибкой: {run_error}")
                                    raise Exception(f"Ошибка при запуске окна: {run_error}")
                                else:
                                    print(f"      ✅ run() завершился успешно")
                            else:
                                print(f"      ⚠️  run() не завершился за 15 секунд")
                                print(f"      🔍 Проверяем состояние окна...")
                                
                                # Проверяем состояние окна после запуска
                                if hasattr(rendering_system, 'showbase') and hasattr(rendering_system.showbase, 'win'):
                                    win = rendering_system.showbase.win
                                    if hasattr(win, 'isValid'):
                                        try:
                                            is_valid = win.isValid()
                                            print(f"      📊 Окно валидно после запуска: {is_valid}")
                                        except Exception as e:
                                            print(f"      ⚠️  Не удалось проверить валидность: {e}")
                                    
                                    if hasattr(win, 'getXSize') and hasattr(win, 'getYSize'):
                                        try:
                                            width = win.getXSize()
                                            height = win.getYSize()
                                            print(f"      📏 Размеры после запуска: {width}x{height}")
                                        except Exception as e:
                                            print(f"      ⚠️  Не удалось получить размеры: {e}")
                                else:
                                    print(f"      ⚠️  Не удалось проверить окно после запуска")
                        else:
                            print(f"      ❌ run() не начал выполняться за 5 секунд")
                            raise Exception("run() не начал выполняться за 5 секунд")
                        
                    except Exception as e:
                        print(f"      ❌ Способ 1 не сработал: {e}")
                        print(f"      🔄 Пробуем способ 2...")
                        
                        # Способ 2: Попытка через ShowBase напрямую
                        print(f"   📋 Способ 2: Прямой вызов showbase.run()")
                        try:
                            if hasattr(rendering_system, 'showbase'):
                                showbase = rendering_system.showbase
                                print(f"      🎬 Вызываем showbase.run() напрямую...")
                                
                                # Запускаем в отдельном потоке
                                def run_showbase_directly():
                                    try:
                                        print(f"         📝 showbase.run() начал выполнение")
                                        showbase.run()
                                        print(f"         ✅ showbase.run() завершился")
                                    except Exception as e:
                                        print(f"         ❌ showbase.run() завершился с ошибкой: {e}")
                                        import traceback
                                        traceback.print_exc()
                                
                                showbase_thread = threading.Thread(target=run_showbase_directly, daemon=True)
                                showbase_thread.start()
                                
                                # Ждем немного
                                time.sleep(3)
                                print(f"         ⏰ showbase.run() запущен в фоне")
                                
                            else:
                                raise Exception("ShowBase не найден")
                                
                        except Exception as e2:
                            print(f"      ❌ Способ 2 не сработал: {e2}")
                            print(f"      🔄 Пробуем способ 3...")
                            
                            # Способ 3: Проверяем, может окно уже создано
                            print(f"   📋 Способ 3: Проверка существующего окна")
                            try:
                                if hasattr(rendering_system, 'showbase') and hasattr(rendering_system.showbase, 'win'):
                                    win = rendering_system.showbase.win
                                    print(f"      🪟 Проверяем существующее окно...")
                                    
                                    if hasattr(win, 'isValid'):
                                        is_valid = win.isValid()
                                        print(f"         📊 Окно валидно: {is_valid}")
                                    
                                    if hasattr(win, 'getXSize') and hasattr(win, 'getYSize'):
                                        width = win.getXSize()
                                        height = win.getYSize()
                                        print(f"         📏 Размеры: {width}x{height}")
                                    
                                    # Пытаемся сделать окно видимым
                                    if hasattr(win, 'setForeground'):
                                        try:
                                            win.setForeground()
                                            print(f"         ✅ Окно выведено на передний план")
                                        except Exception as e:
                                            print(f"         ⚠️  Не удалось вывести окно на передний план: {e}")
                                    
                                    print(f"      🎮 Окно должно быть видимым!")
                                    
                                else:
                                    raise Exception("Окно не найдено")
                                    
                            except Exception as e3:
                                print(f"      ❌ Способ 3 не сработал: {e3}")
                                raise Exception(f"Все способы запуска не сработали. Последняя ошибка: {e3}")
                    
                except Exception as run_error:
                    print(f"   ❌ Ошибка при вызове run(): {run_error}")
                    print(f"   🔍 Детали ошибки:")
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"Ошибка при запуске окна: {run_error}")
                
                print("✅ Главный цикл игры запущен")
                
                # 8. ПРОВЕРКА ПОСЛЕ ЗАПУСКА
                print(f"\n🔍 8. ПРОВЕРКА ПОСЛЕ ЗАПУСКА:")
                if hasattr(rendering_system, 'showbase') and hasattr(rendering_system.showbase, 'win'):
                    win = rendering_system.showbase.win
                    if hasattr(win, 'isValid'):
                        try:
                            is_valid = win.isValid()
                            print(f"   ✅ Окно валидно после запуска: {is_valid}")
                        except Exception as e:
                            print(f"   ⚠️  Не удалось проверить валидность после запуска: {e}")
                    
                    if hasattr(win, 'getXSize') and hasattr(win, 'getYSize'):
                        try:
                            width = win.getXSize()
                            height = win.getYSize()
                            print(f"   📏 Размеры после запуска: {width}x{height}")
                        except Exception as e:
                            print(f"   ⚠️  Не удалось получить размеры после запуска: {e}")
                else:
                    print(f"   ⚠️  Не удалось проверить окно после запуска")
                
                # 9. ПОДДЕРЖАНИЕ ОКНА ОТКРЫТЫМ
                print(f"\n🔄 9. ПОДДЕРЖАНИЕ ОКНА ОТКРЫТЫМ:")
                print(f"   🎮 Окно игры запущено!")
                print(f"   🪟 Оно должно быть видимым на экране")
                print(f"   ⏹️  Для выхода закройте окно игры или нажмите Ctrl+C")
                
                # ВАЖНО: Добавляем бесконечный цикл чтобы лаунчер не завершался
                print(f"   🔄 Лаунчер переходит в режим ожидания...")
                
                try:
                    # Ждем пока окно открыто
                    while True:
                        if hasattr(rendering_system, 'showbase') and hasattr(rendering_system.showbase, 'win'):
                            win = rendering_system.showbase.win
                            if hasattr(win, 'isValid'):
                                try:
                                    is_valid = win.isValid()
                                    if not is_valid:
                                        print(f"   ⚠️  Окно стало невалидным, завершаем работу")
                                        break
                                except Exception as e:
                                    print(f"   ⚠️  Не удалось проверить валидность окна: {e}")
                                    break
                        else:
                            print(f"   ⚠️  Окно не найдено, завершаем работу")
                            break
                        
                        # Ждем немного перед следующей проверкой
                        import time
                        time.sleep(1)
                        
                except KeyboardInterrupt:
                    print(f"\n   🛑 Получен сигнал прерывания (Ctrl+C)")
                    print(f"   🚪 Завершаем работу...")
                except Exception as e:
                    print(f"\n   ❌ Ошибка в цикле ожидания: {e}")
                
                print(f"   ✅ Работа завершена")
                
                print(f"\n🎉 ОКНО ИГРЫ УСПЕШНО ЗАПУЩЕНО!")
                print(f"   🎮 Игра готова к использованию")
                print(f"   🪟 Окно должно быть видимым")
                print(f"   ⏹️  Для выхода закройте окно игры")
                
            else:
                raise Exception("Система рендеринга не найдена в игре")
            
        except Exception as e:
            logger.error(f"Ошибка запуска окна игры: {e}")
            print(f"\n❌ ОШИБКА ЗАПУСКА ОКНА ИГРЫ: {e}")
            print("🔍 Детали ошибки:")
            traceback.print_exc()
            
            # Дополнительная диагностика
            print("\n🔍 ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА:")
            try:
                if hasattr(game, 'systems'):
                    print(f"📋 Доступные системы: {list(game.systems.keys())}")
                else:
                    print("❌ Игра не имеет атрибута 'systems'")
                
                if hasattr(game, 'get_system_info'):
                    try:
                        info = game.get_system_info()
                        print(f"📊 Информация о системах: {info}")
                    except Exception as info_e:
                        print(f"⚠️  Не удалось получить информацию о системах: {info_e}")
                else:
                    print("❌ Игра не имеет метода 'get_system_info'")
                    
            except Exception as diag_e:
                print(f"⚠️  Ошибка дополнительной диагностики: {diag_e}")
            
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

