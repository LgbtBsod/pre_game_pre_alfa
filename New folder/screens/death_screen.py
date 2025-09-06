#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from direct.gui.DirectGui import DirectButton, OnscreenText
from panda3d.core import CardMaker

class DeathScreen:
    """Экран смерти"""
    
    def __init__(self, game):
        self.game = game
        self.elements = []
        
    def enter(self):
        """Вход в экран смерти"""
        # Создаем полупрозрачный фон
        cm = CardMaker("death_background")
        cm.setFrame(-2, 2, -1.5, 1.5)
        background = self.game.aspect2d.attachNewNode(cm.generate())
        background.setColor(0, 0, 0, 0.8)
        self.elements.append(background)
        
        # Заголовок "GAME OVER"
        title = OnscreenText(
            text="GAME OVER",
            pos=(0, 0.3),
            scale=0.2,
            fg=(1, 0, 0, 1),  # Красный цвет
            parent=self.game.aspect2d
        )
        self.elements.append(title)
        
        # Подзаголовок
        subtitle = OnscreenText(
            text="Your character has died!",
            pos=(0, 0.1),
            scale=0.08,
            fg=(1, 1, 1, 1),  # Белый цвет
            parent=self.game.aspect2d
        )
        self.elements.append(subtitle)
        
        # Кнопка "Restart"
        restart_button = DirectButton(
            text="Restart",
            pos=(0, 0, -0.1),
            scale=0.1,
            command=self.restart_game,
            parent=self.game.aspect2d
        )
        self.elements.append(restart_button)
        
        # Кнопка "Main Menu"
        menu_button = DirectButton(
            text="Main Menu",
            pos=(0, 0, -0.25),
            scale=0.1,
            command=self.go_to_main_menu,
            parent=self.game.aspect2d
        )
        self.elements.append(menu_button)
        
        # Кнопка "Exit"
        exit_button = DirectButton(
            text="Exit",
            pos=(0, 0, -0.4),
            scale=0.1,
            command=self.exit_game,
            parent=self.game.aspect2d
        )
        self.elements.append(exit_button)
        
    def exit(self):
        """Выход из экрана смерти"""
        for element in self.elements:
            if hasattr(element, 'destroy'):
                element.destroy()
            elif hasattr(element, 'removeNode'):
                element.removeNode()
        self.elements.clear()
        
    def restart_game(self):
        """Перезапуск игры"""
        self.game.state_manager.change_state("game")
        
    def go_to_main_menu(self):
        """Переход в главное меню"""
        self.game.state_manager.change_state("start")
        
    def exit_game(self):
        """Выход из игры"""
        self.game.quit()
