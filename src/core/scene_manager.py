#!/usr/bin/env python3
"""
Scene Manager - Менеджер сцен для Panda3D
Отвечает только за управление игровыми сценами и переключение между ними
"""

import logging
from typing import Dict, Optional, Any, List
from abc import ABC, abstractmethod
from .interfaces import ISceneManager, SystemState, SystemPriority

logger = logging.getLogger(__name__)

class Scene(ABC):
    """Базовый класс для всех сцен"""
    
    def __init__(self, name: str):
        self.name = name
        self.scene_manager = None
        self.is_initialized = False
        self.scene_root = None  # Корневой узел сцены
        self.ui_root = None     # Корневой узел UI сцены
        
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
    
    def set_visible(self, visible: bool):
        """Установка видимости сцены"""
        if self.scene_root:
            if visible:
                self.scene_root.show()
            else:
                self.scene_root.hide()
        if self.ui_root:
            if visible:
                self.ui_root.show()
            else:
                self.ui_root.hide()

class SceneManager(ISceneManager):
    """Менеджер сцен для Panda3D"""
    
    def __init__(self, render_node, resource_manager, system_manager=None):
        self.render_node = render_node
        self.resource_manager = resource_manager
        # Доступ к менеджеру систем для централизованных обновлений сценой
        self.system_manager = system_manager
        # Опциональные зависимости для унифицированных паттернов состояния/событий
        self.event_system = None
        self.state_manager = None
        
        # Свойства для интерфейса ISystem
        self._system_name = "scene_manager"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Инициализируем атрибуты сразу
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Optional[Scene] = None
        self.previous_scene: Optional[Scene] = None
        self.transitioning = False
        self.transition_type = "instant"
        self.transition_progress = 0.0
        self.scenes_root = None
        self.ui_root = None
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация менеджера сцен"""
        try:
            logger.info("Инициализация менеджера сцен...")
            
            # Создаем корневые узлы
            self.scenes_root = self.render_node.attachNewNode("scenes_root")
            try:
                # UI должен располагаться в 2D-иерархии (aspect2d)
                import builtins
                if hasattr(builtins, 'base') and hasattr(builtins.base, 'aspect2d'):
                    self.ui_root = builtins.base.aspect2d.attachNewNode("ui_root")
                else:
                    # fallback: создаем под render2d, если доступен
                    from direct.showbase import ShowBase
                    self.ui_root = builtins.base.render2d.attachNewNode("ui_root") if hasattr(builtins.base, 'render2d') else self.render_node.attachNewNode("ui_root")
            except Exception:
                # Если нет доступа к base, создаем временно под render
                self.ui_root = self.render_node.attachNewNode("ui_root")
            
            self._system_state = SystemState.READY
            logger.info("Менеджер сцен успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера сцен: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def register_scene(self, name: str, scene: Scene):
        """Регистрация сцены"""
        if name in self.scenes:
            logger.warning(f"Сцена {name} уже зарегистрирована")
            return False
        
        scene.scene_manager = self
        
        # Создаем корневые узлы для сцены
        if self.scenes_root:
            scene.scene_root = self.scenes_root.attachNewNode(f"scene_{name}")
        if self.ui_root:
            scene.ui_root = self.ui_root.attachNewNode(f"ui_{name}")
        
        self.scenes[name] = scene
        
        # Инициализация сцены
        if not scene.initialize():
            logger.error(f"Не удалось инициализировать сцену {name}")
            return False
        
        # По умолчанию сцена невидима
        scene.set_visible(False)
        
        logger.info(f"Сцена {name} зарегистрирована и инициализирована")
        return True
    
    def unregister_scene(self, name: str):
        """Отмена регистрации сцены"""
        if name not in self.scenes:
            return False
        
        scene = self.scenes[name]
        scene.cleanup()
        
        # Удаляем узлы сцены
        if scene.scene_root:
            scene.scene_root.removeNode()
        if scene.ui_root:
            scene.ui_root.removeNode()
        
        del self.scenes[name]
        
        logger.info(f"Сцена {name} удалена")
        return True
    
    def set_active_scene(self, name: str):
        """Установка активной сцены"""
        if name not in self.scenes:
            logger.error(f"Сцена {name} не найдена")
            return False
        
        if self._system_state != SystemState.READY:
            logger.warning("Попытка сменить сцену до инициализации SceneManager")
            return False
        
        # Скрываем предыдущую активную сцену и скрываем её UI
        if self.active_scene:
            try:
                self.active_scene.set_visible(False)
                # Прячем UI предыдущей сцены, чтобы исключить наложение
                if hasattr(self.active_scene, 'ui_root') and self.active_scene.ui_root:
                    self.active_scene.ui_root.hide()
            except Exception:
                pass
            self.previous_scene = self.active_scene
        
        # Показываем новую активную сцену
        self.active_scene = self.scenes[name]
        self.active_scene.set_visible(True)
        # Обновляем глобальное состояние и эмитим событие, если доступны зависимости
        try:
            if self.state_manager:
                self.state_manager.set_state_value("current_scene", name)
        except Exception:
            pass
        try:
            if self.event_system:
                self.event_system.emit_event("scene_changed", {"scene": name}, "scene_manager")
        except Exception:
            pass
        
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
        
        if self._system_state != SystemState.READY:
            logger.warning("Попытка переключения сцены до инициализации SceneManager")
            return False
        
        # Начинаем переход
        self.transitioning = True
        self.transition_type = transition_type
        self.transition_progress = 0.0
        
        # Скрываем предыдущую активную сцену
        if self.active_scene:
            try:
                self.active_scene.set_visible(False)
                if hasattr(self.active_scene, 'ui_root') and self.active_scene.ui_root:
                    self.active_scene.ui_root.hide()
            except Exception:
                pass
            self.previous_scene = self.active_scene
        
        # Показываем новую активную сцену
        self.active_scene = self.scenes[name]
        self.active_scene.set_visible(True)
        # Обновляем глобальное состояние и эмитим событие, если доступны зависимости
        try:
            if self.state_manager:
                self.state_manager.set_state_value("current_scene", name)
        except Exception:
            pass
        try:
            if self.event_system:
                self.event_system.emit_event("scene_changed", {"scene": name, "transition": transition_type}, "scene_manager")
        except Exception:
            pass
        
        # Завершаем переход для мгновенного переключения
        if transition_type == "instant":
            self.transitioning = False
        
        logger.info(f"Переключение на сцену {name} с переходом {transition_type}")
        return True
    
    def update(self, delta_time: float):
        """Обновление менеджера сцен"""
        # Обновление переходов
        if self.transitioning:
            self._update_transition(delta_time)
        
        # Обновление активной сцены
        if self.active_scene:
            self.active_scene.update(delta_time)
    
    def _update_transition(self, delta_time: float):
        """Обновление перехода между сценами"""
        if self.transition_type == "fade":
            self.transition_progress += delta_time / 0.5  # 0.5 секунды на переход
            
            if self.transition_progress >= 1.0:
                self.transitioning = False
                self.transition_progress = 1.0
    
    def render(self, render_node):
        """Отрисовка активной сцены"""
        if self.active_scene:
            self.active_scene.render(render_node)
    
    def handle_event(self, event):
        """Обработка событий активной сцены"""
        if self.active_scene:
            self.active_scene.handle_event(event)
    
    def cleanup(self):
        """Очистка менеджера сцен"""
        logger.info("Очистка менеджера сцен...")
        
        # Очищаем все сцены
        for scene in self.scenes.values():
            scene.cleanup()
        
        # Очищаем корневые узлы
        if self.scenes_root:
            self.scenes_root.removeNode()
        if self.ui_root:
            self.ui_root.removeNode()
        
        self.scenes.clear()
        self.active_scene = None
        self.previous_scene = None
        
        logger.info("Менеджер сцен очищен")
    
    # Реализация недостающих методов интерфейса ISceneManager
    def get_scene(self, name: str) -> Optional[Scene]:
        """Получение сцены по имени"""
        return self.scenes.get(name)
    
    def remove_scene(self, name: str) -> bool:
        """Удаление сцены"""
        if name not in self.scenes:
            return False
        
        scene = self.scenes[name]
        scene.cleanup()
        del self.scenes[name]
        
        # Если удаляемая сцена была активной, сбрасываем активную сцену
        if self.active_scene == scene:
            self.active_scene = None
        
        logger.info(f"Сцена {name} удалена")
        return True
    
    def get_active_scene(self) -> Optional[Scene]:
        """Получение активной сцены"""
        return self.active_scene
    
    def update_active_scene(self, delta_time: float) -> None:
        """Обновление активной сцены"""
        if self.active_scene:
            self.active_scene.update(delta_time)
    
    def add_scene(self, name: str, scene: Scene) -> bool:
        """Добавление сцены"""
        try:
            if name in self.scenes:
                logger.warning(f"Сцена {name} уже существует")
                return False
            
            # Инициализируем сцену
            if not scene.initialize():
                logger.error(f"Не удалось инициализировать сцену {name}")
                return False
            
            # Добавляем сцену
            self.scenes[name] = scene
            scene.scene_manager = self
            
            # Если это первая сцена, делаем её активной
            if not self.active_scene:
                self.active_scene = scene
                scene.set_visible(True)
            
            logger.info(f"Сцена {name} добавлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления сцены {name}: {e}")
            return False
    
    def create_scene(self, name: str, scene_type: str) -> Optional[Scene]:
        """Создание сцены по типу"""
        try:
            # Здесь можно добавить логику создания сцен по типу
            # Пока возвращаем None
            logger.debug(f"Создание сцены {name} типа {scene_type}")
            return None
        except Exception as e:
            logger.error(f"Ошибка создания сцены {name}: {e}")
            return None
    
    def destroy_scene(self, name: str) -> bool:
        """Уничтожение сцены"""
        return self.remove_scene(name)
