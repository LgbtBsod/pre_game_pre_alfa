"""
Менеджер атрибутов сущностей.
Объединяет шаблоны из JSON и индивидуальные атрибуты из БД.
"""

import json
import logging
import sqlite3
from typing import Dict, Optional, Any, List
from pathlib import Path
from dataclasses import asdict

from core.attributes import AttributeManager, AttributeTemplateManager

logger = logging.getLogger(__name__)


class EntityAttributeManager:
    """Центральный менеджер атрибутов сущностей"""

    def __init__(self, db_path: str = "data/game_data.db"):
        self.db_path = db_path
        self.template_manager = AttributeTemplateManager()
        self._init_database()

    def _init_database(self):
        """Инициализирует базу данных для атрибутов сущностей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Таблица для атрибутов сущностей
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS entity_attributes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entity_id TEXT NOT NULL,
                        template_id TEXT NOT NULL,
                        current_value REAL NOT NULL,
                        max_value REAL NOT NULL,
                        growth_rate REAL NOT NULL,
                        level INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(entity_id, template_id)
                    )
                """
                )

                # Таблица для прогресса атрибутов
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS attribute_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entity_id TEXT NOT NULL,
                        attribute_points INTEGER DEFAULT 0,
                        total_experience INTEGER DEFAULT 0,
                        last_level_up TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(entity_id)
                    )
                """
                )

                conn.commit()
                logger.info("База данных атрибутов инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации БД атрибутов: {e}")

    def create_entity_attributes(
        self, entity_id: str, template_ids: Dict[str, float], level: int = 1
    ) -> AttributeManager:
        """Создает менеджер атрибутов для новой сущности"""
        attr_manager = AttributeManager(entity_id)

        # Инициализируем из шаблонов
        attr_manager.initialize_from_templates(template_ids)

        # Сохраняем в БД
        self._save_entity_attributes(entity_id, attr_manager)

        return attr_manager

    def load_entity_attributes(self, entity_id: str) -> Optional[AttributeManager]:
        """Загружает атрибуты сущности из БД"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Загружаем атрибуты
                cursor.execute(
                    """
                    SELECT template_id, current_value, max_value, growth_rate, level
                    FROM entity_attributes 
                    WHERE entity_id = ?
                """,
                    (entity_id,),
                )

                attributes_data = cursor.fetchall()

                if not attributes_data:
                    return None

                # Загружаем прогресс
                cursor.execute(
                    """
                    SELECT attribute_points, total_experience
                    FROM attribute_progress 
                    WHERE entity_id = ?
                """,
                    (entity_id,),
                )

                progress_data = cursor.fetchone()
                attribute_points = progress_data[0] if progress_data else 0

                # Создаем менеджер атрибутов
                attr_manager = AttributeManager(entity_id)
                attr_manager.attribute_points = attribute_points

                # Восстанавливаем атрибуты
                for template_id, current, maximum, growth, level in attributes_data:
                    attr = self.template_manager.create_attribute_from_template(
                        template_id, level
                    )
                    if attr:
                        attr.current = current
                        attr.maximum = maximum
                        attr.growth_rate = growth
                        attr_manager.attributes[template_id] = attr

                return attr_manager

        except Exception as e:
            logger.error(f"Ошибка загрузки атрибутов сущности {entity_id}: {e}")
            return None

    def save_entity_attributes(self, entity_id: str, attr_manager: AttributeManager):
        """Сохраняет атрибуты сущности в БД"""
        self._save_entity_attributes(entity_id, attr_manager)

    def _save_entity_attributes(self, entity_id: str, attr_manager: AttributeManager):
        """Внутренний метод сохранения атрибутов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Сохраняем атрибуты
                for template_id, attr in attr_manager.attributes.items():
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO entity_attributes 
                        (entity_id, template_id, current_value, max_value, growth_rate, level, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                        (
                            entity_id,
                            template_id,
                            attr.current,
                            attr.maximum,
                            attr.growth_rate,
                            1,
                        ),
                    )

                # Сохраняем прогресс
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO attribute_progress 
                    (entity_id, attribute_points, total_experience, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (entity_id, attr_manager.attribute_points, 0),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"Ошибка сохранения атрибутов сущности {entity_id}: {e}")

    def get_entity_attribute_summary(self, entity_id: str) -> Dict[str, Any]:
        """Получает сводку атрибутов сущности"""
        attr_manager = self.load_entity_attributes(entity_id)
        if attr_manager:
            return {
                "entity_id": entity_id,
                "attributes": attr_manager.get_attribute_summary(),
                "attribute_points": attr_manager.attribute_points,
                "effects": attr_manager.get_effects_from_attributes(),
            }
        return {}

    def update_entity_attribute(
        self,
        entity_id: str,
        template_id: str,
        current_value: float = None,
        max_value: float = None,
    ):
        """Обновляет конкретный атрибут сущности"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if current_value is not None:
                    cursor.execute(
                        """
                        UPDATE entity_attributes 
                        SET current_value = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE entity_id = ? AND template_id = ?
                    """,
                        (current_value, entity_id, template_id),
                    )

                if max_value is not None:
                    cursor.execute(
                        """
                        UPDATE entity_attributes 
                        SET max_value = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE entity_id = ? AND template_id = ?
                    """,
                        (max_value, entity_id, template_id),
                    )

                conn.commit()

        except Exception as e:
            logger.error(
                f"Ошибка обновления атрибута {template_id} для сущности {entity_id}: {e}"
            )

    def get_all_entity_attributes(self) -> List[Dict[str, Any]]:
        """Получает атрибуты всех сущностей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT ea.entity_id, ea.template_id, ea.current_value, 
                           ea.max_value, ea.growth_rate, ea.level,
                           ap.attribute_points, ap.total_experience
                    FROM entity_attributes ea
                    LEFT JOIN attribute_progress ap ON ea.entity_id = ap.entity_id
                    ORDER BY ea.entity_id, ea.template_id
                """
                )

                results = cursor.fetchall()
                entities = {}

                for row in results:
                    (
                        entity_id,
                        template_id,
                        current,
                        maximum,
                        growth,
                        level,
                        points,
                        exp,
                    ) = row

                    if entity_id not in entities:
                        entities[entity_id] = {
                            "entity_id": entity_id,
                            "attributes": {},
                            "attribute_points": points or 0,
                            "total_experience": exp or 0,
                        }

                    entities[entity_id]["attributes"][template_id] = {
                        "current": current,
                        "maximum": maximum,
                        "growth_rate": growth,
                        "level": level,
                    }

                return list(entities.values())

        except Exception as e:
            logger.error(f"Ошибка получения всех атрибутов: {e}")
            return []

    def export_entity_attributes_to_json(self, file_path: str = None):
        """Экспортирует атрибуты всех сущностей в JSON"""
        if file_path is None:
            file_path = "data/entity_attributes_export.json"

        try:
            entities_data = self.get_all_entity_attributes()

            export_data = {
                "export_timestamp": (
                    str(Path(file_path).stat().st_mtime)
                    if Path(file_path).exists()
                    else "new"
                ),
                "entities": entities_data,
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Атрибуты экспортированы в {file_path}")

        except Exception as e:
            logger.error(f"Ошибка экспорта атрибутов: {e}")

    def import_entity_attributes_from_json(self, file_path: str):
        """Импортирует атрибуты сущностей из JSON"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            entities_data = import_data.get("entities", [])

            for entity_data in entities_data:
                entity_id = entity_data["entity_id"]

                # Создаем менеджер атрибутов
                attr_manager = AttributeManager(entity_id)
                attr_manager.attribute_points = entity_data.get("attribute_points", 0)

                # Восстанавливаем атрибуты
                for template_id, attr_data in entity_data.get("attributes", {}).items():
                    attr = self.template_manager.create_attribute_from_template(
                        template_id
                    )
                    if attr:
                        attr.current = attr_data["current"]
                        attr.maximum = attr_data["maximum"]
                        attr.growth_rate = attr_data["growth_rate"]
                        attr_manager.attributes[template_id] = attr

                # Сохраняем в БД
                self._save_entity_attributes(entity_id, attr_manager)

            logger.info(f"Импортировано {len(entities_data)} сущностей из {file_path}")

        except Exception as e:
            logger.error(f"Ошибка импорта атрибутов: {e}")

    def get_entity_level(self, entity_id: str) -> int:
        """Получает уровень сущности на основе опыта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT total_experience FROM attribute_progress 
                    WHERE entity_id = ?
                """,
                    (entity_id,),
                )

                result = cursor.fetchone()
                if result:
                    total_exp = result[0]
                    # Простая формула уровня (можно настроить)
                    level = 1 + (total_exp // 100)
                    return max(1, min(level, 100))  # Ограничиваем 1-100

                return 1

        except Exception as e:
            logger.error(f"Ошибка получения уровня сущности {entity_id}: {e}")
            return 1

    def add_experience(self, entity_id: str, amount: int):
        """Добавляет опыт сущности"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE attribute_progress 
                    SET total_experience = total_experience + ?, updated_at = CURRENT_TIMESTAMP
                    WHERE entity_id = ?
                """,
                    (amount, entity_id),
                )

                if cursor.rowcount == 0:
                    # Создаем запись если не существует
                    cursor.execute(
                        """
                        INSERT INTO attribute_progress (entity_id, total_experience)
                        VALUES (?, ?)
                    """,
                        (entity_id, amount),
                    )

                conn.commit()

        except Exception as e:
            logger.error(f"Ошибка добавления опыта для сущности {entity_id}: {e}")


# Глобальный экземпляр менеджера
entity_attribute_manager = EntityAttributeManager()
