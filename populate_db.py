#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных начальными данными.
Заполняет таблицы skills, items, enemy_types базовым контентом.
"""

import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_skills(cursor):
    """Заполняет таблицу навыков"""
    skills_data = [
        # Боевые навыки
        ("basic_attack", "Базовая атака", "Простая физическая атака", "combat", "physical", "single_enemy", 10.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.05, 1.5),
        ("fire_ball", "Огненный шар", "Магическая атака огнем", "magic", "fire", "single_enemy", 25.0, 0.0, 15.0, 2.0, 3.0, 0.9, 0.08, 1.8),
        ("ice_shard", "Ледяной осколок", "Магическая атака льдом", "magic", "ice", "single_enemy", 20.0, 0.0, 12.0, 1.5, 2.5, 0.95, 0.1, 1.6),
        ("lightning_bolt", "Удар молнии", "Электрическая атака", "magic", "lightning", "single_enemy", 30.0, 0.0, 18.0, 3.0, 4.0, 0.85, 0.12, 2.0),
        
        # Поддерживающие навыки
        ("heal", "Исцеление", "Восстанавливает здоровье", "support", "holy", "single_ally", 0.0, 30.0, 12.0, 3.0, 2.0, 1.0, 0.0, 1.0),
        ("shield", "Щит", "Защитный барьер", "support", "none", "self", 0.0, 0.0, 8.0, 5.0, 0.0, 1.0, 0.0, 1.0),
        ("haste", "Ускорение", "Увеличивает скорость", "support", "none", "single_ally", 0.0, 0.0, 10.0, 8.0, 0.0, 1.0, 0.0, 1.0),
        
        # Утилитарные навыки
        ("stealth", "Скрытность", "Скрывает от врагов", "utility", "none", "self", 0.0, 0.0, 5.0, 10.0, 0.0, 1.0, 0.0, 1.0),
        ("detect", "Обнаружение", "Показывает скрытых врагов", "utility", "none", "area", 0.0, 0.0, 3.0, 15.0, 5.0, 0.8, 0.0, 1.0),
        
        # Пассивные навыки
        ("combat_mastery", "Боевое мастерство", "Увеличивает урон", "passive", "none", "self", 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0),
        ("elemental_resistance", "Стихийная устойчивость", "Снижает урон стихий", "passive", "none", "self", 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0),
        
        # Ультимативные навыки
        ("meteor_storm", "Метеоритный шторм", "Мощная огненная атака", "ultimate", "fire", "area", 80.0, 0.0, 50.0, 30.0, 8.0, 0.7, 0.2, 2.5),
        ("time_stop", "Остановка времени", "Останавливает время", "ultimate", "cosmic", "area", 0.0, 0.0, 100.0, 60.0, 10.0, 0.6, 0.0, 1.0),
    ]
    
    cursor.executemany("""
        INSERT INTO skills (skill_id, name, description, skill_type, element, target, 
                          base_damage, base_healing, mana_cost, cooldown, range, 
                          accuracy, critical_chance, critical_multiplier)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, skills_data)
    
    logger.info(f"Добавлено {len(skills_data)} навыков")


def populate_skill_effects(cursor):
    """Заполняет таблицу эффектов навыков"""
    effects_data = [
        # Эффекты для базовой атаки
        ("basic_attack", "damage", 10.0, 0.0, 1.0, "linear", "physical"),
        
        # Эффекты для огненного шара
        ("fire_ball", "damage", 25.0, 0.0, 1.0, "linear", "fire"),
        ("fire_ball", "burn", 5.0, 3.0, 0.8, "linear", "fire"),
        
        # Эффекты для ледяного осколка
        ("ice_shard", "damage", 20.0, 0.0, 1.0, "linear", "ice"),
        ("ice_shard", "freeze", 0.0, 2.0, 0.6, "linear", "ice"),
        
        # Эффекты для удара молнии
        ("lightning_bolt", "damage", 30.0, 0.0, 1.0, "linear", "lightning"),
        ("lightning_bolt", "stun", 0.0, 1.5, 0.7, "linear", "lightning"),
        
        # Эффекты для исцеления
        ("heal", "healing", 30.0, 0.0, 1.0, "linear", "holy"),
        
        # Эффекты для щита
        ("shield", "defense", 20.0, 5.0, 1.0, "linear", "none"),
        
        # Эффекты для ускорения
        ("haste", "speed", 2.0, 8.0, 1.0, "linear", "none"),
        
        # Эффекты для метеоритного шторма
        ("meteor_storm", "damage", 80.0, 0.0, 1.0, "exponential", "fire"),
        ("meteor_storm", "burn", 15.0, 5.0, 0.9, "linear", "fire"),
        
        # Эффекты для остановки времени
        ("time_stop", "time_freeze", 0.0, 3.0, 0.8, "linear", "cosmic"),
    ]
    
    cursor.executemany("""
        INSERT INTO skill_effects (skill_id, effect_type, value, duration, chance, scaling, element)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, effects_data)
    
    logger.info(f"Добавлено {len(effects_data)} эффектов навыков")


def populate_items(cursor):
    """Заполняет таблицу предметов"""
    items_data = [
        # Оружие
        ("sword_iron", "Железный меч", "Надежный железный меч", "weapon", "common", 50, 2.5),
        ("sword_steel", "Стальной меч", "Качественный стальной меч", "weapon", "uncommon", 120, 3.0),
        ("axe_battle", "Боевой топор", "Мощный боевой топор", "weapon", "common", 80, 4.0),
        ("bow_hunting", "Охотничий лук", "Точный охотничий лук", "weapon", "uncommon", 100, 1.5),
        
        # Броня
        ("armor_leather", "Кожаная броня", "Легкая кожаная броня", "armor", "common", 40, 3.0),
        ("armor_chain", "Кольчужная броня", "Надежная кольчужная броня", "armor", "uncommon", 90, 8.0),
        ("shield_wooden", "Деревянный щит", "Простой деревянный щит", "armor", "common", 25, 2.0),
        
        # Зелья
        ("potion_health", "Зелье здоровья", "Восстанавливает здоровье", "consumable", "common", 15, 0.5),
        ("potion_mana", "Зелье маны", "Восстанавливает ману", "consumable", "common", 20, 0.5),
        ("potion_strength", "Зелье силы", "Временно увеличивает силу", "consumable", "uncommon", 35, 0.3),
        
        # Материалы
        ("herb_red", "Красная трава", "Редкая лечебная трава", "material", "rare", 80, 0.1),
        ("crystal_blue", "Синий кристалл", "Магический кристалл", "material", "rare", 150, 0.2),
        ("ore_iron", "Железная руда", "Сырая железная руда", "material", "common", 10, 1.0),
        
        # Специальные предметы
        ("scroll_teleport", "Свиток телепортации", "Перемещает в безопасное место", "special", "rare", 200, 0.1),
        ("key_ancient", "Древний ключ", "Открывает древние двери", "special", "epic", 500, 0.1),
    ]
    
    cursor.executemany("""
        INSERT INTO items (item_id, name, description, item_type, rarity, value, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, items_data)
    
    logger.info(f"Добавлено {len(items_data)} предметов")


def populate_enemy_types(cursor):
    """Заполняет таблицу типов врагов"""
    enemy_data = [
        # Обычные враги
        ("goblin", "Гоблин", 40.0, 8.0, 1.2, 3.0, "aggressive"),
        ("orc", "Орк", 80.0, 15.0, 0.8, 8.0, "aggressive"),
        ("troll", "Тролль", 150.0, 25.0, 0.6, 15.0, "aggressive"),
        ("skeleton", "Скелет", 60.0, 12.0, 1.0, 5.0, "aggressive"),
        
        # Магические враги
        ("mage", "Маг", 50.0, 20.0, 0.7, 2.0, "cautious"),
        ("warlock", "Чернокнижник", 70.0, 25.0, 0.8, 3.0, "cautious"),
        ("elemental_fire", "Огненный элементаль", 100.0, 30.0, 1.1, 8.0, "aggressive"),
        ("elemental_ice", "Ледяной элементаль", 90.0, 28.0, 1.0, 10.0, "defensive"),
        
        # Животные
        ("wolf", "Волк", 45.0, 10.0, 1.5, 2.0, "aggressive"),
        ("bear", "Медведь", 120.0, 20.0, 0.9, 12.0, "aggressive"),
        ("eagle", "Орел", 35.0, 8.0, 2.0, 1.0, "cautious"),
        
        # Боссы
        ("dragon_young", "Молодой дракон", 300.0, 50.0, 1.2, 25.0, "aggressive"),
        ("lich", "Лич", 200.0, 40.0, 0.8, 15.0, "cautious"),
        ("demon_minor", "Младший демон", 250.0, 45.0, 1.0, 18.0, "aggressive"),
    ]
    
    cursor.executemany("""
        INSERT INTO enemy_types (type_id, name, base_health, base_damage, speed, defense, behavior)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, enemy_data)
    
    logger.info(f"Добавлено {len(enemy_data)} типов врагов")


def populate_weapons(cursor):
    """Заполняет таблицу оружия"""
    weapons_data = [
        # Мечи
        ("sword_short", "Короткий меч", "sword", "physical", "common", 15.0, 1.2),
        ("sword_long", "Длинный меч", "sword", "physical", "uncommon", 22.0, 1.0),
        ("sword_bastard", "Полуторный меч", "sword", "physical", "rare", 30.0, 0.9),
        
        # Топоры
        ("axe_hand", "Ручной топор", "axe", "physical", "common", 18.0, 0.8),
        ("axe_battle", "Боевой топор", "axe", "physical", "uncommon", 25.0, 0.7),
        ("axe_double", "Двуручный топор", "axe", "physical", "rare", 35.0, 0.6),
        
        # Копья
        ("spear_wooden", "Деревянное копье", "spear", "physical", "common", 12.0, 1.5),
        ("spear_iron", "Железное копье", "spear", "physical", "uncommon", 18.0, 1.4),
        ("spear_magic", "Магическое копье", "spear", "magic", "rare", 25.0, 1.3),
        
        # Луки
        ("bow_short", "Короткий лук", "bow", "physical", "common", 10.0, 2.0),
        ("bow_long", "Длинный лук", "bow", "physical", "uncommon", 15.0, 1.8),
        ("bow_composite", "Составной лук", "bow", "physical", "rare", 20.0, 1.6),
        
        # Магическое оружие
        ("staff_wooden", "Деревянный посох", "staff", "magic", "common", 8.0, 1.0),
        ("staff_crystal", "Кристальный посох", "staff", "magic", "uncommon", 15.0, 0.9),
        ("staff_ancient", "Древний посох", "staff", "magic", "rare", 25.0, 0.8),
        
        # Экзотическое оружие
        ("dagger_stealth", "Кинжал скрытности", "dagger", "physical", "uncommon", 12.0, 2.5),
        ("hammer_war", "Боевой молот", "hammer", "physical", "uncommon", 28.0, 0.6),
        ("scythe_reaper", "Коса жнеца", "scythe", "physical", "rare", 32.0, 0.7),
    ]
    
    cursor.executemany("""
        INSERT INTO weapons (weapon_id, name, weapon_type, damage_type, rarity, base_damage, attack_speed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, weapons_data)
    
    logger.info(f"Добавлено {len(weapons_data)} видов оружия")


def main():
    """Главная функция заполнения БД"""
    db_path = Path("data/game_data.db")
    
    if not db_path.exists():
        logger.error(f"База данных {db_path} не найдена!")
        logger.info("Сначала запустите create_db.py для создания БД")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        logger.info("Начинаю заполнение базы данных...")
        
        # Заполняем таблицы
        populate_skills(cursor)
        populate_skill_effects(cursor)
        populate_items(cursor)
        populate_enemy_types(cursor)
        populate_weapons(cursor)
        
        # Коммитим изменения
        conn.commit()
        logger.info("База данных успешно заполнена!")
        
        # Показываем статистику
        cursor.execute("SELECT COUNT(*) FROM skills")
        skills_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM skill_effects")
        effects_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM items")
        items_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM enemy_types")
        enemies_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM weapons")
        weapons_count = cursor.fetchone()[0]
        
        logger.info(f"""
Статистика заполнения:
- Навыков: {skills_count}
- Эффектов навыков: {effects_count}
- Предметов: {items_count}
- Типов врагов: {enemies_count}
- Видов оружия: {weapons_count}
        """)
        
    except Exception as e:
        logger.error(f"Ошибка заполнения БД: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
