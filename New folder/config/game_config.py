#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

class GameConfig:
    """Конфигурация игры"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_default_config()
        self.load_config()
        
    def load_default_config(self):
        """Загрузка конфигурации по умолчанию"""
        return {
            "graphics": {
                "fullscreen": False,
                "vsync": True,
                "resolution": [1024, 768],
                "fov": 60
            },
            "audio": {
                "master_volume": 1.0,
                "music_volume": 0.7,
                "sfx_volume": 0.8
            },
            "gameplay": {
                "difficulty": "normal",
                "auto_save": True,
                "show_fps": True
            },
            "controls": {
                "camera_sensitivity": 1.0,
                "movement_speed": 1.0
            }
        }
        
    def load_config(self):
        """Загрузка конфигурации из файла"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.merge_config(loaded_config)
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                
    def save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            
    def merge_config(self, loaded_config):
        """Слияние загруженной конфигурации с текущей"""
        for section, values in loaded_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    for key, value in values.items():
                        if key in self.config[section]:
                            self.config[section][key] = value
                else:
                    self.config[section] = values
                    
    def get(self, section, key, default=None):
        """Получение значения конфигурации"""
        return self.config.get(section, {}).get(key, default)
        
    def set(self, section, key, value):
        """Установка значения конфигурации"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
    def get_section(self, section):
        """Получение всей секции конфигурации"""
        return self.config.get(section, {})
