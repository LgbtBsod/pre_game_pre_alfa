"""
Примеры использования новых возможностей проекта.

Этот файл демонстрирует, как использовать:
- EntityFactory для создания сущностей
- Компонентную систему
- Новые утилиты
- Константы игры
"""

from entities.entity_factory import EntityFactory
from entities.entity_refactored import Entity
from config.game_constants import *
from utils.game_utils import *


def example_entity_creation():
    """Пример создания сущностей через EntityFactory"""
    print("=== Создание сущностей ===")
    
    # Создание игрока
    player = EntityFactory.create_player("player_1", (100, 100))
    print(f"Создан игрок: {player.id} на позиции {player.position}")
    
    # Создание врага
    enemy = EntityFactory.create_enemy(level=5, position=(200, 200))
    print(f"Создан враг уровня {enemy.level} на позиции {enemy.position}")
    
    # Создание босса
    boss = EntityFactory.create_boss(level=15, position=(300, 300))
    print(f"Создан босс уровня {boss.level} на позиции {boss.position}")
    
    # Создание группы врагов
    enemy_pack = EntityFactory.create_enemy_pack(
        pack_size=3, 
        level=3, 
        center_position=(400, 400)
    )
    print(f"Создана группа из {len(enemy_pack)} врагов")
    
    # Создание босса с миньонами
    boss_with_minions = EntityFactory.create_boss_with_minions(
        boss_level=20, 
        minion_count=5, 
        center_position=(500, 500)
    )
    boss, minions = boss_with_minions
    print(f"Создан босс уровня {boss.level} с {len(minions)} миньонами")
    
    return player, enemy, boss, enemy_pack, boss_with_minions


def example_component_usage():
    """Пример работы с компонентами"""
    print("\n=== Работа с компонентами ===")
    
    # Создаем сущность
    entity = Entity("test_entity", (0, 0))
    
    # Работа с атрибутами
    entity.set_attribute_base("strength", 15)
    entity.set_attribute_base("agility", 12)
    entity.set_attribute_bonus("strength", 5)
    
    print(f"Сила: {entity.get_attribute('strength')} (база: 15, бонус: 5)")
    print(f"Ловкость: {entity.get_attribute('agility')} (база: 12)")
    
    # Работа с боевыми характеристиками
    entity.set_health(80)
    entity.set_max_health(100)
    entity.set_mana(50)
    entity.set_max_mana(80)
    
    print(f"Здоровье: {entity.get_health()}/{entity.get_max_health()}")
    print(f"Мана: {entity.get_mana()}/{entity.get_max_mana()}")
    
    # Работа с инвентарем
    entity.add_item("sword", {"type": "weapon", "damage": 25})
    entity.add_item("potion", {"type": "consumable", "heal": 30})
    
    print(f"Предметы в инвентаре: {list(entity.get_inventory().keys())}")
    
    return entity


def example_utility_functions():
    """Пример использования утилит"""
    print("\n=== Использование утилит ===")
    
    # Математические функции
    point1 = (0, 0)
    point2 = (3, 4)
    distance = distance(point1, point2)
    print(f"Расстояние между {point1} и {point2}: {distance}")
    
    # Векторные операции
    vector = (5, 12)
    normalized = normalize_vector(vector)
    print(f"Вектор {vector} нормализован: {normalized}")
    
    # Ограничение значений
    clamped = clamp(150, 0, 100)
    print(f"150 ограничено до [0, 100]: {clamped}")
    
    # Плавная интерполяция
    interpolated = lerp(0, 100, 0.5)
    print(f"Интерполяция от 0 до 100 с фактором 0.5: {interpolated}")
    
    # Случайные точки
    circle_point = random_point_in_circle((0, 0), 10)
    print(f"Случайная точка в круге радиусом 10: {circle_point}")
    
    # Цветовые операции
    color = (255, 128, 64)
    hex_color = rgb_to_hex(color)
    print(f"RGB {color} в HEX: {hex_color}")
    
    # Форматирование
    formatted_time = format_time(3661)  # 1 час 1 минута 1 секунда
    print(f"3661 секунд = {formatted_time}")
    
    formatted_number = format_number(1234567)
    print(f"1234567 = {formatted_number}")


def example_game_constants():
    """Пример использования констант игры"""
    print("\n=== Константы игры ===")
    
    print(f"Размер окна: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    print(f"Размер тайла карты: {TILE_SIZE}")
    print(f"Цвет фона: {BACKGROUND}")
    
    print(f"Настройки сложности:")
    print(f"  Легкая: {ENEMY_COUNT_EASY} врагов, уровни {ENEMY_LEVEL_MIN_EASY}-{ENEMY_LEVEL_MAX_EASY}")
    print(f"  Нормальная: {ENEMY_COUNT_NORMAL} врагов, уровни {ENEMY_LEVEL_MIN_NORMAL}-{ENEMY_LEVEL_MAX_NORMAL}")
    print(f"  Сложная: {ENEMY_COUNT_HARD} врагов, уровни {ENEMY_LEVEL_MIN_HARD}-{ENEMY_LEVEL_MAX_HARD}")
    
    print(f"Уровни боссов:")
    print(f"  Легкий: {BOSS_LEVEL_EASY}")
    print(f"  Нормальный: {BOSS_LEVEL_NORMAL}")
    print(f"  Сложный: {BOSS_LEVEL_HARD}")
    
    print(f"Боевые параметры:")
    print(f"  Базовый урон: {BASE_DAMAGE}")
    print(f"  Критический множитель: {CRITICAL_MULTIPLIER}")
    print(f"  Базовое здоровье игрока: {PLAYER_BASE_HEALTH}")


def example_effect_system():
    """Пример работы с системой эффектов"""
    print("\n=== Система эффектов ===")
    
    # Создаем сущность
    entity = Entity("test_entity", (0, 0))
    entity.set_attribute_base("strength", 10)
    
    print(f"Исходная сила: {entity.get_attribute('strength')}")
    
    # Добавляем эффект увеличения силы
    strength_effect = {
        "type": "attribute_modifier",
        "target": "strength",
        "value": 5,
        "duration": 10.0,
        "description": "Зелье силы"
    }
    
    entity.add_effect(strength_effect)
    print(f"Сила после эффекта: {entity.get_attribute('strength')}")
    
    # Обновляем эффекты (симуляция времени)
    entity.update_effects(5.0)  # Прошло 5 секунд
    print(f"Сила через 5 секунд: {entity.get_attribute('strength')}")
    
    # Обновляем эффекты еще раз (эффект должен исчезнуть)
    entity.update_effects(10.0)  # Прошло еще 10 секунд
    print(f"Сила после истечения эффекта: {entity.get_attribute('strength')}")


def main():
    """Главная функция с примерами"""
    print("Демонстрация возможностей автономного ИИ-выживальщика")
    print("=" * 60)
    
    try:
        # Запускаем все примеры
        example_entity_creation()
        example_component_usage()
        example_utility_functions()
        example_game_constants()
        example_effect_system()
        
        print("\n" + "=" * 60)
        print("Все примеры выполнены успешно!")
        
    except Exception as e:
        print(f"\nОшибка при выполнении примеров: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
