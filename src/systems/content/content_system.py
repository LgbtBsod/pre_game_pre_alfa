#!/usr/bin/env python3
"""Система контента - оптимизированные генераторы
Управление игровым контентом с улучшенной производительностью"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import math
import time
import random
import threading
import concurrent.futures

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState

logger = logging.getLogger(__name__)

# = ТИПЫ КОНТЕНТА

class ContentType(Enum):
    """Типы контента"""
    WORLD = "world"                # Мир
    BIOME = "biome"                # Биомы
    CLIMATE = "climate"            # Климат
    STRUCTURE = "structure"        # Структуры
    DUNGEON = "dungeon"            # Подземелья
    SETTLEMENT = "settlement"      # Поселения
    TOWER = "tower"                # Башни
    MAP = "map"                    # Карты

class GenerationType(Enum):
    """Типы генерации"""
    PROCEDURAL = "procedural"      # Процедурная
    TEMPLATE = "template"          # По шаблону
    HYBRID = "hybrid"              # Гибридная

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class ContentTemplate:
    """Шаблон контента"""
    template_id: str
    name: str
    content_type: ContentType
    generation_type: GenerationType
    parameters: Dict[str, Any] = field(default_factory=dict)
    complexity: float = 1.0
    generation_time: float = 0.0

@dataclass
class ContentChunk:
    """Чанк контента"""
    chunk_id: str
    position: Tuple[int, int]
    content_type: ContentType
    data: Dict[str, Any] = field(default_factory=dict)
    generated_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0

@dataclass
class GenerationTask:
    """Задача генерации"""
    task_id: str
    content_type: ContentType
    position: Tuple[int, int]
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Optional[ContentChunk] = None
    error: Optional[str] = None

class ContentSystem(BaseComponent):
    """Система контента"""
    
    def __init__(self):
        super().__init__(
            component_id="content_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.NORMAL
        )
        
        # Шаблоны контента
        self.content_templates: Dict[str, ContentTemplate] = {}
        
        # Кэш контента
        self.content_cache: Dict[str, ContentChunk] = {}
        self.cache_size_limit: int = 1000
        
        # Очередь генерации
        self.generation_queue: List[GenerationTask] = []
        self.active_tasks: Dict[str, GenerationTask] = {}
        
        # Настройки производительности
        self.max_workers: int = 4
        self.chunk_size: int = 64
        self.lazy_loading: bool = True
        self.async_generation: bool = True
        
        # Статистика
        self.total_chunks_generated: int = 0
        self.total_generation_time: float = 0.0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        
        # Callbacks
        self.on_chunk_generated: Optional[Callable] = None
        self.on_chunk_loaded: Optional[Callable] = None
        self.on_chunk_unloaded: Optional[Callable] = None
        
        logger.info("Система контента инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы контента"""
        try:
            logger.info("Инициализация системы контента...")
            
            # Создание шаблонов контента
            if not self._create_content_templates():
                return False
            
            # Запуск асинхронной генерации
            if self.async_generation:
                self._start_async_generation()
            
            self.state = LifecycleState.READY
            logger.info("Система контента успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы контента: {e}")
            self.state = LifecycleState.ERROR
            return False
    
    def _create_content_templates(self) -> bool:
        """Создание шаблонов контента"""
        try:
            # Шаблоны мира
            world_templates = [
                ContentTemplate(
                    template_id="grassland_world",
                    name="Травянистая равнина",
                    content_type=ContentType.WORLD,
                    generation_type=GenerationType.PROCEDURAL,
                    parameters={
                        "biome_type": "grassland",
                        "elevation_range": (0, 100),
                        "vegetation_density": 0.7,
                        "water_bodies": 0.1
                    },
                    complexity=1.0
                ),
                ContentTemplate(
                    template_id="forest_world",
                    name="Лесной массив",
                    content_type=ContentType.WORLD,
                    generation_type=GenerationType.PROCEDURAL,
                    parameters={
                        "biome_type": "forest",
                        "elevation_range": (50, 200),
                        "vegetation_density": 0.9,
                        "tree_density": 0.8
                    },
                    complexity=1.5
                ),
                ContentTemplate(
                    template_id="mountain_world",
                    name="Горная местность",
                    content_type=ContentType.WORLD,
                    generation_type=GenerationType.PROCEDURAL,
                    parameters={
                        "biome_type": "mountain",
                        "elevation_range": (200, 500),
                        "rock_density": 0.8,
                        "cave_systems": 0.3
                    },
                    complexity=2.0
                )
            ]
            
            # Шаблоны структур
            structure_templates = [
                ContentTemplate(
                    template_id="village_structure",
                    name="Деревня",
                    content_type=ContentType.STRUCTURE,
                    generation_type=GenerationType.TEMPLATE,
                    parameters={
                        "building_count": (5, 15),
                        "building_types": ["house", "shop", "inn"],
                        "layout_type": "organic"
                    },
                    complexity=1.5
                ),
                ContentTemplate(
                    template_id="castle_structure",
                    name="Замок",
                    content_type=ContentType.STRUCTURE,
                    generation_type=GenerationType.TEMPLATE,
                    parameters={
                        "tower_count": (4, 8),
                        "wall_height": (10, 20),
                        "moat": True,
                        "keep_size": "large"
                    },
                    complexity=3.0
                ),
                ContentTemplate(
                    template_id="dungeon_structure",
                    name="Подземелье",
                    content_type=ContentType.DUNGEON,
                    generation_type=GenerationType.PROCEDURAL,
                    parameters={
                        "room_count": (10, 30),
                        "corridor_complexity": 0.7,
                        "trap_density": 0.3,
                        "treasure_rooms": 0.2
                    },
                    complexity=2.5
                )
            ]
            
            # Добавление всех шаблонов
            all_templates = world_templates + structure_templates
            
            for template in all_templates:
                self.content_templates[template.template_id] = template
            
            logger.info(f"Создано {len(self.content_templates)} шаблонов контента")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания шаблонов контента: {e}")
            return False
    
    def _start_async_generation(self):
        """Запуск асинхронной генерации"""
        try:
            # Создание пула потоков для генерации
            self.generation_executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            )
            
            # Запуск обработчика очереди
            self.queue_processor = threading.Thread(
                target=self._process_generation_queue,
                daemon=True
            )
            self.queue_processor.start()
            
            logger.info("Асинхронная генерация запущена")
            
        except Exception as e:
            logger.error(f"Ошибка запуска асинхронной генерации: {e}")
    
    def _process_generation_queue(self):
        """Обработка очереди генерации"""
        try:
            while self.state == LifecycleState.READY:
                if self.generation_queue:
                    # Получение задачи с наивысшим приоритетом
                    task = max(self.generation_queue, key=lambda t: t.priority)
                    self.generation_queue.remove(task)
                    
                    # Выполнение генерации
                    future = self.generation_executor.submit(
                        self._generate_content_chunk,
                        task.content_type,
                        task.position
                    )
                    
                    # Ожидание результата
                    try:
                        chunk = future.result(timeout=30.0)
                        task.result = chunk
                        task.completed_at = time.time()
                        
                        # Сохранение в кэш
                        self._cache_chunk(chunk)
                        
                        # Вызов callback
                        if self.on_chunk_generated:
                            self.on_chunk_generated(chunk)
                        
                    except Exception as e:
                        task.error = str(e)
                        logger.error(f"Ошибка генерации контента: {e}")
                    
                    finally:
                        if task.task_id in self.active_tasks:
                            del self.active_tasks[task.task_id]
                
                time.sleep(0.1)  # Небольшая пауза
                
        except Exception as e:
            logger.error(f"Ошибка обработки очереди генерации: {e}")
    
    def request_content(self, content_type: ContentType, position: Tuple[int, int], 
                       priority: int = 0) -> Optional[ContentChunk]:
        """Запрос контента"""
        try:
            # Проверка кэша
            chunk_id = self._get_chunk_id(content_type, position)
            if chunk_id in self.content_cache:
                chunk = self.content_cache[chunk_id]
                chunk.last_accessed = time.time()
                chunk.access_count += 1
                self.cache_hits += 1
                
                # Вызов callback
                if self.on_chunk_loaded:
                    self.on_chunk_loaded(chunk)
                
                return chunk
            
            self.cache_misses += 1
            
            # Синхронная генерация если отключена асинхронная
            if not self.async_generation:
                chunk = self._generate_content_chunk(content_type, position)
                if chunk:
                    self._cache_chunk(chunk)
                return chunk
            
            # Асинхронная генерация
            task = GenerationTask(
                task_id=chunk_id,
                content_type=content_type,
                position=position,
                priority=priority
            )
            
            self.generation_queue.append(task)
            self.active_tasks[task.task_id] = task
            
            # Если высокий приоритет, ждем завершения
            if priority >= 10:
                while task.task_id in self.active_tasks:
                    time.sleep(0.01)
                
                if task.result:
                    return task.result
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка запроса контента: {e}")
            return None
    
    def _generate_content_chunk(self, content_type: ContentType, 
                               position: Tuple[int, int]) -> Optional[ContentChunk]:
        """Генерация чанка контента"""
        try:
            start_time = time.time()
            
            # Выбор шаблона
            template = self._select_template(content_type, position)
            if not template:
                return None
            
            # Генерация данных
            if template.generation_type == GenerationType.PROCEDURAL:
                data = self._generate_procedural_content(template, position)
            elif template.generation_type == GenerationType.TEMPLATE:
                data = self._generate_template_content(template, position)
            else:  # HYBRID
                data = self._generate_hybrid_content(template, position)
            
            # Создание чанка
            chunk = ContentChunk(
                chunk_id=self._get_chunk_id(content_type, position),
                position=position,
                content_type=content_type,
                data=data
            )
            
            # Обновление статистики
            generation_time = time.time() - start_time
            self.total_chunks_generated += 1
            self.total_generation_time += generation_time
            template.generation_time = generation_time
            
            logger.debug(f"Сгенерирован чанк {chunk.chunk_id} за {generation_time:.3f}s")
            return chunk
            
        except Exception as e:
            logger.error(f"Ошибка генерации чанка контента: {e}")
            return None
    
    def _select_template(self, content_type: ContentType, 
                        position: Tuple[int, int]) -> Optional[ContentTemplate]:
        """Выбор шаблона для генерации"""
        try:
            # Фильтрация по типу контента
            available_templates = [
                template for template in self.content_templates.values()
                if template.content_type == content_type
            ]
            
            if not available_templates:
                return None
            
            # Выбор на основе позиции (можно использовать шум для разнообразия)
            seed = hash(position) % 1000
            random.seed(seed)
            
            # Взвешенный выбор по сложности
            weights = [1.0 / template.complexity for template in available_templates]
            selected_template = random.choices(available_templates, weights=weights)[0]
            
            return selected_template
            
        except Exception as e:
            logger.error(f"Ошибка выбора шаблона: {e}")
            return None
    
    def _generate_procedural_content(self, template: ContentTemplate, 
                                   position: Tuple[int, int]) -> Dict[str, Any]:
        """Генерация процедурного контента"""
        try:
            data = {
                "template_id": template.template_id,
                "generation_type": "procedural",
                "position": position,
                "parameters": template.parameters.copy()
            }
            
            # Генерация на основе типа контента
            if template.content_type == ContentType.WORLD:
                data.update(self._generate_world_data(template, position))
            elif template.content_type == ContentType.DUNGEON:
                data.update(self._generate_dungeon_data(template, position))
            elif template.content_type == ContentType.STRUCTURE:
                data.update(self._generate_structure_data(template, position))
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации процедурного контента: {e}")
            return {}
    
    def _generate_template_content(self, template: ContentTemplate, 
                                 position: Tuple[int, int]) -> Dict[str, Any]:
        """Генерация контента по шаблону"""
        try:
            data = {
                "template_id": template.template_id,
                "generation_type": "template",
                "position": position,
                "parameters": template.parameters.copy()
            }
            
            # Применение шаблона
            if template.content_type == ContentType.STRUCTURE:
                data.update(self._apply_structure_template(template, position))
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации контента по шаблону: {e}")
            return {}
    
    def _generate_hybrid_content(self, template: ContentTemplate, 
                               position: Tuple[int, int]) -> Dict[str, Any]:
        """Генерация гибридного контента"""
        try:
            # Комбинация процедурной и шаблонной генерации
            procedural_data = self._generate_procedural_content(template, position)
            template_data = self._generate_template_content(template, position)
            
            # Объединение данных
            data = {
                "template_id": template.template_id,
                "generation_type": "hybrid",
                "position": position,
                "parameters": template.parameters.copy()
            }
            
            data.update(procedural_data)
            data.update(template_data)
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации гибридного контента: {e}")
            return {}
    
    def _generate_world_data(self, template: ContentTemplate, 
                           position: Tuple[int, int]) -> Dict[str, Any]:
        """Генерация данных мира"""
        try:
            seed = hash(position) % 10000
            random.seed(seed)
            
            params = template.parameters
            elevation_range = params.get("elevation_range", (0, 100))
            
            data = {
                "elevation": random.randint(*elevation_range),
                "biome_type": params.get("biome_type", "grassland"),
                "vegetation_density": random.uniform(0.0, params.get("vegetation_density", 0.7)),
                "water_bodies": random.uniform(0.0, params.get("water_bodies", 0.1)),
                "features": []
            }
            
            # Добавление особенностей
            if data["biome_type"] == "forest":
                data["tree_density"] = random.uniform(0.0, params.get("tree_density", 0.8))
                data["features"].extend(["trees", "undergrowth"])
            
            elif data["biome_type"] == "mountain":
                data["rock_density"] = random.uniform(0.0, params.get("rock_density", 0.8))
                data["features"].extend(["rocks", "cliffs"])
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации данных мира: {e}")
            return {}
    
    def _generate_dungeon_data(self, template: ContentTemplate, 
                             position: Tuple[int, int]) -> Dict[str, Any]:
        """Генерация данных подземелья"""
        try:
            seed = hash(position) % 10000
            random.seed(seed)
            
            params = template.parameters
            room_count = random.randint(*params.get("room_count", (10, 30)))
            
            data = {
                "room_count": room_count,
                "rooms": [],
                "corridors": [],
                "traps": [],
                "treasures": []
            }
            
            # Генерация комнат
            for i in range(room_count):
                room = {
                    "id": i,
                    "position": (random.randint(0, self.chunk_size), random.randint(0, self.chunk_size)),
                    "size": (random.randint(3, 8), random.randint(3, 8)),
                    "type": random.choice(["empty", "treasure", "trap", "boss"])
                }
                data["rooms"].append(room)
            
            # Генерация коридоров
            corridor_count = int(room_count * params.get("corridor_complexity", 0.7))
            for i in range(corridor_count):
                corridor = {
                    "id": i,
                    "start": random.choice(data["rooms"])["position"],
                    "end": random.choice(data["rooms"])["position"],
                    "width": random.randint(1, 3)
                }
                data["corridors"].append(corridor)
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации данных подземелья: {e}")
            return {}
    
    def _generate_structure_data(self, template: ContentTemplate, 
                               position: Tuple[int, int]) -> Dict[str, Any]:
        """Генерация данных структуры"""
        try:
            seed = hash(position) % 10000
            random.seed(seed)
            
            params = template.parameters
            
            data = {
                "buildings": [],
                "layout": params.get("layout_type", "grid"),
                "defenses": []
            }
            
            # Генерация зданий
            if "building_count" in params:
                building_count = random.randint(*params["building_count"])
                building_types = params.get("building_types", ["house"])
                
                for i in range(building_count):
                    building = {
                        "id": i,
                        "type": random.choice(building_types),
                        "position": (random.randint(0, self.chunk_size), random.randint(0, self.chunk_size)),
                        "size": (random.randint(2, 5), random.randint(2, 5))
                    }
                    data["buildings"].append(building)
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации данных структуры: {e}")
            return {}
    
    def _apply_structure_template(self, template: ContentTemplate, 
                                position: Tuple[int, int]) -> Dict[str, Any]:
        """Применение шаблона структуры"""
        try:
            data = {
                "template_applied": True,
                "template_parameters": template.parameters.copy()
            }
            
            # Применение специфичных параметров шаблона
            if template.template_id == "castle_structure":
                data["towers"] = random.randint(*template.parameters.get("tower_count", (4, 8)))
                data["wall_height"] = random.randint(*template.parameters.get("wall_height", (10, 20)))
                data["has_moat"] = template.parameters.get("moat", True)
            
            elif template.template_id == "village_structure":
                data["organic_layout"] = template.parameters.get("layout_type") == "organic"
                data["building_variety"] = template.parameters.get("building_types", ["house"])
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка применения шаблона структуры: {e}")
            return {}
    
    def _get_chunk_id(self, content_type: ContentType, position: Tuple[int, int]) -> str:
        """Получение ID чанка"""
        return f"{content_type.value}_{position[0]}_{position[1]}"
    
    def _cache_chunk(self, chunk: ContentChunk):
        """Кэширование чанка"""
        try:
            # Проверка лимита кэша
            if len(self.content_cache) >= self.cache_size_limit:
                self._cleanup_cache()
            
            self.content_cache[chunk.chunk_id] = chunk
            
        except Exception as e:
            logger.error(f"Ошибка кэширования чанка: {e}")
    
    def _cleanup_cache(self):
        """Очистка кэша"""
        try:
            if not self.content_cache:
                return
            
            # Удаление наименее используемых чанков
            chunks_to_remove = sorted(
                self.content_cache.values(),
                key=lambda c: (c.access_count, c.last_accessed)
            )[:len(self.content_cache) // 4]  # Удаляем 25% наименее используемых
            
            for chunk in chunks_to_remove:
                del self.content_cache[chunk.chunk_id]
                
                # Вызов callback
                if self.on_chunk_unloaded:
                    self.on_chunk_unloaded(chunk)
            
            logger.debug(f"Очищено {len(chunks_to_remove)} чанков из кэша")
            
        except Exception as e:
            logger.error(f"Ошибка очистки кэша: {e}")
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """Получение статистики контента"""
        try:
            return {
                "total_chunks_generated": self.total_chunks_generated,
                "total_generation_time": self.total_generation_time,
                "average_generation_time": self.total_generation_time / max(1, self.total_chunks_generated),
                "cache_size": len(self.content_cache),
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses) * 100,
                "active_tasks": len(self.active_tasks),
                "queued_tasks": len(self.generation_queue),
                "content_templates": len(self.content_templates)
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики контента: {e}")
            return {}
    
    def cleanup(self):
        """Очистка системы контента"""
        try:
            # Остановка асинхронной генерации
            if hasattr(self, 'generation_executor'):
                self.generation_executor.shutdown(wait=True)
            
            # Очистка кэша
            self.content_cache.clear()
            
            # Очистка очереди
            self.generation_queue.clear()
            self.active_tasks.clear()
            
            logger.info("Система контента очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы контента: {e}")
