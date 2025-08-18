#!/usr/bin/env python3
"""Проверка структуры базы данных"""

import sqlite3
from pathlib import Path

def check_database():
    db_path = Path("data/game_data.db")
    
    if not db_path.exists():
        print("База данных не найдена!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Показываем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Найдено таблиц: {len(tables)}")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Показываем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"    Колонки: {len(columns)}")
            for col in columns:
                print(f"      {col[1]} ({col[2]})")
            
            # Показываем количество записей
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    Записей: {count}")
                
                # Показываем первые 3 записи
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    print(f"    Примеры записей:")
                    for i, row in enumerate(rows):
                        print(f"      {i+1}: {row[:3]}...")  # Показываем первые 3 поля
            except Exception as e:
                print(f"    Ошибка чтения данных: {e}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    check_database()
