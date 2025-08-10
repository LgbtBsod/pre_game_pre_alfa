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

from config.unified_settings import unified_settings, get_window_settings, get_fps_settings, get_color_settings, get_ai_settings, get_combat_settings, get_movement_settings, get_ui_settings, get_audio_settings, get_graphics_settings, get_gameplay_settings, get_inventory_settings

logger = logging.getLogger(__name__)


@dataclass
class GameSettings:
    """Основные настройки игры с базовыми значениями из unified_settings"""
    # Графика
    window_width: int = get_window_settings().WIDTH
    window_height: int = get_window_settings().HEIGHT
    fullscreen: bool = get_graphics_settings().FULLSCREEN
    vsync: bool = get_fps_settings().VSYNC
    antialiasing: str = get_graphics_settings().ANTIALIASING
    texture_quality: str = get_graphics_settings().TEXTURE_QUALITY
    shadow_quality: str = get_graphics_settings().SHADOW_QUALITY
    render_fps: int = get_fps_settings().RENDER_FPS
    update_fps: int = get_fps_settings().UPDATE_FPS
    
    # Звук
    master_volume: float = get_audio_settings().MASTER_VOLUME
    music_volume: float = get_audio_settings().MUSIC_VOLUME
    sfx_volume: float = get_audio_settings().SFX_VOLUME
    voice_volume: float = get_audio_settings().VOICE_VOLUME
    ambient_volume: float = get_audio_settings().AMBIENT_VOLUME
    audio_enabled: bool = get_audio_settings().AUDIO_ENABLED
    
    # Интерфейс
    show_damage_numbers: bool = get_ui_settings().SHOW_DAMAGE_NUMBERS
    show_health_bars: bool = get_ui_settings().SHOW_HEALTH_BARS
    show_minimap: bool = get_ui_settings().SHOW_MINIMAP
    ui_scale: float = get_ui_settings().UI_SCALE
    language: str = get_gameplay_settings().LANGUAGE
    font_size: int = get_ui_settings().FONT_SIZE
    
    # Геймплей
    auto_save_interval: int = get_gameplay_settings().AUTO_SAVE_INTERVAL
    max_save_slots: int = get_gameplay_settings().MAX_SAVE_SLOTS
    inventory_slots: int = get_inventory_settings().SLOTS
    equipment_slots: int = get_inventory_settings().EQUIPMENT_SLOTS
    stack_size_limit: int = get_inventory_settings().STACK_SIZE_LIMIT
    weight_limit_enabled: bool = get_inventory_settings().WEIGHT_LIMIT_ENABLED
    base_weight_limit: float = get_inventory_settings().BASE_WEIGHT_LIMIT
    
    # Бой
    base_attack_cooldown: float = get_combat_settings().BASE_ATTACK_COOLDOWN
    critical_hit_threshold: float = 0.95
    block_chance_cap: float = get_combat_settings().BLOCK_CHANCE_CAP
    dodge_chance_cap: float = get_combat_settings().DODGE_CHANCE_CAP
    parry_chance_cap: float = get_combat_settings().PARRY_CHANCE_CAP
    damage_reduction_cap: float = get_combat_settings().DAMAGE_REDUCTION_CAP
    attack_range: float = get_combat_settings().ATTACK_RANGE_BASE
    base_damage: float = get_combat_settings().BASE_DAMAGE
    
    # Движение
    base_movement_speed: float = get_movement_settings().BASE_MOVEMENT_SPEED
    sprint_multiplier: float = get_movement_settings().SPRINT_MULTIPLIER
    crouch_multiplier: float = get_movement_settings().CROUCH_MULTIPLIER
    swim_multiplier: float = get_movement_settings().SWIM_MULTIPLIER
    climb_multiplier: float = get_movement_settings().CLIMB_MULTIPLIER
    gravity: float = get_movement_settings().GRAVITY
    friction: float = get_movement_settings().FRICTION
    collision_tolerance: float = get_movement_settings().COLLISION_TOLERANCE
    
    # ИИ
    learning_rate: float = get_ai_settings().LEARNING_RATE_BASE
    memory_decay_rate: float = get_ai_settings().MEMORY_DECAY_RATE_BASE
    pattern_recognition_threshold: float = get_ai_settings().PATTERN_RECOGNITION_THRESHOLD
    emotion_synthesis_enabled: bool = get_ai_settings().EMOTION_SYNTHESIS_ENABLED
    adaptive_difficulty: bool = get_ai_settings().ADAPTIVE_DIFFICULTY
    ai_update_frequency: float = get_ai_settings().AI_UPDATE_FREQUENCY
    decision_delay: float = get_ai_settings().DECISION_DELAY
    memory_duration: float = get_ai_settings().MEMORY_DURATION


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
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Обновляем только существующие поля
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
            else:
                self._save_settings()
            
            logger.info("Настройки загружены успешно")
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
    
    def _save_settings(self) -> bool:
        """Сохраняет настройки в JSON файл."""
        try:
            settings_data = asdict(self.settings)
            
            with open(self.config_dir / "game_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
            
            logger.info("Настройки сохранены")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Получает значение настройки по ключу."""
        with self._lock:
            return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Устанавливает значение настройки."""
        with self._lock:
            try:
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
                    return True
                return False
            except Exception as e:
                logger.error(f"Ошибка установки настройки {key}: {e}")
                return False
    
    def save_settings(self) -> bool:
        """Сохраняет все настройки."""
        with self._lock:
            return self._save_settings()
    
    def reload_settings(self) -> None:
        """Перезагружает настройки."""
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


# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()
