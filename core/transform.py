"""Компонент для управления позицией и движением сущности."""

from typing import Dict, Any, Optional, Tuple, List
import math
from .component import Component


class TransformComponent(Component):
    """Компонент для управления позицией и движением."""

    def __init__(self, entity):
        super().__init__(entity)
        self.position = [0.0, 0.0]  # [x, y]
        self.rotation = 0.0  # в радианах
        self.scale = [1.0, 1.0]  # [x, y]
        self.velocity = [0.0, 0.0]  # [x, y]
        self.target_position = None
        self.movement_speed = 100.0
        self.rotation_speed = 2.0  # радиан в секунду
        self.is_moving = False
        self.path: List[Tuple[float, float]] = []
        self.current_path_index = 0

    def set_position(self, x: float, y: float) -> None:
        """Установить позицию."""
        self.position[0] = x
        self.position[1] = y

    def get_position(self) -> Tuple[float, float]:
        """Получить текущую позицию."""
        return tuple(self.position)

    def get_x(self) -> float:
        """Получить X координату."""
        return self.position[0]

    def get_y(self) -> float:
        """Получить Y координату."""
        return self.position[1]

    def set_rotation(self, rotation: float) -> None:
        """Установить поворот."""
        self.rotation = rotation

    def get_rotation(self) -> float:
        """Получить текущий поворот."""
        return self.rotation

    def set_scale(self, x: float, y: float) -> None:
        """Установить масштаб."""
        self.scale[0] = x
        self.scale[1] = y

    def get_scale(self) -> Tuple[float, float]:
        """Получить текущий масштаб."""
        return tuple(self.scale)

    def set_velocity(self, x: float, y: float) -> None:
        """Установить скорость."""
        self.velocity[0] = x
        self.velocity[1] = y

    def get_velocity(self) -> Tuple[float, float]:
        """Получить текущую скорость."""
        return tuple(self.velocity)

    def set_movement_speed(self, speed: float) -> None:
        """Установить скорость движения."""
        self.movement_speed = speed

    def move_towards(self, target_pos: Tuple[float, float], delta_time: float) -> bool:
        """Двигаться к цели."""
        if not target_pos:
            return False

        target_x, target_y = target_pos
        current_x, current_y = self.position

        # Вычисляем направление
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 1.0:  # Достигли цели
            self.position[0] = target_x
            self.position[1] = target_y
            self.velocity = [0.0, 0.0]
            self.is_moving = False
            return True

        # Нормализуем направление и применяем скорость
        if distance > 0:
            dx /= distance
            dy /= distance

        # Вычисляем новую позицию
        move_distance = self.movement_speed * delta_time
        new_x = current_x + dx * move_distance
        new_y = current_y + dy * move_distance

        # Обновляем позицию
        self.position[0] = new_x
        self.position[1] = new_y

        # Обновляем скорость для анимации
        self.velocity[0] = dx * self.movement_speed
        self.velocity[1] = dy * self.movement_speed

        # Обновляем поворот в направлении движения
        if abs(dx) > 0.001 or abs(dy) > 0.001:
            target_rotation = math.atan2(dy, dx)
            self._rotate_towards(target_rotation, delta_time)

        self.is_moving = True
        return False

    def move_by(self, dx: float, dy: float, delta_time: float) -> None:
        """Двигаться на указанное расстояние."""
        move_distance = self.movement_speed * delta_time
        self.position[0] += dx * move_distance
        self.position[1] += dy * move_distance

    def set_target_position(self, target_pos: Tuple[float, float]) -> None:
        """Установить цель для движения."""
        self.target_position = target_pos
        self.is_moving = True

    def clear_target_position(self) -> None:
        """Очистить цель движения."""
        self.target_position = None
        self.is_moving = False
        self.velocity = [0.0, 0.0]

    def set_path(self, path: List[Tuple[float, float]]) -> None:
        """Установить путь для следования."""
        self.path = path.copy()
        self.current_path_index = 0
        if self.path:
            self.set_target_position(self.path[0])

    def follow_path(self, delta_time: float) -> bool:
        """Следовать по установленному пути."""
        if not self.path or self.current_path_index >= len(self.path):
            return True

        current_target = self.path[self.current_path_index]
        if self.move_towards(current_target, delta_time):
            # Достигли текущей точки пути
            self.current_path_index += 1
            if self.current_path_index < len(self.path):
                # Переходим к следующей точке
                self.set_target_position(self.path[self.current_path_index])
            else:
                # Достигли конца пути
                self.clear_target_position()
                return True

        return False

    def _rotate_towards(self, target_rotation: float, delta_time: float) -> None:
        """Повернуться к цели."""
        # Нормализуем углы
        current_rot = self.rotation % (2 * math.pi)
        target_rot = target_rotation % (2 * math.pi)

        # Вычисляем кратчайший путь поворота
        angle_diff = target_rot - current_rot

        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        # Применяем поворот
        max_rotation = self.rotation_speed * delta_time
        if abs(angle_diff) <= max_rotation:
            self.rotation = target_rot
        else:
            if angle_diff > 0:
                self.rotation += max_rotation
            else:
                self.rotation -= max_rotation

        self.rotation %= 2 * math.pi

    def distance_to(self, target_pos: Tuple[float, float]) -> float:
        """Вычислить расстояние до цели."""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        return math.sqrt(dx * dx + dy * dy)

    def distance_to_entity(self, other_entity) -> float:
        """Вычислить расстояние до другой сущности."""
        if hasattr(other_entity, "get_component"):
            transform = other_entity.get_component("TransformComponent")
            if transform:
                return self.distance_to(transform.get_position())
        return float("inf")

    def is_near(self, target_pos: Tuple[float, float], radius: float) -> bool:
        """Проверить, находится ли цель в радиусе."""
        return self.distance_to(target_pos) <= radius

    def get_direction_to(self, target_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Получить направление к цели."""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            return (dx / distance, dy / distance)
        return (0.0, 0.0)

    def _on_initialize(self) -> None:
        """Инициализация компонента."""
        pass

    def _on_update(self, delta_time: float) -> None:
        """Обновление компонента."""
        # Автоматически следовать к цели, если она установлена
        if self.target_position:
            self.move_towards(self.target_position, delta_time)
        elif self.path:
            self.follow_path(delta_time)

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь."""
        data = super().to_dict()
        data.update(
            {
                "position": self.position.copy(),
                "rotation": self.rotation,
                "scale": self.scale.copy(),
                "velocity": self.velocity.copy(),
                "target_position": self.target_position,
                "movement_speed": self.movement_speed,
                "rotation_speed": self.rotation_speed,
                "is_moving": self.is_moving,
                "path": self.path.copy(),
                "current_path_index": self.current_path_index,
            }
        )
        return data

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализация из словаря."""
        super().from_dict(data)

        self.position = data.get("position", [0.0, 0.0]).copy()
        self.rotation = data.get("rotation", 0.0)
        self.scale = data.get("scale", [1.0, 1.0]).copy()
        self.velocity = data.get("velocity", [0.0, 0.0]).copy()
        self.target_position = data.get("target_position")
        self.movement_speed = data.get("movement_speed", 100.0)
        self.rotation_speed = data.get("rotation_speed", 2.0)
        self.is_moving = data.get("is_moving", False)
        self.path = data.get("path", []).copy()
        self.current_path_index = data.get("current_path_index", 0)
