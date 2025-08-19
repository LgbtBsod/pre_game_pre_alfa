"""
Фабрика конфигурации
Устраняет хардкод путей и обеспечивает гибкую загрузку конфигурации
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from dataclasses import dataclass

from .config_manager import ConfigManager
from core.error_handler import ErrorHandler, ErrorType, ErrorSeverity

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Типы конфигурации"""
    GAME_SETTINGS = "game_settings"
    ENTITIES = "entities_config"
    ITEMS = "items_config"
    AI = "ai_config"
    UI = "ui_config"
    AUDIO = "audio_config"
    GRAPHICS = "graphics_config"
    NETWORK = "network_config"


class ConfigSource(Enum):
    """Источники конфигурации"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DEFAULT = "default"
    REMOTE = "remote"


@dataclass
class ConfigDefinition:
    """Определение конфигурации"""
    config_type: ConfigType
    source: ConfigSource
    path: Optional[str] = None
    default_data: Optional[Dict[str, Any]] = None
    required: bool = True
    auto_reload: bool = False
    validation_schema: Optional[Dict[str, Any]] = None


class ConfigFactory:
    """
    Фабрика конфигурации.
    Управляет созданием и загрузкой различных типов конфигурации.
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.error_handler = ErrorHandler()
        self.config_manager = ConfigManager(str(self.config_dir))
        
        # Определения конфигураций
        self.config_definitions: Dict[ConfigType, ConfigDefinition] = {}
        self._setup_config_definitions()
        
        # Кэш загруженных конфигураций
        self._loaded_configs: Dict[ConfigType, Dict[str, Any]] = {}
        
        # Валидаторы конфигураций
        self._validators: Dict[ConfigType, callable] = {}
        self._setup_validators()
    
    def _setup_config_definitions(self):
        """Настройка определений конфигураций"""
        self.config_definitions = {
            ConfigType.GAME_SETTINGS: ConfigDefinition(
                config_type=ConfigType.GAME_SETTINGS,
                source=ConfigSource.FILE,
                path="game_settings.json",
                required=True,
                auto_reload=True,
                default_data={
                    "display": {
                        "window_width": 1280,
                        "window_height": 720,
                        "fullscreen": False,
                        "vsync": True,
                        "render_fps": 60
                    },
                    "audio": {
                        "music_volume": 0.7,
                        "sfx_volume": 0.8,
                        "master_volume": 1.0
                    },
                    "gameplay": {
                        "difficulty": "normal",
                        "language": "ru",
                        "autosave": True
                    }
                }
            ),
            
            ConfigType.ENTITIES: ConfigDefinition(
                config_type=ConfigType.ENTITIES,
                source=ConfigSource.FILE,
                path="entities_config.json",
                required=True,
                auto_reload=False,
                default_data={
                    "player": {
                        "health": 100,
                        "speed": 1.0,
                        "damage": 20
                    },
                    "enemy": {
                        "health": 50,
                        "speed": 0.8,
                        "damage": 15
                    }
                }
            ),
            
            ConfigType.ITEMS: ConfigDefinition(
                config_type=ConfigType.ITEMS,
                source=ConfigSource.FILE,
                path="items_config.json",
                required=False,
                auto_reload=False,
                default_data={}
            ),
            
            ConfigType.AI: ConfigDefinition(
                config_type=ConfigType.AI,
                source=ConfigSource.FILE,
                path="ai_config.json",
                required=False,
                auto_reload=False,
                default_data={
                    "difficulty_scaling": True,
                    "learning_rate": 0.1,
                    "max_complexity": 5
                }
            ),
            
            ConfigType.UI: ConfigDefinition(
                config_type=ConfigType.UI,
                source=ConfigSource.FILE,
                path="ui_config.json",
                required=False,
                auto_reload=True,
                default_data={
                    "theme": "default",
                    "font_size": 16,
                    "show_fps": False,
                    "show_debug": False
                }
            ),
            
            ConfigType.AUDIO: ConfigDefinition(
                config_type=ConfigType.AUDIO,
                source=ConfigSource.FILE,
                path="audio_config.json",
                required=False,
                auto_reload=False,
                default_data={
                    "sample_rate": 44100,
                    "channels": 2,
                    "buffer_size": 1024
                }
            ),
            
            ConfigType.GRAPHICS: ConfigDefinition(
                config_type=ConfigType.GRAPHICS,
                source=ConfigSource.FILE,
                path="graphics_config.json",
                required=False,
                auto_reload=False,
                default_data={
                    "texture_quality": "high",
                    "shadow_quality": "medium",
                    "particle_effects": True
                }
            ),
            
            ConfigType.NETWORK: ConfigDefinition(
                config_type=ConfigType.NETWORK,
                source=ConfigSource.FILE,
                path="network_config.json",
                required=False,
                auto_reload=False,
                default_data={
                    "server_address": "localhost",
                    "port": 8080,
                    "timeout": 30
                }
            )
        }
    
    def _setup_validators(self):
        """Настройка валидаторов конфигураций"""
        self._validators[ConfigType.GAME_SETTINGS] = self._validate_game_settings
        self._validators[ConfigType.ENTITIES] = self._validate_entities_config
        self._validators[ConfigType.UI] = self._validate_ui_config
    
    def create_config(self, config_type: ConfigType) -> Dict[str, Any]:
        """
        Создание конфигурации указанного типа
        
        Args:
            config_type: Тип конфигурации
            
        Returns:
            Загруженная конфигурация
        """
        if config_type not in self.config_definitions:
            self.error_handler.handle_error(
                ErrorType.CONFIGURATION,
                f"Неизвестный тип конфигурации: {config_type}",
                severity=ErrorSeverity.ERROR
            )
            return {}
        
        definition = self.config_definitions[config_type]
        
        try:
            # Проверяем кэш
            if config_type in self._loaded_configs:
                return self._loaded_configs[config_type]
            
            # Загружаем конфигурацию
            config_data = self._load_config(definition)
            
            # Валидируем конфигурацию
            if config_type in self._validators:
                if not self._validators[config_type](config_data):
                    logger.warning(f"Валидация конфигурации {config_type.value} не прошла, используются значения по умолчанию")
                    config_data = definition.default_data or {}
            
            # Кэшируем результат
            self._loaded_configs[config_type] = config_data
            
            logger.info(f"Конфигурация {config_type.value} успешно загружена")
            return config_data
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.CONFIGURATION,
                f"Ошибка создания конфигурации {config_type.value}: {str(e)}",
                exception=e,
                context={'config_type': config_type.value},
                severity=ErrorSeverity.ERROR
            )
            
            # Возвращаем данные по умолчанию
            return definition.default_data or {}
    
    def _load_config(self, definition: ConfigDefinition) -> Dict[str, Any]:
        """Загрузка конфигурации из источника"""
        if definition.source == ConfigSource.FILE:
            return self._load_from_file(definition)
        elif definition.source == ConfigSource.ENVIRONMENT:
            return self._load_from_environment(definition)
        elif definition.source == ConfigSource.DEFAULT:
            return definition.default_data or {}
        else:
            logger.warning(f"Неизвестный источник конфигурации: {definition.source}")
            return definition.default_data or {}
    
    def _load_from_file(self, definition: ConfigDefinition) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        if not definition.path:
            return definition.default_data or {}
        
        config_path = self.config_dir / definition.path
        
        if not config_path.exists():
            if definition.required:
                logger.warning(f"Файл конфигурации {config_path} не найден, создается с значениями по умолчанию")
                self._create_default_config_file(config_path, definition.default_data or {})
            else:
                logger.info(f"Файл конфигурации {config_path} не найден, используются значения по умолчанию")
                return definition.default_data or {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Объединяем с данными по умолчанию
            if definition.default_data:
                config_data = self._merge_with_defaults(config_data, definition.default_data)
            
            return config_data
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.CONFIGURATION,
                f"Ошибка чтения файла конфигурации {config_path}: {str(e)}",
                exception=e,
                context={'file_path': str(config_path)},
                severity=ErrorSeverity.ERROR
            )
            return definition.default_data or {}
    
    def _load_from_environment(self, definition: ConfigDefinition) -> Dict[str, Any]:
        """Загрузка конфигурации из переменных окружения"""
        config_data = {}
        
        # Префикс для переменных окружения
        prefix = f"GAME_{definition.config_type.value.upper()}_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config_data[config_key] = self._parse_environment_value(value)
        
        return config_data
    
    def _parse_environment_value(self, value: str) -> Any:
        """Парсинг значения переменной окружения"""
        # Пытаемся преобразовать в число
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Проверяем булевы значения
        if value.lower() in ['true', '1', 'yes', 'on']:
            return True
        elif value.lower() in ['false', '0', 'no', 'off']:
            return False
        
        # Возвращаем как строку
        return value
    
    def _create_default_config_file(self, config_path: Path, default_data: Dict[str, Any]):
        """Создание файла конфигурации с значениями по умолчанию"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Создан файл конфигурации с значениями по умолчанию: {config_path}")
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.CONFIGURATION,
                f"Ошибка создания файла конфигурации {config_path}: {str(e)}",
                exception=e,
                context={'file_path': str(config_path)},
                severity=ErrorSeverity.ERROR
            )
    
    def _merge_with_defaults(self, config_data: Dict[str, Any], default_data: Dict[str, Any]) -> Dict[str, Any]:
        """Объединение конфигурации с значениями по умолчанию"""
        result = default_data.copy()
        
        def merge_dicts(target: Dict[str, Any], source: Dict[str, Any]):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dicts(target[key], value)
                else:
                    target[key] = value
        
        merge_dicts(result, config_data)
        return result
    
    def _validate_game_settings(self, config_data: Dict[str, Any]) -> bool:
        """Валидация настроек игры"""
        try:
            # Проверяем обязательные поля
            required_fields = ['display', 'audio', 'gameplay']
            for field in required_fields:
                if field not in config_data:
                    logger.error(f"Отсутствует обязательное поле в настройках игры: {field}")
                    return False
            
            # Проверяем значения
            display = config_data.get('display', {})
            if display.get('window_width', 0) <= 0 or display.get('window_height', 0) <= 0:
                logger.error("Некорректные размеры окна")
                return False
            
            audio = config_data.get('audio', {})
            for volume_key in ['music_volume', 'sfx_volume', 'master_volume']:
                volume = audio.get(volume_key, 1.0)
                if not 0.0 <= volume <= 1.0:
                    logger.error(f"Некорректная громкость: {volume_key} = {volume}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации настроек игры: {e}")
            return False
    
    def _validate_entities_config(self, config_data: Dict[str, Any]) -> bool:
        """Валидация конфигурации сущностей"""
        try:
            # Проверяем наличие основных типов сущностей
            required_entities = ['player', 'enemy']
            for entity_type in required_entities:
                if entity_type not in config_data:
                    logger.error(f"Отсутствует конфигурация для типа сущности: {entity_type}")
                    return False
                
                entity_config = config_data[entity_type]
                if not isinstance(entity_config, dict):
                    logger.error(f"Некорректная конфигурация для сущности {entity_type}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации конфигурации сущностей: {e}")
            return False
    
    def _validate_ui_config(self, config_data: Dict[str, Any]) -> bool:
        """Валидация конфигурации UI"""
        try:
            # Проверяем размер шрифта
            font_size = config_data.get('font_size', 16)
            if not isinstance(font_size, int) or font_size <= 0:
                logger.error("Некорректный размер шрифта")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации конфигурации UI: {e}")
            return False
    
    def reload_config(self, config_type: ConfigType) -> bool:
        """Перезагрузка конфигурации"""
        try:
            if config_type in self._loaded_configs:
                del self._loaded_configs[config_type]
            
            self.create_config(config_type)
            logger.info(f"Конфигурация {config_type.value} перезагружена")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.CONFIGURATION,
                f"Ошибка перезагрузки конфигурации {config_type.value}: {str(e)}",
                exception=e,
                context={'config_type': config_type.value},
                severity=ErrorSeverity.ERROR
            )
            return False
    
    def get_all_configs(self) -> Dict[ConfigType, Dict[str, Any]]:
        """Получение всех конфигураций"""
        result = {}
        for config_type in ConfigType:
            result[config_type] = self.create_config(config_type)
        return result
    
    def save_config(self, config_type: ConfigType, config_data: Dict[str, Any]) -> bool:
        """Сохранение конфигурации в файл"""
        try:
            definition = self.config_definitions.get(config_type)
            if not definition or not definition.path:
                return False
            
            config_path = self.config_dir / definition.path
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # Обновляем кэш
            self._loaded_configs[config_type] = config_data
            
            logger.info(f"Конфигурация {config_type.value} сохранена")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.CONFIGURATION,
                f"Ошибка сохранения конфигурации {config_type.value}: {str(e)}",
                exception=e,
                context={'config_type': config_type.value},
                severity=ErrorSeverity.ERROR
            )
            return False


# Глобальный экземпляр фабрики конфигурации
config_factory = ConfigFactory()
