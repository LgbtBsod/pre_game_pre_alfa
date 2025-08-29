#!/usr/bin/env python3
"""
Progress Bar Widget Module - Модуль прогресс-баров UI
Современный неоновый дизайн с полупрозрачностью
"""

import logging
from typing import Optional, Tuple, Any
from dataclasses import dataclass
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode

logger = logging.getLogger(__name__)

@dataclass
class ProgressBarStyle:
    """Стиль прогресс-бара"""
    # Размеры
    width: float = 0.3
    height: float = 0.02
    
    # Цвета
    background_color: Tuple[float, float, float, float] = (0.2, 0.2, 0.2, 0.8)
    border_color: Tuple[float, float, float, float] = (0.5, 0.5, 0.5, 0.9)
    fill_color: Tuple[float, float, float, float] = (0.0, 1.0, 0.392, 0.9)
    
    # Текст
    show_text: bool = True
    text_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    text_scale: float = 0.025
    
    # Эффекты
    border_width: float = 0.002
    rounded_corners: bool = True

class NeonProgressBar:
    """Неоновый прогресс-бар с современным дизайном"""
    
    def __init__(self, 
                 title: str = "",
                 style: Optional[ProgressBarStyle] = None,
                 parent=None):
        self.title = title
        self.style = style or ProgressBarStyle()
        self.parent = parent
        
        # UI элементы
        self.background_frame = None
        self.fill_frame = None
        self.border_frame = None
        self.title_label = None
        self.value_label = None
        
        # Состояние
        self.current_value = 0.0
        self.max_value = 100.0
        self.percentage = 0.0
        
        logger.debug(f"Создан неоновый прогресс-бар: {title}")
    
    def create(self, pos: Tuple[float, float, float] = (0, 0, 0)) -> DirectFrame:
        """Создание прогресс-бара Panda3D"""
        try:
            # Основной контейнер
            main_frame = DirectFrame(
                frameColor=(0, 0, 0, 0),
                frameSize=(-self.style.width/2, self.style.width/2, 
                          -self.style.height/2, self.style.height/2),
                parent=self.parent
            )
            main_frame.setPos(*pos)
            
            # Заголовок
            if self.title and self.style.show_text:
                self.title_label = DirectLabel(
                    text=self.title,
                    scale=self.style.text_scale,
                    pos=(0, 0, self.style.height/2 + 0.02),
                    frameColor=(0, 0, 0, 0),
                    text_fg=self.style.text_color,
                    parent=main_frame
                )
            
            # Фон прогресс-бара
            self.background_frame = DirectFrame(
                frameColor=self.style.background_color,
                frameSize=(-self.style.width/2, self.style.width/2, 
                          -self.style.height/2, self.style.height/2),
                parent=main_frame
            )
            
            # Граница
            self.border_frame = DirectFrame(
                frameColor=self.style.border_color,
                frameSize=(-self.style.width/2 - self.style.border_width, 
                          self.style.width/2 + self.style.border_width,
                          -self.style.height/2 - self.style.border_width, 
                          self.style.height/2 + self.style.border_width),
                parent=main_frame
            )
            
            # Заполнение (изначально 0%)
            self.fill_frame = DirectFrame(
                frameColor=self.style.fill_color,
                frameSize=(-self.style.width/2, -self.style.width/2, 
                          -self.style.height/2, self.style.height/2),
                parent=main_frame
            )
            
            # Значение
            if self.style.show_text:
                self.value_label = DirectLabel(
                    text="0%",
                    scale=self.style.text_scale,
                    pos=(0, 0, 0),
                    frameColor=(0, 0, 0, 0),
                    text_fg=self.style.text_color,
                    parent=main_frame
                )
            
            logger.debug(f"Прогресс-бар {self.title} создан успешно")
            return main_frame
            
        except Exception as e:
            logger.error(f"Ошибка создания прогресс-бара {self.title}: {e}")
            return None
    
    def set_value(self, current: float, maximum: Optional[float] = None):
        """Установка значения прогресс-бара"""
        try:
            if maximum is not None:
                self.max_value = maximum
            
            self.current_value = max(0.0, min(current, self.max_value))
            self.percentage = (self.current_value / self.max_value) * 100.0 if self.max_value > 0 else 0.0
            
            # Обновляем заполнение
            if self.fill_frame:
                fill_width = (self.style.width * self.percentage) / 100.0
                self.fill_frame['frameSize'] = (
                    -self.style.width/2, 
                    -self.style.width/2 + fill_width,
                    -self.style.height/2, 
                    self.style.height/2
                )
            
            # Обновляем текст
            if self.value_label:
                self.value_label['text'] = f"{self.percentage:.1f}%"
            
            logger.debug(f"Прогресс-бар {self.title}: {self.percentage:.1f}%")
            
        except Exception as e:
            logger.error(f"Ошибка установки значения прогресс-бара {self.title}: {e}")
    
    def set_percentage(self, percentage: float):
        """Установка процента заполнения"""
        percentage = max(0.0, min(100.0, percentage))
        value = (percentage / 100.0) * self.max_value
        self.set_value(value)
    
    def set_fill_color(self, color: Tuple[float, float, float, float]):
        """Изменение цвета заполнения"""
        if self.fill_frame:
            self.fill_frame['frameColor'] = color
            self.style.fill_color = color
    
    def set_title(self, title: str):
        """Изменение заголовка"""
        if self.title_label:
            self.title_label['text'] = title
        self.title = title
    
    def set_visible(self, visible: bool):
        """Показать/скрыть прогресс-бар"""
        if self.background_frame:
            self.background_frame.setVisible(visible)
        if self.border_frame:
            self.border_frame.setVisible(visible)
        if self.fill_frame:
            self.fill_frame.setVisible(visible)
        if self.title_label:
            self.title_label.setVisible(visible)
        if self.value_label:
            self.value_label.setVisible(visible)
    
    def destroy(self):
        """Уничтожение прогресс-бара"""
        if self.background_frame:
            self.background_frame.destroy()
            self.background_frame = None
        if self.border_frame:
            self.border_frame.destroy()
            self.border_frame = None
        if self.fill_frame:
            self.fill_frame.destroy()
            self.fill_frame = None
        if self.title_label:
            self.title_label.destroy()
            self.title_label = None
        if self.value_label:
            self.value_label.destroy()
            self.value_label = None
        
        logger.debug(f"Прогресс-бар {self.title} уничтожен")

class HealthBar(NeonProgressBar):
    """Прогресс-бар здоровья"""
    
    def __init__(self, parent=None):
        style = ProgressBarStyle(
            width=0.25,
            height=0.015,
            fill_color=(1.0, 0.392, 0.392, 0.9),  # Красный
            show_text=True
        )
        super().__init__("Health", style, parent)
    
    def set_health(self, current: int, maximum: int):
        """Установка здоровья"""
        self.set_value(float(current), float(maximum))
        if self.value_label:
            self.value_label['text'] = f"{current}/{maximum}"

class ManaBar(NeonProgressBar):
    """Прогресс-бар маны"""
    
    def __init__(self, parent=None):
        style = ProgressBarStyle(
            width=0.25,
            height=0.015,
            fill_color=(0.392, 0.392, 1.0, 0.9),  # Синий
            show_text=True
        )
        super().__init__("Mana", style, parent)
    
    def set_mana(self, current: int, maximum: int):
        """Установка маны"""
        self.set_value(float(current), float(maximum))
        if self.value_label:
            self.value_label['text'] = f"{current}/{maximum}"

class ExperienceBar(NeonProgressBar):
    """Прогресс-бар опыта"""
    
    def __init__(self, parent=None):
        style = ProgressBarStyle(
            width=0.3,
            height=0.02,
            fill_color=(1.0, 0.756, 0.027, 0.9),  # Желтый
            show_text=True
        )
        super().__init__("Experience", style, parent)
    
    def set_experience(self, current: int, maximum: int):
        """Установка опыта"""
        self.set_value(float(current), float(maximum))
        if self.value_label:
            self.value_label['text'] = f"{current}/{maximum}"

def create_neon_progress_bar(title: str = "",
                           style: Optional[ProgressBarStyle] = None,
                           parent=None,
                           pos: Tuple[float, float, float] = (0, 0, 0)) -> NeonProgressBar:
    """Фабричная функция для создания неонового прогресс-бара"""
    progress_bar = NeonProgressBar(title, style, parent)
    progress_bar.create(pos)
    return progress_bar

def create_health_bar(parent=None, pos: Tuple[float, float, float] = (0, 0, 0)) -> HealthBar:
    """Фабричная функция для создания прогресс-бара здоровья"""
    health_bar = HealthBar(parent)
    health_bar.create(pos)
    return health_bar

def create_mana_bar(parent=None, pos: Tuple[float, float, float] = (0, 0, 0)) -> ManaBar:
    """Фабричная функция для создания прогресс-бара маны"""
    mana_bar = ManaBar(parent)
    mana_bar.create(pos)
    return mana_bar

def create_experience_bar(parent=None, pos: Tuple[float, float, float] = (0, 0, 0)) -> ExperienceBar:
    """Фабричная функция для создания прогресс-бара опыта"""
    exp_bar = ExperienceBar(parent)
    exp_bar.create(pos)
    return exp_bar
