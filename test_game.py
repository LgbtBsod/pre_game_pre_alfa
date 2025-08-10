"""
Упрощенная версия игры для тестирования.
"""

import sys
import logging
import time
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Импорт основных систем
from config.settings_manager import settings_manager
from entities.player import Player
from entities.enemy import Enemy
from entities.entity_factory import EntityFactory

def test_entities():
    """Тестирует создание и взаимодействие сущностей"""
    logger.info("=== Тестирование сущностей ===")
    
    # Создаем фабрику
    factory = EntityFactory()
    
    # Создаем игрока
    logger.info("Создание игрока...")
    player = factory.create_player("test_player", (0, 0))
    logger.info(f"Игрок создан: {player.name}, уровень: {player.level}")
    logger.info(f"Здоровье: {player.health}/{player.max_health}")
    logger.info(f"Атрибуты: {player.attribute_manager.get_attribute_summary()}")
    
    # Создаем врага
    logger.info("Создание врага...")
    enemy = factory.create_enemy("warrior", 1, (100, 0))
    logger.info(f"Враг создан: {enemy.enemy_type}, уровень: {enemy.level}")
    logger.info(f"Здоровье: {enemy.health}/{enemy.max_health}")
    
    # Тестируем бой
    logger.info("=== Тестирование боя ===")
    
    # Игрок атакует врага
    logger.info("Игрок атакует врага...")
    damage_report = player.attack(enemy)
    if damage_report:
        logger.info(f"Урон: {damage_report.get('damage', 0)}")
        logger.info(f"Здоровье врага: {enemy.health}/{enemy.max_health}")
    
    # Враг атакует игрока
    logger.info("Враг атакует игрока...")
    damage_report = enemy.attack(player)
    if damage_report:
        logger.info(f"Урон: {damage_report.get('damage', 0)}")
        logger.info(f"Здоровье игрока: {player.health}/{player.max_health}")
    
    # Тестируем AI
    logger.info("=== Тестирование AI ===")
    
    # Игрок использует предметы
    logger.info("Игрок использует предметы интеллектуально...")
    player.use_item_intelligently()
    
    # Враг принимает решения
    logger.info("Враг принимает решения...")
    enemy.update_ai(0.1)  # Обновляем AI на 0.1 секунды
    
    # Тестируем обучение
    logger.info("=== Тестирование обучения ===")
    
    # Игрок получает опыт
    logger.info("Игрок получает опыт...")
    player.gain_experience(50)
    logger.info(f"Уровень игрока: {player.level}, опыт: {player.experience}")
    
    # Проверяем улучшения AI
    logger.info(f"Мастерство оружия: {player.weapon_mastery}")
    logger.info(f"Опыт в бою: {player.combat_experience}")
    
    logger.info("=== Тестирование завершено ===")

def test_ai_systems():
    """Тестирует AI системы"""
    logger.info("=== Тестирование AI систем ===")
    
    # Создаем игрока
    player = Player((0, 0))
    
    # Тестируем память
    logger.info("Тестирование памяти...")
    player.ai_memory.store_experience("test_event", {"value": 42})
    recent_events = player.ai_memory.get_recent_events("test_event", 5)
    logger.info(f"События в памяти: {len(recent_events)}")
    
    # Тестируем принятие решений
    logger.info("Тестирование принятия решений...")
    decision = player.decision_maker.make_combat_decision(None, 100)
    logger.info(f"Решение: {decision}")
    
    # Тестируем распознавание паттернов
    logger.info("Тестирование распознавания паттернов...")
    player.pattern_recognizer.analyze_damage_pattern({
        "damage": 15,
        "damage_type": "physical",
        "attacker_type": "enemy"
    })
    
    logger.info("=== AI системы протестированы ===")

def main():
    """Главная функция тестирования"""
    logger.info("Запуск тестирования игры...")
    
    try:
        # Загружаем настройки
        settings_manager.reload_settings()
        logger.info("Настройки загружены")
        
        # Тестируем сущности
        test_entities()
        
        # Тестируем AI системы
        test_ai_systems()
        
        logger.info("Все тесты пройдены успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
