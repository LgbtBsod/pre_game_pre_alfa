"""
Примеры использования системы 16-ричных ID для сущностей.
Демонстрирует генерацию ID, конвертацию и работу с различными типами сущностей.
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from utils.entity_id_generator import (
    EntityType,
    generate_entity_id,
    generate_short_entity_id,
    convert_legacy_id,
    get_entity_id_stats,
    id_generator,
)


class ExampleEntity:
    """Пример сущности для демонстрации"""

    def __init__(self, name: str, entity_type: EntityType):
        self.name = name
        self.entity_type = entity_type
        self.hex_id = generate_short_entity_id(entity_type)
        self.position = (0, 0)
        self.health = 100
        self.max_health = 100

    def __str__(self):
        return f"{self.name} ({self.hex_id})"


def example_basic_id_generation():
    """Пример базовой генерации ID"""
    print("=== Базовая генерация 16-ричных ID ===")

    # Генерируем ID для разных типов сущностей
    player_id = generate_short_entity_id(EntityType.PLAYER)
    enemy_id = generate_short_entity_id(EntityType.ENEMY)
    boss_id = generate_short_entity_id(EntityType.BOSS)
    item_id = generate_short_entity_id(EntityType.ITEM)
    effect_id = generate_short_entity_id(EntityType.EFFECT)

    print(f"Игрок: {player_id}")
    print(f"Враг: {enemy_id}")
    print(f"Босс: {boss_id}")
    print(f"Предмет: {item_id}")
    print(f"Эффект: {effect_id}")

    # Полные ID объекты
    full_player_id = generate_entity_id(EntityType.PLAYER)
    print(f"Полный ID игрока: {full_player_id}")
    print(f"  - hex_id: {full_player_id.hex_id}")
    print(f"  - timestamp: {full_player_id.timestamp}")
    print(f"  - instance_id: {full_player_id.instance_id}")


def example_entity_creation():
    """Пример создания сущностей с 16-ричными ID"""
    print("\n=== Создание сущностей с 16-ричными ID ===")

    # Создаем различные сущности
    player = ExampleEntity("Главный герой", EntityType.PLAYER)
    warrior = ExampleEntity("Гоблин-воин", EntityType.ENEMY)
    boss = ExampleEntity("Гоблин-вожак", EntityType.BOSS)
    sword = ExampleEntity("Железный меч", EntityType.ITEM)
    heal_effect = ExampleEntity("Исцеление", EntityType.EFFECT)

    entities = [player, warrior, boss, sword, heal_effect]

    print("Созданные сущности:")
    for entity in entities:
        print(f"  {entity}")

    return entities


def example_legacy_id_conversion():
    """Пример конвертации старых ID"""
    print("\n=== Конвертация старых ID ===")

    # Старые ID из JSON файлов
    legacy_ids = [
        ("player_001", EntityType.PLAYER),
        ("enemy_001", EntityType.ENEMY),
        ("boss_001", EntityType.BOSS),
        ("wpn_001", EntityType.ITEM),
        ("str_001", EntityType.EFFECT),
        ("heal_001", EntityType.EFFECT),
    ]

    print("Конвертация старых ID в 16-ричные:")
    for legacy_id, entity_type in legacy_ids:
        new_id = convert_legacy_id(legacy_id, entity_type)
        print(f"  {legacy_id} -> {new_id}")

    # Проверяем уникальность
    converted_ids = set()
    for legacy_id, entity_type in legacy_ids:
        new_id = convert_legacy_id(legacy_id, entity_type)
        if new_id in converted_ids:
            print(f"  ВНИМАНИЕ: Дублированный ID: {new_id}")
        converted_ids.add(new_id)

    print(f"Всего уникальных ID: {len(converted_ids)}")


def example_id_uniqueness():
    """Пример проверки уникальности ID"""
    print("\n=== Проверка уникальности ID ===")

    # Генерируем много ID одного типа
    enemy_ids = []
    for i in range(10):
        enemy_id = generate_short_entity_id(EntityType.ENEMY)
        enemy_ids.append(enemy_id)

    print(f"Сгенерировано {len(enemy_ids)} ID врагов:")
    for i, enemy_id in enumerate(enemy_ids, 1):
        print(f"  {i:2d}. {enemy_id}")

    # Проверяем уникальность
    unique_ids = set(enemy_ids)
    print(f"Уникальных ID: {len(unique_ids)}")

    if len(unique_ids) == len(enemy_ids):
        print("  ✓ Все ID уникальны")
    else:
        print("  ✗ Обнаружены дубликаты")


def example_id_format_analysis():
    """Пример анализа формата ID"""
    print("\n=== Анализ формата ID ===")

    # Генерируем несколько ID для анализа
    ids_to_analyze = []
    for entity_type in EntityType:
        if entity_type != EntityType.AI_ENTITY:  # Пропускаем общий тип
            entity_id = generate_short_entity_id(entity_type)
            ids_to_analyze.append((entity_type, entity_id))

    print("Анализ формата ID:")
    for entity_type, entity_id in ids_to_analyze:
        # Разбираем ID на компоненты
        parts = entity_id.split("_")
        if len(parts) == 2:
            prefix, hex_part = parts
            print(f"  {entity_type.value:8s}: {entity_id}")
            print(f"           Префикс: {prefix}")
            print(f"           Hex часть: {hex_part} ({len(hex_part)} символов)")
            print(f"           Длина ID: {len(entity_id)} символов")
        print()


def example_performance_test():
    """Тест производительности генерации ID"""
    print("\n=== Тест производительности ===")

    import time

    # Тестируем скорость генерации
    num_ids = 1000
    start_time = time.time()

    for i in range(num_ids):
        generate_short_entity_id(EntityType.ENEMY)

    end_time = time.time()
    generation_time = end_time - start_time

    print(f"Сгенерировано {num_ids} ID за {generation_time:.4f} секунд")
    print(f"Скорость: {num_ids / generation_time:.0f} ID/сек")

    # Статистика генератора
    stats = get_entity_id_stats()
    print(f"Общая статистика генератора:")
    print(f"  Всего сгенерировано: {stats['total_generated']}")
    print(f"  Использованных ID: {stats['used_ids_count']}")
    print(f"  Счетчики по типам:")
    for entity_type, count in stats["type_counters"].items():
        print(f"    {entity_type}: {count}")


def example_memory_efficiency():
    """Пример эффективности использования памяти"""
    print("\n=== Эффективность использования памяти ===")

    # Сравниваем размеры старых и новых ID
    old_ids = ["player_001", "enemy_001", "boss_001", "wpn_001", "str_001", "heal_001"]

    new_ids = []
    for old_id in old_ids:
        entity_type = EntityType.ENEMY  # Для примера
        new_id = convert_legacy_id(old_id, entity_type)
        new_ids.append(new_id)

    print("Сравнение размеров ID:")
    total_old_size = 0
    total_new_size = 0

    for old_id, new_id in zip(old_ids, new_ids):
        old_size = len(old_id.encode("utf-8"))
        new_size = len(new_id.encode("utf-8"))
        total_old_size += old_size
        total_new_size += new_size

        print(f"  {old_id:12s} -> {new_id:12s}")
        print(f"    Старый размер: {old_size:2d} байт")
        print(f"    Новый размер:  {new_size:2d} байт")
        print(f"    Разница:       {new_size - old_size:+2d} байт")

    print(f"\nОбщая экономия памяти:")
    print(f"  Старые ID: {total_old_size} байт")
    print(f"  Новые ID:  {total_new_size} байт")
    print(f"  Разница:   {total_new_size - total_old_size:+d} байт")

    if total_new_size < total_old_size:
        print(f"  ✓ Экономия: {total_old_size - total_new_size} байт")
    else:
        print(f"  ✗ Перерасход: {total_new_size - total_old_size} байт")


def main():
    """Основная функция с примерами"""
    print("=== Примеры использования системы 16-ричных ID ===")

    # Запускаем все примеры
    example_basic_id_generation()
    entities = example_entity_creation()
    example_legacy_id_conversion()
    example_id_uniqueness()
    example_id_format_analysis()
    example_performance_test()
    example_memory_efficiency()

    print("\n=== Заключение ===")
    print("Система 16-ричных ID обеспечивает:")
    print("  ✓ Уникальную идентификацию всех сущностей")
    print("  ✓ Эффективное использование памяти")
    print("  ✓ Простоту хранения и обработки")
    print("  ✓ Масштабируемость для больших проектов")
    print("  ✓ Обратную совместимость через конвертер")


if __name__ == "__main__":
    main()
