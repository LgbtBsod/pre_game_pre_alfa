"""
Компонент для управления анимацией сущностей
Отвечает только за управление анимацией, не за загрузку ресурсов или отрисовку
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from .base_component import BaseComponent
import logging

logger = logging.getLogger(__name__)


class AnimationState(Enum):
    """Состояния анимации"""
    IDLE = "idle"
    WALKING = "walk"
    ATTACKING = "attack"
    DEAD = "dead"


class Direction(Enum):
    """Направления движения"""
    DOWN = "down"
    UP = "up"
    LEFT = "left"
    RIGHT = "right"


class AnimationController:
    """
    Контроллер анимации.
    Отвечает только за управление состоянием анимации.
    """
    
    def __init__(self):
        self.current_animation = "down_idle"
        self.current_frame = 0
        self.animation_speed = 0.15  # Секунды на кадр
        self.frame_timer = 0
        self.is_playing = True
        self.loop = True
        self.direction = Direction.DOWN
        self.state = AnimationState.IDLE
    
    def set_animation(self, animation_name: str, reset: bool = True) -> None:
        """Установка текущей анимации"""
        if self.current_animation != animation_name or reset:
            self.current_animation = animation_name
            self.current_frame = 0
            self.frame_timer = 0
            logger.debug(f"Установлена анимация: {animation_name}")
    
    def set_direction_animation(self, direction: Direction, state: AnimationState) -> None:
        """Установка анимации по направлению и состоянию"""
        self.direction = direction
        self.state = state
        animation_name = f"{direction.value}_{state.value}"
        self.set_animation(animation_name)
    
    def update(self, delta_time: float, total_frames: int) -> None:
        """Обновление анимации"""
        if not self.is_playing or total_frames == 0:
            return
        
        self.frame_timer += delta_time
        
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            
            if self.current_frame < total_frames - 1:
                self.current_frame += 1
            elif self.loop:
                self.current_frame = 0
    
    def get_current_frame_index(self) -> int:
        """Получение индекса текущего кадра"""
        return self.current_frame
    
    def is_animation_finished(self) -> bool:
        """Проверка завершения анимации"""
        return self.current_frame >= 0 and not self.loop
    
    def pause(self) -> None:
        """Приостановка анимации"""
        self.is_playing = False
    
    def resume(self) -> None:
        """Возобновление анимации"""
        self.is_playing = True
    
    def reset(self) -> None:
        """Сброс анимации к началу"""
        self.current_frame = 0
        self.frame_timer = 0
    
    def set_animation_speed(self, speed: float) -> None:
        """Установка скорости анимации"""
        self.animation_speed = max(0.01, speed)  # Минимум 0.01 секунды на кадр
    
    def set_loop(self, loop: bool) -> None:
        """Установка зацикливания анимации"""
        self.loop = loop


class AnimationComponent(BaseComponent):
    """
    Компонент для управления анимацией сущности.
    Отвечает только за управление анимацией, не за загрузку ресурсов.
    """
    
    def __init__(self, entity_id: str, sprite_path: str = "graphics/player"):
        super().__init__(entity_id)
        self.sprite_path = sprite_path
        self.controller = AnimationController()
        
        # Ссылка на ресурсы (будет установлена извне)
        self._animation_resources = {}
        self._resource_loader = None
    
    def _initialize(self) -> bool:
        """Инициализация компонента анимации"""
        # Компонент анимации не загружает ресурсы самостоятельно
        # Ресурсы должны быть загружены через ResourceLoader
        return True
    
    def set_resource_loader(self, resource_loader) -> None:
        """Установка загрузчика ресурсов"""
        self._resource_loader = resource_loader
    
    def set_animation_resources(self, resources: Dict[str, List]) -> None:
        """Установка ресурсов анимации"""
        self._animation_resources = resources
    
    def get_animation_resources(self) -> Dict[str, List]:
        """Получение ресурсов анимации"""
        return self._animation_resources
    
    def _update(self, delta_time: float) -> None:
        """Обновление компонента анимации"""
        if self._animation_resources:
            current_animation = self.controller.current_animation
            if current_animation in self._animation_resources:
                total_frames = len(self._animation_resources[current_animation])
                self.controller.update(delta_time, total_frames)
    
    def set_direction(self, direction: Direction) -> None:
        """Установка направления"""
        self.controller.set_direction_animation(direction, self.controller.state)
    
    def set_state(self, state: AnimationState) -> None:
        """Установка состояния"""
        self.controller.set_direction_animation(self.controller.direction, state)
    
    def set_animation(self, animation_name: str, reset: bool = True) -> None:
        """Установка анимации по имени"""
        self.controller.set_animation(animation_name, reset)
    
    def get_current_frame_index(self) -> int:
        """Получение индекса текущего кадра"""
        return self.controller.get_current_frame_index()
    
    def get_current_animation_name(self) -> str:
        """Получение имени текущей анимации"""
        return self.controller.current_animation
    
    def is_playing(self) -> bool:
        """Проверка, воспроизводится ли анимация"""
        return self.controller.is_playing
    
    def pause(self) -> None:
        """Приостановка анимации"""
        self.controller.pause()
    
    def resume(self) -> None:
        """Возобновление анимации"""
        self.controller.resume()
    
    def reset(self) -> None:
        """Сброс анимации"""
        self.controller.reset()
    
    def set_animation_speed(self, speed: float) -> None:
        """Установка скорости анимации"""
        self.controller.set_animation_speed(speed)
    
    def set_loop(self, loop: bool) -> None:
        """Установка зацикливания"""
        self.controller.set_loop(loop)
    
    def is_animation_finished(self) -> bool:
        """Проверка завершения анимации"""
        return self.controller.is_animation_finished()
    
    def get_data(self) -> dict:
        """Получение данных для сериализации"""
        data = super().get_data()
        data.update({
            'current_animation': self.controller.current_animation,
            'current_frame': self.controller.current_frame,
            'animation_speed': self.controller.animation_speed,
            'frame_timer': self.controller.frame_timer,
            'is_playing': self.controller.is_playing,
            'loop': self.controller.loop,
            'direction': self.controller.direction.value,
            'state': self.controller.state.value
        })
        return data
    
    def set_data(self, data: dict) -> bool:
        """Установка данных из сериализованного состояния"""
        if not super().set_data(data):
            return False
        
        try:
            if 'current_animation' in data:
                self.controller.current_animation = data['current_animation']
            if 'current_frame' in data:
                self.controller.current_frame = data['current_frame']
            if 'animation_speed' in data:
                self.controller.animation_speed = data['animation_speed']
            if 'frame_timer' in data:
                self.controller.frame_timer = data['frame_timer']
            if 'is_playing' in data:
                self.controller.is_playing = data['is_playing']
            if 'loop' in data:
                self.controller.loop = data['loop']
            if 'direction' in data:
                self.controller.direction = Direction(data['direction'])
            if 'state' in data:
                self.controller.state = AnimationState(data['state'])
            return True
        except Exception as e:
            logger.error(f"Ошибка установки данных AnimationComponent: {e}")
            return False
