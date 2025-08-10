"""
Тест базовых систем игры без UI
"""

import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Импорт основных систем
from config.settings_manager import settings_manager
from core.data_types import data_manager
from core.game_state_manager import game_state_manager
from entities.entity_factory import entity_factory
from items.item_manager import item_manager
from ai.ai_manager import ai_manager
from utils.entity_id_generator import generate_short_entity_id, EntityType


def test_basic_systems():
    """Тест базовых систем"""
    logger.info("=== Тест базовых систем ===")

    try:
        # Загружаем настройки
        settings_manager.reload_settings()
        logger.info("✓ Настройки загружены")

        # Загружаем данные
        data_manager.load_all_data()
        logger.info("✓ Данные загружены")

        # Тестируем генерацию hex ID
        player_id = generate_short_entity_id(EntityType.PLAYER)
        enemy_id = generate_short_entity_id(EntityType.ENEMY)
        item_id = generate_short_entity_id(EntityType.ITEM)

        logger.info(f"✓ Сгенерированы hex ID: {player_id}, {enemy_id}, {item_id}")

        # Создаем игрока
        player = entity_factory.create_player("test_player", (0, 0))
        logger.info(f"✓ Создан игрок: {player.entity_id}")

        # Регистрируем в AI системе
        from ai.ai_core import AICore

        ai_core = AICore(player)
        success = ai_manager.register_entity(player, ai_core)
        logger.info(f"✓ Игрок зарегистрирован в AI: {success}")

        # Создаем врага
        enemy = entity_factory.create_enemy(level=5, position=(100, 100))
        logger.info(f"✓ Создан враг: {enemy.entity_id}")

        # Регистрируем врага в AI
        enemy_ai_core = AICore(enemy)
        success = ai_manager.register_entity(enemy, enemy_ai_core)
        logger.info(f"✓ Враг зарегистрирован в AI: {success}")

        # Тестируем получение данных
        player_data = data_manager.get_entity("plr_00000000")
        if player_data:
            logger.info(f"✓ Получены данные игрока: {player_data.name}")

        # Тестируем AI обновление
        ai_manager.update(0.016)  # 60 FPS
        logger.info("✓ AI обновление выполнено")

        logger.info("=== Все тесты пройдены успешно ===")
        return True

    except Exception as e:
        logger.error(f"✗ Ошибка в тесте: {e}")
        return False


if __name__ == "__main__":
    success = test_basic_systems()
    if success:
        print("Все системы работают корректно!")
    else:
        print("Обнаружены проблемы в системах!")
