"""Базовые интерфейсы для системы игры."""

from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any, List, Tuple, Optional
from dataclasses import dataclass


class Position(Protocol):
    """Протокол для позиции в 2D пространстве."""

    x: float
    y: float


class Damageable(Protocol):
    """Протокол для объектов, которые могут получать урон."""

    health: float
    max_health: float

    def take_damage(self, damage: float) -> None:
        """Получить урон."""
        ...


class Attacker(Protocol):
    """Протокол для объектов, которые могут атаковать."""

    damage_output: float
    attack_speed: float

    def attack(self, target: Damageable) -> None:
        """Атаковать цель."""
        ...


class Movable(Protocol):
    """Протокол для объектов, которые могут двигаться."""

    position: Position
    movement_speed: float

    def move_towards(self, target: Position, delta_time: float) -> None:
        """Двигаться к цели."""
        ...


class Updatable(ABC):
    """Абстрактный базовый класс для объектов, которые обновляются каждый кадр."""

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Обновить состояние объекта."""
        pass


class Renderable(ABC):
    """Абстрактный базовый класс для объектов, которые отрисовываются."""

    @abstractmethod
    def render(self, canvas, camera_position: Tuple[float, float]) -> None:
        """Отрисовать объект на канвасе."""
        pass


class Saveable(ABC):
    """Абстрактный базовый класс для объектов, которые можно сохранить/загрузить."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь для сохранения."""
        pass

    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Загрузить объект из словаря."""
        pass


@dataclass
class GameState:
    """Состояние игры."""

    is_paused: bool = False
    is_menu_shown: bool = True
    current_level: int = 1
    game_time: float = 0.0
    victory_achieved: bool = False


@dataclass
class GameSettings:
    """Настройки игры."""

    difficulty: str = "normal"
    learning_rate: float = 1.0
    window_width: int = 1200
    window_height: int = 800
    tile_size: int = 40
    fps_limit: int = 60
