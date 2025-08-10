"""
Единая система настроек для проекта AI EVOLVE
Устраняет дублирование констант и параметров между модулями
"""

from typing import Dict, Any, Optional
import json
import os
from pathlib import Path


class UnifiedSettings:
    """
    Единая система настроек для всего проекта
    Централизует все константы и параметры
    """

    # ==================== РАЗМЕРЫ ОКНА ====================
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    DEFAULT_WINDOW_WIDTH = 1200
    DEFAULT_WINDOW_HEIGHT = 800

    # ==================== FPS НАСТРОЙКИ ====================
    RENDER_FPS = 60
    UPDATE_FPS = 120
    MAX_FPS = 144
    MIN_FPS = 30

    # ==================== ЦВЕТОВАЯ СХЕМА ====================
    # Основные цвета
    BACKGROUND = (0, 0, 0)
    BACKGROUND_DARK = (26, 26, 26)
    BACKGROUND_LIGHT = (40, 40, 40)

    # Цвета сущностей
    PLAYER_COLOR = (0, 255, 0)
    ENEMY_COLOR = (255, 0, 0)
    NEUTRAL_COLOR = (255, 255, 0)

    # Цвета UI
    TEXT_COLOR = (255, 255, 255)
    TEXT_COLOR_DARK = (200, 200, 200)
    TEXT_COLOR_LIGHT = (255, 255, 255)

    # Цвета кнопок
    BUTTON_COLOR = (60, 60, 60)
    BUTTON_HOVER_COLOR = (80, 80, 80)
    BUTTON_ACTIVE_COLOR = (100, 100, 100)

    # Цвета здоровья
    HEALTH_COLOR = (0, 255, 0)
    HEALTH_LOW_COLOR = (255, 255, 0)
    HEALTH_CRITICAL_COLOR = (255, 0, 0)

    # ==================== AI ПАРАМЕТРЫ ====================
    # Базовые параметры обучения
    LEARNING_RATE_BASE = 0.1
    LEARNING_RATE_PLAYER = 0.2
    LEARNING_RATE_ENEMY = 0.15

    # Параметры памяти
    MEMORY_DECAY_RATE_BASE = 0.95
    MEMORY_DECAY_RATE_FAST = 0.90
    MEMORY_DECAY_RATE_SLOW = 0.98

    # Пороги распознавания
    PATTERN_RECOGNITION_THRESHOLD = 0.7
    DECISION_THRESHOLD = 0.5
    COOPERATION_THRESHOLD = 0.8

    # Параметры эмоций
    EMOTION_DECAY_RATE = 0.95
    EMOTION_INTENSITY_MAX = 1.0
    EMOTION_INTENSITY_MIN = 0.0

    # ==================== БОЕВЫЕ ПАРАМЕТРЫ ====================
    # Базовые параметры атаки
    ATTACK_RANGE_BASE = 50.0
    ATTACK_RANGE_PLAYER = 60.0
    ATTACK_RANGE_ENEMY = 45.0

    # Параметры урона
    BASE_DAMAGE = 10.0
    DAMAGE_VARIANCE = 0.2
    CRITICAL_MULTIPLIER_BASE = 2.0
    CRITICAL_CHANCE_BASE = 0.1

    # Параметры здоровья
    BASE_HEALTH = 100.0
    HEALTH_REGEN_RATE = 1.0
    MAX_HEALTH_MULTIPLIER = 1.5

    # Параметры защиты
    BASE_ARMOR = 0.0
    ARMOR_EFFECTIVENESS = 0.5
    DODGE_CHANCE_BASE = 0.05

    # ==================== ИГРОВЫЕ ПАРАМЕТРЫ ====================
    # Размеры карты
    MAP_WIDTH = 2000
    MAP_HEIGHT = 2000
    TILE_SIZE = 32

    # Параметры камеры
    CAMERA_SPEED = 5.0
    CAMERA_ZOOM_MIN = 0.5
    CAMERA_ZOOM_MAX = 2.0
    CAMERA_ZOOM_STEP = 0.1

    # Параметры физики
    GRAVITY = 0.0
    FRICTION = 0.8
    MAX_SPEED = 5.0

    # ==================== UI ПАРАМЕТРЫ ====================
    # Размеры элементов UI
    BUTTON_HEIGHT = 40
    BUTTON_PADDING = 10
    MENU_PADDING = 20

    # Шрифты
    FONT_SIZE_SMALL = 12
    FONT_SIZE_NORMAL = 14
    FONT_SIZE_LARGE = 18
    FONT_SIZE_TITLE = 24

    # Анимации
    ANIMATION_SPEED = 0.1
    HOVER_ANIMATION_DURATION = 0.2

    # ==================== СИСТЕМНЫЕ ПАРАМЕТРЫ ====================
    # Пути к файлам
    DATA_DIR = "data"
    BACKUP_DIR = "backup"
    LOGS_DIR = "logs"
    SAVES_DIR = "saves"

    # Имена файлов
    GAME_DATA_FILE = "game_data.db"
    SETTINGS_FILE = "game_settings.json"
    ENTITIES_FILE = "entities.json"
    ITEMS_FILE = "items.json"
    ABILITIES_FILE = "abilities.json"

    # Параметры логирования
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(lineno)-3d | %(message)s"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5

    # Параметры резервного копирования
    BACKUP_ENABLED = True
    BACKUP_INTERVAL = 300  # 5 минут
    MAX_BACKUP_FILES = 10

    def __init__(self):
        """Инициализация настроек"""
        self._custom_settings: Dict[str, Any] = {}
        self._load_custom_settings()

    def _load_custom_settings(self):
        """Загрузка пользовательских настроек из файла"""
        settings_file = Path(self.DATA_DIR) / self.SETTINGS_FILE
        if settings_file.exists():
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    self._custom_settings = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
                self._custom_settings = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения настройки"""
        # Сначала проверяем пользовательские настройки
        if key in self._custom_settings:
            return self._custom_settings[key]

        # Затем проверяем атрибуты класса
        if hasattr(self, key):
            return getattr(self, key)

        return default

    def set(self, key: str, value: Any):
        """Установка значения настройки"""
        self._custom_settings[key] = value
        self._save_custom_settings()

    def _save_custom_settings(self):
        """Сохранение пользовательских настроек в файл"""
        settings_file = Path(self.DATA_DIR) / self.SETTINGS_FILE
        settings_file.parent.mkdir(exist_ok=True)

        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self._custom_settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def get_entity_settings(self, entity_type: str) -> Dict[str, Any]:
        """Получение настроек для конкретного типа сущности"""
        base_settings = {
            "learning_rate": self.LEARNING_RATE_BASE,
            "memory_decay_rate": self.MEMORY_DECAY_RATE_BASE,
            "attack_range": self.ATTACK_RANGE_BASE,
            "base_damage": self.BASE_DAMAGE,
            "base_health": self.BASE_HEALTH,
        }

        # Специфичные настройки для типов сущностей
        entity_specific = {
            "player": {
                "learning_rate": self.LEARNING_RATE_PLAYER,
                "attack_range": self.ATTACK_RANGE_PLAYER,
                "color": self.PLAYER_COLOR,
            },
            "enemy": {
                "learning_rate": self.LEARNING_RATE_ENEMY,
                "attack_range": self.ATTACK_RANGE_ENEMY,
                "color": self.ENEMY_COLOR,
            },
            "neutral": {
                "color": self.NEUTRAL_COLOR,
            },
        }

        # Объединяем базовые и специфичные настройки
        if entity_type in entity_specific:
            base_settings.update(entity_specific[entity_type])

        return base_settings

    def get_ui_settings(self) -> Dict[str, Any]:
        """Получение настроек UI"""
        return {
            "window_width": self.WINDOW_WIDTH,
            "window_height": self.WINDOW_HEIGHT,
            "render_fps": self.RENDER_FPS,
            "update_fps": self.UPDATE_FPS,
            "background_color": self.BACKGROUND,
            "text_color": self.TEXT_COLOR,
            "button_color": self.BUTTON_COLOR,
            "button_hover_color": self.BUTTON_HOVER_COLOR,
            "font_size_normal": self.FONT_SIZE_NORMAL,
            "button_height": self.BUTTON_HEIGHT,
            "menu_padding": self.MENU_PADDING,
        }

    def get_ai_settings(self) -> Dict[str, Any]:
        """Получение настроек AI"""
        return {
            "learning_rate_base": self.LEARNING_RATE_BASE,
            "memory_decay_rate_base": self.MEMORY_DECAY_RATE_BASE,
            "pattern_recognition_threshold": self.PATTERN_RECOGNITION_THRESHOLD,
            "decision_threshold": self.DECISION_THRESHOLD,
            "cooperation_threshold": self.COOPERATION_THRESHOLD,
            "emotion_decay_rate": self.EMOTION_DECAY_RATE,
            "emotion_intensity_max": self.EMOTION_INTENSITY_MAX,
            "emotion_intensity_min": self.EMOTION_INTENSITY_MIN,
        }

    def get_combat_settings(self) -> Dict[str, Any]:
        """Получение настроек боевой системы"""
        return {
            "attack_range_base": self.ATTACK_RANGE_BASE,
            "base_damage": self.BASE_DAMAGE,
            "damage_variance": self.DAMAGE_VARIANCE,
            "critical_multiplier_base": self.CRITICAL_MULTIPLIER_BASE,
            "critical_chance_base": self.CRITICAL_CHANCE_BASE,
            "base_health": self.BASE_HEALTH,
            "health_regen_rate": self.HEALTH_REGEN_RATE,
            "base_armor": self.BASE_ARMOR,
            "armor_effectiveness": self.ARMOR_EFFECTIVENESS,
            "dodge_chance_base": self.DODGE_CHANCE_BASE,
        }

    def get_system_settings(self) -> Dict[str, Any]:
        """Получение системных настроек"""
        return {
            "data_dir": self.DATA_DIR,
            "backup_dir": self.BACKUP_DIR,
            "logs_dir": self.LOGS_DIR,
            "saves_dir": self.SAVES_DIR,
            "log_level": self.LOG_LEVEL,
            "log_format": self.LOG_FORMAT,
            "backup_enabled": self.BACKUP_ENABLED,
            "backup_interval": self.BACKUP_INTERVAL,
        }


# Глобальный экземпляр настроек
settings = UnifiedSettings()


def get_settings() -> UnifiedSettings:
    """Получение глобального экземпляра настроек"""
    return settings


def get_entity_settings(entity_type: str) -> Dict[str, Any]:
    """Получение настроек для сущности"""
    return settings.get_entity_settings(entity_type)


def get_ui_settings() -> Dict[str, Any]:
    """Получение настроек UI"""
    return settings.get_ui_settings()


def get_ai_settings() -> Dict[str, Any]:
    """Получение настроек AI"""
    return settings.get_ai_settings()


def get_combat_settings() -> Dict[str, Any]:
    """Получение настроек боевой системы"""
    return settings.get_combat_settings()


def get_system_settings() -> Dict[str, Any]:
    """Получение системных настроек"""
    return settings.get_system_settings()
