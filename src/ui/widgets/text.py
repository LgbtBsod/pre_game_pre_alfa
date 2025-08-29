#!/usr/bin/env python3
"""
Text Widget Module - Модуль текстовых элементов UI
Современный неоновый дизайн с полупрозрачностью
"""

import logging
from typing import Optional, Tuple, Any
from dataclasses import dataclass
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

logger = logging.getLogger(__name__)

@dataclass
class TextStyle:
    """Стиль текста"""
    # Цвета
    text_color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 1.0)
    shadow_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.8)
    
    # Размеры
    scale: float = 0.035
    shadow_offset: Tuple[float, float] = (0.01, 0.01)
    
    # Выравнивание
    align: int = TextNode.ACenter
    
    # Эффекты
    may_change: bool = True
    font: Optional[Any] = None

class NeonText:
    """Неоновый текстовый элемент с современным дизайном"""
    
    def __init__(self, 
                 text: str,
                 pos: Tuple[float, float],
                 style: Optional[TextStyle] = None,
                 parent=None):
        self.text = text
        self.pos = pos
        self.style = style or TextStyle()
        self.parent = parent
        self.text_element = None
        
        logger.debug(f"Создан неоновый текст: {text}")
    
    def create(self) -> OnscreenText:
        """Создание текстового элемента Panda3D"""
        try:
            self.text_element = OnscreenText(
                text=self.text,
                pos=self.pos,
                scale=self.style.scale,
                fg=self.style.text_color,
                align=self.style.align,
                mayChange=self.style.may_change,
                parent=self.parent,
                shadow=self.style.shadow_color,
                shadowOffset=self.style.shadow_offset,
                font=self.style.font
            )
            
            logger.debug(f"Текстовый элемент {self.text} создан успешно")
            return self.text_element
            
        except Exception as e:
            logger.error(f"Ошибка создания текстового элемента {self.text}: {e}")
            return None
    
    def set_text(self, text: str):
        """Изменение текста"""
        if self.text_element:
            self.text_element.setText(text)
            self.text = text
            logger.debug(f"Текст изменен на: {text}")
    
    def set_position(self, pos: Tuple[float, float]):
        """Изменение позиции"""
        if self.text_element:
            self.text_element.setPos(*pos)
            self.pos = pos
    
    def set_scale(self, scale: float):
        """Изменение масштаба"""
        if self.text_element:
            self.text_element.setScale(scale)
            self.style.scale = scale
    
    def set_color(self, color: Tuple[float, float, float, float]):
        """Изменение цвета"""
        if self.text_element:
            self.text_element.setFg(*color)
            self.style.text_color = color
    
    def set_shadow_color(self, shadow_color: Tuple[float, float, float, float]):
        """Изменение цвета тени"""
        if self.text_element:
            self.text_element.setShadow(*shadow_color)
            self.style.shadow_color = shadow_color
    
    def set_visible(self, visible: bool):
        """Показать/скрыть текст"""
        if self.text_element:
            self.text_element.setVisible(visible)
    
    def destroy(self):
        """Уничтожение текстового элемента"""
        if self.text_element:
            self.text_element.destroy()
            self.text_element = None
        logger.debug(f"Текстовый элемент {self.text} уничтожен")

class InfoText(NeonText):
    """Информационный текст для HUD"""
    
    def __init__(self, 
                 text: str,
                 pos: Tuple[float, float],
                 info_type: str = "info",
                 parent=None):
        # Настраиваем стиль в зависимости от типа информации
        if info_type == "health":
            style = TextStyle(
                text_color=(1.0, 0.392, 0.392, 1.0),  # Красный
                scale=0.045
            )
        elif info_type == "mana":
            style = TextStyle(
                text_color=(0.392, 0.392, 1.0, 1.0),  # Синий
                scale=0.045
            )
        elif info_type == "ai":
            style = TextStyle(
                text_color=(0.0, 1.0, 1.0, 1.0),  # Голубой
                scale=0.035
            )
        elif info_type == "skills":
            style = TextStyle(
                text_color=(1.0, 0.392, 1.0, 1.0),  # Розовый
                scale=0.035
            )
        elif info_type == "items":
            style = TextStyle(
                text_color=(1.0, 0.756, 0.027, 1.0),  # Желтый
                scale=0.035
            )
        elif info_type == "effects":
            style = TextStyle(
                text_color=(0.0, 1.0, 0.392, 1.0),  # Зеленый
                scale=0.035
            )
        elif info_type == "genome":
            style = TextStyle(
                text_color=(1.0, 0.5, 0.0, 1.0),  # Оранжевый
                scale=0.035
            )
        elif info_type == "emotion":
            style = TextStyle(
                text_color=(0.8, 0.8, 0.2, 1.0),  # Желтый
                scale=0.035
            )
        else:
            style = TextStyle()
        
        super().__init__(text, pos, style, parent)
        self.info_type = info_type

def create_neon_text(text: str,
                    pos: Tuple[float, float],
                    style: Optional[TextStyle] = None,
                    parent=None) -> NeonText:
    """Фабричная функция для создания неонового текста"""
    text_widget = NeonText(text, pos, style, parent)
    text_widget.create()
    return text_widget

def create_info_text(text: str,
                    pos: Tuple[float, float],
                    info_type: str = "info",
                    parent=None) -> InfoText:
    """Фабричная функция для создания информационного текста"""
    info_widget = InfoText(text, pos, info_type, parent)
    info_widget.create()
    return info_widget
