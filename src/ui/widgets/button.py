#!/usr/bin/env python3
"""
Button Widget Module - Модуль кнопок UI
Современный неоновый дизайн с полупрозрачностью
"""

import logging
from typing import Optional, Callable, Dict, Any, Tuple
from dataclasses import dataclass
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode

logger = logging.getLogger(__name__)

@dataclass
class ButtonStyle:
    """Стиль кнопки"""
    # Цвета
    normal_color: Tuple[float, float, float, float] = (0.0, 1.0, 0.392, 0.8)
    hover_color: Tuple[float, float, float, float] = (0.0, 1.0, 0.6, 0.9)
    pressed_color: Tuple[float, float, float, float] = (0.0, 0.8, 0.3, 1.0)
    disabled_color: Tuple[float, float, float, float] = (0.5, 0.5, 0.5, 0.5)
    
    # Текст
    text_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    text_scale: float = 1.0
    
    # Размеры
    width: float = 0.2
    height: float = 0.05
    
    # Эффекты
    relief: int = 1
    frameColor: Optional[Tuple[float, float, float, float]] = None
    shadow_offset: Tuple[float, float] = (0.01, 0.01)

class NeonButton:
    """Неоновая кнопка с современным дизайном"""
    
    def __init__(self, 
                 text: str,
                 command: Optional[Callable] = None,
                 style: Optional[ButtonStyle] = None,
                 parent=None):
        self.text = text
        self.command = command
        self.style = style or ButtonStyle()
        self.parent = parent
        self.button = None
        self._is_hovered = False
        self._is_pressed = False
        
        logger.debug(f"Создана неоновая кнопка: {text}")
    
    def create(self, pos: Tuple[float, float, float] = (0, 0, 0)) -> DirectButton:
        """Создание кнопки Panda3D"""
        try:
            # Создаем кнопку
            self.button = DirectButton(
                text=self.text,
                pos=pos,
                scale=self.style.text_scale,
                command=self.command,
                frameColor=self.style.normal_color,
                text_fg=self.style.text_color,
                relief=self.style.relief,
                parent=self.parent,
                width=self.style.width,
                height=self.style.height
            )
            
            # Добавляем обработчики событий
            self._setup_event_handlers()
            
            logger.debug(f"Кнопка {self.text} создана успешно")
            return self.button
            
        except Exception as e:
            logger.error(f"Ошибка создания кнопки {self.text}: {e}")
            return None
    
    def _setup_event_handlers(self):
        """Настройка обработчиков событий"""
        if not self.button:
            return
        
        # Обработчик наведения
        self.button.bind(DirectButton.ENTER, self._on_hover)
        self.button.bind(DirectButton.EXIT, self._on_unhover)
        
        # Обработчик нажатия
        self.button.bind(DirectButton.B1PRESS, self._on_press)
        self.button.bind(DirectButton.B1RELEASE, self._on_release)
    
    def _on_hover(self, event):
        """Обработка наведения мыши"""
        self._is_hovered = True
        if self.button:
            self.button['frameColor'] = self.style.hover_color
        logger.debug(f"Кнопка {self.text} в фокусе")
    
    def _on_unhover(self, event):
        """Обработка ухода мыши"""
        self._is_hovered = False
        if self.button and not self._is_pressed:
            self.button['frameColor'] = self.style.normal_color
        logger.debug(f"Кнопка {self.text} потеряла фокус")
    
    def _on_press(self, event):
        """Обработка нажатия"""
        self._is_pressed = True
        if self.button:
            self.button['frameColor'] = self.style.pressed_color
        logger.debug(f"Кнопка {self.text} нажата")
    
    def _on_release(self, event):
        """Обработка отпускания"""
        self._is_pressed = False
        if self.button:
            if self._is_hovered:
                self.button['frameColor'] = self.style.hover_color
            else:
                self.button['frameColor'] = self.style.normal_color
        logger.debug(f"Кнопка {self.text} отпущена")
    
    def set_enabled(self, enabled: bool):
        """Включение/отключение кнопки"""
        if self.button:
            self.button['state'] = DirectButton.NORMAL if enabled else DirectButton.DISABLED
            if not enabled:
                self.button['frameColor'] = self.style.disabled_color
            else:
                self.button['frameColor'] = self.style.normal_color
    
    def set_text(self, text: str):
        """Изменение текста кнопки"""
        if self.button:
            self.button['text'] = text
            self.text = text
    
    def set_position(self, pos: Tuple[float, float, float]):
        """Изменение позиции кнопки"""
        if self.button:
            self.button.setPos(*pos)
    
    def set_scale(self, scale: float):
        """Изменение масштаба кнопки"""
        if self.button:
            self.button.setScale(scale)
    
    def destroy(self):
        """Уничтожение кнопки"""
        if self.button:
            self.button.destroy()
            self.button = None
        logger.debug(f"Кнопка {self.text} уничтожена")

def create_neon_button(text: str, 
                      command: Optional[Callable] = None,
                      style: Optional[ButtonStyle] = None,
                      parent=None,
                      pos: Tuple[float, float, float] = (0, 0, 0)) -> NeonButton:
    """Фабричная функция для создания неоновой кнопки"""
    button = NeonButton(text, command, style, parent)
    button.create(pos)
    return button
