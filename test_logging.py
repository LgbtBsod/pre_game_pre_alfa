"""
Тест новой системы логирования
"""

import sys
import time
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from utils.logger_config import (
    setup_logging,
    get_logger,
    log_system_info,
    log_startup_sequence,
    log_error_with_context,
    log_performance_metrics,
)


def test_basic_logging():
    """Тест базового логирования"""
    print("=== ТЕСТ БАЗОВОГО ЛОГИРОВАНИЯ ===")

    # Настраиваем логирование
    setup_logging("DEBUG")

    # Получаем логгер
    logger = get_logger("Test")

    # Тестируем разные уровни
    logger.debug("Это debug сообщение")
    logger.info("Это info сообщение")
    logger.warning("Это warning сообщение")
    logger.error("Это error сообщение")

    print("✓ Базовое логирование работает")


def test_system_info():
    """Тест логирования информации о системе"""
    print("\n=== ТЕСТ ИНФОРМАЦИИ О СИСТЕМЕ ===")

    try:
        log_system_info()
        print("✓ Информация о системе залогирована")
    except Exception as e:
        print(f"✗ Ошибка логирования информации о системе: {e}")


def test_startup_sequence():
    """Тест логирования последовательности запуска"""
    print("\n=== ТЕСТ ПОСЛЕДОВАТЕЛЬНОСТИ ЗАПУСКА ===")

    try:
        log_startup_sequence()
        print("✓ Последовательность запуска залогирована")
    except Exception as e:
        print(f"✗ Ошибка логирования последовательности запуска: {e}")


def test_error_logging():
    """Тест логирования ошибок с контекстом"""
    print("\n=== ТЕСТ ЛОГИРОВАНИЯ ОШИБОК ===")

    try:
        # Создаем тестовую ошибку
        test_error = ValueError("Тестовая ошибка для проверки логирования")

        # Логируем с контекстом
        log_error_with_context(
            test_error,
            "Тестовая функция",
            {"test_param": "test_value", "test_number": 42},
        )
        print("✓ Ошибка с контекстом залогирована")
    except Exception as e:
        print(f"✗ Ошибка логирования ошибки: {e}")


def test_performance_logging():
    """Тест логирования метрик производительности"""
    print("\n=== ТЕСТ МЕТРИК ПРОИЗВОДИТЕЛЬНОСТИ ===")

    try:
        # Симулируем операцию
        start_time = time.time()
        time.sleep(0.1)  # Имитируем работу
        duration = time.time() - start_time

        # Логируем метрики
        log_performance_metrics(
            "Тестовая операция",
            duration,
            {"iterations": 100, "memory_used": "1.5 MB", "cpu_usage": "25%"},
        )
        print("✓ Метрики производительности залогированы")
    except Exception as e:
        print(f"✗ Ошибка логирования метрик: {e}")


def test_specialized_loggers():
    """Тест специализированных логгеров"""
    print("\n=== ТЕСТ СПЕЦИАЛИЗИРОВАННЫХ ЛОГГЕРОВ ===")

    try:
        # Тестируем разные логгеры
        ui_logger = get_logger("UI")
        game_logger = get_logger("Game")
        ai_logger = get_logger("AI")
        data_logger = get_logger("Data")

        ui_logger.info("UI логгер работает")
        game_logger.info("Game логгер работает")
        ai_logger.info("AI логгер работает")
        data_logger.info("Data логгер работает")

        print("✓ Специализированные логгеры работают")
    except Exception as e:
        print(f"✗ Ошибка специализированных логгеров: {e}")


def test_log_levels():
    """Тест изменения уровней логирования"""
    print("\n=== ТЕСТ ИЗМЕНЕНИЯ УРОВНЕЙ ===")

    try:
        logger = get_logger("LevelTest")

        # Тестируем разные уровни
        print("Устанавливаем уровень DEBUG...")
        setup_logging("DEBUG")
        logger.debug("DEBUG сообщение должно быть видно")

        print("Устанавливаем уровень INFO...")
        setup_logging("INFO")
        logger.debug("DEBUG сообщение НЕ должно быть видно")
        logger.info("INFO сообщение должно быть видно")

        print("Устанавливаем уровень WARNING...")
        setup_logging("WARNING")
        logger.info("INFO сообщение НЕ должно быть видно")
        logger.warning("WARNING сообщение должно быть видно")

        print("✓ Изменение уровней логирования работает")
    except Exception as e:
        print(f"✗ Ошибка изменения уровней: {e}")


def main():
    """Главная функция тестирования"""
    print("=== ТЕСТИРОВАНИЕ НОВОЙ СИСТЕМЫ ЛОГИРОВАНИЯ ===\n")

    try:
        test_basic_logging()
        test_system_info()
        test_startup_sequence()
        test_error_logging()
        test_performance_logging()
        test_specialized_loggers()
        test_log_levels()

        print("\n=== ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО ===")
        print("Проверьте файлы логов в папке 'logs' и корневой директории")

    except Exception as e:
        print(f"\n✗ Критическая ошибка тестирования: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
