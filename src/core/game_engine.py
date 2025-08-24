#!/usr/bin/env python3
"""
Game Engine - Основной игровой движок на Panda3D
Отвечает только за координацию всех систем и управление жизненным циклом игры
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Panda3D imports
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties

from .interfaces import GameState, ISystemManager, IEventEmitter
from .system_manager import SystemManager
from .event_system import EventSystem
from .config_manager import ConfigManager
from .scene_manager import SceneManager
from .resource_manager import ResourceManager
from .performance_manager import PerformanceManager
from .system_factory import SystemFactory

logger = logging.getLogger(__name__)

class GameEngine(ShowBase):
    """
    Основной игровой движок на Panda3D
    Координирует все системы и управляет жизненным циклом игры
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Инициализация Panda3D ShowBase
        super().__init__()
        
        self.config = config
        self.running = False
        self.paused = False
        
        # Состояние игры
        self.current_state = GameState.INITIALIZING
        self.delta_time = 0.0
        self.last_frame_time = time.time()
        
        # Статистика
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Новая архитектура - менеджеры систем
        self.system_manager: Optional[SystemManager] = None
        self.event_system: Optional[EventSystem] = None
        self.system_factory: Optional[SystemFactory] = None
        
        # Существующие менеджеры (для обратной совместимости)
        self.scene_manager: Optional[SceneManager] = None
        self.resource_manager: Optional[ResourceManager] = None
        self.performance_manager: Optional[PerformanceManager] = None
        
        logger.info("Игровой движок Panda3D инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация игрового движка"""
        try:
            logger.info("Начало инициализации игрового движка Panda3D...")
            
            # Инициализация Panda3D
            if not self._initialize_panda3d():
                return False
            
            # Инициализация менеджеров
            if not self._initialize_managers():
                return False
            
            # Инициализация сцен
            if not self._initialize_scenes():
                return False
            
            # Настройка задач
            self._setup_tasks()
            
            self.current_state = GameState.MAIN_MENU
            logger.info("Игровой движок Panda3D успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации игрового движка: {e}")
            return False
    
    def _initialize_panda3d(self) -> bool:
        """Инициализация Panda3D"""
        try:
            # Настройка окна (окно уже создано ShowBase)
            display_config = self.config.get('display', {})
            width = display_config.get('window_width', 1600)
            height = display_config.get('window_height', 900)
            fullscreen = display_config.get('fullscreen', False)
            
            # Создание новых свойств окна
            window_props = WindowProperties()
            window_props.setSize(width, height)
            window_props.setTitle("AI-EVOLVE Enhanced Edition - Panda3D")
            
            if fullscreen:
                window_props.setFullscreen(True)
            
            # Применение новых свойств
            self.win.requestProperties(window_props)
            
            logger.info("Panda3D успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Panda3D: {e}")
            return False
    
    def _initialize_managers(self) -> bool:
        """Инициализация менеджеров систем"""
        try:
            # Инициализация системы событий (новая архитектура)
            self.event_system = EventSystem()
            if not self.event_system.initialize():
                logger.error("Не удалось инициализировать систему событий")
                return False
            
            # Инициализация фабрики систем (новая архитектура)
            self.system_factory = SystemFactory(self.event_system)
            
            # Инициализация менеджера систем (новая архитектура)
            self.system_manager = SystemManager(self.event_system)
            
            # Создаем стандартный набор систем через фабрику
            created_systems = self.system_factory.create_default_systems(self.render, self.win)
            
            # Добавляем созданные системы в менеджер
            for system_name, system in created_systems.items():
                self.system_manager.add_system(system_name, system)
            
            # Добавляем существующие системы в новый менеджер
            self._add_existing_systems_to_manager()
            
            if not self.system_manager.initialize():
                logger.error("Не удалось инициализировать менеджер систем")
                return False
            
            # Инициализация существующих менеджеров (для обратной совместимости)
            self.resource_manager = ResourceManager()
            if not self.resource_manager.initialize():
                logger.error("Не удалось инициализировать менеджер ресурсов")
                return False
            
            self.performance_manager = PerformanceManager()
            if not self.performance_manager.initialize():
                logger.error("Не удалось инициализировать менеджер производительности")
                return False
            
            self.scene_manager = SceneManager(self.render, self.resource_manager)
            if not self.scene_manager.initialize():
                logger.error("Не удалось инициализировать менеджер сцен")
                return False
            
            logger.info("Все менеджеры успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджеров: {e}")
            return False
    
    def _add_existing_systems_to_manager(self):
        """Добавление существующих систем в новый менеджер систем"""
        try:
            # Добавляем существующие системы как адаптеры
            if hasattr(self, 'resource_manager') and self.resource_manager:
                self.system_manager.add_system("resource", self.resource_manager)
            
            if hasattr(self, 'performance_manager') and self.performance_manager:
                self.system_manager.add_system("performance", self.performance_manager)
            
            if hasattr(self, 'scene_manager') and self.scene_manager:
                self.system_manager.add_system("scene", self.scene_manager)
            
            logger.info("Существующие системы добавлены в менеджер систем")
            
        except Exception as e:
            logger.warning(f"Не удалось добавить существующие системы в менеджер: {e}")
    
    def _initialize_scenes(self) -> bool:
        """Инициализация игровых сцен"""
        try:
            # Создание основных сцен
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
            
            # Регистрация сцен
            self.scene_manager.register_scene("menu", MenuScene())
            self.scene_manager.register_scene("game", GameScene())
            self.scene_manager.register_scene("pause", PauseScene())
            self.scene_manager.register_scene("settings", SettingsScene())
            self.scene_manager.register_scene("load_game", LoadScene())
            
            # Установка начальной сцены
            self.scene_manager.set_active_scene("menu")
            
            logger.info("Сцены успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцен: {e}")
            return False
    
    def _setup_tasks(self):
        """Настройка задач Panda3D"""
        # Основная задача обновления
        self.taskMgr.add(self._update_task, "update_task")
        
        logger.debug("Задачи Panda3D настроены")
    
    def run(self):
        """Основной игровой цикл Panda3D"""
        if not self.initialize():
            logger.error("Не удалось инициализировать игровой движок")
            return
        
        self.running = True
        logger.info("Запуск игрового цикла Panda3D")
        
        try:
            # Запуск основного цикла Panda3D (наследуется от ShowBase)
            super().run()
            
        except Exception as e:
            logger.error(f"Критическая ошибка в игровом цикле: {e}")
            self._handle_critical_error(e)
        
        finally:
            self._cleanup()
    
    def _update_task(self, task):
        """Задача обновления состояния игры"""
        if not self.running:
            return task.done
        
        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Обновление всех систем через новый менеджер
        if self.system_manager:
            self.system_manager.update_all_systems(self.delta_time)
        
        # Обновление активной сцены (для обратной совместимости)
        if self.scene_manager and self.scene_manager.active_scene:
            self.scene_manager.active_scene.update(self.delta_time)
        
        # Обновление менеджера производительности (для обратной совместимости)
        if self.performance_manager:
            self.performance_manager.update(self.delta_time)
        
        # Обновление статистики
        self._update_stats()
        
        return task.cont
    
    def _update_stats(self):
        """Обновление статистики"""
        self.frame_count += 1
        current_time = time.time()
        
        # Обновление FPS каждую секунду
        if current_time - self.start_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.start_time = current_time
            
            # Логирование FPS каждые 10 секунд
            if int(current_time) % 10 == 0:
                logger.debug(f"FPS: {self.fps}")
    
    def _handle_critical_error(self, error: Exception):
        """Обработка критических ошибок"""
        logger.critical(f"Критическая ошибка: {error}")
        # Здесь можно добавить логику сохранения состояния игры
        # и показа пользователю сообщения об ошибке
    
    def _cleanup(self):
        """Очистка ресурсов"""
        logger.info("Очистка ресурсов игрового движка...")
        
        try:
            # Очистка нового менеджера систем
            if self.system_manager:
                self.system_manager.cleanup()
            
            # Очистка фабрики систем
            if self.system_factory:
                self.system_factory.cleanup()
            
            # Очистка системы событий
            if self.event_system:
                self.event_system.cleanup()
            
            # Очистка существующих менеджеров (для обратной совместимости)
            if self.scene_manager:
                self.scene_manager.cleanup()
            
            if self.resource_manager:
                self.resource_manager.cleanup()
            
            if self.performance_manager:
                self.performance_manager.cleanup()
            
            # Завершение Panda3D
            try:
                # Сохраняем конфигурацию перед уничтожением
                if hasattr(self, 'config') and isinstance(self.config, dict):
                    # Создаем временный ConfigVariableManager для корректного завершения
                    from panda3d.core import ConfigVariableManager
                    temp_config = ConfigVariableManager()
                    # Копируем настройки
                    for key, value in self.config.items():
                        if isinstance(value, bool):
                            temp_config.SetBool(key, value)
                        elif isinstance(value, int):
                            temp_config.SetInt(key, value)
                        elif isinstance(value, float):
                            temp_config.SetDouble(key, value)
                        elif isinstance(value, str):
                            temp_config.SetString(key, value)
                    
                    # Временно заменяем конфигурацию
                    original_config = getattr(self, '_original_config', None)
                    if original_config is None:
                        self._original_config = self.config
                    self.config = temp_config
                
                self.destroy()
                
                # Восстанавливаем оригинальную конфигурацию
                if hasattr(self, '_original_config'):
                    self.config = self._original_config
                    
            except Exception as e:
                logger.error(f"Ошибка при завершении Panda3D: {e}")
                # Принудительно завершаем
                try:
                    super().destroy()
                except:
                    pass
            
            logger.info("Ресурсы успешно очищены")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов: {e}")
    
    def change_state(self, new_state: GameState):
        """Изменение состояния игры"""
        old_state = self.current_state
        self.current_state = new_state
        logger.info(f"Изменение состояния игры: {old_state} -> {new_state}")
        
        # Обработка изменения состояния
        if new_state == GameState.QUITTING:
            self.running = False
        elif new_state == GameState.PLAYING:
            self.paused = False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        return {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'delta_time': self.delta_time,
            'running_time': time.time() - self.start_time
        }
    
    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if self.win:
            props = self.win.getProperties()
            fullscreen = not props.getFullscreen()
            
            new_props = WindowProperties()
            new_props.setFullscreen(fullscreen)
            self.win.requestProperties(new_props)
            
            logger.info(f"Переключен полноэкранный режим: {fullscreen}")
    
    def set_window_size(self, width: int, height: int):
        """Изменение размера окна"""
        if self.win:
            new_props = WindowProperties()
            new_props.setSize(width, height)
            self.win.requestProperties(new_props)
            
            logger.info(f"Размер окна изменен: {width}x{height}")
    
    # Методы для доступа к новой архитектуре
    def get_system_manager(self) -> Optional[SystemManager]:
        """Получение менеджера систем"""
        return self.system_manager
    
    def get_event_system(self) -> Optional[EventSystem]:
        """Получение системы событий"""
        return self.event_system
    
    def get_system_factory(self) -> Optional[SystemFactory]:
        """Получение фабрики систем"""
        return self.system_factory
    
    def emit_event(self, event_type: str, data: Any, source: str = "game_engine"):
        """Эмиссия события через новую систему событий"""
        if self.event_system:
            self.event_system.emit_event(event_type, data, source)
        else:
            logger.warning("Система событий не инициализирована")
    
    def get_system(self, system_name: str):
        """Получение системы по имени"""
        if self.system_manager:
            return self.system_manager.get_system(system_name)
        return None
    
    def create_system(self, system_name: str, **kwargs):
        """Создание новой системы через фабрику"""
        if self.system_factory:
            return self.system_factory.create_system(system_name, **kwargs)
        return None
