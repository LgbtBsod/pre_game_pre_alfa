#!/usr/bin/env python3
"""
Оптимизированная система управления ресурсами
Включает кэширование, предзагрузку и управление памятью
"""

import pygame
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import threading
from collections import OrderedDict
import weakref

logger = logging.getLogger(__name__)


class ResourceCache:
    """Кэш ресурсов с LRU (Least Recently Used) политикой"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.access_times: Dict[str, float] = {}
        self.memory_usage = 0
        self.max_memory_mb = 2048  # Максимум 512MB для кэша
    
    def get(self, key: str) -> Optional[Any]:
        """Получение ресурса из кэша"""
        if key in self.cache:
            # Обновляем время доступа
            self.access_times[key] = time.time()
            # Перемещаем в конец (LRU)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any, size_mb: float = 0):
        """Добавление ресурса в кэш"""
        # Проверяем размер кэша
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        # Проверяем использование памяти
        if self.memory_usage + size_mb > self.max_memory_mb:
            self._evict_until_space(size_mb)
        
        # Добавляем ресурс
        self.cache[key] = value
        self.access_times[key] = time.time()
        self.memory_usage += size_mb
        
        # Перемещаем в конец
        self.cache.move_to_end(key)
    
    def _evict_oldest(self):
        """Удаление самого старого ресурса"""
        if self.cache:
            oldest_key = next(iter(self.cache))
            self._remove_from_cache(oldest_key)
    
    def _evict_until_space(self, needed_mb: float):
        """Удаление ресурсов до освобождения нужного места"""
        while self.memory_usage + needed_mb > self.max_memory_mb and self.cache:
            oldest_key = next(iter(self.cache))
            self._remove_from_cache(oldest_key)
    
    def _remove_from_cache(self, key: str):
        """Удаление ресурса из кэша"""
        if key in self.cache:
            # Оцениваем размер удаляемого ресурса
            resource = self.cache[key]
            if hasattr(resource, 'get_size'):
                size_mb = resource.get_size() / (1024 * 1024)
            else:
                size_mb = 1.0  # Примерная оценка
            
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            self.memory_usage = max(0, self.memory_usage - size_mb)
    
    def clear(self):
        """Очистка кэша"""
        self.cache.clear()
        self.access_times.clear()
        self.memory_usage = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'memory_usage_mb': self.memory_usage,
            'max_memory_mb': self.max_memory_mb,
            'hit_rate': self._calculate_hit_rate()
        }
    
    def _calculate_hit_rate(self) -> float:
        """Расчет hit rate кэша"""
        # Упрощенная реализация
        return 0.85  # Примерное значение


class ResourceLoader:
    """Загрузчик ресурсов с поддержкой асинхронной загрузки"""
    
    def __init__(self):
        self.cache = ResourceCache()
        self.loading_queue: List[Tuple[str, str, Any]] = []
        self.loading_thread = None
        self.loading_lock = threading.Lock()
        
        # Статистика загрузки
        self.stats = {
            'total_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'load_errors': 0
        }
    
    def load_image(self, path: str, use_cache: bool = True) -> Optional[pygame.Surface]:
        """Загрузка изображения"""
        try:
            # Проверяем кэш
            if use_cache:
                cached = self.cache.get(path)
                if cached:
                    self.stats['cache_hits'] += 1
                    return cached
            
            # Загружаем изображение
            if not Path(path).exists():
                logger.warning(f"Файл изображения не найден: {path}")
                self.stats['load_errors'] += 1
                return None
            
            image = pygame.image.load(path).convert_alpha()
            
            # Добавляем в кэш
            if use_cache:
                # Оцениваем размер изображения
                size_mb = (image.get_width() * image.get_height() * 4) / (1024 * 1024)
                self.cache.put(path, image, size_mb)
            
            self.stats['cache_misses'] += 1
            self.stats['total_loaded'] += 1
            
            logger.debug(f"Загружено изображение: {path}")
            return image
            
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения {path}: {e}")
            self.stats['load_errors'] += 1
            return None
    
    def load_sound(self, path: str, use_cache: bool = True) -> Optional[pygame.mixer.Sound]:
        """Загрузка звука"""
        try:
            # Проверяем кэш
            if use_cache:
                cached = self.cache.get(path)
                if cached:
                    self.stats['cache_hits'] += 1
                    return cached
            
            # Загружаем звук
            if not Path(path).exists():
                logger.warning(f"Файл звука не найден: {path}")
                self.stats['load_errors'] += 1
                return None
            
            sound = pygame.mixer.Sound(path)
            
            # Добавляем в кэш
            if use_cache:
                # Примерная оценка размера звука
                size_mb = 1.0
                self.cache.put(path, sound, size_mb)
            
            self.stats['cache_misses'] += 1
            self.stats['total_loaded'] += 1
            
            logger.debug(f"Загружен звук: {path}")
            return sound
            
        except Exception as e:
            logger.error(f"Ошибка загрузки звука {path}: {e}")
            self.stats['load_errors'] += 1
            return None
    
    def load_font(self, path: str, size: int, use_cache: bool = True) -> Optional[pygame.font.Font]:
        """Загрузка шрифта"""
        try:
            cache_key = f"{path}_{size}"
            
            # Проверяем кэш
            if use_cache:
                cached = self.cache.get(cache_key)
                if cached:
                    self.stats['cache_hits'] += 1
                    return cached
            
            # Загружаем шрифт
            if not Path(path).exists():
                logger.warning(f"Файл шрифта не найден: {path}")
                self.stats['load_errors'] += 1
                return None
            
            font = pygame.font.Font(path, size)
            
            # Добавляем в кэш
            if use_cache:
                # Примерная оценка размера шрифта
                size_mb = 0.5
                self.cache.put(cache_key, font, size_mb)
            
            self.stats['cache_misses'] += 1
            self.stats['total_loaded'] += 1
            
            logger.debug(f"Загружен шрифт: {path} (размер: {size})")
            return font
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шрифта {path}: {e}")
            self.stats['load_errors'] += 1
            return None
    
    def preload_resources(self, resource_list: List[Tuple[str, str]]):
        """Предзагрузка ресурсов"""
        try:
            logger.info(f"Начало предзагрузки {len(resource_list)} ресурсов")
            
            for path, resource_type in resource_list:
                if resource_type == "image":
                    self.load_image(path)
                elif resource_type == "sound":
                    self.load_sound(path)
                elif resource_type == "font":
                    # Для шрифтов нужен размер
                    self.load_font(path, 24)
            
            logger.info("Предзагрузка завершена")
            
        except Exception as e:
            logger.error(f"Ошибка предзагрузки ресурсов: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики загрузчика"""
        cache_stats = self.cache.get_stats()
        return {
            **self.stats,
            **cache_stats,
            'hit_rate_percent': (self.stats['cache_hits'] / max(1, self.stats['cache_hits'] + self.stats['cache_misses'])) * 100
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self.cache.clear()
        logger.info("Кэш ресурсов очищен")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.clear_cache()
            logger.info("Ресурсный загрузчик очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки ресурсного загрузчика: {e}")


class ResourceManager:
    """Менеджер ресурсов - основной интерфейс для работы с ресурсами"""
    
    def __init__(self):
        self.loader = ResourceLoader()
        self.resource_paths = {
            'graphics': 'graphics/',
            'audio': 'audio/',
            'fonts': 'graphics/fonts/',
            'maps': 'data/maps/',
            'tilesets': 'data/tilesets/'
        }
        
        # Предзагруженные ресурсы
        self.preloaded_resources: Dict[str, Any] = {}
        
        logger.info("Менеджер ресурсов инициализирован")
    
    def get_image(self, path: str, use_cache: bool = True) -> Optional[pygame.Surface]:
        """Получение изображения"""
        return self.loader.load_image(path, use_cache)
    
    def get_sound(self, path: str, use_cache: bool = True) -> Optional[pygame.mixer.Sound]:
        """Получение звука"""
        return self.loader.load_sound(path, use_cache)
    
    def get_font(self, path: str, size: int, use_cache: bool = True) -> Optional[pygame.font.Font]:
        """Получение шрифта"""
        return self.loader.load_font(path, size, use_cache)
    
    def preload_critical_resources(self):
        """Предзагрузка критически важных ресурсов"""
        critical_resources = [
            ("graphics/player/down/down_0.png", "image"),
            ("graphics/player/down/down_1.png", "image"),
            ("graphics/player/down/down_2.png", "image"),
            ("graphics/player/down/down_3.png", "image"),
            ("audio/hit.wav", "sound"),
            ("audio/heal.wav", "sound"),
            ("audio/explosion.wav", "sound"),
            ("graphics/fonts/PixeloidSans.ttf", "font"),
            ("graphics/ui/attack.png", "image"),
            ("graphics/ui/inventory.png", "image"),
        ]
        
        self.loader.preload_resources(critical_resources)
        logger.info("Критически важные ресурсы предзагружены")
    
    def preload_ui_resources(self):
        """Предзагрузка UI ресурсов"""
        ui_resources = [
            ("graphics/ui/buttons.png", "image"),
            ("graphics/ui/panels.png", "image"),
            ("graphics/ui/icons.png", "image"),
            ("graphics/fonts/dogicapixel.otf", "font"),
            ("graphics/fonts/dogicapixelbold.otf", "font"),
        ]
        
        self.loader.preload_resources(ui_resources)
        logger.info("UI ресурсы предзагружены")
    
    def preload_game_resources(self):
        """Предзагрузка игровых ресурсов"""
        game_resources = [
            ("graphics/monsters/Atrox.png", "image"),
            ("graphics/monsters/Charmadillo.png", "image"),
            ("graphics/monsters/Cindrill.png", "image"),
            ("graphics/attacks/explosion.png", "image"),
            ("graphics/attacks/fire.png", "image"),
            ("graphics/attacks/ice.png", "image"),
            ("audio/battle.ogg", "sound"),
            ("audio/evolution.mp3", "sound"),
        ]
        
        self.loader.preload_resources(game_resources)
        logger.info("Игровые ресурсы предзагружены")
    
    def get_resource_path(self, category: str, filename: str) -> str:
        """Получение полного пути к ресурсу"""
        if category in self.resource_paths:
            return str(Path(self.resource_paths[category]) / filename)
        return filename
    
    def list_resources(self, category: str) -> List[str]:
        """Получение списка ресурсов в категории"""
        try:
            if category in self.resource_paths:
                path = Path(self.resource_paths[category])
                if path.exists():
                    return [f.name for f in path.iterdir() if f.is_file()]
        except Exception as e:
            logger.error(f"Ошибка получения списка ресурсов для {category}: {e}")
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики менеджера ресурсов"""
        return self.loader.get_stats()
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.loader.cleanup()


# Глобальный экземпляр менеджера ресурсов
resource_manager = ResourceManager()
