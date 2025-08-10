import sqlite3
import json
import os


def analyze_database():
    """Анализирует структуру базы данных"""
    db_path = "data/game_data.db"

    if not os.path.exists(db_path):
        print(f"База данных {db_path} не найдена")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print("Таблицы в базе данных:")
        for table in tables:
            print(f"  - {table[0]}")

        # Анализируем каждую таблицу
        for table in tables:
            table_name = table[0]
            print(f"\nТаблица: {table_name}")

            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            print("  Колонки:")
            for col in columns:
                print(f"    {col[1]} ({col[2]})")

            # Получаем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Записей: {count}")

            # Показываем несколько примеров
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print("  Примеры записей:")
                for row in rows:
                    print(f"    {row}")

        conn.close()

    except Exception as e:
        print(f"Ошибка при анализе базы данных: {e}")


if __name__ == "__main__":
    analyze_database()
