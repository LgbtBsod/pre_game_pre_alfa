#!/usr/bin/env python3
"""
Menu Scene - Сцена главного меню на Panda3D
"""

import logging
from typing import Dict, Any
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode

from ..core.scene_manager import Scene

logger = logging.getLogger(__name__)

class MenuScene(Scene):
    """Сцена главного меню на Panda3D"""
    
    def __init__(self):
        super().__init__("menu")
        
        # UI элементы
        self.title_text = None
        self.start_button = None
        self.settings_button = None
        self.quit_button = None
        self.background_image = None
        
        logger.info("Сцена меню Panda3D создана")
    
    def initialize(self) -> bool:
        """Инициализация сцены меню"""
        try:
            logger.info("Инициализация сцены меню Panda3D...")
            
            # Создание UI элементов
            self._create_ui_elements()
            
            logger.info("Сцена меню Panda3D успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцены меню: {e}")
            return False
    
    def _create_ui_elements(self):
        """Создание UI элементов меню"""
        # Заголовок
        self.title_text = OnscreenText(
            text="AI-EVOLVE Enhanced Edition",
            pos=(0, 0.7),
            scale=0.08,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            mayChange=False
        )
        
        # Кнопка "Начать игру"
        self.start_button = DirectButton(
            text="Start Game",
            pos=(0, 0, 0.2),
            scale=0.06,
            command=self._start_game,
            frameColor=(0.2, 0.2, 0.2, 1),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        # Кнопка "Настройки"
        self.settings_button = DirectButton(
            text="Settings",
            pos=(0, 0, 0),
            scale=0.06,
            command=self._open_settings,
            frameColor=(0.2, 0.2, 0.2, 1),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        # Кнопка "Выход"
        self.quit_button = DirectButton(
            text="Quit",
            pos=(0, 0, -0.2),
            scale=0.06,
            command=self._quit_game,
            frameColor=(0.2, 0.2, 0.2, 1),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        logger.debug("UI элементы меню созданы")
    
    def _start_game(self):
        """Начать игру"""
        if self.scene_manager:
            self.scene_manager.switch_to_scene("game", "fade")
            logger.info("Переключение на игровую сцену")
    
    def _open_settings(self):
        """Открыть настройки"""
        if self.scene_manager:
            self.scene_manager.switch_to_scene("settings", "fade")
            logger.info("Переключение на сцену настроек")
    
    def _quit_game(self):
        """Выход из игры"""
        logger.info("Выход из игры")
        # Здесь можно добавить логику сохранения и выхода
        import sys
        sys.exit(0)
    
    def update(self, delta_time: float):
        """Обновление сцены меню"""
        # Анимация UI элементов
        pass
    
    def render(self, render_node):
        """Отрисовка сцены меню"""
        # Panda3D автоматически отрисовывает UI
        pass
    
    def handle_event(self, event):
        """Обработка событий"""
        # Panda3D автоматически обрабатывает события кнопок
        pass
    
    def cleanup(self):
        """Очистка сцены меню"""
        logger.info("Очистка сцены меню Panda3D...")
        
        # Уничтожение UI элементов
        if self.title_text:
            self.title_text.destroy()
        if self.start_button:
            self.start_button.destroy()
        if self.settings_button:
            self.settings_button.destroy()
        if self.quit_button:
            self.quit_button.destroy()
        if self.background_image:
            self.background_image.destroy()
        
        logger.info("Сцена меню Panda3D очищена")
