#!/usr/bin/env python3
"""
Система управления игровым миром - режим "Творец мира"
Управляет объектами, созданными пользователем
"""

import logging
import time
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import (
    StatType, BASE_STATS, PROBABILITY_CONSTANTS, 
    TIME_CONSTANTS, SYSTEM_LIMITS, WorldObjectType, ObjectState
)

logger = logging.getLogger(__name__)

@dataclass
class WorldObject:
    """Объект в игровом мире"""
    object_id: str
    template_id: str
    object_type: WorldObjectType
    name: str
    x: float
    y: float
    z: float
    width: float
    height: float
    depth: float
    color: Tuple[float, float, float, float]
    state: ObjectState = ObjectState.ACTIVE
    properties: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "user"
    creation_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    node: Any = None  # Panda3D узел

@dataclass
class WorldGrid:
    """Сетка мира для размещения объектов"""
    grid_size: float = 1.0
    width: int = 100
    height: int = 100
    cells: Dict[Tuple[int, int], List[str]] = field(default_factory=dict)

class WorldManager(ISystem):
    """Менеджер игрового мира"""
    
    def __init__(self):
        self._system_name = "world_manager"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Объекты в мире
        self.world_objects: Dict[str, WorldObject] = {}
        
        # Сетка мира
        self.world_grid = WorldGrid()
        
        # Статистика мира
        self.world_stats = {
            'total_objects': 0,
            'active_objects': 0,
            'obstacles_count': 0,
            'traps_count': 0,
            'chests_count': 0,
            'enemies_count': 0,
            'world_size': (0, 0),
            'update_time': 0.0
        }
        
        # Настройки мира
        self.world_settings = {
            'max_objects': 1000,
            'world_bounds': (-50, 50, -50, 50),
            'collision_enabled': True,
            'physics_enabled': True,
            'weather_enabled': False
        }
        
        # Panda3D компоненты
        self.world_root = None
        self.objects_root = None
        
        logger.info("Менеджер игрового мира инициализирован")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация менеджера мира"""
        try:
            logger.info("Инициализация менеджера игрового мира...")
            
            # Настройка Panda3D узлов
            self._setup_world_nodes()
            
            # Инициализация сетки
            self._initialize_grid()
            
            self._system_state = SystemState.READY
            logger.info("Менеджер игрового мира успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера мира: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление менеджера мира"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем объекты мира
            self._update_world_objects(delta_time)
            
            # Обновляем сетку
            self._update_grid()
            
            # Обновляем статистику
            self._update_world_stats()
            
            self.world_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления менеджера мира: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка менеджера мира"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Менеджер мира приостановлен")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки менеджера мира: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление менеджера мира"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Менеджер мира возобновлен")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления менеджера мира: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка менеджера мира"""
        try:
            logger.info("Очистка менеджера игрового мира...")
            
            # Очищаем объекты
            self.world_objects.clear()
            
            # Очищаем сетку
            self.world_grid.cells.clear()
            
            # Сбрасываем статистику
            self.world_stats = {
                'total_objects': 0,
                'active_objects': 0,
                'obstacles_count': 0,
                'traps_count': 0,
                'chests_count': 0,
                'enemies_count': 0,
                'world_size': (0, 0),
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Менеджер игрового мира очищен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки менеджера мира: {e}")
            return False
    
    def _setup_world_nodes(self) -> None:
        """Настройка Panda3D узлов мира"""
        try:
            # Здесь должна быть инициализация Panda3D узлов
            logger.debug("Panda3D узлы мира настроены")
        except Exception as e:
            logger.warning(f"Не удалось настроить Panda3D узлы мира: {e}")
    
    def _initialize_grid(self) -> None:
        """Инициализация сетки мира"""
        try:
            # Создаем пустую сетку
            for x in range(self.world_grid.width):
                for y in range(self.world_grid.height):
                    self.world_grid.cells[(x, y)] = []
            
            logger.debug("Сетка мира инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации сетки: {e}")
    
    def _update_world_objects(self, delta_time: float) -> None:
        """Обновление объектов мира"""
        try:
            current_time = time.time()
            
            for object_id, world_object in self.world_objects.items():
                # Обновляем время последнего обновления
                world_object.last_update = current_time
                
                # Обновляем Panda3D узел
                if world_object.node:
                    world_object.node.setPos(world_object.x, world_object.y, world_object.z)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления объектов мира: {e}")
    
    def _update_grid(self) -> None:
        """Обновление сетки мира"""
        try:
            # Очищаем сетку
            for cell in self.world_grid.cells.values():
                cell.clear()
            
            # Размещаем объекты по сетке
            for object_id, world_object in self.world_objects.items():
                if world_object.state == ObjectState.ACTIVE:
                    grid_x = int(world_object.x / self.world_grid.grid_size)
                    grid_y = int(world_object.y / self.world_grid.grid_size)
                    
                    if (grid_x, grid_y) in self.world_grid.cells:
                        self.world_grid.cells[(grid_x, grid_y)].append(object_id)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления сетки: {e}")
    
    def _update_world_stats(self) -> None:
        """Обновление статистики мира"""
        try:
            self.world_stats['total_objects'] = len(self.world_objects)
            self.world_stats['active_objects'] = len([obj for obj in self.world_objects.values() if obj.state == ObjectState.ACTIVE])
            self.world_stats['obstacles_count'] = len([obj for obj in self.world_objects.values() if obj.object_type == WorldObjectType.OBSTACLE])
            self.world_stats['traps_count'] = len([obj for obj in self.world_objects.values() if obj.object_type == WorldObjectType.TRAP])
            self.world_stats['chests_count'] = len([obj for obj in self.world_objects.values() if obj.object_type == WorldObjectType.CHEST])
            self.world_stats['enemies_count'] = len([obj for obj in self.world_objects.values() if obj.object_type == WorldObjectType.ENEMY])
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики мира: {e}")
    
    def add_world_object(self, object_data: Dict[str, Any]) -> Optional[str]:
        """Добавление объекта в мир"""
        try:
            if len(self.world_objects) >= self.world_settings['max_objects']:
                logger.warning("Достигнут лимит объектов в мире")
                return None
            
            # Создаем объект мира
            world_object = WorldObject(
                object_id=object_data['id'],
                template_id=object_data['template_id'],
                object_type=WorldObjectType(object_data['type']),
                name=object_data['name'],
                x=object_data['x'],
                y=object_data['y'],
                z=object_data['z'],
                width=object_data['properties'].get('width', 1.0),
                height=object_data['properties'].get('height', 1.0),
                depth=object_data['properties'].get('depth', 1.0),
                color=object_data['properties'].get('color', (1.0, 1.0, 1.0, 1.0)),
                properties=object_data['properties'],
                created_by=object_data.get('created_by', 'user'),
                creation_time=object_data.get('creation_time', time.time())
            )
            
            # Создаем Panda3D узел
            if self.objects_root:
                world_object.node = self._create_object_node(world_object)
            
            # Добавляем в мир
            self.world_objects[world_object.object_id] = world_object
            
            logger.info(f"Добавлен объект в мир: {world_object.name} в позиции ({world_object.x}, {world_object.y}, {world_object.z})")
            return world_object.object_id
            
        except Exception as e:
            logger.error(f"Ошибка добавления объекта в мир: {e}")
            return None
    
    def remove_world_object(self, object_id: str) -> bool:
        """Удаление объекта из мира"""
        try:
            if object_id not in self.world_objects:
                return False
            
            world_object = self.world_objects[object_id]
            
            # Удаляем Panda3D узел
            if world_object.node:
                world_object.node.removeNode()
            
            # Удаляем из мира
            del self.world_objects[object_id]
            
            logger.info(f"Удален объект из мира: {world_object.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления объекта из мира: {e}")
            return False
    
    def get_objects_at_position(self, x: float, y: float, radius: float = 1.0) -> List[WorldObject]:
        """Получение объектов в заданной позиции"""
        try:
            objects = []
            
            for world_object in self.world_objects.values():
                if world_object.state != ObjectState.ACTIVE:
                    continue
                
                distance = math.sqrt((world_object.x - x)**2 + (world_object.y - y)**2)
                if distance <= radius:
                    objects.append(world_object)
            
            return objects
            
        except Exception as e:
            logger.error(f"Ошибка получения объектов в позиции: {e}")
            return []
    
    def get_objects_by_type(self, object_type: WorldObjectType) -> List[WorldObject]:
        """Получение объектов по типу"""
        try:
            return [obj for obj in self.world_objects.values() if obj.object_type == object_type]
        except Exception as e:
            logger.error(f"Ошибка получения объектов по типу: {e}")
            return []
    
    def check_collision(self, x: float, y: float, width: float, height: float) -> List[WorldObject]:
        """Проверка коллизий"""
        try:
            if not self.world_settings['collision_enabled']:
                return []
            
            colliding_objects = []
            
            for world_object in self.world_objects.values():
                if world_object.state != ObjectState.ACTIVE:
                    continue
                
                # Проверяем коллизию прямоугольников
                if (x < world_object.x + world_object.width and
                    x + width > world_object.x and
                    y < world_object.y + world_object.depth and
                    y + height > world_object.y):
                    colliding_objects.append(world_object)
            
            return colliding_objects
            
        except Exception as e:
            logger.error(f"Ошибка проверки коллизий: {e}")
            return []
    
    def _create_object_node(self, world_object: WorldObject) -> Any:
        """Создание Panda3D узла для объекта"""
        try:
            # Здесь должна быть логика создания Panda3D узла
            # Пока возвращаем None
            return None
        except Exception as e:
            logger.warning(f"Не удалось создать Panda3D узел для объекта {world_object.object_id}: {e}")
            return None
    
    def get_world_stats(self) -> Dict[str, Any]:
        """Получение статистики мира"""
        return self.world_stats.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'total_objects': len(self.world_objects),
            'active_objects': len([obj for obj in self.world_objects.values() if obj.state == ObjectState.ACTIVE]),
            'world_stats': self.world_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "object_created":
                return self.add_world_object(event_data) is not None
            elif event_type == "object_destroyed":
                object_id = event_data.get('object_id')
                return self.remove_world_object(object_id) if object_id else False
            elif event_type == "object_moved":
                object_id = event_data.get('object_id')
                new_x = event_data.get('x')
                new_y = event_data.get('y')
                new_z = event_data.get('z')
                
                if object_id and object_id in self.world_objects:
                    world_object = self.world_objects[object_id]
                    world_object.x = new_x
                    world_object.y = new_y
                    world_object.z = new_z
                    return True
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
