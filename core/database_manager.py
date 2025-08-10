import sqlite3
import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class DatabaseManager:
    """Менеджер базы данных для игровых данных"""

    def __init__(self, db_path: str = "data/game_data.db"):
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Проверяет существование БД и создает её при необходимости"""
        if not os.path.exists(self.db_path):
            self._create_database()

    def _create_database(self):
        """Создает базу данных с необходимыми таблицами"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Создаем таблицы
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS attributes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                base_value REAL DEFAULT 0.0,
                max_value REAL DEFAULT 100.0,
                growth_rate REAL DEFAULT 1.0,
                category TEXT,
                effects TEXT,
                hex_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS effects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                category TEXT,
                tags TEXT,
                modifiers TEXT,
                max_stacks INTEGER DEFAULT 1,
                duration REAL DEFAULT -1.0,
                interval REAL,
                tick_interval REAL,
                stackable INTEGER DEFAULT 0,
                effect_type TEXT,
                hex_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                slot TEXT,
                rarity TEXT,
                level_requirement INTEGER DEFAULT 1,
                base_damage REAL,
                attack_speed REAL,
                defense REAL,
                damage_type TEXT,
                element TEXT,
                element_damage REAL,
                range REAL,
                cost INTEGER DEFAULT 0,
                mana_cost INTEGER,
                critical_chance REAL,
                weight REAL,
                block_chance REAL,
                heal_amount REAL,
                heal_percent REAL,
                mana_amount REAL,
                mana_percent REAL,
                duration REAL,
                cooldown REAL,
                durability INTEGER,
                max_durability INTEGER,
                effects TEXT,
                modifiers TEXT,
                tags TEXT,
                resist_mod TEXT,
                weakness_mod TEXT,
                elemental_resistance TEXT,
                hex_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                experience_to_next INTEGER DEFAULT 100,
                attributes TEXT,
                combat_stats TEXT,
                equipment_slots TEXT,
                inventory_size INTEGER DEFAULT 20,
                skills TEXT,
                tags TEXT,
                enemy_type TEXT,
                experience_reward INTEGER DEFAULT 0,
                ai_behavior TEXT,
                loot_table TEXT,
                phases TEXT
            );
            
            CREATE TABLE IF NOT EXISTS abilities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                ability_type TEXT,
                cooldown REAL DEFAULT 0.0,
                mana_cost INTEGER DEFAULT 0,
                stamina_cost INTEGER DEFAULT 0,
                health_cost INTEGER DEFAULT 0,
                damage REAL DEFAULT 0.0,
                damage_type TEXT,
                range REAL DEFAULT 0.0,
                area_of_effect REAL DEFAULT 0.0,
                effects TEXT,
                requirements TEXT,
                modifiers TEXT
            );
            
            CREATE TABLE IF NOT EXISTS enemies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                enemy_type TEXT,
                level INTEGER DEFAULT 1,
                experience_reward INTEGER DEFAULT 0,
                attributes TEXT,
                combat_stats TEXT,
                ai_behavior TEXT,
                loot_table TEXT,
                skills TEXT,
                tags TEXT,
                phases TEXT
            );
        """
        )

        conn.commit()
        conn.close()

    def get_connection(self):
        """Возвращает соединение с базой данных"""
        return sqlite3.connect(self.db_path)

    def get_attributes(self) -> Dict[str, Any]:
        """Получает все атрибуты из БД"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM attributes")
        rows = cursor.fetchall()

        attributes = {}
        for row in rows:
            attr_id = row[0]
            attributes[attr_id] = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "base_value": row[3],
                "max_value": row[4],
                "growth_rate": row[5],
                "category": row[6],
                "effects": json.loads(row[7]) if row[7] else {},
                "hex_id": row[8],
            }

        conn.close()
        return attributes

    def get_effects(self) -> Dict[str, Any]:
        """Получает все эффекты из БД"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM effects")
        rows = cursor.fetchall()

        effects = {}
        for row in rows:
            eff_id = row[0]
            effects[eff_id] = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "type": row[3],
                "category": row[4],
                "tags": json.loads(row[5]) if row[5] else [],
                "modifiers": json.loads(row[6]) if row[6] else {},
                "max_stacks": row[7],
                "duration": row[8],
                "interval": row[9],
                "tick_interval": row[10],
                "stackable": bool(row[11]),
                "effect_type": row[12],
                "hex_id": row[13],
            }

        conn.close()
        return effects

    def get_items(self) -> Dict[str, Any]:
        """Получает все предметы из БД"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()

        items = {}
        for row in rows:
            item_id = row[0]
            items[item_id] = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "type": row[3],
                "slot": row[4],
                "rarity": row[5],
                "level_requirement": row[6],
                "base_damage": row[7],
                "attack_speed": row[8],
                "defense": row[9],
                "damage_type": row[10],
                "element": row[11],
                "element_damage": row[12],
                "range": row[13],
                "cost": row[14],
                "mana_cost": row[15],
                "critical_chance": row[16],
                "weight": row[17],
                "block_chance": row[18],
                "heal_amount": row[19],
                "heal_percent": row[20],
                "mana_amount": row[21],
                "mana_percent": row[22],
                "duration": row[23],
                "cooldown": row[24],
                "durability": row[25],
                "max_durability": row[26],
                "effects": json.loads(row[27]) if row[27] else [],
                "modifiers": json.loads(row[28]) if row[28] else {},
                "tags": json.loads(row[29]) if row[29] else [],
                "resist_mod": json.loads(row[30]) if row[30] else {},
                "weakness_mod": json.loads(row[31]) if row[31] else {},
                "elemental_resistance": json.loads(row[32]) if row[32] else {},
                "hex_id": row[33],
            }

        conn.close()
        return items

    def get_entities(self) -> Dict[str, Any]:
        """Получает все сущности из БД"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM entities")
        rows = cursor.fetchall()

        entities = {}
        for row in rows:
            ent_id = row[0]
            entities[ent_id] = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "type": row[3],
                "level": row[4],
                "experience": row[5],
                "experience_to_next": row[6],
                "attributes": json.loads(row[7]) if row[7] else {},
                "combat_stats": json.loads(row[8]) if row[8] else {},
                "equipment_slots": json.loads(row[9]) if row[9] else {},
                "inventory_size": row[10],
                "skills": json.loads(row[11]) if row[11] else [],
                "tags": json.loads(row[12]) if row[12] else [],
                "enemy_type": row[13],
                "experience_reward": row[14],
                "ai_behavior": row[15],
                "loot_table": json.loads(row[16]) if row[16] else [],
                "phases": json.loads(row[17]) if row[17] else [],
            }

        conn.close()
        return entities

    def get_enemies(self) -> Dict[str, Any]:
        """Получает всех врагов из БД"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM enemies")
        rows = cursor.fetchall()

        enemies = {}
        for row in rows:
            enemy_id = row[0]
            enemies[enemy_id] = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "enemy_type": row[3],
                "level": row[4],
                "experience_reward": row[5],
                "attributes": json.loads(row[6]) if row[6] else {},
                "combat_stats": json.loads(row[7]) if row[7] else {},
                "ai_behavior": row[8],
                "loot_table": json.loads(row[9]) if row[9] else [],
                "skills": json.loads(row[10]) if row[10] else [],
                "tags": json.loads(row[11]) if row[11] else [],
                "phases": json.loads(row[12]) if row[12] else [],
            }

        conn.close()
        return enemies

    def add_attribute(self, attr_data: Dict[str, Any]) -> bool:
        """Добавляет новый атрибут в БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO attributes 
                (id, name, description, base_value, max_value, growth_rate, category, effects, hex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    attr_data["id"],
                    attr_data["name"],
                    attr_data.get("description"),
                    attr_data.get("base_value", 0.0),
                    attr_data.get("max_value", 100.0),
                    attr_data.get("growth_rate", 1.0),
                    attr_data.get("category"),
                    json.dumps(attr_data.get("effects", {})),
                    attr_data.get("hex_id", attr_data["id"]),
                ),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении атрибута: {e}")
            return False

    def add_effect(self, effect_data: Dict[str, Any]) -> bool:
        """Добавляет новый эффект в БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO effects 
                (id, name, description, type, category, tags, modifiers, max_stacks, duration, 
                 interval, tick_interval, stackable, effect_type, hex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    effect_data["id"],
                    effect_data["name"],
                    effect_data.get("description"),
                    effect_data.get("type"),
                    effect_data.get("category"),
                    json.dumps(effect_data.get("tags", [])),
                    json.dumps(effect_data.get("modifiers", {})),
                    effect_data.get("max_stacks", 1),
                    effect_data.get("duration", -1),
                    effect_data.get("interval"),
                    effect_data.get("tick_interval"),
                    1 if effect_data.get("stackable", False) else 0,
                    effect_data.get("type"),
                    effect_data.get("hex_id", effect_data["id"]),
                ),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении эффекта: {e}")
            return False

    def add_item(self, item_data: Dict[str, Any]) -> bool:
        """Добавляет новый предмет в БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

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
                    item_data["id"],
                    item_data["name"],
                    item_data.get("description"),
                    item_data.get("type"),
                    item_data.get("slot"),
                    item_data.get("rarity"),
                    item_data.get("level_requirement", 1),
                    item_data.get("base_damage"),
                    item_data.get("attack_speed"),
                    item_data.get("defense"),
                    item_data.get("damage_type"),
                    item_data.get("element"),
                    item_data.get("element_damage"),
                    item_data.get("range"),
                    item_data.get("cost", 0),
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
                    item_data.get("hex_id", item_data["id"]),
                ),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении предмета: {e}")
            return False

    def search_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск предметов по названию или описанию"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM items 
            WHERE name LIKE ? OR description LIKE ?
            LIMIT ?
        """,
            (f"%{query}%", f"%{query}%", limit),
        )

        rows = cursor.fetchall()
        items = []

        for row in rows:
            items.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "rarity": row[5],
                    "level_requirement": row[6],
                    "cost": row[14],
                }
            )

        conn.close()
        return items

    def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Получает предметы определенного типа"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items WHERE type = ?", (item_type,))
        rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "rarity": row[5],
                    "level_requirement": row[6],
                    "cost": row[14],
                }
            )

        conn.close()
        return items

    def get_effects_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Получает эффекты определенной категории"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM effects WHERE category = ?", (category,))
        rows = cursor.fetchall()

        effects = []
        for row in rows:
            effects.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "category": row[4],
                    "duration": row[8],
                }
            )

        conn.close()
        return effects
