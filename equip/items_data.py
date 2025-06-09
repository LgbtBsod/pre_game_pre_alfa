# game_data/items_data.py
import sqlite3
import json
from typing import List, Dict, Callable, Optional, Any

class ItemsData:
    _instance = None
    items_db: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_items_data()
        return cls._instance

    @classmethod
    def _load_items_data(cls):
        """Загружает все данные предметов из БД один раз при старте игры"""
        try:
            conn = sqlite3.connect('assets/items.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, stats, effect, trigger, type, icon FROM artifacts")
            
            for row in cursor.fetchall():
                name, stats, effect, trigger, item_type, icon = row
                cls.items_db[name] = {
                    'stats': json.loads(stats) if stats else {},
                    'effect': effect,
                    'trigger': trigger,
                    'type': item_type,
                    'icon': icon
                }
            print(f"[ItemsData] Loaded {len(cls.items_db)} items")
        except Exception as e:
            print(f"[ItemsData] Error loading items: {e}")
        finally:
            conn.close()

    @classmethod
    def get_item(cls, item_name: str) -> Optional[Dict[str, Any]]:
        """Получает данные предмета по имени"""
        return cls.items_db.get(item_name)

    @classmethod
    def get_all_items(cls) -> Dict[str, Dict[str, Any]]:
        """Возвращает все загруженные предметы"""
        return cls.items_db