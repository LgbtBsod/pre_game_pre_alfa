#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LEGACY МЕНЕДЖЕР СОСТОЯНИЙ ИГРЫ
Используется для обратной совместимости
Рекомендуется использовать core/game_state_manager.py
"""

from core.game_state_manager import GameStateManager as NewGameStateManager, GameState

class GameStateManager:
    """LEGACY Менеджер состояний игры"""
    
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.previous_state = None
        
        # Создаем новый менеджер для расширенного функционала
        self.new_manager = NewGameStateManager()
    
    def add_state(self, name, state):
        """Добавить состояние"""
        self.states[name] = state
    
    def change_state(self, name):
        """Изменить состояние"""
        if self.current_state:
            self.states[self.current_state].exit()
            self.previous_state = self.current_state
        
        self.current_state = name
        if name in self.states:
            self.states[name].enter()
    
    def get_current_state(self):
        """Получить текущее состояние"""
        return self.current_state
    
    def get_previous_state(self):
        """Получить предыдущее состояние"""
        return self.previous_state
