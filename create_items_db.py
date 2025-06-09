# create_item_db.py

import sqlite3
import json
import os


DB_PATH = 'assets/items.db'
JSON_PATH = 'assets/artifacts.json'


def init_db():
    """Создаёт таблицу artifacts, если её нет"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                stats TEXT,
                effect TEXT,
                trigger TEXT,
                subscribe TEXT
            )
        ''')
        conn.commit()


def load_json_data(path):
    """Загружает JSON-данные из файла"""
    if not os.path.exists(path):
        raise FileNotFoundError(f'Файл {path} не найден!')

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def insert_artifact(cursor, artifact):
    """Добавляет один артефакт в базу данных"""
    name = artifact.get('name')
    stats = json.dumps(artifact.get('stats', {}))
    effect = json.dumps(artifact.get('effect', {}))
    trigger = artifact.get('trigger', 'passive')
    subscribe = artifact.get('subscribe', '')

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO artifacts (name, stats, effect, trigger, subscribe)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, stats, effect, trigger, subscribe))
    except sqlite3.Error as e:
        print(f'[Ошибка] Не удалось добавить предмет "{name}": {e}')


def main():
    init_db()

    try:
        data = load_json_data(JSON_PATH)
    except Exception as e:
        print(f'[Ошибка] При загрузке JSON: {e}')
        return

    added_count = 0
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for artifact in data.values():
            insert_artifact(cursor, artifact)
            if cursor.rowcount > 0:
                added_count += 1

        conn.commit()

    print(f'[OK] Успешно добавлено: {added_count} новых предметов')


if __name__ == '__main__':
    main()