"""
Централизованная конфигурация логирования для AI EVOLVE.
Делает логи более понятными для людей и ИИ-помощников.
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Цвета для консоли (Windows поддерживает)
try:
    import colorama

    colorama.init()
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }
except ImportError:
    COLORS = {
        level: ""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "RESET"]
    }


class AIFriendlyFormatter(logging.Formatter):
    """
    Форматтер логов, оптимизированный для понимания ИИ-помощниками.
    Включает контекстную информацию и структурированные данные.
    """

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

        # Основной формат для файлов
        self.file_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(lineno)-4d | %(message)s"
        )

        # Формат для консоли с цветами
        self.console_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(lineno)-4d | %(message)s"
        )

    def format(self, record):
        # Добавляем контекстную информацию
        if not hasattr(record, "ai_context"):
            record.ai_context = self._get_ai_context(record)

        # Форматируем сообщение
        if self.use_colors and hasattr(record, "levelname"):
            color = COLORS.get(record.levelname, "")
            reset = COLORS["RESET"]
            record.levelname = f"{color}{record.levelname}{reset}"

        # Используем разные форматы для файла и консоли
        if hasattr(record, "is_console"):
            return self.console_format.format(record)
        else:
            return self.file_format.format(record)

    def _get_ai_context(self, record) -> str:
        """Генерирует контекстную информацию для ИИ-помощников"""
        context_parts = []

        # Добавляем информацию о модуле
        if record.module != "__main__":
            context_parts.append(f"module:{record.module}")

        # Добавляем информацию о функции
        if record.funcName != "<module>":
            context_parts.append(f"function:{record.funcName}")

        # Добавляем информацию о строке
        context_parts.append(f"line:{record.lineno}")

        # Добавляем информацию о процессе
        if hasattr(record, "process"):
            context_parts.append(f"process:{record.process}")

        # Добавляем информацию о потоке
        if hasattr(record, "thread"):
            context_parts.append(f"thread:{record.thread}")

        return " | ".join(context_parts) if context_parts else "no_context"


class StructuredFormatter(logging.Formatter):
    """
    Форматтер для структурированных логов в JSON формате.
    Полезен для анализа логов программами и ИИ.
    """

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "process": getattr(record, "process", None),
            "thread": getattr(record, "thread", None),
        }

        # Добавляем исключения если есть
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Добавляем дополнительные поля
        for key, value in record.__dict__.items():
            if key not in log_entry and not key.startswith("_"):
                log_entry[key] = str(value)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class LogManager:
    """
    Централизованный менеджер логирования для AI EVOLVE.
    """

    def __init__(self, app_name: str = "AI_EVOLVE"):
        self.app_name = app_name
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Основные логгеры
        self.main_logger = None
        self.ui_logger = None
        self.game_logger = None
        self.ai_logger = None
        self.data_logger = None

        # Настройка логирования
        self._setup_logging()

    def _setup_logging(self):
        """Настраивает систему логирования"""

        # Создаем основной логгер
        self.main_logger = logging.getLogger(self.app_name)
        self.main_logger.setLevel(logging.DEBUG)

        # Очищаем существующие обработчики
        self.main_logger.handlers.clear()

        # Создаем обработчики
        self._create_handlers()

        # Создаем специализированные логгеры
        self._create_specialized_loggers()

        # Устанавливаем уровень по умолчанию
        self.main_logger.setLevel(logging.INFO)

    def _create_handlers(self):
        """Создает обработчики для логов"""

        # 1. Консольный обработчик (INFO и выше)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(AIFriendlyFormatter(use_colors=True))
        console_handler.addFilter(lambda record: setattr(record, "is_console", True))
        self.main_logger.addHandler(console_handler)

        # 2. Файловый обработчик для всех логов (DEBUG и выше)
        all_logs_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "all_logs.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        all_logs_handler.setLevel(logging.DEBUG)
        all_logs_handler.setFormatter(AIFriendlyFormatter(use_colors=False))
        self.main_logger.addHandler(all_logs_handler)

        # 3. Файловый обработчик для ошибок (ERROR и выше)
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(AIFriendlyFormatter(use_colors=False))
        self.main_logger.addHandler(error_handler)

        # 4. JSON обработчик для структурированных логов
        json_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "structured_logs.json",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=3,
            encoding="utf-8",
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(StructuredFormatter())
        self.main_logger.addHandler(json_handler)

        # 5. Специальный обработчик для UI (game_ui.log)
        ui_handler = logging.FileHandler("game_ui.log", encoding="utf-8")
        ui_handler.setLevel(logging.DEBUG)
        ui_handler.setFormatter(AIFriendlyFormatter(use_colors=False))
        self.main_logger.addHandler(ui_handler)

        # 6. Специальный обработчик для игры (game.log)
        game_handler = logging.FileHandler("game.log", encoding="utf-8")
        game_handler.setLevel(logging.DEBUG)
        game_handler.setFormatter(AIFriendlyFormatter(use_colors=False))
        self.main_logger.addHandler(game_handler)

    def _create_specialized_loggers(self):
        """Создает специализированные логгеры для разных частей системы"""

        # UI логгер
        self.ui_logger = logging.getLogger(f"{self.app_name}.UI")
        self.ui_logger.setLevel(logging.DEBUG)

        # Игровой логгер
        self.game_logger = logging.getLogger(f"{self.app_name}.Game")
        self.game_logger.setLevel(logging.DEBUG)

        # AI логгер
        self.ai_logger = logging.getLogger(f"{self.app_name}.AI")
        self.ai_logger.setLevel(logging.DEBUG)

        # Логгер данных
        self.data_logger = logging.getLogger(f"{self.app_name}.Data")
        self.data_logger.setLevel(logging.DEBUG)

    def get_logger(self, name: str) -> logging.Logger:
        """Получает логгер с указанным именем"""
        return logging.getLogger(f"{self.app_name}.{name}")

    def set_level(self, level: str):
        """Устанавливает уровень логирования для всех логгеров"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if level.upper() in level_map:
            log_level = level_map[level.upper()]
            self.main_logger.setLevel(log_level)

            # Устанавливаем уровень для всех обработчиков
            for handler in self.main_logger.handlers:
                handler.setLevel(log_level)

            logging.info(f"Уровень логирования установлен: {level.upper()}")
        else:
            logging.warning(f"Неизвестный уровень логирования: {level}")

    def log_system_info(self):
        """Логирует информацию о системе"""
        import platform
        import psutil

        logging.info("=== ИНФОРМАЦИЯ О СИСТЕМЕ ===")
        logging.info(f"Операционная система: {platform.system()} {platform.release()}")
        logging.info(f"Версия Python: {sys.version}")
        logging.info(f"Архитектура: {platform.architecture()[0]}")
        logging.info(f"Процессор: {platform.processor()}")
        logging.info(f"Память: {psutil.virtual_memory().total // (1024**3)} GB")
        logging.info(f"Текущая директория: {os.getcwd()}")
        logging.info("================================")

    def log_startup_sequence(self):
        """Логирует последовательность запуска"""
        logging.info("=== ПОСЛЕДОВАТЕЛЬНОСТЬ ЗАПУСКА ===")
        logging.info("1. Инициализация системы логирования ✓")
        logging.info("2. Загрузка конфигурации...")
        logging.info("3. Инициализация игровых систем...")
        logging.info("4. Загрузка ресурсов...")
        logging.info("5. Создание UI...")
        logging.info("6. Запуск игрового цикла...")
        logging.info("================================")

    def log_error_with_context(
        self,
        error: Exception,
        context: str = "",
        additional_info: Dict[str, Any] = None,
    ):
        """Логирует ошибку с дополнительным контекстом"""
        logging.error(f"=== ОШИБКА В {context.upper()} ===")
        logging.error(f"Тип ошибки: {type(error).__name__}")
        logging.error(f"Сообщение: {str(error)}")

        if additional_info:
            for key, value in additional_info.items():
                logging.error(f"{key}: {value}")

        # Логируем стек вызовов
        import traceback

        logging.error("Стек вызовов:")
        for line in traceback.format_exc().split("\n"):
            if line.strip():
                logging.error(f"  {line}")

        logging.error("=" * 50)

    def log_performance_metrics(
        self, operation: str, duration: float, additional_metrics: Dict[str, Any] = None
    ):
        """Логирует метрики производительности"""
        logging.info(f"=== МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ: {operation} ===")
        logging.info(f"Время выполнения: {duration:.4f} секунд")

        if additional_metrics:
            for key, value in additional_metrics.items():
                logging.info(f"{key}: {value}")

        logging.info("=" * 50)


# Глобальный экземпляр менеджера логирования
log_manager = LogManager()


def get_logger(name: str) -> logging.Logger:
    """Получает логгер с указанным именем"""
    return log_manager.get_logger(name)


def setup_logging(level: str = "INFO"):
    """Настраивает систему логирования"""
    log_manager.set_level(level)
    return log_manager


def log_system_info():
    """Логирует информацию о системе"""
    log_manager.log_system_info()


def log_startup_sequence():
    """Логирует последовательность запуска"""
    log_manager.log_startup_sequence()


def log_error_with_context(
    error: Exception, context: str = "", additional_info: Dict[str, Any] = None
):
    """Логирует ошибку с дополнительным контекстом"""
    log_manager.log_error_with_context(error, context, additional_info)


def log_performance_metrics(
    operation: str, duration: float, additional_metrics: Dict[str, Any] = None
):
    """Логирует метрики производительности"""
    log_manager.log_performance_metrics(operation, duration, additional_metrics)
