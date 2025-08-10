"""
Запуск игры с полноценным UI интерфейсом
Оптимизированная версия с улучшенной архитектурой
"""

import sys
import time
import threading
from pathlib import Path
from typing import Optional

# Импорт и настройка логирования
from utils.logger_config import (
    setup_logging,
    get_logger,
    log_system_info,
    log_startup_sequence,
    log_error_with_context,
)

# Настраиваем логирование
logger = get_logger("Main")
setup_logging("INFO")

# Импорт основных систем
from config.config_manager import config_manager
from core.data_manager import data_manager
from core.game_state_manager import game_state_manager
from entities.entity_factory import entity_factory
from items.item_manager import item_manager
from ai.ai_manager import ai_manager

# Импорт UI
from ui.main_window import MainWindow


class GameLauncher:
    """Класс для запуска игры с оптимизированной архитектурой"""

    def __init__(self):
        self.main_window: Optional[MainWindow] = None
        self.initialization_complete = False
        self.error_occurred = False
        self.error_message = ""

    def initialize_game_systems(self) -> bool:
        """Инициализация игровых систем с обработкой ошибок"""
        start_time = time.time()

        try:
            logger.info("=== ИНИЦИАЛИЗАЦИЯ ИГРОВЫХ СИСТЕМ ===")

            # Загружаем настройки
            logger.info("Загрузка настроек...")
            config_manager.reload()
            logger.info("✓ Настройки загружены")

            # Загружаем данные
            logger.info("Загрузка игровых данных...")
            data_manager.reload_data()
            logger.info("✓ Данные загружены")

            # Инициализируем AI систему
            logger.info("Инициализация AI системы...")
            ai_manager.initialize()
            logger.info("✓ AI система инициализирована")

            # Проверяем целостность данных
            logger.info("Проверка целостности данных...")
            if not self._verify_data_integrity():
                logger.warning(
                    "⚠ Обнаружены проблемы с данными, но игра может работать"
                )

            duration = time.time() - start_time
            logger.info(f"=== ВСЕ СИСТЕМЫ ИНИЦИАЛИЗИРОВАНЫ УСПЕШНО ===")
            logger.info(f"Время инициализации: {duration:.3f} секунд")

            self.initialization_complete = True
            return True

        except Exception as e:
            duration = time.time() - start_time
            log_error_with_context(
                e,
                "Инициализация игровых систем",
                {
                    "duration": duration,
                    "initialization_complete": self.initialization_complete,
                },
            )
            self.error_occurred = True
            self.error_message = str(e)
            return False

    def _verify_data_integrity(self) -> bool:
        """Проверка целостности игровых данных"""
        try:
            logger.info("Проверка целостности данных...")

            # Проверяем базу данных
            db_path = Path("data/game_data.db")
            if not db_path.exists():
                logger.warning("База данных не найдена")
                return False
            else:
                logger.info("✓ База данных найдена")

            # Проверяем создание тестовых объектов
            logger.info("Тестирование создания сущностей...")

            test_player = entity_factory.create_player("TestPlayer", (100, 100))
            if not test_player:
                logger.warning("⚠ Не удалось создать тестового игрока")
            else:
                logger.info("✓ Тестовый игрок создан")

            test_enemy = entity_factory.create_enemy("warrior", 1, (200, 200))
            if not test_enemy:
                logger.warning("⚠ Не удалось создать тестового врага")
            else:
                logger.info("✓ Тестовый враг создан")

            logger.info("✓ Проверка целостности данных завершена")
            return True

        except Exception as e:
            log_error_with_context(e, "Проверка целостности данных")
            return False

    def create_main_window(self) -> bool:
        """Создание главного окна"""
        start_time = time.time()

        try:
            logger.info("Создание главного окна...")
            self.main_window = MainWindow()

            duration = time.time() - start_time
            logger.info(f"✓ Главное окно создано за {duration:.3f} секунд")
            return True

        except Exception as e:
            duration = time.time() - start_time
            log_error_with_context(
                e,
                "Создание главного окна",
                {
                    "duration": duration,
                    "main_window_created": self.main_window is not None,
                },
            )
            self.error_occurred = True
            self.error_message = str(e)
            return False

    def run_game(self) -> bool:
        """Запуск игры"""
        start_time = time.time()

        try:
            logger.info("=== ЗАПУСК ИГРЫ ===")

            # Инициализируем системы
            if not self.initialize_game_systems():
                logger.error("Не удалось инициализировать игровые системы")
                return False

            # Создаем главное окно
            if not self.create_main_window():
                logger.error("Не удалось создать главное окно")
                return False

            logger.info("Запуск UI интерфейса...")

            # Запускаем UI напрямую (без многопоточности)
            self._run_ui()

            duration = time.time() - start_time
            logger.info(f"=== ИГРА ЗАВЕРШЕНА ===")
            logger.info(f"Общее время работы: {duration:.3f} секунд")
            return True

        except KeyboardInterrupt:
            duration = time.time() - start_time
            logger.info(f"Игра прервана пользователем после {duration:.3f} секунд")
            return True

        except Exception as e:
            duration = time.time() - start_time
            log_error_with_context(
                e,
                "Запуск игры",
                {
                    "duration": duration,
                    "initialization_complete": self.initialization_complete,
                    "main_window_created": self.main_window is not None,
                },
            )
            self.error_occurred = True
            self.error_message = str(e)
            return False

    def _run_ui(self):
        """Запуск UI в отдельном потоке"""
        try:
            if self.main_window:
                logger.info("Запуск главного окна...")
                self.main_window.run()
                logger.info("Главное окно закрыто")
            else:
                logger.error("Главное окно не создано")
        except Exception as e:
            log_error_with_context(
                e, "UI поток", {"main_window_exists": self.main_window is not None}
            )
            self.error_occurred = True
            self.error_message = str(e)

    def show_error_dialog(self):
        """Показ диалога с ошибкой"""
        if self.error_occurred and self.error_message:
            try:
                logger.info("Показ диалога с ошибкой...")

                import tkinter as tk
                from tkinter import messagebox

                root = tk.Tk()
                root.withdraw()  # Скрываем основное окно

                messagebox.showerror(
                    "Ошибка запуска игры",
                    f"Произошла ошибка при запуске игры:\n\n{self.error_message}\n\n"
                    "Проверьте логи в файле game_ui.log для получения дополнительной информации.",
                )

                root.destroy()
                logger.info("Диалог с ошибкой показан")

            except Exception as e:
                log_error_with_context(
                    e,
                    "Показ диалога ошибки",
                    {
                        "original_error": self.error_message,
                        "error_occurred": self.error_occurred,
                    },
                )
                print(f"ОШИБКА: {self.error_message}")
        else:
            logger.warning("Попытка показать диалог ошибки без ошибки")


def check_system_requirements() -> bool:
    """Проверка системных требований"""
    logger.info("Проверка системных требований...")

    try:
        # Проверяем версию Python
        if sys.version_info < (3, 7):
            logger.error("Требуется Python 3.7 или выше")
            return False
        else:
            logger.info(
                f"✓ Версия Python: {sys.version_info.major}.{sys.version_info.minor}"
            )

        # Проверяем необходимые модули
        required_modules = ["tkinter", "json", "sqlite3", "threading"]
        missing_modules = []

        for module in required_modules:
            try:
                __import__(module)
                logger.info(f"✓ Модуль {module} найден")
            except ImportError:
                logger.error(f"✗ Модуль {module} не найден")
                missing_modules.append(module)

        if missing_modules:
            logger.error(f"Отсутствуют модули: {', '.join(missing_modules)}")
            return False

        # Проверяем доступ к файловой системе
        if not Path(".").exists():
            logger.error("Нет доступа к текущей директории")
            return False
        else:
            logger.info("✓ Доступ к файловой системе")

        logger.info("✓ Системные требования выполнены")
        return True

    except Exception as e:
        log_error_with_context(e, "Проверка системных требований")
        return False


def create_backup():
    """Создание резервной копии важных файлов"""
    try:
        logger.info("Создание резервной копии...")

        backup_dir = Path("backup")
        backup_dir.mkdir(exist_ok=True)
        logger.info(f"✓ Директория резервных копий: {backup_dir}")

        important_files = [
            "data/game_data.db",
            "data/game_settings.json",
            "data/difficulty_settings.json",
            "data/ui_settings.json",
            "data/graphics_settings.json",
            "data/audio_settings.json",
            "data/ai_settings.json",
            "data/combat_settings.json",
            "data/inventory_settings.json",
        ]

        backed_up_files = []
        missing_files = []

        for file_path in important_files:
            source = Path(file_path)
            if source.exists():
                backup_path = backup_dir / f"{source.name}.backup"
                import shutil

                shutil.copy2(source, backup_path)
                backed_up_files.append(file_path)
                logger.info(f"✓ Резервная копия создана: {file_path}")
            else:
                missing_files.append(file_path)
                logger.warning(f"⚠ Файл не найден: {file_path}")

        if backed_up_files:
            logger.info(f"✓ Резервная копия создана для {len(backed_up_files)} файлов")
        else:
            logger.warning("⚠ Не создано ни одной резервной копии")

        if missing_files:
            logger.warning(f"⚠ Отсутствуют файлы: {', '.join(missing_files)}")

    except Exception as e:
        log_error_with_context(
            e,
            "Создание резервной копии",
            {
                "backup_dir": (
                    str(backup_dir) if "backup_dir" in locals() else "не создана"
                ),
                "important_files_count": len(important_files),
            },
        )


def main():
    """Главная функция запуска"""
    start_time = time.time()

    try:
        # Логируем информацию о системе и последовательность запуска
        log_system_info()
        log_startup_sequence()

        logger.info("=== ЗАПУСК AI EVOLVE ===")
        logger.info(f"Время запуска: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Версия Python: {sys.version}")
        logger.info(f"Платформа: {sys.platform}")

        # Проверяем системные требования
        if not check_system_requirements():
            logger.error("Системные требования не выполнены")
            return 1

        # Создаем резервную копию
        create_backup()

        # Создаем и запускаем игру
        launcher = GameLauncher()
        success = launcher.run_game()

        # Показываем ошибку, если она произошла
        if launcher.error_occurred:
            launcher.show_error_dialog()

        # Выводим статистику
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Время работы: {duration:.2f} секунд")

        if success:
            logger.info("🎉 Игра завершена успешно!")
            return 0
        else:
            logger.error("❌ Игра завершена с ошибками")
            return 1

    except KeyboardInterrupt:
        logger.info("Игра прервана пользователем")
        return 0

    except Exception as e:
        log_error_with_context(
            e,
            "Главная функция",
            {"start_time": start_time, "duration": time.time() - start_time},
        )
        return 1

    finally:
        logger.info("=== ЗАВЕРШЕНИЕ РАБОТЫ ===")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
