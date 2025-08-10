"""
Запуск игры с полноценным UI интерфейсом
Оптимизированная версия с улучшенной архитектурой
"""
import sys
import logging
import time
import threading
from pathlib import Path
from typing import Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_ui.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Импорт основных систем
from config.settings_manager import settings_manager
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
        try:
            logger.info("=== ИНИЦИАЛИЗАЦИЯ ИГРОВЫХ СИСТЕМ ===")
            
            # Загружаем настройки
            logger.info("Загрузка настроек...")
            settings_manager.reload_settings()
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
                logger.warning("⚠ Обнаружены проблемы с данными, но игра может работать")
            
            logger.info("=== ВСЕ СИСТЕМЫ ИНИЦИАЛИЗИРОВАНЫ УСПЕШНО ===")
            self.initialization_complete = True
            return True
            
        except Exception as e:
            logger.error(f"✗ Ошибка инициализации: {e}")
            self.error_occurred = True
            self.error_message = str(e)
            return False
            
    def _verify_data_integrity(self) -> bool:
        """Проверка целостности игровых данных"""
        try:
            # Проверяем базу данных
            db_path = Path('data/game_data.db')
            if not db_path.exists():
                logger.warning("База данных не найдена")
                return False
                
            # Проверяем создание тестовых объектов
            test_player = entity_factory.create_player("TestPlayer", (100, 100))
            if not test_player:
                logger.warning("Не удалось создать тестового игрока")
                
            test_enemy = entity_factory.create_enemy("warrior", 1, (200, 200))
            if not test_enemy:
                logger.warning("Не удалось создать тестового врага")
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки целостности данных: {e}")
            return False
            
    def create_main_window(self) -> bool:
        """Создание главного окна"""
        try:
            logger.info("Создание главного окна...")
            self.main_window = MainWindow()
            logger.info("✓ Главное окно создано")
            return True
            
        except Exception as e:
            logger.error(f"✗ Ошибка создания главного окна: {e}")
            self.error_occurred = True
            self.error_message = str(e)
            return False
            
    def run_game(self) -> bool:
        """Запуск игры"""
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
            
            logger.info("=== ИГРА ЗАВЕРШЕНА ===")
            return True
            
        except KeyboardInterrupt:
            logger.info("Игра прервана пользователем")
            return True
            
        except Exception as e:
            logger.error(f"✗ Критическая ошибка: {e}")
            self.error_occurred = True
            self.error_message = str(e)
            return False
            
    def _run_ui(self):
        """Запуск UI в отдельном потоке"""
        try:
            if self.main_window:
                self.main_window.run()
        except Exception as e:
            logger.error(f"Ошибка в UI потоке: {e}")
            self.error_occurred = True
            self.error_message = str(e)
            
    def show_error_dialog(self):
        """Показ диалога с ошибкой"""
        if self.error_occurred and self.error_message:
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()  # Скрываем основное окно
                
                messagebox.showerror(
                    "Ошибка запуска игры",
                    f"Произошла ошибка при запуске игры:\n\n{self.error_message}\n\n"
                    "Проверьте логи в файле game_ui.log для получения дополнительной информации."
                )
                
                root.destroy()
                
            except Exception as e:
                logger.error(f"Не удалось показать диалог ошибки: {e}")
                print(f"ОШИБКА: {self.error_message}")


def check_system_requirements() -> bool:
    """Проверка системных требований"""
    logger.info("Проверка системных требований...")
    
    try:
        # Проверяем версию Python
        if sys.version_info < (3, 7):
            logger.error("Требуется Python 3.7 или выше")
            return False
            
        # Проверяем необходимые модули
        required_modules = ['tkinter', 'json', 'sqlite3', 'threading']
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                logger.error(f"Модуль {module} не найден")
                return False
                
        # Проверяем доступ к файловой системе
        if not Path('.').exists():
            logger.error("Нет доступа к текущей директории")
            return False
            
        logger.info("✓ Системные требования выполнены")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка проверки системных требований: {e}")
        return False


def create_backup():
    """Создание резервной копии важных файлов"""
    try:
        logger.info("Создание резервной копии...")
        
        backup_dir = Path('backup')
        backup_dir.mkdir(exist_ok=True)
        
        important_files = [
            'data/game_data.db',
            'data/game_settings.json',
            'data/difficulty_settings.json',
            'data/ui_settings.json',
            'data/graphics_settings.json',
            'data/audio_settings.json',
            'data/ai_settings.json',
            'data/combat_settings.json',
            'data/inventory_settings.json'
        ]
        
        for file_path in important_files:
            source = Path(file_path)
            if source.exists():
                backup_path = backup_dir / f"{source.name}.backup"
                import shutil
                shutil.copy2(source, backup_path)
                
        logger.info("✓ Резервная копия создана")
        
    except Exception as e:
        logger.warning(f"Не удалось создать резервную копию: {e}")


def main():
    """Главная функция запуска"""
    start_time = time.time()
    
    try:
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
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        logger.info("=== ЗАВЕРШЕНИЕ РАБОТЫ ===")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
