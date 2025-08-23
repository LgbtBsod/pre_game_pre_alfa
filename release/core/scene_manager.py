"""
Система управления сценами игры.
Обеспечивает переходы между различными состояниями игры.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SceneType(Enum):
    """Типы сцен"""
    MAIN_MENU = "main_menu"
    GAME = "game"
    PAUSE = "pause"
    SETTINGS = "settings"
    INVENTORY = "inventory"
    LOADING = "loading"


class Scene(ABC):
    """Абстрактный базовый класс для всех сцен"""
    
    def __init__(self, scene_manager: 'SceneManager'):
        self.scene_manager = scene_manager
        self.is_active = False
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация сцены"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Обновление сцены"""
        pass
    
    @abstractmethod
    def render(self, screen) -> None:
        """Отрисовка сцены"""
        pass
    
    @abstractmethod
    def handle_events(self, events) -> None:
        """Обработка событий"""
        pass
    
    def activate(self) -> None:
        """Активация сцены"""
        if not self.is_initialized:
            if self.initialize():
                self.is_initialized = True
            else:
                logger.error(f"Не удалось инициализировать сцену {self.__class__.__name__}")
                return
        
        self.is_active = True
        logger.info(f"Сцена {self.__class__.__name__} активирована")
    
    def deactivate(self) -> None:
        """Деактивация сцены"""
        self.is_active = False
        logger.info(f"Сцена {self.__class__.__name__} деактивирована")
    
    def cleanup(self) -> None:
        """Очистка ресурсов сцены"""
        self.is_active = False
        self.is_initialized = False
        logger.info(f"Сцена {self.__class__.__name__} очищена")


class SceneManager:
    """Менеджер сцен"""
    
    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.previous_scene: Optional[Scene] = None
        self.scene_stack: list = []
        
        logger.info("Менеджер сцен инициализирован")
    
    def register_scene(self, scene_name: str, scene: Scene) -> None:
        """Регистрация сцены"""
        self.scenes[scene_name] = scene
        logger.info(f"Зарегистрирована сцена: {scene_name}")
    
    def switch_scene(self, scene_name: str) -> bool:
        """Переключение на другую сцену"""
        if scene_name not in self.scenes:
            logger.error(f"Сцена {scene_name} не найдена")
            return False
        
        # Сохраняем предыдущую сцену
        if self.current_scene:
            self.previous_scene = self.current_scene
            self.current_scene.deactivate()
        
        # Активируем новую сцену
        self.current_scene = self.scenes[scene_name]
        self.current_scene.activate()
        
        logger.info(f"Переключение на сцену: {scene_name}")
        return True
    
    def push_scene(self, scene_name: str) -> bool:
        """Добавление сцены в стек"""
        if scene_name not in self.scenes:
            logger.error(f"Сцена {scene_name} не найдена")
            return False
        
        # Сохраняем текущую сцену в стеке
        if self.current_scene:
            self.scene_stack.append(self.current_scene)
            self.current_scene.deactivate()
        
        # Активируем новую сцену
        self.current_scene = self.scenes[scene_name]
        self.current_scene.activate()
        
        logger.info(f"Сцена {scene_name} добавлена в стек")
        return True
    
    def pop_scene(self) -> bool:
        """Извлечение сцены из стека"""
        if not self.scene_stack:
            logger.warning("Стек сцен пуст")
            return False
        
        # Деактивируем текущую сцену
        if self.current_scene:
            self.current_scene.deactivate()
        
        # Восстанавливаем предыдущую сцену
        self.current_scene = self.scene_stack.pop()
        self.current_scene.activate()
        
        logger.info("Сцена извлечена из стека")
        return True
    
    def update(self, delta_time: float) -> None:
        """Обновление текущей сцены"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.update(delta_time)
    
    def render(self, screen) -> None:
        """Отрисовка текущей сцены"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.render(screen)
    
    def handle_events(self, events) -> None:
        """Обработка событий текущей сцены"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.handle_events(events)
    
    def get_current_scene_name(self) -> Optional[str]:
        """Получение имени текущей сцены"""
        if self.current_scene:
            for name, scene in self.scenes.items():
                if scene == self.current_scene:
                    return name
        return None
    
    def cleanup(self) -> None:
        """Очистка всех сцен"""
        for scene in self.scenes.values():
            scene.cleanup()
        
        self.scenes.clear()
        self.current_scene = None
        self.previous_scene = None
        self.scene_stack.clear()
        
        logger.info("Все сцены очищены")
