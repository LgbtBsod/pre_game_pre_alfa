"""
Централизованный менеджер конфигурации игры.
Загружает все настройки из JSON файлов конфигурации
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)


class ConfigManager:
    """Централизованный менеджер конфигурации игры"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._lock = threading.RLock()
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._load_all_configs()
    
    def _load_all_configs(self) -> None:
        """Загружает все конфигурационные файлы"""
        config_files = {
            "game": "game_settings.json",
            "entities": "entities_config.json",
            "items": "items_config.json",
            "ai": "ai_config.json",
            "ui": "ui_config.json"
        }
        
        for config_name, filename in config_files.items():
            config_path = self.config_dir / filename
            try:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self._configs[config_name] = json.load(f)
                    logger.info(f"Конфигурация {config_name} загружена из {config_path}")
                else:
                    logger.warning(f"Файл конфигурации {config_path} не найден")
                    self._configs[config_name] = {}
            except Exception as e:
                logger.error(f"Ошибка загрузки конфигурации {config_name}: {e}")
                self._configs[config_name] = {}
    
    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """Получить значение из конфигурации по ключу"""
        with self._lock:
            config = self._configs.get(config_name, {})
            keys = key.split('.')
            value = config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
    
    def get_section(self, config_name: str, section: str) -> Dict[str, Any]:
        """Получить секцию конфигурации"""
        with self._lock:
            config = self._configs.get(config_name, {})
            return config.get(section, {})
    
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Получить всю конфигурацию по имени"""
        with self._lock:
            return self._configs.get(config_name, {}).copy()
    
    def set(self, config_name: str, key: str, value: Any) -> bool:
        """Установить значение в конфигурации"""
        with self._lock:
            if config_name not in self._configs:
                self._configs[config_name] = {}
            
            config = self._configs[config_name]
            keys = key.split('.')
            
            # Создаем вложенную структуру
            current = config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            
            # Сохраняем в файл
            return self._save_config(config_name)
    
    def set_section(self, config_name: str, section: str, values: Dict[str, Any]) -> bool:
        """Установить секцию конфигурации"""
        with self._lock:
            if config_name not in self._configs:
                self._configs[config_name] = {}
            
            self._configs[config_name][section] = values
            return self._save_config(config_name)
    
    def _save_config(self, config_name: str) -> bool:
        """Сохранить конфигурацию в файл"""
        try:
            config_files = {
                "game": "game_settings.json",
                "entities": "entities_config.json",
                "items": "items_config.json",
                "ai": "ai_config.json",
                "ui": "ui_config.json"
            }
            
            if config_name in config_files:
                config_path = self.config_dir / config_files[config_name]
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self._configs[config_name], f, indent=2, ensure_ascii=False)
                logger.info(f"Конфигурация {config_name} сохранена в {config_path}")
                return True
            else:
                logger.error(f"Неизвестная конфигурация: {config_name}")
                return False
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации {config_name}: {e}")
            return False
    
    def reload(self, config_name: Optional[str] = None) -> None:
        """Перезагрузить конфигурацию"""
        if config_name:
            self._load_single_config(config_name)
        else:
            self._load_all_configs()
        logger.info("Конфигурация перезагружена")
    
    def _load_single_config(self, config_name: str) -> None:
        """Загрузить одну конфигурацию по имени"""
        config_files = {
            "game": "game_settings.json",
            "entities": "entities_config.json",
            "items": "items_config.json",
            "ai": "ai_config.json",
            "ui": "ui_config.json"
        }
        
        if config_name in config_files:
            config_path = self.config_dir / config_files[config_name]
            try:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self._configs[config_name] = json.load(f)
                    logger.info(f"Конфигурация {config_name} перезагружена из {config_path}")
                else:
                    logger.warning(f"Файл конфигурации {config_path} не найден")
            except Exception as e:
                logger.error(f"Ошибка перезагрузки конфигурации {config_name}: {e}")
        else:
            logger.error(f"Неизвестная конфигурация: {config_name}")
    
    def reset_to_defaults(self, config_name: str) -> bool:
        """Сбросить конфигурацию к значениям по умолчанию"""
        # Здесь можно добавить логику для сброса к значениям по умолчанию
        logger.info(f"Сброс конфигурации {config_name} к значениям по умолчанию")
        return True
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Получить все конфигурации"""
        with self._lock:
            return {name: config.copy() for name, config in self._configs.items()}
    
    def has_config(self, config_name: str) -> bool:
        """Проверить наличие конфигурации"""
        return config_name in self._configs
    
    def has_key(self, config_name: str, key: str) -> bool:
        """Проверить наличие ключа в конфигурации"""
        with self._lock:
            config = self._configs.get(config_name, {})
            keys = key.split('.')
            value = config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return False
            
            return True


# Создаем глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()
