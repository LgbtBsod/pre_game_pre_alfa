#!/usr/bin/env python3
"""
Скрипт для создания базы данных с правильной структурой.
"""

import sqlite3
import os
from pathlib import Path

def create_database():
    """Создание базы данных с правильной структурой"""
    
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
        # Создание таблицы эффектов с правильной структурой
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

        # Навыки
        cursor.execute("""
            CREATE TABLE skills (
                skill_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
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
                critical_multiplier REAL DEFAULT 1.5
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
                element TEXT DEFAULT 'none',
                FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
            )
        """)

        # Предметы
        cursor.execute("""
            CREATE TABLE items (
                item_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                item_type TEXT NOT NULL,
                rarity TEXT DEFAULT 'common',
                value INTEGER DEFAULT 0,
                weight REAL DEFAULT 0.0,
                icon TEXT DEFAULT ''
            )
        """)

        # Типы врагов (контент)
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

        # Оружие (упрощённая таблица для справочника)
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
        cursor.execute("CREATE INDEX idx_effects_code ON effects(code)")
        cursor.execute("CREATE INDEX idx_effects_type ON effects(effect_type)")
        cursor.execute("CREATE INDEX idx_skills_type ON skills(skill_type)")
        cursor.execute("CREATE INDEX idx_items_type ON items(item_type)")
        cursor.execute("CREATE INDEX idx_enemies_type ON enemy_types(type_id)")
        
        # Коммит изменений
        conn.commit()
        
        print(f"База данных успешно создана: {db_path}")
        for table in ["effects", "skills", "skill_effects", "items", "enemy_types", "weapons"]:
            print(f"Структура таблицы {table}:")
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
