#!/usr/bin/env python3
"""
Оптимизированная система управления ресурсами.
Включает кэширование, пулинг объектов и автоматическую очистку памяти.
"""

import os
import time
import threading
import weakref
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import OrderedDict
import logging
import pygame

logger = logging.getLogger(__name__)


class ResourceCache:
    """Кэш ресурсов с автоматической очисткой"""
    
    def __init__(self, max_size: int = 100, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl  # Time to live в секундах
        self._cache: OrderedDict = OrderedDict()
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Получить ресурс из кэша"""
        with self._lock:
            if key in self._cache:
                # Обновляем время доступа
                self._access_times[key] = time.time()
                # Перемещаем в конец (LRU)
                self._cache.move_to_end(key)
                return self._cache[key]
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Добавить ресурс в кэш"""
        with self._lock:
            # Удаляем старые записи если превышен лимит
            while len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            self._cache[key] = value
            self._access_times[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """Удалить самую старую запись"""
        if self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if oldest_key in self._access_times:
                del self._access_times[oldest_key]
    
    def cleanup_expired(self) -> int:
        """Очистить просроченные записи"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, access_time in self._access_times.items()
                if current_time - access_time > self.ttl
            ]
            
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
            
            return len(expired_keys)
    
    def clear(self) -> None:
        """Очистить весь кэш"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    def __len__(self) -> int:
        """Получить размер кэша"""
        with self._lock:
            return len(self._cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кэша"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'ttl': self.ttl,
                'oldest_access': min(self._access_times.values()) if self._access_times else 0
            }


class ObjectPool:
    """Пулинг объектов для оптимизации памяти"""
    
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self._pool: Dict[str, List[Any]] = {}
        self._lock = threading.RLock()
    
    def get(self, object_type: str, factory_func) -> Any:
        """Получить объект из пула или создать новый"""
        with self._lock:
            if object_type in self._pool and self._pool[object_type]:
                return self._pool[object_type].pop()
            else:
                return factory_func()
    
    def return_object(self, object_type: str, obj: Any) -> None:
        """Вернуть объект в пул"""
        with self._lock:
            if object_type not in self._pool:
                self._pool[object_type] = []
            
            if len(self._pool[object_type]) < self.max_size:
                # Сбрасываем состояние объекта
                if hasattr(obj, 'reset'):
                    obj.reset()
                self._pool[object_type].append(obj)
    
    def clear(self) -> None:
        """Очистить пул"""
        with self._lock:
            self._pool.clear()


class ResourceManager:
    """Оптимизированный менеджер ресурсов"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self._lock = threading.RLock()
        
        # Кэши для разных типов ресурсов
        self._image_cache = ResourceCache(max_size=50, ttl=600.0)  # 10 минут для изображений
        self._sound_cache = ResourceCache(max_size=30, ttl=300.0)  # 5 минут для звуков
        self._font_cache = ResourceCache(max_size=10, ttl=1800.0)  # 30 минут для шрифтов
        
        # Пулинг объектов
        self._object_pool = ObjectPool(max_size=100)
        
        # Статистика
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'resources_loaded': 0,
            'resources_unloaded': 0
        }
        
        # Автоматическая очистка
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Запуск потока автоматической очистки"""
        def cleanup_worker():
            while not self._stop_cleanup.wait(60):  # Каждую минуту
                try:
                    self._cleanup_expired_resources()
                except Exception as e:
                    logger.error(f"Ошибка автоматической очистки: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_expired_resources(self):
        """Очистка просроченных ресурсов"""
        image_expired = self._image_cache.cleanup_expired()
        sound_expired = self._sound_cache.cleanup_expired()
        font_expired = self._font_cache.cleanup_expired()
        
        if image_expired + sound_expired + font_expired > 0:
            logger.debug(f"Очищено ресурсов: {image_expired} изображений, {sound_expired} звуков, {font_expired} шрифтов")
    
    def get_resource(self, path: str, resource_type: str = "image") -> Optional[Any]:
        """
        Получить ресурс с кэшированием
        
        Args:
            path: Путь к ресурсу
            resource_type: Тип ресурса (image, sound, font)
            
        Returns:
            Загруженный ресурс или None
        """
        full_path = str(self.base_path / path)
        
        # Выбираем соответствующий кэш
        cache = self._get_cache_for_type(resource_type)
        
        # Проверяем кэш
        cached_resource = cache.get(full_path)
        if cached_resource:
            self._stats['cache_hits'] += 1
            return cached_resource
        
        self._stats['cache_misses'] += 1
        
        # Загружаем ресурс
        try:
            resource = self._load_resource(full_path, resource_type)
            if resource:
                cache.put(full_path, resource)
                self._stats['resources_loaded'] += 1
                logger.debug(f"Загружен ресурс: {path}")
                return resource
        except Exception as e:
            logger.error(f"Ошибка загрузки ресурса {path}: {e}")
        
        return None
    
    def _get_cache_for_type(self, resource_type: str) -> ResourceCache:
        """Получить кэш для типа ресурса"""
        if resource_type == "image":
            return self._image_cache
        elif resource_type == "sound":
            return self._sound_cache
        elif resource_type == "font":
            return self._font_cache
        else:
            return self._image_cache  # По умолчанию
    
    def _load_resource(self, full_path: str, resource_type: str) -> Optional[Any]:
        """Загрузить ресурс с диска"""
        if not os.path.exists(full_path):
            logger.warning(f"Файл не найден: {full_path}")
            return None
        
        try:
            if resource_type == "image":
                # Проверяем, инициализирован ли pygame.display
                if not pygame.display.get_init():
                    # Создаем временную поверхность для загрузки изображения
                    pygame.display.init()
                    temp_surface = pygame.Surface((1, 1))
                    pygame.display.quit()
                
                return pygame.image.load(full_path).convert_alpha()
            elif resource_type == "sound":
                return pygame.mixer.Sound(full_path)
            elif resource_type == "font":
                return pygame.font.Font(full_path, 16)  # Размер по умолчанию
            else:
                logger.warning(f"Неизвестный тип ресурса: {resource_type}")
                return None
        except Exception as e:
            logger.error(f"Ошибка загрузки {resource_type} из {full_path}: {e}")
            return None
    
    def preload_resources(self, resources: List[Tuple[str, str]]) -> None:
        """
        Предзагрузка ресурсов
        
        Args:
            resources: Список кортежей (путь, тип_ресурса)
        """
        logger.info(f"Начинаем предзагрузку {len(resources)} ресурсов...")
        
        for path, resource_type in resources:
            self.get_resource(path, resource_type)
        
        logger.info("Предзагрузка завершена")
    
    def unload_resource(self, path: str, resource_type: str = "image") -> bool:
        """
        Выгрузить ресурс из кэша
        
        Args:
            path: Путь к ресурсу
            resource_type: Тип ресурса
            
        Returns:
            True если ресурс был выгружен
        """
        full_path = str(self.base_path / path)
        cache = self._get_cache_for_type(resource_type)
        
        with self._lock:
            if full_path in cache._cache:
                del cache._cache[full_path]
                if full_path in cache._access_times:
                    del cache._access_times[full_path]
                self._stats['resources_unloaded'] += 1
                logger.debug(f"Выгружен ресурс: {path}")
                return True
        
        return False
    
    def get_object_from_pool(self, object_type: str, factory_func) -> Any:
        """Получить объект из пула"""
        return self._object_pool.get(object_type, factory_func)
    
    def return_object_to_pool(self, object_type: str, obj: Any) -> None:
        """Вернуть объект в пул"""
        self._object_pool.return_object(object_type, obj)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику менеджера ресурсов (для совместимости)"""
        return self.get_stats()
    
    def clear_cache(self) -> None:
        """Очистить кэш (для совместимости)"""
        self.clear_all_caches()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику менеджера ресурсов"""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'image_cache': self._image_cache.get_stats(),
                'sound_cache': self._sound_cache.get_stats(),
                'font_cache': self._font_cache.get_stats(),
                'object_pool_size': len(self._object_pool._pool)
            })
            return stats
    
    def clear_all_caches(self) -> None:
        """Очистить все кэши"""
        with self._lock:
            self._image_cache.clear()
            self._sound_cache.clear()
            self._font_cache.clear()
            self._object_pool.clear()
            logger.info("Все кэши очищены")
    
    def optimize_memory(self) -> Dict[str, int]:
        """Оптимизация использования памяти"""
        with self._lock:
            # Очищаем просроченные ресурсы
            image_expired = self._image_cache.cleanup_expired()
            sound_expired = self._sound_cache.cleanup_expired()
            font_expired = self._font_cache.cleanup_expired()
            
            total_expired = image_expired + sound_expired + font_expired
            
            if total_expired > 0:
                logger.info(f"Оптимизация памяти: очищено {total_expired} ресурсов")
            
            return {
                'images_cleared': image_expired,
                'sounds_cleared': sound_expired,
                'fonts_cleared': font_expired,
                'total_cleared': total_expired
            }
    
    def shutdown(self) -> None:
        """Завершение работы менеджера ресурсов"""
        logger.info("Завершение работы ResourceManager...")
        
        # Останавливаем поток очистки
        self._stop_cleanup.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        
        # Очищаем все ресурсы
        self.clear_all_caches()
        
        logger.info("ResourceManager завершен")
    
    def __del__(self):
        """Деструктор"""
        self.shutdown()


# Глобальный экземпляр менеджера ресурсов
resource_manager = ResourceManager()
