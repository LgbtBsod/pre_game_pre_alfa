#!/usr/bin/env python3
"""
Оптимизированный валидатор конфигурации.
Включает проверку схем, автоматическую коррекцию и валидацию типов.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Типы конфигурационных значений"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"


@dataclass
class ValidationResult:
    """Результат валидации конфигурации"""
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class ConfigField:
    """Поле конфигурации"""
    name: str
    type: ConfigType
    required: bool = True
    default: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    enum_values: Optional[List[Any]] = None
    description: str = ""
    validator: Optional[Callable] = None


class ConfigSchema:
    """Схема конфигурации"""
    
    def __init__(self, name: str):
        self.name = name
        self.fields: Dict[str, ConfigField] = {}
        self.required_fields: List[str] = []
    
    def add_field(self, field: ConfigField) -> None:
        """Добавить поле в схему"""
        self.fields[field.name] = field
        if field.required:
            self.required_fields.append(field.name)
    
    def validate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидировать конфигурацию
        
        Args:
            config: Конфигурация для валидации
            
        Returns:
            Валидированная конфигурация с значениями по умолчанию
        """
        validated_config = {}
        errors = []
        warnings = []
        
        # Проверяем обязательные поля
        for field_name in self.required_fields:
            if field_name not in config:
                if self.fields[field_name].default is not None:
                    validated_config[field_name] = self.fields[field_name].default
                    warnings.append(f"Поле {field_name} отсутствует, используется значение по умолчанию")
                else:
                    errors.append(f"Обязательное поле {field_name} отсутствует")
        
        # Валидируем все поля
        for field_name, field in self.fields.items():
            if field_name in config:
                value = config[field_name]
                validated_value, field_errors = self._validate_field(field, value)
                
                if field_errors:
                    errors.extend(field_errors)
                else:
                    validated_config[field_name] = validated_value
            elif field.default is not None:
                validated_config[field_name] = field.default
        
        if errors:
            raise ValueError(f"Ошибки валидации конфигурации {self.name}: {errors}")
        
        if warnings:
            for warning in warnings:
                logger.warning(warning)
        
        return validated_config
    
    def _validate_field(self, field: ConfigField, value: Any) -> tuple[Any, List[str]]:
        """Валидировать отдельное поле"""
        errors = []
        
        try:
            # Проверяем тип
            if field.type == ConfigType.STRING:
                if not isinstance(value, str):
                    value = str(value)
                    logger.info(f"Преобразовано в строку: {field.name}")
                
                if field.pattern and not re.match(field.pattern, value):
                    errors.append(f"Поле {field.name} не соответствует паттерну {field.pattern}")
                
            elif field.type == ConfigType.INTEGER:
                if not isinstance(value, int):
                    try:
                        value = int(value)
                        logger.info(f"Преобразовано в целое число: {field.name}")
                    except (ValueError, TypeError):
                        errors.append(f"Поле {field.name} должно быть целым числом")
                
                if field.min_value is not None and value < field.min_value:
                    errors.append(f"Поле {field.name} меньше минимального значения {field.min_value}")
                
                if field.max_value is not None and value > field.max_value:
                    errors.append(f"Поле {field.name} больше максимального значения {field.max_value}")
                
            elif field.type == ConfigType.FLOAT:
                if not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                        logger.info(f"Преобразовано в число с плавающей точкой: {field.name}")
                    except (ValueError, TypeError):
                        errors.append(f"Поле {field.name} должно быть числом")
                
                if field.min_value is not None and value < field.min_value:
                    errors.append(f"Поле {field.name} меньше минимального значения {field.min_value}")
                
                if field.max_value is not None and value > field.max_value:
                    errors.append(f"Поле {field.name} больше максимального значения {field.max_value}")
                
            elif field.type == ConfigType.BOOLEAN:
                if isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                    logger.info(f"Преобразовано в булево значение: {field.name}")
                elif not isinstance(value, bool):
                    errors.append(f"Поле {field.name} должно быть булевым значением")
                
            elif field.type == ConfigType.ARRAY:
                if not isinstance(value, list):
                    errors.append(f"Поле {field.name} должно быть массивом")
                
            elif field.type == ConfigType.OBJECT:
                if not isinstance(value, dict):
                    errors.append(f"Поле {field.name} должно быть объектом")
                
            elif field.type == ConfigType.ENUM:
                if field.enum_values and value not in field.enum_values:
                    errors.append(f"Поле {field.name} должно быть одним из: {field.enum_values}")
            
            # Проверяем кастомный валидатор
            if field.validator:
                try:
                    field.validator(value)
                except Exception as e:
                    errors.append(f"Ошибка валидации поля {field.name}: {e}")
            
        except Exception as e:
            errors.append(f"Ошибка валидации поля {field.name}: {e}")
        
        return value, errors


class ConfigValidator:
    """Валидатор конфигурации"""
    
    def __init__(self):
        self.schemas: Dict[str, ConfigSchema] = {}
        self._load_default_schemas()
    
    def _load_default_schemas(self) -> None:
        """Загрузить схемы по умолчанию"""
        
        # Схема игровых настроек
        game_schema = ConfigSchema("game")
        game_schema.add_field(ConfigField(
            name="window_width",
            type=ConfigType.INTEGER,
            required=True,
            default=1280,
            min_value=800,
            max_value=3840,
            description="Ширина окна игры"
        ))
        game_schema.add_field(ConfigField(
            name="window_height",
            type=ConfigType.INTEGER,
            required=True,
            default=720,
            min_value=600,
            max_value=2160,
            description="Высота окна игры"
        ))
        game_schema.add_field(ConfigField(
            name="fullscreen",
            type=ConfigType.BOOLEAN,
            required=False,
            default=False,
            description="Полноэкранный режим"
        ))
        game_schema.add_field(ConfigField(
            name="target_fps",
            type=ConfigType.INTEGER,
            required=False,
            default=60,
            min_value=30,
            max_value=240,
            description="Целевой FPS"
        ))
        game_schema.add_field(ConfigField(
            name="vsync",
            type=ConfigType.BOOLEAN,
            required=False,
            default=True,
            description="Вертикальная синхронизация"
        ))
        game_schema.add_field(ConfigField(
            name="sound_volume",
            type=ConfigType.FLOAT,
            required=False,
            default=0.7,
            min_value=0.0,
            max_value=1.0,
            description="Громкость звука"
        ))
        game_schema.add_field(ConfigField(
            name="music_volume",
            type=ConfigType.FLOAT,
            required=False,
            default=0.5,
            min_value=0.0,
            max_value=1.0,
            description="Громкость музыки"
        ))
        
        self.schemas["game"] = game_schema
        
        # Схема настроек AI
        ai_schema = ConfigSchema("ai")
        ai_schema.add_field(ConfigField(
            name="difficulty",
            type=ConfigType.ENUM,
            required=False,
            default="normal",
            enum_values=["easy", "normal", "hard", "expert"],
            description="Сложность ИИ"
        ))
        ai_schema.add_field(ConfigField(
            name="learning_enabled",
            type=ConfigType.BOOLEAN,
            required=False,
            default=True,
            description="Включить обучение ИИ"
        ))
        ai_schema.add_field(ConfigField(
            name="max_entities",
            type=ConfigType.INTEGER,
            required=False,
            default=100,
            min_value=10,
            max_value=1000,
            description="Максимальное количество сущностей"
        ))
        
        self.schemas["ai"] = ai_schema
        
        # Схема настроек UI
        ui_schema = ConfigSchema("ui")
        ui_schema.add_field(ConfigField(
            name="theme",
            type=ConfigType.ENUM,
            required=False,
            default="default",
            enum_values=["default", "dark", "light", "colorful"],
            description="Тема интерфейса"
        ))
        ui_schema.add_field(ConfigField(
            name="show_fps",
            type=ConfigType.BOOLEAN,
            required=False,
            default=False,
            description="Показывать FPS"
        ))
        ui_schema.add_field(ConfigField(
            name="show_debug",
            type=ConfigType.BOOLEAN,
            required=False,
            default=False,
            description="Показывать отладочную информацию"
        ))
        
        self.schemas["ui"] = ui_schema
    
    def add_schema(self, schema: ConfigSchema) -> None:
        """Добавить схему"""
        self.schemas[schema.name] = schema
        logger.info(f"Добавлена схема конфигурации: {schema.name}")
    
    def validate_config(self, config: Dict[str, Any]) -> 'ValidationResult':
        """
        Валидировать конфигурацию (универсальный метод)
        
        Args:
            config: Конфигурация для валидации
            
        Returns:
            Результат валидации
        """
        errors = []
        warnings = []
        is_valid = True
        
        # Проверяем основные поля
        if "game" in config:
            game_config = config["game"]
            if "display" in game_config:
                display = game_config["display"]
                
                # Проверяем window_width
                if "window_width" in display:
                    width = display["window_width"]
                    if not isinstance(width, int) or width <= 0:
                        errors.append("window_width должен быть положительным целым числом")
                        is_valid = False
                
                # Проверяем window_height
                if "window_height" in display:
                    height = display["window_height"]
                    if not isinstance(height, int) or height <= 0:
                        errors.append("window_height должен быть положительным целым числом")
                        is_valid = False
        
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    def validate_config_by_name(self, config_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидировать конфигурацию
        
        Args:
            config_name: Имя конфигурации
            config: Конфигурация для валидации
            
        Returns:
            Валидированная конфигурация
        """
        if config_name not in self.schemas:
            logger.warning(f"Схема для конфигурации {config_name} не найдена")
            return config
        
        try:
            schema = self.schemas[config_name]
            validated_config = schema.validate(config)
            logger.info(f"Конфигурация {config_name} валидирована успешно")
            return validated_config
            
        except Exception as e:
            logger.error(f"Ошибка валидации конфигурации {config_name}: {e}")
            raise
    
    def validate_file(self, config_name: str, file_path: Path) -> Dict[str, Any]:
        """
        Валидировать конфигурационный файл
        
        Args:
            config_name: Имя конфигурации
            file_path: Путь к файлу
            
        Returns:
            Валидированная конфигурация
        """
        try:
            if not file_path.exists():
                logger.warning(f"Файл конфигурации не найден: {file_path}")
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return self.validate_config(config_name, config)
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON в файле {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка валидации файла {file_path}: {e}")
            raise
    
    def create_default_config(self, config_name: str) -> Dict[str, Any]:
        """
        Создать конфигурацию по умолчанию
        
        Args:
            config_name: Имя конфигурации
            
        Returns:
            Конфигурация по умолчанию
        """
        if config_name not in self.schemas:
            logger.warning(f"Схема для конфигурации {config_name} не найдена")
            return {}
        
        schema = self.schemas[config_name]
        default_config = {}
        
        for field_name, field in schema.fields.items():
            if field.default is not None:
                default_config[field_name] = field.default
        
        return default_config
    
    def auto_correct_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Автоматическая коррекция конфигурации
        
        Args:
            config: Конфигурация для коррекции
            
        Returns:
            Исправленная конфигурация
        """
        corrected_config = config.copy()
        
        # Исправляем основные поля
        if "game" in corrected_config:
            game_config = corrected_config["game"]
            if "display" in game_config:
                display = game_config["display"]
                
                # Исправляем window_width
                if "window_width" in display:
                    width = display["window_width"]
                    if not isinstance(width, int) or width <= 0:
                        display["window_width"] = 1280  # Значение по умолчанию
                
                # Исправляем window_height
                if "window_height" in display:
                    height = display["window_height"]
                    if not isinstance(height, int) or height <= 0:
                        display["window_height"] = 720  # Значение по умолчанию
        
        return corrected_config
    
    def save_config(self, config_name: str, config: Dict[str, Any], file_path: Path) -> bool:
        """
        Сохранить конфигурацию в файл
        
        Args:
            config_name: Имя конфигурации
            config: Конфигурация
            file_path: Путь к файлу
            
        Returns:
            True если сохранение прошло успешно
        """
        try:
            # Валидируем перед сохранением
            validated_config = self.validate_config(config_name, config)
            
            # Создаем директорию если не существует
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(validated_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Конфигурация {config_name} сохранена в {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации {config_name}: {e}")
            return False
    
    def get_schema_info(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о схеме
        
        Args:
            config_name: Имя конфигурации
            
        Returns:
            Информация о схеме
        """
        if config_name not in self.schemas:
            return None
        
        schema = self.schemas[config_name]
        info = {
            'name': schema.name,
            'fields': {},
            'required_fields': schema.required_fields
        }
        
        for field_name, field in schema.fields.items():
            info['fields'][field_name] = {
                'type': field.type.value,
                'required': field.required,
                'default': field.default,
                'description': field.description,
                'min_value': field.min_value,
                'max_value': field.max_value,
                'pattern': field.pattern,
                'enum_values': field.enum_values
            }
        
        return info
    
    def list_schemas(self) -> List[str]:
        """Получить список доступных схем"""
        return list(self.schemas.keys())
    
    def validate_all_configs(self, config_dir: Path) -> Dict[str, Dict[str, Any]]:
        """
        Валидировать все конфигурационные файлы в директории
        
        Args:
            config_dir: Директория с конфигурациями
            
        Returns:
            Словарь валидированных конфигураций
        """
        validated_configs = {}
        
        if not config_dir.exists():
            logger.warning(f"Директория конфигураций не найдена: {config_dir}")
            return validated_configs
        
        for config_file in config_dir.glob("*.json"):
            config_name = config_file.stem
            
            try:
                validated_config = self.validate_file(config_name, config_file)
                validated_configs[config_name] = validated_config
                
            except Exception as e:
                logger.error(f"Ошибка валидации файла {config_file}: {e}")
                continue
        
        logger.info(f"Валидировано {len(validated_configs)} конфигураций")
        return validated_configs


# Глобальный экземпляр валидатора
config_validator = ConfigValidator()
