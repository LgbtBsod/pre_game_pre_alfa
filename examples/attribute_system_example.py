"""
Пример использования новой системы атрибутов.
Демонстрирует работу с шаблонами из JSON и индивидуальными атрибутами в БД.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.entity_attribute_manager import entity_attribute_manager
from entities.base_entity import BaseEntity
from entities.player import Player
from entities.enemy import Enemy


def demonstrate_attribute_system():
    """Демонстрирует работу системы атрибутов"""
    print("=== Демонстрация системы атрибутов ===\n")
    
    # 1. Создание сущности с атрибутами из шаблонов
    print("1. Создание игрока с атрибутами из шаблонов:")
    
    # Шаблоны атрибутов для игрока
    player_attributes = {
        "str_001": 15.0,  # Сила - выше базовой
        "dex_001": 12.0,  # Ловкость - немного выше
        "int_001": 18.0,  # Интеллект - высокий
        "vit_001": 14.0,  # Живучесть - выше базовой
        "end_001": 11.0,  # Выносливость - базовая
        "fai_001": 16.0,  # Вера - высокий
        "luc_001": 13.0   # Удача - выше базовой
    }
    
    # Создаем игрока с атрибутами
    player = Player("test_player_001", (100, 100), player_attributes)
    
    print(f"   Игрок создан: {player.name}")
    print(f"   Атрибуты загружены: {len(player.attribute_manager.attributes)}")
    
    # Показываем атрибуты
    for attr_id, attr in player.attribute_manager.attributes.items():
        print(f"   {attr_id}: {attr.current}/{attr.maximum} (рост: {attr.growth_rate})")
    
    print(f"   Скорость обучения: {player.learning_rate}")
    print(f"   Скорость забывания: {player.memory_decay_rate}")
    print(f"   Порог распознавания: {player.pattern_recognition_threshold}")
    
    # 2. Сохранение атрибутов в БД
    print("\n2. Сохранение атрибутов в базу данных:")
    player.save_attributes()
    print("   Атрибуты сохранены в БД")
    
    # 3. Создание врага с другими атрибутами
    print("\n3. Создание врага с атрибутами:")
    
    enemy_attributes = {
        "str_001": 20.0,  # Сила - очень высокая
        "dex_001": 8.0,   # Ловкость - низкая
        "vit_001": 25.0,  # Живучесть - очень высокая
        "end_001": 18.0   # Выносливость - высокая
    }
    
    enemy = Enemy("test_enemy_001", (200, 200), enemy_attributes)
    
    print(f"   Враг создан: {enemy.name}")
    print(f"   Атрибуты загружены: {len(enemy.attribute_manager.attributes)}")
    
    # Показываем атрибуты врага
    for attr_id, attr in enemy.attribute_manager.attributes.items():
        print(f"   {attr_id}: {attr.current}/{attr.maximum} (рост: {attr.growth_rate})")
    
    print(f"   Скорость обучения: {enemy.learning_rate}")
    
    # Сохраняем врага
    enemy.save_attributes()
    print("   Атрибуты врага сохранены в БД")
    
    # 4. Загрузка атрибутов из БД
    print("\n4. Загрузка атрибутов из базы данных:")
    
    # Создаем нового игрока без атрибутов
    new_player = Player("test_player_001", (300, 300))
    
    # Загружаем атрибуты из БД
    new_player.load_attributes()
    
    print(f"   Игрок загружен: {new_player.name}")
    print(f"   Атрибуты восстановлены: {len(new_player.attribute_manager.attributes)}")
    
    # Проверяем, что атрибуты загрузились
    for attr_id, attr in new_player.attribute_manager.attributes.items():
        print(f"   {attr_id}: {attr.current}/{attr.maximum}")
    
    print(f"   Скорость обучения: {new_player.learning_rate}")
    
    # 5. Изменение AI атрибутов
    print("\n5. Изменение AI атрибутов:")
    
    print(f"   Исходная скорость обучения: {new_player.learning_rate}")
    
    # Увеличиваем скорость обучения
    new_player.set_ai_attribute("learning_rate", 0.25)
    print(f"   Новая скорость обучения: {new_player.learning_rate}")
    
    # Устанавливаем другие AI атрибуты
    new_player.set_ai_attribute("memory_decay_rate", 0.98)
    new_player.set_ai_attribute("pattern_recognition_threshold", 0.8)
    
    print(f"   Скорость забывания: {new_player.memory_decay_rate}")
    print(f"   Порог распознавания: {new_player.pattern_recognition_threshold}")
    
    # Сохраняем изменения
    new_player.save_attributes()
    print("   Изменения сохранены в БД")
    
    # 6. Получение сводки атрибутов
    print("\n6. Сводка атрибутов из БД:")
    
    summary = entity_attribute_manager.get_entity_attribute_summary("test_player_001")
    print(f"   ID сущности: {summary['entity_id']}")
    print(f"   Очки атрибутов: {summary['attribute_points']}")
    print(f"   Количество атрибутов: {len(summary['attributes'])}")
    
    # Показываем эффекты от атрибутов
    effects = summary.get('effects', {})
    if effects:
        print("   Эффекты от атрибутов:")
        for effect_name, effect_value in effects.items():
            print(f"     {effect_name}: {effect_value}")
    
    # 7. Экспорт атрибутов в JSON
    print("\n7. Экспорт атрибутов в JSON:")
    
    export_path = "data/attributes_demo_export.json"
    entity_attribute_manager.export_entity_attributes_to_json(export_path)
    print(f"   Атрибуты экспортированы в {export_path}")
    
    print("\n=== Демонстрация завершена ===")


def demonstrate_template_loading():
    """Демонстрирует загрузку шаблонов атрибутов"""
    print("\n=== Демонстрация загрузки шаблонов ===\n")
    
    # Получаем все доступные шаблоны
    template_manager = entity_attribute_manager.template_manager
    templates = template_manager.get_all_templates()
    
    print(f"Загружено шаблонов атрибутов: {len(templates)}")
    
    for template_id, template in templates.items():
        print(f"\nШаблон: {template.name} ({template_id})")
        print(f"  Описание: {template.description}")
        print(f"  Категория: {template.category}")
        print(f"  Базовое значение: {template.base_value}")
        print(f"  Максимум: {template.max_value}")
        print(f"  Скорость роста: {template.growth_rate}")
        
        if template.effects:
            print(f"  Эффекты:")
            for effect_name, effect_value in template.effects.items():
                print(f"    {effect_name}: {effect_value}")


if __name__ == "__main__":
    try:
        demonstrate_attribute_system()
        demonstrate_template_loading()
        
    except Exception as e:
        print(f"Ошибка в демонстрации: {e}")
        import traceback
        traceback.print_exc()
