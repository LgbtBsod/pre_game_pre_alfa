#!/usr/bin/env python3
"""Объединенная система визуализации
Объединяет все типы визуализации в единую систему с режимами"""

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Panda3D imports
from panda3d.core import (
    NodePath, PandaNode, GeomNode, Geom, GeomTriangles, GeomVertexData,
    GeomVertexFormat, GeomVertexWriter, TransparencyAttrib, ColorAttrib,
    Vec3, Vec4, Point3, TransformState, AntialiasAttrib, Material,
    AmbientLight, DirectionalLight, PointLight, Spotlight, Fog,
    BillboardEffect, CompassEffect, DepthTestAttrib,
    DepthWriteAttrib, CullFaceAttrib, Shader, ShaderAttrib, Camera,
    PerspectiveLens, OrthographicLens, LVector3
)

from ...core.constants import EmotionType, constants_manager
from ...core.constants_extended import (
    GEOMETRIC_SHAPE_CONSTANTS, EMOTION_VISUALIZATION_CONSTANTS
)
from ...core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from ...core.state_manager import StateManager, StateType

logger = logging.getLogger(__name__)

# = РЕЖИМЫ ВИЗУАЛИЗАЦИИ

class VisualizationMode(Enum):
    """Режимы визуализации"""
    ISOMETRIC = "isometric"
    PERSPECTIVE = "perspective"
    TOP_DOWN = "top_down"
    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"

class EmotionVisualizationType(Enum):
    """Типы визуализации эмоций"""
    COLOR = "color"
    PARTICLE = "particle"
    SHAPE = "shape"
    ANIMATION = "animation"
    SOUND = "sound"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class VisualizationSettings:
    """Настройки визуализации"""
    mode: VisualizationMode = VisualizationMode.ISOMETRIC
    camera_distance: float = 20.0
    camera_angle: float = 45.0
    field_of_view: float = 60.0
    near_plane: float = 0.1
    far_plane: float = 1000.0
    enable_emotions: bool = True
    enable_particles: bool = True
    enable_lighting: bool = True
    enable_shadows: bool = True

@dataclass
class CameraConfig:
    """Конфигурация камеры"""
    position: Vec3 = Vec3(0, 0, 0)
    target: Vec3 = Vec3(0, 0, 0)
    up: Vec3 = Vec3(0, 0, 1)
    distance: float = 20.0
    angle: float = 45.0
    zoom_speed: float = 1.0
    rotation_speed: float = 1.0

@dataclass
class EmotionVisual:
    """Визуальное представление эмоции"""
    emotion_type: EmotionType
    color: Vec4 = Vec4(1, 1, 1, 1)
    intensity: float = 1.0
    particle_effect: Optional[str] = None
    animation: Optional[str] = None
    sound: Optional[str] = None

class UnifiedVisualizationSystem(BaseComponent):
    """Объединенная система визуализации
    Поддерживает все режимы визуализации в одной системе"""
    
    def __init__(self):
        super().__init__(
            component_id="unified_visualization_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Архитектурные компоненты
        self.state_manager: Optional[StateManager] = None
        
        # Настройки
        self.settings = VisualizationSettings()
        self.camera_config = CameraConfig()
        
        # Panda3D компоненты
        self.scene_root: Optional[NodePath] = None
        self.camera_np: Optional[NodePath] = None
        self.main_camera: Optional[Camera] = None
        
        # Визуализация эмоций
        self.emotion_visuals: Dict[EmotionType, EmotionVisual] = {}
        self.active_emotion_effects: Dict[str, List[NodePath]] = {}
        
        # Освещение
        self.lights: Dict[str, NodePath] = {}
        self.ambient_light: Optional[AmbientLight] = None
        self.directional_light: Optional[DirectionalLight] = None
        
        # Эффекты и частицы
        self.particle_systems: Dict[str, Any] = {}
        self.visual_effects: Dict[str, NodePath] = {}
        
        # Статистика
        self.stats = {
            'rendered_objects': 0,
            'active_particles': 0,
            'active_lights': 0,
            'emotion_effects': 0,
            'frame_time': 0.0,
            'mode_switches': 0
        }
        
        logger.info("Объединенная система визуализации создана")
    
    def set_architecture_components(self, state_manager: StateManager, attribute_system=None):
        """Установка архитектурных компонентов"""
        self.state_manager = state_manager
        logger.info("Архитектурные компоненты установлены в UnifiedVisualizationSystem")
    
    def initialize(self) -> bool:
        """Инициализация системы визуализации"""
        try:
            logger.info("Инициализация объединенной системы визуализации...")
            
            # Регистрация состояний
            self._register_system_states()
            
            # Инициализация эмоциональной визуализации
            self._initialize_emotion_visuals()
            
            # Установка режима по умолчанию
            if not self._setup_visualization_mode(self.settings.mode):
                return False
            
            self.system_state = LifecycleState.READY
            logger.info("Объединенная система визуализации инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации объединенной системы визуализации: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def start(self) -> bool:
        """Запуск системы визуализации"""
        try:
            logger.info("Запуск объединенной системы визуализации...")
            
            if self.system_state != LifecycleState.READY:
                logger.error("Система не готова к запуску")
                return False
            
            # Запуск освещения
            self._setup_lighting()
            
            # Запуск эффектов
            self._start_visual_effects()
            
            self.system_state = LifecycleState.RUNNING
            logger.info("Объединенная система визуализации запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска объединенной системы визуализации: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def switch_mode(self, new_mode: VisualizationMode) -> bool:
        """Переключение режима визуализации"""
        try:
            logger.info(f"Переключение режима визуализации: {self.settings.mode} -> {new_mode}")
            
            if self.settings.mode == new_mode:
                logger.info("Режим уже установлен")
                return True
            
            old_mode = self.settings.mode
            self.settings.mode = new_mode
            
            # Настройка нового режима
            if self._setup_visualization_mode(new_mode):
                self.stats['mode_switches'] += 1
                logger.info(f"Режим визуализации переключен на {new_mode}")
                return True
            else:
                # Откат к предыдущему режиму
                self.settings.mode = old_mode
                logger.error(f"Не удалось переключить режим на {new_mode}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка переключения режима визуализации: {e}")
            return False
    
    def _setup_visualization_mode(self, mode: VisualizationMode) -> bool:
        """Настройка режима визуализации"""
        try:
            if mode == VisualizationMode.ISOMETRIC:
                return self._setup_isometric_mode()
            elif mode == VisualizationMode.PERSPECTIVE:
                return self._setup_perspective_mode()
            elif mode == VisualizationMode.TOP_DOWN:
                return self._setup_top_down_mode()
            elif mode == VisualizationMode.FIRST_PERSON:
                return self._setup_first_person_mode()
            elif mode == VisualizationMode.THIRD_PERSON:
                return self._setup_third_person_mode()
            else:
                logger.error(f"Неизвестный режим визуализации: {mode}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка настройки режима {mode}: {e}")
            return False
    
    def _setup_isometric_mode(self) -> bool:
        """Настройка изометрического режима"""
        try:
            if not self.scene_root:
                # Создаем корневой узел сцены если его нет
                from panda3d.core import render
                self.scene_root = render.attachNewNode("visualization_root")
            
            # Создание изометрической камеры
            camera = Camera("isometric_camera")
            
            # Настройка линзы для изометрии
            lens = OrthographicLens()
            lens.setFilmSize(40, 30)
            lens.setNearFar(-100, 100)
            camera.setLens(lens)
            
            # Создание NodePath для камеры
            self.camera_np = self.scene_root.attachNewNode(camera)
            self.main_camera = camera
            
            # Позиционирование камеры для изометрии
            self._update_isometric_camera_position()
            
            logger.info("Изометрический режим настроен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки изометрического режима: {e}")
            return False
    
    def _setup_perspective_mode(self) -> bool:
        """Настройка перспективного режима"""
        try:
            if not self.scene_root:
                from panda3d.core import render
                self.scene_root = render.attachNewNode("visualization_root")
            
            # Создание перспективной камеры
            camera = Camera("perspective_camera")
            
            # Настройка перспективной линзы
            lens = PerspectiveLens()
            lens.setFov(self.settings.field_of_view)
            lens.setNearFar(self.settings.near_plane, self.settings.far_plane)
            camera.setLens(lens)
            
            self.camera_np = self.scene_root.attachNewNode(camera)
            self.main_camera = camera
            
            # Позиционирование камеры
            self._update_perspective_camera_position()
            
            logger.info("Перспективный режим настроен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки перспективного режима: {e}")
            return False
    
    def _setup_top_down_mode(self) -> bool:
        """Настройка режима вида сверху"""
        try:
            if not self.scene_root:
                from panda3d.core import render
                self.scene_root = render.attachNewNode("visualization_root")
            
            camera = Camera("top_down_camera")
            lens = OrthographicLens()
            lens.setFilmSize(50, 50)
            lens.setNearFar(-100, 100)
            camera.setLens(lens)
            
            self.camera_np = self.scene_root.attachNewNode(camera)
            self.main_camera = camera
            
            # Камера смотрит строго вниз
            self.camera_np.setPos(0, 0, 50)
            self.camera_np.lookAt(0, 0, 0)
            
            logger.info("Режим вида сверху настроен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки режима вида сверху: {e}")
            return False
    
    def _setup_first_person_mode(self) -> bool:
        """Настройка режима от первого лица"""
        try:
            if not self.scene_root:
                from panda3d.core import render
                self.scene_root = render.attachNewNode("visualization_root")
            
            camera = Camera("first_person_camera")
            lens = PerspectiveLens()
            lens.setFov(90)  # Широкий угол обзора для FPS
            lens.setNearFar(0.1, 1000)
            camera.setLens(lens)
            
            self.camera_np = self.scene_root.attachNewNode(camera)
            self.main_camera = camera
            
            # Камера на уровне глаз
            self.camera_np.setPos(0, 0, 1.7)
            
            logger.info("Режим от первого лица настроен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки режима от первого лица: {e}")
            return False
    
    def _setup_third_person_mode(self) -> bool:
        """Настройка режима от третьего лица"""
        try:
            if not self.scene_root:
                from panda3d.core import render
                self.scene_root = render.attachNewNode("visualization_root")
            
            camera = Camera("third_person_camera")
            lens = PerspectiveLens()
            lens.setFov(75)
            lens.setNearFar(0.1, 1000)
            camera.setLens(lens)
            
            self.camera_np = self.scene_root.attachNewNode(camera)
            self.main_camera = camera
            
            # Камера позади и выше цели
            self.camera_np.setPos(0, -10, 5)
            self.camera_np.lookAt(0, 0, 0)
            
            logger.info("Режим от третьего лица настроен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки режима от третьего лица: {e}")
            return False
    
    def _update_isometric_camera_position(self):
        """Обновление позиции изометрической камеры"""
        try:
            if self.camera_np:
                # Изометрические углы
                x = self.camera_config.distance * math.cos(math.radians(self.camera_config.angle))
                y = self.camera_config.distance * math.sin(math.radians(self.camera_config.angle))
                z = self.camera_config.distance * 0.7  # Высота для изометрии
                
                # Позиция камеры
                camera_pos = self.camera_config.target + Vec3(x, y, z)
                self.camera_np.setPos(camera_pos)
                
                # Направление на цель
                self.camera_np.lookAt(self.camera_config.target)
                
        except Exception as e:
            logger.error(f"Ошибка обновления позиции изометрической камеры: {e}")
    
    def _update_perspective_camera_position(self):
        """Обновление позиции перспективной камеры"""
        try:
            if self.camera_np:
                # Сферические координаты
                x = self.camera_config.distance * math.cos(math.radians(self.camera_config.angle))
                y = self.camera_config.distance * math.sin(math.radians(self.camera_config.angle))
                z = self.camera_config.distance * 0.5
                
                camera_pos = self.camera_config.target + Vec3(x, y, z)
                self.camera_np.setPos(camera_pos)
                self.camera_np.lookAt(self.camera_config.target)
                
        except Exception as e:
            logger.error(f"Ошибка обновления позиции перспективной камеры: {e}")
    
    def _initialize_emotion_visuals(self):
        """Инициализация визуализации эмоций"""
        try:
            # Настройка цветов для эмоций
            emotion_colors = {
                EmotionType.JOY: Vec4(1.0, 1.0, 0.0, 0.8),        # Желтый
                EmotionType.SADNESS: Vec4(0.0, 0.0, 1.0, 0.8),    # Синий
                EmotionType.ANGER: Vec4(1.0, 0.0, 0.0, 0.8),      # Красный
                EmotionType.FEAR: Vec4(0.5, 0.0, 0.5, 0.8),       # Фиолетовый
                EmotionType.SURPRISE: Vec4(1.0, 0.5, 0.0, 0.8),   # Оранжевый
                EmotionType.DISGUST: Vec4(0.0, 0.5, 0.0, 0.8),    # Зеленый
                EmotionType.TRUST: Vec4(0.0, 1.0, 1.0, 0.8),      # Голубой
                EmotionType.ANTICIPATION: Vec4(1.0, 0.0, 1.0, 0.8), # Магента
                EmotionType.NEUTRAL: Vec4(0.7, 0.7, 0.7, 0.5)     # Серый
            }
            
            for emotion, color in emotion_colors.items():
                self.emotion_visuals[emotion] = EmotionVisual(
                    emotion_type=emotion,
                    color=color
                )
            
            logger.info("Визуализация эмоций инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации визуализации эмоций: {e}")
    
    def _setup_lighting(self):
        """Настройка освещения"""
        try:
            if not self.settings.enable_lighting:
                return
            
            # Ambient light
            self.ambient_light = AmbientLight("ambient")
            self.ambient_light.setColor(Vec4(0.3, 0.3, 0.3, 1))
            ambient_np = self.scene_root.attachNewNode(self.ambient_light)
            self.scene_root.setLight(ambient_np)
            self.lights["ambient"] = ambient_np
            
            # Directional light
            self.directional_light = DirectionalLight("sun")
            self.directional_light.setColor(Vec4(0.8, 0.8, 0.7, 1))
            self.directional_light.setDirection(Vec3(-1, -1, -1))
            sun_np = self.scene_root.attachNewNode(self.directional_light)
            self.scene_root.setLight(sun_np)
            self.lights["sun"] = sun_np
            
            logger.info("Освещение настроено")
            
        except Exception as e:
            logger.error(f"Ошибка настройки освещения: {e}")
    
    def _start_visual_effects(self):
        """Запуск визуальных эффектов"""
        try:
            if self.settings.enable_particles:
                # Инициализация систем частиц
                pass
            
            logger.info("Визуальные эффекты запущены")
            
        except Exception as e:
            logger.error(f"Ошибка запуска визуальных эффектов: {e}")
    
    def _register_system_states(self):
        """Регистрация состояний системы"""
        if self.state_manager:
            self.state_manager.set_state(
                f"{self.component_id}_settings",
                self.settings.__dict__,
                StateType.SETTINGS
            )
            
            self.state_manager.set_state(
                f"{self.component_id}_stats",
                self.stats,
                StateType.STATISTICS
            )
    
    def update(self, delta_time: float):
        """Обновление системы визуализации"""
        if self.system_state != LifecycleState.RUNNING:
            return
        
        try:
            start_time = time.time()
            
            # Обновление камеры в зависимости от режима
            if self.settings.mode == VisualizationMode.ISOMETRIC:
                self._update_isometric_camera_position()
            elif self.settings.mode == VisualizationMode.PERSPECTIVE:
                self._update_perspective_camera_position()
            
            # Обновление эффектов эмоций
            self._update_emotion_effects(delta_time)
            
            # Обновление статистики
            self.stats['frame_time'] = time.time() - start_time
            
            # Обновление состояния в менеджере
            if self.state_manager:
                self.state_manager.set_state(
                    f"{self.component_id}_stats",
                    self.stats,
                    StateType.STATISTICS
                )
                
        except Exception as e:
            logger.error(f"Ошибка обновления системы визуализации: {e}")
    
    def _update_emotion_effects(self, delta_time: float):
        """Обновление эффектов эмоций"""
        try:
            # Здесь будет логика обновления эмоциональных эффектов
            pass
        except Exception as e:
            logger.error(f"Ошибка обновления эффектов эмоций: {e}")
    
    def stop(self) -> bool:
        """Остановка системы визуализации"""
        try:
            logger.info("Остановка объединенной системы визуализации...")
            
            # Очистка эффектов
            self._cleanup_effects()
            
            # Очистка освещения
            self._cleanup_lighting()
            
            self.system_state = LifecycleState.STOPPED
            logger.info("Объединенная система визуализации остановлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки системы визуализации: {e}")
            return False
    
    def _cleanup_effects(self):
        """Очистка эффектов"""
        try:
            for effects in self.active_emotion_effects.values():
                for effect in effects:
                    effect.removeNode()
            self.active_emotion_effects.clear()
            
            for effect in self.visual_effects.values():
                effect.removeNode()
            self.visual_effects.clear()
            
        except Exception as e:
            logger.error(f"Ошибка очистки эффектов: {e}")
    
    def _cleanup_lighting(self):
        """Очистка освещения"""
        try:
            for light in self.lights.values():
                light.removeNode()
            self.lights.clear()
            
        except Exception as e:
            logger.error(f"Ошибка очистки освещения: {e}")
    
    def destroy(self) -> bool:
        """Уничтожение системы визуализации"""
        try:
            logger.info("Уничтожение объединенной системы визуализации...")
            
            # Остановка если запущена
            if self.system_state == LifecycleState.RUNNING:
                self.stop()
            
            # Очистка всех ресурсов
            self._cleanup_effects()
            self._cleanup_lighting()
            
            if self.scene_root:
                self.scene_root.removeNode()
            
            self.emotion_visuals.clear()
            self.particle_systems.clear()
            
            self.system_state = LifecycleState.DESTROYED
            logger.info("Объединенная система визуализации уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы визуализации: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'component_id': self.component_id,
            'state': self.system_state.value,
            'mode': self.settings.mode.value,
            'stats': self.stats.copy(),
            'active_effects': len(self.active_emotion_effects),
            'lights_count': len(self.lights)
        }
