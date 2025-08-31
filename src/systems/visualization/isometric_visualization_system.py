#!/usr/bin/env python3
"""Система изометрической визуализации
Специализированная система для изометрической проекции игры"""

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from panda3d.core import (
    NodePath, PandaNode, GeomNode, Geom, GeomTriangles, GeomVertexData,
    GeomVertexFormat, GeomVertexWriter, TransparencyAttrib, ColorAttrib,
    Vec3, Vec4, Point3, TransformState, AntialiasAttrib, Material,
    AmbientLight, DirectionalLight, PointLight, Spotlight, Fog,
    BillboardEffect, CompassEffect, TransparencyAttrib, DepthTestAttrib,
    DepthWriteAttrib, CullFaceAttrib, Shader, ShaderAttrib, Camera,
    PerspectiveLens, OrthographicLens, Point3, LVector3
)

from ...core.constants import EmotionType, constants_manager
from ...core.constants_extended import (
    GEOMETRIC_SHAPE_CONSTANTS, EMOTION_VISUALIZATION_CONSTANTS
)
from ...core.architecture import BaseComponent

logger = logging.getLogger(__name__)

class IsometricCamera:
    """Изометрическая камера"""
    
    def __init__(self, distance: float = 20.0, angle: float = 45.0):
        self.distance = distance
        self.angle = angle
        self.camera_np = None
        self.target = Vec3(0, 0, 0)
        
        logger.info("Изометрическая камера инициализирована")
    
    def setup_camera(self, scene_root: NodePath) -> NodePath:
        """Настройка изометрической камеры"""
        try:
            # Создание камеры
            camera = Camera("isometric_camera")
            
            # Настройка линзы для изометрии
            lens = OrthographicLens()
            lens.setFilmSize(40, 30)  # Размер области видимости
            lens.setNearFar(-100, 100)
            camera.setLens(lens)
            
            # Создание NodePath для камеры
            self.camera_np = scene_root.attachNewNode(camera)
            
            # Позиционирование камеры для изометрии
            self._update_camera_position()
            
            # Настройка камеры как активной
            scene_root.setCamera(self.camera_np)
            
            logger.info("Изометрическая камера настроена")
            return self.camera_np
            
        except Exception as e:
            logger.error(f"Ошибка настройки изометрической камеры: {e}")
            return NodePath()
    
    def _update_camera_position(self):
        """Обновление позиции камеры"""
        try:
            if self.camera_np:
                # Изометрические углы
                x = self.distance * math.cos(math.radians(self.angle))
                y = self.distance * math.sin(math.radians(self.angle))
                z = self.distance * 0.7  # Высота для изометрии
                
                # Позиция камеры
                camera_pos = self.target + Vec3(x, y, z)
                self.camera_np.setPos(camera_pos)
                
                # Направление на цель
                self.camera_np.lookAt(self.target)
                
        except Exception as e:
            logger.error(f"Ошибка обновления позиции камеры: {e}")
    
    def set_target(self, target: Vec3):
        """Установка цели камеры"""
        self.target = target
        self._update_camera_position()
    
    def set_distance(self, distance: float):
        """Установка расстояния камеры"""
        self.distance = distance
        self._update_camera_position()
    
    def set_angle(self, angle: float):
        """Установка угла камеры"""
        self.angle = angle
        self._update_camera_position()

class IsometricShapeGenerator:
    """Генератор изометрических фигур"""
    
    def __init__(self):
        self.constants = GEOMETRIC_SHAPE_CONSTANTS
        self.shape_cache: Dict[str, GeomNode] = {}
        
        logger.info("Генератор изометрических фигур инициализирован")
    
    def create_isometric_cube(self, size: float = 1.0) -> GeomNode:
        """Создание изометрического куба"""
        try:
            cache_key = f"iso_cube_{size}"
            if cache_key in self.shape_cache:
                return self.shape_cache[cache_key]
            
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('isometric_cube', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            half_size = size / 2
            
            # Вершины изометрического куба (с учетом изометрии)
            vertices = [
                # Передняя грань (наклонена для изометрии)
                (-half_size, -half_size, half_size), (half_size, -half_size, half_size),
                (half_size, half_size, half_size), (-half_size, half_size, half_size),
                # Задняя грань
                (-half_size, -half_size, -half_size), (half_size, -half_size, -half_size),
                (half_size, half_size, -half_size), (-half_size, half_size, -half_size)
            ]
            
            # Нормали для изометрии
            normals = [
                (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),  # Передняя
                (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),  # Задняя
                (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),  # Верхняя
                (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),  # Нижняя
                (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),  # Правая
                (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0)  # Левая
            ]
            
            # Добавление вершин
            for i in range(6):  # 6 граней
                for j in range(4):  # 4 вершины на грань
                    idx = i * 4 + j
                    if idx < len(vertices):
                        v = vertices[idx]
                        n = normals[idx]
                        vertex.addData3(v[0], v[1], v[2])
                        normal.addData3(n[0], n[1], n[2])
                        color.addData4(1, 1, 1, 1)
            
            # Создание треугольников
            prim = GeomTriangles(Geom.UHStatic)
            
            # Индексы для каждой грани (2 треугольника на грань)
            indices = [
                0, 1, 2, 0, 2, 3,  # Передняя
                5, 4, 7, 5, 7, 6,  # Задняя
                3, 2, 6, 3, 6, 7,  # Верхняя
                4, 5, 1, 4, 1, 0,  # Нижняя
                1, 5, 6, 1, 6, 2,  # Правая
                4, 0, 3, 4, 3, 7   # Левая
            ]
            
            for i in range(0, len(indices), 3):
                prim.addVertices(indices[i], indices[i+1], indices[i+2])
            
            prim.closePrimitive()
            
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            
            node = GeomNode('isometric_cube')
            node.addGeom(geom)
            
            self.shape_cache[cache_key] = node
            return node
            
        except Exception as e:
            logger.error(f"Ошибка создания изометрического куба: {e}")
            return self._create_fallback_shape()
    
    def create_isometric_cylinder(self, radius: float = 0.5, height: float = 1.0) -> GeomNode:
        """Создание изометрического цилиндра"""
        try:
            cache_key = f"iso_cylinder_{radius}_{height}"
            if cache_key in self.shape_cache:
                return self.shape_cache[cache_key]
            
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('isometric_cylinder', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            segments = 12
            half_height = height / 2
            
            # Верхняя и нижняя грани
            for i in range(segments):
                angle = 2 * math.pi * i / segments
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                
                # Верхняя грань
                vertex.addData3(x, y, half_height)
                normal.addData3(0, 0, 1)
                color.addData4(1, 1, 1, 1)
                
                # Нижняя грань
                vertex.addData3(x, y, -half_height)
                normal.addData3(0, 0, -1)
                color.addData4(1, 1, 1, 1)
            
            # Центры граней
            vertex.addData3(0, 0, half_height)
            normal.addData3(0, 0, 1)
            color.addData4(1, 1, 1, 1)
            
            vertex.addData3(0, 0, -half_height)
            normal.addData3(0, 0, -1)
            color.addData4(1, 1, 1, 1)
            
            # Создание треугольников
            prim = GeomTriangles(Geom.UHStatic)
            
            # Верхняя и нижняя грани
            top_center = segments * 2
            bottom_center = segments * 2 + 1
            
            for i in range(segments):
                v1 = i * 2
                v2 = ((i + 1) % segments) * 2
                
                # Верхняя грань
                prim.addVertices(top_center, v1, v2)
                # Нижняя грань
                prim.addVertices(bottom_center, v2 + 1, v1 + 1)
            
            prim.closePrimitive()
            
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            
            node = GeomNode('isometric_cylinder')
            node.addGeom(geom)
            
            self.shape_cache[cache_key] = node
            return node
            
        except Exception as e:
            logger.error(f"Ошибка создания изометрического цилиндра: {e}")
            return self._create_fallback_shape()
    
    def _create_fallback_shape(self) -> GeomNode:
        """Создание резервной фигуры"""
        try:
            return self.create_isometric_cube(1.0)
        except Exception as e:
            logger.error(f"Ошибка создания резервной фигуры: {e}")
            node = GeomNode('fallback')
            return node

class IsometricEmotionVisualizer:
    """Визуализатор эмоций для изометрии"""
    
    def __init__(self):
        self.constants = EMOTION_VISUALIZATION_CONSTANTS
        self.emotion_colors = constants_manager.get_emotion_colors()
        self.active_emotions: Dict[str, Any] = {}
        
        logger.info("Визуализатор изометрических эмоций инициализирован")
    
    def create_isometric_emotion_disc(self, emotion_data: Any) -> NodePath:
        """Создание изометрического диска эмоции"""
        try:
            # Создание геометрии диска
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('isometric_emotion_disc', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            radius = emotion_data.size
            segments = 16
            
            # Центр диска
            vertex.addData3(0, 0, 0)
            normal.addData3(0, 0, 1)
            color.addData4(*emotion_data.color)
            
            # Вершины окружности (с учетом изометрии)
            for i in range(segments + 1):
                angle = 2 * math.pi * i / segments
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius * 0.7  # Сжатие по Y для изометрии
                
                vertex.addData3(x, y, 0)
                normal.addData3(0, 0, 1)
                color.addData4(*emotion_data.color)
            
            # Создание треугольников
            prim = GeomTriangles(Geom.UHStatic)
            
            for i in range(segments):
                prim.addVertices(0, i + 1, i + 2)
            
            prim.closePrimitive()
            
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            
            node = GeomNode('isometric_emotion_disc')
            node.addGeom(geom)
            
            # Создание NodePath
            np = NodePath(node)
            
            # Настройка прозрачности для изометрии
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setDepthWrite(False)
            np.setDepthTest(False)
            
            # Позиционирование для изометрии
            np.setPos(emotion_data.position)
            np.setZ(emotion_data.position.z + self.constants["disc_height"])
            
            # Поворот для изометрической проекции
            np.setHpr(0, -45, 0)  # Наклон для изометрии
            
            return np
            
        except Exception as e:
            logger.error(f"Ошибка создания изометрического диска эмоции: {e}")
            return NodePath()

class IsometricVisualizationSystem(BaseComponent):
    """Система изометрической визуализации"""
    
    def __init__(self):
        super().__init__()
        self.shape_generator = IsometricShapeGenerator()
        self.emotion_visualizer = IsometricEmotionVisualizer()
        self.camera = IsometricCamera()
        self.entity_visuals: Dict[str, NodePath] = {}
        self.emotion_visuals: Dict[str, NodePath] = {}
        self.scene_root: Optional[NodePath] = None
        
        logger.info("Система изометрической визуализации инициализирована")
    
    def initialize(self):
        """Инициализация системы"""
        try:
            # Создание корневого узла сцены
            self.scene_root = NodePath("isometric_scene")
            
            # Настройка изометрической камеры
            self.camera.setup_camera(self.scene_root)
            
            # Настройка освещения для изометрии
            self._setup_isometric_lighting()
            
            logger.info("Система изометрической визуализации инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы изометрической визуализации: {e}")
            return False
    
    def _setup_isometric_lighting(self):
        """Настройка освещения для изометрии"""
        try:
            # Ambient свет для равномерного освещения
            ambient_light = AmbientLight("isometric_ambient")
            ambient_light.setColor((0.4, 0.4, 0.4, 1))
            ambient_np = self.scene_root.attachNewNode(ambient_light)
            self.scene_root.setLight(ambient_np)
            
            # Directional свет для изометрии
            directional_light = DirectionalLight("isometric_directional")
            directional_light.setColor((0.6, 0.6, 0.6, 1))
            directional_np = self.scene_root.attachNewNode(directional_light)
            directional_np.setHpr(45, -45, 0)  # Угол для изометрии
            self.scene_root.setLight(directional_np)
            
        except Exception as e:
            logger.error(f"Ошибка настройки изометрического освещения: {e}")
    
    def create_isometric_entity_visual(self, entity_id: str, shape_type: str, 
                                     position: Vec3, color: Vec4) -> bool:
        """Создание изометрической визуализации сущности"""
        try:
            # Удаление существующей визуализации
            if entity_id in self.entity_visuals:
                self.remove_entity_visual(entity_id)
            
            # Создание изометрической фигуры
            shape_node = None
            if shape_type == "cube":
                shape_node = self.shape_generator.create_isometric_cube(1.0)
            elif shape_type == "cylinder":
                shape_node = self.shape_generator.create_isometric_cylinder(0.5, 1.0)
            else:
                shape_node = self.shape_generator.create_isometric_cube(1.0)
            
            if shape_node:
                # Создание NodePath
                np = NodePath(shape_node)
                
                # Применение визуальных свойств
                np.setPos(position)
                np.setColor(*color)
                
                # Добавление к сцене
                np.reparentTo(self.scene_root)
                self.entity_visuals[entity_id] = np
                
                logger.info(f"Создана изометрическая визуализация сущности {entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка создания изометрической визуализации сущности: {e}")
            return False
    
    def create_isometric_emotion_visual(self, entity_id: str, emotion_type: EmotionType,
                                      position: Vec3, intensity: float) -> bool:
        """Создание изометрической визуализации эмоции"""
        try:
            # Удаление существующей визуализации эмоции
            if entity_id in self.emotion_visuals:
                self.remove_emotion_visual(entity_id)
            
            # Создание данных эмоции
            emotion_data = type('EmotionData', (), {
                'entity_id': entity_id,
                'emotion_type': emotion_type,
                'intensity': intensity,
                'position': position,
                'color': self.emotion_visualizer.emotion_colors.get(emotion_type, (1, 1, 1, 1)),
                'size': self.constants["disc_radius"] * intensity,
                'duration': 5.0
            })()
            
            # Создание изометрического диска эмоции
            emotion_np = self.emotion_visualizer.create_isometric_emotion_disc(emotion_data)
            
            if emotion_np and not emotion_np.isEmpty():
                # Добавление к сцене
                emotion_np.reparentTo(self.scene_root)
                self.emotion_visuals[entity_id] = emotion_np
                
                logger.info(f"Создана изометрическая визуализация эмоции для {entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка создания изометрической визуализации эмоции: {e}")
            return False
    
    def update_entity_visual(self, entity_id: str, position: Vec3):
        """Обновление изометрической визуализации сущности"""
        try:
            if entity_id in self.entity_visuals:
                np = self.entity_visuals[entity_id]
                np.setPos(position)
                
        except Exception as e:
            logger.error(f"Ошибка обновления изометрической визуализации сущности: {e}")
    
    def remove_entity_visual(self, entity_id: str):
        """Удаление изометрической визуализации сущности"""
        try:
            if entity_id in self.entity_visuals:
                np = self.entity_visuals[entity_id]
                np.removeNode()
                del self.entity_visuals[entity_id]
                
        except Exception as e:
            logger.error(f"Ошибка удаления изометрической визуализации сущности: {e}")
    
    def remove_emotion_visual(self, entity_id: str):
        """Удаление изометрической визуализации эмоции"""
        try:
            if entity_id in self.emotion_visuals:
                np = self.emotion_visuals[entity_id]
                np.removeNode()
                del self.emotion_visuals[entity_id]
                
        except Exception as e:
            logger.error(f"Ошибка удаления изометрической визуализации эмоции: {e}")
    
    def get_scene_root(self) -> Optional[NodePath]:
        """Получение корневого узла изометрической сцены"""
        return self.scene_root
    
    def get_camera(self) -> IsometricCamera:
        """Получение изометрической камеры"""
        return self.camera
    
    def update(self, delta_time: float):
        """Обновление системы изометрической визуализации"""
        try:
            # Обновление камеры если необходимо
            pass
                
        except Exception as e:
            logger.error(f"Ошибка обновления системы изометрической визуализации: {e}")
    
    def cleanup(self):
        """Очистка системы изометрической визуализации"""
        try:
            # Удаление всех визуализаций
            for entity_id in list(self.entity_visuals.keys()):
                self.remove_entity_visual(entity_id)
            
            for entity_id in list(self.emotion_visuals.keys()):
                self.remove_emotion_visual(entity_id)
            
            # Удаление корневого узла
            if self.scene_root:
                self.scene_root.removeNode()
                self.scene_root = None
            
            logger.info("Система изометрической визуализации очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы изометрической визуализации: {e}")

logger.info("Система изометрической визуализации загружена")
