#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton, DirectFrame
from panda3d.core import TextNode, Vec4, Vec3
from panda3d.core import CardMaker, TransparencyAttrib

class PauseScreen:
    """Экран паузы"""
    
    def __init__(self, game):
        self.game = game
        self.elements = []
        
    def enter(self):
        """Вход в состояние паузы"""
        self.create_overlay()
        self.create_title()
        self.create_buttons()
        
    def exit(self):
        """Выход из состояния паузы"""
        for element in self.elements:
            if hasattr(element, 'destroy'):
                element.destroy()
            else:
                element.removeNode()
        self.elements.clear()
        
    def create_overlay(self):
        """Создание полупрозрачного оверлея"""
        cm = CardMaker("pause_overlay")
        cm.setFrame(-2, 2, -1.5, 1.5)
        overlay = self.game.aspect2d.attachNewNode(cm.generate())
        overlay.setColor(0, 0, 0, 0.7)
        overlay.setTransparency(TransparencyAttrib.MAlpha)
        self.elements.append(overlay)
        
    def create_title(self):
        """Создание заголовка паузы"""
        title = OnscreenText(
            text="PAUSE",
            pos=(0, 0.2),
            scale=0.12,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.8),
            shadowOffset=(0.05, 0.05),
            align=TextNode.ACenter,
            parent=self.game.aspect2d
        )
        self.elements.append(title)
        
        subtitle = OnscreenText(
            text="Press ESC to continue",
            pos=(0, 0.05),
            scale=0.06,
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter,
            parent=self.game.aspect2d
        )
        self.elements.append(subtitle)
        
    def create_buttons(self):
        """Создание кнопок паузы"""
        # Кнопка "Resume"
        resume_btn = DirectButton(
            text="Resume",
            text_scale=0.08,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.2, 0.8, 0.2, 1),
            frameSize=(-0.3, 0.3, -0.05, 0.05),
            pos=(0, 0, -0.1),
            command=self.resume_game,
            parent=self.game.aspect2d
        )
        self.elements.append(resume_btn)
        
        # Кнопка "Settings"
        settings_btn = DirectButton(
            text="Settings",
            text_scale=0.08,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.2, 0.4, 0.8, 1),
            frameSize=(-0.3, 0.3, -0.05, 0.05),
            pos=(0, 0, -0.2),
            command=self.open_settings,
            parent=self.game.aspect2d
        )
        self.elements.append(settings_btn)
        
        # Кнопка "Main Menu"
        menu_btn = DirectButton(
            text="Main Menu",
            text_scale=0.08,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.8, 0.4, 0.2, 1),
            frameSize=(-0.3, 0.3, -0.05, 0.05),
            pos=(0, 0, -0.3),
            command=self.return_to_menu,
            parent=self.game.aspect2d
        )
        self.elements.append(menu_btn)
        
    def resume_game(self):
        """Продолжить игру"""
        self.game.state_manager.change_state("game")
        
    def open_settings(self):
        """Открыть настройки"""
        self.game.state_manager.change_state("settings")
        
    def return_to_menu(self):
        """Вернуться в главное меню"""
        self.game.state_manager.change_state("start")
