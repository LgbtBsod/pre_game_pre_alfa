#!/usr/bin/env python3
"""Система визуализации - геометрические фигуры и эмоции
Обеспечивает визуализацию сущностей и эмоций с помощью геометрических фигур"""

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
    DepthWriteAttrib, CullFaceAttrib, Shader, ShaderAttrib
)

from ...core.constants import EmotionType, constants_manager
from ...core.constants_extended import (
    GEOMETRIC_SHAPE_CONSTANTS, EMOTION_VISUALIZATION_CONSTANTS
)
from ...core.base_component import BaseComponent
from ...core.component_type import ComponentType, Priority

logger = logging.getLogger(__name__)

class ShapeType(Enum):
    """Типы геометрических фигур"""
    SPHERE = "sphere"
    CUBE = "cube"
    CYLINDER = "cylinder"
    DODECAHEDRON = "dodecahedron"
    OCTAHEDRON = "octahedron"
    TORUS = "torus"
    PYRAMID = "pyramid"
    PRISM = "prism"

class EmotionVisualizationType(Enum):
    """Типы визуализации эмоций"""
    DISC = "disc"
    AURA = "aura"
    PARTICLES = "particles"
    WAVES = "waves"
    PULSE = "pulse"

@dataclass
class EntityVisualData:
    """Визуальные данные сущности"""
    entity_id: str
    shape_type: ShapeType
    position: Vec3
    rotation: Vec3
    scale: Vec3
    color: Vec4
    material: Optional[str] = None
    animation: Optional[str] = None
    effects: List[str] = field(default_factory=list)

@dataclass
class EmotionVisualData:
    """Визуальные данные эмоции"""
    entity_id: str
    emotion_type: EmotionType
    intensity: float
    position: Vec3
    visualization_type: EmotionVisualizationType
    color: Vec4
    size: float
    duration: float
    start_time: float = field(default_factory=time.time)

class GeometricShapeGenerator:
    """Генератор геометрических фигур"""
    
    def __init__(self):
        self.constants = GEOMETRIC_SHAPE_CONSTANTS
        self.shape_cache: Dict[str, GeomNode] = {}
        
        logger.info("Генератор геометрических фигур инициализирован")
    
    def create_sphere(self, radius: float = 0.5, segments: int = 16) -> GeomNode:
        """Создание сферы"""
        try:
            cache_key = f"sphere_{radius}_{segments}"
            if cache_key in self.shape_cache:
                return self.shape_cache[cache_key]
            
            # Создание геометрии сферы
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('sphere', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            # Генерация вершин
            for i in range(segments + 1):
                lat = math.pi * (-0.5 + float(i) / segments)
                for j in range(segments):
                    lon = 2 * math.pi * float(j) / segments
                    
                    x = math.cos(lat) * math.cos(lon) * radius
                    y = math.cos(lat) * math.sin(lon) * radius
                    z = math.sin(lat) * radius
                    
                    vertex.addData3(x, y, z)
                    normal.addData3(x/radius, y/radius, z/radius)
                    color.addData4(1, 1, 1, 1)
            
            # Создание треугольников
            prim = GeomTriangles(Geom.UHStatic)
            
            for i in range(segments):
                for j in range(segments):
                    v1 = i * segments + j
                    v2 = i * segments + (j + 1) % segments
                    v3 = (i + 1) * segments + j
                    v4 = (i + 1) * segments + (j + 1) % segments
                    
                    prim.addVertices(v1, v2, v3)
                    prim.addVertices(v2, v4, v3)
            
            prim.closePrimitive()
            
            # Создание геометрии
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            
            node = GeomNode('sphere')
            node.addGeom(geom)
            
            self.shape_cache[cache_key] = node
            return node
            
        except Exception as e:
            logger.error(f"Ошибка создания сферы: {e}")
            return self._create_fallback_shape()
    
    def create_cube(self, size: float = 1.0) -> GeomNode:
        """Создание куба"""
        try:
            cache_key = f"cube_{size}"
            if cache_key in self.shape_cache:
                return self.shape_cache[cache_key]
            
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('cube', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            half_size = size / 2
            
            # Вершины куба
            vertices = [
                # Передняя грань
                (-half_size, -half_size, half_size), (half_size, -half_size, half_size),
                (half_size, half_size, half_size), (-half_size, half_size, half_size),
                # Задняя грань
                (-half_size, -half_size, -half_size), (half_size, -half_size, -half_size),
                (half_size, half_size, -half_size), (-half_size, half_size, -half_size)
            ]
            
            # Нормали для каждой грани
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
            
            node = GeomNode('cube')
            node.addGeom(geom)
            
            self.shape_cache[cache_key] = node
            return node
            
        except Exception as e:
            logger.error(f"Ошибка создания куба: {e}")
            return self._create_fallback_shape()
    
    def create_cylinder(self, radius: float = 0.5, height: float = 1.0, segments: int = 12) -> GeomNode:
        """Создание цилиндра"""
        try:
            cache_key = f"cylinder_{radius}_{height}_{segments}"
            if cache_key in self.shape_cache:
                return self.shape_cache[cache_key]
            
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('cylinder', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
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
            
            # Боковые грани
            for i in range(segments):
                angle1 = 2 * math.pi * i / segments
                angle2 = 2 * math.pi * (i + 1) / segments
                
                x1 = math.cos(angle1) * radius
                y1 = math.sin(angle1) * radius
                x2 = math.cos(angle2) * radius
                y2 = math.sin(angle2) * radius
                
                # Боковые вершины
                vertex.addData3(x1, y1, half_height)
                normal.addData3(x1/radius, y1/radius, 0)
                color.addData4(1, 1, 1, 1)
                
                vertex.addData3(x1, y1, -half_height)
                normal.addData3(x1/radius, y1/radius, 0)
                color.addData4(1, 1, 1, 1)
                
                vertex.addData3(x2, y2, half_height)
                normal.addData3(x2/radius, y2/radius, 0)
                color.addData4(1, 1, 1, 1)
                
                vertex.addData3(x2, y2, -half_height)
                normal.addData3(x2/radius, y2/radius, 0)
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
            
            # Боковые грани
            side_start = segments * 2 + 2
            for i in range(segments):
                base = side_start + i * 4
                prim.addVertices(base, base + 1, base + 2)
                prim.addVertices(base + 1, base + 3, base + 2)
            
            prim.closePrimitive()
            
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            
            node = GeomNode('cylinder')
            node.addGeom(geom)
            
            self.shape_cache[cache_key] = node
            return node
            
        except Exception as e:
            logger.error(f"Ошибка создания цилиндра: {e}")
            return self._create_fallback_shape()
    
    def create_dodecahedron(self, radius: float = 0.5) -> GeomNode:
        """Создание додекаэдра"""
        try:
            cache_key = f"dodecahedron_{radius}"
            if cache_key in self.shape_cache:
                return self.shape_cache[cache_key]
            
            # Золотое сечение
            phi = (1 + math.sqrt(5)) / 2
            
            # Вершины додекаэдра
            vertices = []
            for x in [-1, 1]:
                for y in [-1, 1]:
                    for z in [-1, 1]:
                        vertices.append(Vec3(x, y, z))
            
            for i in range(3):
                for j in range(2):
                    v = [0, 0, 0]
                    v[i] = phi if j == 0 else -phi
                    v[(i + 1) % 3] = 1 / phi
                    v[(i + 2) % 3] = 0
                    vertices.append(Vec3(v[0], v[1], v[2]))
                    
                    v = [0, 0, 0]
                    v[i] = phi if j == 0 else -phi
                    v[(i + 1) % 3] = -1 / phi
                    v[(i + 2) % 3] = 0
                    vertices.append(Vec3(v[0], v[1], v[2]))
            
            # Нормализация и масштабирование
            for i in range(len(vertices)):
                vertices[i].normalize()
                vertices[i] *= radius
            
            # Создание граней (12 пятиугольников)
            faces = [
                [0, 8, 1, 13, 12],
                [0, 12, 4, 14, 2],
                [0, 2, 6, 10, 8],
                [1, 8, 10, 11, 9],
                [1, 9, 3, 15, 13],
                [2, 14, 7, 15, 6],
                [3, 9, 11, 5, 7],
                [3, 15, 7, 14, 4],
                [4, 12, 13, 15, 3],
                [5, 11, 10, 6, 15],
                [5, 7, 15, 6, 10],
                [5, 10, 6, 2, 14]
            ]
            
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('dodecahedron', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            # Добавление вершин
            for v in vertices:
                vertex.addData3(v.x, v.y, v.z)
                normal.addData3(v.x/radius, v.y/radius, v.z/radius)
                color.addData4(1, 1, 1, 1)
            
            # Создание треугольников
            prim = GeomTriangles(Geom.UHStatic)
            
            for face in faces:
                # Разбиение пятиугольника на треугольники
                for i in range(1, len(face) - 1):
                    prim.addVertices(face[0], face[i], face[i + 1])
            
            prim.closePrimitive()
            
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            
            node = GeomNode('dodecahedron')
            node.addGeom(geom)
            
            self.shape_cache[cache_key] = node
            return node
            
        except Exception as e:
            logger.error(f"Ошибка создания додекаэдра: {e}")
            return self._create_fallback_shape()
    
    def create_octahedron(self, radius: float = 0.5) -> GeomNode:
        """Создание октаэдра"""
        try:
            cache_key = f"octahedron_{radius}"
            if cache_key in self.shape_cache:
                return self.shape_cache[cache_key]
            
            # Вершины октаэдра
            vertices = [
                Vec3(radius, 0, 0), Vec3(-radius, 0, 0),
                Vec3(0, radius, 0), Vec3(0, -radius, 0),
                Vec3(0, 0, radius), Vec3(0, 0, -radius)
            ]
            
            # Грани (8 треугольников)
            faces = [
                [0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2],
                [1, 2, 4], [1, 4, 3], [1, 3, 5], [1, 5, 2]
            ]
            
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('octahedron', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            # Добавление вершин
            for v in vertices:
                vertex.addData3(v.x, v.y, v.z)
                normal.addData3(v.x/radius, v.y/radius, v.z/radius)
                color.addData4(1, 1, 1, 1)
            
            # Создание треугольников
            prim = GeomTriangles(Geom.UHStatic)
            
            for face in faces:
                prim.addVertices(face[0], face[1], face[2])
            
            prim.closePrimitive()
            
            geom = Geom(vdata)
            geom.addPrimitive(prim)
            
            node = GeomNode('octahedron')
            node.addGeom(geom)
            
            self.shape_cache[cache_key] = node
            return node
            
        except Exception as e:
            logger.error(f"Ошибка создания октаэдра: {e}")
            return self._create_fallback_shape()
    
    def _create_fallback_shape(self) -> GeomNode:
        """Создание резервной фигуры"""
        try:
            # Простой куб как резервная фигура
            return self.create_cube(1.0)
        except Exception as e:
            logger.error(f"Ошибка создания резервной фигуры: {e}")
            # Создание пустого узла
            node = GeomNode('fallback')
            return node

class EmotionVisualizer:
    """Визуализатор эмоций"""
    
    def __init__(self):
        self.constants = EMOTION_VISUALIZATION_CONSTANTS
        self.emotion_colors = constants_manager.get_emotion_colors()
        self.active_emotions: Dict[str, EmotionVisualData] = {}
        
        logger.info("Визуализатор эмоций инициализирован")
    
    def create_emotion_disc(self, emotion_data: EmotionVisualData) -> NodePath:
        """Создание диска эмоции"""
        try:
            # Создание геометрии диска
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData('emotion_disc', format, Geom.UHStatic)
            
            vertex = GeomVertexWriter(vdata, 'vertex')
            normal = GeomVertexWriter(vdata, 'normal')
            color = GeomVertexWriter(vdata, 'color')
            
            radius = emotion_data.size
            segments = 16
            
            # Центр диска
            vertex.addData3(0, 0, 0)
            normal.addData3(0, 0, 1)
            color.addData4(*emotion_data.color)
            
            # Вершины окружности
            for i in range(segments + 1):
                angle = 2 * math.pi * i / segments
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                
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
            
            node = GeomNode('emotion_disc')
            node.addGeom(geom)
            
            # Создание NodePath
            np = NodePath(node)
            
            # Настройка прозрачности
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setDepthWrite(False)
            np.setDepthTest(False)
            
            # Позиционирование
            np.setPos(emotion_data.position)
            np.setZ(emotion_data.position.z + self.constants["disc_height"])
            
            # Эффект пульсации
            if emotion_data.visualization_type == EmotionVisualizationType.PULSE:
                self._add_pulse_effect(np, emotion_data)
            
            return np
            
        except Exception as e:
            logger.error(f"Ошибка создания диска эмоции: {e}")
            return NodePath()
    
    def create_emotion_aura(self, emotion_data: EmotionVisualData) -> NodePath:
        """Создание ауры эмоции"""
        try:
            # Создание нескольких дисков разного размера
            aura_np = NodePath("emotion_aura")
            
            for i in range(3):
                disc_data = EmotionVisualData(
                    entity_id=emotion_data.entity_id,
                    emotion_type=emotion_data.emotion_type,
                    intensity=emotion_data.intensity,
                    position=emotion_data.position,
                    visualization_type=EmotionVisualizationType.DISC,
                    color=emotion_data.color,
                    size=emotion_data.size * (1.0 + i * 0.3),
                    duration=emotion_data.duration
                )
                
                disc_np = self.create_emotion_disc(disc_data)
                disc_np.setTransparency(TransparencyAttrib.MAlpha)
                disc_np.setAlphaScale(0.3 - i * 0.1)
                disc_np.reparentTo(aura_np)
            
            return aura_np
            
        except Exception as e:
            logger.error(f"Ошибка создания ауры эмоции: {e}")
            return NodePath()
    
    def create_emotion_particles(self, emotion_data: EmotionVisualData) -> NodePath:
        """Создание частиц эмоции"""
        try:
            # Простая система частиц
            particles_np = NodePath("emotion_particles")
            
            particle_count = int(emotion_data.intensity * 10)
            
            for i in range(particle_count):
                # Создание маленькой сферы как частицы
                sphere_gen = GeometricShapeGenerator()
                sphere_node = sphere_gen.create_sphere(0.05, 8)
                
                particle_np = NodePath(sphere_node)
                particle_np.setColor(*emotion_data.color)
                particle_np.setTransparency(TransparencyAttrib.MAlpha)
                particle_np.setAlphaScale(0.7)
                
                # Случайное позиционирование вокруг сущности
                import random
                offset = Vec3(
                    random.uniform(-emotion_data.size, emotion_data.size),
                    random.uniform(-emotion_data.size, emotion_data.size),
                    random.uniform(0, emotion_data.size)
                )
                particle_np.setPos(emotion_data.position + offset)
                
                particle_np.reparentTo(particles_np)
            
            return particles_np
            
        except Exception as e:
            logger.error(f"Ошибка создания частиц эмоции: {e}")
            return NodePath()
    
    def _add_pulse_effect(self, np: NodePath, emotion_data: EmotionVisualData):
        """Добавление эффекта пульсации"""
        try:
            # Простая пульсация масштаба
            import random
            
            def pulse_task(task):
                time = globalClock.getFrameTime()
                scale = 1.0 + 0.2 * math.sin(time * self.constants["pulse_frequency"] * 2 * math.pi)
                np.setScale(scale)
                return task.cont
            
            from direct.task import Task
            taskMgr.add(pulse_task, f"pulse_{emotion_data.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка добавления эффекта пульсации: {e}")
    
    def update_emotion(self, emotion_data: EmotionVisualData):
        """Обновление эмоции"""
        try:
            self.active_emotions[emotion_data.entity_id] = emotion_data
            
            # Проверка истечения времени
            current_time = time.time()
            if current_time - emotion_data.start_time > emotion_data.duration:
                self.remove_emotion(emotion_data.entity_id)
                
        except Exception as e:
            logger.error(f"Ошибка обновления эмоции: {e}")
    
    def remove_emotion(self, entity_id: str):
        """Удаление эмоции"""
        try:
            if entity_id in self.active_emotions:
                del self.active_emotions[entity_id]
                
        except Exception as e:
            logger.error(f"Ошибка удаления эмоции: {e}")

class VisualizationSystem(BaseComponent):
    """Система визуализации"""
    
    def __init__(self):
        super().__init__(
            component_id="visualization_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.MEDIUM
        )
        self.shape_generator = GeometricShapeGenerator()
        self.emotion_visualizer = EmotionVisualizer()
        self.entity_visuals: Dict[str, NodePath] = {}
        self.emotion_visuals: Dict[str, NodePath] = {}
        self.scene_root: Optional[NodePath] = None
        
        logger.info("Система визуализации инициализирована")
    
    def initialize(self):
        """Инициализация системы"""
        try:
            # Создание корневого узла сцены
            self.scene_root = NodePath("visualization_scene")
            
            # Настройка освещения
            self._setup_lighting()
            
            logger.info("Система визуализации инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы визуализации: {e}")
            return False
    
    def _setup_lighting(self):
        """Настройка освещения"""
        try:
            # Ambient свет
            ambient_light = AmbientLight("ambient")
            ambient_light.setColor((0.3, 0.3, 0.3, 1))
            ambient_np = self.scene_root.attachNewNode(ambient_light)
            self.scene_root.setLight(ambient_np)
            
            # Directional свет
            directional_light = DirectionalLight("directional")
            directional_light.setColor((0.7, 0.7, 0.7, 1))
            directional_np = self.scene_root.attachNewNode(directional_light)
            directional_np.setHpr(45, -45, 0)
            self.scene_root.setLight(directional_np)
            
        except Exception as e:
            logger.error(f"Ошибка настройки освещения: {e}")
    
    def create_entity_visual(self, entity_id: str, visual_data: EntityVisualData) -> bool:
        """Создание визуализации сущности"""
        try:
            # Удаление существующей визуализации
            if entity_id in self.entity_visuals:
                self.remove_entity_visual(entity_id)
            
            # Создание геометрической фигуры
            shape_node = None
            if visual_data.shape_type == ShapeType.SPHERE:
                shape_node = self.shape_generator.create_sphere(
                    self.constants["sphere"]["radius"],
                    self.constants["sphere"]["segments"]
                )
            elif visual_data.shape_type == ShapeType.CUBE:
                shape_node = self.shape_generator.create_cube(
                    self.constants["cube"]["size"]
                )
            elif visual_data.shape_type == ShapeType.CYLINDER:
                shape_node = self.shape_generator.create_cylinder(
                    self.constants["cylinder"]["radius"],
                    self.constants["cylinder"]["height"],
                    self.constants["cylinder"]["segments"]
                )
            elif visual_data.shape_type == ShapeType.DODECAHEDRON:
                shape_node = self.shape_generator.create_dodecahedron(
                    self.constants["dodecahedron"]["radius"]
                )
            elif visual_data.shape_type == ShapeType.OCTAHEDRON:
                shape_node = self.shape_generator.create_octahedron(
                    self.constants["octahedron"]["radius"]
                )
            else:
                shape_node = self.shape_generator.create_cube(1.0)
            
            if shape_node:
                # Создание NodePath
                np = NodePath(shape_node)
                
                # Применение визуальных свойств
                np.setPos(visual_data.position)
                np.setHpr(visual_data.rotation)
                np.setScale(visual_data.scale)
                np.setColor(*visual_data.color)
                
                # Применение материала
                if visual_data.material:
                    self._apply_material(np, visual_data.material)
                
                # Добавление к сцене
                np.reparentTo(self.scene_root)
                self.entity_visuals[entity_id] = np
                
                logger.info(f"Создана визуализация сущности {entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка создания визуализации сущности: {e}")
            return False
    
    def create_emotion_visual(self, emotion_data: EmotionVisualData) -> bool:
        """Создание визуализации эмоции"""
        try:
            # Удаление существующей визуализации эмоции
            if emotion_data.entity_id in self.emotion_visuals:
                self.remove_emotion_visual(emotion_data.entity_id)
            
            # Создание визуализации в зависимости от типа
            emotion_np = None
            if emotion_data.visualization_type == EmotionVisualizationType.DISC:
                emotion_np = self.emotion_visualizer.create_emotion_disc(emotion_data)
            elif emotion_data.visualization_type == EmotionVisualizationType.AURA:
                emotion_np = self.emotion_visualizer.create_emotion_aura(emotion_data)
            elif emotion_data.visualization_type == EmotionVisualizationType.PARTICLES:
                emotion_np = self.emotion_visualizer.create_emotion_particles(emotion_data)
            else:
                emotion_np = self.emotion_visualizer.create_emotion_disc(emotion_data)
            
            if emotion_np and not emotion_np.isEmpty():
                # Добавление к сцене
                emotion_np.reparentTo(self.scene_root)
                self.emotion_visuals[emotion_data.entity_id] = emotion_np
                
                # Обновление в визуализаторе
                self.emotion_visualizer.update_emotion(emotion_data)
                
                logger.info(f"Создана визуализация эмоции для {emotion_data.entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка создания визуализации эмоции: {e}")
            return False
    
    def _apply_material(self, np: NodePath, material_name: str):
        """Применение материала"""
        try:
            material = Material(material_name)
            
            if material_name == "shiny":
                material.setShininess(100)
                material.setAmbient((0.2, 0.2, 0.2, 1))
                material.setDiffuse((0.8, 0.8, 0.8, 1))
                material.setSpecular((1, 1, 1, 1))
            elif material_name == "metallic":
                material.setShininess(50)
                material.setAmbient((0.1, 0.1, 0.1, 1))
                material.setDiffuse((0.6, 0.6, 0.6, 1))
                material.setSpecular((0.8, 0.8, 0.8, 1))
            elif material_name == "glow":
                material.setEmission((0.3, 0.3, 0.3, 1))
            
            np.setMaterial(material)
            
        except Exception as e:
            logger.error(f"Ошибка применения материала: {e}")
    
    def update_entity_visual(self, entity_id: str, position: Vec3, rotation: Vec3, scale: Vec3):
        """Обновление визуализации сущности"""
        try:
            if entity_id in self.entity_visuals:
                np = self.entity_visuals[entity_id]
                np.setPos(position)
                np.setHpr(rotation)
                np.setScale(scale)
                
        except Exception as e:
            logger.error(f"Ошибка обновления визуализации сущности: {e}")
    
    def remove_entity_visual(self, entity_id: str):
        """Удаление визуализации сущности"""
        try:
            if entity_id in self.entity_visuals:
                np = self.entity_visuals[entity_id]
                np.removeNode()
                del self.entity_visuals[entity_id]
                
        except Exception as e:
            logger.error(f"Ошибка удаления визуализации сущности: {e}")
    
    def remove_emotion_visual(self, entity_id: str):
        """Удаление визуализации эмоции"""
        try:
            if entity_id in self.emotion_visuals:
                np = self.emotion_visuals[entity_id]
                np.removeNode()
                del self.emotion_visuals[entity_id]
                
            self.emotion_visualizer.remove_emotion(entity_id)
            
        except Exception as e:
            logger.error(f"Ошибка удаления визуализации эмоции: {e}")
    
    def get_scene_root(self) -> Optional[NodePath]:
        """Получение корневого узла сцены"""
        return self.scene_root
    
    def update(self, delta_time: float):
        """Обновление системы"""
        try:
            # Обновление эмоций
            current_time = time.time()
            emotions_to_remove = []
            
            for entity_id, emotion_data in self.emotion_visualizer.active_emotions.items():
                if current_time - emotion_data.start_time > emotion_data.duration:
                    emotions_to_remove.append(entity_id)
            
            for entity_id in emotions_to_remove:
                self.remove_emotion_visual(entity_id)
                
        except Exception as e:
            logger.error(f"Ошибка обновления системы визуализации: {e}")
    
    def cleanup(self):
        """Очистка системы"""
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
            
            logger.info("Система визуализации очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы визуализации: {e}")

logger.info("Система визуализации загружена")
