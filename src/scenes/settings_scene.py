#!/usr/bin/env python3
"""
Settings Scene - Сцена настроек на Panda3D
"""

import logging
from typing import Dict, Any
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectCheckBox import DirectCheckBox
from panda3d.core import TextNode

from ..core.scene_manager import Scene

logger = logging.getLogger(__name__)

class SettingsScene(Scene):
    """Сцена настроек на Panda3D"""
    
    def __init__(self):
        super().__init__("settings")
        
        # UI элементы
        self.title_text = None
        self.back_button = None
        self.apply_button = None
        
        # Настройки
        self.master_volume_slider = None
        self.music_volume_slider = None
        self.sfx_volume_slider = None
        self.fullscreen_checkbox = None
        self.vsync_checkbox = None
        
        logger.info("Сцена настроек Panda3D создана")
    
    def initialize(self) -> bool:
        """Инициализация сцены настроек"""
        try:
            logger.info("Инициализация сцены настроек Panda3D...")
            
            # Создание UI элементов
            self._create_ui_elements()
            
            logger.info("Сцена настроек Panda3D успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцены настроек: {e}")
            return False
    
    def _create_ui_elements(self):
        """Создание UI элементов настроек"""
        # Заголовок
        self.title_text = OnscreenText(
            text="Settings",
            pos=(0, 0.8),
            scale=0.08,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            mayChange=False
        )
        
        # Громкость
        OnscreenText(
            text="Volume:",
            pos=(-0.8, 0.5),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=False
        )
        
        # Общая громкость
        OnscreenText(
            text="Master:",
            pos=(-0.8, 0.3),
            scale=0.04,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=False
        )
        
        self.master_volume_slider = DirectSlider(
            range=(0, 100),
            value=80,
            pageSize=10,
            orientation="horizontal",
            pos=(0, 0, 0.3),
            scale=0.3,
            thumb_frameColor=(0.5, 0.5, 0.5, 1),
            thumb_relief=1,
            command=self._update_master_volume
        )
        
        # Громкость музыки
        OnscreenText(
            text="Music:",
            pos=(-0.8, 0.1),
            scale=0.04,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=False
        )
        
        self.music_volume_slider = DirectSlider(
            range=(0, 100),
            value=70,
            pageSize=10,
            orientation="horizontal",
            pos=(0, 0, 0.1),
            scale=0.3,
            thumb_frameColor=(0.5, 0.5, 0.5, 1),
            thumb_relief=1,
            command=self._update_music_volume
        )
        
        # Громкость эффектов
        OnscreenText(
            text="SFX:",
            pos=(-0.8, -0.1),
            scale=0.04,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=False
        )
        
        self.sfx_volume_slider = DirectSlider(
            range=(0, 100),
            value=80,
            pageSize=10,
            orientation="horizontal",
            pos=(0, 0, -0.1),
            scale=0.3,
            thumb_frameColor=(0.5, 0.5, 0.5, 1),
            thumb_relief=1,
            command=self._update_sfx_volume
        )
        
        # Графика
        OnscreenText(
            text="Graphics:",
            pos=(-0.8, -0.4),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=False
        )
        
        # Полноэкранный режим
        self.fullscreen_checkbox = DirectCheckBox(
            text="Fullscreen Mode",
            pos=(-0.8, 0, -0.6),
            scale=0.04,
            command=self._toggle_fullscreen,
            indicatorValue=0
        )
        
        # Вертикальная синхронизация
        self.vsync_checkbox = DirectCheckBox(
            text="Vertical Sync",
            pos=(-0.8, 0, -0.7),
            scale=0.04,
            command=self._toggle_vsync,
            indicatorValue=1
        )
        
        # Кнопки
        self.apply_button = DirectButton(
            text="Apply",
            pos=(-0.3, 0, -0.9),
            scale=0.05,
            command=self._apply_settings,
            frameColor=(0.2, 0.6, 0.2, 1),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        self.back_button = DirectButton(
            text="Back",
            pos=(0.3, 0, -0.9),
            scale=0.05,
            command=self._go_back,
            frameColor=(0.6, 0.2, 0.2, 1),
            text_fg=(1, 1, 1, 1),
            relief=1
        )
        
        logger.debug("UI элементы настроек созданы")
    
    def _update_master_volume(self):
        """Обновление общей громкости"""
        volume = self.master_volume_slider['value']
        logger.info(f"Общая громкость изменена: {volume}")
    
    def _update_music_volume(self):
        """Обновление громкости музыки"""
        volume = self.music_volume_slider['value']
        logger.info(f"Громкость музыки изменена: {volume}")
    
    def _update_sfx_volume(self):
        """Обновление громкости эффектов"""
        volume = self.sfx_volume_slider['value']
        logger.info(f"Громкость эффектов изменена: {volume}")
    
    def _toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        fullscreen = self.fullscreen_checkbox['indicatorValue']
        logger.info(f"Fullscreen mode: {fullscreen}")
    
    def _toggle_vsync(self):
        """Переключение вертикальной синхронизации"""
        vsync = self.vsync_checkbox['indicatorValue']
        logger.info(f"Vertical sync: {vsync}")
    
    def _apply_settings(self):
        """Применение настроек"""
        logger.info("Применение настроек")
        # Здесь можно добавить логику сохранения настроек
    
    def _go_back(self):
        """Возврат назад"""
        if self.scene_manager:
            self.scene_manager.switch_to_scene("menu", "fade")
            logger.info("Возврат в главное меню")
    
    def update(self, delta_time: float):
        """Обновление сцены настроек"""
        # Анимация UI элементов
        pass
    
    def render(self, render_node):
        """Отрисовка сцены настроек"""
        # Panda3D автоматически отрисовывает UI
        pass
    
    def handle_event(self, event):
        """Обработка событий"""
        # Panda3D автоматически обрабатывает события UI
        pass
    
    def cleanup(self):
        """Очистка сцены настроек"""
        logger.info("Очистка сцены настроек Panda3D...")
        
        # Уничтожение UI элементов
        if self.title_text:
            self.title_text.destroy()
        if self.master_volume_slider:
            self.master_volume_slider.destroy()
        if self.music_volume_slider:
            self.music_volume_slider.destroy()
        if self.sfx_volume_slider:
            self.sfx_volume_slider.destroy()
        if self.fullscreen_checkbox:
            self.fullscreen_checkbox.destroy()
        if self.vsync_checkbox:
            self.vsync_checkbox.destroy()
        if self.apply_button:
            self.apply_button.destroy()
        if self.back_button:
            self.back_button.destroy()
        
        logger.info("Сцена настроек Panda3D очищена")
