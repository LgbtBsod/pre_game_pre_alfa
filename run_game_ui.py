"""
Запуск игры с полноценным UI интерфейсом
"""
import sys
import logging
from pathlib import Path

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


def initialize_game_systems():
    """Инициализация игровых систем"""
    try:
        logger.info("Начинается инициализация игровых систем...")
        
        # Загружаем настройки
        settings_manager.reload_settings()
        logger.info("Настройки загружены")
        
        # Загружаем данные
        data_manager.reload_data()
        logger.info("Данные загружены")
        
        # Инициализируем AI систему
        ai_manager.initialize()
        logger.info("AI система инициализирована")
        
        logger.info("Все системы инициализированы успешно")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка инициализации: {e}")
        return False


def main():
    """Главная функция"""
    try:
        logger.info("Запуск игры с UI интерфейсом...")
        
        # Инициализируем игровые системы
        if not initialize_game_systems():
            logger.error("Не удалось инициализировать игровые системы")
            return
        
        # Создаем и запускаем главное окно
        app = MainWindow()
        logger.info("Главное окно создано, запуск UI...")
        
        # Запускаем UI
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Игра прервана пользователем")
    
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        logger.info("Игра завершена")


if __name__ == "__main__":
    main()
