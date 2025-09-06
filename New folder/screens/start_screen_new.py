#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.ui import BaseScreen

class StartScreen(BaseScreen):
    """Стартовый экран игры"""
    
    def __init__(self, game):
        super().__init__(game)
        
    def enter(self):
        """Вход в состояние стартового экрана"""
        self.create_background(0.9)
        self.create_title("Panda3D Game", (0, 0.3), 0.15, (1, 1, 1, 1))
        self.create_subtitle("Isometric Adventure", (0, 0.1), 0.08, (0.8, 0.8, 0.8, 1))
        
        # Кнопки
        self.create_button("New Game", self.start_new_game, (0, 0, -0.1))
        self.create_button("Settings", self.open_settings, (0, 0, -0.25))
        self.create_button("Exit", self.exit_game, (0, 0, -0.4), 
                          frame_color=(0.8, 0.2, 0.2, 1))
        
    def start_new_game(self):
        """Начать новую игру"""
        self.game.state_manager.change_state("game")
        
    def open_settings(self):
        """Открыть настройки"""
        self.game.state_manager.change_state("settings")
        
    def exit_game(self):
        """Выход из игры"""
        self.game.quit()
