#!/usr/bin/env python3
"""
Скрипт для создания базы данных с правильной структурой для множественных сессий.
"""

import sqlite3
import os
from pathlib import Path

def create_database():
    """Создание базы данных с правильной структурой для множественных сессий"""
    
    # Создание директории data если её нет
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "game_data.db"
    
    # Удаление существующей базы данных
    if db_path.exists():
        os.remove(db_path)
        print(f"Удалена существующая база данных: {db_path}")
    
    # Создание новой базы данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Таблица слотов сохранения
        cursor.execute("""
            CREATE TABLE save_slots (
                slot_id INTEGER PRIMARY KEY,
                session_uuid TEXT UNIQUE NOT NULL,
                save_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_played TEXT NOT NULL,
                player_level INTEGER DEFAULT 1,
                world_seed INTEGER DEFAULT 0,
                play_time REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Таблица данных сессий
        cursor.execute("""
            CREATE TABLE session_data (
                session_uuid TEXT PRIMARY KEY,
                slot_id INTEGER NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_saved TEXT NOT NULL,
                player_data TEXT,
                world_data TEXT,
                inventory_data TEXT,
                progress_data TEXT,
                generation_seed INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1,
                FOREIGN KEY(slot_id) REFERENCES save_slots(slot_id)
            )
        """)

        # Таблица сгенерированных предметов для сессий
        cursor.execute("""
            CREATE TABLE session_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid TEXT NOT NULL,
                item_id TEXT NOT NULL,
                name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                effects TEXT,
                value INTEGER DEFAULT 0,
                weight REAL DEFAULT 0.0,
                icon TEXT DEFAULT '',
                is_obtained INTEGER DEFAULT 0,
                obtained_at TEXT,
                FOREIGN KEY(session_uuid) REFERENCES session_data(session_uuid)
            )
        """)

        # Таблица сгенерированных врагов для сессий
        cursor.execute("""
            CREATE TABLE session_enemies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid TEXT NOT NULL,
                enemy_id TEXT NOT NULL,
                name TEXT NOT NULL,
                enemy_type TEXT NOT NULL,
                biome TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                stats TEXT NOT NULL,
                resistances TEXT,
                weaknesses TEXT,
                abilities TEXT,
                appearance TEXT,
                behavior_pattern TEXT,
                is_defeated INTEGER DEFAULT 0,
                defeated_at TEXT,
                FOREIGN KEY(session_uuid) REFERENCES session_data(session_uuid)
            )
        """)

        # Таблица сгенерированного оружия для сессий
        cursor.execute("""
            CREATE TABLE session_weapons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid TEXT NOT NULL,
                weapon_id TEXT NOT NULL,
                name TEXT NOT NULL,
                weapon_type TEXT NOT NULL,
                tier INTEGER DEFAULT 1,
                damage REAL NOT NULL,
                effects TEXT,
                requirements TEXT,
                appearance TEXT,
                durability INTEGER DEFAULT 100,
                is_obtained INTEGER DEFAULT 0,
                obtained_at TEXT,
                FOREIGN KEY(session_uuid) REFERENCES session_data(session_uuid)
            )
        """)

        # Таблица сгенерированных навыков для сессий
        cursor.execute("""
            CREATE TABLE session_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid TEXT NOT NULL,
                skill_id TEXT NOT NULL,
                name TEXT NOT NULL,
                skill_type TEXT NOT NULL,
                element TEXT NOT NULL,
                target TEXT NOT NULL,
                base_damage REAL DEFAULT 0.0,
                base_healing REAL DEFAULT 0.0,
                mana_cost REAL DEFAULT 0.0,
                cooldown REAL DEFAULT 0.0,
                range REAL DEFAULT 1.0,
                accuracy REAL DEFAULT 1.0,
                critical_chance REAL DEFAULT 0.05,
                critical_multiplier REAL DEFAULT 1.5,
                is_learned INTEGER DEFAULT 0,
                learned_at TEXT,
                FOREIGN KEY(session_uuid) REFERENCES session_data(session_uuid)
            )
        """)

        # Таблица сгенерированных генов для сессий
        cursor.execute("""
            CREATE TABLE session_genes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid TEXT NOT NULL,
                gene_id TEXT NOT NULL,
                name TEXT NOT NULL,
                gene_type TEXT NOT NULL,
                effect_type TEXT NOT NULL,
                value REAL NOT NULL,
                rarity TEXT NOT NULL,
                description TEXT,
                is_obtained INTEGER DEFAULT 0,
                obtained_at TEXT,
                FOREIGN KEY(session_uuid) REFERENCES session_data(session_uuid)
            )
        """)

        # Справочные таблицы (общие для всех сессий)
        cursor.execute("""
            CREATE TABLE effects (
                guid TEXT PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                effect_type TEXT NOT NULL,
                attribute TEXT NOT NULL,
                value REAL NOT NULL,
                is_percent INTEGER DEFAULT 0,
                duration REAL DEFAULT 0.0,
                tick_interval REAL DEFAULT 1.0,
                max_stacks INTEGER DEFAULT 1,
                description TEXT DEFAULT '',
                icon TEXT DEFAULT ''
            )
        """)

        cursor.execute("""
            CREATE TABLE skill_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id TEXT NOT NULL,
                effect_type TEXT NOT NULL,
                value REAL NOT NULL,
                duration REAL DEFAULT 0.0,
                chance REAL DEFAULT 1.0,
                scaling TEXT DEFAULT 'linear',
                element TEXT DEFAULT 'none'
            )
        """)

        cursor.execute("""
            CREATE TABLE enemy_types (
                type_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                base_health REAL DEFAULT 100.0,
                base_damage REAL DEFAULT 10.0,
                speed REAL DEFAULT 1.0,
                defense REAL DEFAULT 5.0,
                behavior TEXT DEFAULT 'balanced'
            )
        """)

        cursor.execute("""
            CREATE TABLE weapons (
                weapon_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                weapon_type TEXT NOT NULL,
                damage_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                base_damage REAL NOT NULL,
                attack_speed REAL DEFAULT 1.0
            )
        """)

        # Создание индексов
        cursor.execute("CREATE INDEX idx_save_slots_active ON save_slots(is_active)")
        cursor.execute("CREATE INDEX idx_session_data_slot ON session_data(slot_id)")
        cursor.execute("CREATE INDEX idx_session_items_uuid ON session_items(session_uuid)")
        cursor.execute("CREATE INDEX idx_session_enemies_uuid ON session_enemies(session_uuid)")
        cursor.execute("CREATE INDEX idx_session_weapons_uuid ON session_weapons(session_uuid)")
        cursor.execute("CREATE INDEX idx_session_skills_uuid ON session_skills(session_uuid)")
        cursor.execute("CREATE INDEX idx_session_genes_uuid ON session_genes(session_uuid)")
        cursor.execute("CREATE INDEX idx_effects_code ON effects(code)")
        cursor.execute("CREATE INDEX idx_effects_type ON effects(effect_type)")
        cursor.execute("CREATE INDEX idx_enemy_types_type ON enemy_types(type_id)")
        
        # Коммит изменений
        conn.commit()
        
        print(f"База данных успешно создана: {db_path}")
        print("\nСтруктура таблиц:")
        for table in ["save_slots", "session_data", "session_items", "session_enemies", 
                     "session_weapons", "session_skills", "session_genes", "effects", 
                     "skill_effects", "enemy_types", "weapons"]:
            print(f"\nТаблица {table}:")
            cursor.execute(f"PRAGMA table_info({table})")
            for col in cursor.fetchall():
                print(f"  - {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"Ошибка создания базы данных: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
