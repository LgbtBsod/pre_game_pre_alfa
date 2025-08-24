#!/usr/bin/env python3
"""
Render System - Система рендеринга
Отвечает только за отрисовку, камеры и настройки графики
"""

import logging
from typing import Dict, Any, Optional
from panda3d.core import (
    WindowProperties, AntialiasAttrib, TransparencyAttrib,
    Vec3, Vec4, Point3, LVector3,
    DirectionalLight, AmbientLight, Spotlight,
    PerspectiveLens, OrthographicLens,
    TextNode, PandaNode, NodePath,
    GraphicsPipe, FrameBufferProperties
)
from ...core.interfaces import ISystem, IRenderable

logger = logging.getLogger(__name__)

class RenderSystem(ISystem):
    """
    Система рендеринга
    Управляет камерами, освещением и настройками графики
    """
    
    def __init__(self, render_node, window):
        self.render_node = render_node
        self.window = window
        
        # Камеры
        self.main_camera = None
        self.ui_camera = None
        
        # Освещение
        self.directional_light = None
        self.ambient_light = None
        self.spotlight = None
        
        # Настройки рендеринга
        self.antialiasing_enabled = True
        self.transparency_enabled = True
        self.depth_test_enabled = True
        
        # Состояние
        self.is_initialized = False
        
        logger.info("Система рендеринга инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы рендеринга"""
        try:
            logger.info("Инициализация системы рендеринга...")
            
            # Настройка камер
            self._setup_cameras()
            
            # Настройка освещения
            self._setup_lighting()
            
            # Настройка рендеринга
            self._setup_rendering()
            
            self.is_initialized = True
            logger.info("Система рендеринга успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы рендеринга: {e}")
            return False
    
    def _setup_cameras(self):
        """Настройка камер"""
        try:
            # Основная камера для 3D сцены
            self.main_camera = self.render_node.attachNewNode("main_camera")
            self.main_camera.setPos(0, -20, 10)
            self.main_camera.lookAt(0, 0, 0)
            
            # UI камера для 2D элементов
            self.ui_camera = self.render_node.attachNewNode("ui_camera")
            self.ui_camera.setPos(0, 0, 0)
            
            # Настройка изометрической проекции для основной камеры
            lens = OrthographicLens()
            lens.setFilmSize(40, 30)
            lens.setNearFar(-100, 100)
            
            # Создаем узел камеры
            camera_node = PandaNode("camera")
            camera_node.setLens(lens)
            self.main_camera.attachNewNode(camera_node)
            
            logger.debug("Камеры настроены")
            
        except Exception as e:
            logger.error(f"Ошибка настройки камер: {e}")
    
    def _setup_lighting(self):
        """Настройка освещения"""
        try:
            # Основное направленное освещение
            self.directional_light = DirectionalLight('dlight')
            self.directional_light.setColor((0.8, 0.8, 0.8, 1))
            dlnp = self.render_node.attachNewNode(self.directional_light)
            dlnp.setHpr(45, -45, 0)
            self.render_node.setLight(dlnp)
            
            # Фоновое освещение
            self.ambient_light = AmbientLight('alight')
            self.ambient_light.setColor((0.2, 0.2, 0.2, 1))
            alnp = self.render_node.attachNewNode(self.ambient_light)
            self.render_node.setLight(alnp)
            
            logger.debug("Освещение настроено")
            
        except Exception as e:
            logger.error(f"Ошибка настройки освещения: {e}")
    
    def _setup_rendering(self):
        """Настройка рендеринга"""
        try:
            # Включение сглаживания
            if self.antialiasing_enabled:
                self.render_node.setAntialias(AntialiasAttrib.MAuto)
            
            # Настройка прозрачности
            if self.transparency_enabled:
                self.render_node.setTransparency(TransparencyAttrib.MAlpha)
            
            # Настройка глубины
            if self.depth_test_enabled:
                self.render_node.setDepthWrite(True)
                self.render_node.setDepthTest(True)
            
            logger.debug("Рендеринг настроен")
            
        except Exception as e:
            logger.error(f"Ошибка настройки рендеринга: {e}")
    
    def set_camera_position(self, camera_name: str, position: Vec3, look_at: Vec3 = None):
        """Установка позиции камеры"""
        try:
            if camera_name == "main":
                camera = self.main_camera
            elif camera_name == "ui":
                camera = self.ui_camera
            else:
                logger.warning(f"Неизвестная камера: {camera_name}")
                return
            
            camera.setPos(position)
            if look_at:
                camera.lookAt(look_at)
            
            logger.debug(f"Позиция камеры {camera_name} изменена")
            
        except Exception as e:
            logger.error(f"Ошибка изменения позиции камеры: {e}")
    
    def add_light(self, light_type: str, position: Vec3, color: Vec4, **kwargs):
        """Добавление источника света"""
        try:
            if light_type == "directional":
                light = DirectionalLight(f"light_{id(self)}")
                light.setColor(color)
                light_np = self.render_node.attachNewNode(light)
                light_np.setPos(position)
                
                if "direction" in kwargs:
                    light_np.setHpr(kwargs["direction"])
                
                self.render_node.setLight(light_np)
                
            elif light_type == "point":
                light = Spotlight(f"light_{id(self)}")
                light.setColor(color)
                light_np = self.render_node.attachNewNode(light)
                light_np.setPos(position)
                
                if "cone_angle" in kwargs:
                    light.setSpotAngle(kwargs["cone_angle"])
                
                self.render_node.setLight(light_np)
            
            logger.debug(f"Добавлен источник света типа {light_type}")
            
        except Exception as e:
            logger.error(f"Ошибка добавления источника света: {e}")
    
    def set_rendering_options(self, antialiasing: bool = None, transparency: bool = None, 
                             depth_test: bool = None):
        """Установка опций рендеринга"""
        try:
            if antialiasing is not None:
                self.antialiasing_enabled = antialiasing
                if antialiasing:
                    self.render_node.setAntialias(AntialiasAttrib.MAuto)
                else:
                    self.render_node.clearAntialias()
            
            if transparency is not None:
                self.transparency_enabled = transparency
                if transparency:
                    self.render_node.setTransparency(TransparencyAttrib.MAlpha)
                else:
                    self.render_node.clearTransparency()
            
            if depth_test is not None:
                self.depth_test_enabled = depth_test
                self.render_node.setDepthWrite(depth_test)
                self.render_node.setDepthTest(depth_test)
            
            logger.debug("Опции рендеринга обновлены")
            
        except Exception as e:
            logger.error(f"Ошибка обновления опций рендеринга: {e}")
    
    def get_camera_info(self, camera_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о камере"""
        try:
            if camera_name == "main":
                camera = self.main_camera
            elif camera_name == "ui":
                camera = self.ui_camera
            else:
                return None
            
            if camera:
                return {
                    "position": camera.getPos(),
                    "rotation": camera.getHpr(),
                    "scale": camera.getScale()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о камере: {e}")
            return None
    
    def render_scene(self, scene_node):
        """Отрисовка сцены"""
        if not self.is_initialized:
            return
        
        try:
            # Отрисовка происходит автоматически в Panda3D
            # Здесь можно добавить дополнительную логику рендеринга
            pass
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга сцены: {e}")
    
    def update(self, delta_time: float) -> None:
        """Обновление системы рендеринга"""
        if not self.is_initialized:
            return
        
        try:
            # Обновление динамического освещения
            self._update_dynamic_lighting(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы рендеринга: {e}")
    
    def _update_dynamic_lighting(self, delta_time: float):
        """Обновление динамического освещения"""
        # Здесь можно добавить логику для движущихся источников света
        # или других динамических эффектов
        pass
    
    def cleanup(self) -> None:
        """Очистка системы рендеринга"""
        logger.info("Очистка системы рендеринга...")
        
        try:
            # Очищаем источники света
            if self.directional_light:
                self.directional_light = None
            
            if self.ambient_light:
                self.ambient_light = None
            
            if self.spotlight:
                self.spotlight = None
            
            # Очищаем камеры
            if self.main_camera:
                self.main_camera.removeNode()
                self.main_camera = None
            
            if self.ui_camera:
                self.ui_camera.removeNode()
                self.ui_camera = None
            
            self.is_initialized = False
            logger.info("Система рендеринга очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы рендеринга: {e}")
