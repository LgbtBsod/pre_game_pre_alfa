"""
Генератор 16-ричных ID для сущностей.
Обеспечивает уникальную идентификацию AI сущностей, предметов и эффектов.
"""

import time
import random
import threading
from typing import Dict, Set, Optional
from dataclasses import dataclass
from enum import Enum


class EntityType(Enum):
    """Типы сущностей для префиксов ID"""

    AI_ENTITY = "ai"
    ITEM = "itm"
    EFFECT = "eff"
    PLAYER = "plr"
    ENEMY = "enm"
    BOSS = "bos"
    NPC = "npc"
    PROJECTILE = "prj"
    TRAP = "trp"
    CONTAINER = "cnt"


@dataclass
class EntityID:
    """16-ричный ID сущности"""

    hex_id: str
    entity_type: EntityType
    timestamp: int
    instance_id: int

    def __str__(self) -> str:
        return f"{self.entity_type.value}_{self.hex_id}"

    def __repr__(self) -> str:
        return f"EntityID({self.hex_id}, {self.entity_type.value})"

    def __hash__(self) -> int:
        return hash(self.hex_id)

    def __eq__(self, other) -> bool:
        if isinstance(other, EntityID):
            return self.hex_id == other.hex_id
        return False


class EntityIDGenerator:
    """Генератор уникальных 16-ричных ID для сущностей"""

    def __init__(self):
        self._lock = threading.RLock()
        self._used_ids: Set[str] = set()
        self._instance_counter = 0
        self._type_counters: Dict[EntityType, int] = {
            entity_type: 0 for entity_type in EntityType
        }

        # Начальное время для уникальности
        self._start_time = int(time.time() * 1000)  # миллисекунды

    def generate_id(self, entity_type: EntityType) -> EntityID:
        """Генерирует уникальный 16-ричный ID для сущности"""
        with self._lock:
            timestamp = int(time.time() * 1000) - self._start_time
            instance_id = self._instance_counter
            type_counter = self._type_counters[entity_type]

            # Создаем 16-ричный ID из компонентов
            # Формат: TTTT_IIII_CCCC_SSSS
            # TTTT - timestamp (4 символа)
            # IIII - instance_id (4 символа)
            # CCCC - type_counter (4 символа)
            # SSSS - случайное число (4 символа)

            random_part = random.randint(0, 0xFFFF)

            # Комбинируем компоненты
            combined = (
                (timestamp << 48)
                | (instance_id << 32)
                | (type_counter << 16)
                | random_part
            )

            # Конвертируем в 16-ричную строку
            hex_id = f"{combined:016x}"

            # Проверяем уникальность
            while hex_id in self._used_ids:
                random_part = random.randint(0, 0xFFFF)
                combined = (
                    (timestamp << 48)
                    | (instance_id << 32)
                    | (type_counter << 16)
                    | random_part
                )
                hex_id = f"{combined:016x}"

            # Добавляем в использованные
            self._used_ids.add(hex_id)

            # Увеличиваем счетчики
            self._instance_counter += 1
            self._type_counters[entity_type] += 1

            return EntityID(hex_id, entity_type, timestamp, instance_id)

    def generate_short_id(self, entity_type: EntityType) -> str:
        """Генерирует короткий 16-ричный ID (8 символов)"""
        with self._lock:
            timestamp = int(time.time() * 1000) - self._start_time
            instance_id = self._instance_counter
            type_counter = self._type_counters[entity_type]

            # Короткий формат: TTTT_IIII
            combined = (timestamp & 0xFFFF) | ((instance_id & 0xFFFF) << 16)
            hex_id = f"{combined:08x}"

            # Проверяем уникальность
            while hex_id in self._used_ids:
                instance_id += 1
                combined = (timestamp & 0xFFFF) | ((instance_id & 0xFFFF) << 16)
                hex_id = f"{combined:08x}"

            self._used_ids.add(hex_id)
            self._instance_counter += 1
            self._type_counters[entity_type] += 1

            return f"{entity_type.value}_{hex_id}"

    def register_existing_id(self, hex_id: str) -> bool:
        """Регистрирует существующий ID как использованный"""
        with self._lock:
            if hex_id in self._used_ids:
                return False
            self._used_ids.add(hex_id)
            return True

    def is_id_used(self, hex_id: str) -> bool:
        """Проверяет, используется ли ID"""
        with self._lock:
            return hex_id in self._used_ids

    def get_stats(self) -> Dict[str, int]:
        """Возвращает статистику генератора"""
        with self._lock:
            return {
                "total_generated": self._instance_counter,
                "used_ids_count": len(self._used_ids),
                "type_counters": {t.value: c for t, c in self._type_counters.items()},
            }


class LegacyIDConverter:
    """Конвертер старых строковых ID в 16-ричные"""

    def __init__(self, id_generator: EntityIDGenerator):
        self.id_generator = id_generator
        self._conversion_map: Dict[str, str] = {}
        self._reverse_map: Dict[str, str] = {}

    def convert_legacy_id(self, legacy_id: str, entity_type: EntityType) -> str:
        """Конвертирует старый ID в новый 16-ричный"""
        if legacy_id in self._conversion_map:
            return self._conversion_map[legacy_id]

        # Генерируем новый ID
        new_id = self.id_generator.generate_short_id(entity_type)

        # Сохраняем маппинг
        self._conversion_map[legacy_id] = new_id
        self._reverse_map[new_id] = legacy_id

        return new_id

    def get_legacy_id(self, hex_id: str) -> Optional[str]:
        """Получает оригинальный ID по 16-ричному"""
        return self._reverse_map.get(hex_id)

    def get_conversion_map(self) -> Dict[str, str]:
        """Возвращает карту конвертации"""
        return self._conversion_map.copy()


# Глобальные экземпляры
id_generator = EntityIDGenerator()
legacy_converter = LegacyIDConverter(id_generator)


def generate_entity_id(entity_type: EntityType) -> EntityID:
    """Удобная функция для генерации ID сущности"""
    return id_generator.generate_id(entity_type)


def generate_short_entity_id(entity_type: EntityType) -> str:
    """Удобная функция для генерации короткого ID сущности"""
    return id_generator.generate_short_id(entity_type)


def convert_legacy_id(legacy_id: str, entity_type: EntityType) -> str:
    """Удобная функция для конвертации старого ID"""
    return legacy_converter.convert_legacy_id(legacy_id, entity_type)


def get_entity_id_stats() -> Dict[str, int]:
    """Получить статистику генератора ID"""
    return id_generator.get_stats()
