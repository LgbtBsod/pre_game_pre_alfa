#!/usr/bin/env python3
"""
Resource Manager - Менеджер ресурсов
Отвечает только за загрузку, кэширование и управление игровыми ресурсами
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import pygame

logger = logging.getLogger(__name__)

class ResourceManager:
    """Менеджер ресурсов игры"""
    
    def __init__(self, assets_dir: Optional[Path] = None):
        self.assets_dir = assets_dir or Path("assets")
        
        # Кэши ресурсов
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music: Dict[str, str] = {}  # Пути к музыкальным файлам
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.data: Dict[str, Any] = {}
        
        # Статистика
        self.total_resources = 0
        self.loaded_resources = 0
        
        # Настройки
        self.enable_caching = True
        self.max_cache_size = 1000  # Максимальное количество ресурсов в кэше
        
        logger.info("Менеджер ресурсов инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация менеджера ресурсов"""
        try:
            logger.info("Инициализация менеджера ресурсов...")
            
            # Создание директорий ресурсов
            self._create_asset_directories()
            
            # Сканирование доступных ресурсов
            self._scan_assets()
            
            # Предзагрузка критических ресурсов
            self._preload_critical_resources()
            
            logger.info("Менеджер ресурсов успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера ресурсов: {e}")
            return False
    
    def _create_asset_directories(self):
        """Создание директорий для ресурсов"""
        directories = [
            "graphics",
            "audio",
            "data",
            "maps",
            "fonts"
        ]
        
        for directory in directories:
            dir_path = self.assets_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Создана директория: {directory}")
    
    def _scan_assets(self):
        """Сканирование доступных ресурсов"""
        try:
            # Сканируем графику
            graphics_dir = self.assets_dir / "graphics"
            if graphics_dir.exists():
                self._scan_directory(graphics_dir, "images")
            
            # Сканируем аудио
            audio_dir = self.assets_dir / "audio"
            if audio_dir.exists():
                self._scan_directory(audio_dir, "sounds")
            
            # Сканируем данные
            data_dir = self.assets_dir / "data"
            if data_dir.exists():
                self._scan_directory(data_dir, "data")
            
            logger.info(f"Найдено ресурсов: {self.total_resources}")
            
        except Exception as e:
            logger.error(f"Ошибка сканирования ресурсов: {e}")
    
    def _scan_directory(self, directory: Path, resource_type: str):
        """Сканирование директории на предмет ресурсов"""
        extensions = {
            "images": [".png", ".jpg", ".jpeg", ".bmp", ".gif"],
            "sounds": [".wav", ".ogg", ".mp3"],
            "data": [".json", ".xml", ".txt", ".csv"]
        }
        
        if resource_type not in extensions:
            return
        
        valid_extensions = extensions[resource_type]
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in valid_extensions:
                self.total_resources += 1
                logger.debug(f"Найден ресурс: {file_path}")
    
    def _preload_critical_resources(self):
        """Предзагрузка критически важных ресурсов"""
        critical_resources = [
            ("graphics/ui/button.png", "images"),
            ("graphics/ui/background.png", "images"),
            ("audio/ui/click.wav", "sounds"),
            ("fonts/main.ttf", "fonts")
        ]
        
        for resource_path, resource_type in critical_resources:
            try:
                if resource_type == "images":
                    self.load_image(resource_path)
                elif resource_type == "sounds":
                    self.load_sound(resource_path)
                elif resource_type == "fonts":
                    self.load_font(resource_path)
            except Exception as e:
                logger.warning(f"Не удалось предзагрузить {resource_path}: {e}")
    
    def load_image(self, path: str, scale: float = 1.0) -> Optional[pygame.Surface]:
        """Загрузка изображения"""
        try:
            # Проверяем кэш
            cache_key = f"{path}_{scale}"
            if cache_key in self.images:
                logger.debug(f"Изображение {path} загружено из кэша")
                return self.images[cache_key]
            
            # Загружаем изображение
            full_path = self.assets_dir / path
            if not full_path.exists():
                logger.warning(f"Файл изображения не найден: {full_path}")
                return None
            
            image = pygame.image.load(str(full_path)).convert_alpha()
            
            # Масштабирование
            if scale != 1.0:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)
            
            # Кэширование
            if self.enable_caching:
                self._add_to_cache("images", cache_key, image)
            
            self.loaded_resources += 1
            logger.debug(f"Изображение {path} загружено")
            return image
            
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения {path}: {e}")
            return None
    
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """Загрузка звука"""
        try:
            # Проверяем кэш
            if path in self.sounds:
                logger.debug(f"Звук {path} загружен из кэша")
                return self.sounds[path]
            
            # Загружаем звук
            full_path = self.assets_dir / path
            if not full_path.exists():
                logger.warning(f"Файл звука не найден: {full_path}")
                return None
            
            sound = pygame.mixer.Sound(str(full_path))
            
            # Кэширование
            if self.enable_caching:
                self._add_to_cache("sounds", path, sound)
            
            self.loaded_resources += 1
            logger.debug(f"Звук {path} загружен")
            return sound
            
        except Exception as e:
            logger.error(f"Ошибка загрузки звука {path}: {e}")
            return None
    
    def load_font(self, path: str, size: int = 24) -> Optional[pygame.font.Font]:
        """Загрузка шрифта"""
        try:
            # Проверяем кэш
            cache_key = f"{path}_{size}"
            if cache_key in self.fonts:
                logger.debug(f"Шрифт {path} загружен из кэша")
                return self.fonts[cache_key]
            
            # Загружаем шрифт
            full_path = self.assets_dir / path
            if not full_path.exists():
                logger.warning(f"Файл шрифта не найден: {full_path}")
                return None
            
            font = pygame.font.Font(str(full_path), size)
            
            # Кэширование
            if self.enable_caching:
                self._add_to_cache("fonts", cache_key, font)
            
            self.loaded_resources += 1
            logger.debug(f"Шрифт {path} загружен")
            return font
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шрифта {path}: {e}")
            return None
    
    def load_data(self, path: str) -> Optional[Any]:
        """Загрузка данных"""
        try:
            # Проверяем кэш
            if path in self.data:
                logger.debug(f"Данные {path} загружены из кэша")
                return self.data[path]
            
            # Загружаем данные
            full_path = self.assets_dir / path
            if not full_path.exists():
                logger.warning(f"Файл данных не найден: {full_path}")
                return None
            
            # Определяем тип файла и загружаем соответственно
            if path.endswith('.json'):
                import json
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif path.endswith('.xml'):
                import xml.etree.ElementTree as ET
                tree = ET.parse(full_path)
                data = tree.getroot()
            else:
                # Текстовый файл
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = f.read()
            
            # Кэширование
            if self.enable_caching:
                self._add_to_cache("data", path, data)
            
            self.loaded_resources += 1
            logger.debug(f"Данные {path} загружены")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных {path}: {e}")
            return None
    
    def _add_to_cache(self, cache_type: str, key: str, resource: Any):
        """Добавление ресурса в кэш"""
        cache = getattr(self, cache_type)
        
        # Проверка размера кэша
        if len(cache) >= self.max_cache_size:
            self._cleanup_cache(cache_type)
        
        cache[key] = resource
        logger.debug(f"Ресурс {key} добавлен в кэш {cache_type}")
    
    def _cleanup_cache(self, cache_type: str):
        """Очистка кэша"""
        cache = getattr(self, cache_type)
        
        # Удаляем 20% самых старых ресурсов
        items_to_remove = len(cache) // 5
        keys_to_remove = list(cache.keys())[:items_to_remove]
        
        for key in keys_to_remove:
            del cache[key]
        
        logger.debug(f"Кэш {cache_type} очищен, удалено {items_to_remove} ресурсов")
    
    def unload_resource(self, resource_type: str, key: str):
        """Выгрузка ресурса из памяти"""
        try:
            cache = getattr(self, resource_type)
            if key in cache:
                del cache[key]
                self.loaded_resources -= 1
                logger.debug(f"Ресурс {key} выгружен из {resource_type}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка выгрузки ресурса {key}: {e}")
            return False
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """Очистка кэша"""
        if cache_type is None:
            # Очищаем все кэши
            self.images.clear()
            self.sounds.clear()
            self.fonts.clear()
            self.data.clear()
            logger.info("Все кэши очищены")
        else:
            # Очищаем конкретный кэш
            cache = getattr(self, cache_type)
            cache.clear()
            logger.info(f"Кэш {cache_type} очищен")
    
    def get_resource_info(self) -> Dict[str, Any]:
        """Получение информации о ресурсах"""
        return {
            'total_resources': self.total_resources,
            'loaded_resources': self.loaded_resources,
            'cache_sizes': {
                'images': len(self.images),
                'sounds': len(self.sounds),
                'fonts': len(self.fonts),
                'data': len(self.data)
            },
            'cache_enabled': self.enable_caching,
            'max_cache_size': self.max_cache_size
        }
    
    def cleanup(self):
        """Очистка всех ресурсов"""
        logger.info("Очистка менеджера ресурсов...")
        
        # Очищаем все кэши
        self.clear_cache()
        
        # Сбрасываем счетчики
        self.total_resources = 0
        self.loaded_resources = 0
        
        logger.info("Менеджер ресурсов очищен")
