#!/usr/bin/env python3
"""
Panel Widget Module - Модуль панелей UI
Современный неоновый дизайн с полупрозрачностью
"""

import logging
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode

from .button import NeonButton, ButtonStyle

logger = logging.getLogger(__name__)

@dataclass
class PanelStyle:
    """Стиль панели"""
    # Цвета фона
    background_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.8)
    border_color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 0.6)
    
    # Заголовок
    title_color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 1.0)
    title_scale: float = 0.05
    
    # Размеры
    width: float = 1.0
    height: float = 0.8
    
    # Эффекты
    relief: int = 1
    border_width: float = 0.01

class NeonPanel:
    """Неоновая панель с современным дизайном"""
    
    def __init__(self, 
                 title: str = "",
                 style: Optional[PanelStyle] = None,
                 parent=None):
        self.title = title
        self.style = style or PanelStyle()
        self.parent = parent
        
        # UI элементы
        self.background_frame = None
        self.title_label = None
        self.content_frame = None
        self.buttons: List[NeonButton] = []
        
        logger.debug(f"Создана неоновая панель: {title}")
    
    def create(self, pos: Tuple[float, float, float] = (0, 0, 0)) -> DirectFrame:
        """Создание панели Panda3D"""
        try:
            # Основная панель
            self.background_frame = DirectFrame(
                frameColor=self.style.background_color,
                frameSize=(-self.style.width/2, self.style.width/2, 
                          -self.style.height/2, self.style.height/2),
                relief=self.style.relief,
                borderWidth=self.style.border_width,
                borderColor=self.style.border_color,
                parent=self.parent
            )
            self.background_frame.setPos(*pos)
            
            # Заголовок
            if self.title:
                self.title_label = DirectLabel(
                    text=self.title,
                    scale=self.style.title_scale,
                    pos=(0, 0, self.style.height/2 - 0.05),
                    frameColor=(0, 0, 0, 0),
                    text_fg=self.style.title_color,
                    parent=self.background_frame
                )
            
            # Контентная область
            self.content_frame = DirectFrame(
                frameColor=(0, 0, 0, 0),
                frameSize=(-self.style.width/2 + 0.05, self.style.width/2 - 0.05,
                          -self.style.height/2 + 0.1, self.style.height/2 - 0.1),
                parent=self.background_frame
            )
            
            logger.debug(f"Панель {self.title} создана успешно")
            return self.background_frame
            
        except Exception as e:
            logger.error(f"Ошибка создания панели {self.title}: {e}")
            return None
    
    def add_button(self, text: str, command=None, pos: Tuple[float, float, float] = (0, 0, 0)) -> NeonButton:
        """Добавление кнопки на панель"""
        try:
            button = NeonButton(text, command, parent=self.content_frame)
            button.create(pos)
            self.buttons.append(button)
            logger.debug(f"Кнопка {text} добавлена на панель {self.title}")
            return button
        except Exception as e:
            logger.error(f"Ошибка добавления кнопки {text}: {e}")
            return None
    
    def add_buttons_grid(self, button_configs: List[Tuple[str, callable, Tuple[float, float, float]]], 
                        columns: int = 2, spacing: float = 0.1):
        """Добавление кнопок в сетку"""
        try:
            for i, (text, command, _) in enumerate(button_configs):
                row = i // columns
                col = i % columns
                pos = (col * spacing - (columns-1) * spacing/2, 0, -row * spacing)
                self.add_button(text, command, pos)
            
            logger.debug(f"Добавлено {len(button_configs)} кнопок в сетку на панель {self.title}")
        except Exception as e:
            logger.error(f"Ошибка добавления кнопок в сетку: {e}")
    
    def set_title(self, title: str):
        """Изменение заголовка панели"""
        if self.title_label:
            self.title_label['text'] = title
        self.title = title
    
    def set_position(self, pos: Tuple[float, float, float]):
        """Изменение позиции панели"""
        if self.background_frame:
            self.background_frame.setPos(*pos)
    
    def set_size(self, width: float, height: float):
        """Изменение размера панели"""
        if self.background_frame:
            self.background_frame['frameSize'] = (-width/2, width/2, -height/2, height/2)
            self.style.width = width
            self.style.height = height
    
    def set_visible(self, visible: bool):
        """Показать/скрыть панель"""
        if self.background_frame:
            self.background_frame.setVisible(visible)
    
    def clear_content(self):
        """Очистка содержимого панели"""
        # Уничтожаем кнопки
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()
        
        # Очищаем контентную область
        if self.content_frame:
            self.content_frame.removeAllChildren()
            self.content_frame = DirectFrame(
                frameColor=(0, 0, 0, 0),
                frameSize=(-self.style.width/2 + 0.05, self.style.width/2 - 0.05,
                          -self.style.height/2 + 0.1, self.style.height/2 - 0.1),
                parent=self.background_frame
            )
        
        logger.debug(f"Содержимое панели {self.title} очищено")
    
    def destroy(self):
        """Уничтожение панели"""
        # Уничтожаем кнопки
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()
        
        # Уничтожаем основные элементы
        if self.background_frame:
            self.background_frame.destroy()
            self.background_frame = None
        
        logger.debug(f"Панель {self.title} уничтожена")

def create_neon_panel(title: str = "",
                     style: Optional[PanelStyle] = None,
                     parent=None,
                     pos: Tuple[float, float, float] = (0, 0, 0)) -> NeonPanel:
    """Фабричная функция для создания неоновой панели"""
    panel = NeonPanel(title, style, parent)
    panel.create(pos)
    return panel
