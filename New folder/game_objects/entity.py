#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from utils.geometry import GeometryUtils

class Entity:
    """Базовый класс для всех игровых сущностей"""
    
    def __init__(self, game, x=0, y=0, z=0, color=(1, 1, 1, 1)):
        self.game = game
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.node = None
        self.speed = 5.0
        self.health = 100
        self.max_health = 100
        self.attack_damage = 20
        self.attack_range = 2.0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 1.0
        
    def create_visual(self):
        """Создание визуального представления (переопределяется в наследниках)"""
        pass
        
    def move_to(self, x, y, z=None):
        """Перемещение к указанной позиции"""
        self.x = x
        self.y = y
        if z is not None:
            self.z = z
            
        if self.node:
            self.node.setPos(self.x, self.y, self.z)
            
    def get_distance_to(self, other):
        """Получение расстояния до другой сущности"""
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
        
    def is_alive(self):
        """Проверка, жива ли сущность"""
        return self.health > 0
        
    def take_damage(self, damage):
        """Получение урона"""
        self.health = max(0, self.health - damage)
        
    def heal(self, amount):
        """Лечение"""
        self.health = min(self.max_health, self.health + amount)
        
    def attack(self, target):
        """Атака цели"""
        if self.attack_cooldown > 0:
            return False
            
        distance = self.get_distance_to(target)
        if distance <= self.attack_range:
            target.take_damage(self.attack_damage)
            self.attack_cooldown = self.attack_cooldown_time
            return True
        return False
        
    def update_cooldown(self, dt):
        """Обновление кулдауна атаки"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
    def destroy(self):
        """Уничтожение сущности"""
        if self.node:
            self.node.removeNode()
            self.node = None
