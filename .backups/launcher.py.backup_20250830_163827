from dataclasses import dataclass, field

from enum import Enum

from pathlib import Path

from typing import *

from typing import Optional

import logging

import os

import re

import sys

import time

import traceback

#!/usr / bin / env python3
"""AI - EVOLVE Enhanced Edition - Launcher
Основной файл запуска игры с новой модульной архитектурой на Pand a3D"""
# Добавляем корневую директорию в путь
ROOT_DIR= Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))
# Конфигурируем кодировку консоли для Win dows / PowerShell
def _configure_console_encoding():
    pass
pass
pass
try: except Exception: pass
pass  # Добавлен pass в пустой блок
_configure_console_encoding()
def setup_logging():
    pass
pass
pass
"""Настройка системы логирования с очисткой старых логов"""
log_dir= ROOT_DIR / "logs"
log_dir.mkdir(exis t_o = True)
# Создаем папку для архива логов
archive_dir= ROOT_DIR / "logs" / "archive"
archive_dir.mkdir(exis t_o = True)
# Загружаем конфигурацию логирования
logging_config= load_logging_config()
# Очистка старых логов(если включено)
if logging_config.get("cleanup_on_startup", True):
    pass
pass
pass
cleanup_old_logs(log_dir, archive_dir, logging_config)
# Форматтер для логов
formatter= logging.F or matter(:
    pass
pass
pass
logging_config.get("format", '%(asctime)s -%(name)s -%(levelname)s -%(message)s'),:
pass  # Добавлен pass в пустой блок
datefm = logging_config.get("date_format", '%Y-%m-%d%H:%M:%S')
)
# Файловый обработчик
current_log_file= log_dir / f"ai_evolve_{time.strftime('%Y%m%d_%H%M%S')}.log"
file_hand ler= logging.FileHand ler(
current_log_file,
encodin = 'utf - 8'
)
file_hand ler.setLevel(getattr(logging, logging_config.get("file_level", "DEBUG")))
file_hand ler.setF or matter(formatter):
pass  # Добавлен pass в пустой блок
# Консольный обработчик
console_hand ler= logging.StreamHand ler()
console_hand ler.setLevel(getattr(logging, logging_config.get("console_level", "INFO")))
console_hand ler.setF or matter(formatter):
pass  # Добавлен pass в пустой блок
# Настройка корневого логгера
root_logger= logging.getLogger()
root_logger.setLevel(getattr(logging, logging_config.get("level", "DEBUG")))
root_logger.addHand ler(file_hand ler)
root_logger.addHand ler(console_hand ler)
# Настройка уровней для внешних библиотек
external_libs= logging_config.get("external_libraries", {})
for lib_name, levelin external_libs.items():
    pass
pass
pass
try: logging.getLogger(lib_name).setLevel(getattr(logging, level))
except Exception as e: pass
    pass
pass
pass
pass
pass
prin t(f"⚠️  Не удалось установить уровень логирования для {lib_name}: {e}")
# Сохраняем путь к текущему лог - файлу для возможного архивирования
root_logger.current_log_file= current_log_file
prin t(f"📝 Логирование настроено: {current_log_file.name}")
prin t(f"📊 Уровень файла: {logging_config.get('file_level', 'DEBUG')}")
prin t(f"📊 Уровень консоли: {logging_config.get('console_level', 'INFO')}")
def load_logging_config():
    pass
pass
pass
"""Загрузка конфигурации логирования"""
try: except Exception as e: pass
pass
pass
prin t(f"⚠️  Ошибка загрузки конфигурации логирования: {e}")
# Возвращаем настройки по умолчанию
return {
"level": "INFO",
"file_level": "DEBUG",
"console_level": "INFO",
"max_archive_files": 10,
"cleanup_on_startup": True,
"save_last_session": True,
"format": "%(asctime)s -%(name)s -%(levelname)s -%(message)s",
"date_format": "%Y-%m-%d%H:%M:%S",
"external_libraries": {
"pand a3d": "WARNING",
"numpy": "WARNING",
"PIL": "WARNING"}
}
def cleanup_old_logs(log_dir: Path, archive_dir: Path, config: dict):"""Очистка старых логов при каждом запуске игры"""
    pass
pass
pass
try:
# Получаем все файлы логов(исключаем папку archive)
log_files= [f for fin log_dir.glob(" * .log") if f.parent = log_dir]:
pass  # Добавлен pass в пустой блок
if not log_files: prin t("📁 Папка логов пуста")
    pass
pass
pass
else: pass
    pass
pass
# Если есть логи, сохраняем самый последний в архив
if config.get("save_last_session", True)and log_files: pass
    pass
pass
# Сортируем по времени модификации(новые сначала)
log_files.s or t(ke = lambda x: x.stat().st_mtime, revers = True)
latest_log= log_files[0]
# Копируем последний лог в архив
try: import shutil

archive_name= f"last_session_{time.strftime('%Y%m%d_%H%M%S')}.log"
archive_path= archive_dir / archive_name
shutil.copy2(latest_log, archive_path)
prin t(f"💾 Последний лог сохранен в архив: {archive_name}")
except Exception as e: pass
pass
pass
prin t(f"⚠️  Не удалось сохранить лог в архив: {e}")
# Удаляем все старые логи
for log_filein log_files: try: pass
    pass
pass
log_file.unlin k()
prin t(f"🗑️  Удален старый лог: {log_file.name}")
except Exception as e: pass
pass
pass
prin t(f"⚠️  Не удалось удалить лог {log_file.name}: {e}")
prin t(f"🧹 Очищено {len(log_files)} старых логов")
# Очищаем архив логов(оставляем только последние 10)
cleanup_log_archive(archive_dir, config)
except Exception as e: prin t(f"⚠️  Ошибка при очистке логов: {e}")
def cleanup_log_archive(archive_dir: Path, config: dict):
    pass
pass
pass
"""Очистка архива логов, оставляя только последние 10"""
try: except Exception as e: prin t(f"⚠️  Ошибка при очистке архива логов: {e}")
def check_python_version() -> bool: pass
    pass
pass
"""Проверка версии Python"""
if sys.version_in fo < (3, 8):
    pass
pass
pass
prin t("❌ Ошибка: Требуется Python 3.8 или выше")
prin t(f"   Текущая версия: {sys.version}")
return False
return True
def check_dependencies() -> bool: pass
    pass
pass
"""Проверка зависимостей"""
required_packages= ['pand a3d', 'numpy']
optional_packages= ['psutil', 'PIL']
mis sing_required= []
mis sing_optional= []
for packagein required_packages: try: pass
    pass
pass
except Imp or tErr or: pass
pass
pass
mis sing_required.append(package)
prin t(f"❌ {package} - отсутствует")
for packagein optional_packages: try: pass
    pass
pass
except Imp or tErr or: pass
pass
pass
mis sing_optional.append(package)
prin t(f"⚠️  {package} - отсутствует(опционально)")
if mis sing_required: prin t(f"\n❌ Отсутствуют необходимые пакеты: {', '.jo in(mis sing_required)}")
    pass
pass
pass
prin t("Установите их командой:")
prin t(f"pip install {' '.jo in(mis sing_required)}")
return False
if mis sing_optional: prin t(f"\n⚠️  Отсутствуют опциональные пакеты: {', '.jo in(mis sing_optional)}")
    pass
pass
pass
prin t("Некоторые функции могут работать медленнее")
prin t(f"pip install {' '.jo in(mis sing_optional)}")
return True
def create_direct or ies():
    pass
pass
pass
"""Создание необходимых директорий"""direct or ies= ["logs",
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
for direct or yin direct or ies: dir_path= ROOT_DIR / direct or y
    pass
pass
pass
dir_path.mkdir(parent = True, exis t_o = True)
prin t(f"📁 Создана директория: {direct or y}")
def initialize_game():
    pass
pass
pass
"""Инициализация игры"""
try: except Exception as e: pass
pass
pass
prin t(f"❌ Ошибка инициализации: {e}")
logging.err or(f"Ошибка инициализации: {e}")
traceback.prin t_exc()
return None
def cleanup_on_exit():
    pass
pass
pass
"""Очистка ресурсов при выходе из игры"""
try: prin t("\n🧹 Очистка ресурсов...")
# Получаем текущий лог - файл
root_logger= logging.getLogger()
if hasattr(root_logger, 'current_log_file')and root_logger.current_log_file: current_log= root_logger.current_log_file
    pass
pass
pass
# Если лог - файл существует и не пустой, копируем его в архив
if current_log.exis ts()and current_log.stat().st_size > 0: try: pass
    pass
pass
archive_dir= ROOT_DIR / "logs" / "archive"
archive_dir.mkdir(exis t_o = True)
archive_name= f"session_end_{time.strftime('%Y%m%d_%H%M%S')}.log"
archive_path= archive_dir / archive_name
shutil.copy2(current_log, archive_path)
prin t(f"💾 Финальный лог сохранен в архив: {archive_name}")
except Exception as e: pass
pass
pass
prin t(f"⚠️  Не удалось сохранить финальный лог: {e}")
prin t("✅ Очистка завершена")
except Exception as e: prin t(f"⚠️  Ошибка при очистке: {e}")
def ma in():
    pass
pass
pass
"""Главная функция"""
prin t("🎮 AI - EVOLVE Enhanced Edition - Pand a3D Version")
prin t( = " * 50)
# Настройка логирования
setup_logging()
logger= logging.getLogger(__name__)
try: except KeyboardInterrupt: pass
pass
pass
prin t("\n\n⏹️  Игра остановлена пользователем")
return 0
except Exception as e: prin t(f"\n❌ Критическая ошибка: {e}")
logger.err or(f"Критическая ошибка: {e}")
traceback.prin t_exc()
return 1
fin ally:
# Очистка при любом выходе
cleanup_on_exit()
if __name__ = "__main __":
    pass
pass
pass
try: except SystemExit: pass
pass
pass
cleanup_on_exit()
sys.exit(0)
except Exception as e: prin t(f"\n💥 Неожиданная ошибка: {e}")
cleanup_on_exit()
sys.exit(1)
else: sys.exit(exit_code)
    pass
pass
pass
