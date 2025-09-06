#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class InputManager:
    """Менеджер ввода"""
    
    def __init__(self, game):
        self.game = game
        self.key_states = {}
        self.callbacks = {}
        
    def register_key(self, key, callback, event_type="press"):
        """Регистрация клавиши"""
        if event_type == "press":
            self.game.accept(key, callback)
        elif event_type == "release":
            self.game.accept(f"{key}-up", callback)
        elif event_type == "hold":
            self.callbacks[key] = callback
            
    def update(self, dt):
        """Обновление состояния клавиш"""
        for key, callback in self.callbacks.items():
            if self.game.mouseWatcherNode.isButtonDown(key):
                callback(dt)
                
    def is_key_pressed(self, key):
        """Проверка нажатия клавиши"""
        return self.game.mouseWatcherNode.isButtonDown(key)
