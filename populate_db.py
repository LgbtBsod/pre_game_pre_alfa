#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных начальными данными.
Заполняет таблицы skills, items, enemy_types, weapons начальным контентом.
"""

import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_skills(cursor):
    """Заполняет таблицу навыков"""
    skills_data = [
        ("basic_attack", "Базовая атака", "Простая физическая атака", "combat", "physical", "single_enemy", 10.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.05, 1.5),
        ("fire_ball", "Огненный шар", "Магическая атака огнем", "magic", "fire", "single_enemy", 25.0, 0.0, 15.0, 2.0, 3.0, 0.9, 0.1, 1.8),
        ("ice_shard", "Ледяной осколок", "Магическая атака льдом", "magic", "ice", "single_enemy", 20.0, 0.0, 12.0, 1.5, 2.5, 0.95, 0.08, 1.6),
        ("heal", "Исцеление", "Восстанавливает здоровье", "support", "holy", "single_ally", 0.0, 30.0, 12.0, 3.0, 2.0, 1.0, 0.0, 1.0),
        ("lightning_bolt", "Молния", "Электрическая атака", "magic", "lightning", "single_enemy", 30.0, 0.0, 18.0, 2.5, 4.0, 0.85, 0.15, 2.0),
        ("poison_dart", "Отравленный дротик", "Атака ядом", "combat", "poison", "single_enemy", 15.0, 0.0, 8.0, 1.0, 2.0, 0.9, 0.12, 1.4),
        ("shield_bash", "Удар щитом", "Защитная атака", "combat", "physical", "single_enemy", 18.0, 0.0, 5.0, 1.5, 1.5, 0.8, 0.08, 1.3),
        ("fire_nova", "Огненная вспышка", "Атака по области", "magic", "fire", "area", 35.0, 0.0, 25.0, 8.0, 3.0, 0.8, 0.2, 2.2),
        ("ice_wall", "Ледяная стена", "Защитное заклинание", "support", "ice", "self", 0.0, 0.0, 20.0, 5.0, 0.0, 1.0, 0.0, 1.0),
        ("stealth", "Скрытность", "Пассивная способность", "passive", "none", "self", 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0)
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


def populate_items(cursor):
    """Заполняет таблицу предметов"""
    items_data = [
        ("health_potion", "Зелье здоровья", "Восстанавливает здоровье", "consumable", "common", 50, 0.5, "graphics/items/health_potion.png"),
        ("mana_potion", "Зелье маны", "Восстанавливает ману", "consumable", "common", 40, 0.3, "graphics/items/mana_potion.png"),
        ("strength_potion", "Зелье силы", "Временно увеличивает силу", "consumable", "uncommon", 80, 0.4, "graphics/items/strength_potion.png"),
        ("invisibility_cloak", "Плащ-невидимка", "Делает невидимым", "equipment", "rare", 200, 1.0, "graphics/items/invisibility_cloak.png"),
        ("fire_resistance_ring", "Кольцо огнестойкости", "Увеличивает сопротивление огню", "equipment", "uncommon", 120, 0.1, "graphics/items/fire_ring.png"),
        ("ice_resistance_ring", "Кольцо ледостойкости", "Увеличивает сопротивление льду", "equipment", "uncommon", 120, 0.1, "graphics/items/ice_ring.png"),
        ("lightning_resistance_ring", "Кольцо молниестойкости", "Увеличивает сопротивление молнии", "equipment", "uncommon", 120, 0.1, "graphics/items/lightning_ring.png"),
        ("poison_resistance_ring", "Кольцо ядостойкости", "Увеличивает сопротивление яду", "equipment", "uncommon", 120, 0.1, "graphics/items/poison_ring.png"),
        ("healing_scroll", "Свиток исцеления", "Мгновенно исцеляет", "consumable", "rare", 150, 0.2, "graphics/items/healing_scroll.png"),
        ("teleport_scroll", "Свиток телепортации", "Перемещает в безопасное место", "consumable", "epic", 300, 0.1, "graphics/items/teleport_scroll.png")
    ]
    
    cursor.executemany("""
        INSERT INTO items (item_id, name, description, item_type, rarity, value, weight, icon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, items_data)
    
    logger.info(f"Добавлено {len(items_data)} предметов")


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
        
        # Заполняем все таблицы
        populate_effects(cursor)
        populate_skills(cursor)
        populate_skill_effects(cursor)
        populate_items(cursor)
        populate_enemy_types(cursor)
        populate_weapons(cursor)
        
        # Коммитим изменения
        conn.commit()
        logger.info("База данных успешно заполнена!")
        
        # Показываем статистику
        for table in ["effects", "skills", "skill_effects", "items", "enemy_types", "weapons"]:
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
