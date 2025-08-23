"""
Кнопки для pygame интерфейса
"""

import pygame
import logging
from typing import Callable, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class Button:
    """Кнопка для pygame интерфейса"""
    
    def __init__(self, 
                 x: int, 
                 y: int, 
                 width: int, 
                 height: int, 
                 text: str,
                 action: Optional[Callable] = None,
                 font_size: int = 24,
                 colors: Optional[dict] = None):
        """
        Инициализация кнопки
        
        Args:
            x, y: Позиция кнопки
            width, height: Размеры кнопки
            text: Текст кнопки
            action: Функция, вызываемая при нажатии
            font_size: Размер шрифта
            colors: Словарь с цветами кнопки
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
        
        # Цвета по умолчанию
        self.colors = colors or {
            'normal': (100, 100, 100),
            'hover': (150, 150, 150),
            'pressed': (200, 200, 200),
            'disabled': (50, 50, 50),
            'text': (255, 255, 255),
            'text_disabled': (128, 128, 128),
            'border': (200, 200, 200)
        }
        
        # Состояние кнопки
        self.state = 'normal'  # normal, hover, pressed, disabled
        self.enabled = True
        
        # Создаем поверхности для разных состояний
        self._create_surfaces()
    
    def _create_surfaces(self):
        """Создание поверхностей для разных состояний кнопки"""
        self.surfaces = {}
        
        for state in ['normal', 'hover', 'pressed', 'disabled']:
            surface = pygame.Surface((self.rect.width, self.rect.height))
            surface.set_colorkey((0, 0, 0))  # Прозрачный фон
            
            # Цвет фона
            bg_color = self.colors[state]
            pygame.draw.rect(surface, bg_color, (0, 0, self.rect.width, self.rect.height))
            
            # Рамка
            pygame.draw.rect(surface, self.colors['border'], (0, 0, self.rect.width, self.rect.height), 2)
            
            # Текст
            text_color = self.colors['text_disabled'] if state == 'disabled' else self.colors['text']
            text_surface = self.font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
            surface.blit(text_surface, text_rect)
            
            self.surfaces[state] = surface
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий pygame
        
        Args:
            event: Событие pygame
            
        Returns:
            True если событие обработано кнопкой
        """
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_up(event)
            
        return False
    
    def _handle_mouse_motion(self, event: pygame.event.Event) -> bool:
        """Обработка движения мыши"""
        if self.rect.collidepoint(event.pos):
            if self.state != 'pressed':
                self.state = 'hover'
            return True
        else:
            if self.state != 'pressed':
                self.state = 'normal'
            return False
    
    def _handle_mouse_down(self, event: pygame.event.Event) -> bool:
        """Обработка нажатия мыши"""
        if event.button == 1 and self.rect.collidepoint(event.pos):  # Левый клик
            self.state = 'pressed'
            return True
        return False
    
    def _handle_mouse_up(self, event: pygame.event.Event) -> bool:
        """Обработка отпускания мыши"""
        if event.button == 1 and self.state == 'pressed':  # Левый клик
            if self.rect.collidepoint(event.pos):
                self._execute_action()
            self.state = 'hover' if self.rect.collidepoint(event.pos) else 'normal'
            return True
        return False
    
    def _execute_action(self):
        """Выполнение действия кнопки"""
        if self.action:
            try:
                self.action()
            except Exception as e:
                logger.error(f"Ошибка выполнения действия кнопки '{self.text}': {e}")
    
    def render(self, screen: pygame.Surface):
        """Отрисовка кнопки"""
        if not self.enabled:
            state = 'disabled'
        else:
            state = self.state
            
        screen.blit(self.surfaces[state], self.rect)
    
    def set_enabled(self, enabled: bool):
        """Установка состояния активности кнопки"""
        self.enabled = enabled
        if not enabled:
            self.state = 'disabled'
        elif self.state == 'disabled':
            self.state = 'normal'
    
    def set_text(self, text: str):
        """Изменение текста кнопки"""
        self.text = text
        self._create_surfaces()
    
    def set_action(self, action: Callable):
        """Изменение действия кнопки"""
        self.action = action
    
    def is_hovered(self) -> bool:
        """Проверка наведения мыши"""
        return self.state == 'hover'
    
    def is_pressed(self) -> bool:
        """Проверка нажатия"""
        return self.state == 'pressed'


class ButtonGroup:
    """Группа кнопок для управления состоянием"""
    
    def __init__(self):
        self.buttons = []
        self.selected_button = None
    
    def add_button(self, button: Button):
        """Добавление кнопки в группу"""
        self.buttons.append(button)
    
    def remove_button(self, button: Button):
        """Удаление кнопки из группы"""
        if button in self.buttons:
            self.buttons.remove(button)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий для всех кнопок группы"""
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def render(self, screen: pygame.Surface):
        """Отрисовка всех кнопок группы"""
        for button in self.buttons:
            button.render(screen)
    
    def set_all_enabled(self, enabled: bool):
        """Установка состояния активности для всех кнопок"""
        for button in self.buttons:
            button.set_enabled(enabled)
    
    def get_clicked_button(self) -> Optional[Button]:
        """Получение последней нажатой кнопки"""
        for button in self.buttons:
            if button.is_pressed():
                return button
        return None


class ToggleButton(Button):
    """Кнопка-переключатель"""
    
    def __init__(self, 
                 x: int, 
                 y: int, 
                 width: int, 
                 height: int, 
                 text: str,
                 action: Optional[Callable] = None,
                 font_size: int = 24,
                 colors: Optional[dict] = None):
        super().__init__(x, y, width, height, text, action, font_size, colors)
        self.toggled = False
        
        # Дополнительные цвета для переключателя
        if colors is None:
            self.colors.update({
                'toggled': (0, 150, 0),
                'toggled_hover': (0, 200, 0),
                'toggled_pressed': (0, 250, 0)
            })
    
    def _create_surfaces(self):
        """Создание поверхностей с учетом состояния переключателя"""
        self.surfaces = {}
        
        states = ['normal', 'hover', 'pressed', 'disabled']
        if hasattr(self.colors, 'toggled'):
            states.extend(['toggled', 'toggled_hover', 'toggled_pressed'])
        
        for state in states:
            surface = pygame.Surface((self.rect.width, self.rect.height))
            surface.set_colorkey((0, 0, 0))
            
            # Определяем цвет фона
            if 'toggled' in state:
                base_state = state.replace('toggled_', '')
                bg_color = self.colors.get(state, self.colors.get('toggled', (0, 150, 0)))
            else:
                bg_color = self.colors[state]
            
            pygame.draw.rect(surface, bg_color, (0, 0, self.rect.width, self.rect.height))
            pygame.draw.rect(surface, self.colors['border'], (0, 0, self.rect.width, self.rect.height), 2)
            
            # Текст
            text_color = self.colors['text_disabled'] if state == 'disabled' else self.colors['text']
            text_surface = self.font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
            surface.blit(text_surface, text_rect)
            
            self.surfaces[state] = surface
    
    def _execute_action(self):
        """Выполнение действия с переключением состояния"""
        self.toggled = not self.toggled
        super()._execute_action()
    
    def render(self, screen: pygame.Surface):
        """Отрисовка с учетом состояния переключателя"""
        if not self.enabled:
            state = 'disabled'
        elif self.toggled:
            if self.state == 'pressed':
                state = 'toggled_pressed'
            elif self.state == 'hover':
                state = 'toggled_hover'
            else:
                state = 'toggled'
        else:
            state = self.state
            
        screen.blit(self.surfaces[state], self.rect)
    
    def set_toggled(self, toggled: bool):
        """Установка состояния переключателя"""
        self.toggled = toggled
    
    def is_toggled(self) -> bool:
        """Проверка состояния переключателя"""
        return self.toggled
