#!/usr/bin/env python3
"""
Config Manager - Менеджер конфигурации игры
Отвечает только за загрузку, валидацию и управление настройками
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class DisplayConfig:
    """Конфигурация отображения"""
    window_width: int = 1600
    window_height: int = 900
    fullscreen: bool = False
    vsync: bool = True
    fps: int = 120
    render_scale: float = 1.0

@dataclass
class AudioConfig:
    """Конфигурация аудио"""
    master_volume: float = 1.0
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    enable_music: bool = True
    enable_sfx: bool = True

@dataclass
class GameplayConfig:
    """Конфигурация геймплея"""
    difficulty: str = "normal"
    auto_save: bool = True
    save_interval: int = 300  # секунды
    enable_tutorial: bool = True
    language: str = "en"

@dataclass
class AIConfig:
    """Конфигурация ИИ"""
    learning_rate: float = 0.1
    exploration_rate: float = 0.1
    memory_size: int = 1000
    enable_adaptive_difficulty: bool = True
    ai_update_frequency: float = 0.1

@dataclass
class PerformanceConfig:
    """Конфигурация производительности"""
    enable_vsync: bool = True
    max_fps: int = 120
    enable_multithreading: bool = True
    texture_quality: str = "high"
    shadow_quality: str = "medium"

class ConfigManager:
    """Менеджер конфигурации игры"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        # Конфигурации по умолчанию
        self.display_config = DisplayConfig()
        self.audio_config = AudioConfig()
        self.gameplay_config = GameplayConfig()
        self.ai_config = AIConfig()
        self.performance_config = PerformanceConfig()
        
        # Загруженная конфигурация
        self._loaded_config: Dict[str, Any] = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файлов"""
        try:
            logger.info("Загрузка конфигурации...")
            
            # Загружаем основные настройки
            self._load_display_config()
            self._load_audio_config()
            self._load_gameplay_config()
            self._load_ai_config()
            self._load_performance_config()
            
            # Собираем общую конфигурацию
            self._loaded_config = {
                'display': asdict(self.display_config),
                'audio': asdict(self.audio_config),
                'gameplay': asdict(self.gameplay_config),
                'ai': asdict(self.ai_config),
                'performance': asdict(self.performance_config)
            }
            
            logger.info("Конфигурация успешно загружена")
            return self._loaded_config
            
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return self._get_default_config()
    
    def _load_display_config(self):
        """Загрузка конфигурации отображения"""
        config_file = self.config_dir / "display_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.display_config, key):
                            setattr(self.display_config, key, value)
            except Exception as e:
                logger.warning(f"Ошибка загрузки display_config.json: {e}")
    
    def _load_audio_config(self):
        """Загрузка конфигурации аудио"""
        config_file = self.config_dir / "audio_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.audio_config, key):
                            setattr(self.audio_config, key, value)
            except Exception as e:
                logger.warning(f"Ошибка загрузки audio_config.json: {e}")
    
    def _load_gameplay_config(self):
        """Загрузка конфигурации геймплея"""
        config_file = self.config_dir / "gameplay_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.gameplay_config, key):
                            setattr(self.gameplay_config, key, value)
            except Exception as e:
                logger.warning(f"Ошибка загрузки gameplay_config.json: {e}")
    
    def _load_ai_config(self):
        """Загрузка конфигурации ИИ"""
        config_file = self.config_dir / "ai_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.ai_config, key):
                            setattr(self.ai_config, key, value)
            except Exception as e:
                logger.warning(f"Ошибка загрузки ai_config.json: {e}")
    
    def _load_performance_config(self):
        """Загрузка конфигурации производительности"""
        config_file = self.config_dir / "performance_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.performance_config, key):
                            setattr(self.performance_config, key, value)
            except Exception as e:
                logger.warning(f"Ошибка загрузки performance_config.json: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Получение конфигурации по умолчанию"""
        return {
            'display': asdict(self.display_config),
            'audio': asdict(self.audio_config),
            'gameplay': asdict(self.gameplay_config),
            'ai': asdict(self.ai_config),
            'performance': asdict(self.performance_config)
        }
    
    def save_config(self):
        """Сохранение текущей конфигурации в файлы"""
        try:
            logger.info("Сохранение конфигурации...")
            
            # Сохраняем каждую секцию в отдельный файл
            self._save_section_config('display_config.json', asdict(self.display_config))
            self._save_section_config('audio_config.json', asdict(self.audio_config))
            self._save_section_config('gameplay_config.json', asdict(self.gameplay_config))
            self._save_section_config('ai_config.json', asdict(self.ai_config))
            self._save_section_config('performance_config.json', asdict(self.performance_config))
            
            logger.info("Конфигурация успешно сохранена")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
    
    def _save_section_config(self, filename: str, data: Dict[str, Any]):
        """Сохранение секции конфигурации в файл"""
        config_file = self.config_dir / filename
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения {filename}: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        try:
            return self._loaded_config.get(section, {}).get(key, default)
        except (KeyError, AttributeError):
            return default
    
    def set(self, section: str, key: str, value: Any):
        """Установка значения конфигурации"""
        if section not in self._loaded_config:
            self._loaded_config[section] = {}
        self._loaded_config[section][key] = value
        
        # Обновляем соответствующий объект конфигурации
        self._update_config_object(section, key, value)
    
    def _update_config_object(self, section: str, key: str, value: Any):
        """Обновление объекта конфигурации"""
        config_objects = {
            'display': self.display_config,
            'audio': self.audio_config,
            'gameplay': self.gameplay_config,
            'ai': self.ai_config,
            'performance': self.performance_config
        }
        
        if section in config_objects and hasattr(config_objects[section], key):
            setattr(config_objects[section], key, value)
    
    def reset_to_defaults(self):
        """Сброс к настройкам по умолчанию"""
        logger.info("Сброс конфигурации к настройкам по умолчанию")
        
        self.display_config = DisplayConfig()
        self.audio_config = AudioConfig()
        self.gameplay_config = GameplayConfig()
        self.ai_config = AIConfig()
        self.performance_config = PerformanceConfig()
        
        self._loaded_config = self._get_default_config()
