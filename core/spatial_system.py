#!/usr/bin/env python3
"""
Оптимизированная система пространственного поиска.
Использует квадродерево для эффективного поиска объектов в 2D пространстве.
"""

import math
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SpatialObjectType(Enum):
    """Типы пространственных объектов"""
    ENTITY = "entity"
    ITEM = "item"
    PROJECTILE = "projectile"
    EFFECT = "effect"
    TRIGGER = "trigger"


class SpatialIndex(Enum):
    """Типы пространственных индексов"""
    QUADTREE = "quadtree"
    GRID = "grid"
    RTREE = "rtree"
    HASH = "hash"


@dataclass
class BoundingBox:
    """Ограничивающий прямоугольник"""
    x: float
    y: float
    width: float
    height: float
    
    @property
    def left(self) -> float:
        return self.x
    
    @property
    def right(self) -> float:
        return self.x + self.width
    
    @property
    def top(self) -> float:
        return self.y
    
    @property
    def bottom(self) -> float:
        return self.y + self.height
    
    @property
    def center_x(self) -> float:
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        return self.y + self.height / 2
    
    def intersects(self, other: 'BoundingBox') -> bool:
        """Проверка пересечения с другим прямоугольником"""
        return (self.left < other.right and self.right > other.left and
                self.top < other.bottom and self.bottom > other.top)
    
    def contains_point(self, x: float, y: float) -> bool:
        """Проверка содержания точки"""
        return self.left <= x <= self.right and self.top <= y <= self.bottom
    
    def contains_box(self, other: 'BoundingBox') -> bool:
        """Проверка полного содержания другого прямоугольника"""
        return (self.left <= other.left and self.right >= other.right and
                self.top <= other.top and self.bottom >= other.bottom)
    
    def distance_to_point(self, x: float, y: float) -> float:
        """Расстояние до точки"""
        dx = max(0, max(self.left - x, x - self.right))
        dy = max(0, max(self.top - y, y - self.bottom))
        return math.sqrt(dx * dx + dy * dy)
    
    def distance_to_box(self, other: 'BoundingBox') -> float:
        """Расстояние до другого прямоугольника"""
        dx = max(0, max(self.left - other.right, other.left - self.right))
        dy = max(0, max(self.top - other.bottom, other.top - self.bottom))
        return math.sqrt(dx * dx + dy * dy)


@dataclass
class SpatialObject:
    """Пространственный объект"""
    id: str
    object_type: SpatialObjectType
    bounds: BoundingBox
    data: Any
    last_update: float = 0.0
    
    def __post_init__(self):
        if self.last_update == 0.0:
            self.last_update = time.time()


class QuadTreeNode:
    """Узел квадродерева"""
    
    def __init__(self, bounds: BoundingBox, max_objects: int = 10, max_depth: int = 8):
        self.bounds = bounds
        self.max_objects = max_objects
        self.max_depth = max_depth
        
        self.objects: List[SpatialObject] = []
        self.children: List[Optional['QuadTreeNode']] = [None] * 4
        self.depth = 0
        self.is_leaf = True
    
    def insert(self, obj: SpatialObject) -> bool:
        """Вставить объект в узел"""
        if not self.bounds.contains_box(obj.bounds):
            return False
        
        if self.is_leaf and len(self.objects) < self.max_objects:
            self.objects.append(obj)
            return True
        
        if self.is_leaf and self.depth < self.max_depth:
            self._split()
        
        if not self.is_leaf:
            for child in self.children:
                if child and child.insert(obj):
                    return True
        
        # Если не удалось вставить в дочерние узлы, добавляем в текущий
        if self.is_leaf:
            self.objects.append(obj)
        
        return True
    
    def _split(self) -> None:
        """Разделить узел на 4 дочерних"""
        half_width = self.bounds.width / 2
        half_height = self.bounds.height / 2
        mid_x = self.bounds.x + half_width
        mid_y = self.bounds.y + half_height
        
        # Создаем дочерние узлы
        self.children[0] = QuadTreeNode(  # Северо-запад
            BoundingBox(self.bounds.x, self.bounds.y, half_width, half_height),
            self.max_objects, self.max_depth
        )
        self.children[1] = QuadTreeNode(  # Северо-восток
            BoundingBox(mid_x, self.bounds.y, half_width, half_height),
            self.max_objects, self.max_depth
        )
        self.children[2] = QuadTreeNode(  # Юго-запад
            BoundingBox(self.bounds.x, mid_y, half_width, half_height),
            self.max_objects, self.max_depth
        )
        self.children[3] = QuadTreeNode(  # Юго-восток
            BoundingBox(mid_x, mid_y, half_width, half_height),
            self.max_objects, self.max_depth
        )
        
        # Устанавливаем глубину дочерних узлов
        for child in self.children:
            child.depth = self.depth + 1
        
        # Перемещаем существующие объекты в дочерние узлы
        remaining_objects = []
        for obj in self.objects:
            inserted = False
            for child in self.children:
                if child.insert(obj):
                    inserted = True
                    break
            if not inserted:
                remaining_objects.append(obj)
        
        self.objects = remaining_objects
        self.is_leaf = False
    
    def query_range(self, query_bounds: BoundingBox) -> List[SpatialObject]:
        """Поиск объектов в заданном диапазоне"""
        result = []
        
        if not self.bounds.intersects(query_bounds):
            return result
        
        # Добавляем объекты текущего узла
        for obj in self.objects:
            if obj.bounds.intersects(query_bounds):
                result.append(obj)
        
        # Рекурсивно ищем в дочерних узлах
        if not self.is_leaf:
            for child in self.children:
                if child:
                    result.extend(child.query_range(query_bounds))
        
        return result
    
    def query_radius(self, center_x: float, center_y: float, radius: float) -> List[SpatialObject]:
        """Поиск объектов в радиусе от точки"""
        # Создаем квадратную область для быстрого отсечения
        query_bounds = BoundingBox(
            center_x - radius, center_y - radius,
            radius * 2, radius * 2
        )
        
        candidates = self.query_range(query_bounds)
        result = []
        
        for obj in candidates:
            distance = obj.bounds.distance_to_point(center_x, center_y)
            if distance <= radius:
                result.append(obj)
        
        return result
    
    def remove(self, obj_id: str) -> bool:
        """Удалить объект по ID"""
        # Удаляем из текущего узла
        for i, obj in enumerate(self.objects):
            if obj.id == obj_id:
                del self.objects[i]
                return True
        
        # Рекурсивно ищем в дочерних узлах
        if not self.is_leaf:
            for child in self.children:
                if child and child.remove(obj_id):
                    return True
        
        return False
    
    def update_object(self, obj_id: str, new_bounds: BoundingBox) -> bool:
        """Обновить позицию объекта"""
        # Находим и удаляем объект
        if self.remove(obj_id):
            # Создаем новый объект с обновленными границами
            # (в реальной реализации нужно сохранить данные объекта)
            new_obj = SpatialObject(
                id=obj_id,
                object_type=SpatialObjectType.ENTITY,  # Временное значение
                bounds=new_bounds,
                data=None
            )
            return self.insert(new_obj)
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику узла"""
        stats = {
            'objects_count': len(self.objects),
            'depth': self.depth,
            'is_leaf': self.is_leaf,
            'bounds': self.bounds
        }
        
        if not self.is_leaf:
            stats['children'] = [
                child.get_stats() if child else None
                for child in self.children
            ]
        
        return stats


class SpatialSystem:
    """Система пространственного поиска"""
    
    def __init__(self, world_bounds: BoundingBox = None, max_objects_per_node: int = 10):
        if world_bounds is None:
            world_bounds = BoundingBox(0, 0, 10000, 10000)  # Дефолтные границы мира
        self.world_bounds = world_bounds
        self.max_objects_per_node = max_objects_per_node
        
        # Корневой узел квадродерева
        self.root = QuadTreeNode(world_bounds, max_objects_per_node)
        
        # Кэш объектов для быстрого доступа
        self._object_cache: Dict[str, SpatialObject] = {}
        
        # Статистика
        self._stats = {
            'objects_added': 0,
            'objects_removed': 0,
            'queries_performed': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def add_object(self, obj_id: str, bounds: BoundingBox, 
                  object_type: SpatialObjectType = SpatialObjectType.ENTITY, data: Any = None) -> bool:
        """
        Добавить объект в пространственную систему
        
        Args:
            obj_id: Уникальный ID объекта
            object_type: Тип объекта
            bounds: Границы объекта
            data: Дополнительные данные
            
        Returns:
            True если объект добавлен успешно
        """
        if obj_id in self._object_cache:
            logger.warning(f"Объект с ID {obj_id} уже существует")
            return False
        
        spatial_obj = SpatialObject(
            id=obj_id,
            object_type=object_type,
            bounds=bounds,
            data=data
        )
        
        if self.root.insert(spatial_obj):
            self._object_cache[obj_id] = spatial_obj
            self._stats['objects_added'] += 1
            return True
        
        return False
    
    def remove_object(self, obj_id: str) -> bool:
        """
        Удалить объект из пространственной системы
        
        Args:
            obj_id: ID объекта для удаления
            
        Returns:
            True если объект удален
        """
        if obj_id in self._object_cache:
            if self.root.remove(obj_id):
                del self._object_cache[obj_id]
                self._stats['objects_removed'] += 1
                return True
        
        return False
    
    def update_object(self, obj_id: str, new_bounds: BoundingBox) -> bool:
        """
        Обновить позицию объекта
        
        Args:
            obj_id: ID объекта
            new_bounds: Новые границы объекта
            
        Returns:
            True если объект обновлен
        """
        if obj_id in self._object_cache:
            if self.root.update_object(obj_id, new_bounds):
                # Обновляем кэш
                self._object_cache[obj_id].bounds = new_bounds
                self._object_cache[obj_id].last_update = time.time()
                return True
        
        return False
    
    def query_area(self, bounds: BoundingBox) -> List[SpatialObject]:
        """Алиас для query_range для совместимости"""
        return self.query_range(bounds)
    
    def query_range(self, bounds: BoundingBox) -> List[SpatialObject]:
        """
        Поиск объектов в заданном диапазоне
        
        Args:
            bounds: Границы поиска
            
        Returns:
            Список найденных объектов
        """
        self._stats['queries_performed'] += 1
        return self.root.query_range(bounds)
    
    def query_radius(self, center_x: float, center_y: float, radius: float) -> List[SpatialObject]:
        """
        Поиск объектов в радиусе от точки
        
        Args:
            center_x: X координата центра
            center_y: Y координата центра
            radius: Радиус поиска
            
        Returns:
            Список найденных объектов
        """
        self._stats['queries_performed'] += 1
        return self.root.query_radius(center_x, center_y, radius)
    
    def query_nearest(self, center_x: float, center_y: float, 
                     object_type: Optional[SpatialObjectType] = None) -> Optional[SpatialObject]:
        """
        Поиск ближайшего объекта
        
        Args:
            center_x: X координата центра
            center_y: Y координата центра
            object_type: Тип объекта для поиска (опционально)
            
        Returns:
            Ближайший объект или None
        """
        # Начинаем с небольшого радиуса и увеличиваем
        radius = 100.0
        max_radius = self.world_bounds.width + self.world_bounds.height
        
        while radius <= max_radius:
            candidates = self.query_radius(center_x, center_y, radius)
            
            if candidates:
                # Фильтруем по типу если указан
                if object_type:
                    candidates = [obj for obj in candidates if obj.object_type == object_type]
                
                if candidates:
                    # Находим ближайший
                    nearest = min(candidates, 
                                key=lambda obj: obj.bounds.distance_to_point(center_x, center_y))
                    return nearest
            
            radius *= 2
        
        return None
    
    def get_object(self, obj_id: str) -> Optional[SpatialObject]:
        """
        Получить объект по ID
        
        Args:
            obj_id: ID объекта
            
        Returns:
            Объект или None
        """
        if obj_id in self._object_cache:
            self._stats['cache_hits'] += 1
            return self._object_cache[obj_id]
        
        self._stats['cache_misses'] += 1
        return None
    
    def get_objects_by_type(self, object_type: SpatialObjectType) -> List[SpatialObject]:
        """
        Получить все объекты определенного типа
        
        Args:
            object_type: Тип объекта
            
        Returns:
            Список объектов
        """
        return [obj for obj in self._object_cache.values() if obj.object_type == object_type]
    
    def get_all_objects(self) -> List[SpatialObject]:
        """Получить все объекты"""
        return list(self._object_cache.values())
    
    def clear(self) -> None:
        """Очистить все объекты"""
        self.root = QuadTreeNode(self.world_bounds, self.max_objects_per_node)
        self._object_cache.clear()
        logger.info("Пространственная система очищена")
    
    def optimize(self) -> Dict[str, Any]:
        """
        Оптимизация структуры данных
        
        Returns:
            Статистика оптимизации
        """
        start_time = time.time()
        
        # Перестраиваем квадродерево
        old_cache = self._object_cache.copy()
        self.clear()
        
        for obj in old_cache.values():
            self.add_object(obj.id, obj.object_type, obj.bounds, obj.data)
        
        optimization_time = time.time() - start_time
        
        return {
            'optimization_time': optimization_time,
            'objects_rebuilt': len(old_cache),
            'new_tree_depth': self._get_tree_depth(self.root)
        }
    
    def _get_tree_depth(self, node: QuadTreeNode) -> int:
        """Получить глубину дерева"""
        if node.is_leaf:
            return node.depth
        
        max_child_depth = 0
        for child in node.children:
            if child:
                max_child_depth = max(max_child_depth, self._get_tree_depth(child))
        
        return max_child_depth
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику системы"""
        stats = self._stats.copy()
        stats.update({
            'total_objects': len(self._object_cache),
            'tree_stats': self.root.get_stats(),
            'world_bounds': self.world_bounds
        })
        return stats
    
    def validate_integrity(self) -> bool:
        """Проверка целостности данных"""
        try:
            # Проверяем соответствие кэша и дерева
            cached_ids = set(self._object_cache.keys())
            
            # Собираем все ID из дерева
            tree_ids = set()
            self._collect_tree_ids(self.root, tree_ids)
            
            # Проверяем соответствие
            if cached_ids != tree_ids:
                logger.error(f"Несоответствие кэша и дерева: {cached_ids - tree_ids}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации целостности: {e}")
            return False
    
    def _collect_tree_ids(self, node: QuadTreeNode, ids: Set[str]) -> None:
        """Собрать все ID из дерева"""
        for obj in node.objects:
            ids.add(obj.id)
        
        if not node.is_leaf:
            for child in node.children:
                if child:
                    self._collect_tree_ids(child, ids)


# Утилитарные функции
def create_bounding_box_from_center(center_x: float, center_y: float, 
                                   width: float, height: float) -> BoundingBox:
    """Создать ограничивающий прямоугольник от центра"""
    return BoundingBox(
        center_x - width / 2,
        center_y - height / 2,
        width, height
    )


def create_bounding_box_from_circle(center_x: float, center_y: float, 
                                   radius: float) -> BoundingBox:
    """Создать ограничивающий прямоугольник для круга"""
    diameter = radius * 2
    return BoundingBox(
        center_x - radius,
        center_y - radius,
        diameter, diameter
    )
