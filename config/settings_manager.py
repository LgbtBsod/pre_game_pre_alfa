"""Менеджер настроек игры - централизованное управление конфигурацией."""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SettingsManager:
    """Централизованный менеджер настроек игры."""
    
    def __init__(self, config_dir: str = "data"):
        self.config_dir = Path(config_dir)
        self._settings_cache = {}
        self._load_all_settings()
    
    def _load_all_settings(self):
        """Загружает все настройки из JSON файлов."""
        try:
            # Основные настройки игры
            self._load_file("game_settings.json", "game_settings")
            
            # Настройки сложности
            self._load_file("difficulty_settings.json", "difficulty")
            
            # Настройки UI
            self._load_file("ui_settings.json", "ui")
            
            # Настройки графики
            self._load_file("graphics_settings.json", "graphics")
            
            # Настройки звука
            self._load_file("audio_settings.json", "audio")
            
            # Настройки ИИ
            self._load_file("ai_settings.json", "ai")
            
            # Настройки боя
            self._load_file("combat_settings.json", "combat")
            
            # Настройки инвентаря
            self._load_file("inventory_settings.json", "inventory")
            
            logger.info("Все настройки загружены успешно")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
            self._create_default_settings()
    
    def _load_file(self, filename: str, section: str):
        """Загружает настройки из конкретного файла."""
        file_path = self.config_dir / filename
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._settings_cache[section] = data
                    logger.debug(f"Загружены настройки из {filename}")
            except Exception as e:
                logger.error(f"Ошибка загрузки {filename}: {e}")
                self._settings_cache[section] = {}
        else:
            logger.warning(f"Файл настроек {filename} не найден")
            self._settings_cache[section] = {}
    
    def _create_default_settings(self):
        """Создает настройки по умолчанию."""
        self._settings_cache = {
            "game_settings": self._get_default_game_settings(),
            "difficulty": self._get_default_difficulty_settings(),
            "ui": self._get_default_ui_settings(),
            "graphics": self._get_default_graphics_settings(),
            "audio": self._get_default_audio_settings(),
            "ai": self._get_default_ai_settings(),
            "combat": self._get_default_combat_settings(),
            "inventory": self._get_default_inventory_settings()
        }
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Получает значение настройки."""
        try:
            return self._settings_cache.get(section, {}).get(key, default)
        except KeyError:
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Получает всю секцию настроек."""
        return self._settings_cache.get(section, {})
    
    def set_setting(self, section: str, key: str, value: Any):
        """Устанавливает значение настройки."""
        if section not in self._settings_cache:
            self._settings_cache[section] = {}
        self._settings_cache[section][key] = value
    
    def save_settings(self, section: str = None):
        """Сохраняет настройки в файл."""
        try:
            if section:
                self._save_section(section)
            else:
                for section_name in self._settings_cache:
                    self._save_section(section_name)
            logger.info("Настройки сохранены")
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
    
    def _save_section(self, section: str):
        """Сохраняет секцию настроек в файл."""
        filename = f"{section}_settings.json"
        file_path = self.config_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings_cache[section], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения {filename}: {e}")
    
    def _get_default_game_settings(self) -> Dict[str, Any]:
        """Настройки игры по умолчанию."""
        return {
            "window": {
                "width": 1200,
                "height": 800,
                "title": "Autonomous AI Survivor",
                "fullscreen": False,
                "vsync": True
            },
            "gameplay": {
                "auto_save_interval": 300,
                "max_save_slots": 10,
                "language": "ru",
                "debug_mode": False
            },
            "performance": {
                "target_fps": 60,
                "update_fps": 120,
                "enable_vsync": True,
                "enable_antialiasing": True
            }
        }
    
    def _get_default_difficulty_settings(self) -> Dict[str, Any]:
        """Настройки сложности по умолчанию."""
        return {
            "easy": {
                "enemy_health_multiplier": 0.8,
                "enemy_damage_multiplier": 0.7,
                "player_health_multiplier": 1.2,
                "player_damage_multiplier": 1.1,
                "experience_multiplier": 1.3,
                "enemy_count": 3,
                "enemy_level_range": [1, 3],
                "boss_level": 5
            },
            "normal": {
                "enemy_health_multiplier": 1.0,
                "enemy_damage_multiplier": 1.0,
                "player_health_multiplier": 1.0,
                "player_damage_multiplier": 1.0,
                "experience_multiplier": 1.0,
                "enemy_count": 5,
                "enemy_level_range": [2, 5],
                "boss_level": 10
            },
            "hard": {
                "enemy_health_multiplier": 1.3,
                "enemy_damage_multiplier": 1.4,
                "player_health_multiplier": 0.9,
                "player_damage_multiplier": 0.9,
                "experience_multiplier": 0.8,
                "enemy_count": 7,
                "enemy_level_range": [3, 8],
                "boss_level": 15
            }
        }
    
    def _get_default_ui_settings(self) -> Dict[str, Any]:
        """Настройки UI по умолчанию."""
        return {
            "display": {
                "show_health_bars": True,
                "show_damage_numbers": True,
                "show_minimap": True,
                "show_quest_log": True,
                "show_fps": False,
                "ui_scale": 1.0
            },
            "colors": {
                "player": "#00ff00",
                "enemy": "#ff0000",
                "boss": "#ff00ff",
                "npc": "#0000ff",
                "item": "#ffff00",
                "ui_background": "#000000",
                "ui_text": "#ffffff",
                "ui_button": "#444444",
                "ui_button_hover": "#666666"
            },
            "fonts": {
                "main_font": "Arial",
                "main_font_size": 14,
                "title_font_size": 18,
                "small_font_size": 12
            }
        }
    
    def _get_default_graphics_settings(self) -> Dict[str, Any]:
        """Настройки графики по умолчанию."""
        return {
            "resolution": {
                "width": 1920,
                "height": 1080,
                "fullscreen": False
            },
            "quality": {
                "texture_quality": "high",
                "shadow_quality": "medium",
                "particle_quality": "high",
                "antialiasing": "msaa_4x"
            },
            "effects": {
                "enable_shadows": True,
                "enable_bloom": True,
                "enable_motion_blur": False,
                "enable_dof": False
            },
            "performance": {
                "vsync": True,
                "triple_buffering": True,
                "max_fps": 60
            }
        }
    
    def _get_default_audio_settings(self) -> Dict[str, Any]:
        """Настройки звука по умолчанию."""
        return {
            "volumes": {
                "master_volume": 1.0,
                "music_volume": 0.8,
                "sfx_volume": 1.0,
                "voice_volume": 0.9,
                "ambient_volume": 0.6
            },
            "audio": {
                "enable_music": True,
                "enable_sfx": True,
                "enable_voice": True,
                "enable_ambient": True,
                "audio_device": "default"
            }
        }
    
    def _get_default_ai_settings(self) -> Dict[str, Any]:
        """Настройки ИИ по умолчанию."""
        return {
            "learning": {
                "learning_rate": 0.1,
                "memory_decay_rate": 0.95,
                "pattern_recognition_threshold": 0.7
            },
            "behavior": {
                "emotion_synthesis_enabled": True,
                "adaptive_difficulty": True,
                "cooperation_enabled": True,
                "pathfinding_enabled": True
            },
            "performance": {
                "ai_update_frequency": 0.1,
                "max_ai_entities": 50,
                "ai_optimization_level": "medium"
            }
        }
    
    def _get_default_combat_settings(self) -> Dict[str, Any]:
        """Настройки боя по умолчанию."""
        return {
            "mechanics": {
                "base_attack_cooldown": 1.0,
                "critical_hit_threshold": 0.95,
                "block_chance_cap": 0.75,
                "dodge_chance_cap": 0.5,
                "parry_chance_cap": 0.4,
                "damage_reduction_cap": 0.8
            },
            "damage": {
                "base_damage": 10,
                "critical_multiplier": 2.0,
                "elemental_damage_multiplier": 1.5
            },
            "effects": {
                "max_active_effects": 20,
                "effect_duration_base": 10.0,
                "effect_tick_rate": 1.0
            }
        }
    
    def _get_default_inventory_settings(self) -> Dict[str, Any]:
        """Настройки инвентаря по умолчанию."""
        return {
            "limits": {
                "max_stack_size": 99,
                "inventory_slots": 20,
                "equipment_slots": 8,
                "weight_limit": 100.0
            },
            "features": {
                "auto_sort_enabled": True,
                "weight_limit_enabled": True,
                "quick_slot_count": 8,
                "auto_equip_enabled": True
            }
        }


# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()
