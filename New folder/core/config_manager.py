#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МЕНЕДЖЕР КОНФИГУРАЦИИ
Централизованное управление всеми настройками игры
Соблюдает принцип единой ответственности
"""

import json
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from utils.logging_system import get_logger, log_system_event

class ConfigCategory(Enum):
    """Категории конфигурации"""
    GRAPHICS = "graphics"
    AUDIO = "audio"
    GAMEPLAY = "gameplay"
    CONTROLS = "controls"
    UI = "ui"
    AI = "ai"
    PERFORMANCE = "performance"
    DEBUG = "debug"

@dataclass
class ConfigValue:
    """Значение конфигурации"""
    value: Any
    default: Any
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    description: str = ""
    category: ConfigCategory = ConfigCategory.GAMEPLAY

class ConfigManager:
    """Менеджер конфигурации"""
    
    def __init__(self, config_directory: str = "config"):
        self.config_directory = Path(config_directory)
        self.config_directory.mkdir(parents=True, exist_ok=True)
        
        self.config: Dict[str, ConfigValue] = {}
        self.config_files: Dict[ConfigCategory, str] = {
            ConfigCategory.GRAPHICS: "graphics.json",
            ConfigCategory.AUDIO: "audio.json",
            ConfigCategory.GAMEPLAY: "gameplay.json",
            ConfigCategory.CONTROLS: "controls.json",
            ConfigCategory.UI: "ui.json",
            ConfigCategory.AI: "ai.json",
            ConfigCategory.PERFORMANCE: "performance.json",
            ConfigCategory.DEBUG: "debug.json"
        }
        
        self.logger = get_logger("config_manager")
        
        # Инициализация конфигурации по умолчанию
        self._initialize_default_config()
        
        # Загрузка сохраненной конфигурации
        self.load_all_configs()
        
        log_system_event("config_manager", "initialized")
    
    def _initialize_default_config(self):
        """Инициализация конфигурации по умолчанию"""
        
        # Графика
        self._set_config("window_width", 1920, ConfigCategory.GRAPHICS, 
                        description="Ширина окна", min_value=800, max_value=3840)
        self._set_config("window_height", 1080, ConfigCategory.GRAPHICS,
                        description="Высота окна", min_value=600, max_value=2160)
        self._set_config("fullscreen", False, ConfigCategory.GRAPHICS,
                        description="Полноэкранный режим")
        self._set_config("vsync", True, ConfigCategory.GRAPHICS,
                        description="Вертикальная синхронизация")
        self._set_config("antialiasing", 4, ConfigCategory.GRAPHICS,
                        description="Сглаживание", min_value=0, max_value=8)
        self._set_config("texture_quality", "high", ConfigCategory.GRAPHICS,
                        description="Качество текстур", 
                        options=["low", "medium", "high", "ultra"])
        self._set_config("shadow_quality", "medium", ConfigCategory.GRAPHICS,
                        description="Качество теней",
                        options=["low", "medium", "high", "ultra"])
        
        # Аудио
        self._set_config("master_volume", 1.0, ConfigCategory.AUDIO,
                        description="Общая громкость", min_value=0.0, max_value=1.0)
        self._set_config("music_volume", 0.7, ConfigCategory.AUDIO,
                        description="Громкость музыки", min_value=0.0, max_value=1.0)
        self._set_config("sfx_volume", 0.8, ConfigCategory.AUDIO,
                        description="Громкость звуковых эффектов", min_value=0.0, max_value=1.0)
        self._set_config("voice_volume", 0.9, ConfigCategory.AUDIO,
                        description="Громкость голоса", min_value=0.0, max_value=1.0)
        
        # Геймплей
        self._set_config("difficulty", "normal", ConfigCategory.GAMEPLAY,
                        description="Сложность игры",
                        options=["easy", "normal", "hard", "nightmare"])
        self._set_config("auto_save", True, ConfigCategory.GAMEPLAY,
                        description="Автоматическое сохранение")
        self._set_config("auto_save_interval", 300, ConfigCategory.GAMEPLAY,
                        description="Интервал автосохранения (секунды)", min_value=60, max_value=3600)
        self._set_config("tutorial_enabled", True, ConfigCategory.GAMEPLAY,
                        description="Включить обучение")
        self._set_config("ai_difficulty", "medium", ConfigCategory.GAMEPLAY,
                        description="Сложность ИИ",
                        options=["easy", "medium", "hard", "adaptive"])
        
        # Управление
        self._set_config("mouse_sensitivity", 1.0, ConfigCategory.CONTROLS,
                        description="Чувствительность мыши", min_value=0.1, max_value=5.0)
        self._set_config("invert_mouse_y", False, ConfigCategory.CONTROLS,
                        description="Инвертировать ось Y мыши")
        self._set_config("keyboard_layout", "qwerty", ConfigCategory.CONTROLS,
                        description="Раскладка клавиатуры",
                        options=["qwerty", "azerty", "dvorak"])
        
        # UI
        self._set_config("ui_scale", 1.0, ConfigCategory.UI,
                        description="Масштаб интерфейса", min_value=0.5, max_value=2.0)
        self._set_config("show_fps", False, ConfigCategory.UI,
                        description="Показывать FPS")
        self._set_config("show_debug_info", False, ConfigCategory.UI,
                        description="Показывать отладочную информацию")
        self._set_config("language", "ru", ConfigCategory.UI,
                        description="Язык интерфейса",
                        options=["en", "ru", "de", "fr", "es"])
        
        # ИИ
        self._set_config("ai_learning_enabled", True, ConfigCategory.AI,
                        description="Включить обучение ИИ")
        self._set_config("ai_evolution_enabled", True, ConfigCategory.AI,
                        description="Включить эволюцию ИИ")
        self._set_config("ai_memory_size", 1000, ConfigCategory.AI,
                        description="Размер памяти ИИ", min_value=100, max_value=10000)
        self._set_config("ai_decision_frequency", 0.1, ConfigCategory.AI,
                        description="Частота принятия решений ИИ (секунды)", min_value=0.01, max_value=1.0)
        
        # Производительность
        self._set_config("max_fps", 60, ConfigCategory.PERFORMANCE,
                        description="Максимальный FPS", min_value=30, max_value=300)
        self._set_config("target_fps", 60, ConfigCategory.PERFORMANCE,
                        description="Целевой FPS", min_value=30, max_value=144)
        self._set_config("frame_rate_limit", True, ConfigCategory.PERFORMANCE,
                        description="Ограничение частоты кадров")
        self._set_config("multithreading", True, ConfigCategory.PERFORMANCE,
                        description="Многопоточность")
        self._set_config("memory_optimization", True, ConfigCategory.PERFORMANCE,
                        description="Оптимизация памяти")
        
        # Отладка
        self._set_config("debug_mode", False, ConfigCategory.DEBUG,
                        description="Режим отладки")
        self._set_config("log_level", "INFO", ConfigCategory.DEBUG,
                        description="Уровень логирования",
                        options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self._set_config("save_debug_logs", False, ConfigCategory.DEBUG,
                        description="Сохранять отладочные логи")
        self._set_config("performance_profiling", False, ConfigCategory.DEBUG,
                        description="Профилирование производительности")
    
    def _set_config(self, key: str, value: Any, category: ConfigCategory, 
                   description: str = "", min_value: Optional[Union[int, float]] = None,
                   max_value: Optional[Union[int, float]] = None, 
                   options: Optional[List[str]] = None):
        """Установка конфигурации"""
        self.config[key] = ConfigValue(
            value=value,
            default=value,
            min_value=min_value,
            max_value=max_value,
            description=description,
            category=category
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        if key in self.config:
            return self.config[key].value
        return default
    
    def set(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        if key not in self.config:
            self.logger.warning(f"Попытка установить неизвестную конфигурацию: {key}")
            return False
        
        config_value = self.config[key]
        
        # Проверка ограничений
        if config_value.min_value is not None and value < config_value.min_value:
            self.logger.warning(f"Значение {key} меньше минимального: {value} < {config_value.min_value}")
            return False
        
        if config_value.max_value is not None and value > config_value.max_value:
            self.logger.warning(f"Значение {key} больше максимального: {value} > {config_value.max_value}")
            return False
        
        # Установка значения
        old_value = config_value.value
        config_value.value = value
        
        log_system_event("config_manager", "config_changed", {
            "key": key,
            "old_value": old_value,
            "new_value": value,
            "category": config_value.category.value
        })
        
        return True
    
    def get_category_configs(self, category: ConfigCategory) -> Dict[str, Any]:
        """Получение всех конфигураций категории"""
        configs = {}
        for key, config_value in self.config.items():
            if config_value.category == category:
                configs[key] = config_value.value
        return configs
    
    def reset_to_default(self, key: Optional[str] = None, category: Optional[ConfigCategory] = None):
        """Сброс конфигурации к значениям по умолчанию"""
        if key:
            if key in self.config:
                self.config[key].value = self.config[key].default
                log_system_event("config_manager", "config_reset", {"key": key})
        elif category:
            for key, config_value in self.config.items():
                if config_value.category == category:
                    config_value.value = config_value.default
            log_system_event("config_manager", "category_reset", {"category": category.value})
        else:
            for config_value in self.config.values():
                config_value.value = config_value.default
            log_system_event("config_manager", "all_configs_reset")
    
    def load_config(self, category: ConfigCategory) -> bool:
        """Загрузка конфигурации категории"""
        try:
            config_file = self.config_directory / self.config_files[category]
            if not config_file.exists():
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Загружаем только конфигурации данной категории
            for key, value in data.items():
                if key in self.config and self.config[key].category == category:
                    self.config[key].value = value
            
            log_system_event("config_manager", "config_loaded", {
                "category": category.value,
                "file": config_file.name
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации {category.value}: {e}")
            return False
    
    def save_config(self, category: ConfigCategory) -> bool:
        """Сохранение конфигурации категории"""
        try:
            config_file = self.config_directory / self.config_files[category]
            
            # Собираем конфигурации категории
            data = {}
            for key, config_value in self.config.items():
                if config_value.category == category:
                    data[key] = config_value.value
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            log_system_event("config_manager", "config_saved", {
                "category": category.value,
                "file": config_file.name
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации {category.value}: {e}")
            return False
    
    def load_all_configs(self) -> bool:
        """Загрузка всех конфигураций"""
        success = True
        for category in ConfigCategory:
            if not self.load_config(category):
                success = False
        
        log_system_event("config_manager", "all_configs_loaded", {"success": success})
        return success
    
    def save_all_configs(self) -> bool:
        """Сохранение всех конфигураций"""
        success = True
        for category in ConfigCategory:
            if not self.save_config(category):
                success = False
        
        log_system_event("config_manager", "all_configs_saved", {"success": success})
        return success
    
    def get_config_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Получение информации о конфигурации"""
        if key not in self.config:
            return None
        
        config_value = self.config[key]
        return {
            "value": config_value.value,
            "default": config_value.default,
            "min_value": config_value.min_value,
            "max_value": config_value.max_value,
            "description": config_value.description,
            "category": config_value.category.value
        }
    
    def get_all_configs_info(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о всех конфигурациях"""
        return {key: self.get_config_info(key) for key in self.config.keys()}
    
    def validate_config(self) -> List[str]:
        """Валидация конфигурации"""
        errors = []
        
        for key, config_value in self.config.items():
            # Проверка ограничений
            if config_value.min_value is not None and config_value.value < config_value.min_value:
                errors.append(f"{key}: значение {config_value.value} меньше минимального {config_value.min_value}")
            
            if config_value.max_value is not None and config_value.value > config_value.max_value:
                errors.append(f"{key}: значение {config_value.value} больше максимального {config_value.max_value}")
        
        return errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики менеджера"""
        return {
            "total_configs": len(self.config),
            "categories": {
                category.value: len([c for c in self.config.values() if c.category == category])
                for category in ConfigCategory
            },
            "config_files": {
                category.value: self.config_files[category]
                for category in ConfigCategory
            },
            "validation_errors": len(self.validate_config())
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        # Сохраняем все конфигурации перед очисткой
        self.save_all_configs()
        
        self.config.clear()
        self.config_files.clear()
        
        log_system_event("config_manager", "cleanup_completed")
