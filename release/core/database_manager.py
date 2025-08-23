"""
Простой менеджер доступа к SQLite БД контента игры.
Обеспечивает минимально необходимые методы для DataManager.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Any, List
import threading
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Обёртка над SQLite для чтения данных игры."""

    def __init__(self, db_path: str = "data/game_data.db"):
        self.db_path = Path(db_path)
        self._lock = threading.RLock()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # ---- Effects ----
    def get_effects(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            result: Dict[str, Dict[str, Any]] = {}
            if not self.db_path.exists():
                return result
            try:
                conn = self._connect()
                cur = conn.cursor()
                cur.execute("SELECT * FROM effects")
                for row in cur.fetchall():
                    effect_id = row["code"]
                    result[effect_id] = {
                        "id": effect_id,
                        "name": row["name"],
                        "description": row["description"],
                        "type": row["effect_type"],
                        "category": row["attribute"],
                        "duration": row["duration"],
                        "tick_interval": row["tick_interval"],
                        "max_stacks": row["max_stacks"],
                        "stackable": (row["max_stacks"] or 1) > 1,
                        "modifiers": {},  # Можно расширить при необходимости
                        "hex_id": row["guid"],
                    }
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка чтения effects: {e}")
            return result

    # ---- Items ----
    def get_items(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            result: Dict[str, Dict[str, Any]] = {}
            if not self.db_path.exists():
                return result
            try:
                conn = self._connect()
                cur = conn.cursor()
                cur.execute("SELECT * FROM items")
                for row in cur.fetchall():
                    item_id = row["item_id"]
                    result[item_id] = {
                        "id": item_id,
                        "name": row["name"],
                        "description": row["description"],
                        "type": row["item_type"],
                        "slot": None,
                        "rarity": row["rarity"],
                        "level_requirement": 1,
                        "base_damage": 0.0,
                        "attack_speed": 1.0,
                        "damage_type": None,
                        "element": None,
                        "element_damage": 0.0,
                        "defense": 0.0,
                        "weight": row["weight"],
                        "durability": 100,
                        "max_durability": 100,
                        "cost": row["value"],
                        "range": 0.0,
                        "effects": [],
                        "modifiers": {},
                        "tags": [],
                        "resist_mod": {},
                        "weakness_mod": {},
                        "hex_id": None,
                    }
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка чтения items: {e}")
            return result

    def search_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        with self._lock:
            results: List[Dict[str, Any]] = []
            if not self.db_path.exists():
                return results
            try:
                conn = self._connect()
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM items WHERE name LIKE ? OR description LIKE ? LIMIT ?",
                    (f"%{query}%", f"%{query}%", limit),
                )
                for row in cur.fetchall():
                    results.append({
                        "id": row["item_id"],
                        "name": row["name"],
                        "description": row["description"],
                        "type": row["item_type"],
                        "slot": None,
                        "rarity": row["rarity"],
                        "level_requirement": 1,
                        "base_damage": 0.0,
                        "attack_speed": 1.0,
                        "damage_type": None,
                        "element": None,
                        "element_damage": 0.0,
                        "defense": 0.0,
                        "weight": row["weight"],
                        "durability": 100,
                        "max_durability": 100,
                        "cost": row["value"],
                        "range": 0.0,
                        "effects": [],
                        "modifiers": {},
                        "tags": [],
                        "resist_mod": {},
                        "weakness_mod": {},
                        "hex_id": None,
                    })
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка поиска items: {e}")
            return results

    # ---- Entities ----
    def get_entities(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            result: Dict[str, Dict[str, Any]] = {}
            if not self.db_path.exists():
                return result
            try:
                conn = self._connect()
                cur = conn.cursor()
                cur.execute("SELECT * FROM enemy_types")
                for row in cur.fetchall():
                    type_id = row["type_id"]
                    result[type_id] = {
                        "id": type_id,
                        "name": row["name"],
                        "description": row["name"],
                        "type": "enemy",
                        "level": 1,
                        "experience": 0,
                        "base_health": row["base_health"],
                        "base_mana": 0.0,
                        "base_damage": row["base_damage"],
                        "base_armor": row["defense"],
                        "base_speed": row["speed"],
                        "attack_range": 1.0,
                        "ai_type": None,
                        "behavior_pattern": row["behavior"],
                        "difficulty_rating": 1.0,
                        "loot_table": [],
                        "hex_id": None,
                    }
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка чтения enemy_types: {e}")
            return result

    # ---- Attributes (пока нет таблицы) ----
    def get_attributes(self) -> Dict[str, Dict[str, Any]]:
        return {}
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Получить предмет по ID"""
        with self._lock:
            if not self.db_path.exists():
                return None
            try:
                conn = self._connect()
                cur = conn.cursor()
                cur.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
                row = cur.fetchone()
                conn.close()
                
                if row:
                    return {
                        "id": row["item_id"],
                        "name": row["name"],
                        "description": row["description"],
                        "type": row["item_type"],
                        "rarity": row["rarity"],
                        "value": row["value"],
                        "weight": row["weight"],
                        "icon": row["icon"]
                    }
                return None
            except Exception as e:
                logger.error(f"Ошибка получения предмета {item_id}: {e}")
                return None
    
    def get_weapon(self, weapon_id: str) -> Optional[Dict[str, Any]]:
        """Получить оружие по ID"""
        with self._lock:
            if not self.db_path.exists():
                return None
            try:
                conn = self._connect()
                cur = conn.cursor()
                cur.execute("SELECT * FROM weapons WHERE weapon_id = ?", (weapon_id,))
                row = cur.fetchone()
                conn.close()
                
                if row:
                    return {
                        "weapon_id": row["weapon_id"],
                        "name": row["name"],
                        "weapon_type": row["weapon_type"],
                        "damage_type": row["damage_type"],
                        "rarity": row["rarity"],
                        "base_damage": row["base_damage"],
                        "attack_speed": row["attack_speed"]
                    }
                return None
            except Exception as e:
                logger.error(f"Ошибка получения оружия {weapon_id}: {e}")
                return None


# Глобальный экземпляр
database_manager = DatabaseManager()


