#!/usr/bin/env python3
"""
Pause Scene - Сцена паузы на Panda3D
"""

import logging
from typing import Dict, Any
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode

from ..core.scene_manager import Scene

logger = logging.getLogger(__name__)

class PauseScene(Scene):
    """Сцена паузы на Panda3D"""
    
    def __init__(self):
        super().__init__("pause")
        
        # UI элементы
        self.pause_text = None
        self.resume_button = None
        self.settings_button = None
        self.menu_button = None
        
        logger.info("Сцена паузы Panda3D создана")
    
    def initialize(self) -> bool:
        """Инициализация сцены паузы"""
        try:
            logger.info("Инициализация сцены паузы Panda3D...")
            
            # Создание UI элементов
            self._create_ui_elements()
            
            logger.info("Сцена паузы Panda3D успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцены паузы: {e}")
            return False
    
    def _create_ui_elements(self):
        """Создание UI элементов паузы"""
        # Используем корневой узел UI сцены
        parent_node = self.ui_root if self.ui_root else None
        
        # Современный неоновый заголовок паузы
        self.pause_text = OnscreenText(
            text="⏸️ PAUSED",
            pos=(0, 0.5),
            scale=0.12,
            fg=(255, 255, 0, 1),  # Неоновый желтый
            align=TextNode.ACenter,
            mayChange=False,
            parent=parent_node,
            shadow=(0, 0, 0, 0.8),
            shadowOffset=(0.02, 0.02)
        )
        
        # Кнопка "Продолжить"
        self.resume_button = DirectButton(
            text="▶️ RESUME",
            pos=(0, 0, 0.1),
            scale=0.07,
            command=self._resume_game,
            frameColor=(0, 255, 100, 0.8),  # Неоновый зеленый
            text_fg=(255, 255, 255, 1),
            relief=1,
            parent=parent_node
        )
        
        # Кнопка "Настройки"
        self.settings_button = DirectButton(
            text="⚙️ SETTINGS",
            pos=(0, 0, -0.1),
            scale=0.07,
            command=self._open_settings,
            frameColor=(255, 100, 255, 0.8),  # Неоновый розовый
            text_fg=(255, 255, 255, 1),
            relief=1,
            parent=parent_node
        )
        
        # Кнопка "Главное меню"
        self.menu_button = DirectButton(
            text="🏠 MAIN MENU",
            pos=(0, 0, -0.3),
            scale=0.07,
            command=self._return_to_menu,
            frameColor=(100, 100, 255, 0.8),  # Неоновый синий
            text_fg=(255, 255, 255, 1),
            relief=1,
            parent=parent_node
        )
        
        logger.debug("UI элементы паузы созданы")
    
    def _resume_game(self):
        """Продолжить игру"""
        if self.scene_manager:
            self.scene_manager.switch_to_scene("game", "instant")
            logger.info("Возобновление игры")
    
    def _open_settings(self):
        """Открыть настройки"""
        if self.scene_manager:
            self.scene_manager.switch_to_scene("settings", "fade")
            logger.info("Переключение на сцену настроек")
    
    def _return_to_menu(self):
        """Вернуться в главное меню"""
        if self.scene_manager:
            self.scene_manager.switch_to_scene("menu", "fade")
            logger.info("Возврат в главное меню")
    
    def update(self, delta_time: float):
        """Обновление сцены паузы"""
        # Анимация UI элементов
        pass
    
    def render(self, render_node):
        """Отрисовка сцены паузы"""
        # Panda3D автоматически отрисовывает UI
        pass
    
    def handle_event(self, event):
        """Обработка событий"""
        # Panda3D автоматически обрабатывает события кнопок
        pass
    
    def cleanup(self):
        """Очистка сцены паузы"""
        logger.info("Очистка сцены паузы Panda3D...")
        
        # Уничтожение UI элементов
        if self.pause_text:
            self.pause_text.destroy()
        if self.resume_button:
            self.resume_button.destroy()
        if self.settings_button:
            self.settings_button.destroy()
        if self.menu_button:
            self.menu_button.destroy()
        
        logger.info("Сцена паузы Panda3D очищена")
