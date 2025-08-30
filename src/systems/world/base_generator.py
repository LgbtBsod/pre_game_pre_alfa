#!/usr/bin/env python3
"""Базовый класс для всех генераторов мира
Устраняет дублирование кода между генераторами"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = БАЗОВЫЕ ТИПЫ
class GeneratorType(Enum):
    """Типы генераторов"""
    HEIGHT_MAP = "height_map"
    STRUCTURE = "structure"
    DUNGEON = "dungeon"
    SETTLEMENT = "settlement"
    TOWER = "tower"
    WEATHER = "weather"
    TIME = "time"
    SEASON = "season"

class GenerationQuality(Enum):
    """Качество генерации"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

# = БАЗОВЫЕ НАСТРОЙКИ
@dataclass
class BaseGeneratorSettings:
    """Базовые настройки генератора"""
    generator_type: GeneratorType
    quality: GenerationQuality = GenerationQuality.MEDIUM
    seed: Optional[int] = None
    enable_caching: bool = True
    enable_multithreading: bool = True
    max_cache_size: int = 1000
    update_interval: float = 0.1

# = БАЗОВЫЙ ГЕНЕРАТОР
class BaseGenerator(BaseComponent):
    """Базовый класс для всех генераторов мира"""
    
    def __init__(self, generator_type: GeneratorType, component_id: str = None):
        super().__init__(
            component_id=component_id or f"{generator_type.value}_generator",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Базовые настройки
        self.generator_type = generator_type
        self.settings = BaseGeneratorSettings(generator_type=generator_type)
        
        # Генератор случайных чисел
        self.rng = random.Random()
        if self.settings.seed:
            self.rng.seed(self.settings.seed)
        
        # Кэш и статистика
        self.generation_cache: Dict[str, Any] = {}
        self.generation_stats = {
            "total_generations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "generation_time": 0.0,
            "last_generation": 0.0
        }
        
        # Callbacks
        self.generation_callbacks: List[callable] = []
        self.error_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация базового генератора"""
        try:
            # Инициализация кэша
            if self.settings.enable_caching:
                self._initialize_cache()
            
            # Инициализация генератора
            if not self._initialize_generator():
                return False
            
            self.logger.info(f"BaseGenerator {self.generator_type.value} инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации BaseGenerator: {e}")
            return False
    
    def _initialize_cache(self):
        """Инициализация кэша"""
        self.generation_cache.clear()
        self.logger.info("Кэш генератора инициализирован")
    
    def _initialize_generator(self) -> bool:
        """Инициализация конкретного генератора (переопределяется в наследниках)"""
        return True
    
    def generate(self, parameters: Dict[str, Any]) -> Optional[Any]:
        """Генерация контента с кэшированием"""
        try:
            start_time = time.time()
            
            # Создание ключа кэша
            cache_key = self._create_cache_key(parameters)
            
            # Проверка кэша
            if self.settings.enable_caching and cache_key in self.generation_cache:
                self.generation_stats["cache_hits"] += 1
                result = self.generation_cache[cache_key]
                self.logger.debug(f"Кэш-хит для {cache_key}")
                return result
            
            # Генерация нового контента
            self.generation_stats["cache_misses"] += 1
            result = self._generate_content(parameters)
            
            if result is not None:
                # Сохранение в кэш
                if self.settings.enable_caching:
                    self._add_to_cache(cache_key, result)
                
                # Обновление статистики
                generation_time = time.time() - start_time
                self.generation_stats["total_generations"] += 1
                self.generation_stats["generation_time"] += generation_time
                self.generation_stats["last_generation"] = time.time()
                
                # Уведомление о генерации
                self._notify_generation_completed(result, parameters)
                
                self.logger.debug(f"Сгенерирован контент за {generation_time:.3f}с")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации: {e}")
            self._notify_generation_error(e, parameters)
            return None
    
    def _create_cache_key(self, parameters: Dict[str, Any]) -> str:
        """Создание ключа кэша"""
        # Создание стабильного ключа на основе параметров
        key_parts = [f"{k}={v}" for k, v in sorted(parameters.items())]
        return f"{self.generator_type.value}:{':'.join(key_parts)}"
    
    def _generate_content(self, parameters: Dict[str, Any]) -> Optional[Any]:
        """Генерация контента (переопределяется в наследниках)"""
        raise NotImplementedError("Метод _generate_content должен быть переопределен")
    
    def _add_to_cache(self, key: str, content: Any):
        """Добавление в кэш"""
        if len(self.generation_cache) >= self.settings.max_cache_size:
            # Удаление старых записей
            oldest_key = min(self.generation_cache.keys(), 
                           key=lambda k: self.generation_cache[k].get('timestamp', 0))
            del self.generation_cache[oldest_key]
        
        self.generation_cache[key] = {
            'content': content,
            'timestamp': time.time()
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self.generation_cache.clear()
        self.logger.info("Кэш генератора очищен")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        return {
            "cache_size": len(self.generation_cache),
            "max_cache_size": self.settings.max_cache_size,
            "cache_hits": self.generation_stats["cache_hits"],
            "cache_misses": self.generation_stats["cache_misses"],
            "hit_rate": (self.generation_stats["cache_hits"] / 
                        max(1, self.generation_stats["cache_hits"] + self.generation_stats["cache_misses"]))
        }
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        return {
            "total_generations": self.generation_stats["total_generations"],
            "average_generation_time": (self.generation_stats["generation_time"] / 
                                      max(1, self.generation_stats["total_generations"])),
            "last_generation": self.generation_stats["last_generation"],
            "generator_type": self.generator_type.value,
            "quality": self.settings.quality.value
        }
    
    def add_generation_callback(self, callback: callable):
        """Добавление callback для завершения генерации"""
        self.generation_callbacks.append(callback)
    
    def add_error_callback(self, callback: callable):
        """Добавление callback для ошибок"""
        self.error_callbacks.append(callback)
    
    def _notify_generation_completed(self, result: Any, parameters: Dict[str, Any]):
        """Уведомление о завершении генерации"""
        for callback in self.generation_callbacks:
            try:
                callback(result, parameters)
            except Exception as e:
                self.logger.error(f"Ошибка в callback генерации: {e}")
    
    def _notify_generation_error(self, error: Exception, parameters: Dict[str, Any]):
        """Уведомление об ошибке генерации"""
        for callback in self.error_callbacks:
            try:
                callback(error, parameters)
            except Exception as e:
                self.logger.error(f"Ошибка в callback ошибки: {e}")
    
    def set_seed(self, seed: int):
        """Установка сида для генератора"""
        self.settings.seed = seed
        self.rng.seed(seed)
        self.logger.info(f"Установлен сид генератора: {seed}")
    
    def _on_destroy(self):
        """Уничтожение базового генератора"""
        self.generation_cache.clear()
        self.generation_callbacks.clear()
        self.error_callbacks.clear()
        
        self.logger.info(f"BaseGenerator {self.generator_type.value} уничтожен")
