#!/usr/bin/env python3
"""
Menu Widget Module - Модуль меню UI
Современный неоновый дизайн с полупрозрачностью
"""

import logging
from typing import Optional, Dict, Any, Tuple, List, Callable
from dataclasses import dataclass
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel

from .button import NeonButton, ButtonStyle
from .panel import NeonPanel, PanelStyle

logger = logging.getLogger(__name__)

@dataclass
class MenuStyle:
    """Стиль меню"""
    # Размеры
    width: float = 0.8
    height: float = 0.6
    
    # Цвета
    background_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.9)
    border_color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 0.8)
    
    # Заголовок
    title_color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 1.0)
    title_scale: float = 0.08
    
    # Кнопки
    button_spacing: float = 0.08
    button_style: Optional[ButtonStyle] = None

class NeonMenu:
    """Неоновое меню с современным дизайном"""
    
    def __init__(self, 
                 title: str = "",
                 style: Optional[MenuStyle] = None,
                 parent=None):
        self.title = title
        self.style = style or MenuStyle()
        self.parent = parent
        
        # UI элементы
        self.background_frame = None
        self.title_label = None
        self.content_frame = None
        self.buttons: List[NeonButton] = []
        
        # Состояние
        self.is_visible = False
        self.current_page = 0
        self.pages: List[List[Tuple[str, Callable]]] = [[]]
        
        logger.debug(f"Создано неоновое меню: {title}")
    
    def create(self, pos: Tuple[float, float, float] = (0, 0, 0)) -> DirectFrame:
        """Создание меню Panda3D"""
        try:
            # Основная панель
            self.background_frame = DirectFrame(
                frameColor=self.style.background_color,
                frameSize=(-self.style.width/2, self.style.width/2, 
                          -self.style.height/2, self.style.height/2),
                relief=1,
                borderWidth=0.01,
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
            
            logger.debug(f"Меню {self.title} создано успешно")
            return self.background_frame
            
        except Exception as e:
            logger.error(f"Ошибка создания меню {self.title}: {e}")
            return None
    
    def add_button(self, text: str, command: Optional[Callable] = None, 
                   page: int = 0, pos: Optional[Tuple[float, float, float]] = None) -> NeonButton:
        """Добавление кнопки в меню"""
        try:
            # Создаем кнопку
            button = NeonButton(text, command, self.style.button_style, self.content_frame)
            
            # Позиционируем кнопку
            if pos is None:
                # Автоматическое позиционирование
                button_count = len(self.buttons)
                button_pos = (0, 0, self.style.height/2 - 0.15 - button_count * self.style.button_spacing)
            else:
                button_pos = pos
            
            button.create(button_pos)
            self.buttons.append(button)
            
            # Добавляем в страницу
            while len(self.pages) <= page:
                self.pages.append([])
            self.pages[page].append((text, command))
            
            logger.debug(f"Кнопка {text} добавлена в меню {self.title} на страницу {page}")
            return button
            
        except Exception as e:
            logger.error(f"Ошибка добавления кнопки {text}: {e}")
            return None
    
    def add_buttons(self, button_configs: List[Tuple[str, Optional[Callable]]], 
                   page: int = 0, start_y: float = None):
        """Добавление нескольких кнопок"""
        try:
            if start_y is None:
                start_y = self.style.height/2 - 0.15
            
            for i, (text, command) in enumerate(button_configs):
                pos = (0, 0, start_y - i * self.style.button_spacing)
                self.add_button(text, command, page, pos)
            
            logger.debug(f"Добавлено {len(button_configs)} кнопок в меню {self.title} на страницу {page}")
        except Exception as e:
            logger.error(f"Ошибка добавления кнопок: {e}")
    
    def set_page(self, page: int):
        """Переключение на страницу"""
        try:
            if 0 <= page < len(self.pages):
                self.current_page = page
                self._update_visibility()
                logger.debug(f"Меню {self.title} переключено на страницу {page}")
            else:
                logger.warning(f"Страница {page} не существует в меню {self.title}")
        except Exception as e:
            logger.error(f"Ошибка переключения страницы: {e}")
    
    def next_page(self):
        """Следующая страница"""
        if self.current_page < len(self.pages) - 1:
            self.set_page(self.current_page + 1)
    
    def prev_page(self):
        """Предыдущая страница"""
        if self.current_page > 0:
            self.set_page(self.current_page - 1)
    
    def _update_visibility(self):
        """Обновление видимости элементов по страницам"""
        try:
            for i, button in enumerate(self.buttons):
                # Определяем, на какой странице находится кнопка
                button_page = 0
                for page_idx, page_buttons in enumerate(self.pages):
                    if any(text == button.text for text, _ in page_buttons):
                        button_page = page_idx
                        break
                
                # Показываем только кнопки текущей страницы
                button.set_visible(button_page == self.current_page)
                
        except Exception as e:
            logger.error(f"Ошибка обновления видимости: {e}")
    
    def show(self):
        """Показать меню"""
        if self.background_frame:
            self.background_frame.setVisible(True)
            self.is_visible = True
            self._update_visibility()
            logger.debug(f"Меню {self.title} показано")
    
    def hide(self):
        """Скрыть меню"""
        if self.background_frame:
            self.background_frame.setVisible(False)
            self.is_visible = False
            logger.debug(f"Меню {self.title} скрыто")
    
    def toggle(self):
        """Переключить видимость меню"""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def set_title(self, title: str):
        """Изменение заголовка меню"""
        if self.title_label:
            self.title_label['text'] = title
        self.title = title
    
    def clear_buttons(self):
        """Очистка всех кнопок"""
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()
        self.pages = [[]]
        self.current_page = 0
        logger.debug(f"Все кнопки меню {self.title} очищены")
    
    def destroy(self):
        """Уничтожение меню"""
        self.clear_buttons()
        
        if self.background_frame:
            self.background_frame.destroy()
            self.background_frame = None
        
        logger.debug(f"Меню {self.title} уничтожено")

class MainMenu(NeonMenu):
    """Главное меню игры"""
    
    def __init__(self, parent=None):
        style = MenuStyle(
            width=1.0,
            height=0.8,
            title_scale=0.1
        )
        super().__init__("AI-EVOLVE ENHANCED EDITION", style, parent)
    
    def create_default_buttons(self):
        """Создание стандартных кнопок главного меню"""
        button_configs = [
            ("START GAME", None),
            ("WORLD CREATOR", None),
            ("SETTINGS", None),
            ("QUIT GAME", None)
        ]
        self.add_buttons(button_configs)

class PauseMenu(NeonMenu):
    """Меню паузы"""
    
    def __init__(self, parent=None):
        style = MenuStyle(
            width=0.6,
            height=0.5,
            title_scale=0.06
        )
        super().__init__("PAUSED", style, parent)
    
    def create_default_buttons(self):
        """Создание стандартных кнопок меню паузы"""
        button_configs = [
            ("RESUME", None),
            ("SETTINGS", None),
            ("MAIN MENU", None)
        ]
        self.add_buttons(button_configs)

class SettingsMenu(NeonMenu):
    """Меню настроек"""
    
    def __init__(self, parent=None):
        style = MenuStyle(
            width=0.7,
            height=0.6,
            title_scale=0.06
        )
        super().__init__("SETTINGS", style, parent)
    
    def create_default_buttons(self):
        """Создание стандартных кнопок меню настроек"""
        button_configs = [
            ("VIDEO", None),
            ("AUDIO", None),
            ("CONTROLS", None),
            ("BACK", None)
        ]
        self.add_buttons(button_configs)

def create_neon_menu(title: str = "",
                    style: Optional[MenuStyle] = None,
                    parent=None,
                    pos: Tuple[float, float, float] = (0, 0, 0)) -> NeonMenu:
    """Фабричная функция для создания неонового меню"""
    menu = NeonMenu(title, style, parent)
    menu.create(pos)
    return menu

def create_main_menu(parent=None, pos: Tuple[float, float, float] = (0, 0, 0)) -> MainMenu:
    """Фабричная функция для создания главного меню"""
    menu = MainMenu(parent)
    menu.create(pos)
    menu.create_default_buttons()
    return menu

def create_pause_menu(parent=None, pos: Tuple[float, float, float] = (0, 0, 0)) -> PauseMenu:
    """Фабричная функция для создания меню паузы"""
    menu = PauseMenu(parent)
    menu.create(pos)
    menu.create_default_buttons()
    return menu

def create_settings_menu(parent=None, pos: Tuple[float, float, float] = (0, 0, 0)) -> SettingsMenu:
    """Фабричная функция для создания меню настроек"""
    menu = SettingsMenu(parent)
    menu.create(pos)
    menu.create_default_buttons()
    return menu
