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
from .interfaces import IConfigManager

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

class ConfigManager(IConfigManager):
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
            return {}
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        try:
            keys = key.split('.')
            value = self._loaded_config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception as e:
            logger.error(f"Ошибка получения конфигурации {key}: {e}")
            return default
    
    def set_config(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        try:
            keys = key.split('.')
            config = self._loaded_config
            
            # Проходим по всем ключам кроме последнего
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Устанавливаем значение
            config[keys[-1]] = value
            
            # Сохраняем изменения
            self._save_config()
            
            logger.debug(f"Конфигурация {key} установлена в {value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки конфигурации {key}: {e}")
            return False
            return self._loaded_config
            return self._loaded_config
        except:
            logger.error("Ошибка загрузки конфигурации")
    
    # Реализация интерфейса IConfigManager
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Сохранение конфигурации"""
        try:
            # Обновляем внутренние конфигурации
            if 'display' in config:
                for key, value in config['display'].items():
                    if hasattr(self.display_config, key):
                        setattr(self.display_config, key, value)
            
            if 'audio' in config:
                for key, value in config['audio'].items():
                    if hasattr(self.audio_config, key):
                        setattr(self.audio_config, key, value)
            
            if 'gameplay' in config:
                for key, value in config['gameplay'].items():
                    if hasattr(self.gameplay_config, key):
                        setattr(self.gameplay_config, key, value)
            
            if 'ai' in config:
                for key, value in config['ai'].items():
                    if hasattr(self.ai_config, key):
                        setattr(self.ai_config, key, value)
            
            if 'performance' in config:
                for key, value in config['performance'].items():
                    if hasattr(self.performance_config, key):
                        setattr(self.performance_config, key, value)
            
            # Сохраняем в файлы
            self._save_display_config()
            self._save_audio_config()
            self._save_gameplay_config()
            self._save_ai_config()
            self._save_performance_config()
            
            logger.info("Конфигурация успешно сохранена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        try:
            # Разбираем ключ (например: "display.window_width")
            if '.' in key:
                section, param = key.split('.', 1)
                if section == 'display' and hasattr(self.display_config, param):
                    return getattr(self.display_config, param)
                elif section == 'audio' and hasattr(self.audio_config, param):
                    return getattr(self.audio_config, param)
                elif section == 'gameplay' and hasattr(self.gameplay_config, param):
                    return getattr(self.gameplay_config, param)
                elif section == 'ai' and hasattr(self.ai_config, param):
                    return getattr(self.ai_config, param)
                elif section == 'performance' and hasattr(self.performance_config, param):
                    return getattr(self.performance_config, param)
            else:
                # Прямой доступ к загруженной конфигурации
                return self._loaded_config.get(key, default)
            
            return default
            
        except Exception as e:
            logger.error(f"Ошибка получения значения {key}: {e}")
            return default
    
    def set_value(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        try:
            # Разбираем ключ (например: "display.window_width")
            if '.' in key:
                section, param = key.split('.', 1)
                if section == 'display' and hasattr(self.display_config, param):
                    setattr(self.display_config, param, value)
                    self._save_display_config()
                    return True
                elif section == 'audio' and hasattr(self.audio_config, param):
                    setattr(self.audio_config, param, value)
                    self._save_audio_config()
                    return True
                elif section == 'gameplay' and hasattr(self.gameplay_config, param):
                    setattr(self.gameplay_config, param, value)
                    self._save_gameplay_config()
                    return True
                elif section == 'ai' and hasattr(self.ai_config, param):
                    setattr(self.ai_config, param, value)
                    self._save_ai_config()
                    return True
                elif section == 'performance' and hasattr(self.performance_config, param):
                    setattr(self.performance_config, param, value)
                    self._save_performance_config()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка установки значения {key}: {e}")
            return False
            
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
    
    # Реализация методов интерфейса ISystem
    def initialize(self) -> bool:
        """Инициализация системы"""
        try:
            self.load_config()
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации ConfigManager: {e}")
            return False
    
    def update(self, delta_time: float):
        """Обновление системы"""
        # ConfigManager не требует постоянного обновления
        pass
    
    def cleanup(self):
        """Очистка системы"""
        try:
            self.save_config()
            logger.info("ConfigManager очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки ConfigManager: {e}")
    
    # Реализация методов интерфейса IConfigManager
    def get_value(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        # Поддерживаем формат "section.key"
        if '.' in key:
            section, subkey = key.split('.', 1)
            return self.get(section, subkey, default)
        else:
            # Ищем во всех секциях
            for section in self._loaded_config:
                if key in self._loaded_config[section]:
                    return self._loaded_config[section][key]
            return default
    
    def set_value(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        try:
            # Поддерживаем формат "section.key"
            if '.' in key:
                section, subkey = key.split('.', 1)
                self.set(section, subkey, value)
            else:
                # Устанавливаем в первую доступную секцию
                if self._loaded_config:
                    first_section = list(self._loaded_config.keys())[0]
                    self.set(first_section, key, value)
            return True
        except Exception as e:
            logger.error(f"Ошибка установки значения {key}: {e}")
            return False
