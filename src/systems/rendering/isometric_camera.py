#!/usr/bin/env python3
"""
Изометрическая камера AI-EVOLVE
Ортографическая проекция с управлением
"""

import logging
import math
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from panda3d.core import (
    OrthographicLens, Camera, NodePath, Vec3, Point3,
    WindowProperties, GraphicsPipe, GraphicsEngine,
    FrameBufferProperties, GraphicsOutput
)

logger = logging.getLogger(__name__)

@dataclass
class CameraSettings:
    """Настройки камеры"""
    film_size_x: float = 20.0
    film_size_y: float = 15.0
    near_plane: float = 0.1
    far_plane: float = 1000.0
    position: Tuple[float, float, float] = (15, -15, 15)
    look_at: Tuple[float, float, float] = (0, 0, 0)
    follow_speed: float = 0.1
    zoom_speed: float = 0.1
    rotation_speed: float = 0.05

@dataclass
class CameraState:
    """Состояние камеры"""
    is_following: bool = False
    is_centered: bool = False
    current_zoom: float = 1.0
    current_rotation: float = 0.0
    target_position: Optional[Tuple[float, float, float]] = None
    last_update_time: float = 0.0

class IsometricCamera:
    """Класс изометрической камеры"""
    
    def __init__(self, showbase, camera_settings: CameraSettings = None):
        self.showbase = showbase
        self.camera = showbase.camera
        self.settings = camera_settings or CameraSettings()
        self.state = CameraState()
        
        # Цель для следования
        self.target = None
        
        # Настройка изометрической проекции
        self._setup_isometric_projection()
        
        # Позиционирование камеры
        self._setup_camera_position()
        
        # Управление камерой
        self._setup_camera_controls()
        
        logger.info("Изометрическая камера инициализирована")
    
    def _setup_isometric_projection(self) -> None:
        """Настройка изометрической проекции"""
        try:
            # Создаем ортографическую линзу
            self.lens = OrthographicLens()
            
            # Устанавливаем размер пленки
            self.lens.setFilmSize(self.settings.film_size_x, self.settings.film_size_y)
            
            # Устанавливаем ближнюю и дальнюю плоскости
            self.lens.setNear(self.settings.near_plane)
            self.lens.setFar(self.settings.far_plane)
            
            # Применяем линзу к камере
            self.camera.node().setLens(self.lens)
            
            logger.debug("Настроена ортографическая проекция")
            
        except Exception as e:
            logger.error(f"Ошибка настройки изометрической проекции: {e}")
    
    def _setup_camera_position(self) -> None:
        """Настройка позиции камеры"""
        try:
            # Устанавливаем начальную позицию
            self.camera.setPos(*self.settings.position)
            
            # Направляем камеру на цель
            self.camera.lookAt(*self.settings.look_at)
            
            logger.debug("Настроена позиция камеры")
            
        except Exception as e:
            logger.error(f"Ошибка настройки позиции камеры: {e}")
    
    def _setup_camera_controls(self) -> None:
        """Настройка управления камерой"""
        try:
            # Привязываем клавиши управления
            self.showbase.accept("c", self.toggle_follow)
            self.showbase.accept("space", self.center_on_target)
            self.showbase.accept("wheel_up", self.zoom_in)
            self.showbase.accept("wheel_down", self.zoom_out)
            self.showbase.accept("arrow_left", self.rotate_left)
            self.showbase.accept("arrow_right", self.rotate_right)
            
            logger.debug("Настроено управление камерой")
            
        except Exception as e:
            logger.error(f"Ошибка настройки управления камерой: {e}")
    
    def set_target(self, target: NodePath) -> None:
        """Установка цели для следования"""
        try:
            self.target = target
            logger.info(f"Установлена цель камеры: {target}")
            
        except Exception as e:
            logger.error(f"Ошибка установки цели камеры: {e}")
    
    def clear_target(self) -> None:
        """Очистка цели камеры"""
        try:
            self.target = None
            self.state.is_following = False
            logger.info("Цель камеры очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки цели камеры: {e}")
    
    def toggle_follow(self) -> None:
        """Переключение режима следования"""
        try:
            self.state.is_following = not self.state.is_following
            
            if self.state.is_following:
                logger.info("Включен режим следования камеры")
            else:
                logger.info("Выключен режим следования камеры")
                
        except Exception as e:
            logger.error(f"Ошибка переключения режима следования: {e}")
    
    def center_on_target(self) -> None:
        """Центрирование на цели"""
        try:
            if self.target:
                target_pos = self.target.getPos()
                self.camera.lookAt(target_pos)
                self.state.is_centered = True
                logger.info("Камера центрирована на цели")
            else:
                logger.warning("Нет цели для центрирования")
                
        except Exception as e:
            logger.error(f"Ошибка центрирования на цели: {e}")
    
    def zoom_in(self) -> None:
        """Приближение камеры"""
        try:
            new_zoom = self.state.current_zoom + self.settings.zoom_speed
            self._apply_zoom(new_zoom)
            logger.debug(f"Приближение камеры: {new_zoom}")
            
        except Exception as e:
            logger.error(f"Ошибка приближения камеры: {e}")
    
    def zoom_out(self) -> None:
        """Отдаление камеры"""
        try:
            new_zoom = self.state.current_zoom - self.settings.zoom_speed
            self._apply_zoom(new_zoom)
            logger.debug(f"Отдаление камеры: {new_zoom}")
            
        except Exception as e:
            logger.error(f"Ошибка отдаления камеры: {e}")
    
    def _apply_zoom(self, zoom_level: float) -> None:
        """Применение масштабирования"""
        try:
            # Ограничиваем масштабирование
            zoom_level = max(0.1, min(5.0, zoom_level))
            
            # Обновляем размер пленки
            new_film_x = self.settings.film_size_x / zoom_level
            new_film_y = self.settings.film_size_y / zoom_level
            
            self.lens.setFilmSize(new_film_x, new_film_y)
            self.state.current_zoom = zoom_level
            
        except Exception as e:
            logger.error(f"Ошибка применения масштабирования: {e}")
    
    def rotate_left(self) -> None:
        """Поворот камеры влево"""
        try:
            new_rotation = self.state.current_rotation + self.settings.rotation_speed
            self._apply_rotation(new_rotation)
            logger.debug(f"Поворот камеры влево: {new_rotation}")
            
        except Exception as e:
            logger.error(f"Ошибка поворота камеры влево: {e}")
    
    def rotate_right(self) -> None:
        """Поворот камеры вправо"""
        try:
            new_rotation = self.state.current_rotation - self.settings.rotation_speed
            self._apply_rotation(new_rotation)
            logger.debug(f"Поворот камеры вправо: {new_rotation}")
            
        except Exception as e:
            logger.error(f"Ошибка поворота камеры вправо: {e}")
    
    def _apply_rotation(self, rotation: float) -> None:
        """Применение поворота"""
        try:
            # Ограничиваем поворот
            rotation = rotation % (2 * math.pi)
            
            # Вычисляем новую позицию камеры
            radius = math.sqrt(sum(x*x for x in self.settings.position))
            x = radius * math.cos(rotation)
            y = radius * math.sin(rotation)
            z = self.settings.position[2]
            
            # Обновляем позицию камеры
            self.camera.setPos(x, y, z)
            self.camera.lookAt(*self.settings.look_at)
            
            self.state.current_rotation = rotation
            
        except Exception as e:
            logger.error(f"Ошибка применения поворота: {e}")
    
    def set_camera_position(self, position: Tuple[float, float, float]) -> None:
        """Установка позиции камеры"""
        try:
            self.camera.setPos(*position)
            logger.debug(f"Установлена позиция камеры: {position}")
            
        except Exception as e:
            logger.error(f"Ошибка установки позиции камеры: {e}")
    
    def set_look_at(self, target: Tuple[float, float, float]) -> None:
        """Установка точки обзора"""
        try:
            self.camera.lookAt(*target)
            logger.debug(f"Установлена точка обзора: {target}")
            
        except Exception as e:
            logger.error(f"Ошибка установки точки обзора: {e}")
    
    def get_camera_position(self) -> Tuple[float, float, float]:
        """Получение позиции камеры"""
        try:
            pos = self.camera.getPos()
            return (pos.x, pos.y, pos.z)
            
        except Exception as e:
            logger.error(f"Ошибка получения позиции камеры: {e}")
            return (0, 0, 0)
    
    def get_camera_rotation(self) -> float:
        """Получение поворота камеры"""
        try:
            return self.state.current_rotation
            
        except Exception as e:
            logger.error(f"Ошибка получения поворота камеры: {e}")
            return 0.0
    
    def get_camera_zoom(self) -> float:
        """Получение масштаба камеры"""
        try:
            return self.state.current_zoom
            
        except Exception as e:
            logger.error(f"Ошибка получения масштаба камеры: {e}")
            return 1.0
    
    def reset_camera(self) -> None:
        """Сброс камеры в исходное положение"""
        try:
            # Сбрасываем позицию
            self.camera.setPos(*self.settings.position)
            self.camera.lookAt(*self.settings.look_at)
            
            # Сбрасываем состояние
            self.state.is_following = False
            self.state.is_centered = False
            self.state.current_zoom = 1.0
            self.state.current_rotation = 0.0
            
            # Сбрасываем масштабирование
            self.lens.setFilmSize(self.settings.film_size_x, self.settings.film_size_y)
            
            logger.info("Камера сброшена в исходное положение")
            
        except Exception as e:
            logger.error(f"Ошибка сброса камеры: {e}")
    
    def update(self, delta_time: float) -> None:
        """Обновление камеры"""
        try:
            # Обновляем следование за целью
            if self.state.is_following and self.target:
                self._update_following(delta_time)
            
            # Обновляем состояние
            self.state.last_update_time += delta_time
            
        except Exception as e:
            logger.error(f"Ошибка обновления камеры: {e}")
    
    def _update_following(self, delta_time: float) -> None:
        """Обновление следования за целью"""
        try:
            if not self.target:
                return
            
            # Получаем позицию цели
            target_pos = self.target.getPos()
            current_pos = self.camera.getPos()
            
            # Вычисляем новую позицию с плавным переходом
            new_x = current_pos.x + (target_pos.x - current_pos.x) * self.settings.follow_speed
            new_y = current_pos.y + (target_pos.y - current_pos.y) * self.settings.follow_speed
            new_z = current_pos.z + (target_pos.z - current_pos.z) * self.settings.follow_speed
            
            # Применяем новую позицию
            self.camera.setPos(new_x, new_y, new_z)
            
            # Направляем камеру на цель
            self.camera.lookAt(target_pos)
            
        except Exception as e:
            logger.error(f"Ошибка обновления следования: {e}")
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Получение информации о камере"""
        try:
            return {
                "position": self.get_camera_position(),
                "rotation": self.get_camera_rotation(),
                "zoom": self.get_camera_zoom(),
                "is_following": self.state.is_following,
                "is_centered": self.state.is_centered,
                "target": str(self.target) if self.target else None,
                "film_size": (self.lens.getFilmSize()[0], self.lens.getFilmSize()[1]),
                "near_plane": self.lens.getNear(),
                "far_plane": self.lens.getFar()
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о камере: {e}")
            return {}
    
    def set_camera_settings(self, settings: CameraSettings) -> None:
        """Обновление настроек камеры"""
        try:
            self.settings = settings
            
            # Применяем новые настройки
            self._setup_isometric_projection()
            self._setup_camera_position()
            
            logger.info("Настройки камеры обновлены")
            
        except Exception as e:
            logger.error(f"Ошибка обновления настроек камеры: {e}")
    
    def create_camera_effect(self, effect_type: str, duration: float, **kwargs) -> None:
        """Создание эффекта камеры"""
        try:
            if effect_type == "shake":
                self._create_shake_effect(duration, **kwargs)
            elif effect_type == "zoom":
                self._create_zoom_effect(duration, **kwargs)
            elif effect_type == "rotation":
                self._create_rotation_effect(duration, **kwargs)
            else:
                logger.warning(f"Неизвестный тип эффекта камеры: {effect_type}")
                
        except Exception as e:
            logger.error(f"Ошибка создания эффекта камеры: {e}")
    
    def _create_shake_effect(self, duration: float, intensity: float = 0.1) -> None:
        """Создание эффекта тряски камеры"""
        try:
            # TODO: Реализация эффекта тряски
            logger.debug(f"Создан эффект тряски камеры: {duration}s, {intensity}")
            
        except Exception as e:
            logger.error(f"Ошибка создания эффекта тряски: {e}")
    
    def _create_zoom_effect(self, duration: float, target_zoom: float = 1.5) -> None:
        """Создание эффекта масштабирования"""
        try:
            # TODO: Реализация эффекта масштабирования
            logger.debug(f"Создан эффект масштабирования: {duration}s, {target_zoom}")
            
        except Exception as e:
            logger.error(f"Ошибка создания эффекта масштабирования: {e}")
    
    def _create_rotation_effect(self, duration: float, target_rotation: float = 0.0) -> None:
        """Создание эффекта поворота"""
        try:
            # TODO: Реализация эффекта поворота
            logger.debug(f"Создан эффект поворота: {duration}s, {target_rotation}")
            
        except Exception as e:
            logger.error(f"Ошибка создания эффекта поворота: {e}")
