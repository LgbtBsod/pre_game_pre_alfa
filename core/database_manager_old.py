import sqlite3
import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


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

        # Создаем таблицы для игровых сущностей
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
                base_health REAL,
                base_mana REAL,
                base_armor REAL,
                base_speed REAL,
                attack_range REAL,
                ai_type TEXT,
                behavior_pattern TEXT,
                difficulty_rating REAL,
                loot_table TEXT,
                hex_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS entity_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                base_level INTEGER DEFAULT 1,
                base_experience INTEGER DEFAULT 0,
                base_attributes TEXT,
                base_combat_stats TEXT,
                equipment_slots TEXT,
                inventory_size INTEGER DEFAULT 20,
                base_skills TEXT,
                tags TEXT,
                ai_behavior TEXT DEFAULT 'passive',
                loot_table TEXT,
                spawn_conditions TEXT,
                hex_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS item_templates (
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
            
            CREATE TABLE IF NOT EXISTS abilities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                category TEXT,
                level_requirement INTEGER DEFAULT 1,
                mana_cost INTEGER DEFAULT 0,
                cooldown REAL DEFAULT 0.0,
                duration REAL DEFAULT 0.0,
                range REAL DEFAULT 0.0,
                area_of_effect REAL DEFAULT 0.0,
                base_damage REAL DEFAULT 0.0,
                damage_type TEXT,
                element TEXT,
                effects TEXT,
                modifiers TEXT,
                tags TEXT,
                hex_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                max_level INTEGER DEFAULT 1,
                base_value REAL DEFAULT 0.0,
                growth_rate REAL DEFAULT 1.0,
                requirements TEXT,
                effects TEXT,
                modifiers TEXT,
                tags TEXT,
                hex_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS quests (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                category TEXT,
                level_requirement INTEGER DEFAULT 1,
                objectives TEXT,
                rewards TEXT,
                prerequisites TEXT,
                time_limit REAL DEFAULT -1.0,
                repeatable INTEGER DEFAULT 0,
                hex_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                category TEXT,
                coordinates TEXT,
                connections TEXT,
                entities TEXT,
                items TEXT,
                hazards TEXT,
                hex_id TEXT
            );
            """
        )

        conn.commit()
        conn.close()
        logger.info("База данных создана успешно")

    def get_connection(self):
        """Получает соединение с базой данных"""
        return sqlite3.connect(self.db_path)

    def get_attributes(self) -> Dict[str, Any]:
        """Получает все атрибуты из БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM attributes")
            rows = cursor.fetchall()
            conn.close()

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
                    "effects": json.loads(row[7]) if row[7] else [],
                    "hex_id": row[8]
                }

            return attributes
        except Exception as e:
            logger.error(f"Ошибка получения атрибутов: {e}")
            return {}

    def get_effects(self) -> Dict[str, Any]:
        """Получает все эффекты из БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM effects")
            rows = cursor.fetchall()
            conn.close()

            effects = {}
            for row in rows:
                effect_id = row[0]
                effects[effect_id] = {
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
                    "hex_id": row[13]
                }

            return effects
        except Exception as e:
            logger.error(f"Ошибка получения эффектов: {e}")
            return {}

    def get_items(self) -> Dict[str, Any]:
        """Получает все предметы из БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items")
            rows = cursor.fetchall()
            conn.close()

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
                    "resist_mod": row[30],
                    "weakness_mod": row[31],
                    "elemental_resistance": row[32],
                    "hex_id": row[33]
                }

            return items
        except Exception as e:
            logger.error(f"Ошибка получения предметов: {e}")
            return {}

    def get_entities(self) -> Dict[str, Any]:
        """Получает все сущности из БД"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM entities")
        rows = cursor.fetchall()
        
        entities = {}
        for row in rows:
            entity_id = row[0]
            entities[entity_id] = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "type": row[3],
                "level": row[4],
                "experience": row[5],
                "experience_to_next": row[6],
                "attributes": json.loads(row[7]) if row[7] else {},
                "combat_stats": json.loads(row[8]) if row[8] else {},
                "equipment_slots": json.loads(row[9]) if row[9] else [],
                "inventory_size": row[10],
                "skills": json.loads(row[11]) if row[11] else [],
                "tags": json.loads(row[12]) if row[12] else [],
                "hex_id": row[13]
            }
        
        conn.close()
        return entities

    def get_entity_templates(self) -> Dict[str, Any]:
        """Получает шаблоны сущностей для создания новых экземпляров"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM entity_templates")
        rows = cursor.fetchall()
        
        templates = {}
        for row in rows:
            template_id = row[0]
            templates[template_id] = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "type": row[3],
                "base_level": row[4],
                "base_experience": row[5],
                "base_attributes": json.loads(row[6]) if row[6] else {},
                "base_combat_stats": json.loads(row[7]) if row[7] else {},
                "equipment_slots": json.loads(row[8]) if row[8] else [],
                "inventory_size": row[9],
                "base_skills": json.loads(row[10]) if row[10] else [],
                "tags": json.loads(row[11]) if row[11] else [],
                "ai_behavior": row[12],
                "loot_table": json.loads(row[13]) if row[13] else [],
                "spawn_conditions": json.loads(row[14]) if row[14] else {},
                "hex_id": row[15]
            }
        
        conn.close()
        return templates

    def get_item_templates(self) -> Dict[str, Any]:
        """Получает шаблоны предметов для создания новых экземпляров"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM item_templates")
        rows = cursor.fetchall()
        
        templates = {}
        for row in rows:
            template_id = row[0]
            templates[template_id] = {
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
                "hex_id": row[33]
            }
        
        conn.close()
        return templates

    def add_entity_template(self, template_data: Dict[str, Any]) -> bool:
        """Добавляет новый шаблон сущности"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO entity_templates (
                    id, name, description, type, base_level, base_experience,
                    base_attributes, base_combat_stats, equipment_slots,
                    inventory_size, base_skills, tags, ai_behavior,
                    loot_table, spawn_conditions, hex_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_data.get('id'),
                template_data.get('name'),
                template_data.get('description'),
                template_data.get('type'),
                template_data.get('base_level', 1),
                template_data.get('base_experience', 0),
                json.dumps(template_data.get('base_attributes', {})),
                json.dumps(template_data.get('base_combat_stats', {})),
                json.dumps(template_data.get('equipment_slots', [])),
                template_data.get('inventory_size', 20),
                json.dumps(template_data.get('base_skills', [])),
                json.dumps(template_data.get('tags', [])),
                template_data.get('ai_behavior', 'passive'),
                json.dumps(template_data.get('loot_table', [])),
                json.dumps(template_data.get('spawn_conditions', {})),
                template_data.get('hex_id')
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Entity template {template_data.get('id')} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding entity template: {e}")
            return False

    def add_item_template(self, template_data: Dict[str, Any]) -> bool:
        """Добавляет новый шаблон предмета"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO item_templates (
                    id, name, description, type, slot, rarity, level_requirement,
                    base_damage, attack_speed, defense, damage_type, element,
                    element_damage, range, cost, mana_cost, critical_chance,
                    weight, block_chance, heal_amount, heal_percent, mana_amount,
                    mana_percent, duration, cooldown, durability, max_durability,
                    effects, modifiers, tags, resist_mod, weakness_mod,
                    elemental_resistance, hex_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_data.get('id'),
                template_data.get('name'),
                template_data.get('description'),
                template_data.get('type'),
                template_data.get('slot'),
                template_data.get('rarity'),
                template_data.get('level_requirement', 1),
                template_data.get('base_damage'),
                template_data.get('attack_speed'),
                template_data.get('defense'),
                template_data.get('damage_type'),
                template_data.get('element'),
                template_data.get('element_damage'),
                template_data.get('range'),
                template_data.get('cost', 0),
                template_data.get('mana_cost'),
                template_data.get('critical_chance'),
                template_data.get('weight'),
                template_data.get('block_chance'),
                template_data.get('heal_amount'),
                template_data.get('heal_percent'),
                template_data.get('mana_amount'),
                template_data.get('mana_percent'),
                template_data.get('duration'),
                template_data.get('cooldown'),
                template_data.get('durability'),
                template_data.get('max_durability'),
                json.dumps(template_data.get('effects', [])),
                json.dumps(template_data.get('modifiers', {})),
                json.dumps(template_data.get('tags', [])),
                json.dumps(template_data.get('resist_mod', {})),
                json.dumps(template_data.get('weakness_mod', {})),
                json.dumps(template_data.get('elemental_resistance', {})),
                template_data.get('hex_id')
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Item template {template_data.get('id')} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding item template: {e}")
            return False

    def migrate_json_to_database(self):
        """Мигрирует данные из JSON файлов в базу данных"""
        try:
            # Создаем таблицы для шаблонов если их нет
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS entity_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT,
                    base_level INTEGER DEFAULT 1,
                    base_experience INTEGER DEFAULT 0,
                    base_attributes TEXT,
                    base_combat_stats TEXT,
                    equipment_slots TEXT,
                    inventory_size INTEGER DEFAULT 20,
                    base_skills TEXT,
                    tags TEXT,
                    ai_behavior TEXT DEFAULT 'passive',
                    loot_table TEXT,
                    spawn_conditions TEXT,
                    hex_id TEXT
                );
                
                CREATE TABLE IF NOT EXISTS item_templates (
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
            """)
            
            conn.commit()
            conn.close()
            
            # Мигрируем данные из JSON файлов
            self._migrate_entities_json()
            self._migrate_items_json()
            
            logger.info("JSON to database migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during JSON to database migration: {e}")
            return False

    def _migrate_entities_json(self):
        """Мигрирует данные сущностей из JSON в БД"""
        try:
            entities_file = Path("data/entities.json")
            if not entities_file.exists():
                logger.warning("entities.json not found, skipping migration")
                return
            
            with open(entities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for entity_id, entity_data in data.get('entities', {}).items():
                # Создаем шаблон сущности
                template_data = {
                    'id': entity_id,
                    'name': entity_data.get('name', ''),
                    'description': entity_data.get('description', ''),
                    'type': entity_data.get('type', ''),
                    'base_level': entity_data.get('level', 1),
                    'base_experience': entity_data.get('experience', 0),
                    'base_attributes': entity_data.get('attributes', {}),
                    'base_combat_stats': entity_data.get('combat_stats', {}),
                    'equipment_slots': entity_data.get('equipment_slots', []),
                    'inventory_size': entity_data.get('inventory_size', 20),
                    'base_skills': entity_data.get('skills', []),
                    'tags': entity_data.get('tags', []),
                    'ai_behavior': entity_data.get('ai_behavior', 'passive'),
                    'loot_table': entity_data.get('loot_table', []),
                    'spawn_conditions': {},
                    'hex_id': entity_data.get('hex_id', entity_id)
                }
                
                self.add_entity_template(template_data)
            
            logger.info("Entities JSON migration completed")
            
        except Exception as e:
            logger.error(f"Error migrating entities JSON: {e}")

    def _migrate_items_json(self):
        """Мигрирует данные предметов из JSON в БД"""
        try:
            items_file = Path("data/items.json")
            if not items_file.exists():
                logger.warning("items.json not found, skipping migration")
                return
            
            with open(items_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item_id, item_data in data.get('items', {}).items():
                # Создаем шаблон предмета
                template_data = {
                    'id': item_id,
                    'name': item_data.get('name', ''),
                    'description': item_data.get('description', ''),
                    'type': item_data.get('type', ''),
                    'slot': item_data.get('slot', ''),
                    'rarity': item_data.get('rarity', 'common'),
                    'level_requirement': item_data.get('level_requirement', 1),
                    'base_damage': item_data.get('base_damage'),
                    'attack_speed': item_data.get('attack_speed'),
                    'defense': item_data.get('defense'),
                    'damage_type': item_data.get('damage_type'),
                    'element': item_data.get('element'),
                    'element_damage': item_data.get('element_damage'),
                    'range': item_data.get('range'),
                    'cost': item_data.get('cost', 0),
                    'mana_cost': item_data.get('mana_cost'),
                    'critical_chance': item_data.get('critical_chance'),
                    'weight': item_data.get('weight'),
                    'block_chance': item_data.get('block_chance'),
                    'heal_amount': item_data.get('heal_amount'),
                    'heal_percent': item_data.get('heal_percent'),
                    'mana_amount': item_data.get('mana_amount'),
                    'mana_percent': item_data.get('mana_percent'),
                    'duration': item_data.get('duration'),
                    'cooldown': item_data.get('cooldown'),
                    'durability': item_data.get('durability'),
                    'max_durability': item_data.get('max_durability'),
                    'effects': item_data.get('effects', []),
                    'modifiers': item_data.get('modifiers', {}),
                    'tags': item_data.get('tags', []),
                    'resist_mod': item_data.get('resist_mod', {}),
                    'weakness_mod': item_data.get('weakness_mod', {}),
                    'elemental_resistance': item_data.get('elemental_resistance', {}),
                    'hex_id': item_data.get('hex_id', item_id)
                }
                
                self.add_item_template(template_data)
            
            logger.info("Items JSON migration completed")
            
        except Exception as e:
            logger.error(f"Error migrating items JSON: {e}")

    def get_enemies(self) -> Dict[str, Any]:
        """Получает всех врагов из БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE type = 'enemy'")
            rows = cursor.fetchall()
            conn.close()

            enemies = {}
            for row in rows:
                enemy_id = row[0]
                enemies[enemy_id] = {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "level": row[4],
                    "experience": row[5],
                    "base_health": row[6],
                    "base_mana": row[7],
                    "base_damage": row[8],
                    "base_armor": row[9],
                    "base_speed": row[10],
                    "attack_range": row[11],
                    "ai_type": row[12],
                    "behavior_pattern": row[13],
                    "difficulty_rating": row[14],
                    "loot_table": json.loads(row[15]) if row[15] else [],
                    "hex_id": row[16]
                }

            return enemies
        except Exception as e:
            logger.error(f"Ошибка получения врагов: {e}")
            return {}

    def add_attribute(self, attr_data: Dict[str, Any]) -> bool:
        """Добавляет новый атрибут в БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO attributes 
                (id, name, description, base_value, max_value, growth_rate, category, effects, hex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attr_data.get("id"),
                attr_data.get("name"),
                attr_data.get("description"),
                attr_data.get("base_value", 0.0),
                attr_data.get("max_value", 100.0),
                attr_data.get("growth_rate", 1.0),
                attr_data.get("category"),
                json.dumps(attr_data.get("effects", [])),
                attr_data.get("hex_id")
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Атрибут {attr_data.get('name')} добавлен в БД")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления атрибута: {e}")
            return False

    def add_effect(self, effect_data: Dict[str, Any]) -> bool:
        """Добавляет новый эффект в БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO effects 
                (id, name, description, type, category, tags, modifiers, max_stacks, duration, interval, tick_interval, stackable, effect_type, hex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                effect_data.get("id"),
                effect_data.get("name"),
                effect_data.get("description"),
                effect_data.get("type"),
                effect_data.get("category"),
                json.dumps(effect_data.get("tags", [])),
                json.dumps(effect_data.get("modifiers", {})),
                effect_data.get("max_stacks", 1),
                effect_data.get("duration", -1.0),
                effect_data.get("interval"),
                effect_data.get("tick_interval"),
                int(effect_data.get("stackable", False)),
                effect_data.get("effect_type"),
                effect_data.get("hex_id")
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Эффект {effect_data.get('name')} добавлен в БД")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления эффекта: {e}")
            return False

    def add_item(self, item_data: Dict[str, Any]) -> bool:
        """Добавляет новый предмет в БД"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO items 
                (id, name, description, type, slot, rarity, level_requirement, base_damage, attack_speed, defense, damage_type, element, element_damage, range, cost, mana_cost, critical_chance, weight, block_chance, heal_amount, heal_percent, mana_amount, mana_percent, duration, cooldown, durability, max_durability, effects, modifiers, tags, resist_mod, weakness_mod, elemental_resistance, hex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_data.get("id"),
                item_data.get("name"),
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
                item_data.get("resist_mod"),
                item_data.get("weakness_mod"),
                item_data.get("elemental_resistance"),
                item_data.get("hex_id")
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Предмет {item_data.get('name')} добавлен в БД")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления предмета: {e}")
            return False

    def search_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Ищет предметы по запросу"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM items 
                WHERE name LIKE ? OR description LIKE ? OR type LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
            
            rows = cursor.fetchall()
            conn.close()

            items = []
            for row in rows:
                items.append({
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
                    "resist_mod": row[30],
                    "weakness_mod": row[31],
                    "elemental_resistance": row[32],
                    "hex_id": row[33]
                })

            return items
        except Exception as e:
            logger.error(f"Ошибка поиска предметов: {e}")
            return []

    def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Получает предметы определенного типа"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM items WHERE type = ?", (item_type,))
            rows = cursor.fetchall()
            conn.close()

            items = []
            for row in rows:
                items.append({
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
                    "resist_mod": row[30],
                    "weakness_mod": row[31],
                    "elemental_resistance": row[32],
                    "hex_id": row[33]
                })

            return items
        except Exception as e:
            logger.error(f"Ошибка получения предметов по типу: {e}")
            return []

    def get_effects_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Получает эффекты определенной категории"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM effects WHERE category = ?", (category,))
            rows = cursor.fetchall()
            conn.close()

            effects = []
            for row in rows:
                effects.append({
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
                    "hex_id": row[13]
                })

            return effects
        except Exception as e:
            logger.error(f"Ошибка получения эффектов по категории: {e}")
            return []

    def backup_database(self, backup_path: str = None) -> bool:
        """Создает резервную копию базы данных"""
        try:
            if backup_path is None:
                backup_dir = Path("backup")
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"game_data_{timestamp}.db.backup"
            
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Резервная копия БД создана: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии БД: {e}")
            return False

    def restore_database(self, backup_path: str) -> bool:
        """Восстанавливает базу данных из резервной копии"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Файл резервной копии не найден: {backup_path}")
                return False
            
            import shutil
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"БД восстановлена из резервной копии: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка восстановления БД: {e}")
            return False

    def migrate_entity_config_to_database(self, config_data: Dict[str, Any]) -> bool:
        """Мигрирует настройки сущностей из JSON конфигурации в базу данных"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for entity_type, entity_config in config_data.items():
                # Создаем шаблон сущности
                template_data = {
                    'id': f"{entity_type}_template",
                    'name': entity_type.capitalize(),
                    'type': entity_type,
                    'base_stats': json.dumps(entity_config.get('base_stats', {})),
                    'leveling': json.dumps(entity_config.get('leveling', {})),
                    'ai_behavior': json.dumps(entity_config.get('ai_behavior', {})),
                    'loot': json.dumps(entity_config.get('loot', {})),
                    'inventory': json.dumps(entity_config.get('inventory', {})),
                    'interaction': json.dumps(entity_config.get('interaction', {})),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Добавляем или обновляем шаблон
                self.add_entity_template(template_data)
                
            conn.commit()
            logger.info(f"Successfully migrated {len(config_data)} entity types to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate entity config to database: {e}")
            return False

    def get_entity_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Получает конфигурацию сущности из базы данных"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM entity_templates 
                WHERE type = ? AND is_active = 1
                ORDER BY created_at DESC 
                LIMIT 1
            """, (entity_type,))
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                entity_data = dict(zip(columns, row))
                
                # Парсим JSON поля
                for field in ['base_stats', 'leveling', 'ai_behavior', 'loot', 'inventory', 'interaction']:
                    if entity_data.get(field):
                        try:
                            entity_data[field] = json.loads(entity_data[field])
                        except json.JSONDecodeError:
                            entity_data[field] = {}
                
                return entity_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get entity config for {entity_type}: {e}")
            return None

    def get_all_entity_configs(self) -> Dict[str, Any]:
        """Получает все конфигурации сущностей из базы данных"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM entity_templates 
                WHERE is_active = 1
                ORDER BY type, created_at DESC
            """)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            configs = {}
            for row in rows:
                entity_data = dict(zip(columns, row))
                entity_type = entity_data['type']
                
                # Парсим JSON поля
                for field in ['base_stats', 'leveling', 'ai_behavior', 'loot', 'inventory', 'interaction']:
                    if entity_data.get(field):
                        try:
                            entity_data[field] = json.loads(entity_data[field])
                        except json.JSONDecodeError:
                            entity_data[field] = {}
                
                configs[entity_type] = entity_data
            
            return configs
            
        except Exception as e:
            logger.error(f"Failed to get all entity configs: {e}")
            return {}


# Глобальный экземпляр менеджера БД
database_manager = DatabaseManager()
