"""
Централизованный менеджер настроек игры.
Использует единые настройки и загружает пользовательские конфигурации из JSON файлов.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import threading

from config.unified_settings import UnifiedSettings

logger = logging.getLogger(__name__)


@dataclass
class GameSettings:
    """Основные настройки игры с базовыми значениями из UnifiedSettings"""

    # Графика
    window_width: int = UnifiedSettings.WINDOW_WIDTH
    window_height: int = UnifiedSettings.WINDOW_HEIGHT
    fullscreen: bool = False
    vsync: bool = True
    antialiasing: str = "msaa_4x"
    texture_quality: str = "high"
    shadow_quality: str = "medium"
    render_fps: int = UnifiedSettings.RENDER_FPS
    update_fps: int = UnifiedSettings.UPDATE_FPS

    # Звук
    master_volume: float = 1.0
    music_volume: float = 0.8
    sfx_volume: float = 1.0
    voice_volume: float = 0.9
    ambient_volume: float = 0.6
    audio_enabled: bool = True

    # Интерфейс
    show_damage_numbers: bool = True
    show_health_bars: bool = True
    show_minimap: bool = True
    ui_scale: float = 1.0
    language: str = "ru"
    font_size: int = UnifiedSettings.FONT_SIZE_NORMAL

    # Геймплей
    auto_save_interval: int = 300
    max_save_slots: int = 10
    inventory_slots: int = 20
    equipment_slots: int = 8
    stack_size_limit: int = 99
    weight_limit_enabled: bool = True
    base_weight_limit: float = 100.0

    # Бой
    base_attack_cooldown: float = 1.0
    critical_hit_threshold: float = 0.95
    block_chance_cap: float = 0.75
    dodge_chance_cap: float = 0.5
    parry_chance_cap: float = 0.4
    damage_reduction_cap: float = 0.8
    attack_range: float = UnifiedSettings.ATTACK_RANGE_BASE
    base_damage: float = UnifiedSettings.BASE_DAMAGE

    # Движение
    base_movement_speed: float = 2.0
    sprint_multiplier: float = 1.5
    crouch_multiplier: float = 0.6
    swim_multiplier: float = 0.7
    climb_multiplier: float = 0.4
    gravity: float = UnifiedSettings.GRAVITY
    friction: float = UnifiedSettings.FRICTION
    collision_tolerance: float = 2.0

    # ИИ
    learning_rate: float = UnifiedSettings.LEARNING_RATE_BASE
    memory_decay_rate: float = UnifiedSettings.MEMORY_DECAY_RATE_BASE
    pattern_recognition_threshold: float = UnifiedSettings.PATTERN_RECOGNITION_THRESHOLD
    emotion_synthesis_enabled: bool = True
    adaptive_difficulty: bool = True
    ai_update_frequency: float = 0.1
    decision_delay: float = 0.5
    memory_duration: float = 30.0


class SettingsManager:
    """Централизованный менеджер настроек игры."""

    def __init__(self, config_dir: str = "data"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()
        self.settings = GameSettings()
        self._load_settings()

    def _load_settings(self) -> None:
        """Загружает настройки из JSON файла."""
        try:
            settings_file = self.config_dir / "game_settings.json"
            if settings_file.exists():
                with open(settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Обновляем настройки из файла
                for key, value in data.items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)

                logger.info("Настройки загружены успешно")
            else:
                logger.info(
                    "Файл настроек не найден, используются значения по умолчанию"
                )
                self._save_settings()
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")

    def _save_settings(self) -> bool:
        """Сохраняет настройки в JSON файл."""
        try:
            settings_file = self.config_dir / "game_settings.json"
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.settings), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Получает значение настройки."""
        with self._lock:
            return getattr(self.settings, key, default)

    def set_setting(self, key: str, value: Any) -> bool:
        """Устанавливает значение настройки."""
        try:
            with self._lock:
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
                    return True
                return False
        except Exception as e:
            logger.error(f"Ошибка установки настройки {key}: {e}")
            return False

    def save_settings(self) -> bool:
        """Сохраняет текущие настройки в файл."""
        with self._lock:
            return self._save_settings()

    def reload_settings(self) -> None:
        """Перезагружает настройки из файла."""
        with self._lock:
            self._load_settings()

    def get_all_settings(self) -> Dict[str, Any]:
        """Возвращает все настройки в виде словаря."""
        with self._lock:
            return asdict(self.settings)

    def reset_to_defaults(self) -> None:
        """Сбрасывает настройки к значениям по умолчанию."""
        with self._lock:
            self.settings = GameSettings()
            self._save_settings()

    def get_entity_settings(self, entity_type: str) -> Dict[str, Any]:
        """Получает настройки для конкретного типа сущности."""
        from config.unified_settings import get_entity_settings

        return get_entity_settings(entity_type)

    def get_combat_settings(self) -> Dict[str, Any]:
        """Получает настройки боевой системы."""
        from config.unified_settings import get_combat_settings

        return get_combat_settings()

    def get_ai_settings(self) -> Dict[str, Any]:
        """Получает настройки AI системы."""
        from config.unified_settings import get_ai_settings

        return get_ai_settings()

    def get_ui_settings(self) -> Dict[str, Any]:
        """Получает настройки UI."""
        from config.unified_settings import get_ui_settings

        return get_ui_settings()


# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()
