#!/usr/bin/env python3
"""
Scene Manager - Менеджер сцен
Управляет переключением между игровыми сценами и их жизненным циклом
"""

import logging
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
import pygame

logger = logging.getLogger(__name__)

class Scene(ABC):
    """Базовый класс для всех игровых сцен"""
    
    def __init__(self, name: str):
        self.name = name
        self.active = False
        self.initialized = False
        self.scene_manager = None  # Ссылка на менеджер сцен
        
    def set_scene_manager(self, scene_manager):
        """Установка ссылки на менеджер сцен"""
        self.scene_manager = scene_manager
        
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация сцены"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float):
        """Обновление состояния сцены"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Отрисовка сцены"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """Обработка событий"""
        pass
    
    def activate(self):
        """Активация сцены"""
        if not self.initialized:
            if not self.initialize():
                logger.error(f"Не удалось инициализировать сцену {self.name}")
                return False
        
        self.active = True
        logger.info(f"Сцена {self.name} активирована")
        return True
    
    def deactivate(self):
        """Деактивация сцены"""
        self.active = False
        logger.info(f"Сцена {self.name} деактивирована")
    
    def cleanup(self):
        """Очистка ресурсов сцены"""
        self.active = False
        self.initialized = False
        logger.info(f"Сцена {self.name} очищена")

class SceneManager:
    """Менеджер сцен"""
    
    def __init__(self, screen: pygame.Surface, resource_manager):
        self.screen = screen
        self.resource_manager = resource_manager
        
        # Сцены
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Optional[Scene] = None
        self.previous_scene: Optional[Scene] = None
        
        # Переходы между сценами
        self.transitioning = False
        self.transition_type = "fade"  # fade, slide, instant
        
        logger.info("Менеджер сцен инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация менеджера сцен"""
        try:
            logger.info("Инициализация менеджера сцен...")
            
            # Создание базовых сцен
            self._create_base_scenes()
            
            logger.info("Менеджер сцен успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера сцен: {e}")
            return False
    
    def _create_base_scenes(self):
        """Создание базовых сцен"""
        try:
            # Создаем базовые сцены
            try:
                from scenes.menu_scene import MenuScene
                from scenes.game_scene import GameScene
                from scenes.pause_scene import PauseScene
                from scenes.settings_scene import SettingsScene
                from scenes.load_scene import LoadScene
            except ImportError:
                from src.scenes.menu_scene import MenuScene
                from src.scenes.game_scene import GameScene
                from src.scenes.pause_scene import PauseScene
                from src.scenes.settings_scene import SettingsScene
                from src.scenes.load_scene import LoadScene
            
            # Регистрируем сцены
            self.register_scene("menu", MenuScene())
            self.register_scene("game", GameScene())
            self.register_scene("pause", PauseScene())
            self.register_scene("settings", SettingsScene())
            self.register_scene("load_game", LoadScene())
            
        except ImportError as e:
            logger.warning(f"Не удалось импортировать некоторые сцены: {e}")
            # Создаем заглушки
            self._create_stub_scenes()
    
    def _create_stub_scenes(self):
        """Создание заглушек для сцен"""
        class StubScene(Scene):
            def initialize(self) -> bool:
                self.initialized = True
                return True
            
            def update(self, delta_time: float):
                pass
            
            def render(self, screen: pygame.Surface):
                screen.fill((100, 100, 100))
                font = pygame.font.Font(None, 36)
                text = font.render(f"Stub Scene: {self.name}", True, (255, 255, 255))
                screen.blit(text, (100, 100))
            
            def handle_event(self, event: pygame.event.Event):
                pass
        
        # Регистрируем заглушки
        self.register_scene("menu", StubScene("menu"))
        self.register_scene("game", StubScene("game"))
        self.register_scene("pause", StubScene("pause"))
    
    def register_scene(self, name: str, scene: Scene):
        """Регистрация новой сцены"""
        if name in self.scenes:
            logger.warning(f"Сцена {name} уже зарегистрирована, перезаписываем")
            # Очищаем старую сцену
            old_scene = self.scenes[name]
            if old_scene == self.active_scene:
                self.set_active_scene(None)
            old_scene.cleanup()
        
        # Устанавливаем ссылку на менеджер сцен
        scene.set_scene_manager(self)
        
        self.scenes[name] = scene
        logger.info(f"Сцена {name} зарегистрирована")
    
    def unregister_scene(self, name: str):
        """Отмена регистрации сцены"""
        if name in self.scenes:
            scene = self.scenes[name]
            if scene == self.active_scene:
                self.set_active_scene(None)
            
            scene.cleanup()
            del self.scenes[name]
            logger.info(f"Сцена {name} удалена")
    
    def set_active_scene(self, scene_name: Optional[str]):
        """Установка активной сцены"""
        if scene_name is None:
            # Деактивируем текущую сцену
            if self.active_scene:
                self.previous_scene = self.active_scene
                self.active_scene.deactivate()
                self.active_scene = None
            return
        
        if scene_name not in self.scenes:
            logger.error(f"Сцена {scene_name} не найдена")
            return
        
        # Деактивируем текущую сцену
        if self.active_scene:
            self.previous_scene = self.active_scene
            self.active_scene.deactivate()
        
        # Активируем новую сцену
        new_scene = self.scenes[scene_name]
        if new_scene.activate():
            self.active_scene = new_scene
            logger.info(f"Активная сцена изменена на {scene_name}")
        else:
            logger.error(f"Не удалось активировать сцену {scene_name}")
            # Возвращаемся к предыдущей сцене
            if self.previous_scene:
                self.active_scene = self.previous_scene
                self.active_scene.activate()
    
    def get_scene(self, name: str) -> Optional[Scene]:
        """Получение сцены по имени"""
        return self.scenes.get(name)
    
    def get_active_scene_name(self) -> Optional[str]:
        """Получение имени активной сцены"""
        return self.active_scene.name if self.active_scene else None
    
    def switch_to_scene(self, scene_name: str, transition: str = "fade"):
        """Переключение на сцену с переходом"""
        if scene_name not in self.scenes:
            logger.error(f"Сцена {scene_name} не найдена")
            return False
        
        if self.transitioning:
            logger.warning("Переход уже выполняется")
            return False
        
        self.transitioning = True
        self.transition_type = transition
        
        # Выполняем переход
        if transition == "instant":
            self.set_active_scene(scene_name)
            self.transitioning = False
        else:
            # Здесь можно добавить анимацию перехода
            self._perform_transition(scene_name)
        
        return True
    
    def _perform_transition(self, target_scene: str):
        """Выполнение перехода между сценами"""
        # Простая реализация перехода
        self.set_active_scene(target_scene)
        self.transitioning = False
    
    def update(self, delta_time: float):
        """Обновление активной сцены"""
        if self.active_scene and self.active_scene.active:
            self.active_scene.update(delta_time)
    
    def render(self, screen: pygame.Surface):
        """Отрисовка активной сцены"""
        if self.active_scene and self.active_scene.active:
            self.active_scene.render(screen)
    
    def handle_event(self, event: pygame.event.Event):
        """Передача события в активную сцену"""
        if self.active_scene and self.active_scene.active:
            self.active_scene.handle_event(event)
    
    def cleanup(self):
        """Очистка всех сцен"""
        logger.info("Очистка менеджера сцен...")
        
        # Деактивируем активную сцену
        if self.active_scene:
            self.active_scene.deactivate()
            self.active_scene = None
        
        # Очищаем все сцены
        for scene in self.scenes.values():
            scene.cleanup()
        
        self.scenes.clear()
        self.previous_scene = None
        self.transitioning = False
        
        logger.info("Менеджер сцен очищен")
    
    def get_scene_list(self) -> list:
        """Получение списка всех сцен"""
        return list(self.scenes.keys())
    
    def is_scene_active(self, scene_name: str) -> bool:
        """Проверка активности сцены"""
        return (self.active_scene and 
                self.active_scene.name == scene_name and 
                self.active_scene.active)
