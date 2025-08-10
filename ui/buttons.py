"""Кнопки пользовательского интерфейса."""

import logging
from typing import Callable, Optional, Any
from direct.gui.DirectGui import DirectButton

logger = logging.getLogger(__name__)

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.pressed = False
        self.font_size = 24
        self.font = pygame.font.SysFont(None, self.font_size)
    
    def update(self, mouse_pos, mouse_pressed):
        """Обновляет состояние кнопки (наведение, нажатие)"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_pressed:
            self.pressed = True
        else:
            self.pressed = False

    def draw(self, surface):
        """Отрисовывает кнопку на экране"""
        # Цвет фона
        bg_color = (90, 110, 150) if self.hovered else (70, 90, 120)
        border_color = (100, 130, 180) if self.hovered else (100, 120, 150)

        # Рисуем фон кнопки
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=10)

        # Текст
        text_surf = self.font.render(self.text, True, (240, 240, 240))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                logger.debug(f"Button '{self.text}' pressed")  # Отладочный вывод
                return self.action()
        return None

    def check_hover(self, pos):
        """Проверяет наведение курсора"""
        self.hovered = self.rect.collidepoint(pos)