#!/usr/bin/env python3
"""
Scene Manager - Менеджер сцен для Panda3D
Отвечает только за управление игровыми сценами и переключение между ними
"""

import logging
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class Scene(ABC):
    """Базовый класс для всех сцен"""
    
    def __init__(self, name: str):
        self.name = name
        self.scene_manager = None
        self.is_initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация сцены"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float):
        """Обновление сцены"""
        pass
    
    @abstractmethod
    def render(self, render_node):
        """Отрисовка сцены"""
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """Обработка событий"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Очистка сцены"""
        pass

class SceneManager:
    """Менеджер сцен для Panda3D"""
    
    def __init__(self, render_node, resource_manager):
        self.render_node = render_node
        self.resource_manager = resource_manager
        
        # Сцены
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Optional[Scene] = None
        self.previous_scene: Optional[Scene] = None
        
        # Состояние переключения
        self.transitioning = False
        self.transition_type = "instant"
        self.transition_progress = 0.0
        
        logger.info("Менеджер сцен Panda3D инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация менеджера сцен"""
        try:
            logger.info("Инициализация менеджера сцен...")
            
            # Создание корневого узла для сцен
            self.scenes_root = self.render_node.attachNewNode("scenes_root")
            
            logger.info("Менеджер сцен успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера сцен: {e}")
            return False
    
    def register_scene(self, name: str, scene: Scene):
        """Регистрация сцены"""
        if name in self.scenes:
            logger.warning(f"Сцена {name} уже зарегистрирована")
            return False
        
        scene.scene_manager = self
        self.scenes[name] = scene
        
        # Инициализация сцены
        if not scene.initialize():
            logger.error(f"Не удалось инициализировать сцену {name}")
            return False
        
        logger.info(f"Сцена {name} зарегистрирована и инициализирована")
        return True
    
    def unregister_scene(self, name: str):
        """Отмена регистрации сцены"""
        if name not in self.scenes:
            return False
        
        scene = self.scenes[name]
        scene.cleanup()
        del self.scenes[name]
        
        logger.info(f"Сцена {name} удалена")
        return True
    
    def set_active_scene(self, name: str):
        """Установка активной сцены"""
        if name not in self.scenes:
            logger.error(f"Сцена {name} не найдена")
            return False
        
        # Сохраняем предыдущую сцену
        if self.active_scene:
            self.previous_scene = self.active_scene
        
        # Устанавливаем новую активную сцену
        self.active_scene = self.scenes[name]
        
        logger.info(f"Активная сцена изменена на {name}")
        return True
    
    def switch_to_scene(self, name: str, transition_type: str = "instant"):
        """Переключение на сцену с переходом"""
        if name not in self.scenes:
            logger.error(f"Сцена {name} не найдена")
            return False
        
        if self.transitioning:
            logger.warning("Переход уже выполняется")
            return False
        
        # Начинаем переход
        self.transitioning = True
        self.transition_type = transition_type
        self.transition_progress = 0.0
        
        # Сохраняем предыдущую сцену
        if self.active_scene:
            self.previous_scene = self.active_scene
        
        # Устанавливаем новую активную сцену
        self.active_scene = self.scenes[name]
        
        logger.info(f"Переключение на сцену {name} с переходом {transition_type}")
        return True
    
    def update(self, delta_time: float):
        """Обновление менеджера сцен"""
        # Обновление перехода
        if self.transitioning:
            self._update_transition(delta_time)
        
        # Обновление активной сцены
        if self.active_scene:
            self.active_scene.update(delta_time)
    
    def _update_transition(self, delta_time: float):
        """Обновление перехода между сценами"""
        if self.transition_type == "instant":
            self.transition_progress = 1.0
        elif self.transition_type == "fade":
            self.transition_progress += delta_time / 0.5  # 0.5 секунды на переход
        elif self.transition_type == "slide":
            self.transition_progress += delta_time / 0.3  # 0.3 секунды на переход
        
        # Завершение перехода
        if self.transition_progress >= 1.0:
            self.transitioning = False
            self.transition_progress = 1.0
            logger.debug("Переход между сценами завершен")
    
    def render(self, render_node):
        """Отрисовка активной сцены"""
        if self.active_scene:
            self.active_scene.render(render_node)
    
    def handle_event(self, event):
        """Обработка событий"""
        if self.active_scene:
            self.active_scene.handle_event(event)
    
    def get_scene(self, name: str) -> Optional[Scene]:
        """Получение сцены по имени"""
        return self.scenes.get(name)
    
    def get_active_scene_name(self) -> Optional[str]:
        """Получение имени активной сцены"""
        if self.active_scene:
            return self.active_scene.name
        return None
    
    def get_scene_names(self) -> list:
        """Получение списка имен всех сцен"""
        return list(self.scenes.keys())
    
    def is_scene_active(self, name: str) -> bool:
        """Проверка, является ли сцена активной"""
        return self.active_scene and self.active_scene.name == name
    
    def cleanup(self):
        """Очистка менеджера сцен"""
        logger.info("Очистка менеджера сцен...")
        
        # Очистка всех сцен
        for scene in self.scenes.values():
            scene.cleanup()
        
        self.scenes.clear()
        self.active_scene = None
        self.previous_scene = None
        
        logger.info("Менеджер сцен очищен")
