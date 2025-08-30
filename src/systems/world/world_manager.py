#!/usr/bin/env python3
"""Менеджер мира - главная система управления процедурно генерируемым миром
Координирует генерацию ландшафта, структур, биомов и экологических систем"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import time
import math
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.architecture import BaseComponent, ComponentType, Priority
from src.systems.world.height_map_generator import HeightMapGenerator
from src.systems.world.structure_generator import StructureGenerator

# = ТИПЫ МИРА
class WorldType(Enum):
    """Типы мира"""
    CONTINENTAL = "continental"   # Континентальный
    ISLAND = "island"            # Островной
    UNDERGROUND = "underground"  # Подземный
    FLOATING = "floating"        # Плавающий
    HYBRID = "hybrid"            # Гибридный

class ChunkState(Enum):
    """Состояния чанка"""
    UNLOADED = "unloaded"        # Не загружен
    LOADING = "loading"          # Загружается
    LOADED = "loaded"            # Загружен
    ACTIVE = "active"            # Активен
    UNLOADING = "unloading"      # Выгружается

# = ДАТАКЛАССЫ
@dataclass
class WorldSettings:
    """Настройки мира"""
    world_type: WorldType = WorldType.CONTINENTAL
    world_seed: int = 0
    chunk_size: int = 64
    max_chunks_loaded: int = 25
    view_distance: int = 3
    generation_threads: int = 4
    auto_save_interval: float = 300.0  # 5 минут
    max_chunk_generation_time: float = 5.0  # 5 секунд

@dataclass
class WorldChunk:
    """Чанк мира"""
    chunk_id: str
    chunk_x: int
    chunk_y: int
    chunk_size: int
    state: ChunkState = ChunkState.UNLOADED
    height_map: Optional[Any] = None
    biome_map: Optional[Any] = None
    structures: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    last_accessed: float = field(default_factory=time.time)
    generation_time: float = 0.0
    memory_usage: float = 0.0

@dataclass
class WorldStats:
    """Статистика мира"""
    total_chunks: int = 0
    loaded_chunks: int = 0
    active_chunks: int = 0
    total_structures: int = 0
    total_entities: int = 0
    memory_usage_mb: float = 0.0
    generation_time: float = 0.0
    last_update: float = field(default_factory=time.time)

# = ОСНОВНАЯ СИСТЕМА УПРАВЛЕНИЯ МИРОМ
class WorldManager(BaseComponent):
    """Главный менеджер мира"""
    
    def __init__(self):
        super().__init__(
            component_id="WorldManager",
            component_type=ComponentType.MANAGER,
            priority=Priority.CRITICAL
        )
        
        # Настройки мира
        self.settings = WorldSettings()
        self.world_stats = WorldStats()
        
        # Подсистемы мира
        self.height_generator: Optional[HeightMapGenerator] = None
        self.structure_generator: Optional[StructureGenerator] = None
        
        # Управление чанками
        self.chunks: Dict[str, WorldChunk] = {}
        self.chunk_load_queue: List[str] = []
        self.chunk_unload_queue: List[str] = []
        
        # Многопоточность
        self.executor: Optional[ThreadPoolExecutor] = None
        self.generation_lock = threading.Lock()
        
        # Кэш и оптимизация
        self.chunk_cache: Dict[str, Any] = {}
        self.spatial_index: Dict[Tuple[int, int], str] = {}  # (x, y) -> chunk_id
        
        # События и колбэки
        self.chunk_loaded_callbacks: List[Callable] = []
        self.chunk_unloaded_callbacks: List[Callable] = []
        self.world_updated_callbacks: List[Callable] = []
        
        # Автосохранение
        self.last_save_time = time.time()
        self.auto_save_enabled = True
    
    def _on_initialize(self) -> bool:
"""Инициализация менеджера мира"""
        try:
            # Инициализируем подсистемы
            self.height_generator = HeightMapGenerator()
            self.structure_generator = StructureGenerator()
            
            if not self.height_generator.initialize():
                self._logger.error("Не удалось инициализировать генератор высот")
                return False
            
            if not self.structure_generator.initialize():
                self._logger.error("Не удалось инициализировать генератор структур")
                return False
            
            # Инициализируем многопоточность
            self.executor = ThreadPoolExecutor(max_workers=self.settings.generation_threads)
            
            # Устанавливаем seed мира
            if self.settings.world_seed == 0:
                self.settings.world_seed = int(time.time())
            
            self._logger.info(f"Менеджер мира инициализирован с seed: {self.settings.world_seed}")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка инициализации менеджера мира: {e}")
            return False
    
    def load_chunk(self, chunk_x: int, chunk_y: int, priority: bool = False) -> Optional[WorldChunk]:
        """Загрузка чанка мира"""
        try:
            chunk_id = f"{chunk_x}_{chunk_y}"
            
            # Проверяем, не загружен ли уже чанк
            if chunk_id in self.chunks:
                chunk = self.chunks[chunk_id]
                chunk.last_accessed = time.time()
                
                if chunk.state == ChunkState.LOADED:
                    chunk.state = ChunkState.ACTIVE
                    return chunk
                elif chunk.state == ChunkState.LOADING:
                    return None  # Чанк уже загружается
            
            # Проверяем лимит загруженных чанков
            if len([c for c in self.chunks.values() if c.state in [ChunkState.LOADED, ChunkState.ACTIVE]]) >= self.settings.max_chunks_loaded:
                self._unload_oldest_chunks()
            
            # Создаем новый чанк
            chunk = WorldChunk(
                chunk_id=chunk_id,
                chunk_x=chunk_x,
                chunk_y=chunk_y,
                chunk_size=self.settings.chunk_size,
                state=ChunkState.LOADING
            )
            
            self.chunks[chunk_id] = chunk
            self.spatial_index[(chunk_x, chunk_y)] = chunk_id
            
            # Добавляем в очередь загрузки
            if priority:
                self.chunk_load_queue.insert(0, chunk_id)
            else:
                self.chunk_load_queue.append(chunk_id)
            
            # Запускаем асинхронную загрузку
            self._load_chunk_async(chunk_id)
            
            return chunk
            
        except Exception as e:
            self._logger.error(f"Ошибка загрузки чанка {chunk_x}, {chunk_y}: {e}")
            return None
    
    def _load_chunk_async(self, chunk_id: str):
        """Асинхронная загрузка чанка"""
        try:
            if self.executor:
                future = self.executor.submit(self._generate_chunk_content, chunk_id)
                future.add_done_callback(lambda f: self._on_chunk_generated(chunk_id, f))
            
        except Exception as e:
            self._logger.error(f"Ошибка запуска асинхронной загрузки чанка {chunk_id}: {e}")
    
    def _generate_chunk_content(self, chunk_id: str) -> bool:
        """Генерация содержимого чанка"""
        try:
            if chunk_id not in self.chunks:
return False
            
            chunk = self.chunks[chunk_id]
            start_time = time.time()
            
            # Генерируем карту высот
            height_map = self.height_generator.generate_height_map(
                chunk.chunk_x, chunk.chunk_y, chunk.chunk_size
            )
            
            # Генерируем карту биомов
            biome_map = self.height_generator.generate_biome_map(
                height_map, chunk.chunk_x, chunk.chunk_y
            )
            
            # Генерируем структуры
            structures = self.structure_generator.generate_structures_for_chunk(
                chunk.chunk_x, chunk.chunk_y, chunk.chunk_size, self.settings.world_seed
            )
            
            # Сохраняем результаты
            with self.generation_lock:
                chunk.height_map = height_map
                chunk.biome_map = biome_map
                chunk.structures = [s.structure_id for s in structures]
                chunk.generation_time = time.time() - start_time
                chunk.state = ChunkState.LOADED
                chunk.last_accessed = time.time()
            
# Обновляем статистику
            self.world_stats.total_structures += len(structures)
            self.world_stats.generation_time += chunk.generation_time
            
            self._logger.debug(f"Чанк {chunk_id} сгенерирован за {chunk.generation_time:.3f}с")
return True
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации содержимого чанка {chunk_id}: {e}")
return False
    
    def _on_chunk_generated(self, chunk_id: str, future):
        """Обработка завершения генерации чанка"""
        try:
            if chunk_id in self.chunks:
                chunk = self.chunks[chunk_id]
                
                if future.result():
                    # Уведомляем о загрузке чанка
                    self._notify_chunk_loaded(chunk)
                    
                    # Обновляем статистику
                    self.world_stats.loaded_chunks += 1
                    self.world_stats.total_chunks += 1
                else:
                    # Ошибка генерации
                    chunk.state = ChunkState.UNLOADED
                    if chunk_id in self.chunks:
                        del self.chunks[chunk_id]
                    if (chunk.chunk_x, chunk.chunk_y) in self.spatial_index:
                        del self.spatial_index[(chunk.chunk_x, chunk.chunk_y)]
            
        except Exception as e:
            self._logger.error(f"Ошибка обработки завершения генерации чанка {chunk_id}: {e}")
    
    def unload_chunk(self, chunk_x: int, chunk_y: int) -> bool:
        """Выгрузка чанка мира"""
        try:
            chunk_id = f"{chunk_x}_{chunk_y}"
            
            if chunk_id not in self.chunks:
return False
            
            chunk = self.chunks[chunk_id]
            
            if chunk.state in [ChunkState.LOADING, ChunkState.LOADED, ChunkState.ACTIVE]:
                chunk.state = ChunkState.UNLOADING
                self.chunk_unload_queue.append(chunk_id)
                
                # Уведомляем о выгрузке
                self._notify_chunk_unloaded(chunk)
                
                # Обновляем статистику
                if chunk.state == ChunkState.LOADED:
                    self.world_stats.loaded_chunks -= 1
                elif chunk.state == ChunkState.ACTIVE:
                    self.world_stats.active_chunks -= 1
                
return True
            
return False
            
        except Exception as e:
            self._logger.error(f"Ошибка выгрузки чанка {chunk_x}, {chunk_y}: {e}")
return False
    
    def _unload_oldest_chunks(self):
        """Выгрузка самых старых чанков"""
        try:
            # Сортируем чанки по времени последнего доступа
            sorted_chunks = sorted(
                [c for c in self.chunks.values() if c.state in [ChunkState.LOADED, ChunkState.ACTIVE]],
                key=lambda c: c.last_accessed
            )
            
            # Выгружаем самые старые
            chunks_to_unload = sorted_chunks[:len(sorted_chunks) // 2]
            
            for chunk in chunks_to_unload:
                self.unload_chunk(chunk.chunk_x, chunk.chunk_y)
            
        except Exception as e:
            self._logger.error(f"Ошибка выгрузки старых чанков: {e}")
    
    def get_chunk_at_position(self, world_x: float, world_y: float) -> Optional[WorldChunk]:
        """Получение чанка по позиции в мире"""
        try:
            chunk_x = int(world_x // self.settings.chunk_size)
            chunk_y = int(world_y // self.settings.chunk_size)
            
            chunk_id = self.spatial_index.get((chunk_x, chunk_y))
            if chunk_id and chunk_id in self.chunks:
                return self.chunks[chunk_id]
            
            return None
            
        except Exception as e:
            self._logger.error(f"Ошибка получения чанка по позиции ({world_x}, {world_y}): {e}")
return None
    
    def get_chunks_in_area(self, center: Tuple[float, float], radius: float) -> List[WorldChunk]:
        """Получение чанков в заданной области"""
        try:
            chunks = []
            center_chunk_x = int(center[0] // self.settings.chunk_size)
            center_chunk_y = int(center[1] // self.settings.chunk_size)
            
            # Определяем диапазон чанков
            chunk_radius = int(radius // self.settings.chunk_size) + 1
            
            for dx in range(-chunk_radius, chunk_radius + 1):
                for dy in range(-chunk_radius, chunk_radius + 1):
                    chunk_x = center_chunk_x + dx
                    chunk_y = center_chunk_y + dy
                    
                    chunk_id = self.spatial_index.get((chunk_x, chunk_y))
                    if chunk_id and chunk_id in self.chunks:
                        chunk = self.chunks[chunk_id]
                        if chunk.state in [ChunkState.LOADED, ChunkState.ACTIVE]:
                            chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            self._logger.error(f"Ошибка получения чанков в области: {e}")
            return []
    
    def update_chunk_priorities(self, player_position: Tuple[float, float]):
        """Обновление приоритетов загрузки чанков на основе позиции игрока"""
        try:
            player_chunk_x = int(player_position[0] // self.settings.chunk_size)
            player_chunk_y = int(player_position[1] // self.settings.chunk_size)
            
            # Определяем чанки в области видимости
            view_chunks = []
            for dx in range(-self.settings.view_distance, self.settings.view_distance + 1):
                for dy in range(-self.settings.view_distance, self.settings.view_distance + 1):
                    chunk_x = player_chunk_x + dx
                    chunk_y = player_chunk_y + dy
                    chunk_id = f"{chunk_x}_{chunk_y}"
                    
                    if chunk_id not in self.chunks:
                        # Загружаем новый чанк с высоким приоритетом
                        self.load_chunk(chunk_x, chunk_y, priority=True)
                    else:
                        chunk = self.chunks[chunk_id]
                        if chunk.state == ChunkState.LOADED:
                            chunk.state = ChunkState.ACTIVE
                        chunk.last_accessed = time.time()
                        view_chunks.append(chunk_id)
            
            # Выгружаем чанки вне области видимости
            for chunk_id, chunk in self.chunks.items():
                if chunk_id not in view_chunks and chunk.state == ChunkState.ACTIVE:
                    chunk.state = ChunkState.LOADED
            
        except Exception as e:
            self._logger.error(f"Ошибка обновления приоритетов чанков: {e}")
    
    def add_chunk_loaded_callback(self, callback: Callable):
        """Добавление колбэка для события загрузки чанка"""
        try:
            if callback not in self.chunk_loaded_callbacks:
                self.chunk_loaded_callbacks.append(callback)
        except Exception as e:
            self._logger.error(f"Ошибка добавления колбэка загрузки чанка: {e}")
    
    def add_chunk_unloaded_callback(self, callback: Callable):
        """Добавление колбэка для события выгрузки чанка"""
        try:
            if callback not in self.chunk_unloaded_callbacks:
                self.chunk_unloaded_callbacks.append(callback)
        except Exception as e:
            self._logger.error(f"Ошибка добавления колбэка выгрузки чанка: {e}")
    
    def _notify_chunk_loaded(self, chunk: WorldChunk):
        """Уведомление о загрузке чанка"""
        try:
            for callback in self.chunk_loaded_callbacks:
                try:
                    callback(chunk)
                except Exception as e:
                    self._logger.error(f"Ошибка в колбэке загрузки чанка: {e}")
        except Exception as e:
            self._logger.error(f"Ошибка уведомления о загрузке чанка: {e}")
    
    def _notify_chunk_unloaded(self, chunk: WorldChunk):
        """Уведомление о выгрузке чанка"""
        try:
            for callback in self.chunk_unloaded_callbacks:
                try:
                    callback(chunk)
                except Exception as e:
                    self._logger.error(f"Ошибка в колбэке выгрузки чанка: {e}")
        except Exception as e:
            self._logger.error(f"Ошибка уведомления о выгрузке чанка: {e}")
    
    def get_world_stats(self) -> WorldStats:
        """Получение статистики мира"""
        try:
            # Обновляем статистику
            self.world_stats.loaded_chunks = len([c for c in self.chunks.values() 
                                                if c.state == ChunkState.LOADED])
            self.world_stats.active_chunks = len([c for c in self.chunks.values() 
                                                if c.state == ChunkState.ACTIVE])
            self.world_stats.total_chunks = len(self.chunks)
            self.world_stats.last_update = time.time()
            
            # Вычисляем использование памяти
            total_memory = 0.0
            for chunk in self.chunks.values():
                if chunk.height_map is not None:
                    total_memory += chunk.height_map.nbytes / (1024 * 1024)  # МБ
                if chunk.biome_map is not None:
                    total_memory += chunk.biome_map.nbytes / (1024 * 1024)  # МБ
            
            self.world_stats.memory_usage_mb = total_memory
            
            return self.world_stats
            
        except Exception as e:
            self._logger.error(f"Ошибка получения статистики мира: {e}")
            return self.world_stats
    
    def save_world_state(self) -> bool:
        """Сохранение состояния мира"""
        try:
            # TODO: Реализовать сохранение состояния мира
            self.last_save_time = time.time()
            self._logger.info("Состояние мира сохранено")
return True
            
        except Exception as e:
            self._logger.error(f"Ошибка сохранения состояния мира: {e}")
return False
    
    def _on_update(self, delta_time: float) -> bool:
        """Обновление менеджера мира"""
        try:
            # Проверяем автосохранение
            if (self.auto_save_enabled and 
                time.time() - self.last_save_time > self.settings.auto_save_interval):
                self.save_world_state()
            
            # Обрабатываем очередь выгрузки
            self._process_unload_queue()
            
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка обновления менеджера мира: {e}")
            return False
    
    def _process_unload_queue(self):
        """Обработка очереди выгрузки чанков"""
        try:
            while self.chunk_unload_queue:
                chunk_id = self.chunk_unload_queue.pop(0)
                
                if chunk_id in self.chunks:
                    chunk = self.chunks[chunk_id]
                    
                    # Очищаем данные чанка
                    chunk.height_map = None
                    chunk.biome_map = None
                    chunk.structures.clear()
                    chunk.entities.clear()
                    chunk.state = ChunkState.UNLOADED
                    
                    # Удаляем из индекса
                    if (chunk.chunk_x, chunk.chunk_y) in self.spatial_index:
                        del self.spatial_index[(chunk.chunk_x, chunk.chunk_y)]
                    
                    # Удаляем чанк
                    del self.chunks[chunk_id]
                    
                    self._logger.debug(f"Чанк {chunk_id} выгружен")
            
        except Exception as e:
            self._logger.error(f"Ошибка обработки очереди выгрузки: {e}")
    
    def _on_destroy(self) -> bool:
        """Уничтожение менеджера мира"""
        try:
            # Сохраняем состояние
            self.save_world_state()
            
            # Останавливаем executor
            if self.executor:
                self.executor.shutdown(wait=True)
            
            # Очищаем чанки
            self.chunks.clear()
            self.spatial_index.clear()
            self.chunk_cache.clear()
            
            # Очищаем колбэки
            self.chunk_loaded_callbacks.clear()
            self.chunk_unloaded_callbacks.clear()
            self.world_updated_callbacks.clear()
            
            self._logger.info("Менеджер мира уничтожен")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка уничтожения менеджера мира: {e}")
return False
