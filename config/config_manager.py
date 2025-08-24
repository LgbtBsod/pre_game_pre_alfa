#!/usr/bin/env python3
"""
Улучшенная система управления конфигурацией
Включает валидацию, горячую перезагрузку и типизированные настройки
"""

import json
import logging
import os
from typing import Dict, Any, Optional, Union, List, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import threading
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class DisplayConfig:
    """Конфигурация отображения"""
    window_width: int = 1600
    window_height: int = 900
    fullscreen: bool = False
    vsync: bool = True
    render_fps: int = 120
    hardware_acceleration: bool = True
    anti_aliasing: bool = True
    texture_quality: str = "high"  # low, medium, high, ultra
    shadow_quality: str = "medium"  # off, low, medium, high
    particle_count: int = 200


@dataclass
class AudioConfig:
    """Конфигурация аудио"""
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    master_volume: float = 1.0
    enable_music: bool = True
    enable_sfx: bool = True
    audio_quality: str = "high"  # low, medium, high
    max_sounds: int = 32


@dataclass
class GameplayConfig:
    """Конфигурация геймплея"""
    difficulty: str = "normal"  # easy, normal, hard, nightmare
    auto_save: bool = True
    auto_save_interval: int = 300  # секунды
    tutorial_enabled: bool = True
    language: str = "ru"
    subtitles: bool = True
    camera_sensitivity: float = 1.0
    invert_y_axis: bool = False


@dataclass
class EnhancedConfig:
    """Конфигурация Enhanced Edition"""
    enabled: bool = True
    memory_system: bool = True
    emotional_ai: bool = True
    enhanced_combat: bool = True
    enhanced_content: bool = True
    skill_system: bool = True
    curse_blessing: bool = True
    risk_reward: bool = True
    meta_progression: bool = True


@dataclass
class DebugConfig:
    """Конфигурация отладки"""
    enabled: bool = False
    show_fps: bool = False
    show_debug_info: bool = False
    log_level: str = "INFO"
    save_debug_logs: bool = True
    performance_profiling: bool = False
    show_hitboxes: bool = False
    show_pathfinding: bool = False


@dataclass
class PerformanceConfig:
    """Конфигурация производительности"""
    auto_optimize: bool = True
    target_fps: int = 60
    max_entities: int = 100
    max_particles: int = 200
    memory_limit_mb: int = 512
    gc_interval: int = 300  # секунды
    texture_cache_size: int = 100
    sound_cache_size: int = 50


class ConfigValidator:
    """Валидатор конфигурации"""
    
    @staticmethod
    def validate_display(config: DisplayConfig) -> List[str]:
        """Валидация конфигурации отображения"""
        errors = []
        
        if config.window_width < 800 or config.window_width > 3840:
            errors.append("window_width должен быть в диапазоне 800-3840")
        
        if config.window_height < 600 or config.window_height > 2160:
            errors.append("window_height должен быть в диапазоне 600-2160")
        
        if config.render_fps < 30 or config.render_fps > 300:
            errors.append("render_fps должен быть в диапазоне 30-300")
        
        if config.particle_count < 0 or config.particle_count > 1000:
            errors.append("particle_count должен быть в диапазоне 0-1000")
        
        valid_texture_qualities = ["low", "medium", "high", "ultra"]
        if config.texture_quality not in valid_texture_qualities:
            errors.append(f"texture_quality должен быть одним из: {valid_texture_qualities}")
        
        valid_shadow_qualities = ["off", "low", "medium", "high"]
        if config.shadow_quality not in valid_shadow_qualities:
            errors.append(f"shadow_quality должен быть одним из: {valid_shadow_qualities}")
        
        return errors
    
    @staticmethod
    def validate_audio(config: AudioConfig) -> List[str]:
        """Валидация конфигурации аудио"""
        errors = []
        
        for volume_name, volume_value in [
            ("music_volume", config.music_volume),
            ("sfx_volume", config.sfx_volume),
            ("master_volume", config.master_volume)
        ]:
            if volume_value < 0.0 or volume_value > 1.0:
                errors.append(f"{volume_name} должен быть в диапазоне 0.0-1.0")
        
        if config.max_sounds < 1 or config.max_sounds > 128:
            errors.append("max_sounds должен быть в диапазоне 1-128")
        
        valid_audio_qualities = ["low", "medium", "high"]
        if config.audio_quality not in valid_audio_qualities:
            errors.append(f"audio_quality должен быть одним из: {valid_audio_qualities}")
        
        return errors
    
    @staticmethod
    def validate_gameplay(config: GameplayConfig) -> List[str]:
        """Валидация конфигурации геймплея"""
        errors = []
        
        valid_difficulties = ["easy", "normal", "hard", "nightmare"]
        if config.difficulty not in valid_difficulties:
            errors.append(f"difficulty должен быть одним из: {valid_difficulties}")
        
        if config.auto_save_interval < 60 or config.auto_save_interval > 3600:
            errors.append("auto_save_interval должен быть в диапазоне 60-3600 секунд")
        
        if config.camera_sensitivity < 0.1 or config.camera_sensitivity > 5.0:
            errors.append("camera_sensitivity должен быть в диапазоне 0.1-5.0")
        
        return errors
    
    @staticmethod
    def validate_performance(config: PerformanceConfig) -> List[str]:
        """Валидация конфигурации производительности"""
        errors = []
        
        if config.target_fps < 30 or config.target_fps > 300:
            errors.append("target_fps должен быть в диапазоне 30-300")
        
        if config.max_entities < 10 or config.max_entities > 1000:
            errors.append("max_entities должен быть в диапазоне 10-1000")
        
        if config.max_particles < 0 or config.max_particles > 2000:
            errors.append("max_particles должен быть в диапазоне 0-2000")
        
        if config.memory_limit_mb < 128 or config.memory_limit_mb > 4096:
            errors.append("memory_limit_mb должен быть в диапазоне 128-4096")
        
        return errors


class ConfigManager:
    """Менеджер конфигурации"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Конфигурации
        self.display = DisplayConfig()
        self.audio = AudioConfig()
        self.gameplay = GameplayConfig()
        self.enhanced = EnhancedConfig()
        self.debug = DebugConfig()
        self.performance = PerformanceConfig()
        
        # Кэш конфигурации
        self._config_cache: Dict[str, Any] = {}
        self._lock = threading.RLock()
        
        # Callbacks для изменений
        self._change_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Загрузка конфигурации
        self.load_all_configs()
        
        logger.info("Менеджер конфигурации инициализирован")
    
    def load_all_configs(self):
        """Загрузка всех конфигураций"""
        try:
            self._load_config('display', self.display)
            self._load_config('audio', self.audio)
            self._load_config('gameplay', self.gameplay)
            self._load_config('enhanced', self.enhanced)
            self._load_config('debug', self.debug)
            self._load_config('performance', self.performance)
            
            logger.info("Все конфигурации загружены")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигураций: {e}")
            self._create_default_configs()
    
    def _load_config(self, name: str, config_obj: Any):
        """Загрузка конкретной конфигурации"""
        config_file = self.config_dir / f"{name}_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Обновляем объект конфигурации
                for key, value in data.items():
                    if hasattr(config_obj, key):
                        setattr(config_obj, key, value)
                
                logger.info(f"Конфигурация {name} загружена из {config_file}")
                
            except Exception as e:
                logger.error(f"Ошибка загрузки конфигурации {name}: {e}")
                self._save_config(name, config_obj)
        else:
            # Создаем файл с настройками по умолчанию
            self._save_config(name, config_obj)
    
    def _save_config(self, name: str, config_obj: Any):
        """Сохранение конфигурации"""
        config_file = self.config_dir / f"{name}_config.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(config_obj), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Конфигурация {name} сохранена в {config_file}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации {name}: {e}")
    
    def _create_default_configs(self):
        """Создание конфигураций по умолчанию"""
        logger.info("Создание конфигураций по умолчанию")
        
        self._save_config('display', self.display)
        self._save_config('audio', self.audio)
        self._save_config('gameplay', self.gameplay)
        self._save_config('enhanced', self.enhanced)
        self._save_config('debug', self.debug)
        self._save_config('performance', self.performance)
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        with self._lock:
            try:
                config_obj = getattr(self, section, None)
                if config_obj:
                    return getattr(config_obj, key, default)
                return default
            except Exception as e:
                logger.error(f"Ошибка получения конфигурации {section}.{key}: {e}")
                return default
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        with self._lock:
            try:
                config_obj = getattr(self, section, None)
                if config_obj and hasattr(config_obj, key):
                    old_value = getattr(config_obj, key)
                    setattr(config_obj, key, value)
                    
                    # Валидация
                    if not self._validate_config(section, config_obj):
                        # Откатываем изменения при ошибке валидации
                        setattr(config_obj, key, old_value)
                        return False
                    
                    # Сохраняем конфигурацию
                    self._save_config(section, config_obj)
                    
                    # Уведомляем об изменениях
                    self._notify_change(section, key, old_value, value)
                    
                    logger.info(f"Конфигурация обновлена: {section}.{key} = {value}")
                    return True
                
                return False
                
            except Exception as e:
                logger.error(f"Ошибка установки конфигурации {section}.{key}: {e}")
                return False
    
    def _validate_config(self, section: str, config_obj: Any) -> bool:
        """Валидация конфигурации"""
        try:
            validator = ConfigValidator()
            
            if section == 'display':
                errors = validator.validate_display(config_obj)
            elif section == 'audio':
                errors = validator.validate_audio(config_obj)
            elif section == 'gameplay':
                errors = validator.validate_gameplay(config_obj)
            elif section == 'performance':
                errors = validator.validate_performance(config_obj)
            else:
                return True  # Для остальных секций валидация не требуется
            
            if errors:
                logger.error(f"Ошибки валидации конфигурации {section}: {errors}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации конфигурации {section}: {e}")
            return False
    
    def _notify_change(self, section: str, key: str, old_value: Any, new_value: Any):
        """Уведомление об изменении конфигурации"""
        callback_key = f"{section}.{key}"
        for callback in self._change_callbacks[callback_key]:
            try:
                callback(old_value, new_value)
            except Exception as e:
                logger.error(f"Ошибка в callback изменения конфигурации: {e}")
    
    def register_change_callback(self, section: str, key: str, callback: Callable[[Any, Any], None]):
        """Регистрация callback для изменений конфигурации"""
        callback_key = f"{section}.{key}"
        self._change_callbacks[callback_key].append(callback)
        logger.info(f"Зарегистрирован callback для {callback_key}")
    
    def unregister_change_callback(self, section: str, key: str, callback: Callable[[Any, Any], None]):
        """Отмена регистрации callback"""
        callback_key = f"{section}.{key}"
        if callback_key in self._change_callbacks:
            if callback in self._change_callbacks[callback_key]:
                self._change_callbacks[callback_key].remove(callback)
                logger.info(f"Callback для {callback_key} отменен")
    
    def reload_config(self, section: str = None):
        """Перезагрузка конфигурации"""
        with self._lock:
            try:
                if section:
                    config_obj = getattr(self, section, None)
                    if config_obj:
                        self._load_config(section, config_obj)
                        logger.info(f"Конфигурация {section} перезагружена")
                else:
                    self.load_all_configs()
                    logger.info("Все конфигурации перезагружены")
                    
            except Exception as e:
                logger.error(f"Ошибка перезагрузки конфигурации: {e}")
    
    def export_config(self, filename: str = None) -> str:
        """Экспорт конфигурации"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"config_export_{timestamp}.json"
        
        try:
            export_data = {
                'display': asdict(self.display),
                'audio': asdict(self.audio),
                'gameplay': asdict(self.gameplay),
                'enhanced': asdict(self.enhanced),
                'debug': asdict(self.debug),
                'performance': asdict(self.performance),
                'export_timestamp': datetime.now().isoformat()
            }
            
            export_file = self.config_dir / filename
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Конфигурация экспортирована в {export_file}")
            return str(export_file)
            
        except Exception as e:
            logger.error(f"Ошибка экспорта конфигурации: {e}")
            return ""
    
    def import_config(self, filename: str) -> bool:
        """Импорт конфигурации"""
        try:
            import_file = Path(filename)
            if not import_file.exists():
                logger.error(f"Файл конфигурации не найден: {filename}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Обновляем конфигурации
            for section, data in import_data.items():
                if section in ['display', 'audio', 'gameplay', 'enhanced', 'debug', 'performance']:
                    config_obj = getattr(self, section, None)
                    if config_obj:
                        for key, value in data.items():
                            if hasattr(config_obj, key):
                                setattr(config_obj, key, value)
            
            # Сохраняем все конфигурации
            self._save_config('display', self.display)
            self._save_config('audio', self.audio)
            self._save_config('gameplay', self.gameplay)
            self._save_config('enhanced', self.enhanced)
            self._save_config('debug', self.debug)
            self._save_config('performance', self.performance)
            
            logger.info(f"Конфигурация импортирована из {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка импорта конфигурации: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Получение сводки конфигурации"""
        return {
            'display': {
                'resolution': f"{self.display.window_width}x{self.display.window_height}",
                'fullscreen': self.display.fullscreen,
                'fps': self.display.render_fps,
                'quality': self.display.texture_quality
            },
            'audio': {
                'master_volume': self.audio.master_volume,
                'music_volume': self.audio.music_volume,
                'sfx_volume': self.audio.sfx_volume
            },
            'gameplay': {
                'difficulty': self.gameplay.difficulty,
                'language': self.gameplay.language,
                'auto_save': self.gameplay.auto_save
            },
            'enhanced': {
                'enabled': self.enhanced.enabled,
                'features': [
                    'memory_system' if self.enhanced.memory_system else None,
                    'emotional_ai' if self.enhanced.emotional_ai else None,
                    'enhanced_combat' if self.enhanced.enhanced_combat else None,
                    'enhanced_content' if self.enhanced.enhanced_content else None,
                    'skill_system' if self.enhanced.skill_system else None,
                    'curse_blessing' if self.enhanced.curse_blessing else None,
                    'risk_reward' if self.enhanced.risk_reward else None,
                    'meta_progression' if self.enhanced.meta_progression else None
                ]
            },
            'performance': {
                'auto_optimize': self.performance.auto_optimize,
                'target_fps': self.performance.target_fps,
                'max_entities': self.performance.max_entities
            }
        }


# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()
