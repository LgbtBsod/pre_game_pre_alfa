"""
Простой тест базовой функциональности.
"""

import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_basic_imports():
    """Тестирует базовые импорты"""
    logger.info("=== Тестирование базовых импортов ===")
    
    try:
        # Тестируем импорт настроек
        from config.settings_manager import settings_manager
        logger.info("✅ Настройки импортированы")
        
        # Тестируем импорт атрибутов
        from core.attributes import AttributeManager, Attribute
        logger.info("✅ Атрибуты импортированы")
        
        # Тестируем импорт боевых характеристик
        from core.combat_stats import CombatStatsManager, CombatStats
        logger.info("✅ Боевые характеристики импортированы")
        
        # Тестируем импорт инвентаря
        from core.inventory import InventoryManager, Inventory, Equipment
        logger.info("✅ Инвентарь импортирован")
        
        # Тестируем импорт базовой сущности
        from entities.base_entity import BaseEntity
        logger.info("✅ Базовая сущность импортирована")
        
        # Тестируем импорт игрока
        from entities.player import Player
        logger.info("✅ Игрок импортирован")
        
        # Тестируем импорт врага
        from entities.enemy import Enemy
        logger.info("✅ Враг импортирован")
        
        logger.info("=== Все импорты успешны ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        return False

def test_basic_creation():
    """Тестирует создание базовых объектов"""
    logger.info("=== Тестирование создания объектов ===")
    
    try:
        # Создаем атрибуты
        from core.attributes import AttributeManager
        attr_manager = AttributeManager()
        attr_manager.initialize_default_attributes()
        logger.info("✅ Менеджер атрибутов создан")
        
        # Создаем боевые характеристики
        from core.combat_stats import CombatStatsManager
        combat_manager = CombatStatsManager()
        logger.info("✅ Менеджер боевых характеристик создан")
        
        # Создаем инвентарь
        from core.inventory import InventoryManager
        inv_manager = InventoryManager()
        logger.info("✅ Менеджер инвентаря создан")
        
        # Создаем базовую сущность
        from entities.base_entity import BaseEntity
        entity = BaseEntity("test_entity", (0, 0))
        logger.info("✅ Базовая сущность создана")
        
        # Создаем игрока
        from entities.player import Player
        player = Player((0, 0))
        logger.info("✅ Игрок создан")
        
        # Создаем врага
        from entities.enemy import Enemy
        enemy = Enemy("warrior", 1, (100, 0))
        logger.info("✅ Враг создан")
        
        logger.info("=== Все объекты созданы успешно ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_interaction():
    """Тестирует базовое взаимодействие"""
    logger.info("=== Тестирование взаимодействия ===")
    
    try:
        # Создаем игрока и врага
        from entities.player import Player
        from entities.enemy import Enemy
        
        player = Player((0, 0))
        enemy = Enemy("warrior", 1, (100, 0))
        
        logger.info(f"Игрок: здоровье {player.health}/{player.max_health}")
        logger.info(f"Враг: здоровье {enemy.health}/{enemy.max_health}")
        
        # Игрок атакует врага
        damage_report = player.attack(enemy)
        if damage_report:
            logger.info(f"Игрок нанес {damage_report.get('damage', 0)} урона")
            logger.info(f"Враг: здоровье {enemy.health}/{enemy.max_health}")
        
        # Враг атакует игрока
        damage_report = enemy.attack(player)
        if damage_report:
            logger.info(f"Враг нанес {damage_report.get('damage', 0)} урона")
            logger.info(f"Игрок: здоровье {player.health}/{player.max_health}")
        
        logger.info("=== Взаимодействие протестировано ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка взаимодействия: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    logger.info("🚀 Запуск простого тестирования...")
    
    # Тестируем импорты
    if not test_basic_imports():
        logger.error("❌ Тест импортов провален")
        return
    
    # Тестируем создание
    if not test_basic_creation():
        logger.error("❌ Тест создания провален")
        return
    
    # Тестируем взаимодействие
    if not test_basic_interaction():
        logger.error("❌ Тест взаимодействия провален")
        return
    
    logger.info("🎉 Все тесты пройдены успешно!")
    logger.info("🎮 Игра готова к запуску!")

if __name__ == "__main__":
    main()
