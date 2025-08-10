"""
Скрипт для конвертации существующих JSON файлов в 16-ричные ID.
Конвертирует ID сущностей, предметов и эффектов в новый формат.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from utils.entity_id_generator import (
    EntityType,
    convert_legacy_id,
    legacy_converter,
    id_generator,
)


class JSONConverter:
    """Конвертер JSON файлов в 16-ричные ID"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.conversion_log = []

    def convert_all_files(self):
        """Конвертирует все JSON файлы"""
        print("Начинаем конвертацию JSON файлов в 16-ричные ID...")

        # Конвертируем файлы
        self.convert_entities()
        self.convert_items()
        self.convert_effects()
        self.convert_abilities()

        # Сохраняем лог конвертации
        self.save_conversion_log()

        print("Конвертация завершена!")
        print(f"Статистика генератора ID: {id_generator.get_stats()}")

    def convert_entities(self):
        """Конвертирует entities.json"""
        file_path = self.data_dir / "entities.json"
        if not file_path.exists():
            print(f"Файл {file_path} не найден")
            return

        print(f"Конвертируем {file_path}...")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        converted_data = {"entities": {}}

        for entity_id, entity_data in data.get("entities", {}).items():
            # Определяем тип сущности
            entity_type = self._determine_entity_type_from_data(entity_data)

            # Конвертируем ID
            new_id = convert_legacy_id(entity_id, entity_type)

            # Обновляем данные
            entity_data["id"] = new_id
            entity_data["hex_id"] = new_id

            # Конвертируем связанные ID
            entity_data = self._convert_related_ids(entity_data, entity_type)

            converted_data["entities"][new_id] = entity_data

            self.conversion_log.append(
                {
                    "file": "entities.json",
                    "old_id": entity_id,
                    "new_id": new_id,
                    "type": entity_type.value,
                }
            )

        # Сохраняем с резервной копией
        self._save_with_backup(file_path, converted_data)

    def convert_items(self):
        """Конвертирует items.json"""
        file_path = self.data_dir / "items.json"
        if not file_path.exists():
            print(f"Файл {file_path} не найден")
            return

        print(f"Конвертируем {file_path}...")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        converted_data = {"items": {}}

        for item_id, item_data in data.get("items", {}).items():
            # Конвертируем ID предмета
            new_id = convert_legacy_id(item_id, EntityType.ITEM)

            # Обновляем данные
            item_data["id"] = new_id
            item_data["hex_id"] = new_id

            # Конвертируем связанные ID
            item_data = self._convert_related_ids(item_data, EntityType.ITEM)

            converted_data["items"][new_id] = item_data

            self.conversion_log.append(
                {
                    "file": "items.json",
                    "old_id": item_id,
                    "new_id": new_id,
                    "type": "item",
                }
            )

        # Сохраняем комбинации элементов
        if "elemental_combinations" in data:
            converted_data["elemental_combinations"] = data["elemental_combinations"]

        if "effect_combinations" in data:
            converted_data["effect_combinations"] = data["effect_combinations"]

        # Сохраняем с резервной копией
        self._save_with_backup(file_path, converted_data)

    def convert_effects(self):
        """Конвертирует effects.json"""
        file_path = self.data_dir / "effects.json"
        if not file_path.exists():
            print(f"Файл {file_path} не найден")
            return

        print(f"Конвертируем {file_path}...")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        converted_data = {"effects": {}}

        for effect_id, effect_data in data.get("effects", {}).items():
            # Конвертируем ID эффекта
            new_id = convert_legacy_id(effect_id, EntityType.EFFECT)

            # Обновляем данные
            effect_data["id"] = new_id
            effect_data["hex_id"] = new_id

            converted_data["effects"][new_id] = effect_data

            self.conversion_log.append(
                {
                    "file": "effects.json",
                    "old_id": effect_id,
                    "new_id": new_id,
                    "type": "effect",
                }
            )

        # Сохраняем с резервной копией
        self._save_with_backup(file_path, converted_data)

    def convert_abilities(self):
        """Конвертирует abilities.json"""
        file_path = self.data_dir / "abilities.json"
        if not file_path.exists():
            print(f"Файл {file_path} не найден")
            return

        print(f"Конвертируем {file_path}...")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        converted_data = {"abilities": {}}

        for ability_id, ability_data in data.get("abilities", {}).items():
            # Конвертируем ID способности
            new_id = convert_legacy_id(ability_id, EntityType.EFFECT)

            # Обновляем данные
            ability_data["id"] = new_id
            ability_data["hex_id"] = new_id

            # Конвертируем связанные ID
            ability_data = self._convert_related_ids(ability_data, EntityType.EFFECT)

            converted_data["abilities"][new_id] = ability_data

            self.conversion_log.append(
                {
                    "file": "abilities.json",
                    "old_id": ability_id,
                    "new_id": new_id,
                    "type": "ability",
                }
            )

        # Сохраняем с резервной копией
        self._save_with_backup(file_path, converted_data)

    def _determine_entity_type_from_data(
        self, entity_data: Dict[str, Any]
    ) -> EntityType:
        """Определяет тип сущности из данных"""
        entity_type = entity_data.get("type", "").lower()

        if entity_type == "boss":
            return EntityType.BOSS
        elif entity_type == "enemy":
            return EntityType.ENEMY
        elif entity_type == "player":
            return EntityType.PLAYER
        elif entity_type == "npc":
            return EntityType.NPC
        else:
            return EntityType.AI_ENTITY

    def _convert_related_ids(
        self, data: Dict[str, Any], parent_type: EntityType
    ) -> Dict[str, Any]:
        """Конвертирует связанные ID в данных"""
        # Конвертируем атрибуты
        if "attributes" in data:
            converted_attrs = {}
            for attr_id, value in data["attributes"].items():
                new_attr_id = convert_legacy_id(attr_id, EntityType.EFFECT)
                converted_attrs[new_attr_id] = value
            data["attributes"] = converted_attrs

        # Конвертируем эффекты
        if "effects" in data:
            converted_effects = []
            for effect_id in data["effects"]:
                new_effect_id = convert_legacy_id(effect_id, EntityType.EFFECT)
                converted_effects.append(new_effect_id)
            data["effects"] = converted_effects

        # Конвертируем навыки
        if "skills" in data:
            converted_skills = []
            for skill_id in data["skills"]:
                new_skill_id = convert_legacy_id(skill_id, EntityType.EFFECT)
                converted_skills.append(new_skill_id)
            data["skills"] = converted_skills

        # Конвертируем таблицу лута
        if "loot_table" in data:
            converted_loot = []
            for item_id in data["loot_table"]:
                new_item_id = convert_legacy_id(item_id, EntityType.ITEM)
                converted_loot.append(new_item_id)
            data["loot_table"] = converted_loot

        # Конвертируем фазы босса
        if "phases" in data:
            for phase in data["phases"]:
                if "effects" in phase:
                    converted_phase_effects = []
                    for effect_id in phase["effects"]:
                        new_effect_id = convert_legacy_id(effect_id, EntityType.EFFECT)
                        converted_phase_effects.append(new_effect_id)
                    phase["effects"] = converted_phase_effects

                if "skills" in phase:
                    converted_phase_skills = []
                    for skill_id in phase["skills"]:
                        new_skill_id = convert_legacy_id(skill_id, EntityType.EFFECT)
                        converted_phase_skills.append(new_skill_id)
                    phase["skills"] = converted_phase_skills

        return data

    def _save_with_backup(self, file_path: Path, data: Dict[str, Any]):
        """Сохраняет файл с созданием резервной копии"""
        # Создаем резервную копию
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        if file_path.exists():
            file_path.rename(backup_path)
            print(f"Создана резервная копия: {backup_path}")

        # Сохраняем новый файл
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Сохранен файл: {file_path}")

    def save_conversion_log(self):
        """Сохраняет лог конвертации"""
        log_path = self.data_dir / "conversion_log.json"

        log_data = {
            "conversion_date": str(Path().cwd()),
            "total_converted": len(self.conversion_log),
            "conversions": self.conversion_log,
            "conversion_map": legacy_converter.get_conversion_map(),
        }

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print(f"Лог конвертации сохранен: {log_path}")


def main():
    """Основная функция"""
    print("=== Конвертер JSON файлов в 16-ричные ID ===")

    # Проверяем аргументы командной строки
    data_dir = "data"
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]

    # Создаем конвертер и запускаем
    converter = JSONConverter(data_dir)
    converter.convert_all_files()

    print("\n=== Статистика конвертации ===")
    print(f"Всего конвертировано: {len(converter.conversion_log)}")

    # Группируем по типам
    type_counts = {}
    for conversion in converter.conversion_log:
        conv_type = conversion["type"]
        type_counts[conv_type] = type_counts.get(conv_type, 0) + 1

    for conv_type, count in type_counts.items():
        print(f"{conv_type}: {count}")


if __name__ == "__main__":
    main()
