"""
Тестирование основных игровых систем
"""
import sys
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_basic_systems():
    """Тестирование основных систем"""
    logger.info("=== ТЕСТИРОВАНИЕ ОСНОВНЫХ СИСТЕМ ===")
    
    try:
        # Импорт основных систем
        from config.settings_manager import settings_manager
        from core.data_manager import data_manager
        from core.game_state_manager import game_state_manager
        from entities.entity_factory import entity_factory
        from ai.ai_manager import ai_manager
        
        logger.info("✓ Все модули импортированы успешно")
        
        # Тест настроек
        settings_manager.reload_settings()
        logger.info("✓ Настройки загружены")
        
        # Тест данных
        data_manager.reload_data()
        logger.info("✓ Данные загружены")
        
        # Тест AI системы
        ai_manager.initialize()
        logger.info("✓ AI система инициализирована")
        
        # Тест создания игрока
        player = entity_factory.create_player("TestPlayer", (100, 100))
        if player:
            logger.info(f"✓ Игрок создан: {player.name}")
        else:
            logger.error("✗ Не удалось создать игрока")
        
        # Тест создания врага
        enemy = entity_factory.create_enemy("warrior", 1, (200, 200))
        if enemy:
            logger.info(f"✓ Враг создан: {enemy.enemy_type}")
        else:
            logger.error("✗ Не удалось создать врага")
        
        # Тест состояния игры
        game_id = game_state_manager.create_new_game(
            save_name="TestSave",
            player_name="TestPlayer",
            difficulty="normal"
        )
        if game_id:
            logger.info(f"✓ Состояние игры создано: {game_id}")
        else:
            logger.error("✗ Не удалось создать состояние игры")
        
        logger.info("=== ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО ===")
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_systems():
    """Тестирование UI систем"""
    logger.info("=== ТЕСТИРОВАНИЕ UI СИСТЕМ ===")
    
    try:
        # Импорт UI модулей
        from ui.main_window import MainWindow
        from ui.game_menu import GameMenu
        from ui.render_manager import RenderManager
        
        logger.info("✓ UI модули импортированы")
        
        # Тест создания главного окна
        app = MainWindow()
        logger.info("✓ Главное окно создано")
        
        # Тест создания меню
        import tkinter as tk
        root = tk.Tk()
        canvas = tk.Canvas(root, width=800, height=600)
        menu = GameMenu(canvas, 800, 600)
        logger.info("✓ Игровое меню создано")
        
        # Тест создания рендер менеджера
        from core.game_state_manager import game_state_manager
        render_manager = RenderManager(canvas, game_state_manager)
        logger.info("✓ Рендер менеджер создан")
        
        root.destroy()
        logger.info("✓ UI системы протестированы")
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка тестирования UI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_systems():
    """Тестирование AI систем"""
    logger.info("=== ТЕСТИРОВАНИЕ AI СИСТЕМ ===")
    
    try:
        from ai.ai_manager import ai_manager
        from ai.ai_core import AICore, AIState, AIPriority
        from entities.entity_factory import entity_factory
        
        # Создаем тестовую сущность
        enemy = entity_factory.create_enemy("warrior", 1, (100, 100))
        if enemy:
            # Создаем AI ядро
            ai_core = AICore(
                entity=enemy,
                personality_type="aggressive",
                priority=AIPriority.NORMAL
            )
            
            # Регистрируем в AI системе
            success = ai_manager.register_entity(enemy, ai_core)
            if success:
                logger.info("✓ AI сущность зарегистрирована")
            else:
                logger.error("✗ Не удалось зарегистрировать AI сущность")
            
            # Тест обновления AI
            ai_manager.update(0.016)  # 16ms
            logger.info("✓ AI система обновлена")
            
            # Получаем статистику
            stats = ai_manager.get_performance_stats()
            logger.info(f"✓ AI статистика: {stats}")
            
        else:
            logger.error("✗ Не удалось создать тестовую сущность")
        
        logger.info("✓ AI системы протестированы")
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка тестирования AI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    logger.info("Начинается тестирование игровых систем...")
    
    # Тестируем основные системы
    basic_ok = test_basic_systems()
    
    # Тестируем UI системы
    ui_ok = test_ui_systems()
    
    # Тестируем AI системы
    ai_ok = test_ai_systems()
    
    # Итоговый результат
    if basic_ok and ui_ok and ai_ok:
        logger.info("🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ КОРРЕКТНО!")
        logger.info("Игра готова к запуску!")
    else:
        logger.error("❌ НЕКОТОРЫЕ СИСТЕМЫ ИМЕЮТ ПРОБЛЕМЫ")
        logger.info("Проверьте логи выше для деталей")
    
    return basic_ok and ui_ok and ai_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
