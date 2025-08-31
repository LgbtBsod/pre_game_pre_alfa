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
            logger.info("=" * 50)
            logger.info("🎮 СОЗДАНИЕ СТАРТОВОГО МЕНЮ")
            logger.info("=" * 50)
            
            if ui_manager:
                logger.info("🔍 Попытка создания стартового меню через UIManager...")
                # Создаем стартовое меню через UIManager
                start_menu = ui_manager.create_start_menu()
                if start_menu:
                    logger.info("✅ Стартовое меню отображено через UIManager")
                    return True
                else:
                    logger.warning("⚠️  Не удалось создать стартовое меню через UIManager")
                    return False
            else:
                logger.info("🔍 UIManager не предоставлен, создаем простое меню...")
                # Создаем простое стартовое меню напрямую
                result = self._create_simple_start_menu()
                if result:
                    logger.info("✅ Простое стартовое меню создано успешно")
                    return True
                else:
                    logger.warning("⚠️  Не удалось создать простое стартовое меню")
                    return False
                
        except Exception as e:
            logger.error("=" * 50)
            logger.error("❌ ОШИБКА СОЗДАНИЯ СТАРТОВОГО МЕНЮ")
            logger.error("=" * 50)
            logger.error(f"Ошибка отображения стартового меню: {e}")
            import traceback
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            return False
    
    def _on_start_game(self):
        """Обработчик нажатия кнопки START GAME"""
        try:
            logger.info("🎮 Кнопка START GAME нажата!")
            
            # Скрываем стартовое меню
            if hasattr(self, 'start_menu_elements'):
                for element in self.start_menu_elements.values():
                    if hasattr(element, 'hide'):
                        element.hide()
                        logger.info("✅ Стартовое меню скрыто")
            
            # Здесь можно добавить логику запуска игры
            logger.info("🚀 Запуск игрового процесса...")
            
            # Создаем простую игровую сцену
            self._create_game_scene()
            
        except Exception as e:
            logger.error(f"❌ Ошибка при нажатии START GAME: {e}")
    
    def _on_settings(self):
        """Обработчик нажатия кнопки SETTINGS"""
        try:
            logger.info("⚙️  Кнопка SETTINGS нажата!")
            
            # Здесь можно добавить логику настроек
            logger.info("🔧 Открытие настроек...")
            
            # Пока что просто выводим сообщение
            if hasattr(self, 'showbase') and hasattr(self.showbase, 'render2d'):
                from direct.gui.DirectLabel import DirectLabel
                
                settings_label = DirectLabel(
                    parent=self.showbase.render2d,
                    text="Настройки пока не реализованы",
                    scale=0.03,
                    pos=(0, 0, 0),
                    text_fg=(1, 1, 1, 1),
                    text_shadow=(0, 0, 0, 1)
                )
                
                # Убираем через 3 секунды
                from direct.task import Task
                def remove_settings_label(task):
                    settings_label.destroy()
                    return Task.done
                
                self.showbase.taskMgr.doMethodLater(3.0, remove_settings_label, "remove_settings")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при нажатии SETTINGS: {e}")
    
    def _on_quit_game(self):
        """Обработчик нажатия кнопки QUIT GAME"""
        try:
            logger.info("🚪 Кнопка QUIT GAME нажата!")
            
            # Завершаем игру
            logger.info("🛑 Завершение игры...")
            
            if hasattr(self, 'showbase'):
                self.showbase.userExit()
            
        except Exception as e:
            logger.error(f"❌ Ошибка при нажатии QUIT GAME: {e}")
    
    def _create_game_scene(self):
        """Создание игровой сцены после нажатия START GAME"""
        try:
            logger.info("🎨 Создание игровой сцены...")
            
            if hasattr(self, 'showbase'):
                # Создаем простую 3D сцену
                from panda3d.core import GeomNode, NodePath
                
                # Создаем тестовый куб
                test_node = GeomNode("game_cube")
                test_np = self.showbase.render.attachNewNode(test_node)
                test_np.setPos(0, 5, 0)
                
                # Добавляем текст "ИГРА ЗАПУЩЕНА"
                from direct.gui.DirectLabel import DirectLabel
                
                game_label = DirectLabel(
                    parent=self.showbase.render2d,
                    text="ИГРА ЗАПУЩЕНА!",
                    scale=0.05,
                    pos=(0, 0, 0.3),
                    text_fg=(0, 1, 0, 1),
                    text_shadow=(0, 0, 0, 1)
                )
                
                logger.info("✅ Игровая сцена создана")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания игровой сцены: {e}")
    
    def _create_simple_start_menu(self):
        """Создание простого стартового меню"""
        try:
            logger.info("=" * 50)
            logger.info("🎮 СОЗДАНИЕ ПРОСТОГО СТАРТОВОГО МЕНЮ")
            logger.info("=" * 50)
            
            logger.info("Начинаем создание простого стартового меню...")
            
            # Импортируем необходимые компоненты
            try:
                from direct.gui.DirectFrame import DirectFrame
                from direct.gui.DirectButton import DirectButton
                from direct.gui.DirectLabel import DirectLabel
                logger.info("✅ Импорт DirectGUI компонентов успешен")
            except ImportError as e:
                logger.error(f"❌ Ошибка импорта DirectGUI: {e}")
                return False
            
            if not hasattr(self, 'showbase') or not hasattr(self.showbase, 'render2d'):
                logger.error("❌ showbase.render2d недоступен")
                return False
            
            logger.info("✅ showbase.render2d доступен")
            
            # Создаем основную панель меню
            try:
                menu_frame = DirectFrame(
                    frameColor=(0.2, 0.2, 0.2, 0.8),
                    frameSize=(-0.3, 0.3, -0.4, 0.4),
                    pos=(0, 0, 0)
                )
                logger.info("✅ Панель меню создана")
            except Exception as e:
                logger.error(f"❌ Ошибка создания панели меню: {e}")
                return False
            
            # Привязываем к render2d
            try:
                menu_frame.reparentTo(self.showbase.render2d)
                logger.info("✅ Панель меню привязана к render2d")
            except Exception as e:
                logger.error(f"❌ Ошибка привязки панели к render2d: {e}")
                return False
            
            # Создаем заголовок
            try:
                title_label = DirectLabel(
                    parent=menu_frame,
                    text="AI EVOLVE",
                    scale=0.05,
                    pos=(0, 0, 0.25),
                    text_fg=(1, 1, 1, 1),
                    text_shadow=(0, 0, 0, 1)
                )
                logger.info("✅ Заголовок создан")
            except Exception as e:
                logger.error(f"❌ Ошибка создания заголовка: {e}")
                return False
            
            # СОЗДАЕМ МАКСИМАЛЬНО ПРОСТЫЕ КНОПКИ
            logger.info("🔧 Создание максимально простых кнопок...")
            
            try:
                # Простая функция для тестирования
                def simple_test_click():
                    logger.info("🎯 ПРОСТАЯ КНОПКА НАЖАТА!")
                    print("🎯 КНОПКА РАБОТАЕТ!")
                
                # Кнопка START GAME - максимально простая
                start_button = DirectButton(
                    parent=menu_frame,
                    text="START GAME",
                    scale=0.04,
                    pos=(0, 0, 0.1),
                    frameColor=(0.3, 0.6, 0.3, 1),
                    text_fg=(1, 1, 1, 1),
                    command=simple_test_click,  # Используем простую функцию
                    relief=1
                )
                logger.info("✅ Кнопка START GAME создана")
                
                # Кнопка SETTINGS - максимально простая
                settings_button = DirectButton(
                    parent=menu_frame,
                    text="SETTINGS",
                    scale=0.04,
                    pos=(0, 0, 0),
                    frameColor=(0.3, 0.3, 0.6, 1),
                    text_fg=(1, 1, 1, 1),
                    command=simple_test_click,  # Используем простую функцию
                    relief=1
                )
                logger.info("✅ Кнопка SETTINGS создана")
                
                # Кнопка QUIT GAME - максимально простая
                quit_button = DirectButton(
                    parent=menu_frame,
                    text="QUIT GAME",
                    scale=0.04,
                    pos=(0, 0, -0.1),
                    frameColor=(0.6, 0.3, 0.3, 1),
                    text_fg=(1, 1, 1, 1),
                    command=simple_test_click,  # Используем простую функцию
                    relief=1
                )
                logger.info("✅ Кнопка QUIT GAME создана")
                
                # Сохраняем ссылки на элементы меню
                self.start_menu_elements = {
                    'frame': menu_frame,
                    'title': title_label,
                    'start_button': start_button,
                    'settings_button': settings_button,
                    'quit_button': quit_button
                }
                
                # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА КНОПОК
                logger.info("🔍 Проверка функциональности кнопок...")
                
                # Проверяем, что кнопки действительно имеют обработчики
                if hasattr(start_button, 'command'):
                    logger.info("   ✅ START GAME кнопка имеет обработчик")
                    # Проверяем, что обработчик действительно функция
                    if callable(start_button.command):
                        logger.info("   ✅ Обработчик START GAME вызываемый")
                    else:
                        logger.warning("   ⚠️  Обработчик START GAME не вызываемый")
                else:
                    logger.warning("   ⚠️  START GAME кнопка не имеет обработчика")
                
                if hasattr(settings_button, 'command'):
                    logger.info("   ✅ SETTINGS кнопка имеет обработчик")
                    if callable(settings_button.command):
                        logger.info("   ✅ Обработчик SETTINGS вызываемый")
                    else:
                        logger.warning("   ⚠️  Обработчик SETTINGS не вызываемый")
                else:
                    logger.warning("   ⚠️  SETTINGS кнопка не имеет обработчика")
                
                if hasattr(quit_button, 'command'):
                    logger.info("   ✅ QUIT GAME кнопка имеет обработчик")
                    if callable(quit_button.command):
                        logger.info("   ✅ Обработчик QUIT GAME вызываемый")
                    else:
                        logger.warning("   ⚠️  Обработчик QUIT GAME не вызываемый")
                else:
                    logger.warning("   ⚠️  QUIT GAME кнопка не имеет обработчика")
                
                # Проверяем состояние кнопок
                if hasattr(start_button, 'state'):
                    logger.info(f"   📊 Состояние START GAME кнопки: {start_button.state()}")
                if hasattr(settings_button, 'state'):
                    logger.info(f"   📊 Состояние SETTINGS кнопки: {settings_button.state()}")
                if hasattr(quit_button, 'state'):
                    logger.info(f"   📊 Состояние QUIT GAME кнопки: {quit_button.state()}")
                
                # Проверяем, что кнопки привязаны к правильному родителю
                logger.info(f"   🔗 Родитель START GAME кнопки: {start_button.getParent()}")
                logger.info(f"   🔗 Родитель SETTINGS кнопки: {settings_button.getParent()}")
                logger.info(f"   🔗 Родитель QUIT GAME кнопки: {quit_button.getParent()}")
                
                # Проверяем, что кнопки действительно в render2d
                if start_button.getParent() == self.showbase.render2d:
                    logger.info("   ✅ START GAME кнопка в render2d")
                else:
                    logger.warning("   ⚠️  START GAME кнопка НЕ в render2d")
                
                if settings_button.getParent() == self.showbase.render2d:
                    logger.info("   ✅ SETTINGS кнопка в render2d")
                else:
                    logger.warning("   ⚠️  SETTINGS кнопка НЕ в render2d")
                
                if quit_button.getParent() == self.showbase.render2d:
                    logger.info("   ✅ QUIT GAME кнопка в render2d")
                else:
                    logger.warning("   ⚠️  QUIT GAME кнопка НЕ в render2d")
                
            except Exception as e:
                logger.error(f"❌ Ошибка создания кнопок: {e}")
                return False
            
            # Дополнительная проверка - убеждаемся что меню видимо
            logger.info("🔍 Проверка видимости меню...")
            try:
                if hasattr(menu_frame, 'isVisible'):
                    is_visible = menu_frame.isVisible()
                    logger.info(f"   📊 Меню видимо: {is_visible}")
                else:
                    logger.info("   ⚠️  Метод isVisible недоступен")
                
                if hasattr(menu_frame, 'getPos'):
                    pos = menu_frame.getPos()
                    logger.info(f"   📍 Позиция меню: {pos}")
                else:
                    logger.info("   ⚠️  Метод getPos недоступен")
                
                if hasattr(menu_frame, 'getScale'):
                    scale = menu_frame.getScale()
                    logger.info(f"   📐 Масштаб меню: {scale}")
                else:
                    logger.info("   ⚠️  Метод getScale недоступен")
                    
            except Exception as e:
                logger.warning(f"   ⚠️  Не удалось проверить свойства меню: {e}")
            
            # Проверяем, что mouseWatcherNode доступен
            logger.info("🔍 Проверка mouseWatcherNode...")
            if hasattr(self.showbase, 'mouseWatcherNode'):
                mouse_watcher = self.showbase.mouseWatcherNode
                if mouse_watcher:
                    logger.info("   ✅ mouseWatcherNode доступен")
                    if hasattr(mouse_watcher, 'hasMouse'):
                        has_mouse = mouse_watcher.hasMouse()
                        logger.info(f"   📊 Мышь в окне: {has_mouse}")
                else:
                    logger.warning("   ⚠️  mouseWatcherNode не инициализирован")
            else:
                logger.warning("   ⚠️  mouseWatcherNode не найден")
            
            logger.info("✅ Простое стартовое меню создано успешно")
            return True
            
        except Exception as e:
            logger.error("=" * 50)
            logger.error("❌ ОШИБКА СОЗДАНИЯ СТАРТОВОГО МЕНЮ")
            logger.error("=" * 50)
            logger.error(f"Ошибка создания стартового меню: {e}")
            import traceback
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            return False
    
    def run(self):
        """Запуск главного цикла Panda3D"""
        try:
            logger.info("=" * 60)
            logger.info("🚀 ЗАПУСК ГЛАВНОГО ЦИКЛА PANDA3D")
            logger.info("=" * 60)
            
            if hasattr(self, 'showbase'):
                logger.info("✅ ShowBase найден")
                
                # Показываем стартовое меню
                logger.info("🎮 Отображение стартового меню...")
                menu_result = self.show_start_menu()
                if menu_result:
                    logger.info("✅ Стартовое меню успешно отображено")
                else:
                    logger.warning("⚠️  Не удалось отобразить стартовое меню")
                
                # Проверяем состояние окна перед запуском
                logger.info("🔍 Проверка состояния окна перед запуском...")
                if hasattr(self.showbase, 'win'):
                    win = self.showbase.win
                    logger.info(f"Окно найдено: {type(win).__name__}")
                    if hasattr(win, 'isValid'):
                        try:
                            is_valid = win.isValid()
                            logger.info(f"Окно валидно: {is_valid}")
                        except Exception as e:
                            logger.warning(f"Не удалось проверить валидность окна: {e}")
                else:
                    logger.warning("Окно не найдено в ShowBase")
                
                # Дополнительная проверка - убеждаемся, что окно видимо
                logger.info("🔍 Проверка видимости окна...")
                if hasattr(self.showbase, 'win'):
                    win = self.showbase.win
                    if hasattr(win, 'getXSize') and hasattr(win, 'getYSize'):
                        try:
                            width = win.getXSize()
                            height = win.getYSize()
                            logger.info(f"Размеры окна: {width}x{height}")
                        except Exception as e:
                            logger.warning(f"Не удалось получить размеры окна: {e}")
                    
                    # Проверяем, что окно не минимизировано
                    if hasattr(win, 'getState'):
                        try:
                            state = win.getState()
                            logger.info(f"Состояние окна: {state}")
                        except Exception as e:
                            logger.warning(f"Не удалось получить состояние окна: {e}")
                
                # Запускаем главный цикл
                logger.info("🚀 ЗАПУСКАЕМ ГЛАВНЫЙ ЦИКЛ...")
                logger.info("⚠️  ВНИМАНИЕ: Окно должно остаться открытым!")
                logger.info("   Для выхода закройте окно игры")
                
                # ВАЖНО: Используем тот же подход что сработал в простом тесте
                self.showbase.run()
                logger.info("✅ showbase.run() завершен")
                
            else:
                logger.error("❌ Panda3D не инициализирован")
                raise Exception("Panda3D не инициализирован")
                
        except Exception as e:
            logger.error("=" * 60)
            logger.error("❌ ОШИБКА ЗАПУСКА ГЛАВНОГО ЦИКЛА")
            logger.error("=" * 60)
            logger.error(f"Ошибка запуска главного цикла: {e}")
            import traceback
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            raise
    
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
