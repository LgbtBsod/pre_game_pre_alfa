"""Примеры использования основных компонентов игры."""

import sys
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.entity_factory import EntityFactory
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from core.component import ComponentManager
from core.attributes import AttributesComponent
from core.combat_stats import CombatStatsComponent
from core.inventory import InventoryComponent
from core.transform import TransformComponent
from core.skill_system import SkillSystem
from core.leveling_system import LevelingSystem
from config.game_constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, BACKGROUND,
    ENEMY_COUNT_EASY, ENEMY_LEVEL_MIN_EASY, ENEMY_LEVEL_MAX_EASY,
    ENEMY_COUNT_NORMAL, ENEMY_LEVEL_MIN_NORMAL, ENEMY_LEVEL_MAX_NORMAL,
    ENEMY_COUNT_HARD, ENEMY_LEVEL_MIN_HARD, ENEMY_LEVEL_MAX_HARD,
    BOSS_LEVEL_EASY, BOSS_LEVEL_NORMAL, BOSS_LEVEL_HARD,
    BASE_DAMAGE, CRITICAL_MULTIPLIER, PLAYER_BASE_HEALTH
)
from utils.game_utils import (
    calculate_distance, normalize_vector, clamp_value,
    interpolate_values, random_point_in_circle, rgb_to_hex,
    format_time, format_number
)


def example_entity_creation():
    """Пример создания сущностей через EntityFactory"""
    logger.info("=== Создание сущностей ===")
    
    # Создание игрока
    player = EntityFactory.create_player("player_1", (100, 100))
    logger.info(f"Создан игрок: {player.id} на позиции {player.position}")
    
    # Создание врага
    enemy = EntityFactory.create_enemy(level=5, position=(200, 200))
    logger.info(f"Создан враг уровня {enemy.level} на позиции {enemy.position}")
    
    # Создание босса
    boss = EntityFactory.create_boss(level=15, position=(300, 300))
    logger.info(f"Создан босс уровня {boss.level} на позиции {boss.position}")
    
    # Создание группы врагов
    enemy_pack = EntityFactory.create_enemy_pack(
        pack_size=3, 
        level=3, 
        center_position=(400, 400)
    )
    logger.info(f"Создана группа из {len(enemy_pack)} врагов")
    
    # Создание босса с миньонами
    boss_with_minions = EntityFactory.create_boss_with_minions(
        boss_level=20, 
        minion_count=5, 
        center_position=(500, 500)
    )
    boss, minions = boss_with_minions
    logger.info(f"Создан босс уровня {boss.level} с {len(minions)} миньонами")
    
    return player, enemy, boss, enemy_pack, boss_with_minions


def example_component_usage():
    """Пример работы с компонентами"""
    logger.info("\n=== Работа с компонентами ===")
    
    # Создаем сущность
    entity = EntityFactory.create_player("test_entity", (0, 0))
    
    # Работа с атрибутами
    entity.set_attribute_base("strength", 15)
    entity.set_attribute_base("agility", 12)
    entity.set_attribute_bonus("strength", 5)
    
    logger.info(f"Сила: {entity.get_attribute('strength')} (база: 15, бонус: 5)")
    logger.info(f"Ловкость: {entity.get_attribute('agility')} (база: 12)")
    
    # Работа с боевыми характеристиками
    entity.set_health(80)
    entity.set_max_health(100)
    entity.set_mana(50)
    entity.set_max_mana(80)
    
    logger.info(f"Здоровье: {entity.get_health()}/{entity.get_max_health()}")
    logger.info(f"Мана: {entity.get_mana()}/{entity.get_max_mana()}")
    
    # Работа с инвентарем
    entity.add_item("sword", {"type": "weapon", "damage": 25})
    entity.add_item("potion", {"type": "consumable", "heal": 30})
    
    logger.info(f"Предметы в инвентаре: {list(entity.get_inventory().keys())}")
    
    return entity


def example_utility_functions():
    """Пример использования утилит"""
    logger.info("\n=== Использование утилит ===")
    
    # Математические функции
    point1 = (0, 0)
    point2 = (3, 4)
    distance = calculate_distance(point1, point2)
    logger.info(f"Расстояние между {point1} и {point2}: {distance}")
    
    # Векторные операции
    vector = (5, 12)
    normalized = normalize_vector(vector)
    logger.info(f"Вектор {vector} нормализован: {normalized}")
    
    # Ограничение значений
    clamped = clamp_value(150, 0, 100)
    logger.info(f"150 ограничено до [0, 100]: {clamped}")
    
    # Плавная интерполяция
    interpolated = interpolate_values(0, 100, 0.5)
    logger.info(f"Интерполяция от 0 до 100 с фактором 0.5: {interpolated}")
    
    # Случайные точки
    circle_point = random_point_in_circle((0, 0), 10)
    logger.info(f"Случайная точка в круге радиусом 10: {circle_point}")
    
    # Цветовые операции
    color = (255, 128, 64)
    hex_color = rgb_to_hex(color)
    logger.info(f"RGB {color} в HEX: {hex_color}")
    
    # Форматирование
    formatted_time = format_time(3661)  # 1 час 1 минута 1 секунда
    logger.info(f"3661 секунд = {formatted_time}")
    
    formatted_number = format_number(1234567)
    logger.info(f"1234567 = {formatted_number}")


def example_game_constants():
    """Пример использования констант игры"""
    logger.info("\n=== Константы игры ===")
    
    logger.info(f"Размер окна: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    logger.info(f"Размер тайла карты: {TILE_SIZE}")
    logger.info(f"Цвет фона: {BACKGROUND}")
    
    logger.info(f"Настройки сложности:")
    logger.info(f"  Легкая: {ENEMY_COUNT_EASY} врагов, уровни {ENEMY_LEVEL_MIN_EASY}-{ENEMY_LEVEL_MAX_EASY}")
    logger.info(f"  Нормальная: {ENEMY_COUNT_NORMAL} врагов, уровни {ENEMY_LEVEL_MIN_NORMAL}-{ENEMY_LEVEL_MAX_NORMAL}")
    logger.info(f"  Сложная: {ENEMY_COUNT_HARD} врагов, уровни {ENEMY_LEVEL_MIN_HARD}-{ENEMY_LEVEL_MAX_HARD}")
    
    logger.info(f"Уровни боссов:")
    logger.info(f"  Легкий: {BOSS_LEVEL_EASY}")
    logger.info(f"  Нормальный: {BOSS_LEVEL_NORMAL}")
    logger.info(f"  Сложный: {BOSS_LEVEL_HARD}")
    
    logger.info(f"Боевые параметры:")
    logger.info(f"  Базовый урон: {BASE_DAMAGE}")
    logger.info(f"  Критический множитель: {CRITICAL_MULTIPLIER}")
    logger.info(f"  Базовое здоровье игрока: {PLAYER_BASE_HEALTH}")


def example_effect_system():
    """Пример работы с системой эффектов"""
    logger.info("\n=== Система эффектов ===")
    
    # Создаем сущность
    entity = EntityFactory.create_player("test_entity", (0, 0))
    entity.set_attribute_base("strength", 10)
    
    logger.info(f"Исходная сила: {entity.get_attribute('strength')}")
    
    # Добавляем эффект увеличения силы
    strength_effect = {
        "type": "attribute_modifier",
        "target": "strength",
        "value": 5,
        "duration": 10.0,
        "description": "Зелье силы"
    }
    
    entity.add_effect(strength_effect)
    logger.info(f"Сила после эффекта: {entity.get_attribute('strength')}")
    
    # Обновляем эффекты (симуляция времени)
    entity.update_effects(5.0)  # Прошло 5 секунд
    logger.info(f"Сила через 5 секунд: {entity.get_attribute('strength')}")
    
    # Обновляем эффекты еще раз (эффект должен исчезнуть)
    entity.update_effects(10.0)  # Прошло еще 10 секунд
    logger.info(f"Сила после истечения эффекта: {entity.get_attribute('strength')}")


def main():
    """Главная функция с примерами"""
    logger.info("Демонстрация возможностей автономного ИИ-выживальщика")
    logger.info("=" * 60)
    
    try:
        # Запускаем все примеры
        example_entity_creation()
        example_component_usage()
        example_utility_functions()
        example_game_constants()
        example_effect_system()
        
        logger.info("\n" + "=" * 60)
        logger.info("Все примеры выполнены успешно!")
        
    except Exception as e:
        logger.error(f"\nОшибка при выполнении примеров: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
