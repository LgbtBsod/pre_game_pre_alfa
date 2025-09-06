#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from panda3d.core import AmbientLight, DirectionalLight, Vec4

class LightingManager:
    """Менеджер освещения сцены"""
    
    def __init__(self, game):
        self.game = game
        self.lights = []
        
    def setup_basic_lighting(self):
        """Настройка базового освещения"""
        self.clear_lighting()
        
        # Окружающий свет
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor(Vec4(0.5, 0.5, 0.5, 1))
        ambient_light_np = self.game.render.attachNewNode(ambient_light)
        self.game.render.setLight(ambient_light_np)
        self.lights.append(ambient_light_np)
        
        # Направленный свет сверху
        directional_light = DirectionalLight('directional_light')
        directional_light.setColor(Vec4(0.8, 0.8, 0.8, 1))
        directional_light_np = self.game.render.attachNewNode(directional_light)
        directional_light_np.setHpr(45, -45, 0)
        self.game.render.setLight(directional_light_np)
        self.lights.append(directional_light_np)
        
        # Дополнительный направленный свет
        directional_light2 = DirectionalLight('directional_light2')
        directional_light2.setColor(Vec4(0.4, 0.4, 0.4, 1))
        directional_light2_np = self.game.render.attachNewNode(directional_light2)
        directional_light2_np.setHpr(-45, -30, 0)
        self.game.render.setLight(directional_light2_np)
        self.lights.append(directional_light2_np)
        
    def clear_lighting(self):
        """Очистка всех источников света"""
        # Удаляем все источники света из рендера
        self.game.render.clearLight()
        
        # Уничтожаем все ноды света
        for light in self.lights:
            if light and not light.isEmpty():
                light.removeNode()
        self.lights.clear()
        
    def add_light(self, light_type, color, position=None, direction=None):
        """Добавление нового источника света"""
        if light_type == "ambient":
            light = AmbientLight('custom_ambient_light')
        elif light_type == "directional":
            light = DirectionalLight('custom_directional_light')
        else:
            return None
            
        light.setColor(color)
        light_np = self.game.render.attachNewNode(light)
        
        if position:
            light_np.setPos(position)
        if direction:
            light_np.setHpr(direction)
            
        self.game.render.setLight(light_np)
        self.lights.append(light_np)
        return light_np
