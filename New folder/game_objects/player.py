#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from utils.geometry import GeometryUtils
from game_objects.entity import Entity

class Player(Entity):
    """Класс игрока"""
    
    def __init__(self, game, x=0, y=0, z=0):
        super().__init__(game, x, y, z, (0.2, 0.8, 0.2, 1))  # Зеленый цвет
        self.speed = 8.0
        self.health = 100
        self.max_health = 100
        self.mana = 100
        self.max_mana = 100
        self.stamina = 100
        self.max_stamina = 100
        self.mana_regen_rate = 5.0
        self.stamina_regen_rate = 10.0
        self.attack_damage = 25
        self.attack_range = 3.0
        
    def create_visual(self):
        """Создание визуального представления игрока"""
        player = self.game.render.attachNewNode("player")

        # Основное тело (куб)
        GeometryUtils.create_simple_cube(player, "body", 0, 0, 0.5, 0.6, 0.6, 0.6, self.color)

        # Голова
        head_color = (self.color[0] * 0.8, self.color[1] * 0.8, self.color[2] * 0.8, self.color[3])
        GeometryUtils.create_simple_cube(player, "head", 0, 0, 1.2, 0.4, 0.4, 0.4, head_color)

        # Ноги
        leg_color = (self.color[0] * 0.6, self.color[1] * 0.6, self.color[2] * 0.6, self.color[3])
        GeometryUtils.create_simple_cube(player, "leg1", -0.2, 0, 0.2, 0.2, 0.2, 0.4, leg_color)
        GeometryUtils.create_simple_cube(player, "leg2", 0.2, 0, 0.2, 0.2, 0.2, 0.4, leg_color)

        # Руки
        arm_color = (self.color[0] * 0.7, self.color[1] * 0.7, self.color[2] * 0.7, self.color[3])
        GeometryUtils.create_simple_cube(player, "arm1", -0.4, 0, 0.8, 0.2, 0.2, 0.4, arm_color)
        GeometryUtils.create_simple_cube(player, "arm2", 0.4, 0, 0.8, 0.2, 0.2, 0.4, arm_color)

        player.setPos(self.x, self.y, self.z)
        self.node = player
        return player
        
    def move(self, dx, dy, dt=0.016):
        """Движение игрока"""
        # Фиксированная скорость без привязки к FPS
        move_distance = self.speed * dt
        
        new_x = self.x + dx * move_distance
        new_y = self.y + dy * move_distance
        
        # Ограничиваем движение границами карты
        map_size = 200
        new_x = max(-map_size, min(map_size, new_x))
        new_y = max(-map_size, min(map_size, new_y))
        
        self.move_to(new_x, new_y)
        
    def restore_mana(self, amount):
        """Восстановление маны"""
        self.mana = min(self.max_mana, self.mana + amount)

    def restore_stamina(self, amount):
        """Восстановление выносливости"""
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def use_mana(self, amount):
        """Использование маны"""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def use_stamina(self, amount):
        """Использование выносливости"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def update_cooldown(self, dt):
        """Обновление кулдауна атаки и восстановление ресурсов"""
        super().update_cooldown(dt)
        
        # Восстановление маны и выносливости
        self.restore_mana(self.mana_regen_rate * dt)
        self.restore_stamina(self.stamina_regen_rate * dt)
