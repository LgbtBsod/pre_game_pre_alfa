#!/usr/bin/env python3
"""Система рендеринга - интеграция с Panda3D
Управление камерами, освещением, материалами и оптимизацией рендеринга"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import math
import time
import threading

# Пробуем разные способы импорта Panda3D
try:
    from panda3d.core import *
    from panda3d.core import NodePath
except ImportError:
    try:
        from direct.showbase.ShowBase import ShowBase
    except ImportError:
        try:
            from direct.showbase import ShowBase
        except ImportError:
            raise ImportError("Не удалось импортировать Panda3D ни одним способом")

try:
    from direct.task import Task
except ImportError:
    Task = None

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState

logger = logging.getLogger(__name__)

# = ТИПЫ РЕНДЕРИНГА

class CameraType(Enum):
    """Типы камер"""
    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"
    ORBITAL = "orbital"
    ISOMETRIC = "isometric"
    TOP_DOWN = "top_down"
    FREE = "free"

class RenderQuality(Enum):
    """Качество рендеринга"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

class LightingType(Enum):
    """Типы освещения"""
    AMBIENT = "ambient"
    DIRECTIONAL = "directional"
    POINT = "point"
    SPOT = "spot"
    AREA = "area"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class CameraSettings:
    """Настройки камеры"""
    camera_type: CameraType
    position: Tuple[float, float, float] = (0, 0, 0)
    target: Tuple[float, float, float] = (0, 0, 0)
    fov: float = 60.0
    near_plane: float = 0.1
    far_plane: float = 1000.0
    sensitivity: float = 1.0
    zoom_speed: float = 1.0
    orbit_radius: float = 10.0
    orbit_speed: float = 1.0

@dataclass
class LightingSettings:
    """Настройки освещения"""
    lighting_type: LightingType
    position: Tuple[float, float, float] = (0, 0, 0)
    direction: Tuple[float, float, float] = (0, -1, 0)
    color: Tuple[float, float, float] = (1, 1, 1)
    intensity: float = 1.0
    range: float = 100.0
    angle: float = 45.0
    cast_shadows: bool = True

@dataclass
class MaterialSettings:
    """Настройки материала"""
    material_id: str
    diffuse_color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    specular_color: Tuple[float, float, float] = (1, 1, 1)
    ambient_color: Tuple[float, float, float] = (0.2, 0.2, 0.2)
    shininess: float = 32.0
    transparency: float = 1.0
    texture_path: Optional[str] = None
    normal_map_path: Optional[str] = None
    shader_path: Optional[str] = None

@dataclass
class RenderSettings:
    """Настройки рендеринга"""
    quality: RenderQuality = RenderQuality.MEDIUM
    resolution: Tuple[int, int] = (1280, 720)
    fullscreen: bool = False
    vsync: bool = True
    antialiasing: bool = True
    shadows: bool = True
    reflections: bool = False
    post_processing: bool = True
    max_fps: int = 60

class RenderSystem(BaseComponent):
    """Система рендеринга с интеграцией Panda3D"""
    
    def __init__(self):
        super().__init__(
            component_id="render_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.CRITICAL
        )
        
        # Panda3D компоненты
        self.showbase: Optional[ShowBase] = None
        self.render: Optional[NodePath] = None
        self.cam: Optional[NodePath] = None
        
        # Камеры
        self.cameras: Dict[str, NodePath] = {}
        self.active_camera: Optional[str] = None
        self.camera_settings: Dict[str, CameraSettings] = {}
        
        # Освещение
        self.lights: Dict[str, Light] = {}
        self.lighting_settings: Dict[str, LightingSettings] = {}
        
        # Материалы
        self.materials: Dict[str, MaterialSettings] = {}
        self.material_cache: Dict[str, Material] = {}
        
        # Настройки рендеринга
        self.render_settings = RenderSettings()
        
        # Оптимизация
        self.lod_manager: Optional[LODManager] = None
        self.occlusion_culler: Optional[OcclusionCuller] = None
        
        # Callbacks
        self.on_camera_change: Optional[Callable] = None
        self.on_quality_change: Optional[Callable] = None
        
        logger.info("Система рендеринга инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы рендеринга"""
        try:
            logger.info("Инициализация RenderSystem...")
            
            # Создаем окно Panda3D
            if not self._create_panda3d_window():
                return False
            
            # Создание базовых камер
            if not self._create_default_cameras():
                return False
            
            # Настройка освещения
            if not self._setup_lighting():
                return False
            
            # Загрузка материалов
            if not self._load_materials():
                return False
            
            # Настройка оптимизации
            if not self._setup_optimization():
                return False
            
            # Создаем базовую сцену для демонстрации
            self._create_demo_scene()
            
            self.system_state = LifecycleState.READY
            logger.info("RenderSystem инициализирован успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации RenderSystem: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def _create_panda3d_window(self) -> bool:
        """Создание окна Panda3D"""
        try:
            # Импортируем Panda3D
            from panda3d.core import WindowProperties, GraphicsPipe
            from direct.showbase.ShowBase import ShowBase
            
            # Создаем базовое окно
            self.showbase = ShowBase()
            
            # Настраиваем свойства окна
            props = WindowProperties()
            props.setTitle("AI-EVOLVE Enhanced Edition")
            props.setSize(*self.render_settings.resolution)
            props.setFullscreen(self.render_settings.fullscreen)
            props.setCursorHidden(False)
            
            # Применяем свойства
            self.showbase.win.requestProperties(props)
            
            # Настройка вертикальной синхронизации
            if self.render_settings.vsync:
                try:
                    if hasattr(self.showbase.win, 'setVerticalSync'):
                        self.showbase.win.setVerticalSync(True)
                    else:
                        logger.warning("setVerticalSync не поддерживается в данной версии Panda3D")
                except Exception as vsync_e:
                    logger.warning(f"Не удалось установить вертикальную синхронизацию: {vsync_e}")
            
            # Получаем основные компоненты
            self.render = self.showbase.render
            self.cam = self.showbase.cam
            
            logger.info("Окно Panda3D создано успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания окна Panda3D: {e}")
            return False
    
    def _create_demo_scene(self):
        """Создание демонстрационной сцены"""
        try:
            # Создаем простой куб для демонстрации
            cube_geom = self._create_simple_cube()
            if cube_geom:
                # Оборачиваем GeomNode в NodePath для доступа к методам позиционирования
                cube = self.render.attachNewNode(cube_geom)
                cube.setPos(0, 0, 0)
                cube.setScale(1)
                
                # Применяем материал
                if 'default' in self.material_cache:
                    cube.setMaterial(self.material_cache['default'])
            
            # Добавляем текст
            from panda3d.core import TextNode
            text = TextNode("title")
            text.setText("AI-EVOLVE Enhanced Edition")
            text.setAlign(TextNode.ACenter)
            try:
                # Пробуем использовать setTextColor для новых версий Panda3D
                if hasattr(text, 'setTextColor'):
                    text.setTextColor(1, 1, 1, 1)
                elif hasattr(text, 'setColor'):
                    text.setColor(1, 1, 1, 1)
                else:
                    logger.warning("setColor не поддерживается для TextNode в данной версии Panda3D")
            except Exception as e:
                logger.warning(f"Не удалось установить цвет текста: {e}")
            
            text_np = self.render.attachNewNode(text)
            text_np.setPos(0, 0, 3)
            text_np.setScale(0.5)
            
            logger.info("Демонстрационная сцена создана")
            
        except Exception as e:
            logger.error(f"Ошибка создания демонстрационной сцены: {e}")
    
    def _create_simple_cube(self):
        """Создание простого куба"""
        try:
            from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter
            from panda3d.core import GeomTriangles, Geom, GeomNode
            
            # Создаем геометрию куба
            format = GeomVertexFormat.getV3n3c4()
            vdata = GeomVertexData("cube", format, Geom.UHStatic)
            
            # Вершины куба
            vertex = GeomVertexWriter(vdata, "vertex")
            normal = GeomVertexWriter(vdata, "normal")
            color = GeomVertexWriter(vdata, "color")
            
            # 8 вершин куба
            vertex.addData3(-1, -1, -1)
            vertex.addData3(1, -1, -1)
            vertex.addData3(1, 1, -1)
            vertex.addData3(-1, 1, -1)
            vertex.addData3(-1, -1, 1)
            vertex.addData3(1, -1, 1)
            vertex.addData3(1, 1, 1)
            vertex.addData3(-1, 1, 1)
            
            # Нормали и цвета
            for i in range(8):
                normal.addData3(0, 0, 1)
                color.addData4(0.8, 0.8, 0.8, 1)
            
            # Индексы для граней
            tris = GeomTriangles(Geom.UHStatic)
            
            # Нижняя грань
            tris.addVertices(0, 1, 2)
            tris.addVertices(0, 2, 3)
            # Верхняя грань
            tris.addVertices(4, 7, 6)
            tris.addVertices(4, 6, 5)
            # Передняя грань
            tris.addVertices(0, 4, 5)
            tris.addVertices(0, 5, 1)
            # Задняя грань
            tris.addVertices(2, 6, 7)
            tris.addVertices(2, 7, 3)
            # Левая грань
            tris.addVertices(0, 3, 7)
            tris.addVertices(0, 7, 4)
            # Правая грань
            tris.addVertices(1, 5, 6)
            tris.addVertices(1, 6, 2)
            
            tris.closePrimitive()
            
            # Создаем геометрию
            geom = Geom(vdata)
            geom.addPrimitive(tris)
            
            # Создаем узел
            node = GeomNode("cube")
            node.addGeom(geom)
            
            return node
            
        except Exception as e:
            logger.error(f"Ошибка создания куба: {e}")
            return None
    
    def _create_default_cameras(self) -> bool:
        """Создание базовых камер"""
        try:
            # Основная камера
            main_camera = CameraSettings(
                camera_type=CameraType.THIRD_PERSON,
                position=(0, -20, 10),
                target=(0, 0, 0),
                fov=60.0
            )
            
            self.camera_settings["main"] = main_camera
            self.cameras["main"] = self.cam
            self.active_camera = "main"
            
            # Орбитальная камера
            orbital_camera = self._create_orbital_camera()
            self.cameras["orbital"] = orbital_camera
            self.camera_settings["orbital"] = CameraSettings(
                camera_type=CameraType.ORBITAL,
                position=(0, -20, 10),
                target=(0, 0, 0),
                orbit_radius=20.0
            )
            
            # Изометрическая камера
            isometric_camera = self._create_isometric_camera()
            self.cameras["isometric"] = isometric_camera
            self.camera_settings["isometric"] = CameraSettings(
                camera_type=CameraType.ISOMETRIC,
                position=(20, -20, 20),
                target=(0, 0, 0),
                fov=45.0
            )
            
            logger.info(f"Создано {len(self.cameras)} камер")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания камер: {e}")
            return False
    
    def _create_orbital_camera(self) -> NodePath:
        """Создание орбитальной камеры"""
        try:
            from panda3d.core import Camera
            
            # Создание камеры
            camera = Camera("orbital_camera")
            camera_np = self.render.attachNewNode(camera)
            
            # Настройка позиции
            camera_np.setPos(0, -20, 10)
            camera_np.lookAt(0, 0, 0)
            
            return camera_np
            
        except Exception as e:
            logger.error(f"Ошибка создания орбитальной камеры: {e}")
            return self.cam
    
    def _create_isometric_camera(self) -> NodePath:
        """Создание изометрической камеры"""
        try:
            from panda3d.core import Camera
            
            # Создание камеры
            camera = Camera("isometric_camera")
            camera_np = self.render.attachNewNode(camera)
            
            # Настройка изометрической позиции
            camera_np.setPos(20, -20, 20)
            camera_np.lookAt(0, 0, 0)
            
            return camera_np
            
        except Exception as e:
            logger.error(f"Ошибка создания изометрической камеры: {e}")
            return self.cam
    
    def _setup_lighting(self) -> bool:
        """Настройка освещения"""
        try:
            from panda3d.core import AmbientLight, DirectionalLight
            
            # Окружающее освещение
            ambient_light = AmbientLight("ambient_light")
            ambient_light.setColor((0.3, 0.3, 0.3, 1))
            ambient_np = self.render.attachNewNode(ambient_light)
            self.render.setLight(ambient_np)
            self.lights["ambient"] = ambient_light
            
            # Направленное освещение (солнце)
            directional_light = DirectionalLight("directional_light")
            directional_light.setColor((0.8, 0.8, 0.7, 1))
            directional_np = self.render.attachNewNode(directional_light)
            directional_np.setHpr(45, -45, 0)
            self.render.setLight(directional_np)
            self.lights["directional"] = directional_light
            
            # Настройки освещения
            self.lighting_settings["ambient"] = LightingSettings(
                lighting_type=LightingType.AMBIENT,
                color=(0.3, 0.3, 0.3),
                intensity=0.3
            )
            
            self.lighting_settings["directional"] = LightingSettings(
                lighting_type=LightingType.DIRECTIONAL,
                direction=(1, -1, 0),
                color=(0.8, 0.8, 0.7),
                intensity=0.8,
                cast_shadows=True
            )
            
            logger.info(f"Настроено {len(self.lights)} источников света")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки освещения: {e}")
            return False
    
    def _load_materials(self) -> bool:
        """Загрузка материалов"""
        try:
            from panda3d.core import Material, VBase4
            
            # Базовые материалы
            materials = [
                MaterialSettings(
                    material_id="default",
                    diffuse_color=(0.8, 0.8, 0.8),
                    specular_color=(1, 1, 1),
                    shininess=32.0
                ),
                MaterialSettings(
                    material_id="metal",
                    diffuse_color=(0.7, 0.7, 0.8),
                    specular_color=(1, 1, 1),
                    shininess=128.0
                ),
                MaterialSettings(
                    material_id="wood",
                    diffuse_color=(0.6, 0.4, 0.2),
                    specular_color=(0.3, 0.3, 0.3),
                    shininess=16.0
                ),
                MaterialSettings(
                    material_id="stone",
                    diffuse_color=(0.5, 0.5, 0.5),
                    specular_color=(0.2, 0.2, 0.2),
                    shininess=8.0
                )
            ]
            
            for material in materials:
                self.materials[material.material_id] = material
                self._create_material(material)
            
            logger.info(f"Загружено {len(self.materials)} материалов")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки материалов: {e}")
            return False
    
    def _create_material(self, material_settings: MaterialSettings):
        """Создание материала"""
        try:
            from panda3d.core import Material, VBase4
            
            material = Material()
            
            # Настройка цветов
            material.setDiffuse(VBase4(*material_settings.diffuse_color, 1.0))
            material.setSpecular(VBase4(*material_settings.specular_color, 1.0))
            material.setAmbient(VBase4(*material_settings.ambient_color, 1.0))
            material.setShininess(material_settings.shininess)
            
            # Настройка прозрачности
            if material_settings.transparency < 1.0:
                material.setTransparency(Material.MAlpha)
            
            # Загрузка текстур
            if material_settings.texture_path:
                texture = self._load_texture(material_settings.texture_path)
                if texture:
                    material.setTexture(texture)
            
            self.material_cache[material_settings.material_id] = material
            
        except Exception as e:
            logger.error(f"Ошибка создания материала {material_settings.material_id}: {e}")
    
    def _load_texture(self, texture_path: str):
        """Загрузка текстуры"""
        try:
            from panda3d.core import Texture
            texture = Texture(texture_path)
            texture.read(texture_path)
            return texture
        except Exception as e:
            logger.warning(f"Не удалось загрузить текстуру {texture_path}: {e}")
            return None
    
    def _setup_optimization(self) -> bool:
        """Настройка оптимизации рендеринга"""
        try:
            # Импорт оптимизации рендеринга
            try:
                from panda3d.core import LODManager, OcclusionCuller
                self.lod_manager = LODManager()
                self.occlusion_culler = OcclusionCuller()
                logger.info("Оптимизация рендеринга настроена")
            except ImportError:
                logger.warning("LODManager недоступен в данной версии Panda3D - оптимизация отключена")
                self.lod_manager = None
                self.occlusion_culler = None
            
            # Настройка качества рендеринга
            self._apply_quality_settings()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки оптимизации: {e}")
            return False
    
    def _apply_quality_settings(self):
        """Применение настроек качества"""
        try:
            quality = self.render_settings.quality
            
            if quality == RenderQuality.LOW:
                # Низкое качество
                try:
                    if hasattr(self.showbase.win, 'setAntialias'):
                        self.showbase.win.setAntialias(False)
                    else:
                        logger.warning("setAntialias не поддерживается в данной версии Panda3D")
                except Exception as e:
                    logger.warning(f"Не удалось отключить сглаживание: {e}")
                    
                self.render.setShaderAuto(False)
                
            elif quality == RenderQuality.MEDIUM:
                # Среднее качество
                try:
                    if hasattr(self.showbase.win, 'setAntialias'):
                        self.showbase.win.setAntialias(True)
                    else:
                        logger.warning("setAntialias не поддерживается в данной версии Panda3D")
                except Exception as e:
                    logger.warning(f"Не удалось включить сглаживание: {e}")
                    
                self.render.setShaderAuto(True)
                
            elif quality == RenderQuality.HIGH:
                # Высокое качество
                try:
                    if hasattr(self.showbase.win, 'setAntialias'):
                        self.showbase.win.setAntialias(True)
                    else:
                        logger.warning("setAntialias не поддерживается в данной версии Panda3D")
                except Exception as e:
                    logger.warning(f"Не удалось включить сглаживание: {e}")
                    
                self.render.setShaderAuto(True)
                self.render.setTwoSidedLighting(True)
                
            elif quality == RenderQuality.ULTRA:
                # Ультра качество
                try:
                    if hasattr(self.showbase.win, 'setAntialias'):
                        self.showbase.win.setAntialias(True)
                    else:
                        logger.warning("setAntialias не поддерживается в данной версии Panda3D")
                except Exception as e:
                    logger.warning(f"Не удалось включить сглаживание: {e}")
                    
                self.render.setShaderAuto(True)
                self.render.setTwoSidedLighting(True)
                self.render.setDepthTest(True)
                self.render.setDepthWrite(True)
            
            logger.info(f"Применены настройки качества: {quality.value}")
            
        except Exception as e:
            logger.error(f"Ошибка применения настроек качества: {e}")
    
    def start(self) -> bool:
        """Запуск системы рендеринга"""
        try:
            logger.info("Запуск RenderSystem...")
            
            if self.system_state != LifecycleState.READY:
                logger.error("RenderSystem не готов к запуску")
                return False
            
            # Запускаем главный цикл Panda3D
            self._start_render_loop()
            
            self.system_state = LifecycleState.RUNNING
            logger.info("RenderSystem запущен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска RenderSystem: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def _start_render_loop(self):
        """Запуск цикла рендеринга"""
        try:
            # Добавляем задачу обновления
            from direct.task import Task
            
            def update_task(task):
                # Вращение куба
                cube = self.render.find("cube")
                if cube:
                    cube.setH(cube.getH() + 1)
                return Task.cont
            
            self.showbase.taskMgr.add(update_task, "render_update")
            
            logger.info("Цикл рендеринга запущен")
            
        except Exception as e:
            logger.error(f"Ошибка запуска цикла рендеринга: {e}")
    
    def update(self, delta_time: float):
        """Обновление системы рендеринга"""
        if self.system_state != LifecycleState.RUNNING:
            return
        
        try:
            # Обновляем статистику
            self.system_stats['update_count'] += 1
            self.system_stats['total_update_time'] += delta_time
            self.system_stats['last_update_time'] = time.time()
            
            # Обновляем орбитальные камеры
            for camera_id, settings in self.camera_settings.items():
                if settings.camera_type == CameraType.ORBITAL:
                    # Автоматическое вращение
                    current_time = time.time()
                    angle_x = current_time * settings.orbit_speed * 0.1
                    angle_y = math.pi / 4  # Фиксированный угол
                    self.orbit_camera(camera_id, angle_x, angle_y)
            
            # Обновляем Panda3D
            if hasattr(self, 'showbase'):
                self.showbase.graphicsEngine.renderFrame()
                
        except Exception as e:
            logger.error(f"Ошибка обновления RenderSystem: {e}")
    
    def show_start_menu(self, ui_manager=None):
        """Отображение стартового меню"""
        try:
            if ui_manager:
                # Создаем стартовое меню через UIManager
                start_menu = ui_manager.create_start_menu()
                if start_menu:
                    logger.info("Стартовое меню отображено")
                    return True
                else:
                    logger.warning("Не удалось создать стартовое меню")
                    return False
            else:
                # Создаем простое стартовое меню напрямую
                self._create_simple_start_menu()
                return True
                
        except Exception as e:
            logger.error(f"Ошибка отображения стартового меню: {e}")
            return False
    
    def _create_simple_start_menu(self):
        """Создание простого стартового меню"""
        try:
            from direct.gui.DirectFrame import DirectFrame
            from direct.gui.DirectButton import DirectButton
            from direct.gui.DirectLabel import DirectLabel
            
            # Основная панель меню
            menu_frame = DirectFrame(
                frameColor=(0.0, 0.0, 0.0, 0.8),
                frameSize=(-0.4, 0.4, -0.6, 0.6),
                pos=(0, 0, 0)
            )
            menu_frame.reparentTo(self.render2d)
            
            # Заголовок
            title_label = DirectLabel(
                text="AI-EVOLVE ENHANCED EDITION",
                text_fg=(0.0, 1.0, 1.0, 1.0),
                text_scale=0.08,
                pos=(0, 0, 0.4),
                parent=menu_frame
            )
            
            # Кнопка "Начать игру"
            start_button = DirectButton(
                text="START GAME",
                text_fg=(1.0, 1.0, 1.0, 1.0),
                text_scale=0.06,
                frameColor=(0.2, 0.2, 0.2, 0.9),
                frameSize=(-0.3, 0.3, -0.05, 0.05),
                pos=(0, 0, 0.2),
                parent=menu_frame,
                command=self._on_start_game
            )
            
            # Кнопка "Настройки"
            settings_button = DirectButton(
                text="SETTINGS",
                text_fg=(1.0, 1.0, 1.0, 1.0),
                text_scale=0.06,
                frameColor=(0.2, 0.2, 0.2, 0.9),
                frameSize=(-0.3, 0.3, -0.05, 0.05),
                pos=(0, 0, 0.1),
                parent=menu_frame,
                command=self._on_settings
            )
            
            # Кнопка "Выход"
            quit_button = DirectButton(
                text="QUIT GAME",
                text_fg=(1.0, 1.0, 1.0, 1.0),
                text_scale=0.06,
                frameColor=(0.2, 0.2, 0.2, 0.9),
                frameSize=(-0.3, 0.3, -0.05, 0.05),
                pos=(0, 0, -0.1),
                parent=menu_frame,
                command=self._on_quit_game
            )
            
            # Сохраняем ссылки на элементы меню
            self.start_menu_elements = {
                'frame': menu_frame,
                'title': title_label,
                'start_button': start_button,
                'settings_button': settings_button,
                'quit_button': quit_button
            }
            
            logger.info("Простое стартовое меню создано")
            
        except Exception as e:
            logger.error(f"Ошибка создания простого стартового меню: {e}")
    
    def _on_start_game(self):
        """Обработчик нажатия кнопки 'Начать игру'"""
        try:
            logger.info("Нажата кнопка 'Начать игру'")
            # Скрываем стартовое меню
            if hasattr(self, 'start_menu_elements'):
                for element in self.start_menu_elements.values():
                    if element:
                        element.hide()
                logger.info("Стартовое меню скрыто")
            
            # Здесь можно добавить логику перехода к игре
            
        except Exception as e:
            logger.error(f"Ошибка обработки кнопки 'Начать игру': {e}")
    
    def _on_settings(self):
        """Обработчик нажатия кнопки 'Настройки'"""
        try:
            logger.info("Нажата кнопка 'Настройки'")
            # Здесь можно добавить логику открытия настроек
            
        except Exception as e:
            logger.error(f"Ошибка обработки кнопки 'Настройки': {e}")
    
    def _on_quit_game(self):
        """Обработчик нажатия кнопки 'Выход'"""
        try:
            logger.info("Нажата кнопка 'Выход'")
            # Выход из игры
            import sys
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Ошибка обработки кнопки 'Выход': {e}")
    
    def run(self):
        """Запуск главного цикла Panda3D"""
        try:
            if hasattr(self, 'showbase'):
                logger.info("Запуск главного цикла Panda3D...")
                
                # Показываем стартовое меню
                self.show_start_menu()
                
                # Запускаем главный цикл
                self.showbase.run()
            else:
                logger.error("Panda3D не инициализирован")
                
        except Exception as e:
            logger.error(f"Ошибка запуска главного цикла: {e}")
    
    def switch_camera(self, camera_id: str) -> bool:
        """Переключение камеры"""
        try:
            if camera_id not in self.cameras:
                logger.error(f"Камера {camera_id} не найдена")
                return False
            
            # Переключение активной камеры
            old_camera = self.active_camera
            self.active_camera = camera_id
            
            # Применение настроек камеры
            camera_np = self.cameras[camera_id]
            settings = self.camera_settings.get(camera_id)
            
            if settings:
                camera_np.setPos(*settings.position)
                camera_np.lookAt(*settings.target)
            
            # Вызов callback
            if self.on_camera_change:
                self.on_camera_change(old_camera, camera_id)
            
            logger.info(f"Переключена камера: {old_camera} -> {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка переключения камеры: {e}")
            return False
    
    def set_camera_position(self, camera_id: str, position: Tuple[float, float, float]):
        """Установка позиции камеры"""
        try:
            if camera_id not in self.cameras:
                return False
            
            camera_np = self.cameras[camera_id]
            camera_np.setPos(*position)
            
            # Обновление настроек
            if camera_id in self.camera_settings:
                self.camera_settings[camera_id].position = position
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки позиции камеры: {e}")
            return False
    
    def orbit_camera(self, camera_id: str, angle_x: float, angle_y: float):
        """Орбитальное движение камеры"""
        try:
            if camera_id not in self.cameras:
                return False
            
            camera_np = self.cameras[camera_id]
            settings = self.camera_settings.get(camera_id)
            
            if not settings or settings.camera_type != CameraType.ORBITAL:
                return False
            
            # Вычисление новой позиции
            radius = settings.orbit_radius
            x = radius * math.sin(angle_y) * math.cos(angle_x)
            y = radius * math.sin(angle_y) * math.sin(angle_x)
            z = radius * math.cos(angle_y)
            
            camera_np.setPos(x, y, z)
            camera_np.lookAt(*settings.target)
            
        except Exception as e:
            logger.error(f"Ошибка орбитального движения камеры: {e}")
    
    def add_light(self, light_id: str, settings: LightingSettings) -> bool:
        """Добавление источника света"""
        try:
            from panda3d.core import AmbientLight, DirectionalLight, PointLight, Spotlight, VBase4
            
            if settings.lighting_type == LightingType.AMBIENT:
                light = AmbientLight(light_id)
            elif settings.lighting_type == LightingType.DIRECTIONAL:
                light = DirectionalLight(light_id)
            elif settings.lighting_type == LightingType.POINT:
                light = PointLight(light_id)
            elif settings.lighting_type == LightingType.SPOT:
                light = Spotlight(light_id)
            else:
                logger.error(f"Неподдерживаемый тип освещения: {settings.lighting_type}")
                return False
            
            # Настройка света
            light.setColor(VBase4(*settings.color, 1.0))
            
            # Размещение света
            light_np = self.render.attachNewNode(light)
            light_np.setPos(*settings.position)
            
            if settings.lighting_type in [LightingType.DIRECTIONAL, LightingType.SPOT]:
                light_np.lookAt(*settings.direction)
            
            # Применение света
            self.render.setLight(light_np)
            
            # Сохранение
            self.lights[light_id] = light
            self.lighting_settings[light_id] = settings
            
            logger.info(f"Добавлен источник света: {light_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления источника света: {e}")
            return False
    
    def apply_material(self, node_path, material_id: str) -> bool:
        """Применение материала к объекту"""
        try:
            if material_id not in self.material_cache:
                logger.error(f"Материал {material_id} не найден")
                return False
            
            material = self.material_cache[material_id]
            node_path.setMaterial(material)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка применения материала: {e}")
            return False
    
    def set_render_quality(self, quality: RenderQuality) -> bool:
        """Установка качества рендеринга"""
        try:
            self.render_settings.quality = quality
            self._apply_quality_settings()
            
            # Вызов callback
            if self.on_quality_change:
                self.on_quality_change(quality)
            
            logger.info(f"Установлено качество рендеринга: {quality.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки качества рендеринга: {e}")
            return False
    
    def get_camera_info(self, camera_id: str):
        """Получение информации о камере"""
        try:
            if camera_id not in self.cameras:
                return None
            
            camera_np = self.cameras[camera_id]
            settings = self.camera_settings.get(camera_id)
            
            return {
                "camera_id": camera_id,
                "position": camera_np.getPos(),
                "rotation": camera_np.getHpr(),
                "settings": settings.__dict__ if settings else None,
                "is_active": camera_id == self.active_camera
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о камере: {e}")
            return None
    
    def get_render_stats(self) -> Dict[str, Any]:
        """Получение статистики рендеринга"""
        try:
            return {
                "active_camera": self.active_camera,
                "total_cameras": len(self.cameras),
                "total_lights": len(self.lights),
                "total_materials": len(self.materials),
                "render_quality": self.render_settings.quality.value,
                "resolution": self.render_settings.resolution,
                "fps": self.showbase.getAverageFrameRate() if hasattr(self, 'showbase') else 0
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики рендеринга: {e}")
            return {}
    
    def cleanup(self):
        """Очистка системы рендеринга"""
        try:
            # Очистка камер
            for camera_np in self.cameras.values():
                if camera_np != self.cam:  # Не удаляем основную камеру
                    camera_np.removeNode()
            
            # Очистка источников света
            for light in self.lights.values():
                light.removeNode()
            
            # Очистка данных
            self.cameras.clear()
            self.camera_settings.clear()
            self.lights.clear()
            self.lighting_settings.clear()
            self.materials.clear()
            self.material_cache.clear()
            
            logger.info("Система рендеринга очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы рендеринга: {e}")
