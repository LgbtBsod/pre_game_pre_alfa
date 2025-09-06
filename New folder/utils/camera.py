#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from panda3d.core import Vec3, Point3

class CameraController:
    """Контроллер камеры с различными режимами"""
    
    def __init__(self, game):
        self.game = game
        self.camera_angle = 45
        self.camera_distance = 20
        self.camera_height = 15
        self.camera_mode = "follow"  # "follow" или "free"
        self.free_camera_speed = 10.0
        self.free_camera_pos = Vec3(0, 0, 15)
        
    def setup_isometric_camera(self, target_pos=None):
        """Настройка изометрической камеры"""
        if target_pos is None:
            target_pos = Point3(0, 0, 0)
            
        # Вычисляем позицию камеры
        rad_angle = math.radians(self.camera_angle)
        camera_x = target_pos.getX() + self.camera_distance * math.cos(rad_angle)
        camera_y = target_pos.getY() + self.camera_distance * math.sin(rad_angle)
        camera_z = target_pos.getZ() + self.camera_height
        
        # Устанавливаем позицию и направление камеры
        self.game.camera.setPos(camera_x, camera_y, camera_z)
        self.game.camera.lookAt(target_pos)
        
    def setup_free_camera(self):
        """Настройка свободной камеры"""
        self.game.camera.setPos(self.free_camera_pos)
        self.game.camera.setHpr(0, -30, 0)
        
    def rotate_camera(self, direction):
        """Поворот камеры"""
        if self.camera_mode == "follow":
            self.camera_angle += direction * 5
            if self.camera_angle < 0:
                self.camera_angle += 360
            elif self.camera_angle >= 360:
                self.camera_angle -= 360
                
    def move_free_camera(self, direction):
        """Движение свободной камеры"""
        if self.camera_mode != "free":
            return
            
        dt = 0.016  # Фиксированная скорость
        
        if direction == "forward":
            self.free_camera_pos.y += self.free_camera_speed * dt
        elif direction == "backward":
            self.free_camera_pos.y -= self.free_camera_speed * dt
        elif direction == "left":
            self.free_camera_pos.x -= self.free_camera_speed * dt
        elif direction == "right":
            self.free_camera_pos.x += self.free_camera_speed * dt
        elif direction == "up":
            self.free_camera_pos.z += self.free_camera_speed * dt
        elif direction == "down":
            self.free_camera_pos.z -= self.free_camera_speed * dt
            
        self.setup_free_camera()
        
    def toggle_mode(self):
        """Переключение режима камеры"""
        if self.camera_mode == "follow":
            self.camera_mode = "free"
            self.setup_free_camera()
        else:
            self.camera_mode = "follow"
            
    def update(self, target_pos=None):
        """Обновление камеры"""
        if self.camera_mode == "follow" and target_pos:
            self.setup_isometric_camera(target_pos)
