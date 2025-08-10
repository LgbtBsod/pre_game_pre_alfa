import sqlite3
import json
import os
from datetime import datetime


def migrate_data_to_db():
    """Мигрирует данные из JSON файлов в базу данных"""

    # Создаем подключение к БД
    conn = sqlite3.connect("data/game_data.db")
    cursor = conn.cursor()

    print("Начинаем миграцию данных...")

    # Мигрируем атрибуты
    if os.path.exists("data/attributes.json"):
        print("\nМигрируем атрибуты...")
        with open("data/attributes.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for attr_id, attr_data in data["attributes"].items():
            cursor.execute(
                """
                INSERT OR REPLACE INTO attributes 
                (id, name, description, base_value, max_value, growth_rate, category, effects, hex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    attr_id,
                    attr_data["name"],
                    attr_data["description"],
                    attr_data["base_value"],
                    attr_data["max_value"],
                    attr_data["growth_rate"],
                    attr_data["category"],
                    json.dumps(attr_data["effects"]),
                    attr_data.get("hex_id", attr_id),
                ),
            )
        print(f"  Мигрировано {len(data['attributes'])} атрибутов")

    # Мигрируем эффекты
    if os.path.exists("data/effects.json"):
        print("\nМигрируем эффекты...")
        with open("data/effects.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for eff_id, eff_data in data["effects"].items():
            cursor.execute(
                """
                INSERT OR REPLACE INTO effects 
                (id, name, description, type, category, tags, modifiers, max_stacks, duration, 
                 interval, tick_interval, stackable, effect_type, hex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    eff_id,
                    eff_data["name"],
                    eff_data["description"],
                    eff_data["type"],
                    eff_data["category"],
                    json.dumps(eff_data.get("tags", [])),
                    json.dumps(eff_data.get("modifiers", {})),
                    eff_data.get("max_stacks", 1),
                    eff_data.get("duration", -1),
                    eff_data.get("interval"),
                    eff_data.get("tick_interval"),
                    1 if eff_data.get("stackable", False) else 0,
                    eff_data["type"],
                    eff_data.get("hex_id", eff_id),
                ),
            )
        print(f"  Мигрировано {len(data['effects'])} эффектов")

    # Мигрируем предметы
    if os.path.exists("data/items.json"):
        print("\nМигрируем предметы...")
        with open("data/items.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for item_id, item_data in data["items"].items():
            cursor.execute(
                """
                INSERT OR REPLACE INTO items 
                (id, name, description, type, slot, rarity, level_requirement, base_damage, 
                 attack_speed, defense, damage_type, element, element_damage, range, cost, 
                 mana_cost, critical_chance, weight, block_chance, heal_amount, heal_percent, 
                 mana_amount, mana_percent, duration, cooldown, durability, max_durability, 
                 effects, modifiers, tags, resist_mod, weakness_mod, elemental_resistance, hex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_id,
                    item_data["name"],
                    item_data["description"],
                    item_data["type"],
                    item_data.get("slot"),
                    item_data.get("rarity"),
                    item_data.get("level_requirement"),
                    item_data.get("base_damage"),
                    item_data.get("attack_speed"),
                    item_data.get("defense"),
                    item_data.get("damage_type"),
                    item_data.get("element"),
                    item_data.get("element_damage"),
                    item_data.get("range"),
                    item_data.get("cost"),
                    item_data.get("mana_cost"),
                    item_data.get("critical_chance"),
                    item_data.get("weight"),
                    item_data.get("block_chance"),
                    item_data.get("heal_amount"),
                    item_data.get("heal_percent"),
                    item_data.get("mana_amount"),
                    item_data.get("mana_percent"),
                    item_data.get("duration"),
                    item_data.get("cooldown"),
                    item_data.get("durability"),
                    item_data.get("max_durability"),
                    json.dumps(item_data.get("effects", [])),
                    json.dumps(item_data.get("modifiers", {})),
                    json.dumps(item_data.get("tags", [])),
                    json.dumps(item_data.get("resist_mod", {})),
                    json.dumps(item_data.get("weakness_mod", {})),
                    json.dumps(item_data.get("elemental_resistance", {})),
                    item_data.get("hex_id", item_id),
                ),
            )
        print(f"  Мигрировано {len(data['items'])} предметов")

    # Мигрируем сущности
    if os.path.exists("data/entities.json"):
        print("\nМигрируем сущности...")
        with open("data/entities.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for ent_id, ent_data in data["entities"].items():
            cursor.execute(
                """
                INSERT OR REPLACE INTO entities 
                (id, name, description, type, level, experience, experience_to_next, attributes, 
                 combat_stats, equipment_slots, inventory_size, skills, tags, enemy_type, 
                 experience_reward, ai_behavior, loot_table, phases)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    ent_id,
                    ent_data["name"],
                    ent_data["description"],
                    ent_data.get("type"),
                    ent_data.get("level"),
                    ent_data.get("experience"),
                    ent_data.get("experience_to_next"),
                    json.dumps(ent_data.get("attributes", {})),
                    json.dumps(ent_data.get("combat_stats", {})),
                    json.dumps(ent_data.get("equipment_slots", {})),
                    ent_data.get("inventory_size"),
                    json.dumps(ent_data.get("skills", [])),
                    json.dumps(ent_data.get("tags", [])),
                    ent_data.get("enemy_type"),
                    ent_data.get("experience_reward"),
                    ent_data.get("ai_behavior"),
                    json.dumps(ent_data.get("loot_table", [])),
                    json.dumps(ent_data.get("phases", [])),
                ),
            )
        print(f"  Мигрировано {len(data['entities'])} сущностей")

    # Сохраняем изменения
    conn.commit()
    conn.close()

    print("\nМиграция завершена!")


if __name__ == "__main__":
    migrate_data_to_db()
