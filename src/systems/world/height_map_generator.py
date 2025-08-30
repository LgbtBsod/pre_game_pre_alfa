#!/usr/bin/env python3
"""Генератор высот для процедурного мира
Использует шум Перлина для создания естественного ландшафта"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import math
import random
import time
import numpy as np

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ И ПЕРЕЧИСЛЕНИЯ
class TerrainType(Enum):
    """Типы местности"""
    WATER = "water"           # Вода
    BEACH = "beach"           # Пляж
    GRASSLAND = "grassland"   # Равнина
    FOREST = "forest"         # Лес
    HILLS = "hills"           # Холмы
    MOUNTAINS = "mountains"   # Горы
    SNOW = "snow"             # Снег
    DESERT = "desert"         # Пустыня

class NoiseType(Enum):
    """Типы шума для генерации"""
    PERLIN = "perlin"         # Шум Перлина
    SIMPLEX = "simplex"       # Симплекс шум
    CELLULAR = "cellular"     # Клеточный шум
    FRACTAL = "fractal"       # Фрактальный шум

# = ДАТАКЛАССЫ ДЛЯ НАСТРОЕК
@dataclass
class HeightMapSettings:
    """Настройки генерации высот"""
    width: int = 1024
    height: int = 1024
    scale: float = 50.0
    octaves: int = 6
    persistence: float = 0.5
    lacunarity: float = 2.0
    base_height: float = 0.0
    max_height: float = 1000.0
    min_height: float = -100.0
    sea_level: float = 0.0
    mountain_threshold: float = 0.7
    hill_threshold: float = 0.4
    beach_width: float = 0.05

@dataclass
class BiomeSettings:
    """Настройки биомов"""
    temperature_range: Tuple[float, float] = (-30.0, 50.0)
    humidity_range: Tuple[float, float] = (0.0, 1.0)
    elevation_influence: float = 0.3
    temperature_influence: float = 0.4
    humidity_influence: float = 0.3

@dataclass
class ErosionSettings:
    """Настройки эрозии"""
    enabled: bool = True
    iterations: int = 1000
    erosion_rate: float = 0.1
    deposition_rate: float = 0.1
    evaporation_rate: float = 0.01
    gravity: float = 9.81

# = ОСНОВНАЯ СИСТЕМА ГЕНЕРАЦИИ ВЫСОТ
class HeightMapGenerator(BaseComponent):
    """Генератор высот для процедурного мира"""
    
    def __init__(self):
        super().__init__(
            component_id="HeightMapGenerator",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки генерации
        self.settings = HeightMapSettings()
        self.biome_settings = BiomeSettings()
        self.erosion_settings = ErosionSettings()
        
        # Кэш для сгенерированных данных
        self.height_cache: Dict[str, np.ndarray] = {}
        self.biome_cache: Dict[str, np.ndarray] = {}
        self.temperature_cache: Dict[str, np.ndarray] = {}
        self.humidity_cache: Dict[str, np.ndarray] = {}
        
        # Системные параметры
        self.seed = int(time.time())
        self.random_generator = random.Random(self.seed)
        
        # Статистика генерации
        self.generation_stats = {
            "total_chunks": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_time": 0.0
        }
    
    def _on_initialize(self) -> bool:
        """Инициализация генератора высот"""
        try:
            # Устанавливаем seed для воспроизводимости
            random.seed(self.seed)
            np.random.seed(self.seed)
            
            self._logger.info(f"Генератор высот инициализирован с seed: {self.seed}")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка инициализации генератора высот: {e}")
            return False
    
    def generate_height_map(self, chunk_x: int, chunk_y: int, 
                           chunk_size: int = 64) -> np.ndarray:
        """Генерация карты высот для чанка"""
        try:
            start_time = time.time()
            chunk_key = f"{chunk_x}_{chunk_y}_{chunk_size}"
            
            # Проверяем кэш
            if chunk_key in self.height_cache:
                self.generation_stats["cache_hits"] += 1
                return self.height_cache[chunk_key]
            
            self.generation_stats["cache_misses"] += 1
            
            # Создаем базовую карту высот
            height_map = self._create_base_height_map(chunk_x, chunk_y, chunk_size)
            
            # Применяем слои шума
            height_map = self._apply_noise_layers(height_map, chunk_x, chunk_y, chunk_size)
            
            # Применяем эрозию
            if self.erosion_settings.enabled:
                height_map = self._apply_erosion(height_map)
            
            # Нормализуем высоты
            height_map = self._normalize_heights(height_map)
            
            # Кэшируем результат
            self.height_cache[chunk_key] = height_map
            
            # Обновляем статистику
            generation_time = time.time() - start_time
            self.generation_stats["total_time"] += generation_time
            self.generation_stats["total_chunks"] += 1
            
            self._logger.debug(f"Сгенерирован чанк {chunk_x}, {chunk_y} за {generation_time:.3f}с")
            
            return height_map
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации карты высот для чанка {chunk_x}, {chunk_y}: {e}")
            # Возвращаем пустую карту в случае ошибки
            return np.zeros((chunk_size, chunk_size), dtype=np.float32)
    
    def _create_base_height_map(self, chunk_x: int, chunk_y: int, chunk_size: int) -> np.ndarray:
        """Создание базовой карты высот"""
        try:
            # Создаем координатную сетку
            x_coords = np.linspace(chunk_x * chunk_size, (chunk_x + 1) * chunk_size, chunk_size)
            y_coords = np.linspace(chunk_y * chunk_size, (chunk_y + 1) * chunk_size, chunk_size)
            X, Y = np.meshgrid(x_coords, y_coords)
            
            # Базовые высоты
            base_height = np.full((chunk_size, chunk_size), self.settings.base_height, dtype=np.float32)
            
            # Добавляем глобальный уклон (например, от севера к югу)
            global_slope = (Y - chunk_y * chunk_size) * 0.01
            base_height += global_slope
            
            return base_height
            
        except Exception as e:
            self._logger.error(f"Ошибка создания базовой карты высот: {e}")
            return np.zeros((chunk_size, chunk_size), dtype=np.float32)
    
    def _apply_noise_layers(self, height_map: np.ndarray, chunk_x: int, chunk_y: int, 
                           chunk_size: int) -> np.ndarray:
        """Применение слоев шума к карте высот"""
        try:
            result = height_map.copy()
            
            # Основной слой шума (крупные формы рельефа)
            main_noise = self._generate_perlin_noise(chunk_x, chunk_y, chunk_size, 
                                                   scale=self.settings.scale, octaves=1)
            result += main_noise * 200.0
            
            # Детализирующий слой (средние формы)
            detail_noise = self._generate_perlin_noise(chunk_x, chunk_y, chunk_size,
                                                     scale=self.settings.scale * 0.5, octaves=3)
            result += detail_noise * 100.0
            
            # Мелкие детали (каменистость)
            fine_noise = self._generate_perlin_noise(chunk_x, chunk_y, chunk_size,
                                                   scale=self.settings.scale * 0.25, octaves=6)
            result += fine_noise * 50.0
            
            # Фрактальный шум для естественности
            fractal_noise = self._generate_fractal_noise(chunk_x, chunk_y, chunk_size)
            result += fractal_noise * 75.0
            
            return result
            
        except Exception as e:
            self._logger.error(f"Ошибка применения слоев шума: {e}")
            return height_map
    
    def _generate_perlin_noise(self, chunk_x: int, chunk_y: int, chunk_size: int,
                              scale: float, octaves: int) -> np.ndarray:
        """Генерация шума Перлина"""
        try:
            # Создаем координатную сетку
            x_coords = np.linspace(chunk_x * chunk_size / scale, 
                                 (chunk_x + 1) * chunk_size / scale, chunk_size)
            y_coords = np.linspace(chunk_y * chunk_size / scale, 
                                 (chunk_y + 1) * chunk_size / scale, chunk_size)
            X, Y = np.meshgrid(x_coords, y_coords)
            
            # Генерируем шум Перлина
            noise = np.zeros((chunk_size, chunk_size))
            
            for i in range(octaves):
                frequency = self.settings.lacunarity ** i
                amplitude = self.settings.persistence ** i
                
                # Смешиваем координаты для разнообразия
                x_noise = X * frequency + self.random_generator.uniform(0, 1000)
                y_noise = Y * frequency + self.random_generator.uniform(0, 1000)
                
                # Простая реализация шума Перлина (для производительности)
                layer_noise = self._simple_perlin_noise(x_noise, y_noise)
                noise += layer_noise * amplitude
            
            return noise
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации шума Перлина: {e}")
            return np.zeros((chunk_size, chunk_size))
    
    def _simple_perlin_noise(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Упрощенная реализация шума Перлина"""
        try:
            # Интерполяция между случайными значениями
            x_int = x.astype(int)
            y_int = y.astype(int)
            
            # Получаем случайные значения для углов
            corners = np.zeros((x.shape[0], x.shape[1], 4))
            
            for i in range(x.shape[0]):
                for j in range(x.shape[1]):
                    # Генерируем детерминированные случайные значения
                    seed = hash((x_int[i, j], y_int[i, j])) % 1000000
                    random.seed(seed)
                    
                    corners[i, j, 0] = random.uniform(-1, 1)  # Левый верхний
                    corners[i, j, 1] = random.uniform(-1, 1)  # Правый верхний
                    corners[i, j, 2] = random.uniform(-1, 1)  # Левый нижний
                    corners[i, j, 3] = random.uniform(-1, 1)  # Правый нижний
            
            # Интерполяция
            x_frac = x - x_int
            y_frac = y - y_int
            
            # Функция сглаживания
            def smoothstep(t):
                return t * t * (3.0 - 2.0 * t)
            
            x_smooth = smoothstep(x_frac)
            y_smooth = smoothstep(y_frac)
            
            # Билинейная интерполяция
            noise = (corners[:, :, 0] * (1 - x_smooth) * (1 - y_smooth) +
                    corners[:, :, 1] * x_smooth * (1 - y_smooth) +
                    corners[:, :, 2] * (1 - x_smooth) * y_smooth +
                    corners[:, :, 3] * x_smooth * y_smooth)
            
            return noise
            
        except Exception as e:
            self._logger.error(f"Ошибка простого шума Перлина: {e}")
            return np.zeros_like(x)
    
    def _generate_fractal_noise(self, chunk_x: int, chunk_y: int, chunk_size: int) -> np.ndarray:
        """Генерация фрактального шума"""
        try:
            result = np.zeros((chunk_size, chunk_size))
            
            # Множественные слои с разными масштабами
            for i in range(4):
                scale = self.settings.scale * (0.5 ** i)
                amplitude = 50.0 * (0.7 ** i)
                
                layer = self._generate_perlin_noise(chunk_x, chunk_y, chunk_size, scale, 2)
                result += layer * amplitude
            
            return result
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации фрактального шума: {e}")
            return np.zeros((chunk_size, chunk_size))
    
    def _apply_erosion(self, height_map: np.ndarray) -> np.ndarray:
        """Применение эрозии к карте высот"""
        try:
            if not self.erosion_settings.enabled:
                return height_map
            
            result = height_map.copy()
            height, width = result.shape
            
            # Простая гидравлическая эрозия
            for iteration in range(self.erosion_settings.iterations):
                # Выбираем случайную точку
                x = self.random_generator.randint(0, width - 1)
                y = self.random_generator.randint(0, height - 1)
                
                if y < height - 1:  # Не на нижней границе
                    # Вычисляем градиент
                    current_height = result[y, x]
                    down_height = result[y + 1, x]
                    
                    if current_height > down_height:
                        # Переносим материал вниз
                        height_diff = current_height - down_height
                        transfer = min(height_diff * self.erosion_settings.erosion_rate, 
                                     height_diff * 0.5)
                        
                        result[y, x] -= transfer
                        result[y + 1, x] += transfer * self.erosion_settings.deposition_rate
                
                # Эвапорация
                if iteration % 100 == 0:
                    result *= (1.0 - self.erosion_settings.evaporation_rate)
            
            return result
            
        except Exception as e:
            self._logger.error(f"Ошибка применения эрозии: {e}")
            return height_map
    
    def _normalize_heights(self, height_map: np.ndarray) -> np.ndarray:
        """Нормализация высот в заданный диапазон"""
        try:
            # Ограничиваем высоты
            height_map = np.clip(height_map, 
                               self.settings.min_height, 
                               self.settings.max_height)
            
            # Нормализуем к диапазону [0, 1]
            normalized = (height_map - self.settings.min_height) / \
                        (self.settings.max_height - self.settings.min_height)
            
            # Преобразуем обратно к реальным высотам
            result = normalized * (self.settings.max_height - self.settings.min_height) + \
                    self.settings.min_height
            
            return result.astype(np.float32)
            
        except Exception as e:
            self._logger.error(f"Ошибка нормализации высот: {e}")
            return height_map
    
    def generate_biome_map(self, height_map: np.ndarray, chunk_x: int, chunk_y: int) -> np.ndarray:
        """Генерация карты биомов на основе высот"""
        try:
            chunk_key = f"biome_{chunk_x}_{chunk_y}"
            
            if chunk_key in self.biome_cache:
                return self.biome_cache[chunk_key]
            
            height, width = height_map.shape
            biome_map = np.zeros((height, width), dtype=np.int32)
            
            # Генерируем температуру и влажность
            temperature_map = self._generate_temperature_map(chunk_x, chunk_y, height, width)
            humidity_map = self._generate_humidity_map(chunk_x, chunk_y, height, width)
            
            # Определяем биомы для каждой точки
            for y in range(height):
                for x in range(width):
                    height_val = height_map[y, x]
                    temperature = temperature_map[y, x]
                    humidity = humidity_map[y, x]
                    
                    biome = self._determine_biome(height_val, temperature, humidity)
                    biome_map[y, x] = biome.value
            
            # Кэшируем результат
            self.biome_cache[chunk_key] = biome_map
            
            return biome_map
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации карты биомов: {e}")
            return np.zeros_like(height_map, dtype=np.int32)
    
    def _generate_temperature_map(self, chunk_x: int, chunk_y: int, height: int, width: int) -> np.ndarray:
        """Генерация карты температур"""
        try:
            chunk_key = f"temp_{chunk_x}_{chunk_y}"
            
            if chunk_key in self.temperature_cache:
                return self.temperature_cache[chunk_key]
            
            # Базовая температура зависит от широты (Y координата)
            base_temp = np.linspace(self.biome_settings.temperature_range[1],
                                  self.biome_settings.temperature_range[0], height)
            base_temp = np.tile(base_temp[:, np.newaxis], (1, width))
            
            # Добавляем случайные вариации
            noise = self._generate_perlin_noise(chunk_x, chunk_y, width, 
                                              scale=100.0, octaves=2)
            temperature_variation = noise * 10.0
            
            # Финальная температура
            temperature = base_temp + temperature_variation
            temperature = np.clip(temperature, 
                                self.biome_settings.temperature_range[0],
                                self.biome_settings.temperature_range[1])
            
            # Кэшируем результат
            self.temperature_cache[chunk_key] = temperature
            
            return temperature
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации карты температур: {e}")
            return np.full((height, width), 
                         (self.biome_settings.temperature_range[0] + 
                          self.biome_settings.temperature_range[1]) / 2)
    
    def _generate_humidity_map(self, chunk_x: int, chunk_y: int, height: int, width: int) -> np.ndarray:
        """Генерация карты влажности"""
        try:
            chunk_key = f"humidity_{chunk_x}_{chunk_y}"
            
            if chunk_key in self.humidity_cache:
                return self.humidity_cache[chunk_key]
            
            # Базовая влажность
            humidity = np.full((height, width), 0.5)
            
            # Добавляем случайные вариации
            noise = self._generate_perlin_noise(chunk_x, chunk_y, width,
                                              scale=80.0, octaves=3)
            humidity_variation = noise * 0.3
            
            # Финальная влажность
            humidity = humidity + humidity_variation
            humidity = np.clip(humidity, 0.0, 1.0)
            
            # Кэшируем результат
            self.humidity_cache[chunk_key] = humidity
            
            return humidity
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации карты влажности: {e}")
            return np.full((height, width), 0.5)
    
    def _determine_biome(self, height: float, temperature: float, humidity: float) -> TerrainType:
        """Определение биома на основе параметров"""
        try:
            # Нормализуем высоту
            normalized_height = (height - self.settings.min_height) / \
                              (self.settings.max_height - self.settings.min_height)
            
            # Определяем биом по высоте
            if normalized_height < self.settings.beach_width:
                return TerrainType.BEACH
            elif normalized_height < self.settings.hill_threshold:
                if humidity > 0.6:
                    return TerrainType.FOREST
                else:
                    return TerrainType.GRASSLAND
            elif normalized_height < self.settings.mountain_threshold:
                return TerrainType.HILLS
            else:
                if temperature < -10:
                    return TerrainType.SNOW
                else:
                    return TerrainType.MOUNTAINS
            
        except Exception as e:
            self._logger.error(f"Ошибка определения биома: {e}")
            return TerrainType.GRASSLAND
    
    def clear_cache(self) -> None:
        """Очистка кэша"""
        try:
            self.height_cache.clear()
            self.biome_cache.clear()
            self.temperature_cache.clear()
            self.humidity_cache.clear()
            
            self._logger.info("Кэш генератора высот очищен")
            
        except Exception as e:
            self._logger.error(f"Ошибка очистки кэша: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        try:
            cache_size = len(self.height_cache) + len(self.biome_cache) + \
                        len(self.temperature_cache) + len(self.humidity_cache)
            
            avg_time = (self.generation_stats["total_time"] / 
                       max(self.generation_stats["total_chunks"], 1))
            
            return {
                "total_chunks": self.generation_stats["total_chunks"],
                "cache_hits": self.generation_stats["cache_hits"],
                "cache_misses": self.generation_stats["cache_misses"],
                "cache_hit_rate": (self.generation_stats["cache_hits"] / 
                                 max(self.generation_stats["cache_hits"] + 
                                     self.generation_stats["cache_misses"], 1)),
                "total_time": self.generation_stats["total_time"],
                "average_time_per_chunk": avg_time,
                "cache_size": cache_size,
                "memory_usage_mb": cache_size * 64 * 64 * 4 / (1024 * 1024)  # Примерный размер в МБ
            }
            
        except Exception as e:
            self._logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def _on_destroy(self) -> bool:
        """Уничтожение генератора высот"""
        try:
            # Очищаем кэш
            self.clear_cache()
            
            # Сбрасываем статистику
            self.generation_stats = {
                "total_chunks": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "total_time": 0.0
            }
            
            self._logger.info("Генератор высот уничтожен")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка уничтожения генератора высот: {e}")
            return False
