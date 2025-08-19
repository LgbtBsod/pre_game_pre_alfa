#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных начальными данными.
Заполняет справочные таблицы и создает примеры сессий.
"""

import sqlite3
from pathlib import Path
import logging
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_effects(cursor):
    """Заполняет таблицу эффектов"""
    effects_data = [
        ("EFFECT_001", "STRENGTH_BOOST", "Увеличение силы", "buff", "strength", 10.0, 0, 30.0, 1.0, 1, "Временно увеличивает силу", ""),
        ("EFFECT_002", "WEAKNESS", "Слабость", "debuff", "strength", -5.0, 0, 20.0, 1.0, 1, "Временно уменьшает силу", ""),
        ("EFFECT_003", "HEALING", "Исцеление", "heal", "health", 25.0, 0, 0.0, 0.0, 1, "Восстанавливает здоровье", ""),
        ("EFFECT_004", "POISON", "Отравление", "dot", "health", -3.0, 0, 10.0, 2.0, 5, "Наносит урон от яда", ""),
        ("EFFECT_005", "BURN", "Горение", "dot", "health", -4.0, 0, 8.0, 1.5, 3, "Наносит урон от огня", ""),
        ("EFFECT_006", "FREEZE", "Заморозка", "debuff", "speed", -0.5, 0, 5.0, 1.0, 1, "Замедляет движение", ""),
        ("EFFECT_007", "STUN", "Оглушение", "debuff", "speed", -1.0, 0, 3.0, 0.0, 1, "Полностью останавливает", ""),
        ("EFFECT_008", "INVISIBILITY", "Невидимость", "buff", "stealth", 1.0, 0, 15.0, 1.0, 1, "Делает невидимым", ""),
        ("EFFECT_009", "REGENERATION", "Регенерация", "hot", "health", 2.0, 0, 20.0, 2.0, 1, "Постепенно восстанавливает здоровье", ""),
        ("EFFECT_010", "MANA_BOOST", "Увеличение маны", "buff", "mana", 20.0, 0, 25.0, 1.0, 1, "Временно увеличивает ману", "")
    ]
    
    cursor.executemany("""
        INSERT INTO effects (guid, code, name, effect_type, attribute, value, is_percent, 
                           duration, tick_interval, max_stacks, description, icon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, effects_data)
    
    logger.info(f"Добавлено {len(effects_data)} эффектов")


def populate_skill_effects(cursor):
    """Заполняет таблицу эффектов навыков"""
    effects_data = [
        ("basic_attack", "damage", 10.0, 0.0, 1.0, "linear", "physical"),
        ("fire_ball", "damage", 25.0, 0.0, 1.0, "linear", "fire"),
        ("fire_ball", "burn", 5.0, 3.0, 0.3, "linear", "fire"),
        ("ice_shard", "damage", 20.0, 0.0, 1.0, "linear", "ice"),
        ("ice_shard", "slow", 0.5, 2.0, 0.4, "linear", "ice"),
        ("heal", "healing", 30.0, 0.0, 1.0, "linear", "holy"),
        ("lightning_bolt", "damage", 30.0, 0.0, 1.0, "linear", "lightning"),
        ("lightning_bolt", "stun", 1.0, 1.0, 0.2, "linear", "lightning"),
        ("poison_dart", "damage", 15.0, 0.0, 1.0, "linear", "poison"),
        ("poison_dart", "poison", 8.0, 5.0, 0.6, "linear", "poison"),
        ("shield_bash", "damage", 18.0, 0.0, 1.0, "linear", "physical"),
        ("shield_bash", "stun", 0.5, 1.0, 0.3, "linear", "physical"),
        ("fire_nova", "damage", 35.0, 0.0, 1.0, "linear", "fire"),
        ("fire_nova", "burn", 8.0, 4.0, 0.5, "linear", "fire"),
        ("ice_wall", "defense", 15.0, 8.0, 1.0, "linear", "ice"),
        ("stealth", "stealth", 1.0, 0.0, 1.0, "linear", "none")
    ]
    
    cursor.executemany("""
        INSERT INTO skill_effects (skill_id, effect_type, value, duration, chance, scaling, element)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, effects_data)
    
    logger.info(f"Добавлено {len(effects_data)} эффектов навыков")


def populate_enemy_types(cursor):
    """Заполняет таблицу типов врагов"""
    enemy_types_data = [
        ("goblin", "Гоблин", 50.0, 8.0, 1.2, 3.0, "aggressive"),
        ("orc", "Орк", 120.0, 25.0, 0.8, 8.0, "aggressive"),
        ("troll", "Тролль", 200.0, 35.0, 0.6, 15.0, "aggressive"),
        ("dragon", "Дракон", 500.0, 80.0, 1.5, 25.0, "aggressive"),
        ("undead", "Нежить", 80.0, 15.0, 0.9, 5.0, "aggressive"),
        ("demon", "Демон", 300.0, 45.0, 1.1, 12.0, "aggressive"),
        ("angel", "Ангел", 250.0, 40.0, 1.3, 10.0, "balanced"),
        ("beast", "Зверь", 100.0, 20.0, 1.4, 6.0, "aggressive"),
        ("construct", "Конструкт", 150.0, 30.0, 0.7, 20.0, "defensive"),
        ("elemental", "Элементаль", 180.0, 35.0, 1.0, 8.0, "balanced")
    ]
    
    cursor.executemany("""
        INSERT INTO enemy_types (type_id, name, base_health, base_damage, speed, defense, behavior)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, enemy_types_data)
    
    logger.info(f"Добавлено {len(enemy_types_data)} типов врагов")


def populate_weapons(cursor):
    """Заполняет таблицу оружия"""
    weapons_data = [
        ("sword_common", "Обычный меч", "sword", "physical", "common", 25.0, 1.5),
        ("sword_rare", "Редкий меч", "sword", "physical", "rare", 40.0, 1.8),
        ("axe_common", "Обычный топор", "axe", "physical", "common", 35.0, 1.0),
        ("axe_rare", "Редкий топор", "axe", "physical", "rare", 55.0, 1.2),
        ("spear_common", "Обычное копье", "spear", "physical", "common", 30.0, 1.8),
        ("spear_rare", "Редкое копье", "spear", "physical", "rare", 45.0, 2.0),
        ("bow_common", "Обычный лук", "bow", "physical", "common", 20.0, 2.0),
        ("bow_rare", "Редкий лук", "bow", "physical", "rare", 35.0, 2.5),
        ("staff_common", "Обычный посох", "staff", "magic", "common", 15.0, 1.2),
        ("staff_rare", "Редкий посох", "staff", "magic", "rare", 25.0, 1.5),
        ("dagger_common", "Обычный кинжал", "dagger", "physical", "common", 18.0, 3.0),
        ("dagger_rare", "Редкий кинжал", "dagger", "physical", "rare", 30.0, 3.5),
        ("fire_staff", "Огненный посох", "staff", "fire", "uncommon", 30.0, 1.3),
        ("ice_staff", "Ледяной посох", "staff", "ice", "uncommon", 28.0, 1.3),
        ("lightning_staff", "Молниевый посох", "staff", "lightning", "uncommon", 32.0, 1.3)
    ]
    
    cursor.executemany("""
        INSERT INTO weapons (weapon_id, name, weapon_type, damage_type, rarity, base_damage, attack_speed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, weapons_data)
    
    logger.info(f"Добавлено {len(weapons_data)} видов оружия")


def create_example_sessions(cursor):
    """Создает примеры сессий для демонстрации"""
    import json
    
    # Создаем два примера слотов сохранения
    session_uuids = [str(uuid.uuid4()), str(uuid.uuid4())]
    now = datetime.now().isoformat()
    
    # Слот 1
    cursor.execute("""
        INSERT INTO save_slots 
        (slot_id, session_uuid, save_name, created_at, last_played, player_level, world_seed, play_time, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (1, session_uuids[0], "Пример сохранения 1", now, now, 5, 12345, 3600.0, 1))
    
    # Слот 2
    cursor.execute("""
        INSERT INTO save_slots 
        (slot_id, session_uuid, save_name, created_at, last_played, player_level, world_seed, play_time, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (2, session_uuids[1], "Пример сохранения 2", now, now, 3, 67890, 1800.0, 1))
    
    # Данные сессии 1
    player_data_1 = {
        "name": "Игрок 1",
        "level": 5,
        "experience": 1250,
        "health": 100,
        "mana": 80,
        "position": {"x": 100, "y": 100, "z": 0}
    }
    
    world_data_1 = {
        "name": "Лесной мир",
        "biome": "forest",
        "difficulty": 1.2,
        "explored_areas": 15
    }
    
    cursor.execute("""
        INSERT INTO session_data 
        (session_uuid, slot_id, state, created_at, last_saved, player_data, world_data, 
         inventory_data, progress_data, generation_seed, current_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_uuids[0], 1, "active", now, now,
        json.dumps(player_data_1), json.dumps(world_data_1),
        json.dumps({"items": [], "weapons": [], "skills": []}),
        json.dumps({"completed_levels": [1, 2, 3, 4], "current_quest": "main_quest_5"}),
        12345, 5
    ))
    
    # Данные сессии 2
    player_data_2 = {
        "name": "Игрок 2",
        "level": 3,
        "experience": 450,
        "health": 80,
        "mana": 60,
        "position": {"x": 50, "y": 50, "z": 0}
    }
    
    world_data_2 = {
        "name": "Горный мир",
        "biome": "mountain",
        "difficulty": 0.8,
        "explored_areas": 8
    }
    
    cursor.execute("""
        INSERT INTO session_data 
        (session_uuid, slot_id, state, created_at, last_saved, player_data, world_data, 
         inventory_data, progress_data, generation_seed, current_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_uuids[1], 2, "active", now, now,
        json.dumps(player_data_2), json.dumps(world_data_2),
        json.dumps({"items": [], "weapons": [], "skills": []}),
        json.dumps({"completed_levels": [1, 2], "current_quest": "main_quest_3"}),
        67890, 3
    ))
    
    # Добавляем примеры сгенерированного контента для сессии 1
    example_items_1 = [
        ("item_001", "Зелье здоровья", "consumable", "common", json.dumps(["healing"]), 50, 0.5, "", 0, None),
        ("item_002", "Меч новичка", "weapon", "common", json.dumps(["damage_boost"]), 100, 2.0, "", 0, None),
        ("item_003", "Кольцо защиты", "equipment", "uncommon", json.dumps(["defense_boost"]), 200, 0.1, "", 0, None)
    ]
    
    for item in example_items_1:
        cursor.execute("""
            INSERT INTO session_items 
            (session_uuid, item_id, name, item_type, rarity, effects, value, weight, icon, is_obtained, obtained_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_uuids[0],) + item)
    
    # Добавляем примеры сгенерированного контента для сессии 2
    example_items_2 = [
        ("item_004", "Зелье маны", "consumable", "common", json.dumps(["mana_boost"]), 40, 0.3, "", 0, None),
        ("item_005", "Лук охотника", "weapon", "uncommon", json.dumps(["range_boost"]), 150, 1.5, "", 0, None)
    ]
    
    for item in example_items_2:
        cursor.execute("""
            INSERT INTO session_items 
            (session_uuid, item_id, name, item_type, rarity, effects, value, weight, icon, is_obtained, obtained_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_uuids[1],) + item)
    
    logger.info(f"Создано 2 примера сессий с UUID: {session_uuids[0][:8]}... и {session_uuids[1][:8]}...")


def main():
    """Главная функция заполнения БД"""
    db_path = Path("data/game_data.db")
    
    if not db_path.exists():
        logger.error("База данных не найдена. Сначала запустите create_db.py")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        logger.info("Начинаю заполнение базы данных...")
        
        # Заполняем справочные таблицы
        populate_effects(cursor)
        populate_skill_effects(cursor)
        populate_enemy_types(cursor)
        populate_weapons(cursor)
        
        # Создаем примеры сессий
        create_example_sessions(cursor)
        
        # Коммитим изменения
        conn.commit()
        logger.info("База данных успешно заполнена!")
        
        # Показываем статистику
        for table in ["effects", "skill_effects", "enemy_types", "weapons", 
                     "save_slots", "session_data", "session_items"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"Таблица {table}: {count} записей")
            
    except Exception as e:
        logger.error(f"Ошибка заполнения БД: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
