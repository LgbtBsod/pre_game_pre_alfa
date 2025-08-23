"""
Компонент для отрисовки спрайтов
Отвечает только за отрисовку, не за управление анимацией или загрузку ресурсов
"""

from typing import Optional, Tuple, Dict, List
from .base_component import BaseComponent
import logging

# Условный импорт pygame
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    pygame = None

logger = logging.getLogger(__name__)


class SpriteRenderer:
    """
    Рендерер спрайтов.
    Отвечает только за отрисовку спрайтов на экране.
    """
    
    def __init__(self):
        self.visible = True
        self.alpha = 255  # Прозрачность (0-255)
        self.color_mod = (255, 255, 255)  # Модификатор цвета
        self.flip_horizontal = False
        self.flip_vertical = False
    
    def render(self, surface: pygame.Surface, sprite: pygame.Surface, 
               position: Tuple[float, float], scale: float = 1.0, 
               rotation: float = 0.0) -> None:
        """
        Отрисовка спрайта на поверхности
        
        Args:
            surface: Поверхность для отрисовки
            sprite: Спрайт для отрисовки
            position: Позиция (x, y)
            scale: Масштаб
            rotation: Поворот в радианах
        """
        if not self.visible or not PYGAME_AVAILABLE or sprite is None:
            return
        
        try:
            # Создаем копию спрайта для модификации
            render_sprite = sprite.copy()
            
            # Применяем модификаторы
            if self.alpha != 255:
                render_sprite.set_alpha(self.alpha)
            
            if self.color_mod != (255, 255, 255):
                render_sprite.fill(self.color_mod, special_flags=pygame.BLEND_MULT)
            
            # Применяем отражения
            if self.flip_horizontal or self.flip_vertical:
                render_sprite = pygame.transform.flip(
                    render_sprite, 
                    self.flip_horizontal, 
                    self.flip_vertical
                )
            
            # Применяем масштаб
            if scale != 1.0:
                original_size = render_sprite.get_size()
                new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                render_sprite = pygame.transform.scale(render_sprite, new_size)
            
            # Применяем поворот
            if rotation != 0.0:
                render_sprite = pygame.transform.rotate(render_sprite, rotation)
            
            # Получаем прямоугольник для позиционирования
            rect = render_sprite.get_rect()
            rect.center = position
            
            # Отрисовываем
            surface.blit(render_sprite, rect)
            
        except Exception as e:
            logger.error(f"Ошибка отрисовки спрайта: {e}")
    
    def set_visibility(self, visible: bool) -> None:
        """Установка видимости"""
        self.visible = visible
    
    def set_alpha(self, alpha: int) -> None:
        """Установка прозрачности (0-255)"""
        self.alpha = max(0, min(255, alpha))
    
    def set_color_mod(self, color: Tuple[int, int, int]) -> None:
        """Установка модификатора цвета"""
        self.color_mod = tuple(max(0, min(255, c)) for c in color)
    
    def set_flip(self, horizontal: bool = False, vertical: bool = False) -> None:
        """Установка отражения"""
        self.flip_horizontal = horizontal
        self.flip_vertical = vertical


class SpriteComponent(BaseComponent):
    """
    Компонент для отрисовки спрайтов сущности.
    Отвечает только за отрисовку, не за управление анимацией.
    """
    
    def __init__(self, entity_id: str):
        super().__init__(entity_id)
        self.renderer = SpriteRenderer()
        
        # Ссылки на другие компоненты (будут установлены извне)
        self._transform_component = None
        self._animation_component = None
        
        # Ресурсы спрайтов (будут установлены извне)
        self._sprite_resources = {}
        self._current_sprite = None
    
    def _initialize(self) -> bool:
        """Инициализация компонента спрайта"""
        return True
    
    def set_transform_component(self, transform_component) -> None:
        """Установка компонента трансформации"""
        self._transform_component = transform_component
    
    def set_animation_component(self, animation_component) -> None:
        """Установка компонента анимации"""
        self._animation_component = animation_component
    
    def set_sprite_resources(self, resources: Dict[str, List]) -> None:
        """Установка ресурсов спрайтов"""
        self._sprite_resources = resources
    
    def get_current_sprite(self) -> Optional[pygame.Surface]:
        """Получение текущего спрайта для отрисовки"""
        if not self._animation_component or not self._sprite_resources:
            return self._current_sprite
        
        try:
            current_animation = self._animation_component.get_current_animation_name()
            current_frame = self._animation_component.get_current_frame_index()
            
            if current_animation in self._sprite_resources:
                frames = self._sprite_resources[current_animation]
                if 0 <= current_frame < len(frames):
                    return frames[current_frame]
            
            return self._current_sprite
            
        except Exception as e:
            logger.error(f"Ошибка получения текущего спрайта: {e}")
            return self._current_sprite
    
    def set_static_sprite(self, sprite: pygame.Surface) -> None:
        """Установка статического спрайта (без анимации)"""
        self._current_sprite = sprite
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """
        Отрисовка спрайта
        
        Args:
            surface: Поверхность для отрисовки
            camera_offset: Смещение камеры (x, y)
        """
        if not self._transform_component:
            return
        
        # Получаем текущий спрайт
        sprite = self.get_current_sprite()
        if not sprite:
            return
        
        # Получаем позицию из компонента трансформации
        position_2d = self._transform_component.get_position_2d()
        adjusted_position = (
            position_2d[0] - camera_offset[0],
            position_2d[1] - camera_offset[1]
        )
        
        # Получаем параметры трансформации
        scale = self._transform_component.scale
        rotation = self._transform_component.get_rotation_degrees()
        
        # Отрисовываем
        self.renderer.render(surface, sprite, adjusted_position, scale, rotation)
    
    def get_rect(self, camera_offset: Tuple[float, float] = (0, 0)) -> Optional[pygame.Rect]:
        """Получение прямоугольника спрайта"""
        if not self._transform_component:
            return None
        
        sprite = self.get_current_sprite()
        if not sprite:
            return None
        
        try:
            rect = sprite.get_rect()
            position_2d = self._transform_component.get_position_2d()
            rect.center = (
                position_2d[0] - camera_offset[0],
                position_2d[1] - camera_offset[1]
            )
            return rect
        except Exception as e:
            logger.error(f"Ошибка получения прямоугольника спрайта: {e}")
            return None
    
    def set_visibility(self, visible: bool) -> None:
        """Установка видимости"""
        self.renderer.set_visibility(visible)
    
    def set_alpha(self, alpha: int) -> None:
        """Установка прозрачности"""
        self.renderer.set_alpha(alpha)
    
    def set_color_mod(self, color: Tuple[int, int, int]) -> None:
        """Установка модификатора цвета"""
        self.renderer.set_color_mod(color)
    
    def set_flip(self, horizontal: bool = False, vertical: bool = False) -> None:
        """Установка отражения"""
        self.renderer.set_flip(horizontal, vertical)
    
    def is_visible(self) -> bool:
        """Проверка видимости"""
        return self.renderer.visible
    
    def get_data(self) -> dict:
        """Получение данных для сериализации"""
        data = super().get_data()
        data.update({
            'visible': self.renderer.visible,
            'alpha': self.renderer.alpha,
            'color_mod': self.renderer.color_mod,
            'flip_horizontal': self.renderer.flip_horizontal,
            'flip_vertical': self.renderer.flip_vertical
        })
        return data
    
    def set_data(self, data: dict) -> bool:
        """Установка данных из сериализованного состояния"""
        if not super().set_data(data):
            return False
        
        try:
            if 'visible' in data:
                self.renderer.visible = data['visible']
            if 'alpha' in data:
                self.renderer.alpha = data['alpha']
            if 'color_mod' in data:
                self.renderer.color_mod = tuple(data['color_mod'])
            if 'flip_horizontal' in data:
                self.renderer.flip_horizontal = data['flip_horizontal']
            if 'flip_vertical' in data:
                self.renderer.flip_vertical = data['flip_vertical']
            return True
        except Exception as e:
            logger.error(f"Ошибка установки данных SpriteComponent: {e}")
            return False
