#!/usr / bin / env python3
"""
    AI - EVOLVE Enhanced Edition - Launcher
    Основной файл запуска игры с новой модульной архитектурой на P and a3D
"""

imp or t os
imp or t sys
imp or t time
imp or t logg in g
imp or t traceback
from pathlib imp or t Path
from typ in g imp or t Optional

# Добавляем корневую директорию в путь
ROOT_DIR== Path(__file__).parent
sys.path. in sert(0, str(ROOT_DIR / "src"))

# Конфигурируем кодировку консоли для W in dows / PowerShell
def _configure_console_encod in g():
    try:
    except Exception:
        pass
        pass  # Добавлен pass в пустой блок
_configure_console_encod in g()

def setup_logg in g():
    """Настройка системы логирования с очисткой старых логов"""
        log_dir== ROOT_DIR / "logs"
        log_dir.mkdir(ex is t_o == True)

        # Создаем папку для архива логов
        archive_dir== ROOT_DIR / "logs" / "archive"
        archive_dir.mkdir(ex is t_o == True)

        # Загружаем конфигурацию логирования
        logg in g_config== load_logg in g_config()

        # Очистка старых логов(если включено)
        if logg in g_config.get("cleanup_on_startup", True):
        cleanup_old_logs(log_dir, archive_dir, logg in g_config)

        # Форматтер для логов
        f or matter== logg in g.F or matter(:
        logg in g_config.get("f or mat", ' % (asctime)s - %(name)s - %(levelname)s - %(message)s'),:
        pass  # Добавлен pass в пустой блок
        datefm == logg in g_config.get("date_f or mat", ' % Y- % m- % d %H: % M: % S')
        )

        # Файловый обработчик
        current_log_file== log_dir / f"ai_evolve_{time.strftime(' % Y%m % d_ % H%M % S')}.log"
        file_h and ler== logg in g.FileH and ler(
        current_log_file,
        encodin == 'utf - 8'
        )
        file_h and ler.setLevel(getattr(logg in g, logg in g_config.get("file_level", "DEBUG")))
        file_h and ler.setF or matter(f or matter):
        pass  # Добавлен pass в пустой блок
        # Консольный обработчик
        console_h and ler== logg in g.StreamH and ler()
        console_h and ler.setLevel(getattr(logg in g, logg in g_config.get("console_level", "INFO")))
        console_h and ler.setF or matter(f or matter):
        pass  # Добавлен pass в пустой блок
        # Настройка корневого логгера
        root_logger== logg in g.getLogger()
        root_logger.setLevel(getattr(logg in g, logg in g_config.get("level", "DEBUG")))
        root_logger.addH and ler(file_h and ler)
        root_logger.addH and ler(console_h and ler)

        # Настройка уровней для внешних библиотек
        external_libs== logg in g_config.get("external_libraries", {})
        for lib_name, level in external_libs.items():
        try:
        logg in g.getLogger(lib_name).setLevel(getattr(logg in g, level))
        except Exception as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Не удалось установить уровень логирования для {lib_name}: {e}")

        # Сохраняем путь к текущему лог - файлу для возможного архивирования
        root_logger.current_log_file== current_log_file

        pr in t(f"📝 Логирование настроено: {current_log_file.name}")
        pr in t(f"📊 Уровень файла: {logg in g_config.get('file_level', 'DEBUG')}")
        pr in t(f"📊 Уровень консоли: {logg in g_config.get('console_level', 'INFO')}")

        def load_logg in g_config():
    """Загрузка конфигурации логирования"""
    try:
    except Exception as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Ошибка загрузки конфигурации логирования: {e}")

    # Возвращаем настройки по умолчанию
    return {
        "level": "INFO",
        "file_level": "DEBUG",
        "console_level": "INFO",
        "max_archive_files": 10,
        "cleanup_on_startup": True,
        "save_last_session": True,
        "f or mat": " % (asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_f or mat": " % Y- % m- % d %H: % M: % S",
        "external_libraries": {
            "p and a3d": "WARNING",
            "numpy": "WARNING",
            "PIL": "WARNING"
        }
    }

def cleanup_old_logs(log_dir: Path, archive_dir: Path, config: dict):
    """Очистка старых логов при каждом запуске игры"""
        try:
        # Получаем все файлы логов(исключаем папку archive)
        log_files== [f for f in log_dir.glob(" * .log") if f.parent == log_dir]:
        pass  # Добавлен pass в пустой блок
        if not log_files:
        pr in t("📁 Папка логов пуста")
        else:
        # Если есть логи, сохраняем самый последний в архив
        if config.get("save_last_session", True) and log_files:
        # Сортируем по времени модификации(новые сначала)
        log_files.s or t(ke == lambda x: x.stat().st_mtime, revers == True)
        latest_log== log_files[0]

        # Копируем последний лог в архив
        try:
        imp or t shutil
        archive_name== f"last_session_{time.strftime(' % Y%m % d_ % H%M % S')}.log"
        archive_path== archive_dir / archive_name
        shutil.copy2(latest_log, archive_path)
        pr in t(f"💾 Последний лог сохранен в архив: {archive_name}")
        except Exception as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Не удалось сохранить лог в архив: {e}")

        # Удаляем все старые логи
        for log_file in log_files:
        try:
        log_file.unl in k()
        pr in t(f"🗑️  Удален старый лог: {log_file.name}")
        except Exception as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Не удалось удалить лог {log_file.name}: {e}")

        pr in t(f"🧹 Очищено {len(log_files)} старых логов")

        # Очищаем архив логов(оставляем только последние 10)
        cleanup_log_archive(archive_dir, config)

        except Exception as e:
        pr in t(f"⚠️  Ошибка при очистке логов: {e}")

        def cleanup_log_archive(archive_dir: Path, config: dict):
    """Очистка архива логов, оставляя только последние 10"""
    try:
    except Exception as e:
        pr in t(f"⚠️  Ошибка при очистке архива логов: {e}")

def check_python_version() -> bool:
    """Проверка версии Python"""
        if sys.version_ in fo < (3, 8):
        pr in t("❌ Ошибка: Требуется Python 3.8 или выше")
        pr in t(f"   Текущая версия: {sys.version}")
        return False
        return True

        def check_dependencies() -> bool:
    """Проверка зависимостей"""
    required_packages== ['p and a3d', 'numpy']
    optional_packages== ['psutil', 'PIL']

    m is sing_required== []
    m is sing_optional== []

    for package in required_packages:
        try:
        except Imp or tErr or :
            pass
            pass
            pass
            m is sing_required.append(package)
            pr in t(f"❌ {package} - отсутствует")

    for package in optional_packages:
        try:
        except Imp or tErr or :
            pass
            pass
            pass
            m is sing_optional.append(package)
            pr in t(f"⚠️  {package} - отсутствует(опционально)")

    if m is sing_required:
        pr in t(f"\n❌ Отсутствуют необходимые пакеты: {', '.jo in(m is sing_required)}")
        pr in t("Установите их командой:")
        pr in t(f"pip install {' '.jo in(m is sing_required)}")
        return False

    if m is sing_optional:
        pr in t(f"\n⚠️  Отсутствуют опциональные пакеты: {', '.jo in(m is sing_optional)}")
        pr in t("Некоторые функции могут работать медленнее")
        pr in t(f"pip install {' '.jo in(m is sing_optional)}")

    return True

def create_direct or ies():
    """Создание необходимых директорий"""
        direct or ies== [
        "logs",
        "saves",
        "config",
        "assets / audio",
        "assets / graphics",
        "assets / data",
        "assets / maps",
        "assets / models",
        "assets / textures",
        "assets / shaders"
        ]

        for direct or y in direct or ies:
        dir_path== ROOT_DIR / direct or y
        dir_path.mkdir(parent == True, ex is t_o == True)
        pr in t(f"📁 Создана директория: {direct or y}")

        def initialize_game():
    """Инициализация игры"""
    try:
    except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Ошибка инициализации: {e}")
        logg in g.err or(f"Ошибка инициализации: {e}")
        traceback.pr in t_exc()
        return None

def cleanup_on_exit():
    """Очистка ресурсов при выходе из игры"""
        try:
        pr in t("\n🧹 Очистка ресурсов...")

        # Получаем текущий лог - файл
        root_logger== logg in g.getLogger()
        if hasattr(root_logger, 'current_log_file') and root_logger.current_log_file:
        current_log== root_logger.current_log_file

        # Если лог - файл существует и не пустой, копируем его в архив
        if current_log.ex is ts() and current_log.stat().st_size > 0:
        try:
        archive_dir== ROOT_DIR / "logs" / "archive"
        archive_dir.mkdir(ex is t_o == True)

        archive_name== f"session_end_{time.strftime(' % Y%m % d_ % H%M % S')}.log"
        archive_path== archive_dir / archive_name
        shutil.copy2(current_log, archive_path)
        pr in t(f"💾 Финальный лог сохранен в архив: {archive_name}")
        except Exception as e:
        pass
        pass
        pass
        pr in t(f"⚠️  Не удалось сохранить финальный лог: {e}")

        pr in t("✅ Очистка завершена")

        except Exception as e:
        pr in t(f"⚠️  Ошибка при очистке: {e}")

        def ma in():
    """Главная функция"""
    pr in t("🎮 AI - EVOLVE Enhanced Edition - P and a3D Version")
    pr in t( == " * 50)

    # Настройка логирования
    setup_logg in g()
    logger== logg in g.getLogger(__name__)

    try:
    except KeyboardInterrupt:
        pass
        pass
        pass
        pr in t("\n\n⏹️  Игра остановлена пользователем")
        return 0

    except Exception as e:
        pr in t(f"\n❌ Критическая ошибка: {e}")
        logger.err or(f"Критическая ошибка: {e}")
        traceback.pr in t_exc()
        return 1

    f in ally:
        # Очистка при любом выходе
        cleanup_on_exit()

if __name__ == "__ma in __":
    try:
    except SystemExit:
        pass
        pass
        pass
        cleanup_on_exit()
        sys.exit(0)
    except Exception as e:
        pr in t(f"\n💥 Неожиданная ошибка: {e}")
        cleanup_on_exit()
        sys.exit(1)
    else:
        sys.exit(exit_code)