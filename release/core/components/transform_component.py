"""
Компонент для управления позицией и трансформацией сущностей
"""

import math
from typing import Tuple, Optional
from dataclasses import dataclass
from .base_component import BaseComponent
import logging

logger = logging.getLogger(__name__)


@dataclass
class Vector3:
    """3D вектор для позиции"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def distance_to(self, other: 'Vector3') -> float:
        """Расчет расстояния до другой позиции"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def move_towards(self, target: 'Vector3', speed: float, delta_time: float) -> None:
        """Движение к целевой позиции"""
        dx = target.x - self.x
        dy = target.y - self.y
        dz = target.z - self.z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        if distance > 0:
            move_distance = speed * delta_time
            if move_distance >= distance:
                self.x = target.x
                self.y = target.y
                self.z = target.z
            else:
                factor = move_distance / distance
                self.x += dx * factor
                self.y += dy * factor
                self.z += dz * factor
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """Преобразование в кортеж"""
        return (self.x, self.y, self.z)
    
    @classmethod
    def from_tuple(cls, pos_tuple: Tuple[float, float, float]) -> 'Vector3':
        """Создание из кортежа"""
        return cls(pos_tuple[0], pos_tuple[1], pos_tuple[2])


class TransformComponent(BaseComponent):
    """
    Компонент для управления позицией, поворотом и масштабом сущности.
    Отвечает только за трансформацию.
    """
    
    def __init__(self, entity_id: str, position: Vector3 = None, rotation: float = 0.0, scale: float = 1.0):
        super().__init__(entity_id)
        self.position = position or Vector3()
        self.rotation = rotation  # В радианах
        self.scale = scale
        
        # Кэш для оптимизации
        self._last_position = Vector3()
        self._has_moved = False
    
    def _initialize(self) -> bool:
        """Инициализация компонента трансформации"""
        self._last_position = Vector3(self.position.x, self.position.y, self.position.z)
        return True
    
    def _update(self, delta_time: float) -> None:
        """Обновление компонента трансформации"""
        # Проверяем, изменилась ли позиция
        if (self.position.x != self._last_position.x or 
            self.position.y != self._last_position.y or 
            self.position.z != self._last_position.z):
            self._has_moved = True
            self._last_position = Vector3(self.position.x, self.position.y, self.position.z)
        else:
            self._has_moved = False
    
    def set_position(self, x: float, y: float, z: float = 0.0) -> None:
        """Установка позиции"""
        self.position.x = x
        self.position.y = y
        self.position.z = z
    
    def set_position_vector(self, position: Vector3) -> None:
        """Установка позиции через вектор"""
        self.position = position
    
    def move(self, dx: float, dy: float, dz: float = 0.0) -> None:
        """Перемещение на указанное расстояние"""
        self.position.x += dx
        self.position.y += dy
        self.position.z += dz
    
    def set_rotation(self, rotation: float) -> None:
        """Установка поворота в радианах"""
        self.rotation = rotation
    
    def rotate(self, angle: float) -> None:
        """Поворот на указанный угол в радианах"""
        self.rotation += angle
    
    def set_scale(self, scale: float) -> None:
        """Установка масштаба"""
        self.scale = scale
    
    def get_position(self) -> Vector3:
        """Получение позиции"""
        return Vector3(self.position.x, self.position.y, self.position.z)
    
    def get_position_2d(self) -> Tuple[float, float]:
        """Получение 2D позиции (x, y)"""
        return (self.position.x, self.position.y)
    
    def get_rotation_degrees(self) -> float:
        """Получение поворота в градусах"""
        return math.degrees(self.rotation)
    
    def distance_to(self, other_transform: 'TransformComponent') -> float:
        """Расстояние до другой сущности"""
        return self.position.distance_to(other_transform.position)
    
    def move_towards(self, target_transform: 'TransformComponent', speed: float, delta_time: float) -> None:
        """Движение к другой сущности"""
        self.position.move_towards(target_transform.position, speed, delta_time)
    
    def has_moved(self) -> bool:
        """Проверка, изменилась ли позиция с последнего обновления"""
        return self._has_moved
    
    def get_data(self) -> dict:
        """Получение данных для сериализации"""
        data = super().get_data()
        data.update({
            'position': self.position.to_tuple(),
            'rotation': self.rotation,
            'scale': self.scale
        })
        return data
    
    def set_data(self, data: dict) -> bool:
        """Установка данных из сериализованного состояния"""
        if not super().set_data(data):
            return False
        
        try:
            if 'position' in data:
                self.position = Vector3.from_tuple(data['position'])
            if 'rotation' in data:
                self.rotation = data['rotation']
            if 'scale' in data:
                self.scale = data['scale']
            return True
        except Exception as e:
            logger.error(f"Ошибка установки данных TransformComponent: {e}")
            return False
