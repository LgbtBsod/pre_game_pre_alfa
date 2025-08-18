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
        
        # Создание индексов
        cursor.execute("CREATE INDEX idx_effects_code ON effects(code)")
        cursor.execute("CREATE INDEX idx_effects_type ON effects(effect_type)")
        
        # Коммит изменений
        conn.commit()
        
        print(f"База данных успешно создана: {db_path}")
        print("Структура таблицы effects:")
        
        # Показать структуру таблицы
        cursor.execute("PRAGMA table_info(effects)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"Ошибка создания базы данных: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
