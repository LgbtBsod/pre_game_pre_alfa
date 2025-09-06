#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from panda3d.core import CardMaker

class GeometryUtils:
    """Утилиты для создания геометрических объектов"""
    
    @staticmethod
    def create_simple_cube(parent, name, x, y, z, width, height, depth, color):
        """Создание простого куба из 6 граней"""
        cube = parent.attachNewNode(name)

        # Передняя грань
        cm = CardMaker(f"{name}_front")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        front = cube.attachNewNode(cm.generate())
        front.setPos(0, depth/2, 0)
        front.setColor(*color)

        # Задняя грань
        cm = CardMaker(f"{name}_back")
        cm.setFrame(-width/2, width/2, -height/2, height/2)
        back = cube.attachNewNode(cm.generate())
        back.setPos(0, -depth/2, 0)
        back.setHpr(0, 180, 0)
        back.setColor(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, color[3])

        # Левая грань
        cm = CardMaker(f"{name}_left")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        left = cube.attachNewNode(cm.generate())
        left.setPos(-width/2, 0, 0)
        left.setHpr(0, -90, 0)
        left.setColor(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, color[3])

        # Правая грань
        cm = CardMaker(f"{name}_right")
        cm.setFrame(-depth/2, depth/2, -height/2, height/2)
        right = cube.attachNewNode(cm.generate())
        right.setPos(width/2, 0, 0)
        right.setHpr(0, 90, 0)
        right.setColor(color[0] * 0.6, color[1] * 0.6, color[2] * 0.6, color[3])

        # Верхняя грань
        cm = CardMaker(f"{name}_top")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        top = cube.attachNewNode(cm.generate())
        top.setPos(0, 0, height/2)
        top.setHpr(0, 0, -90)
        top.setColor(color[0] * 1.2, color[1] * 1.2, color[2] * 1.2, color[3])

        # Нижняя грань
        cm = CardMaker(f"{name}_bottom")
        cm.setFrame(-width/2, width/2, -depth/2, depth/2)
        bottom = cube.attachNewNode(cm.generate())
        bottom.setPos(0, 0, -height/2)
        bottom.setHpr(0, 0, 90)
        bottom.setColor(color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, color[3])

        cube.setPos(x, y, z)
        return cube
    
    @staticmethod
    def create_sphere(parent, name, x, y, z, radius, color, segments=16):
        """Создание сферы из множества граней"""
        sphere = parent.attachNewNode(name)
        
        for i in range(segments):
            angle = (i / segments) * 360
            next_angle = ((i + 1) / segments) * 360
            
            cm = CardMaker(f"{name}_segment_{i}")
            cm.setFrame(-radius, radius, -radius, radius)
            segment = sphere.attachNewNode(cm.generate())
            segment.setPos(0, 0, 0)
            segment.setHpr(angle, 0, 0)
            segment.setColor(*color)
        
        sphere.setPos(x, y, z)
        return sphere
    
    @staticmethod
    def create_cylinder(parent, name, x, y, z, radius, height, color, segments=8):
        """Создание цилиндра"""
        cylinder = parent.attachNewNode(name)
        
        # Боковые грани
        for i in range(segments):
            angle = (i / segments) * 360
            cm = CardMaker(f"{name}_side_{i}")
            cm.setFrame(-radius, radius, -height/2, height/2)
            side = cylinder.attachNewNode(cm.generate())
            side.setPos(0, 0, 0)
            side.setHpr(angle, 0, 0)
            side.setColor(*color)
        
        # Верхняя и нижняя грани
        cm = CardMaker(f"{name}_top")
        cm.setFrame(-radius, radius, -radius, radius)
        top = cylinder.attachNewNode(cm.generate())
        top.setPos(0, 0, height/2)
        top.setHpr(0, 0, -90)
        top.setColor(*color)
        
        cm = CardMaker(f"{name}_bottom")
        cm.setFrame(-radius, radius, -radius, radius)
        bottom = cylinder.attachNewNode(cm.generate())
        bottom.setPos(0, 0, -height/2)
        bottom.setHpr(0, 0, 90)
        bottom.setColor(*color)
        
        cylinder.setPos(x, y, z)
        return cylinder
