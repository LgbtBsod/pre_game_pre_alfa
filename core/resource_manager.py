"""Оптимизированный менеджер ресурсов для управления игровыми данными."""

import json
import logging
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from collections import defaultdict, OrderedDict
import weakref

from config.settings_manager import settings_manager
from core.data_manager import data_manager

logger = logging.getLogger(__name__)


class ResourceCache:
    """Кэш для ресурсов с LRU (Least Recently Used) политикой."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.access_times = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Получает ресурс из кэша."""
        with self._lock:
            if key in self.cache:
                # Обновляем время доступа
                self.access_times[key] = time.time()
                # Перемещаем в конец (LRU)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None

    def put(self, key: str, value: Any):
        """Добавляет ресурс в кэш."""
        with self._lock:
            if key in self.cache:
                # Обновляем существующий
                self.cache.move_to_end(key)
                self.cache[key] = value
            else:
                # Добавляем новый
                self.cache[key] = value
                # Проверяем размер кэша
                if len(self.cache) > self.max_size:
                    # Удаляем самый старый элемент
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    if oldest_key in self.access_times:
                        del self.access_times[oldest_key]

            self.access_times[key] = time.time()

    def remove(self, key: str):
        """Удаляет ресурс из кэша."""
        with self._lock:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]

    def clear(self):
        """Очищает кэш."""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()

    def size(self) -> int:
        """Возвращает размер кэша."""
        with self._lock:
            return len(self.cache)

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша."""
        with self._lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "usage_percent": (len(self.cache) / self.max_size) * 100,
            }


class ResourceManager:
    """Оптимизированный менеджер ресурсов."""

    def __init__(self):
        self.cache = ResourceCache()
        self._lock = threading.Lock()
        self._load_callbacks = defaultdict(list)
        self._resource_paths = {}
        self._loaded_resources = {}
        self._loading_queue = []
        self._is_loading = False

        # Инициализация путей к ресурсам
        self._init_resource_paths()

        # Загрузка базовых ресурсов
        self._load_base_resources()

    def _init_resource_paths(self):
        """Инициализирует пути к ресурсам."""
        base_path = Path("data")
        self._resource_paths = {
            "game_settings": base_path / "game_settings.json",
            "difficulty": base_path / "difficulty_settings.json",
            "ui": base_path / "ui_settings.json",
            "graphics": base_path / "graphics_settings.json",
            "audio": base_path / "audio_settings.json",
            "ai": base_path / "ai_settings.json",
            "combat": base_path / "combat_settings.json",
            "inventory": base_path / "inventory_settings.json",
        }

    def _load_base_resources(self):
        """Загружает базовые ресурсы при инициализации."""
        try:
            # Загружаем настройки
            for resource_type, path in self._resource_paths.items():
                if path.exists():
                    self._load_json_resource(resource_type, path)

            logger.info("Базовые ресурсы загружены")

        except Exception as e:
            logger.error(f"Ошибка загрузки базовых ресурсов: {e}")

    def _load_json_resource(self, resource_type: str, path: Path):
        """Загружает JSON ресурс."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._loaded_resources[resource_type] = data
            logger.debug(f"Загружен ресурс: {resource_type}")

        except Exception as e:
            logger.error(f"Ошибка загрузки {resource_type}: {e}")
            self._loaded_resources[resource_type] = {}

    def _import_to_database(self):
        """Импортирует данные в базу данных."""
        try:
            # Импорт предметов
            if "items" in self._loaded_resources:
                for item_id, item_data in (
                    self._loaded_resources["items"].get("items", {}).items()
                ):
                    item_data["id"] = item_id
                    # Преобразуем range в attack_range для совместимости
                    if "range" in item_data:
                        item_data["attack_range"] = item_data.pop("range")
                    # Создаем объект ItemData
                    from core.data_manager import ItemData

                    try:
                        item = ItemData(**item_data)
                        data_manager.add_item(item)
                    except Exception as e:
                        logger.warning(f"Ошибка создания предмета {item_id}: {e}")
                        continue

            # Импорт врагов
            if "entities" in self._loaded_resources:
                for entity_id, entity_data in (
                    self._loaded_resources["entities"].get("entities", {}).items()
                ):
                    if entity_data.get("type") in ["enemy", "boss"]:
                        entity_data["id"] = entity_id
                        # Создаем объект EnemyData
                        from core.data_manager import EnemyData

                        try:
                            enemy = EnemyData(**entity_data)
                            data_manager.add_enemy(enemy)
                        except Exception as e:
                            logger.warning(f"Ошибка создания врага {entity_id}: {e}")
                            continue

            logger.info("Данные импортированы в базу данных")

        except Exception as e:
            logger.error(f"Ошибка импорта в БД: {e}")

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Получает настройку."""
        return settings_manager.get_setting(section, key, default)

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Получает предмет."""
        # Сначала проверяем кэш
        cached_item = self.cache.get(f"item_{item_id}")
        if cached_item:
            return cached_item

        # Затем базу данных
        item = data_manager.get_item(item_id)
        if item:
            self.cache.put(f"item_{item_id}", item)
            return item

        # Наконец, загруженные ресурсы
        if "items" in self._loaded_resources:
            items = self._loaded_resources["items"].get("items", {})
            if item_id in items:
                item_data = items[item_id].copy()
                item_data["id"] = item_id
                self.cache.put(f"item_{item_id}", item_data)
                return item_data

        return None

    def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Получает предметы по типу."""
        # Сначала база данных
        items = data_manager.get_items_by_type(item_type)
        if items:
            # Кэшируем результаты
            for item in items:
                self.cache.put(f"item_{item['id']}", item)
            return items

        # Затем загруженные ресурсы
        if "items" in self._loaded_resources:
            items = []
            for item_id, item_data in (
                self._loaded_resources["items"].get("items", {}).items()
            ):
                if item_data.get("type") == item_type:
                    item_data = item_data.copy()
                    item_data["id"] = item_id
                    items.append(item_data)
                    self.cache.put(f"item_{item_id}", item_data)
            return items

        return []

    def get_enemy(self, enemy_id: str) -> Optional[Dict[str, Any]]:
        """Получает врага."""
        # Сначала проверяем кэш
        cached_enemy = self.cache.get(f"enemy_{enemy_id}")
        if cached_enemy:
            return cached_enemy

        # Затем базу данных
        enemy = data_manager.get_enemy(enemy_id)
        if enemy:
            self.cache.put(f"enemy_{enemy_id}", enemy)
            return enemy

        # Наконец, загруженные ресурсы
        if "entities" in self._loaded_resources:
            entities = self._loaded_resources["entities"].get("entities", {})
            if enemy_id in entities:
                enemy_data = entities[enemy_id].copy()
                enemy_data["id"] = enemy_id
                self.cache.put(f"enemy_{enemy_id}", enemy_data)
                return enemy_data

        return None

    def get_enemies_by_type(self, enemy_type: str) -> List[Dict[str, Any]]:
        """Получает врагов по типу."""
        # Сначала база данных
        enemies = data_manager.get_enemies_by_type(enemy_type)
        if enemies:
            # Кэшируем результаты
            for enemy in enemies:
                self.cache.put(f"enemy_{enemy['id']}", enemy)
            return enemies

        # Затем загруженные ресурсы
        if "entities" in self._loaded_resources:
            enemies = []
            for entity_id, entity_data in (
                self._loaded_resources["entities"].get("entities", {}).items()
            ):
                if entity_data.get("enemy_type") == enemy_type:
                    entity_data = entity_data.copy()
                    entity_data["id"] = entity_id
                    enemies.append(entity_data)
                    self.cache.put(f"enemy_{entity_id}", entity_data)
            return enemies

        return []

    def get_effect(self, effect_id: str) -> Optional[Dict[str, Any]]:
        """Получает эффект."""
        if "effects" in self._loaded_resources:
            effects = self._loaded_resources["effects"].get("effects", {})
            return effects.get(effect_id)
        return None

    def get_ability(self, ability_id: str) -> Optional[Dict[str, Any]]:
        """Получает способность."""
        if "abilities" in self._loaded_resources:
            abilities = self._loaded_resources["abilities"].get("abilities", {})
            return abilities.get(ability_id)
        return None

    def get_attribute(self, attribute_id: str) -> Optional[Dict[str, Any]]:
        """Получает атрибут."""
        if "attributes" in self._loaded_resources:
            attributes = self._loaded_resources["attributes"].get("attributes", {})
            return attributes.get(attribute_id)
        return None

    def add_load_callback(self, resource_type: str, callback: Callable):
        """Добавляет callback для загрузки ресурсов."""
        self._load_callbacks[resource_type].append(callback)

    def reload_resource(self, resource_type: str):
        """Перезагружает ресурс."""
        try:
            if resource_type in self._resource_paths:
                path = self._resource_paths[resource_type]
                if path.exists():
                    self._load_json_resource(resource_type, path)

                    # Вызываем callbacks
                    for callback in self._load_callbacks[resource_type]:
                        try:
                            callback()
                        except Exception as e:
                            logger.error(f"Ошибка в callback для {resource_type}: {e}")

                    logger.info(f"Ресурс {resource_type} перезагружен")

        except Exception as e:
            logger.error(f"Ошибка перезагрузки ресурса {resource_type}: {e}")

    def preload_resources(self, resource_types: List[str]):
        """Предзагружает ресурсы."""
        for resource_type in resource_types:
            if resource_type in self._resource_paths:
                path = self._resource_paths[resource_type]
                if path.exists():
                    self._load_json_resource(resource_type, path)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша."""
        return self.cache.get_stats()

    def clear_cache(self):
        """Очищает кэш."""
        self.cache.clear()
        logger.info("Кэш ресурсов очищен")

    def optimize_cache(self):
        """Оптимизирует кэш."""
        # Удаляем неиспользуемые ресурсы
        current_time = time.time()
        to_remove = []

        for key, access_time in self.cache.access_times.items():
            if current_time - access_time > 300:  # 5 минут
                to_remove.append(key)

        for key in to_remove:
            self.cache.remove(key)

        if to_remove:
            logger.info(f"Удалено {len(to_remove)} неиспользуемых ресурсов из кэша")

    def save_resource(self, resource_type: str, data: Dict[str, Any]):
        """Сохраняет ресурс."""
        try:
            if resource_type in self._resource_paths:
                path = self._resource_paths[resource_type]

                # Обновляем в памяти
                self._loaded_resources[resource_type] = data

                # Сохраняем в файл
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"Ресурс {resource_type} сохранен")

        except Exception as e:
            logger.error(f"Ошибка сохранения ресурса {resource_type}: {e}")

    def get_resource_info(self) -> Dict[str, Any]:
        """Возвращает информацию о ресурсах."""
        info = {
            "loaded_resources": list(self._loaded_resources.keys()),
            "cache_stats": self.get_cache_stats(),
            "resource_paths": {k: str(v) for k, v in self._resource_paths.items()},
        }
        return info


# Глобальный экземпляр менеджера ресурсов
resource_manager = ResourceManager()
