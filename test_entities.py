#!/usr/bin/env python3
"""
Тестовый скрипт для проверки архитектуры сущностей
"""

import sys
import os
import time

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.entities import Player, NPC, Enemy, BaseEntity, EntityType
from src.entities.items import Weapon, Armor, Consumable

def test_base_entity():
    """Тест базовой сущности"""
    print("=== Тест базовой сущности ===")
    
    # Создаем базовую сущность
    entity = BaseEntity("test_entity", EntityType.NPC, "Тестовая сущность")
    
    print(f"Создана сущность: {entity.name}")
    print(f"Тип: {entity.entity_type.value}")
    print(f"Здоровье: {entity.stats.health}/{entity.stats.max_health}")
    print(f"Уровень: {entity.stats.level}")
    
    # Тестируем получение урона
    print(f"\nПолучаем урон...")
    entity.take_damage(20, source="test")
    print(f"Здоровье после урона: {entity.stats.health}/{entity.stats.max_health}")
    
    # Тестируем лечение
    print(f"\nЛечимся...")
    entity.heal(10, source="test")
    print(f"Здоровье после лечения: {entity.stats.health}/{entity.stats.max_health}")
    
    # Тестируем получение опыта
    print(f"\nПолучаем опыт...")
    entity.gain_experience(50, source="test")
    print(f"Опыт: {entity.stats.experience}/{entity.stats.experience_to_next}")
    
    # Тестируем эмоции
    print(f"\nДобавляем эмоцию...")
    entity.add_emotion('joy', 0.5, 10.0, 'test')
    print(f"Настроение: {entity.emotions.mood:.2f}")
    print(f"Количество эмоций: {len(entity.emotions.emotions)}")
    
    print(f"\nИнформация о сущности:")
    print(entity.get_info())
    
    return entity

def test_player():
    """Тест игрока"""
    print("\n=== Тест игрока ===")
    
    # Создаем игрока
    player = Player("test_player", "Тестовый игрок")
    
    print(f"Создан игрок: {player.name}")
    print(f"Репутация: {player.player_stats.reputation}")
    print(f"Время игры: {player.player_stats.total_playtime:.1f} сек")
    
    # Тестируем квесты
    print(f"\nНачинаем квест...")
    player.start_quest("test_quest_1")
    print(f"Активные квесты: {len(player.active_quests)}")
    
    # Тестируем посещение локации
    print(f"\nПосещаем локацию...")
    player.visit_location("test_location_1")
    print(f"Посещенные локации: {len(player.player_memory.locations_visited)}")
    
    # Тестируем встречу с NPC
    print(f"\nВстречаем NPC...")
    player.meet_npc("test_npc_1")
    print(f"Встреченные NPC: {len(player.player_memory.npcs_met)}")
    
    # Тестируем репутацию
    print(f"\nПолучаем репутацию...")
    player.gain_reputation("test_faction", 10)
    print(f"Репутация: {player.player_stats.reputation}")
    
    print(f"\nИнформация об игроке:")
    print(player.get_info())
    
    return player

def test_npc():
    """Тест NPC"""
    print("\n=== Тест NPC ===")
    
    # Создаем NPC
    npc = NPC("test_npc", "Тестовый NPC", "merchant")
    
    print(f"Создан NPC: {npc.name}")
    print(f"Профессия: {npc.npc_stats.profession}")
    print(f"Дружелюбие: {npc.personality.friendliness:.2f}")
    
    # Тестируем взаимодействие с игроком
    print(f"\nВзаимодействуем с игроком...")
    response = npc.interact_with_player("test_player", "greeting", {
        'player_name': 'Тестовый игрок'
    })
    print(f"Ответ NPC: {response['message']}")
    print(f"Изменение отношений: {response['relationship_change']:.2f}")
    
    # Тестируем диалоговые опции
    print(f"\nПолучаем диалоговые опции...")
    options = npc.get_dialogue_options("test_player")
    print(f"Доступные опции: {len(options)}")
    for option in options:
        print(f"  - {option['text']} (ID: {option['id']})")
    
    # Тестируем торговца
    print(f"\nДелаем NPC торговцем...")
    npc.set_merchant(True, ["item_1", "item_2"], {"item_1": 100, "item_2": 200})
    print(f"Торговец: {'Да' if npc.is_merchant else 'Нет'}")
    print(f"Товары: {npc.shop_inventory}")
    
    print(f"\nИнформация о NPC:")
    print(npc.get_info())
    
    return npc

def test_enemy():
    """Тест врага"""
    print("\n=== Тест врага ===")
    
    # Создаем врага
    enemy = Enemy("test_enemy", "Тестовый враг", "goblin")
    
    print(f"Создан враг: {enemy.name}")
    print(f"Уровень угрозы: {enemy.enemy_stats.threat_level}")
    print(f"Агрессия: {enemy.enemy_stats.aggression:.2f}")
    
    # Тестируем способности
    print(f"\nДобавляем способности...")
    enemy.add_ability("fireball")
    enemy.add_ability("charge")
    print(f"Способности: {enemy.abilities}")
    
    # Тестируем патрулирование
    print(f"\nУстанавливаем маршрут патрулирования...")
    patrol_points = [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)]
    enemy.set_patrol_route(patrol_points)
    print(f"Патрульные точки: {len(enemy.patrol_points)}")
    
    # Тестируем дроп
    print(f"\nДобавляем предметы в дроп...")
    enemy.add_drop_item("gold_coin", 0.8)
    enemy.add_drop_item("rare_sword", 0.1, guaranteed=False)
    enemy.add_drop_item("quest_item", 1.0, guaranteed=True)
    print(f"Предметы в дропе: {len(enemy.drop_table)}")
    print(f"Гарантированные предметы: {enemy.guaranteed_drops}")
    
    # Тестируем атаку
    print(f"\nАтакуем цель...")
    success = enemy.attack("test_target", "basic")
    print(f"Атака успешна: {success}")
    
    # Тестируем отступление
    print(f"\nПолучаем урон для отступления...")
    enemy.take_damage(80, source="test")  # Большой урон
    print(f"Здоровье: {enemy.stats.health}/{enemy.stats.max_health}")
    print(f"Отступление: {'Да' if enemy.is_retreating else 'Нет'}")
    
    print(f"\nИнформация о враге:")
    print(enemy.get_info())
    
    return enemy

def test_items():
    """Тест предметов"""
    print("\n=== Тест предметов ===")
    
    # Создаем оружие
    sword = Weapon("test_sword", "Тестовый меч", "Острый меч", damage=25, attack_speed=1.2)
    print(f"Создано оружие: {sword.name}")
    print(f"Урон: {sword.damage}")
    print(f"Скорость атаки: {sword.attack_speed}")
    
    # Создаем броню
    armor = Armor("test_armor", "Тестовая броня", "Прочная броня", defense=15, armor_type="medium")
    print(f"Создана броня: {armor.name}")
    print(f"Защита: {armor.defense}")
    print(f"Тип брони: {armor.armor_type}")
    
    # Создаем зелье
    potion = Consumable("test_potion", "Тестовое зелье", "Восстанавливает здоровье", heal_amount=50)
    print(f"Создано зелье: {potion.name}")
    print(f"Лечение: {potion.heal_amount}")
    print(f"Расходуемое: {potion.is_consumable}")
    
    return sword, armor, potion

def test_inventory_management():
    """Тест управления инвентарем"""
    print("\n=== Тест управления инвентарем ===")
    
    # Создаем игрока
    player = Player("inventory_test_player", "Тестовый игрок")
    
    # Создаем предметы
    sword, armor, potion = test_items()
    
    # Добавляем предметы в инвентарь
    print(f"\nДобавляем предметы в инвентарь...")
    player.add_item(sword)
    player.add_item(armor)
    player.add_item(potion)
    print(f"Предметов в инвентаре: {len(player.inventory.items)}")
    
    # Экипируем предметы
    print(f"\nЭкипируем предметы...")
    player.equip_item(sword, "weapon")
    player.equip_item(armor, "chest")
    print(f"Экипированных предметов: {len(player.inventory.equipped_items)}")
    
    # Используем зелье
    print(f"\nИспользуем зелье...")
    player.use_item(potion, target="inventory_test_player")
    print(f"Предметов в инвентаре после использования: {len(player.inventory.items)}")
    
    return player

def main():
    """Основная функция тестирования"""
    print("Начинаем тестирование архитектуры сущностей...")
    print("=" * 50)
    
    try:
        # Тестируем базовую сущность
        entity = test_base_entity()
        
        # Тестируем игрока
        player = test_player()
        
        # Тестируем NPC
        npc = test_npc()
        
        # Тестируем врага
        enemy = test_enemy()
        
        # Тестируем предметы
        test_items()
        
        # Тестируем управление инвентарем
        inventory_player = test_inventory_management()
        
        print("\n" + "=" * 50)
        print("Все тесты завершены успешно!")
        print("Архитектура сущностей работает корректно.")
        
    except Exception as e:
        print(f"\nОшибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
